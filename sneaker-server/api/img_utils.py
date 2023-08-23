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

MAX_THREADS = 10


def get_visuals_all_items():
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

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(get_visual_item, images_to_download)

    logging.info("Finished downloading")

def get_visual_item(item_data):
    item_uuid, item_img_url = item_data
    download_first_img(item_uuid, item_img_url, redownload=False)
    download_360_images(item_uuid, item_img_url, redownload=False)
    make_gif(item_uuid)
    delete_images(item_uuid)
    
def download_first_img(item_uuid, img_url, redownload=True):
    img_folder_path = os.path.join(IMAGE_PATH, item_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)
    
    first_img_path = os.path.join(img_folder_path, f"{item_uuid}.png")

    if not redownload and os.path.exists(first_img_path):
        return True
    
    img_360_url = _convert_url_to_360_url(img_url, "01")
    
    if _download_picture(img_360_url, first_img_path):
        _trim_image(first_img_path)
        return True
    
    img_standard_url = f"{img_url.split('?')[0]}?w={IMAGE_WIDTH}"
    disallow_transparency = "&bg=FFFFFF"
    
    if _download_picture(f"{img_standard_url}{disallow_transparency}", first_img_path):
        _trim_image(first_img_path)
        return True
    return False


def download_360_images(item_uuid, img_url, redownload=True):
    img_folder_path = os.path.join(IMAGE_PATH, item_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)
    
    for i in range(1, NUM_IMAGES + 1):
        index = str(i).zfill(INDEX_LENGTH)
        img_save_path = os.path.join(img_folder_path, f"{index}.png")

        if not redownload and os.path.exists(img_save_path):
            logging.info(f"Image {index} already exists. Skipping download.")
            return False
        
        img_url = _convert_url_to_360_url(img_url)
        if _download_picture(img_url, img_save_path):
            continue
        return False


def make_gif(uuid: str):
    gif_folder_path = os.path.join(IMAGE_PATH, uuid, "gif")
    img_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    if os.path.exists(gif_folder_path):
        return False
    
    logging.info(f"Creating gif for {uuid}.")
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
    logging.info(f"Created gif for {uuid}.")
    return True


def delete_images(uuid):
    item_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    for i, file in enumerate(os.listdir(item_folder_path, start=1)):
        logging.info(f"Removed image {str(i).zfill(INDEX_LENGTH)} for {uuid}")
        remove_path = os.path.join(IMAGE_PATH, uuid, "img", file)
        os.remove(remove_path)
            
            
def _download_picture(img_url, save_path):
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
            logging.info(f"Successfully saved {img_url} to {save_path}")
        return True
    return False
    

def _convert_url_to_360_url(image_url: str, index):
    IMAGE_URL_INDEX = 4
    url_key_360 = (
        image_url.split("/")[IMAGE_URL_INDEX]
        .replace("-Product.png", "")
        .replace("-Product.jpg", "")
        .replace("-Product_V2.jpg", "")
        .replace("-Product_V2.png", "")
        .replace("_V2", "")
        .replace(".png", "")
        .replace(".jpg", "")
    )

    return f"https://images.stockx.com/360/{url_key_360}/Images/{url_key_360}/Lv2/img{index}.jpg?w={IMAGE_WIDTH}"


def _is_row_white(row, threshold=WHITE_THRESHOLD):
    return all(pixel >= threshold for pixel in row) or all(pixel == 0 for pixel in row)


def _trim_image(path):
    image = Image.open(path)
    grey_image = image.convert("L")
    data = list(grey_image.getdata())
    width, height = grey_image.size
    pixels = [data[i : i + width] for i in range(0, len(data), width)]

    top_crop = 0
    for row in pixels:
        if _is_row_white(row):
            top_crop += 1
        else:
            break

    bottom_crop = 0
    for row in reversed(pixels):
        if _is_row_white(row):
            bottom_crop += 1
        else:
            break

    cropped_image = image.crop((0, top_crop, width, height - bottom_crop))
    cropped_image.save(path)





