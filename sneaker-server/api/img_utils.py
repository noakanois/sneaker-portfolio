import os
import logging
import sys
import requests
import sqlite3
import shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

DATABASE_PATH = "test.db"
IMAGE_PATH = os.path.join(".", "img_data")
NUM_IMAGES = 36
IMAGE_WIDTH = 800
INDEX_LENGTH = 2
WHITE_THRESHOLD = 230

MAX_THREADS = 5


<<<<<<< HEAD
def convert_url_to_gif_url(image_url: str):
    IMAGE_URL_INDEX = 4
    url_key = (
        image_url.split("/")[IMAGE_URL_INDEX]
        .replace("-Product.png", "")
        .replace("-Product.jpg", "")
        .replace("-Product_V2.jpg", "")
        .replace("-Product_V2.png", "")
        .replace("_V2", "")
        .replace(".png", "")
        .replace(".jpg", "")
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
        logger.info(f"First image already exists for shoe {shoe_uuid}. Skipping download.")
        return "EXISTS"

    response = requests.get(image_url, stream=True)

    if response.status_code == 200:
        with open(image_save_path, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
            logger.info(f"Successfully saved first image for shoe {shoe_uuid}. (360)")
            return "GIF"
    else:
        logger.warning(
            f"Failed to download first image from {image_url}, downloading it from non 360 view instead."
        )
        original_image_url_split = original_image_url.split("?")
        original_image_url = f"{original_image_url_split[0]}?w={IMAGE_WIDTH}"
        disallow_transperency = "&bg=FFFFFF"
        response = requests.get(
            f"{original_image_url}{disallow_transperency}", stream=True
        )

        if response.status_code == 200:
            with open(image_save_path, "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(
                    f"Successfully saved first image for shoe {shoe_uuid}. (Static) Non Static URL: {image_url}"
                )
                return "STATIC"
        else:
            logger.info(f"Failed to download first image from {original_image_url}")
            return "ERROR"


def get_images(original_image_link, shoe_uuid):
    logger.info(f"Downloading images for {shoe_uuid}.")
    logger.info(f"360 view pictures available for the shoe_uuid {shoe_uuid}, downloading all images.")
    image_url = convert_url_to_gif_url(original_image_link)
    img_folder_path = os.path.join(IMAGE_PATH, shoe_uuid, "img")
    os.makedirs(os.path.join(IMAGE_PATH, shoe_uuid), exist_ok=True)
    logger.info(
        f"Ensured shoe images folder under {img_folder_path}"
    )
=======
def get_visuals_all_items():
    with sqlite3.connect(DATABASE_PATH) as conn:
        images_todownload = (
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
        executor.map(get_visual_item, images_todownload)

    logging.info("Finished downloading")


def get_visual_item(itemdata, redownload=False):
    item_uuid, item_img_url = itemdata
    logging.info(f"Started downloading for {item_uuid}")
    download_first_img(item_uuid, item_img_url, redownload)
    download_360_images(item_uuid, item_img_url, redownload)
    make_gif(item_uuid)
    delete_images(item_uuid)
    logging.info(f"Finished downloading for {item_uuid}")

>>>>>>> f39e0092bcc5b8ba97b18624f7a34f44095070da

def download_first_img(item_uuid, img_url, redownload=True):
    img_folder_path = os.path.join(IMAGE_PATH, item_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)

<<<<<<< HEAD
    link_template = image_url.rsplit("/", 1)[0]     
    for i in range(2, NUM_IMAGES + 1):
=======
    first_img_path = os.path.join(img_folder_path, f"{item_uuid}.png")

    if not redownload and os.path.exists(first_img_path):
        return True

    img_360_url = convert_url_to_360_url(img_url, "01")

    if download_picture(img_360_url, first_img_path):
        return download_and_trim(first_img_path, item_uuid)

    img_standard_url = f"{img_url.split('?')[0]}?w={IMAGE_WIDTH}"
    disallow_transparency = "&bg=FFFFFF"

    if download_picture(f"{img_standard_url}{disallow_transparency}", first_img_path):
        return download_and_trim(first_img_path, item_uuid)

    return False


def download_and_trim(first_img_path, item_uuid):
    trim_image(first_img_path)
    logging.info(f"Finished downloading first image for {item_uuid}")
    return True


def download_360_images(item_uuid, img_url, redownload=True):
    img_folder_path = os.path.join(IMAGE_PATH, item_uuid, "img")
    os.makedirs(img_folder_path, exist_ok=True)

    if not redownload and os.path.exists(os.path.join(IMAGE_PATH, item_uuid, "gif")):
        return False

    for i in range(1, NUM_IMAGES + 1):
>>>>>>> f39e0092bcc5b8ba97b18624f7a34f44095070da
        index = str(i).zfill(INDEX_LENGTH)
        img_save_path = os.path.join(img_folder_path, f"{index}.png")

        img_url = convert_url_to_360_url(img_url, index)
        if download_picture(img_url, img_save_path):
            continue

<<<<<<< HEAD
        image_url = f"{link_template}/img{index}.jpg?w={IMAGE_WIDTH}"

        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            with open(image_save_path, "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                logger.info(f"Successfully saved image {index} with url {image_url}")
            
        else:
            logger.warning(
                f"Failed to download image {index} from {image_url}, deleted all images."
            )
            delete_images(shoe_uuid, True)
            return False
    logger.info(f"Successfully downloaded all images for {shoe_uuid}.")
    return True
 
=======
        return False
    return True
>>>>>>> f39e0092bcc5b8ba97b18624f7a34f44095070da


def make_gif(uuid: str):
    gif_folder_path = os.path.join(IMAGE_PATH, uuid, "gif")
    img_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    if os.path.exists(gif_folder_path):
        return False
    logging.info(f"Creating gif for {uuid}.")
    img_files = [f for f in os.listdir(img_folder_path) if f.endswith(".png")]
    num_images = len(img_files)
    frames = [
        Image.open(f"{img_folder_path}/{str(i).zfill(INDEX_LENGTH)}.png")
        for i in range(1, num_images)
    ]

<<<<<<< HEAD

def join_images(uuid, img_folder_path, gif_folder_path):
    logger.info(f"Creating gif for {uuid}.")
    frames = [
        Image.open(f"{img_folder_path}/{str(i).zfill(INDEX_LENGTH)}.png")
        for i in range(1, NUM_IMAGES + 1)
    ]

=======
>>>>>>> f39e0092bcc5b8ba97b18624f7a34f44095070da
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
<<<<<<< HEAD
    logger.info(f"Successfully created gif for {uuid}.")
    

def delete_images(uuid, delete_all = False):
    for file in os.listdir(os.path.join(IMAGE_PATH, uuid, "img")):
        if not delete_all and file == "01.png":
            continue
        remove_path = os.path.join(IMAGE_PATH, uuid, "img", file)
        os.remove(remove_path)
        logger.info(f"Removed image {file} for {uuid}")
    logger.info(f"Successfully deleted unneccessary pictures for {uuid}.")


=======
    logging.info(f"Created gif for {uuid}.")
    return True


def delete_images(uuid):
    img_folder_path = os.path.join(IMAGE_PATH, uuid, "img")
    for i in range(1, NUM_IMAGES + 1):
        try:
            index = str(i).zfill(INDEX_LENGTH)
            img_path = os.path.join(img_folder_path, f"{index}.png")
            os.remove(img_path)
            logging.info(f"Removed image {str(i).zfill(INDEX_LENGTH)} for {uuid}")
        except:
            pass


def download_picture(img_url, save_path):
    logging.info(f"Download_picture with {img_url}")
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
            logging.info(f"Successfully saved {img_url} to {save_path}")
        return True
    logging.info(f"Failure download_picture with {img_url}")
    return False


def convert_url_to_360_url(image_url: str, index):
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


>>>>>>> f39e0092bcc5b8ba97b18624f7a34f44095070da
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
    logger.info(f"Successfully cropped first image in {path}.")


<<<<<<< HEAD
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
            if os.path.exists(os.path.join(IMAGE_PATH, shoe_uuid, "img", "01.png")):
                logger.info(
                    f"Images for shoe {shoe_uuid} already downloaded. Skipping."
                )
                return
            status = download_first_image(shoe_image_url,shoe_uuid)
            if status == "GIF":
                if get_images(shoe_image_url, shoe_uuid):
                    make_gif(shoe_image_url, shoe_uuid)
                    delete_images(shoe_uuid)
                    
                else:
                    return False
            trim_image(os.path.join(IMAGE_PATH, shoe_uuid, "img", "01.png"))
            return True
            
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            executor.map(process_shoe, images_to_download)

    logging.info("Finished downloading")
=======
if __name__ == "__main__":
    # get_visual_item(("0fe34fb8-d996-55d9-b592-86651c40b82a", "https://images.stockx.com/images/Nike-Air-Max-90-Off-White-Desert-Ore/Images/Nike-Air-Max-90-Off-White-Desert-Ore-Product.jpg"))
    pass
>>>>>>> f39e0092bcc5b8ba97b18624f7a34f44095070da
