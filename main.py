import math
import random

from PIL import Image

"""
Highly inspired by this tutorial : https://rtouti.github.io/graphics/perlin-noise-algorithm
"""


#  Returns a blank canvas following the inputted width and height
def create_canvas(width: int, height: int) -> Image:
    return Image.new("RGB", (width, height), "#FFFFFF")


#  Returns a flattened (near 0 and 1) version of an inputted value
def fade(t: float | int) -> int | float:
    #  Only handle values between 0 and 1
    #  Entering a value < 0.5 will return a value closer to 0
    #  Entering a value > 0.5 will return a value closer to 1
    #  Entering 0.5 will return 0.5
    return ((6 * t - 15) * t + 10) * t * t * t


#  Returns a permutation table of 2 times the inputted size
def perm_table(size: int) -> list[int]:
    array = [i for i in range(size)]
    random.shuffle(array)

    for i in range(size):
        array.append(array[i])

    return array


#  Returns a constant vector from an inputted integer
def get_constant_vect(value: int) -> tuple[int, int]:
    vect = tuple()
    match value % 4:
        case 0:
            vect = (1.0, 1.0)
        case 1:
            vect = (-1.0, 1.0)
        case 2:
            vect = (-1.0, -1.0)
        case 3:
            vect = (1.0, -1.0)
    return vect


# Returns the dot product of 2 vectors of coordinates (x; y)
def dot_product_2d(vect1: tuple, vect2: tuple) -> float:
    return vect1[0] * vect2[0] + vect1[1] * vect2[1]


#  Returns a value that lies the 2 inputted ones
def linear_interpolation(t: float, value1: int | float, value2: int | float) -> float:
    return value1 + t * (value2 - value1)


#  Returns a float value between -1 and 1 for an inputted point of coordinates (x; y)
#  pt : the permutation table
#  border_size : the size of a side of your canvas, assuming it's a square
def noise_2d(x: int | float, y: int | float, pt: list[int], border_size: int) -> float:
    gX = math.floor(x) % border_size
    gY = math.floor(y) % border_size
    xf = x - math.floor(x)
    yf = y - math.floor(y)

    # 4 corner vector relative to the point (x, y)
    top_left_vect = (xf, yf - 1.0)
    top_right_vect = (xf - 1.0, yf - 1.0)
    bottom_left_vect = (xf, yf)
    bottom_right_vect = (xf - 1.0, yf)

    # pick a value in the permutation table for the 4 corners
    top_left = pt[pt[gX] + gY + 1]
    top_right = pt[pt[gX + 1] + gY + 1]
    bottom_left = pt[pt[gX] + gY]
    bottom_right = pt[pt[gX + 1] + gY]

    # dot product of the corner point value in the permutation table as a constant vector and corner vector
    dot_top_left = dot_product_2d(get_constant_vect(top_left), top_left_vect)
    dot_top_right = dot_product_2d(get_constant_vect(top_right), top_right_vect)
    dot_bottom_left = dot_product_2d(get_constant_vect(bottom_left), bottom_left_vect)
    dot_bottom_right = dot_product_2d(get_constant_vect(bottom_right), bottom_right_vect)

    u = fade(xf)
    v = fade(yf)

    n = linear_interpolation(u,
                             linear_interpolation(v, dot_bottom_left, dot_top_left),
                             linear_interpolation(v, dot_bottom_right, dot_top_right)
                             )

    return n


#  Changes the color of every pixel of the canvas for a gray shade
#  octave : higher value increases level of details
def apply_noise(canvas: Image, octave: int) -> Image:
    image = canvas.load()
    #  Assuming the canvas is a square
    border_size: int = canvas.height
    #  Permutation table
    pt = perm_table(size=border_size)

    for y in range(canvas.height):
        for x in range(canvas.width):
            coord = (int(x), int(y))

            n: float = 0.0

            frequency: float = 0.025
            motion: float = 1.0

            for _ in range(octave):
                n += motion * noise_2d(x * frequency, y * frequency, pt=pt, border_size=border_size)
                motion *= 0.5
                frequency *= 2

            n += 1
            n *= 0.5
            n = round(n * 255)

            if n < 0.5:
                color = (0, 0, 2 * n)
            elif n < 0.9:
                color = (0, n, round(n * 0.5))
            else:
                color = (n, n, n)

            image[coord] = color

    return canvas


#  Create an image of a given size and applies noise on it following octave
def create_noise(width: int, height: int, octave: int) -> Image:
    return apply_noise(create_canvas(width, height), octave=octave)


#  Save the given image as a png following file path and name
def save_image(image: Image, path: str, name: str) -> Image:
    image.save(f"{path}/{name}.png")


#  Displays the given image
def show_map(canvas: Image) -> None:
    canvas.show()


#  Practical function that creates, apply noise and displays an image
#  User can choose to save/ preview it or not with a given path/ name (or default one)
def render_canvas(width: int, height: int, octave: int,
                  preview: bool = True, save: bool = False,
                  path: str = "C:", name: str = "noise") -> None:
    image = create_noise(width, height, octave=octave)

    #  User wants to preview the generated image
    if preview:
        show_map(image)

    #  User wants to save the generated image
    if save:
        save_name: str = name

        #  Preventing duplicate name is no specific name is given
        if save_name == "noise":
            save_name: str = f"noise_{(random.randint(10000, 99999))}"

        save_image(image, path, save_name)


#  Example of a canvas of 256x256 with 10 octaves of Perlin noise
render_canvas(256, 256, 10, preview=False, save=True, path="C:/Users/GabHas/Desktop/")
