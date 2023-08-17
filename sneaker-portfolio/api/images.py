
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

router_image = APIRouter()
router_image.mount("/images", StaticFiles(directory="./img_data"), name="images")