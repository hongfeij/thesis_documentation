from gpiozero import Button
from signal import pause

def button_pressed():
    print("Button was pressed!")

button = Button(27)
button.when_pressed = button_pressed

print("Ready: Press the button...")
pause()
