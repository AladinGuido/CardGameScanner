import copy

import cv2


class PlayingCard:
    def __init__(self, card_name, card_description, card_image, card_image_blob):
        self.card_name = card_name
        self.card_description = card_description
        self.card_image = card_image
        self.card_image_blob = card_image_blob
        self.card_image_gray = cv2.cvtColor(copy.copy(card_image), cv2.COLOR_BGR2GRAY)

    def template_match(self, image):
        result = cv2.matchTemplate(image, self.card_image_gray, cv2.TM_CCOEFF_NORMED)
        return result

    def template_match_inverted(self, image):
        image_inverted = cv2.bitwise_not(image)
        template_inverted = cv2.bitwise_not(self.card_image_gray)
        result = cv2.matchTemplate(image_inverted, template_inverted, cv2.TM_CCOEFF_NORMED)
        return result

    def check_match(self, image):
        coeff = []
        coeff.append(cv2.matchTemplate(image, self.card_image_gray, cv2.TM_CCOEFF_NORMED))
        coeff.append(cv2.matchTemplate(cv2.rotate(image, cv2.ROTATE_180), self.card_image_gray, cv2.TM_CCOEFF_NORMED))

        coeff.append(cv2.matchTemplate(cv2.flip(image, 0), self.card_image_gray, cv2.TM_CCOEFF_NORMED))
        coeff.append(cv2.matchTemplate(cv2.rotate(cv2.flip(image, 0), cv2.ROTATE_180), self.card_image_gray, cv2.TM_CCOEFF_NORMED))

        match_score = sorted(coeff)[-1]
        return match_score
