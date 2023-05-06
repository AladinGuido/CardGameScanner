import copy
import cv2
import numpy as np
import imageproc
import dbhelper
import playingcard

CAMERA_URI = "http://192.168.1.238:4747/video"  # ?1920x1080"
DB_PATH = "database/playing_cards_old.db"

def main(card_width, card_height, card_list):
    image_processing = imageproc.ImageProcessing(card_width, card_height)

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
                reordered_approx = approximation.reshape((4, 2))
                reordered_corners = image_processing.reorder_corners(reordered_approx)
                # frame_show = cv2.drawContours(frame_show, reordered_corners, -1, (0, 0, 255), 5)

                frame = image_processing.warp_image(frame, reordered_corners)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                hist_match = {}
                for card in card_list:
                    hist_match[card.card_name] = card.template_match(frame_gray)
                sorted_dict = list(sorted(hist_match.items(), key=lambda item: item[1]))[-1]
                print(sorted_dict)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


def fill_card_array(db_path, card_game_name):
    card_width = -1
    card_height = -1
    card_list = []
    try:
        db_helper = dbhelper.DBHelper(db_path)
        result_card_game = db_helper.query(f"SELECT * FROM card_game WHERE name = '{card_game_name}';")
        print(result_card_game)
        if len(result_card_game) != 0:

            card_game_id = result_card_game[0][0]
            card_width = result_card_game[0][3]
            card_height = result_card_game[0][4]
            cards = db_helper.query(f"SELECT * FROM cards WHERE card_game = '{card_game_id}'")

            for card in cards:
                card_name = card[1]
                card_description = card[2]
                card_np_array = np.frombuffer(card[3], np.uint8)
                card_image = cv2.imdecode(card_np_array, cv2.IMREAD_COLOR)
                card_list.append(playingcard.PlayingCard(
                    card_name=card_name,
                    card_description=card_description,
                    card_image=card_image
                ))
        else:
            print("No cardgame found")
    except Exception as e:
        print("An error occured!")
        print(type(e))

    return card_width, card_height, card_list


if __name__ == "__main__":
    #card_width, card_height, card_list = fill_card_array(DB_PATH, "Frantic")
    #main(card_width, card_height, card_list)
    db = dbhelper.DBHelper(DB_PATH)
    result = db.query("SELECT * FROM card_game;")
    print(result)

