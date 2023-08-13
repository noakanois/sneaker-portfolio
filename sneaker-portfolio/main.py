import os
import logging
import sys
import requests
import shutil
from PIL import Image

PROJECT_PATH = os.path.join(".", "data")
NUM_IMAGES = 36
MAX_WIDTH = 1200

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger()


def sanitize_style_id(style_id: str) -> str:
    return style_id.replace(" ", "-").replace("/", "-")


def get_angle_images_from_original_image(original_image_link, style_id):
    if not original_image_link:
        logger.error("No link provided.")
        return

    img_folder_path = os.path.join(PROJECT_PATH, style_id, "img")
    
    os.makedirs(os.path.join(PROJECT_PATH, style_id), exist_ok=True)
    logger.info(f"Ensured style_id folder under {os.path.join(PROJECT_PATH, style_id)}")

    os.makedirs(img_folder_path, exist_ok=True)
    
    link_template = original_image_link.rsplit("/", 1)[0]
    
    for i in range(1, NUM_IMAGES + 1):
        image_save_path = os.path.join(img_folder_path, f"{str(i).zfill(2)}.png")

        if os.path.exists(image_save_path):
            logger.info(f"Image {i} already exists. Skipping download.")
            continue

        image_url = f"{link_template}/img{i:02d}.jpg"
        
        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            logger.info(f"Successfully accessed the Website, saving image {i}")
            with open(image_save_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved image {i}")

            image = Image.open(image_save_path)
            width_percent = (MAX_WIDTH / float(image.size[0]))
            resized_image = image.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            resized_image.save(image_save_path)
        else:
            logger.warning(f"Failed to download image {i} from {image_url}")



def resize_and_save_image(image_path: str):
    image = Image.open(image_path)
    width_percent = (MAX_WIDTH / float(image.size[0]))
    resized_image = image.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
    resized_image.save(image_path)


def make_gif(link: str, style_id: str):
    style_id = sanitize_style_id(style_id)

    img_folder_path = os.path.join(PROJECT_PATH, style_id, "img")
    if not os.path.exists(img_folder_path):
        logger.info(f"Downloading images for {style_id}.")
        get_angle_images_from_original_image(link, style_id)
        logger.info(f"Successfully downloaded images for {style_id}.")

    gif_folder_path = os.path.join(PROJECT_PATH, style_id, "gif")
    if not os.path.exists(gif_folder_path):
        join_images(style_id, img_folder_path, gif_folder_path)



def join_images(style_id, img_folder_path, gif_folder_path):
    logger.info(f"Creating gif for {style_id}.")
    frames = [Image.open(f"{img_folder_path}/{i}.png") for i in range(1, NUM_IMAGES + 1)]

    os.mkdir(gif_folder_path)
    gif_path = os.path.join(gif_folder_path, f"{style_id}.gif")

    frames[0].save(gif_path, format="GIF", append_images=frames, save_all=True, duration=100, loop=0)
    logger.info(f"Successfully created gif for {style_id}.")


if __name__ == "__main__":
    test_url = "https://images.stockx.com/360/Air-Jordan-1-High-OG-SP-fragment-design-x-Travis-Scott/Images/Air-Jordan-1-High-OG-SP-fragment-design-x-Travis-Scott/Lv2/img01.jpg?fm=avif&auto=compress&w=576&dpr=2&updated_at=1635344578&h=384&q=75"
    test_style_id = "DH3227-105"

    get_angle_images_from_original_image(test_url, test_style_id)
    make_gif(test_url, test_style_id)
