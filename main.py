import copy
from urllib import request
import webbrowser
import cv2
import numpy as np
import imageproc

CAMERA_URI = "http://192.168.1.238:4747/video"#?1920x1080"


def main():
    image_processing = imageproc.ImageProcessing()

    capture = cv2.VideoCapture(CAMERA_URI)
    while (True):
        # get image from ip cam
        ret, frame = capture.read()
        frame_show = copy.copy(frame)

        # preprocess image and get largest contour
        output_frame = image_processing.pre_process_image(image=frame)
        contour = image_processing.get_biggest_contour(output_frame)
        if len(contour) != 0:

            # get corners of largest contour
            approximation, corners = image_processing.get_corners(contour)


            if len(corners) != 0:
                reordered_approx = approximation.reshape((4,2))
                reordered_corners = image_processing.reorder_corners(reordered_approx)
                #frame_show = cv2.drawContours(frame_show, reordered_corners, -1, (0, 0, 255), 5)

                frame = image_processing.warp_image(frame, reordered_corners)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
