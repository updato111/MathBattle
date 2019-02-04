import cv2
import pyautogui
import time
import random
import numpy as np


class OperationResolver():

    __author__ : "EnriqueMoran"

    def __init__(self):
        self.one = "./images/numbers/one.png"
        self.two = "./images/numbers/two.png"
        self.three = "./images/numbers/three.png"
        self.four = "./images/numbers/four.png"
        self.five = "./images/numbers/five.png"
        self.six = "./images/numbers/six.png"
        self.seven = "./images/numbers/seven.png"
        self.eight = "./images/numbers/eight.png"
        self.nine = "./images/numbers/nine.png"
        self.zero = "./images/numbers/zero.png"
        self.equals = "./images/symbols/equals.png"
        self.plus = "./images/symbols/plus.png"
        self.minus = "./images/symbols/minus.png"
        self.multiplication = "./images/symbols/multiplication.png"
        self.division = "./images/symbols/division.png"
        self.right = "./images/symbols/right.png"
        self.wrong = "./images/symbols/wrong.png"
        self.play = "./images/symbols/play.png"
        self.retry = "./images/symbols/retry.png"
        self.matchTemplateMethod = eval('cv2.TM_CCOEFF_NORMED')    # Placing this here saves time (avoid multiple eval)


    def getPosition(self, itemPath, image):    # Get right button position and confidence score
        game = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        item = cv2.imread(itemPath, 0)
        match = cv2.matchTemplate(game,item, self.matchTemplateMethod)
        w, h = item.shape[::-1]
        _, max_val, _, top_left = cv2.minMaxLoc(match)
        position = (top_left[0] + ((top_left[0] + w) / 2), top_left[1] + (top_left[1] + h) / 2)
        return position, max_val


    def getPositions(self, image):
        positions = {self.one:None, self.two:None, self.three:None, self.four:None, self.five:None, self.six:None, self.seven:None, 
        self.eight:None, self.nine:None, self.zero:None, self.equals:None, self.plus:None, self.minus:None, self.multiplication:None,
        self.division:None, self.right:None, self.wrong:None, self.play:None, self.retry:None}

        for itemPath in positions.keys():
            newPosition, confidence = self.getPosition(itemPath, image)
            if confidence < 0.9:
                positions[itemPath] = None
            else:
                positions[itemPath] = newPosition
        res = {key : value for (key, value) in positions.items() if value}    # Dict with non None elements
        return res


    def sortPositions(self, positions):    # Sort elements from left to right
        res = {}
        sorted_keys = sorted(positions, key=positions.get)
        for key in sorted_keys:
            res[key] = positions[key]
        return res


    def getRightSideElements(self, positions, element):    # Return elements that are at element's right side
        res = {}
        for item, position in positions.items():
            if item != element:
                if position[0] > positions[element][0] and (abs(position[1] - positions[element][1]) < 25):
                    res[item] = position
        return res


    def getLeftSideElements(self, positions, element):    # Return elements that are at element's left side
        res = {}
        for item, position in positions.items():
            if item != element:
                if position[0] < positions[element][0] and (abs(position[1] - positions[element][1]) < 25):
                    res[item] = position
        return res


    def getResultElements(self, positions):    # Return result elements
        res = {}
        for item, position in positions.items():
            if item != self.equals:
                if position[0] > positions[self.equals][0] and (abs(position[1] - positions[self.equals][1]) < 25):
                    res[item] = position
        return res


    def getStringElement(self, element):
        equivalence = {self.one:'1', self.two:'2', self.three:'3', self.four:'4', self.five:'5', 
                        self.six:'6', self.seven:'7', self.eight:'8', self.nine:'9', self.zero:'0',
                        self.equals:'=', self.plus:'+', self.minus:'-', self.multiplication:'*', 
                        self.division:'/'}
        return equivalence[element]


    def identifyElements(self, positions):
        symbol = [key for key in positions.keys() if key in [self.plus, self.minus, self.multiplication, self.division]][0]
        rightSide = self.getRightSideElements(positions, symbol)
        leftSide = self.getLeftSideElements(positions, symbol)
        result = self.getResultElements(positions)
        operation_left = list(leftSide.keys()) + [symbol] + list(rightSide.keys())
        operation_right = list(result.keys())
        res_left = [self.getStringElement(element) for element in operation_left]
        res_right = [self.getStringElement(element) for element in operation_right]
        return res_left,res_right


    def getOperation(self, elements_left, elements_right):
        right = ""
        left = ""

        for element in elements_right:
            right += element

        for element in elements_left:
            left += element

        right_value = eval(right)
        left_value = eval(left)

        if right_value == left_value:
            return True
        else:
            return False




class MathBattle():

    def __init__(self):
        self.right_pos = None    # Buttons coordinates
        self.wrong_pos = None
        self.play_retry_pos = None


    def start(self):
        try:
            play_retry_button = pyautogui.locateOnScreen('./images/symbols/play.png', confidence=0.9)
            self.play_retry_pos = pyautogui.center(play_retry_button)
            pyautogui.moveTo(self.play_retry_pos.x, self.play_retry_pos.y, 0.5)
            print("Play button localized: ", str(self.play_retry_pos.x), ", ", str(self.play_retry_pos.y))
        except:
            play_retry_button = pyautogui.locateOnScreen('./images/symbols/retry.png', confidence=0.9)
            self.play_retry_pos = pyautogui.center(play_retry_button)
            pyautogui.moveTo(self.play_retry_pos.x, self.play_retry_pos.y, 0.5)
            print("Retry button localized: ", str(self.play_retry_pos.x), ", ", str(self.play_retry_pos.y))
        pyautogui.click()
        time.sleep(0.1)

        right_button = pyautogui.locateOnScreen('./images/symbols/right.png', confidence=0.9)
        self.right_pos = pyautogui.center(right_button)
        print("Right button localized: ", str(self.right_pos.x), ", ", str(self.right_pos.y))
        time.sleep(0.1)

        wrong_button = pyautogui.locateOnScreen('./images/symbols/wrong.png', confidence=0.9)
        self.wrong_pos = pyautogui.center(wrong_button)
        print("Wrong button localized: ", str(self.wrong_pos.x), ", ", str(self.wrong_pos.y))

        self.run()


    def run(self):
        operationResolver = OperationResolver()

        while True:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            positions = operationResolver.getPositions(screenshot)
            positions = operationResolver.sortPositions(positions)

            if operationResolver.retry in positions.keys():
                print("Lose")
                break

            symbol = [key for key in positions.keys() if key in [operationResolver.plus, operationResolver.minus, operationResolver.multiplication, operationResolver.division]][0]

            right = operationResolver.getRightSideElements(positions, symbol)
            left = operationResolver.getLeftSideElements(positions, symbol)
            result = operationResolver.getResultElements(positions)
            right, left = operationResolver.identifyElements(positions)

            try:
                res = operationResolver.getOperation(left, right)
            except:
                print("Random!")
                res = random.choice([True, False])    # If there are the same digit in the screen, it will crash

            if res:
                pyautogui.moveTo(self.right_pos.x, self.right_pos.y, 0.1)
                pyautogui.click()
            else:
                pyautogui.moveTo(self.wrong_pos.x, self.wrong_pos.y, 0.1)
                pyautogui.click()



if __name__ == "__main__":
    
    mathBattle = MathBattle()
    mathBattle.start()