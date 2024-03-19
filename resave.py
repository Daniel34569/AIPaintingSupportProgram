import os
import cv2
import argparse

#./../H/Select/implacable breasts out/To18837

# Add command line arguments
parser = argparse.ArgumentParser(description="Process PNG files")
parser.add_argument('--result_type', type=str, default='png', help='Result type (default: png)')
parser.add_argument('--input_dir', type=str, default='./tmp', help='Input directory (default: ./)')
parser.add_argument('--shrink_ratio', type=float, default=1.0, help='Shrink ratio for resizing the image (default: 1.0)')
parser.add_argument('--resize_to_px', type=int, default=-1, help='Resize to target px (will replace shrink_ratio)')
parser.add_argument('--seperate_vertical', type=int, default=1, help='Seperate image vertical')
args = parser.parse_args()

# Set the directory path containing the PNG files
dir_path = args.input_dir

# Get all PNG files in the directory
png_files = [f for f in os.listdir(dir_path) if f.endswith('.png')]

# Loop through each PNG file and save it with a new name
for i, file in enumerate(png_files):
    # Read the image
    img = cv2.imread(os.path.join(dir_path, file))
    
    # Resize the image using the shrink ratio
    if args.resize_to_px != -1:
        new_width = args.resize_to_px
        new_height = args.resize_to_px
        ratio = max(new_width / img.shape[1], new_height / img.shape[0])
    else:
        new_width = int(img.shape[1] * args.shrink_ratio)
        new_height = int(img.shape[0] * args.shrink_ratio)
        ratio = args.shrink_ratio
    if ratio > 1.0:
        interpolation_method=cv2.INTER_CUBIC
    elif ratio < 1.0:
        interpolation_method=cv2.INTER_AREA
    
    if args.shrink_ratio != 1.0 or args.resize_to_px != -1:
        print("Resize to target width:%d, height:%d, interpolation:%s"%(new_width, new_height, interpolation_method))
        resized_img = cv2.resize(img, (new_width, new_height), interpolation=interpolation_method)

    # Save the image with a new name
    new_name = str(i+1) + '.' + args.result_type
    if args.shrink_ratio != 1.0 or args.resize_to_px != -1:
        if args.seperate_vertical > 1:
            img_width = resized_img.shape[1]
            img_height = resized_img.shape[0]
            per_height = img_height / args.seperate_vertical
            for j in range(args.seperate_vertical):
                cv2.imwrite(os.path.join(dir_path, new_name), resized_img[per_height * j: per_height * j + per_height,:,:])
        else:
            cv2.imwrite(os.path.join(dir_path, new_name), resized_img)
    else:
        if args.seperate_vertical > 1:
            img_width = img.shape[1]
            img_height = img.shape[0]
            per_height = int(img_height / args.seperate_vertical)
            print("Separate to %d part vertical!, each part is width : %d, height : %d"%(args.seperate_vertical, img_width, per_height))
            for j in range(args.seperate_vertical):
                new_name = str(i+1) + '_' + str(j) + '.' + args.result_type
                cv2.imwrite(os.path.join(dir_path, new_name), img[per_height * j: per_height * j + per_height,:,:])
        else:
            cv2.imwrite(os.path.join(dir_path, new_name), img)
    # Free up memory by deleting the image object
    del img
    if args.shrink_ratio != 1.0 or args.resize_to_px != -1:
        del resized_img