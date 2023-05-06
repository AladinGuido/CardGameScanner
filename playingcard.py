import copy

import cv2


class PlayingCard:
    def __init__(self, card_name, card_description, card_image):
        self.card_name = card_name
        self.card_description = card_description
        self.card_image = card_image
        self.card_image_gray = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)

    def template_match(self, image):
        result = cv2.matchTemplate(image, self.card_image_gray, cv2.TM_CCOEFF_NORMED)
        return result
