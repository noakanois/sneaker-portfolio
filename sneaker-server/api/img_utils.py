import os
import logging
import sys
import requests
import sqlite3
import shutil
from threading import Thread
from PIL import Image

DATABASE_PATH = "test.db"
IMAGE_PATH = os.path.join(".", "img_data")
NUM_IMAGES = 36
IMAGE_WIDTH = 800
INDEX_LENGTH = 2
WHITE_THRESHOLD = 230

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger()


def convert_to_gif_url(image_url: str) -> str:
    IMAGE_URL_INDEX = 4
    url_key = image_url.split("/")[IMAGE_URL_INDEX].replace("-Product.jpg", "").replace("-Product_V2.jpg", "")
    return f"https://images.stockx.com/360/{url_key }/Images/{url_key}/Lv2/img01.jpg?w={IMAGE_WIDTH}"


def download_first_image(original_image_url: str, shoe_uuid: str):
    image_url = convert_to_gif_url(original_image_url)
    img_folder_path = os.path.join(IMAGE_PATH, shoe_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)
    image_save_path = os.path.join(img_folder_path, "01.png")

    if os.path.exists(image_save_path):
        logger.info("First image already exists. Skipping download.")
        return

    save_image_from_url(image_url, image_save_path, original_image_url)


def save_image_from_url(image_url: str, save_path: str, original_image_url: str = None):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
            logger.info(f"Successfully saved image to {save_path}")
    elif original_image_url:
        download_from_fallback_url(original_image_url, save_path)


def download_from_fallback_url(original_image_url: str, save_path: str):
    image_url_split = original_image_url.split("?")
    image_url = f"{image_url_split[0]}?w={IMAGE_WIDTH}"
    disallow_transparency = "&bg=FFFFFF"
    save_image_from_url(f"{image_url}{disallow_transparency}", save_path)


def download_remaining_images(original_image_link: str, shoe_uuid: str):
    img_folder_path = os.path.join(IMAGE_PATH, shoe_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)
    link_template = original_image_link.rsplit("/", 1)[0]

    for i in range(2, NUM_IMAGES + 1):
        index = str(i).zfill(INDEX_LENGTH)
        image_save_path = os.path.join(img_folder_path, f"{index}.png")
        if os.path.exists(image_save_path):
            logger.info(f"Image {index} already exists. Skipping download.")
            continue
        image_url = f"{link_template}/img{index}.jpg?w={IMAGE_WIDTH}"
        save_image_from_url(image_url, image_save_path)


def make_gif(image_url: str, uuid: str):
    image_url = convert_to_gif_url(image_url)
    logger.info(f"Downloading images for {uuid}.")
    download_remaining_images(image_url, uuid)
    logger.info(f"Successfully downloaded images for {uuid}.")
    gif_folder_path = os.path.join(IMAGE_PATH, uuid, "gif")
    img_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    if not os.path.exists(gif_folder_path):
        combine_images(uuid, img_folder_path, gif_folder_path)

def is_row_white(row, threshold=WHITE_THRESHOLD):
    return all(pixel >= threshold for pixel in row) or all(pixel == 0 for pixel in row)


def combine_images(uuid, img_folder_path, gif_folder_path):
    logger.info(f"Creating gif for {uuid}.")
    try:
        frames = [
            Image.open(os.path.join(img_folder_path, f"{str(i).zfill(INDEX_LENGTH)}.png"))
            for i in range(1, NUM_IMAGES + 1)
        ]
    except OSError:
        logger.info("Gif not available, saving static image of shoe instead.")
        frames = [Image.open(os.path.join(img_folder_path, "01.png"))]
    os.makedirs(gif_folder_path, exist_ok=True)
    gif_path = os.path.join(gif_folder_path, f"{uuid}.gif")
    frames[0].save(gif_path, format="GIF", append_images=frames, save_all=True, duration=100, loop=0)
    logger.info(f"Successfully created gif for {uuid}.")
    cleanup_images(frames, uuid)

def cleanup_images(frames, uuid):
    for i, frame in enumerate(frames):
        if i == 0:
            trim_image(frame.filename)
            logger.info(f"Trimmed image under file path {frame.filename}")
        else:
            logger.info(f"Removed image {str(i).zfill(INDEX_LENGTH)} for {uuid}")
            os.remove(frame.filename)


def trim_image(path):
    image = Image.open(path)
    grey_image = image.convert("L")
    pixels = list(grey_image.getdata())
    width, height = grey_image.size
    rows = [pixels[i : i + width] for i in range(0, len(pixels), width)]
    top_crop, bottom_crop = 0, 0

    for row in rows:
        if is_row_white(row):
            top_crop += 1
        else:
            break
    for row in reversed(rows):
        if is_row_white(row):
            bottom_crop += 1
        else:
            break

    cropped_image = image.crop((0, top_crop, width, height - bottom_crop))
    cropped_image.save(path)


def download_not_available_images():
    with sqlite3.connect(DATABASE_PATH) as conn:
        images_to_download = conn.cursor().execute(
            """
            SELECT portfolios.shoe_uuid, shoes.imageUrl 
            FROM portfolios 
            JOIN shoes ON portfolios.shoe_uuid = shoes.uuid
            """
        ).fetchall()

        threads = []
        for shoe_uuid, shoe_image_url in images_to_download:
            if os.path.exists(os.path.join(IMAGE_PATH, shoe_uuid)):
                logger.info(f"Images for shoe {shoe_uuid} already downloaded. Skipping.")
                continue
            download_first_image(shoe_image_url, shoe_uuid)
            thread = Thread(target=make_gif, args=(shoe_image_url, shoe_uuid))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    download_not_available_images()
