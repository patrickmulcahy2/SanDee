# mock_ws281x.py

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Color(R={self.r}, G={self.g}, B={self.b})"

def Color(r, g, b):
    return (r, g, b)

class PixelStrip:
    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None):
        self._num = num
        self._pixels = [Color(0, 0, 0)] * num

    def begin(self):
        pass

    def show(self):
        pass

    def setPixelColor(self, n, color):
        if 0 <= n < self._num:
            self._pixels[n] = color

    def numPixels(self):
        return self._num

    def getPixels(self):
        return self._pixels

    def setBrightness(self, brightness):
        pass
