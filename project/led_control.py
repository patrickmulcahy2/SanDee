
try:
    from rpi_ws281x import PixelStrip, Color
except (ImportError, RuntimeError):
    from mock.rpi_ws281x import PixelStrip, Color
from .config import IO_pins, socketio, LED_color



strip = PixelStrip(
    num=16,
    pin=IO_pins["LED_pin"],
    freq_hz=800000,
    dma=10,
    invert=False,
    brightness=(0.2)*255,
)

strip.begin()

#METHODS
strip.setPixelColor(0, Color(255, 0, 0))
strip.show()
socketio.sleep(1)

strip.setBrightness(0.2*255)
strip.show()

otherControl = False

def set_all_pixels(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def control_LED(dT):
    while not otherControl:
        color = Color(LED_color.r, LED_color.g, LED_color.b)
        set_all_pixels(color)
        socketio.sleep(dT)

def completion_flash():
    global otherControl

    otherControl = True

    pulses = 3
    delay = 0.02

    for _ in range(pulses):
        # Fade in
        for b in range(0, 256, 5):
            color = Color(0, b, 0)

            set_all_pixels(color)

            socketio.sleep(delay)

        # Fade out
        for b in range(255, -1, -5):
            color = Color(0, b, 0)

            set_all_pixels(color)

            socketio.sleep(delay)

    otherControl = False