import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QWidget, QTextEdit
from PyQt5.QtGui import QPainter, QImage, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint
import numpy as np
import cv2
from segment_anything import SamPredictor, sam_model_registry
import torch
import time
import os
import argparse
from pathlib import Path

def get_images(directory):
    file_list = []
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jfif"):
            file_list.append(os.path.join(directory, filename))
    return file_list

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.points = []
        self.point_labels = []
        self.blue_pen = QPen(Qt.blue, 8, Qt.SolidLine)
        self.red_pen = QPen(Qt.red, 8, Qt.SolidLine)
        self.setScaledContents(True)

    def setImage(self, image_path):
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        self.setPixmap(self.pixmap)
        self.origin_input_img = cv2.imread(image_path)
        self.origin_input_img = cv2.cvtColor(self.origin_input_img, cv2.COLOR_BGR2RGB)
        height, width, _ = self.origin_input_img.shape
        self.blue_pen = QPen(Qt.blue, int(min(height, width) * 0.02), Qt.SolidLine)
        self.red_pen = QPen(Qt.red, int(min(height, width) * 0.02), Qt.SolidLine)
        print(f"Set Image with shape:{self.origin_input_img.shape}")
        predictor.set_image(self.origin_input_img)
        print(f"Set Image Success")

    def updatePixmap(self):
        # Modify the pixmap here
        if len(self.points) > 0:
            mask = self.get_mask()
            self.blend_mask(mask)
        painter = QPainter(self.pixmap)
        for point, point_label in zip(self.points, self.point_labels):
            if point_label == 0:
                painter.setPen(self.red_pen)
            elif point_label == 1:
                painter.setPen(self.blue_pen)
            painter.drawPoint(point)
        painter.end()
        self.setPixmap(self.pixmap)  # Update the pixmap

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    def mousePressEvent(self, event):
        self.points.append(event.pos())
        if event.buttons() == Qt.LeftButton:
            self.point_labels.append(1)
        elif event.buttons() == Qt.RightButton:
            self.point_labels.append(0)
        self.updatePixmap()
        self.repaint()

    def revert_point(self):
        if len(self.points) > 0:
            self.points = self.points[:-1]
            self.point_labels = self.point_labels[:-1]
        if len(self.points) == 0:
            self.reset_image()
        self.updatePixmap()
    
    def reset_image(self):
        self.points = []
        self.point_labels = []
        np_img = cv2.resize(self.origin_input_img, (self.pixmap.width(), self.pixmap.height()))[:, :, [2, 1, 0]]
        np_img = self.numpy_to_qpixmap(np_img)
        self.pixmap = np_img
        self.updatePixmap()

    def get_mask(self):
        x_ratio = self.origin_input_img.shape[1] / self.width()
        y_ratio = self.origin_input_img.shape[0] / self.height()
        input_points = np.array([[int(point.x() * x_ratio), int(point.y() * y_ratio)] for point in self.points])
        input_label = np.array([point for point in self.point_labels])
        #print(f"Input points :{input_points}")
        #print(f"Input label :{input_label}")
        start_time = time.time()
        masks, _, _ = predictor.predict(
            point_coords=input_points,
            point_labels=input_label,
            multimask_output=True,
        )
        end_time = time.time()
        elapsed_time = end_time - start_time  # Calculate the difference which is the execution time
        print(f'The time taken by the code is {elapsed_time} seconds.')
        return masks[current_mask_type]

    def blend_mask(self):
        mask = self.get_mask()
        img = cv2.imread(self.image_path)
        overlay = np.full_like(img, (255,0,0), dtype=np.uint8)
        cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img, mask.astype(np.uint8))
        self.pixmap = QPixmap.fromImage(QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888))
        self.setPixmap(self.pixmap)

    def save_masked_image(self):
        global output_path
        if len(self.points) == 0:
            mask = np.ones(self.origin_input_img.shape[:2])
        else:
            mask = self.get_mask()
        alpha_channel = (mask * 255).astype('uint8')
        print(alpha_channel.shape)
        bgra_image = np.dstack((self.origin_input_img[:, :, [2, 1, 0]], alpha_channel))
        mask_4c = cv2.cvtColor(alpha_channel, cv2.COLOR_GRAY2BGRA)
        bgra_image[mask_4c==0] = 0
        image_path = Path(self.image_path)
        filename = image_path.name

        # check if the file is a .jfif file
        if image_path.suffix.lower() == '.jfif':
            # change the extension to .png
            filename = filename.replace('.jfif', '.png')

        output_filename = os.path.join(output_path, filename)
        cv2.imwrite(output_filename, bgra_image)

    def blend_mask(self, mask):
        # Resize the mask to match the pixmap size
        mask = cv2.resize((mask * 255).astype('uint8'), (self.pixmap.width(), self.pixmap.height()))
        
        np_img = cv2.resize(self.origin_input_img, (self.pixmap.width(), self.pixmap.height()))[:, :, [2, 1, 0]]
        
        # Convert the 1-channel mask to a 3-channel mask
        mask_3c = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
        # Blend the numpy array with the mask
        overlay = np.full_like(np_img, (0,0,255), dtype=np.uint8)
        
        # Where mask is 1, blend the image with overlay; otherwise, keep original color
        np_img[mask_3c==255] = (0.7 * overlay[mask_3c==255] + 0.3 * np_img[mask_3c==255]).astype(np.uint8)

        # Convert the blended numpy array back to a QImage, then to a QPixmap
        blended_pixmap = self.numpy_to_qpixmap(np_img)
        
        self.pixmap = blended_pixmap
        #self.setPixmap(self.pixmap)

    def numpy_to_qpixmap(self, np_img):
        height, width, channel = np_img.shape
        bytesPerLine = channel * width
        np_data = np_img.data.tobytes()  # convert memoryview to bytes
        if channel == 3:
            # BGR format
            q_img = QImage(np_data, width, height, bytesPerLine, QImage.Format_RGB888)
        elif channel == 4:
            # BGRA format
            q_img = QImage(np_data, width, height, bytesPerLine, QImage.Format_ARGB32)
        else:
            raise ValueError(f'Unsupported number of channels: {channel}')

        q_img = q_img.rgbSwapped()
        qpixmap = QPixmap.fromImage(q_img)
        return qpixmap

    def qimage_to_numpy(self, qimage):
        print(qimage.format(),' format')
        qimage = qimage.convertToFormat(QImage.Format_ARGB32)
        width = qimage.width()
        height = qimage.height()
        bytesPerLine = 4 * width
        ptr = qimage.bits()
        ptr.setsize(height * bytesPerLine)
        np_img = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        # Convert RGB to BGR
        np_img = np_img[:, :, [0, 1, 2]]
        return np_img


class MainWindow(QMainWindow):
    def __init__(self, image_paths):
        super().__init__()
        self.image_paths = image_paths
        self.current_image_index = 0

        self.image_label = ImageLabel()
        self.next_button = QPushButton('Next (d)', self)
        self.prev_button = QPushButton('Prev (a)', self)
        self.save_button = QPushButton('Save (s)', self)

        self.next_button_mask = QPushButton('Next MaskType (q)', self)
        self.prev_button_mask = QPushButton('Prev MaskType (e)', self)
        self.revert_point_button = QPushButton('Revert Point (r)', self)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setText("Show the status here")

        self.initUI()

    def initUI(self):
        self.next_button.clicked.connect(self.next_image)
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button_mask.clicked.connect(lambda: self.modifyModelType(True))
        self.prev_button_mask.clicked.connect(lambda: self.modifyModelType(False))
        self.revert_point_button.clicked.connect(self.revert_point)
        self.save_button.clicked.connect(self.save_image)

        large_hbox = QHBoxLayout()

        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        
        sub_vbox = QVBoxLayout()
        
        #Add button to control image
        hbox = QHBoxLayout()
        hbox.addWidget(self.prev_button)
        hbox.addWidget(self.next_button)
        sub_vbox.addLayout(hbox)

        #Add button to control mask type
        hbox_mask = QHBoxLayout()
        hbox_mask.addWidget(self.next_button_mask)
        hbox_mask.addWidget(self.prev_button_mask)
        hbox_mask.addWidget(self.revert_point_button)
        sub_vbox.addLayout(hbox_mask)



        sub_vbox.addWidget(self.save_button)
        
        large_hbox.addLayout(sub_vbox)
        large_hbox.addWidget(self.status_text)
        vbox.addLayout(large_hbox)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.load_image()
        self.showStatus()

    def load_image(self):
        self.image_label.setImage(self.image_paths[self.current_image_index])
        self.image_label.points = []

    def next_image(self):
        if self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.load_image()
            self.showStatus()

    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()
            self.showStatus()

    def save_image(self):
        self.image_label.save_masked_image()

    def revert_point(self):
        self.image_label.revert_point()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.prev_image()
        elif event.key() == Qt.Key_D:
            self.next_image()
        elif event.key() == Qt.Key_S:
            self.save_image()
        elif event.key() == Qt.Key_Q:
            self.modifyModelType(False)
        elif event.key() == Qt.Key_E:
            self.modifyModelType(True)
        elif event.key() == Qt.Key_R:
            self.revert_point()
        self.showStatus()
    
    def modifyModelType(self, is_add):
        global current_mask_type
        current_mask_type = current_mask_type + (1 if is_add else -1)
        if current_mask_type == -1:
            current_mask_type = 2
        elif current_mask_type == 3:
            current_mask_type = 0
        self.image_label.updatePixmap()
        self.showStatus()
    
    def showStatus(self):
        self.status_text.clear()
        self.status_text.append(f"Model type : {model_type}")
        self.status_text.append(f"Mask : {current_mask_type}")
        self.status_text.append(f"Image Index : {self.current_image_index + 1}/{len(self.image_paths)}")

def main(image_paths):
    app = QApplication(sys.argv)
    win = MainWindow(image_paths)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add watermark to images in a folder.")
    parser.add_argument("--input_dir", default="./seg_test", help="Target folder to process")
    parser.add_argument("--result_folder", default="./seg_testOut", help="Folder to save result images (default: original folder)")

    args = parser.parse_args()

    #image_paths = ["a.png", "b.png", "sam_input.png"]  # Replace with your image paths
    image_paths = get_images(args.input_dir)
    if len(image_paths) == 0:
        print("Path is Empty!!")
        exit()

    output_path = args.result_folder
    os.makedirs(output_path, exist_ok=True)

    sam_checkpoint = "sam_vit_h_4b8939.pth"
    model_type = "vit_h"
    sam = sam_model_registry[model_type](checkpoint=f"./{sam_checkpoint}")
    print(f"Sam Success")
    sam.to(device="cuda")
    predictor = SamPredictor(sam)
    print(f"Predictor Success")

    current_mask_type = 0

    main(image_paths)
