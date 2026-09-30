import rasterio
from rasterio.warp import transform_bounds
from PIL import Image
import os

tiff_path = r'd:\Research_AI\Beki_storymap_and_dashboard\inputs\GIS-extras\testmap1.tiff'
output_dir = r'd:\Research_AI\Beki_storymap_and_dashboard\assets\layers'
os.makedirs(output_dir, exist_ok=True)

out_jpg = os.path.join(output_dir, 'political_map.jpg')

with rasterio.open(tiff_path) as src:
    print(f"Original CRS: {src.crs}")
    print(f"Original Bounds: {src.bounds}")
    
    # Transform bounds from EPSG:3857 to EPSG:4326 (WGS84 Lat/Lon)
    wgs84_bounds = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
    print(f"WGS84 Bounds (west, south, east, north): {wgs84_bounds}")
    
    # Read RGBA bands
    data = src.read()
    print(f"Raster shape: {data.shape}")

# Convert 4-band numpy array (C, H, W) to PIL Image
import numpy as np
# transpose from (C, H, W) to (H, W, C)
img_np = np.moveaxis(data, 0, -1)

# Create PIL Image
im = Image.fromarray(img_np)

# Convert RGBA to RGB for JPEG web loading
rgb = Image.new("RGB", im.size, (255, 255, 255))
if im.mode == 'RGBA':
    rgb.paste(im, mask=im.split()[3])
else:
    rgb.paste(im)

rgb.save(out_jpg, 'JPEG', quality=85)
print(f"Saved web image to {out_jpg}, size: {os.path.getsize(out_jpg)} bytes")

# Print exact Leaflet bounds
west, south, east, north = wgs84_bounds
print(f"Leaflet Bounds: [[{south:.6f}, {west:.6f}], [{north:.6f}, {east:.6f}]]")
