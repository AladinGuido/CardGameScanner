import cv2

import imageproc

CAMERA_URI = "http://192.168.1.238:4747/video"

def main():

    image_processing = imageproc.ImageProcessing()

    capture = cv2.VideoCapture(CAMERA_URI)
    while (True):
        ret, frame = capture.read()
        output_frame = image_processing.pre_process_image(image=frame)
        image_processing.get_corners(output_frame)

        cv2.imshow('frame', output_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()