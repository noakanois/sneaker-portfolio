import os
import logging
import sys
import requests
import sqlite3
import shutil
from multiprocessing import Process
from PIL import Image

DATABASE_PATH = "test.db"
IMAGE_PATH = os.path.join(".", "img_data")
NUM_IMAGES = 36
IMAGE_WIDTH = 800
INDEX_LENGTH = 2
WHITE_THRESHOLD = 230

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger()


def convert_url_to_gif_url(image_url: str):
    url_key =  image_url.split("/")[4].replace("-Product.jpg", "").replace("-Product_V2.jpg", "")
    return f"https://images.stockx.com/360/{url_key }/Images/{url_key}/Lv2/img01.jpg?w={IMAGE_WIDTH}"


def download_first_image(old_image_url, shoe_uuid):
    image_url = convert_url_to_gif_url(old_image_url)
    if not image_url:
        logger.error("No link provided.")
        return
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
            logger.info(f"Successfully saved first image")
    else:
        logger.warning(
            f"Failed to download first image from {image_url}, trying to download it from non 360 view instead."
        )
        image_url_split = old_image_url.split("?")
        image_url = f"{image_url_split[0]}?w={IMAGE_WIDTH}"
        disallow_transperency = "&bg=FFFFFF"
        response = requests.get(f"{image_url}{disallow_transperency}", stream=True)

        if response.status_code == 200:
            with open(image_save_path, "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved first image")
        else:
            logger.info(f"Failed to download first image from {image_url}")


def get_rest_of_images(original_image_link, shoe_uuid):
    if not original_image_link:
        logger.error("No link provided.")
        return

    img_folder_path = os.path.join(IMAGE_PATH, shoe_uuid, "img")

    os.makedirs(os.path.join(IMAGE_PATH, shoe_uuid), exist_ok=True)
    logger.info(f"Ensured style_id folder under {os.path.join(IMAGE_PATH, shoe_uuid)}")

    os.makedirs(img_folder_path, exist_ok=True)

    link_template = original_image_link.rsplit("/", 1)[0]

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

        else:
            logger.warning(
                f"Failed to download image {index} from {image_url}, won't try for more images anymore."
            )
            break


def make_gif(image_url: str, uuid: str):
    image_url = convert_url_to_gif_url(image_url)
    logger.info(f"Downloading images for {uuid}.")
    get_rest_of_images(image_url, uuid)
    logger.info(f"Successfully downloaded images for {uuid}.")
    gif_folder_path = os.path.join(IMAGE_PATH, uuid, "gif")
    img_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    if not os.path.exists(gif_folder_path):
        join_images(uuid, img_folder_path, gif_folder_path)


def join_images(uuid, img_folder_path, gif_folder_path):
    logger.info(f"Creating gif for {uuid}.")
    try:
        frames = [
            Image.open(f"{img_folder_path}/{str(i).zfill(INDEX_LENGTH)}.png")
            for i in range(1, NUM_IMAGES + 1)
        ]
    except OSError:
        logger.info(f"gif not available, saving static image of shoe instead.")
        frames = [Image.open(f"{img_folder_path}/01.png")]
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
    delete_images(frames, uuid)
    logger.info(f"Successfully deleted unneccessary pictures for {uuid}.")


def delete_images(frames, uuid):
    for i, frame in enumerate(frames):
        if i == 0:
            trim_image(frame.filename)
            logger.info(f"Cut image under file path {frame.filename}")
        else:
            logger.info(f"Removed image {str(i).zfill(INDEX_LENGTH)} for {uuid}")
            os.remove(frame.filename)


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
        for shoe_uuid, shoe_imageUrl in images_to_download:
            if os.path.exists(os.path.join(IMAGE_PATH, shoe_uuid)):
                logger.info(
                    f"Already downloaded images for shoe {shoe_uuid}, skipping download."
                )
                continue
            download_first_image(shoe_imageUrl, shoe_uuid)
            gif_process = Process(target=make_gif, args=(shoe_imageUrl, shoe_uuid))
            gif_process.start()
