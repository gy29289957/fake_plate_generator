from PIL import Image
from PIL import ImageFont
import os
from common import*


# for debug
def draw_points(img, points, method='circle'):
    color = (0, 255, 0)
    for i in range(len(points)):
        if method == 'circle':
            img = cv2.circle(img, points[i], 2, color, 2)
        else:
            if i == len(points) - 1:
                img = cv2.line(img, points[i], points[0], color)
            else:
                img = cv2.line(img, points[i], points[i + 1], color)
    return img


class GenPlate_OldVer:
    def __init__(self, fontCh_file, fontEng_path_file, NoPlates):
        self.plate_height = 160
        self.plate_width = 320
        self.font_height = 130
        self.font_width = 50
        self.ch_font_height = 35
        self.ch_font_width = 30

        self.dash_size = (10, 12)
        self.text_component = {6: [(3, 3), (2, 4), (4, 2)],
                               5: [(3, 2), (2, 3)],
                               4: [(2, 2)]}
        self.fontC_small = ImageFont.truetype(fontCh_file, 28, 0)
        self.fontE = ImageFont.truetype(fontEng_path_file, 120, 0)

        # below value will be updated in generate()
        self.bg_type = -1
        self.bg_color = (-1, -1, -1)
        self.ft_color = (-1, -1, -1)

        # load all background image
        bg_path = "./images/old.bmp"
        img = cv2.imread(bg_path)
        self.scale_size = (img.shape[1] / self.plate_width, img.shape[0] / self.plate_height)
        img = cv2.resize(img, (self.plate_width, self.plate_height))
        self.bgs = img

        self.wheelchair = cv2.imread("./images/wheelchair.png")
        self.exhaust = cv2.imread("./images/exhaust.png")
        self.smu = cv2.imread("./images/smu2.jpg")
        self.noplates_path = []
        for parent, parent_folder, filenames in os.walk(NoPlates):
            for filename in filenames:
                path = parent + "/" + filename
                self.noplates_path.append(path)

    def addString(self, img):
        ch_base = round(img.shape[1] / 3) 
        gap = round(ch_base / 3 - self.ch_font_width) +5
        strings = mix_string[r(6)]
        for i in range(3):
            img[0:0 + self.ch_font_height, ch_base:ch_base + self.ch_font_width] = GenCh(self.fontC_small, strings[i], self.ft_color, self.ch_font_width, self.ch_font_height)
            ch_base += self.ch_font_width + gap

    def addWheelChair(self, img):
        wheelchair = cv2.resize(self.wheelchair, (0, 0),
                                fx=1 / self.scale_size[0],
                                fy=1 / self.scale_size[1])
        x = int((img.shape[1] - wheelchair.shape[1]) / 2)
        y = 8
        img[y:y + wheelchair.shape[0], x:x + wheelchair.shape[1]] = wheelchair

    def addExhaust(self, img):
        exhaust = cv2.resize(self.exhaust, (0, 0),
                             fx=1 / self.scale_size[0],
                             fy=1 / self.scale_size[1])
        if r(2) is 0:
            x = r(20) + 5   # left
        else:
            x = img.shape[1] - (exhaust.shape[1] + r(20) + 5)   # right
        y = r(8) + 5
        img[y:y + exhaust.shape[0], x:x + exhaust.shape[1]] = exhaust

    def draw(self, val):
        img = np.array(Image.new("RGB", (self.plate_width, self.plate_height), (255, 255, 255)))

        if self.ft_color == COLOR_TYPE['white']:
            color = COLOR_TYPE['black']
        else:
            color = self.ft_color

        str_length = len(val)

        gap = 15  # diatance between top and font
        base = 0
        font_gap = 0

        if str_length == 6:
            base = 0
            font_gap = 0
        elif str_length == 5:
            base = 20
            font_gap = 5
        elif str_length == 4:
            base = 28
            font_gap = 16

        seg = self.text_component[str_length]
        seg_content_len = len(seg)
        self.seg_type = seg[r(seg_content_len)]

        seg_front = self.seg_type[0]
        seg_rear = self.seg_type[1]

        points = []
        # eng font
        for i in range(seg_front):
            img[gap:gap + self.font_height, base:base + self.font_width] = GenEng(self.fontE, val[i], color, self.font_width, self.font_height)
            points.append([(base, gap),
                           (base + self.font_width, gap),
                           (base + self.font_width, gap + self.font_height),
                           (base, gap + self.font_height)])
            base += self.font_width + font_gap

            # cv2.imshow("1", img)
            # cv2.waitKey(0)

        # num font
        base += self.dash_size[1] + 5  # shift bacause the '-'
        for i in range(seg_rear):
            img[gap:gap + self.font_height, base:base + self.font_width] = GenEng(self.fontE, val[i + seg_front], color, self.font_width, self.font_height)
            points.append([(base, gap),
                           (base + self.font_width, gap),
                           (base + self.font_width, gap + self.font_height),
                           (base, gap + self.font_height)])
            base += self.font_width + font_gap

            # cv2.imshow("1", img)
            # cv2.waitKey(0)

        random_add_mark = r(4)
        if random_add_mark is 0:
            self.addString(img)
                # cv2.imshow("1", img)
                # cv2.waitKey(0)
        elif random_add_mark is 1:
            self.addWheelChair(img)

        if r(3) is 0:
            self.addExhaust(img)

        if (self.bg_color == COLOR_TYPE['red']) or (self.bg_color == COLOR_TYPE['green']):
            img = (255 - img)  # inverse

        # ttt = np.copy(img)
        # for j in range(len(points)):
        #     ttt = draw_points(ttt, points[j])
        # cv2.imshow('img', img)
        # cv2.waitKey(0)
        return img, points

    def genBackground(self):
        bg = np.copy(self.bgs)
        bg[np.where((bg == [255, 255, 255]).all(axis=2))] = self.bg_color
        return bg

    def genDash(self, img, length):
        dash_height = self.dash_size[0]
        dash_width = self.dash_size[1]

        # start position
        x = 0
        y = 0
        if self.seg_type == (4, 2):
            x = round(img.shape[1] * 2 / 3 - 8)
        if self.seg_type == (2, 4):
            x = round(img.shape[1] / 3 - 3)
        elif self.seg_type == (2, 2) or self.seg_type == (3, 3):
            x = round((img.shape[1] - dash_width) / 2)
        elif self.seg_type == (2, 3):
            x = round(img.shape[1] * 2 / 5 + 3)
        elif self.seg_type == (3, 2):
            x = round(img.shape[1] * 3 / 5 - 4)

        y = round(img.shape[0] / 2 - 5)

        img[y:y + dash_height, x:x + dash_width] = np.full([dash_height, dash_width, 3], self.ft_color, np.uint8)

    def generate(self, text):
        self.bg_type = r(6)  # choise background type
        self.bg_color = COLOR_TYPE[BG_FT_TYPE[self.bg_type][0]]
        self.ft_color = COLOR_TYPE[BG_FT_TYPE[self.bg_type][1]]
        # print(self.bg_type, BG_FT_TYPE[self.bg_type], self.bg_color, self.ft_color)

        fg, points = self.draw(text)
        # cv2.imshow("fg", fg)
        # cv2.waitKey(0)
        bg = self.genBackground()
        self.genDash(bg, len(text))
        # cv2.imshow("bg", bg)
        # cv2.waitKey(0)
        if (self.bg_color == COLOR_TYPE['red']) or (self.bg_color == COLOR_TYPE['green']):
            com = cv2.bitwise_or(fg, bg)
        else:
            com = cv2.bitwise_and(fg, bg)

        # cv2.imshow("r", com)
        # cv2.waitKey(0)
        com, points = rot(com, r(60) - 30, com.shape, 30, points)
        com, points = rotRandrom(com, 10, (com.shape[1], com.shape[0]), points)
        com, points = random_position(com, points)

        # random add 
        if r(2) is 1:
            com = AddSmudginess(com, self.smu)

        com = tfactor(com)
        com = random_envirment(com, self.noplates_path)
        com = AddGauss(com, 1 + r(4))
        com = addNoise(com)

        # show points
        # ttt = np.copy(com)
        # for i in range(len(points)):
        #     ttt = draw_points(ttt, points[i], 'line')
        # cv2.imshow('ttt', ttt)
        # cv2.waitKey(0)

        # cv2.imshow("r", com)
        # cv2.waitKey(0)
        return com, points

    def genPlateString(self, val):
        plateStr = ""

        for cpos in range(val):
            plateStr += chars[r(34)]  # mix

        return plateStr

    # img_size is (w, h)
    def genBatch(self, batchSize, pos, charRange, img_size, text_len=-1, transpose=False, color_code='BGR'):
        plateStrs = []
        plateImg = []
        platePoints = []
        for i in range(batchSize):
            # random gen 4~5 text r(3) is 0, 1 or 2
            if text_len == -1:
                plateStr = self.genPlateString(r(3) + 4)
            else:
                plateStr = self.genPlateString(text_len)

            img, points = self.generate(plateStr)
            scale_size = (img.shape[1] / img_size[0], img.shape[0] / img_size[1])
            img = cv2.resize(img, img_size)

            # check bounding
            new_points = []
            for strs in points:
                pt_tmp = []
                for pt in strs:
                    x = int(pt[0] / scale_size[0])
                    if x > img.shape[1]:
                        x = img.shape[1]
                    elif x < 0:
                        x = 0
                    y = int(pt[1] / scale_size[1])
                    if y > img.shape[0]:
                        y = img.shape[0]
                    elif y < 0:
                        y = 0
                    pt_tmp.append((x, y))
                new_points.append(pt_tmp)

            if transpose is True:
                img = img.transpose(1, 0, 2)

            if color_code is 'GRAY':
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif color_code is 'RGB':
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # filename = os.path.join(outputPath, plateStr + ".jpg")
            plateImg.append(img)
            plateStrs.append(plateStr)
            platePoints.append(new_points)
            # print(filename)
            # cv2.imwrite(filename, img)
            # cv2.imshow(plateStr, img)
            # cv2.waitKey(0)

        return plateStrs, plateImg, platePoints
