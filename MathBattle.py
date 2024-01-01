import cv2
import pyautogui
import time
import random
import math
import numpy as np


class OperationResolver():

    __author__ : "EnriqueMoran"

    __version__ : "0.1.5"

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


    def getPosition(self, itemPath, image):    # Return position and confidence of a number from template matching
        res = []
        confidence = 0.99    # Initial confidence
        game = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        item = cv2.imread(itemPath, 0)
        w, h = item.shape[::-1]

        match = cv2.matchTemplate(game, item, self.matchTemplateMethod)
        while len(res) < 2:
            if confidence < 0.95:
                return [(itemPath, (0.0, 0.0), -1)]    # The number is not in the image
            loc = np.where(match >= confidence)
            for pt in zip(*loc[::-1]):
                res.append((pt[0] + (pt[0] + w) / 2, pt[1] + (pt[1] + h) / 2))
            confidence -= 0.01
        print("BEFORE: ", [(itemPath, pos, confidence) for pos in res])
        res = self.removeDuplicatedPositions(res)
        print("AFTER: ", [(itemPath, pos, confidence) for pos in res])
        return [(itemPath, pos, confidence) for pos in res]    # 3-tuple (itemPath, position, confidence)


    def removeDuplicatedPositions(self, positions):    # Remove false positive by proximity
        res = [positions[0]]
        for x_1, y_1 in positions:
            if (x_1, y_1) != res[-1]:
                #if math.sqrt((x_1 - res[-1][0]) ** 2 + (y_1 - res[-1][1]) ** 2) > 5:
                if abs(x_1 - res[-1][0]) > 2 and abs(y_1 - res[-1][1]) > 2:
                    res.append((x_1, y_1))            
        return res


    def getAllPositions(self, image):
        res = []
        itemPaths = [self.one, self.two, self.three, self.four, self.five, self.six,
                    self.seven, self.eight, self.nine, self.zero, self.equals, self.plus, 
                    self.minus, self.multiplication, self.division, self.retry]
        for itemPath in itemPaths:
            res += self.getPosition(itemPath, image)
        return res


    def getPositions(self, image):    # Return number and symbol position with confidence >= 0.9
        res = []
        positions = self.getAllPositions(image)
        for itemPath, position, confidence in positions:
            if confidence >= 0.9:
                res.append((itemPath, position))
        return res


    def getRightSideElements(self, positions, element):    # Return elements that are at element's right side
        res = []
        for item, position in positions:
            if item != element[0]:
                if position[0] > element[1][0] and (abs(position[1] - element[1][1]) < 25):
                    res.append((item, position))
        return res


    def getLeftSideElements(self, positions, element):    # Return elements that are at element's left side
        res = []
        for item, position in positions:
            if item != element[0]:
                if position[0] < element[1][0] and (abs(position[1] - element[1][1]) < 25):
                    res.append((item, position))
        return res


    def getResultElements(self, positions, image):    # Return result elements
        res = []
        _, equalsPos, _ = self.getPosition(self.equals, image)[0]
        for item, position in positions:
            if item != self.equals:
                if position[0] > equalsPos[0] and (abs(position[1] - equalsPos[1]) < 25):
                    res.append((item, position))
        return res


    def getStringElement(self, element):
        equivalence = {self.one:'1', self.two:'2', self.three:'3', self.four:'4', self.five:'5', 
                        self.six:'6', self.seven:'7', self.eight:'8', self.nine:'9', self.zero:'0',
                        self.equals:'=', self.plus:'+', self.minus:'-', self.multiplication:'*', 
                        self.division:'/'}
        return equivalence[element]


    def identifyElements(self, positions, image):
        symbol = [key for key in positions if key[0] in [self.plus, self.minus, self.multiplication, self.division]][0]
        
        rightSide = self.getRightSideElements(positions, symbol)
        leftSide = self.getLeftSideElements(positions, symbol)
        result = self.getResultElements(positions, image)
        
        operation_left = [key[0] for key in leftSide] + [symbol[0]] + [key[0] for key in rightSide]
        operation_right = [key[0] for key in result]
        
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
        try:    # First play
            play_retry_button = pyautogui.locateOnScreen('./images/symbols/play.png', confidence=0.9)
            self.play_retry_pos = pyautogui.center(play_retry_button)
            pyautogui.moveTo(self.play_retry_pos.x, self.play_retry_pos.y, 0.5)
            print("Play button localized: ", str(self.play_retry_pos.x), ", ", str(self.play_retry_pos.y))
        except:    # Retry
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
            positions =  sorted(positions, key=lambda tup : tup[1])    # Sort elements from left to right position

            if operationResolver.retry in [pos[0] for pos in positions]:    # If there is retry button on screen
                print("Lose")
                return None

            try:
                symbol = [key for key in positions if key[0] in [operationResolver.plus, operationResolver.minus, operationResolver.multiplication, operationResolver.division]][0]
                
                right = operationResolver.getRightSideElements(positions, symbol)
                left = operationResolver.getLeftSideElements(positions, symbol)
                result = operationResolver.getResultElements(positions, screenshot)
                right, left = operationResolver.identifyElements(positions, screenshot)
                print(right, left, "\n\n\n")

                
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
