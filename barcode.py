#!/usr/bin/python3

import cv2
from PIL import Image
import os
from natsort import natsorted
import optparse

parser = optparse.OptionParser()
parser.add_option('-s', '--src', action='store', dest="source", help='The input-file')
parser.add_option('-o', '--output', action='store', dest="output", help='The output file-name (default: final.jpg)', default='final.jpg')
parser.add_option('--avg', action="store_true", dest="modeavg", help="Instead of using the compressing images, the average color of them will be used (default: false)", default=False)
parser.add_option('-w', '--bar-width', action="store", dest="barwidth", help='The width of each bar in the final image (default: 5px)', default=5)
parser.add_option('--height', action="store", dest="barheight", help="The height of the final image (Default: same as src-video)", default="auto")
parser.add_option('-i', '--interval', action="store", dest="interval", help="The interval where each frame gets picked out of the video (default: 1000 (ms))", default=1000)
parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="Enables verbose-output")


options, args = parser.parse_args()

global verbosebol
verbosebol = options.verbose

if options.source:
    pass
else:
    print('You need to define a src-video with the -s flag!')
    exit()

src = options.source
imgsrc = 'frames'
barsrc = 'bars'

frame = 1
second = int(options.interval)
barwidth = int(options.barwidth)
finalheight = 0
avgcolors = dict()

def checkfile(file, options):
    if os.path.isfile(file):
        pass
    else:
        print('This file does not exist!')
        exit()
    if options.source[-4:] == '.mp4':
        pass
    else:
        print('Error: Only mp4 videos are supported!')
        exit()

def verboseout(verb):
    if verbosebol:
        print(verb)
    else:
        pass

def startup(imgsrc,barsrc):
    if not os.path.exists(imgsrc):
        os.makedirs(imgsrc)
    if not os.path.exists(barsrc):
        os.makedirs(barsrc)

def cleanup(imgsrc, barsrc):
    img = os.listdir(imgsrc)
    for item in img:
        os.remove(os.path.join(imgsrc, item))
    bar = os.listdir(barsrc)
    for item in bar:
        os.remove(os.path.join(barsrc, item))

def getframes(src, frame, second):
    vidcap = cv2.VideoCapture(src)
    success,image = vidcap.read()
    count = 0
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*second))
        success, image = vidcap.read()
        verboseout("Reading Frame at timestamp (" + str(count) + ")", )
        if success:
            cv2.imwrite(os.path.join(imgsrc, '%d.jpg' % count), image)
            count += frame
        else:
            break

def concat(barwidth, barsrc):
    posx = 0
    bars = os.listdir(barsrc)
    if options.barheight == 'auto':
        im = Image.open(os.path.join(barsrc, bars[0]))
        width, height = im.size
        im.close()
    else:
        height = int(options.barheight)
    width = len(bars) * barwidth
    finalimg = Image.new('RGB', (width, height))
    for item in bars:
        im = Image.open(os.path.join(barsrc, item))
        finalimg.paste(im, (posx, 0))
        posx += barwidth
    finalimg.save(options.output)
    finalimg.show()

def concatavg(avgcolors):
    pass

def reziseframes(imgsrc, barwidth, barsrc):
    frames = os.listdir(imgsrc)
    frames = natsorted(frames)
    for item in frames:
        with Image.open(os.path.join(imgsrc, item)) as img:
            verboseout('Cropping frame: ' + item)
            width, height = img.size
            out = img.resize((barwidth, height), resample=0, box=None)
            out.save(os.path.join(barsrc, item))

def avgcolor(imgsrc, avgcolors):
    frames = os.listdir(imgsrc)
    frames = natsorted(frames)
    for item in frames:
        rt, gt, bt = 0, 0, 0
        c = 0
        with Image.open(os.path.join(imgsrc, item)) as img:
            width, height = img.size
            rgb_img = img.convert('RGB')
            for i in range(0, width-1):
                for j in range(0, height-1):
                    r, g, b = rgb_img.getpixel((i, j))
                    rt += r
                    gt += g
                    bt += b
                    c += 1
        avgcolors[item] = 'rbg({}, {}, {})'.format(round(rt / c), round(gt / c), round(bt / c))

checkfile(src, options)
startup(imgsrc, barsrc)
print('Getting Individual frames...')
getframes(src, frame, second)
print('Resizing frames...')
reziseframes(imgsrc, barwidth, barsrc)
if options.modeavg:
    avgcolor(barsrc, avgcolors)
else:
    pass
print('Putting frames together...')
if options.modeavg:
    concatavg(barwidth)
else:
    concat(barwidth, barsrc)
print('Cleaning up...')
cleanup(imgsrc, barsrc)
print('Finished!')
print('Saved as \'' + options.output + '\'')
print('Press enter to exit!')
input()
exit()
