

import os
import logging
import sys
import requests
import shutil
from PIL import Image


PROJECT_PATH = os.path.join(".", "img_data")
NUM_IMAGES = 36
MAX_WIDTH = 1200

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger()

def convert_url_to_gif_url(image_url:str):
    split_url = image_url.split("/")
    shoe_split = split_url[4][:len(split_url[4])-12]
    return f"https://images.stockx.com/360/{shoe_split}/Images/{shoe_split}/Lv2/img01.jpg?w=800"


def download_first_image(old_image_url, shoe_uuid):
    image_url = convert_url_to_gif_url(old_image_url)
    if not image_url:
        logger.error("No link provided.")
        return
    img_folder_path = os.path.join(PROJECT_PATH, shoe_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)
    image_save_path = os.path.join(img_folder_path, "01.png")

    if os.path.exists(image_save_path):
        logger.info(f"First image already exists. Skipping download.")
    else:
        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            logger.info(f"Successfully accessed the Website, saving first image")
            with open(image_save_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved first image")
        else:

            logger.warning(f"Failed to download first image from {image_url}, trying to download it from non 360 view instead.")
            image_url_split = old_image_url.split("?")
            image_url = f"{image_url_split[0]}?w=800"
            response = requests.get(image_url, stream=True)

            if response.status_code == 200:
                logger.info(f"Successfully accessed the Website, saving first image")
                with open(image_save_path, 'wb') as file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, file)
                    logger.info(f"Successfully saved first image")
            else:
                logger.info(f"Failed to download first image from {image_url}")



def get_rest_of_images(original_image_link, shoe_uuid):
    if not original_image_link:
        logger.error("No link provided.")
        return

    img_folder_path = os.path.join(PROJECT_PATH, shoe_uuid, "img")
    
    os.makedirs(os.path.join(PROJECT_PATH, shoe_uuid), exist_ok=True)
    logger.info(f"Ensured style_id folder under {os.path.join(PROJECT_PATH, shoe_uuid)}")

    os.makedirs(img_folder_path, exist_ok=True)
    
    link_template = original_image_link.rsplit("/", 1)[0]
    
    for i in range(2, NUM_IMAGES + 1):
        image_save_path = os.path.join(img_folder_path, f"{str(i).zfill(2)}.png")

        if os.path.exists(image_save_path):
            logger.info(f"Image {i} already exists. Skipping download.")
            continue

        image_url = f"{link_template}/img{i:02d}.jpg?w=800"
        
        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            logger.info(f"Successfully accessed the Website, saving image {i}")
            with open(image_save_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved image {i} with url {image_url}")

        else:
            logger.warning(f"Failed to download image {i} from {image_url}, won't try for more images anymore.")
            break





def make_gif(image_url: str, uuid: str):
    image_url = convert_url_to_gif_url(image_url)
    logger.info(f"Downloading images for {uuid}.")
    get_rest_of_images(image_url, uuid)
    logger.info(f"Successfully downloaded images for {uuid}.")
    gif_folder_path = os.path.join(PROJECT_PATH, uuid, "gif")
    img_folder_path = os.path.join(PROJECT_PATH, uuid, "img")
    if not os.path.exists(gif_folder_path):
        join_images(uuid, img_folder_path, gif_folder_path)



def join_images(uuid, img_folder_path, gif_folder_path):
    logger.info(f"Creating gif for {uuid}.")
    try:
        frames = [Image.open(f"{img_folder_path}/{i:02d}.png") for i in range(1, NUM_IMAGES + 1)]
    except OSError:
        logger.info(f"gif not available, saving static image of shoe instead.")
        frames = [Image.open(f"{img_folder_path}/01.png")]
    os.mkdir(gif_folder_path)
    gif_path = os.path.join(gif_folder_path, f"{uuid}.gif")
    frames[0].save(gif_path, format="GIF", append_images=frames, save_all=True, duration=100, loop=0)
    logger.info(f"Successfully created gif for {uuid}.")
    delete_images(frames,uuid)
    logger.info(f"Successfully deleted unneccessary pictures for {uuid}.")

def delete_images(frames,uuid):
    for i,frame in enumerate(frames):
        if i == 0: 
            
            trimmed_image = trim_image(frame)
         
            trimmed_image.save(frame.filename)  # Replace 'trimmed_image.jpg' with your desired output path
            logger.info(f"Cut image under file path {frame.filename}")
        else:
            logger.info(f"Removed image {i} for {uuid}")
            os.remove(frame.filename)


def trim_image(image):
    img_data = image.load()
    width, height = image.size

    # Iterate through rows from top
    for y in range(height):
        row_has_color = any(img_data[x, y] != (255, 255, 255) for x in range(width))
        if row_has_color:
            break
    else:
        y = 0

    # Iterate through rows from bottom
    for y_end in range(height - 1, -1, -1):
        row_has_color = any(img_data[x, y_end] != (255, 255, 255) for x in range(width))
        if row_has_color:
            break
    else:
        y_end = height - 1

    if y_end >= y:
        image = image.crop((0, y, width, y_end + 1))  # Crop the image

    return image


if __name__ == "__main__":
    pass
    # a = trim_image(Image.open("./img_data/b809d894-5bee-5e24-9e6e-15e5da10a80c/img/01.png"))
    # Save or display the trimmed image
    # a.save("./img_data/b809d894-5bee-5e24-9e6e-15e5da10a80c/img/02.png")  
    # test_url = "https://images.stockx.com/360/Air-Jordan-1-High-OG-SP-fragment-design-x-Travis-Scott/Images/Air-Jordan-1-High-OG-SP-fragment-design-x-Travis-Scott/Lv2/img01.jpg?fm=avif&auto=compress&w=576&dpr=2&updated_at=1635344578&h=384&q=75"
    # test_uuid = "DH3227-105"
    # download_first_image(test_url,test_uuid)
    # make_gif(test_url, test_uuid)
