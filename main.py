import copy
import cv2
import imageproc
import dbhelper

CAMERA_URI = "http://192.168.1.238:4747/video"#?1920x1080"
DB_PATH = "database/playing_cards.db"


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

def fill_card_array(db_path, card_game_name):
    try:
        db_helper = dbhelper.DBHelper(db_path)
        result_card_game = db_helper.query(f"SELECT * FROM card_game WHERE name = '{card_game_name}';")
        if len(result_card_game) != 0:
            card_game_id = result_card_game[0][0]
            cards = db_helper.query(f"SELECT * FROM cards WHERE card_game = '{card_game_id}'")
            print(cards)
        else:
            print("No cardgame found")
    except Exception as e:
        print("An error occured!")
        print(type(e))

if __name__ == "__main__":
    #main()
    fill_card_array(DB_PATH, "Frantic")

    #
    # CARD_GAME_ID = result[0][0]
    # result
    # np_array = np.frombuffer(result[0][3], np.uint8)
    # image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    # cv2.imshow('Image', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print(result[0])
