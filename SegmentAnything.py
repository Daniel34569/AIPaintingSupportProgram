from segment_anything import SamPredictor, sam_model_registry
import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import time
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QImage, QPen
from PyQt5.QtCore import Qt, QPoint

sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"


sam = sam_model_registry[model_type](checkpoint=f"./{sam_checkpoint}")
print(f"Sam Success")
sam.to(device="cuda")
predictor = SamPredictor(sam)
print(f"Predictor Success")

input_img = cv2.imread("./sam_input.png")
input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)

start_time = time.time()
predictor.set_image(input_img)
input_point = np.array([[461, 185]])
input_label = np.array([1])
masks, _, _ = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True,
)
end_time = time.time()

print(masks.shape,'masks.shape')
elapsed_time = end_time - start_time  # Calculate the difference which is the execution time

print(f'The time taken by the code is {elapsed_time} seconds.')

cv2.imwrite("./sam_res0.png",(masks[0] * 255).astype('uint8'))
cv2.imwrite("./sam_res1.png",(masks[1] * 255).astype('uint8'))
cv2.imwrite("./sam_res2.png",(masks[2] * 255).astype('uint8'))