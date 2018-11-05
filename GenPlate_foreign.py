from PIL import Image
from PIL import ImageFont
import os
from common import*

PLATE_BG_COLOR = [(100, 100, 255), (214, 143, 63), (0, 242, 255)]
class GenPlate_foreign:
    def __init__(self, fontCh_file, fontEng_path_file, NoPlates):
        self.plate_height = 160
        self.plate_width = 380
        self.font_height = 130
        self.font_width = 50
        self.ch_font_height = 120
        self.ch_font_width = 100

        self.dash_size = (10, 10)
        self.text_component = (1, 4)
        self.fontC = ImageFont.truetype(fontCh_file, 120, 0)
        self.fontE = ImageFont.truetype(fontEng_path_file, 120, 0)

        # below value will be updated in generate()
        self.bg_type = -1
        self.bg_color = (-1, -1, -1)
        self.ft_color = (-1, -1, -1)

        # load all background image
        bg_path = "./images/foreign.bmp"
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
        img = Image.new("RGB", (130, 130), (255, 255, 255))
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
        base = 15
        font_gap = 0

        seg_front = self.text_component[0]
        seg_rear = self.text_component[1]

        points = []
        # eng font
        for i in range(seg_front):
            img[gap + 7:gap + 7 + self.ch_font_height, base:base + self.ch_font_width] = self.GenCh_(self.fontC, val[i], color, self.ch_font_width, self.ch_font_height)
            
            points.append([(base, gap),
                           (base + self.font_width, gap),
                           (base + self.font_width, gap + self.font_height),
                           (base, gap + self.font_height)])
            base += self.font_width + font_gap

            # cv2.imshow("1", img)
            # cv2.waitKey(0)

        # num font
        base += 90  # shift bacause the '-'
        for i in range(seg_rear):
            img[gap:gap + self.font_height, base:base + self.font_width] = GenEng(self.fontE, val[i + seg_front], color, self.font_width, self.font_height)
            points.append([(base, gap),
                           (base + self.font_width, gap),
                           (base + self.font_width, gap + self.font_height),
                           (base, gap + self.font_height)])
            base += self.font_width + font_gap

            # cv2.imshow("1", img)
            # cv2.waitKey(0)

        # img = (255 - img)  # inverse

        # ttt = np.copy(img)
        # for j in range(len(points)):
        #     ttt = draw_points(ttt, points[j])
        # cv2.imshow('img', img)
        # cv2.waitKey(0)
        return img, points

    def genBackground(self):
        bg = np.copy(self.bgs)
        bg[np.where((bg == [100, 100, 255]).all(axis=2))] = self.bg_color
        return bg

    def generate(self, text):
        self.bg_color = PLATE_BG_COLOR[r(3)]
        self.ft_color = (255, 255, 255)
        # print(self.bg_type, BG_FT_TYPE[self.bg_type], self.bg_color, self.ft_color)

        fg, points = self.draw(text)
        # cv2.imshow("fg", fg)
        # cv2.waitKey(0)
        bg = self.genBackground()
        # cv2.imshow("bg", bg)
        # cv2.waitKey(0)
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
        seg_front = self.text_component[0]

        for cpos in range(val):
            if cpos == 0:
                plateStr += chars[35 + r(2)]
            else:
                plateStr += chars[r(10)]  # number

        return plateStr

    # img_size is (w, h)
    def genBatch(self, batchSize, pos, charRange, img_size, text_len=-1, transpose=False, color_code='BGR'):
        plateStrs = []
        plateImg = []
        platePoints = []
        for i in range(batchSize):
            plateStr = self.genPlateString(5)

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
