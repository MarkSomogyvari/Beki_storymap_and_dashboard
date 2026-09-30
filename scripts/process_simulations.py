import glob
import os
import rasterio
import numpy as np
from PIL import Image

def process_flood_simulations():
    input_dir = r'd:\Research_AI\Beki_storymap_and_dashboard\inputs\flood_simulations'
    output_dir = r'd:\Research_AI\Beki_storymap_and_dashboard\assets\simulations'
    os.makedirs(output_dir, exist_ok=True)
    
    files = sorted(glob.glob(os.path.join(input_dir, '*.tif')))
    print(f"Found {len(files)} flood simulation files.")
    
    bounds_result = None
    
    for file_path in files:
        filename = os.path.basename(file_path)
        discharge_val = os.path.splitext(filename)[0]
        out_png = os.path.join(output_dir, f'sim_{discharge_val}.png')
        
        with rasterio.open(file_path) as src:
            if bounds_result is None:
                b = src.bounds
                bounds_result = [[b.bottom, b.left], [b.top, b.right]]
                print(f"Simulation WGS84 Bounds: {bounds_result}")
            
            data = src.read() # (3, H, W)
            
        # Reshape to (H, W, 3)
        rgb_arr = np.moveaxis(data, 0, -1)
        h, w, c = rgb_arr.shape
        
        # Create RGBA array with alpha channel
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = rgb_arr[:, :, :3]
        
        # Determine background pixels: white (255, 255, 255) or dark grey/black (< 50, < 50, < 50)
        r, g, b_ch = rgb_arr[:, :, 0], rgb_arr[:, :, 1], rgb_arr[:, :, 2]
        
        is_white = (r > 245) & (g > 245) & (b_ch > 245)
        is_dark_bg = (r < 50) & (g < 50) & (b_ch < 50)
        is_bg = is_white | is_dark_bg
        
        # Set alpha: 0 for background, 220 (approx 85% opacity) for flood hazard area
        rgba[:, :, 3] = np.where(is_bg, 0, 220)
        
        img = Image.fromarray(rgba, 'RGBA')
        img.save(out_png, 'PNG', optimize=True)
        print(f"Processed {filename} -> {out_png} ({os.path.getsize(out_png)} bytes)")

    print("ALL SIMULATION FILES PROCESSED SUCCESSFULLY!")

if __name__ == '__main__':
    process_flood_simulations()
