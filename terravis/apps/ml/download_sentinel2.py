import os
import requests
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def get_access_token(username: str, password: str) -> str:
    """Exchange username/password for a short-lived OAuth2 access token."""
    response = requests.post(
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data={
            "client_id": "cdse-public",
            "username": username,
            "password": password,
            "grant_type": "password",
        },
    )
    response.raise_for_status()  # throws if login failed, instead of failing silently
    return response.json()["access_token"]


def search_products(bbox: str, cloud_cover_max: int = 80, limit: int = 5):
    """
    Query the OData catalogue for Sentinel-2 L2A scenes.
    bbox: WKT polygon string, "lon lat,lon lat,..." (closed ring)
    """
    filter_query = (
        f"Collection/Name eq 'SENTINEL-2' "
        f"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(({bbox}))') "
        f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value gt {cloud_cover_max - 20} and att/OData.CSC.DoubleAttribute/Value lt {cloud_cover_max})"
    )
    url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter={filter_query}&$top={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["value"]


def download_product(product_id: str, product_name: str, token: str, out_dir: str = "."):
    url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    out_path = os.path.join(out_dir, f"{product_name}.zip")
    with open(out_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return out_path


if __name__ == "__main__":
    user = os.environ["COPERNICUS_USER"]
    password = os.environ["COPERNICUS_PASSWORD"]

    print("Getting access token...")
    token = get_access_token(user, password)
    print("Token acquired.")

    # Rough bounding box around Bhubaneswar/Odisha region — WKT format: "lon lat, lon lat, ..." (closed polygon, first = last point)
    bbox = "85.7 20.1,85.9 20.1,85.9 20.3,85.7 20.3,85.7 20.1"

    print("Searching for scenes...")
    products = search_products(bbox, cloud_cover_max=80, limit=5)
    print(f"Found {len(products)} products.")

    for p in products:
        print(f" - {p['Name']} (cloud cover ~{p.get('ContentDate', {})})")

    if products:
        first = products[0]
        print(f"Downloading {first['Name']}...")
        path = download_product(first["Id"], first["Name"], token)
        print(f"Saved to {path}")