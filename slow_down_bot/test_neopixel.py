import board
import neopixel
import time

# Pin where NeoPixel is connected
pixel_pin = board.D10
num_pixels = 1  # Number of pixels

# Initialize NeoPixel with GRBW color order and auto-write disabled
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=neopixel.RGB)

try:
    while True:
        # Display red color
        pixels.fill((255, 255, 255))
        pixels.show()
        print("Red")
        time.sleep(1)
        
        # Turn off the pixel
        pixels.fill((0, 0, 0))
        pixels.show()
        print("Off")
        time.sleep(1)
except KeyboardInterrupt:
    # Ensure pixels are turned off on exit
    pixels.fill((0, 0, 0))
    pixels.show()
