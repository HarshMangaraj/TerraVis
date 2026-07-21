import rasterio

# Path to the Blue band (B02) from your downloaded Sentinel-2 scene
path = "extracted/S2A_MSIL2A_20241207T045201_N0511_R076_T45QUC_20241207T074151.SAFE/GRANULE/L2A_T45QUC_A049408_20241207T050111/IMG_DATA/R10m/T45QUC_20241207T045201_B02_10m.jp2"

with rasterio.open(path) as src:
    print("Number of bands:", src.count)
    print("Width x Height (pixels):", src.width, "x", src.height)
    print("CRS (coordinate system):", src.crs)
    print("Resolution (meters/pixel):", src.res)
    print("Bounding box (real-world coords):", src.bounds)
    print("Data type:", src.dtypes)

    # Read the actual pixel data as a numpy array
    band_data = src.read(1)  # "1" = first (and only) band in this file
    print("Array shape:", band_data.shape)
    print("Min/Max pixel values:", band_data.min(), band_data.max())