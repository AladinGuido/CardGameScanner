import io
import time

import cv2
import numpy as np
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.image import Image, CoreImage

import dbhelper
import imageproc
import playingcard

CAMERA_URI = "http://192.168.1.238:4747/video"  # ?1920x1080"
DB_PATH = "database/playing_cards.db"
MATCH_ON_FRAME = 30
BYPASS_STAGE_1 = False
BYPASS_STAGE_2 = False
SCAN_CARD = True


"""
def main(card_width, card_height, card_list):
    image_processing = imageproc.ImageProcessing(card_width, card_height)

    capture = cv2.VideoCapture(CAMERA_URI)
    frame_count = 0
    while True:
        # get image from ip cam
        ret, frame = capture.read()
        frame_show = copy.copy(frame)

        # preprocess image and get largest contour
        pre_processed_image = image_processing.pre_process_image(image=frame)
        contour = image_processing.get_biggest_contour(pre_processed_image)
        if len(contour) > 0:

            # get corners of largest contour
            approximation, corners = image_processing.get_corners(contour)

            if len(corners) != 0:
                reordered_approx = approximation.reshape((4, 2))
                reordered_corners = image_processing.reorder_corners(reordered_approx)
                # frame_show = cv2.drawContours(frame_show, reordered_corners, -1, (0, 0, 255), 5)

                warped_frame = image_processing.warp_image(frame, reordered_corners)
                warped_frame_gray = cv2.cvtColor(warped_frame, cv2.COLOR_BGR2GRAY)

                if frame_count == MATCH_ON_FRAME:
                    hist_match = {}
                    for card in card_list:
                        # hist_match[card.card_name] = card.template_match_inverted(warped_frame_gray)
                        hist_match[card.card_name] = card.check_match(warped_frame_gray)
                    sorted_dict = list(sorted(hist_match.items(), key=lambda item: item[1]))[-1]
                    print(sorted_dict)
                    frame_count = 0
                else:
                    frame_count += 1

        cv2.imshow('frame', frame_show)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
"""

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
                card_image_blob = card[3]
                card_list.append(playingcard.PlayingCard(
                    card_name=card_name,
                    card_description=card_description,
                    card_image=card_image,
                    card_image_blob=card_image_blob
                ))
        else:
            print("No cardgame found")
    except Exception as e:
        print("An error occured!")
        print(type(e))

    return card_width, card_height, card_list


class CardProcessor:
    def __init__(self, card_game_name):
        self.card_game_name = card_game_name
        self.card_with, self.card_height, self.card_list = fill_card_array(DB_PATH, "Frantic")
        self.image_processing = imageproc.ImageProcessing(self.card_with, self.card_height)
        self.capture = cv2.VideoCapture(CAMERA_URI)

    def scan_card(self, timeout):
        output_list = []
        frame_count = 0
        start_time = time.time()
        time_elapsed = 0
        while time_elapsed < timeout and len(output_list) < 3:
            ret, frame = self.capture.read()
            if ret:
                pre_processed_image = self.image_processing.pre_process_image(frame)
                contour = self.image_processing.get_biggest_contour(pre_processed_image)
                if len(contour) > 0:
                    # get corners of largest contour
                    approximation, corners = self.image_processing.get_corners(contour)

                    if len(corners) != 0:
                        reordered_approx = approximation.reshape((4, 2))
                        reordered_corners = self.image_processing.reorder_corners(reordered_approx)

                        warped_frame = self.image_processing.warp_image(frame, reordered_corners)
                        warped_frame_gray = cv2.cvtColor(warped_frame, cv2.COLOR_BGR2GRAY)

                        if frame_count == MATCH_ON_FRAME:
                            hist_match = {}
                            for card in self.card_list:
                                hist_match[card.card_name] = card.check_match(warped_frame_gray)
                            sorted_dict = list(sorted(hist_match.items(), key=lambda item: item[1]))[-1]
                            output_list.append(sorted_dict[0])
                            frame_count = 0
                        else:
                            frame_count += 1

            time_elapsed = time.time() - start_time


        return output_list

    def get_card_effect(self, card_name):
        for card in self.card_list:
            if card.card_name == card_name:
                return card.card_description

    def get_card_texture(self, card_name):
        for card in self.card_list:
            if card.card_name == card_name:
                blob = card.card_image_blob
                data = io.BytesIO(blob)
                img = CoreImage(data, ext="png").texture
                return img


class CardScanner(App):
    def build(self):
        self.title = "Card Scanner V1.0"
        self.root = Builder.load_file('card_scanner.kv')
        self.card_processor = CardProcessor("Frantic")
        self.image_widget = Image(source='empty.png')
        self.root.ids.image_display.add_widget(self.image_widget)

    def handle_scan_button(self):

        cards = self.card_processor.scan_card(10)
        highest_match = ""
        max_match_count = 0
        for card in cards:
            match_count = cards.count(card)
            if match_count > max_match_count:
                max_match_count = match_count
                highest_match = card

        card_effect = self.card_processor.get_card_effect(highest_match)
        self.root.ids.text_input_effect.text = card_effect

        #self.root.ids.card_picture.clear_widgets()
        print(self.root.ids.image_display)

        self.image_widget.texture = self.card_processor.get_card_texture(highest_match)

        self.root.ids.button_scan_card.text = 'Scan Card'




if __name__ == "__main__":
    CardScanner().run()
