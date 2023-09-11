import os
import pytest
from unittest.mock import patch, MagicMock
from api.scrape import get_search_json


@pytest.fixture
def mock_response():
    with open(
        os.path.join(os.path.dirname(__file__), "mock_data/mock_search_response.json"),
        "rb",
    ) as f:
        response_content = f.read()
    response = MagicMock()
    response.content = response_content
    return response


@patch("requests.get")
def test_get_search_json(mock_get, mock_response):
    mock_get.return_value = mock_response
    first_entry = {
        "Release Date": "2020-09-17",
        "Retail Price": "200",
        "brand": "Jordan",
        "description": "Please Note: The clear heel tab does experience slight "
        "yellowing due to storage by the manufacturer. The Air Jordan "
        "3 Fragment is the follow up to the very popular 2015 Air "
        "Jordan 1 collaboration. Fans waited patiently for Fragment’s "
        "founder Hiroshi Fujiwara to drop a new collaboration with "
        "Jordan Brand, after a slew of other collaborations with "
        "other entities such as Louis Vuitton, Anti-Social Social "
        "Club, and Pokemon. The Air Jordan 3 Fragment brings the "
        "lighting bolt brand back to a classic Jordan model.\n"
        "<br>\n"
        "<br>\n"
        "Following Hiroshi Fujiwara’s love for simplistic motifs, the "
        "Air Jordan 3 Fragment comes dressed in white and black. The "
        "upper features a primarily white leather upper with a black "
        "full-grain leather mudguard. This collaboration replaces the "
        "Elephant print that typically appears on a Jordan 3 with "
        "plush black leather embossed with the Fragment lighting bolt "
        "logo. The sneaker’s white midsole has the colorway’s style "
        "code and release date printed in black text. To show true "
        "unison between the two brands, the Fragment’s lighting bolt "
        "logo appears behind a translucent Jumpman, in a similar "
        "fashion to August’s Fire Red Denim 3s.\n"
        "<br>\n"
        "<br>\n"
        "The Air Jordan 3 Fragment dropped in September of 2020 for "
        "$200.",
        "imageUrl": "https://images.stockx.com/images/Air-Jordan-3-Retro-Fragment-Product.jpg",
        "model": "Jordan 3 Retro",
        "name": "Fragment",
        "releaseDate": "2020-09-17",
        "retailPrice": "200",
        "smallImageUrl": "https://images.stockx.com/images/Air-Jordan-3-Retro-Fragment-Product.jpg?fit=fill&bg=FFFFFF&w=300&h=214&fm=webp&auto=compress&q=90&dpr=2&trim=color&updated_at=1607649971",
        "thumbUrl": "https://images.stockx.com/images/Air-Jordan-3-Retro-Fragment-Product.jpg?fit=fill&bg=FFFFFF&w=140&h=100&fm=webp&auto=compress&q=90&dpr=2&trim=color&updated_at=1607649971",
        "title": "Jordan 3 Retro Fragment",
        "urlKey": "air-jordan-3-retro-fragment",
    }

    assert get_search_json("Fragment_Jordan")[0] == first_entry
    assert len(get_search_json("Fragment_Jordan")) == 20
