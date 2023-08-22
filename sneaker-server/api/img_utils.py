import os
import logging
import sys
import requests
import sqlite3
import shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

DATABASE_PATH = "test.db"
IMAGE_PATH = os.path.join(".", "img_data")
NUM_IMAGES = 36
IMAGE_WIDTH = 800
INDEX_LENGTH = 2
WHITE_THRESHOLD = 230

logging.basicConfig(filename="logs.txt",filemode='a', level=logging.DEBUG)
logger = logging.getLogger()


def convert_url_to_gif_url(image_url: str):
    IMAGE_URL_INDEX = 4
    url_key = (
        image_url.split("/")[IMAGE_URL_INDEX]
        .replace("-Product.png","")
        .replace("-Product.jpg", "")
        .replace("-Product_V2.jpg", "")
        .replace("-Product_V2.png", "")
        .replace("_V2", "")
        .replace(".png","")
        .replace(".jpg","")
    )
    
    return f"https://images.stockx.com/360/{url_key }/Images/{url_key}/Lv2/img01.jpg?w={IMAGE_WIDTH}"


def download_first_image(original_image_url, shoe_uuid):
    logger.info(f"preConvert for {shoe_uuid}: {original_image_url}")
    image_url = convert_url_to_gif_url(original_image_url)
    logger.info(f"postConvert for {shoe_uuid}: {image_url}")
    img_folder_path = os.path.join(IMAGE_PATH, shoe_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)
    image_save_path = os.path.join(img_folder_path, "01.png")
   
    if os.path.exists(image_save_path):
        logger.info(f"First image already exists. Skipping download.")
        return

    response = requests.get(image_url, stream=True)

    if response.status_code == 200:
        with open(image_save_path, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
            logger.info(f"Successfully saved first image for shoe {shoe_uuid}. (360)")
            return "GIF"
    else:
        logger.warning(
            f"Failed to download first image from {image_url}, trying to download it from non 360 view instead."
        )
        original_image_url_split = original_image_url.split("?")
        original_image_url = f"{original_image_url_split[0]}?w={IMAGE_WIDTH}"
        disallow_transperency = "&bg=FFFFFF"
        response = requests.get(f"{original_image_url}{disallow_transperency}", stream=True)

        if response.status_code == 200:
            with open(image_save_path, "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved first image for shoe {shoe_uuid}. (Static) Non Static URL: {image_url}")
                return "STATIC"
        else:
            logger.info(f"Failed to download first image from {original_image_url}")
            return "ERROR"


def get_images(original_image_link, shoe_uuid):
    status_string = download_first_image(original_image_link,shoe_uuid)
    
    if status_string == "ERROR":
        logger.error(f"Unable to download the first image for shoe_uuid {shoe_uuid}.")
        return 0
    elif status_string == "STATIC":
        logger.info(f"GIF not available for shoe_uuid {shoe_uuid}, only leaving static image.")
        return 1
    logger.info(f"GIF available for the shoe_uuid {shoe_uuid}, downloading all images.")
    image_url = convert_url_to_gif_url(original_image_link)
    img_folder_path = os.path.join(IMAGE_PATH, shoe_uuid, "img")
    os.makedirs(os.path.join(IMAGE_PATH, shoe_uuid), exist_ok=True)
    logger.info(
        f"Ensured shoe images folder under {os.path.join(IMAGE_PATH, shoe_uuid)}"
    )

    os.makedirs(img_folder_path, exist_ok=True)

    link_template = image_url.rsplit("/", 1)[0]
    final_count = 0
    for i in range(2, NUM_IMAGES + 1):
        index = str(i).zfill(INDEX_LENGTH)
        image_save_path = os.path.join(img_folder_path, f"{index}.png")

        if os.path.exists(image_save_path):
            logger.info(f"Image {index} already exists. Skipping download.")
            continue

        image_url = f"{link_template}/img{index}.jpg?w={IMAGE_WIDTH}"

        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            with open(image_save_path, "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved image {index} with url {image_url}")
                final_count += 1
        else:
            logger.warning(
                f"Failed to download image {index} from {image_url}, deleted all images."
            )
            delete_images(shoe_uuid)
            break
    return final_count


def make_gif(image_url: str, uuid: str):
    
    logger.info(f"Downloading images for {uuid}.")
    amount_images = get_images(image_url, uuid)
    if amount_images == 0:
        logger.error(f"Could not create gif because no images could be downloaded.")
        return
    elif amount_images == 1:
        logger.info(f"Successfully downloaded {amount_images} images for {uuid}.")
        logger.info(f"Not creating gif for {uuid} because only one image is available.")
        trim_image(os.path.join(IMAGE_PATH,uuid,"img","01.png"))
        return
    logger.info(f"Successfully downloaded {amount_images} images for {uuid}.")
    gif_folder_path = os.path.join(IMAGE_PATH, uuid, "gif")
    img_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    if not os.path.exists(gif_folder_path):
        join_images(uuid, img_folder_path, gif_folder_path)


def join_images(uuid, img_folder_path, gif_folder_path):
    logger.info(f"Creating gif for {uuid}.")
    frames = [
        Image.open(f"{img_folder_path}/{str(i).zfill(INDEX_LENGTH)}.png")
        for i in range(1, NUM_IMAGES + 1)
    ]
 
    os.mkdir(gif_folder_path)
    gif_path = os.path.join(gif_folder_path, f"{uuid}.gif")
    frames[0].save(
        gif_path,
        format="GIF",
        append_images=frames,
        save_all=True,
        duration=100,
        loop=0,
    )
    logger.info(f"Successfully created gif for {uuid}.")
    delete_images(uuid)
    trim_image(os.path.join(IMAGE_PATH,uuid,"img","01.png"))
    logger.info(f"Successfully deleted unneccessary pictures for {uuid}.")


def delete_images(uuid):
    for i, file in enumerate(os.listdir(os.path.join(IMAGE_PATH,uuid,"img"))):
        if file == "01.png":
            continue
        logger.info(f"Removed image {str(i).zfill(INDEX_LENGTH)} for {uuid}")
        remove_path = os.path.join(IMAGE_PATH,uuid,"img",file)
        os.remove(remove_path) 
  

def is_row_white(row, threshold=WHITE_THRESHOLD):
    return all(pixel >= threshold for pixel in row) or all(pixel == 0 for pixel in row)


def trim_image(path):
    image = Image.open(path)
    grey_image = image.convert("L")
    data = list(grey_image.getdata())
    width, height = grey_image.size
    pixels = [data[i : i + width] for i in range(0, len(data), width)]

    top_crop = 0
    for row in pixels:
        if is_row_white(row):
            top_crop += 1
        else:
            break

    bottom_crop = 0
    for row in reversed(pixels):
        if is_row_white(row):
            bottom_crop += 1
        else:
            break

    cropped_image = image.crop((0, top_crop, width, height - bottom_crop))
    cropped_image.save(path)


MAX_THREADS = 10


def download_not_available_images():
    with sqlite3.connect(DATABASE_PATH) as conn:
        images_to_download = (
            conn.cursor()
            .execute(
                """
            SELECT portfolios.shoe_uuid, shoes.imageUrl 
            FROM portfolios 
            JOIN shoes ON portfolios.shoe_uuid = shoes.uuid
            """
            )
            .fetchall()
        )

        def process_shoe(shoe_data):
            shoe_uuid, shoe_image_url = shoe_data
            if os.path.exists(os.path.join(IMAGE_PATH, shoe_uuid,"img","01.png")):
                logger.info(
                    f"Images for shoe {shoe_uuid} already downloaded. Skipping."
                )
                return
            make_gif(shoe_image_url, shoe_uuid)

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            executor.map(process_shoe, images_to_download)

    logging.info("Finished downloading")
