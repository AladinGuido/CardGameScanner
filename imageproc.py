import cv2
import numpy as np


class ImageProcessing:

    def __init__(self):
        self.KERNEL_SIZE = np.ones((5, 5))
        self.THRESHOLD_ADD = 100

    def pre_process_image(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
        image_canny = cv2.Canny(image_blurred, 100, 150)
        #image_dilate = cv2.dilate(image_canny, self.KERNEL_SIZE, iterations=2)
        #image_erode = cv2.erode(image_dilate, self.KERNEL_SIZE, iterations=1)

        return image_canny

    def get_corners(self, pre_processed_image):
        cnts, hier = cv2.findContours(pre_processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        index_sort = sorted(range(len(cnts)), key=lambda i: cv2.contourArea(cnts[i]), reverse=True)
        print(index_sort)