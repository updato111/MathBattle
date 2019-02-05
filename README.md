# MathBattle Telegram Bot
Bot made for MathBattle telegram game. This script recognises the operation shown on screen and checks whether the given result is correct or not. **pyautogui, opencv and numpy libraries is needed!**

![alt tag](https://i.gyazo.com/dad0046853d9f6f9246fc99f0f793e79.gif)


## How it works
The script recognises each operand, the operation symbol and result parts, after that, will recognise each digit in order to form the whole number and check if the result is correct. Recognition is made by opencv2 template matching.


![alt tag](https://i.gyazo.com/4e0cae69ee6e15363f80dac328e81c75.png)


## Usage
Leave the play button uncovered and run the script. It will automatically start and stop once the retry button appears (dont cover the button). 

![alt tag](https://i.gyazo.com/77022a874b421d8cd99b8638153e4efc.png)


## TODO
* **Fix duplicated digits:** If there are any duplicated digits on the screen, the script will press a button randomly. It works correctly only when all digits are different.
