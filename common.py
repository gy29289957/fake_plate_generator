import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw
from math import *


COLOR_TYPE = {'white': (255, 255, 255), 'black': (10, 10, 10),
              'red': (0, 0, 255), 'green': (0, 201, 0),
              'yellow': (20, 170, 240)}

BG_FT_TYPE = [('white', 'black'), ('white', 'red'), ('white', 'green'),
              ('red', 'white'), ('green', 'white'), ('yellow', 'black')]

index = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
         "8": 8, "9": 9, "A": 10, "B": 11, "C": 12, "D": 13, "E": 14,
         "F": 15, "G": 16, "H": 17, "J": 18, "K": 19, "L": 20, "M": 21,
         "N": 22, "P": 23, "Q": 24, "R": 25, "S": 26, "T": 27, "U": 28,
         "V": 29, "W": 30, "X": 31, "Y": 32, "Z": 33, "軍": 34, "外": 35,
         "使": 36}

chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A",
         "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M",
         "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y",
         "Z", "軍", "外", "使"]

electric_string = ["電", "動", "車"]

area_string = {0: ["台", "灣", "省"],
               1: ["台", "北", "市"],
               2: ["高", "雄", "市"],
               3: ["金", "門", "縣"],
               4: ["連", "江", "縣"]}

mix_string = {0: ["台", "灣", "省"],
              1: ["台", "北", "市"],
              2: ["高", "雄", "市"],
              3: ["金", "門", "縣"],
              4: ["連", "江", "縣"],
              5: ["電", "動", "車"]}


def CoordinateTrans(points, M):
    ret = []
    for text in points:
        ps = []
        for p in text:
            x = p[0]
            y = p[1]
            d = M[2, 0] * x + M[2, 1] * y + M[2, 2]
            p = (int((M[0, 0] * x + M[0, 1] * y + M[0, 2]) / d),
                 int((M[1, 0] * x + M[1, 1] * y + M[1, 2]) / d))
            ps.append(p)
        ret.append(ps)
    return ret


def AddSmudginess(img, Smu):
    rows = r(Smu.shape[0] - img.shape[0])
    cols = r(Smu.shape[1] - img.shape[1])
    adder = Smu[rows:rows + img.shape[0], cols:cols + img.shape[1]]
    #   adder = cv2.bitwise_not(adder)
    img = cv2.bitwise_not(img)
    img = cv2.bitwise_and(adder, img)
    img = cv2.bitwise_not(img)
    return img


def rot(img, angel, shape, max_angel, points):
    size_o = [shape[1], shape[0]]

    size = (shape[1] + int(shape[0] * cos((float(max_angel) / 180) * 3.14)), shape[0])

    interval = abs(int(sin((float(angel) / 180) * 3.14) * shape[0]))

    pts1 = np.float32([[0, 0],
                       [0, size_o[1]],
                       [size_o[0], 0],
                       [size_o[0], size_o[1]]])
    if(angel > 0):
        pts2 = np.float32([[interval, 0],
                           [0, size[1]],
                           [size[0], 0],
                           [size[0] - interval, size_o[1]]])
    else:
        pts2 = np.float32([[0, 0],
                           [interval, size[1]],
                           [size[0] - interval, 0],
                           [size[0], size_o[1]]])

    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, size)
    
    points = CoordinateTrans(points, M)
    return dst, points


def rotRandrom(img, factor, size, points):
    shape = size
    pts1 = np.float32([[0, 0],
                       [0, shape[0]],
                       [shape[1], 0],
                       [shape[1], shape[0]]])
    pts2 = np.float32([[r(factor), r(factor)],
                       [r(factor), shape[0] - r(factor)],
                       [shape[1] - r(factor), r(factor)],
                       [shape[1] - r(factor), shape[0] - r(factor)]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    M[0:2, 0:2] = M[0:2, 0:2] * ((r(2) + 9.5) / 10)  # scaling
    dst = cv2.warpPerspective(img, M, size)
    points = CoordinateTrans(points, M)
    return dst, points


# shadow
def tfactor(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    y = r(img.shape[0])

    hsv[0:y, :, 0] = hsv[0:y, :, 0] * (0.8 + np.random.random() * 0.2)
    hsv[0:y, :, 1] = hsv[0:y, :, 1] * (0.3 + np.random.random() * 0.7)
    hsv[0:y, :, 2] = hsv[0:y, :, 2] * (0.2 + np.random.random() * 0.8)

    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


def random_envirment(img, data_set):
    index = r(len(data_set))
    env = cv2.imread(data_set[index])

    env = cv2.resize(env, (img.shape[1], img.shape[0]))

    bak = (img == 0)
    bak = bak.astype(np.uint8) * 255

    inv = cv2.bitwise_and(bak, env)
    img = cv2.bitwise_or(inv, img)

    return img


def find_rect(im):
    gray = np.array(im, dtype=np.uint8)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    binary = np.uint8(gray)
    cnts = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    if (len(cnts) > 0):
        box = cv2.boundingRect(cnts[0])
    else:
        box = (0, 0, 0, 0)
    return box


def random_position(img, points):
    x, y, w, h = find_rect(img)
    width_range = img.shape[1] - w
    height_range = img.shape[0] - h
    mov_x = r(width_range) - x
    mov_y = r(height_range) - y
    M = np.identity(3)
    M[0, 2] = mov_x
    M[1, 2] = mov_y
    dst = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
    points = CoordinateTrans(points, M)
    return dst, points


def GenCh(f, val, color, ch_font_width, ch_font_height):
    img = Image.new("RGB", (ch_font_width, ch_font_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), val, color, font=f)
    # img = img.resize((10, 50))
    A = np.array(img)
    # cv2.imshow("ch", A)
    return A


def GenEng(f, val, color, eng_font_width, eng_font_height):
    img = Image.new("RGB", (eng_font_width, eng_font_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((0, 2), val, color, font=f)
    A = np.array(img)
    # cv2.imshow("ch1", A)
    return A


def AddGauss(img, level):
    return cv2.blur(img, (level * 2 + 1, level * 2 + 1))


def r(val):
    return int(np.random.random() * val)


def AddNoiseSingleChannel(single):
    diff = 255 - single.max()
    noise = np.random.normal(0, 1 + r(6), single.shape)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    noise = diff * noise
    noise = noise.astype(np.uint8)
    dst = single + noise
    return dst


def addNoise(img, sdev=0.5, avg=10):
    img[:, :, 0] = AddNoiseSingleChannel(img[:, :, 0])
    img[:, :, 1] = AddNoiseSingleChannel(img[:, :, 1])
    img[:, :, 2] = AddNoiseSingleChannel(img[:, :, 2])
    return img
