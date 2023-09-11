from api.img_utils import convert_url_to_360_url, is_row_white


def test_convert_url_to_360_url():
    image_url = (
        "https://images.stockx.com/images/Air-Jordan-3-Retro-Fragment-Product.jpg"
    )
    index = "01"
    expected_url = "https://images.stockx.com/360/Air-Jordan-3-Retro-Fragment/Images/Air-Jordan-3-Retro-Fragment/Lv2/img01.jpg?w=800"
    assert convert_url_to_360_url(image_url, index) == expected_url


def test_is_row_white():
    row = [255, 255, 255]
    assert is_row_white(row) == True
