import copy

import cv2
import numpy as np

def get_coordinate_diff(c1, c2):
    x1 = c1[0]
    y1 = c1[1]

    x2 = c2[0]
    y2 = c2[1]

    x_diff_squared = (x1 - x2)**2
    y_diff_squared = (y1 - y2)**2
    distance = (x_diff_squared + y_diff_squared)**(1/2)
    return distance

class ImageProcessing:

    def __init__(self, card_width, card_height):
        self.KERNEL_SIZE = np.ones((5, 5))
        self.THRESHOLD_ADD = 100
        self.MIN_AREA_SIZE = 5000
        self.CARD_WIDTH = card_width
        self.CARD_HEIGHT = card_height


    def pre_process_image(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
        image_canny = cv2.Canny(image_blurred, 100, 150)
        # image_dilate = cv2.dilate(image_canny, self.KERNEL_SIZE, iterations=2)
        # image_erode = cv2.erode(image_dilate, self.KERNEL_SIZE, iterations=1)

        return image_canny

    def get_biggest_contour(self, pre_processed_image):
        biggest_area = -1
        biggest_contour = []
        contours, hier = cv2.findContours(pre_processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            contour_area = cv2.contourArea(contour)
            if contour_area > self.MIN_AREA_SIZE:
                if contour_area > biggest_area:
                    biggest_area = contour_area
                    biggest_contour = contour
        return biggest_contour

    def get_corners(self, contour):
        arc_length = cv2.arcLength(contour, True)
        approximation = cv2.approxPolyDP(contour, 0.05 * arc_length, True)
        if len(approximation) == 4:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            return approximation, box
        return []

    def reorder_corners(self, corners):
        ordered_points = np.zeros((4, 1, 2), np.int32)
        corner_points_sum = corners.sum(1)

        ordered_points[0] = corners[np.argmin(corner_points_sum)]


        diff_dictionary = {}
        for point in corners:
            coordinate_diff = get_coordinate_diff(point, ordered_points[0][0])
            if coordinate_diff != 0.0:
                diff_dictionary[coordinate_diff] = point

        for i, key in enumerate(sorted(diff_dictionary.keys())):
            ordered_points[(i+1)] = diff_dictionary.get(key)


        return ordered_points

    def warp_image(self, image, corners):
        source_points = np.float32(corners)
        destination_points = np.float32([[0, 0], [self.CARD_WIDTH, 0], [0, self.CARD_HEIGHT], [self.CARD_WIDTH, self.CARD_HEIGHT]])
        perspective_matrix = cv2.getPerspectiveTransform(source_points, destination_points)
        warped_image = cv2.warpPerspective(image, perspective_matrix, (self.CARD_WIDTH, self.CARD_HEIGHT))
        return warped_image

