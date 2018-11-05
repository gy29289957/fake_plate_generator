from PIL import Image
from PIL import ImageFont
import os
from common import*


class GenPlate_jun:
    def __init__(self, fontCh_file, fontEng_path_file, NoPlates):
        self.plate_height = 160
        self.plate_width = 380
        self.font_height = 130
        self.font_width = 50
        self.ch_font_height = 130
        self.ch_font_width = 50

        self.dash_size = (10, 10)
        self.text_component = (2, 5)
        self.fontC = ImageFont.truetype(fontCh_file, 120, 0)
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

        self.smu = cv2.imread("./images/smu2.jpg")
        self.noplates_path = []
        for parent, parent_folder, filenames in os.walk(NoPlates):
            for filename in filenames:
                path = parent + "/" + filename
                self.noplates_path.append(path)

    def GenCh_(self, f, val, color, font_width, font_height):
        img = Image.new("RGB", (120, 160), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), val, color, font=f)
        # cv2.imshow("ch", np.array(img))
        # cv2.waitKey(0)
        img = img.resize((font_width, font_height))
        A = np.array(img)
        # cv2.imshow("ch", A)
        return A

    def draw(self, val):
        img = np.array(Image.new("RGB", (self.plate_width, self.plate_height), (255, 255, 255)))

        color = COLOR_TYPE['black']

        str_length = len(val)

        gap = 15  # diatance between top and font
        base = 10
        font_gap = 0

        seg_front = self.text_component[0]
        seg_rear = self.text_component[1]

        points = []
        # eng font
        for i in range(seg_front):
            if i == 0:
                img[gap:gap + self.ch_font_height, base:base + self.ch_font_width] = self.GenCh_(self.fontC, val[i], color, self.ch_font_width, self.ch_font_height)
            else:
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
        x = round(img.shape[1] / 3 - 15)

        y = round(img.shape[0] / 2 - 5)

        img[y:y + dash_height, x:x + dash_width] = np.full([dash_height, dash_width, 3], self.ft_color, np.uint8)

    def generate(self, text):
        self.bg_color = (255, 0, 0)
        self.ft_color = (255, 255, 255)
        # print(self.bg_type, BG_FT_TYPE[self.bg_type], self.bg_color, self.ft_color)

        fg, points = self.draw(text)
        # cv2.imshow("fg", fg)
        # cv2.waitKey(0)
        bg = self.genBackground()
        self.genDash(bg, len(text))
        # cv2.imshow("bg", bg)
        # cv2.waitKey(0)
        com = cv2.bitwise_or(fg, bg)


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
        seg_front = self.text_component[0]

        for cpos in range(val):
            if cpos == 0:
                plateStr += chars[34]
            elif cpos == 1:
                plateStr += chars[r(34)]
            else:
                plateStr += chars[r(10)]  # number

        return plateStr

    # img_size is (w, h)
    def genBatch(self, batchSize, pos, charRange, img_size, text_len=-1, transpose=False, color_code='BGR'):
        plateStrs = []
        plateImg = []
        platePoints = []
        for i in range(batchSize):
            plateStr = self.genPlateString(7)

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
