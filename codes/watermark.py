import os
import argparse
from PIL import Image, ImageEnhance

def add_watermark(img, watermark, opacity, ratio, position):
    base = img.convert("RGBA")

    # Calculate watermark dimensions based on the target image and given ratio
    if len(ratio) == 1:
        shorter_side = min(img.width, img.height)
        watermark_scale = shorter_side * ratio[0]
        watermark_width = int(watermark.width * watermark_scale / max(watermark.width, watermark.height))
        watermark_height = int(watermark.height * watermark_scale / max(watermark.width, watermark.height))
    else:
        watermark_width = int(img.width * ratio[0])
        watermark_height = int(img.height * ratio[1])

    mark = watermark.convert("RGBA").resize((watermark_width, watermark_height), Image.ANTIALIAS)
    
    # Apply the opacity to the watermark
    alpha = mark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    mark.putalpha(alpha)

    x = int(position[0] * img.width)
    y = int(position[1] * img.height)

    # Check and adjust the watermark position to ensure it is within the image boundaries
    if x + watermark_width > img.width:
        x = img.width - watermark_width
    if y + watermark_height > img.height:
        y = img.height - watermark_height

    base.paste(mark, (x, y), mark)
    return base.convert("RGB")

def process_folder(folder, watermark_path, result_folder, opacity, ratio, position):
    watermark = Image.open(watermark_path)
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(os.path.join(root, file))
                result = add_watermark(img, watermark, opacity, ratio, position)

                if not result_folder:
                    result_folder = root
                os.makedirs(result_folder, exist_ok=True)

                result.save(os.path.join(result_folder, f'watermarked_{file}'))

def main():
    parser = argparse.ArgumentParser(description="Add watermark to images in a folder.")
    parser.add_argument("--folder", default="./WatermarkTest", help="Target folder to process")
    parser.add_argument("--opacity", default=0.5, type=float, help="Opacity of the watermark")
    parser.add_argument("--ratio", default=[0.1], nargs='+', type=float, help="Size of the watermark on the image, given as width_ratio and/or height_ratio")
    parser.add_argument("--position", default=[0.8,0.8], nargs=2, type=float, help="Position of the watermark on the image")
    parser.add_argument("--watermark_image", default="./WaterMark/Watermark.png", help="Path to the watermark image")
    parser.add_argument("--result_folder", default="./TmpWaterMarkResult", help="Folder to save result images (default: original folder)")

    args = parser.parse_args()

    process_folder(args.folder, args.watermark_image, args.result_folder, args.opacity, args.ratio, args.position)

if __name__ == "__main__":
    main()
