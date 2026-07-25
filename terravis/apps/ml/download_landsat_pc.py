import requests
import os

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/token"

def search_landsat(bbox, max_results=5, max_cloud=30):
    payload = {
        "collections": ["landsat-c2-l2"],
        "bbox": bbox,  # [min_lon, min_lat, max_lon, max_lat]
        "query": {"eo:cloud_cover": {"lt": max_cloud}},
        "limit": max_results,
    }
    resp = requests.post(STAC_URL, json=payload)
    resp.raise_for_status()
    return resp.json()["features"]


def get_signed_url(asset_href):
    """Planetary Computer assets need a short-lived SAS token appended to the URL."""
    collection = "landsat-c2-l2"
    resp = requests.get(f"{SAS_URL}/{collection}")
    resp.raise_for_status()
    token = resp.json()["token"]
    return f"{asset_href}?{token}"


def download_band(url, out_path):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)


if __name__ == "__main__":
    bbox = [85.7, 20.1, 85.9, 20.3]  # same Odisha region

    print("Searching Landsat scenes...")
    scenes = search_landsat(bbox)
    print(f"Found {len(scenes)} scenes")
    for s in scenes[:3]:
        print(" -", s["id"], "cloud:", s["properties"].get("eo:cloud_cover"))

    if not scenes:
        print("No scenes found, try relaxing max_cloud or bbox")
        exit()

    scene = scenes[0]
    print(f"\nUsing scene: {scene['id']}")

    os.makedirs("landsat_data", exist_ok=True)
    bands_needed = {"red": "red", "green": "green", "blue": "blue", "thermal": "lwir11"}
    print("Available assets:", list(scene["assets"].keys()))

    for label, asset_key in bands_needed.items():
        if asset_key not in scene["assets"]:
            print(f"Asset '{asset_key}' not found, skipping")
            continue

        href = scene["assets"][asset_key]["href"]
        signed_url = get_signed_url(href)
        out_path = f"landsat_data/{scene['id']}_{label}.TIF"
        print(f"Downloading {label}...")
        download_band(signed_url, out_path)
        print(f"Saved {out_path}")