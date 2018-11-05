import os
import re
from GenPlate_NewVer import *
from GenPlate_OldVer import *
from GenPlate_jun import *
from GenPlate_foreign import *
import matplotlib.pyplot as plt
import argparse
import json


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def write_pts(code, points):
    ret = []
    for index, pt in enumerate(points):
        pt_data = {}
        pt_data["line_color"] = None
        pt_data["fill_color"] = None
        pt_data["label"] = code[index]
        pt_data["points"] = [[int(pt[0][0]), int(pt[0][1])],
                             [int(pt[1][0]), int(pt[1][1])],
                             [int(pt[2][0]), int(pt[2][1])],
                             [int(pt[3][0]), int(pt[3][1])]]
        ret.append(pt_data)
    return ret


def write_json(filepath, code, points):
    filepath = filepath.replace('\\', '/')
    filename = re.search('ChePai/(.*)\.', filepath).group(1)
    data = {}
    data["imagePath"] = os.path.basename(filename) + ".jpg"
    data["imageData"] = None
    data["flags"] = {}
    data["fillColor"] = [255, 0, 0, 128]
    data["lineColor"] = [0, 255, 0, 128]
    data["shapes"] = write_pts(code, points)
    print(filepath)
    with open(filepath.replace('.jpg', '') + '.json', 'w') as f:
        json.dump(data, f, indent=4)
    f.close()


def main():
    parser = argparse.ArgumentParser(description='Use this script to generate plate. EX: python3 genplate.py --amount=20 --output=/data/datasets/fake_plate_font --version=old')
    # parser.add_argument('--model', required=True,
    #                     help='Path to a binary file of model contains trained weights. ')
    parser.add_argument('--amount', type=int, default=40,
                        help='Amount of test data generated. ')
    # parser.add_argument('--input', help='Path to input image or video file. ')
    parser.add_argument('--output', help='Path to output image. ')
    parser.add_argument('--json', type=str2bool, default=False, help='Create the image info. for LabelMe. ')
    parser.add_argument('--show', type=str2bool, default=False, help='Show the images. ')
    parser.add_argument('--version', default='new', help='Plate version. (old, new, jun, foreign)')

    args = parser.parse_args()
    if args.output is not None:
        if (not os.path.exists(args.output)):
            os.mkdir(args.output)

    if args.version == 'new':
        G = GenPlate_NewVer("./font/ARIALUNI.TTF", './font/ChePai.ttf', "./NoPlates")
        strs, imgs, points = G.genBatch(args.amount, 2, range(31, 65), (260, 84))
    elif args.version == 'old':
        G = GenPlate_OldVer("./font/ARIALUNI.TTF", './font/ChePai_Old.ttf', "./NoPlates")
        strs, imgs, points = G.genBatch(args.amount, 2, range(31, 65), (200, 84))
    elif args.version == 'jun':
        G = GenPlate_jun("./font/ARIALUNI.TTF", './font/ChePai_Old.ttf', "./NoPlates")
        strs, imgs, points = G.genBatch(args.amount, 2, range(31, 65), (260, 84))
    else:
        G = GenPlate_foreign("./font/kaiu.ttf", './font/ChePai_Old.ttf', "./NoPlates")
        strs, imgs, points = G.genBatch(args.amount, 2, range(31, 65), (200, 84))

    imgs_size = len(imgs)

    if args.show is True:
        fig = plt.figure(figsize=(12, 12))
        fig_row = int(ceil(imgs_size / 6))
        fig_col = 6

    # create folder
    if args.output is not None:
        filepath = os.path.join(args.output, 'ChePai')
        if (not os.path.exists(filepath)):
            os.mkdir(filepath)

    for idx, img in enumerate(imgs[0:imgs_size]):
        if args.show is True:
            ax = fig.add_subplot(fig_row, fig_col, idx + 1)
        if args.output is not None:
            # add plate code        
            filename = os.path.join(filepath, strs[idx])
            filename += '.jpg'
            # cv2.imwrite(filename, img)
            cv2.imencode('.jpg', img)[1].tofile(filename)
            if args.json is True:
                write_json(filename, strs[idx], points[idx])
        if args.show is True:
            ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ax.set_axis_off()
    if args.show is True:
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    main()
