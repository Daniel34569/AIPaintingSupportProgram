import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import argparse

from mosiac_util import * 

class ImageProcessor:
    def __init__(self, select_roi_shrink_ratio, image_dir):
        self.select_roi_shrink_ratio = select_roi_shrink_ratio
        self.image_dir = image_dir
        self.image_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')])
        self.current_image_index = 0
        self.image = None
        self.tk_image = None
        self.create_ui()

    def create_ui(self):
        self.window = tk.Tk()

        self.canvas = tk.Canvas(self.window, width=500, height=500)
        self.canvas.pack()

        self.prev_button = tk.Button(self.window, text="<< Prev", command=self.load_prev_image)
        self.prev_button.pack(side=tk.LEFT)

        self.process_button = tk.Button(self.window, text="Process", command=self.process_image)
        self.process_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.window, text="Next >>", command=self.load_next_image)
        self.next_button.pack(side=tk.LEFT)

        self.load_image()

    def load_image(self):
        img_path = self.image_files[self.current_image_index]
        img = Image.open(img_path)
        self.image = img.resize((int(img.width*self.select_roi_shrink_ratio), int(img.height*self.select_roi_shrink_ratio)))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

    def load_next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.load_image()

    def load_prev_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
        self.load_image()

    def process_image(self):
        print(f'Processing image {self.image_files[self.current_image_index]}')
        # Here you need to include the code that will process the image using the 4 points

    def run(self):
        self.window.mainloop()

# Define global variables
drawing = False
ix, iy = -1, -1
points = []
current_file = 0
file_list = []
select_roi_shrink_ratio = 0.8
line_points = []
output_path = None
original_img = None
current_image = None
original_size_img = None
exit_count = 0
current_window_width = 0
current_window_height = 0
pixel_size = -1

def draw_lines(event, x, y, flags, param):
    global drawing, ix, iy, line_points, current_image, points

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            dist = np.sqrt((ix - x)**2 + (iy - y)**2)
            if dist > 0.01*min(original_img.shape[:2]):
                temp_img = original_img.copy()
                cv2.line(temp_img, (ix, iy), (x, y), (0, 255, 0), 5)
                cv2.imshow('Image window', temp_img)
                current_image = temp_img

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.line(original_img, (ix, iy), (x, y), (0, 255, 0), 5)
        points.append((ix, iy))
        points.append((x, y))
        line_points.append((ix, iy))
        line_points.append((x, y))
        current_image = original_img

def get_images(directory):
    global file_list

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            file_list.append(os.path.join(directory, filename))

def process_image():
    global points, img, current_file, output_path, src_img, original_size_img, select_roi_shrink_ratio

    if len(points) >= 4:
        #print(points, 'points')
        #img = mosaic_roi(img, [points[i:i+2] for i in range(0, len(points), 2)], pixel_size=-1)
        #img = mosaic_roi(src_img, tuple([list(t) for t in points]), pixel_size=-1)
        img_processed = mosaic_roi(original_size_img, tuple([[val / select_roi_shrink_ratio for val in t]for t in points[:4]]), pixel_size=pixel_size)
        loop_count = 1
        while len(points) - loop_count * 4 >= 4:
            img_processed = mosaic_roi(img_processed, tuple([[val / select_roi_shrink_ratio for val in t]for t in points[4 * loop_count: 4 * loop_count + 4]]), pixel_size=pixel_size)
            loop_count += 1
        cv2.imwrite(output_path + '\\' +file_list[current_file].split('\\')[-1], img_processed)
        #print(output_path + '\\' +file_list[current_file].split('\\')[-1])
        img_processed = cv2.resize(img_processed, (img.shape[1], img.shape[0]))
        cv2.imshow('Image window', img_processed)
        cv2.waitKey(0)
        cv2.destroyWindow('Image window')
        change_image(1)
        points = []

def change_image(step):
    global current_file, img, file_list, select_roi_shrink_ratio, original_img, current_image, exit_count, original_size_img, current_window_width, current_window_height

    current_file = (current_file + step)
    if current_file >= len(file_list):
        print("Last Image of the dir, exit...")
        exit()
    if current_file < 0:
        print("First Image of the dir, exit...")
        exit()
    """
    if current_file >= len(file_list):
        print("Last Image of the dir, press again to exit...")
        while(1):
            key = cv2.waitKey(1) & 0xFF
            if key == ord('d'): # 'n' key for next image
                exit()
            elif key == ord('a'): # 'p' key for previous image
                current_file = current_file - 1
                break
            elif key == 27: # 'ESC' key to exit
                exit()
    elif current_file < 0:
        print("First Image of the dir, press again to exit...")
        while(1):
            key = cv2.waitKey(1) & 0xFF
            if key == ord('d'): # 'n' key for next image
                current_file = current_file + 1
                break
            elif key == ord('a'): # 'p' key for previous image
                exit()
            elif key == 27: # 'ESC' key to exit
                exit()
    """
    print(f"Processing file [{current_file + 1} / {len(file_list)}]")
    img = cv2.imread(file_list[current_file])
    max_size = (int(img.shape[1]*select_roi_shrink_ratio), int(img.shape[0]*select_roi_shrink_ratio))
    print(max_size, 'Max size')
    original_size_img = img.copy()
    img = cv2.resize(img, max_size)
    original_img = img.copy()
    current_image = original_img.copy()
    cv2.namedWindow('Image window', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image window', draw_lines)
    if current_window_width == 0 and current_window_height == 0:
        current_window_width = current_image.shape[1]
        current_window_height = current_image.shape[0]
        cv2.resizeWindow('Image window', current_window_width, current_window_height)
    else:
        current_window_width = current_image.shape[1]
        current_window_height = current_image.shape[0]


def revert_line():
    global img, line_points, original_img, points, current_image

    if len(points) >= 2:
        #original_img = cv2.resize(img_processed, (img.shape[1], img.shape[0])).copy()
        original_img = img.copy()
        for i in range(0, len(points)-2, 2):
            cv2.line(original_img, points[i], points[i+1], (0, 255, 0), 5)
        points = points[:-2]
        current_image = original_img

if __name__ == '__main__':
    print("Welcome to use Mosaic tool!")
    print("Press a to change to previous image, d to change to next image")
    print("Press r to revert last line")
    print("Press space key to return to original image size * shrink ratio")
    print("Press s to process mosaic")
    print("Press ESC to exit")

    parser = argparse.ArgumentParser(description="Add watermark to images in a folder.")
    parser.add_argument("--input_dir", default="./WatermarkTest", help="Target folder to process")
    parser.add_argument("--result_folder", default="./TmpWaterMarkResult", help="Folder to save result images (default: original folder)")
    parser.add_argument("--select_roi_shrink_ratio", default=-1, type=float, help="Shrink ratio for the ROI selection window.")
    parser.add_argument("--pixel_size", default=-1, type=int, help="Mosaic size")

    args = parser.parse_args()

    get_images(args.input_dir)
    output_path = args.result_folder
    os.makedirs(output_path, exist_ok=True)
    if args.select_roi_shrink_ratio > 0 :
        select_roi_shrink_ratio = args.select_roi_shrink_ratio
    if args.pixel_size > 0 :
        pixel_size = args.pixel_size

    change_image(0)

    while(1):
        cv2.namedWindow('Image window', cv2.WINDOW_NORMAL)
        cv2.imshow('Image window', current_image)
        cv2.setMouseCallback('Image window', draw_lines)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('d'): # 'n' key for next image
            cv2.destroyWindow('Image window')
            change_image(1)
        elif key == ord('a'): # 'p' key for previous image
            cv2.destroyWindow('Image window')
            change_image(-1)
        elif key == ord('s'): # 's' key to process current image
            process_image()
        elif key == ord('r'): # 'p' key for previous image
            revert_line()
        elif key == 32: # space key to resume original image size
            cv2.resizeWindow('Image window', current_window_width, current_window_height)
        elif key == 27: # 'ESC' key to exit
            break

    cv2.destroyAllWindows()