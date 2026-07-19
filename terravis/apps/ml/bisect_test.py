import requests

base = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

queries = {
    "1_collection_only": "Collection/Name eq 'SENTINEL-2'",
    "2_plus_producttype": "Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A')",
    "3_plus_intersects": "Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((85.7 20.1,85.9 20.1,85.9 20.3,85.7 20.3,85.7 20.1))')",
    "4_plus_cloudcover": "Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((85.7 20.1,85.9 20.1,85.9 20.3,85.7 20.3,85.7 20.1))') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value gt 60 and att/OData.CSC.DoubleAttribute/Value lt 80)",
    "4b_cloudcover_single_condition": "Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((85.7 20.1,85.9 20.1,85.9 20.3,85.7 20.3,85.7 20.1))') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 80)",
}

for label, filt in queries.items():
    url = f"{base}?$filter={filt}&$top=2"
    resp = requests.get(url)
    print(f"{label}: status {resp.status_code}")
    if resp.status_code != 200:
        print("  ERROR:", resp.text[:300])
    else:
        print("  OK, got", len(resp.json().get("value", [])), "results")