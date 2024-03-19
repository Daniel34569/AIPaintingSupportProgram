from PIL import Image
import piexif
import piexif.helper
import os
import argparse

IGNORED_INFO_KEYS = {
    'jfif', 'jfif_version', 'jfif_unit', 'jfif_density', 'dpi', 'exif',
    'loop', 'background', 'timestamp', 'duration', 'progressive', 'progression',
    'icc_profile', 'chromaticity', 'photoshop',
}

#def read_info_from_image(image: Image.Image) -> tuple[str | None, dict]:
def read_info_from_image(file_path):
    with Image.open(file_path) as image:
        items = (image.info or {}).copy()

        geninfo = items.pop('parameters', None)

        if "exif" in items:
            exif = piexif.load(items["exif"])
            exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b'')
            try:
                exif_comment = piexif.helper.UserComment.load(exif_comment)
            except ValueError:
                exif_comment = exif_comment.decode('utf8', errors="ignore")

            if exif_comment:
                items['exif comment'] = exif_comment
                geninfo = exif_comment

        for field in IGNORED_INFO_KEYS:
            items.pop(field, None)

        if items.get("Software", None) == "NovelAI":
            try:
                json_info = json.loads(items["Comment"])
                sampler = sd_samplers.samplers_map.get(json_info["sampler"], "Euler a")

                geninfo = f"""{items["Description"]}
    Negative prompt: {json_info["uc"]}
    Steps: {json_info["steps"]}, Sampler: {sampler}, CFG scale: {json_info["scale"]}, Seed: {json_info["seed"]}, Size: {image.width}x{image.height}, Clip skip: 2, ENSD: 31337"""
            except Exception:
                errors.report("Error parsing NovelAI image generation parameters", exc_info=True)

        return geninfo, items

def read_png_metadata_and_save_to_txt(input_dir, output_dir, is_output_to_one_file):
    
    for file_path in os.listdir(input_dir):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            metadata, _ = read_info_from_image(os.path.join(input_dir, file_path))
            #print(a)

            base_filename = os.path.splitext(file_path)[0]
            if(is_output_to_one_file):
                output_file_path = os.path.join(output_dir, f"{os.path.splitext(input_dir)[0]}.txt")
            else:
                output_file_path = os.path.join(output_dir, f"{base_filename}.txt")
            
            # Write the metadata to a text file
            if(is_output_to_one_file):
                with open(output_file_path, 'a', encoding='utf-8') as f:
                    f.write('Filename:\n')
                    f.write(file_path)
                    f.write('\n\n')
                    f.write(metadata)
                    f.write('\n\n')
            else:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(metadata)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract metadata and save to txt")
    parser.add_argument("--input_dir", default="./Test", help="Target folder to process")
    parser.add_argument("--result_folder", default="./Test_result", help="Folder to save result")
    parser.add_argument("--is_output_to_one_file", default=False, type=bool, help="Is output all metadata into one txt")

    args = parser.parse_args()
    read_png_metadata_and_save_to_txt(args.input_dir, args.result_folder, args.is_output_to_one_file)