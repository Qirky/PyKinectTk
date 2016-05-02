"""
    Module that contains the colour data and how to convert
    between PyGame and Numpy Arrays
"""

from pygame import surfarray, transform
from cv2 import transpose, cvtColor, resize, COLOR_BGR2RGB

def img(surface):
    """ img(pygame.Surface) -> numpy.array """
    array = surfarray.array3d(surface)
    array = transpose(array)
    array = cvtColor(array, COLOR_BGR2RGB)
    return array

def surface(img, scale=1):
    """ surface(numpy.array) -> pygame.Surface """
    surf = resize(img, (0,0), fx=scale, fy=scale)
    surf = cvtColor(surf, COLOR_BGR2RGB)
    surf = surfarray.make_surface(surf)
    surf = transform.rotate(surf, -90)
    surf = transform.flip(surf, True, False)
    return surf
