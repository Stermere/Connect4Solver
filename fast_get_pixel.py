from ctypes import windll

class PixelReader():
    DC = windll.user32.GetDC(0)

    # returns the color of the pixel at x,y as a 32-bit integer
    @staticmethod
    def get_pixel(x, y):
        return windll.gdi32.GetPixel(PixelReader.DC, x, y)

    # returns the color of the pixel at x,y as a 3-tuple of RGB values
    @staticmethod
    def get_pixel_rgb(x, y):
        pixel = PixelReader.get_pixel(x, y)
        return (pixel & 0xff, (pixel >> 8) & 0xff, (pixel >> 16) & 0xff)

if __name__ == "__main__":
    # Example usage:
    import time
    start_time = time.time()
    print(PixelReader.get_pixel_rgb(1000,1000))
    print(PixelReader.get_pixel(1000,1000))
    print("--- %s seconds ---" % (time.time() - start_time))