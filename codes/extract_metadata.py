from PIL import Image

def read_png_metadata(file_path):
    # Open the image file
    with Image.open(file_path) as img:
        # Print basic metadata
        print(f"Format: {img.format}")
        print(f"Size: {img.size}")  # (width, height)
        print(f"Mode: {img.mode}")  # Color mode (e.g., RGB, RGBA, L)
        
        # Attempt to print more detailed metadata, if available
        if "dpi" in img.info:
            print(f"DPI: {img.info['dpi']}")
        if "icc_profile" in img.info:
            print("ICC Profile: Available")
        if "exif" in img.info:
            print("EXIF Data: Available")
        
        # Accessing PNG-specific chunks like tEXt, iTXt, etc., requires a more detailed approach,
        # potentially using another library or custom parsing based on the PNG specification.

# Replace 'path/to/your/image.png' with the actual path to your PNG file
file_path = 'path/to/your/image.png'
read_png_metadata(file_path)
