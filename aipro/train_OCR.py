import sys
import argparse
from general_operations import *


# Function to analyze  each cell
def cell_analyse(img_to_analyze):
    tx = img_to_analyze.shape[1]
    ty = img_to_analyze.shape[0]
    x_unit = int(tx / 9)
    y_unit = int(ty / 9)
    y_ind = 0
    cube_array_fun = []
    while y_ind + 9 < ty:
        x_ind = 0;
        while x_ind + 9 < tx:
            # Remove 5 pixels from each direction to isolate the digit
            ry = y_ind + 5
            ryy = y_unit + y_ind - 5
            rx = x_ind + 5
            rxx = x_unit + x_ind - 5

            # Store each cell
            roi = img_to_analyze[ry:ryy, rx:rxx]
            cube_array_fun.append(roi)
            x_ind += x_unit
        y_ind += y_unit
    return cube_array_fun


# Check if cell contains a digit
def train_digits_ocr(cube_array):
    samples = np.empty((0, 225))
    responses = []
    keys = [i for i in range(48, 58)]

    for x in xrange(0, len(cube_array)):

        cube_array[x] = cv2.medianBlur(cube_array[x], 5)
        cube_array[x] = cv2.adaptiveThreshold(cube_array[x], 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13,
                                              5)

        kernel = np.ones((3, 3), np.uint8)
        cube_array[x] = cv2.morphologyEx(cube_array[x], cv2.MORPH_OPEN, kernel)

        cube_array[x] = cube_array[x][2:cube_array[x].shape[0], 2:cube_array[x].shape[1]]

        total = cv2.countNonZero(cube_array[x])

        if total > 100:
            cell_im = cube_array[x].copy()
            img_cnts, cnts, _ = cv2.findContours(cell_im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnt = sorted(cnts, key=cv2.contourArea, reverse=True)
            cnt = cnt[0]

            [x, y, w, h] = cv2.boundingRect(cnt)
            roi = cell_im[y:y + h, x:x + w]
            roismall = cv2.resize(roi, (15, 15))
            cv2.imshow('Num', cell_im)
            key = cv2.waitKey(0)

            if key == 27:  # (escape to quit)
                sys.exit()
            elif key in keys:
                responses.append(int(chr(key)))
                sample = roismall.reshape((1, 225))
                samples = np.append(samples, sample, 0)

    responses = np.array(responses, np.float32)
    responses = responses.reshape((responses.size, 1))

    f = open('samples.data', 'ab')
    np.savetxt(f, samples)
    f.close()

    f = open('responses.data', 'ab')
    np.savetxt(f, responses)
    f.close()

    print "training complete"

# Get the input image
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--img", required=True, help="path to the input image")
args = vars(ap.parse_args())

img = cv2.imread(args["img"])

if (img is None):
    print "Image not found"
    sys.exit()

# Resize the image
img = img_resize(img, 900.0)
orig_image = img.copy()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 75, 200)

kernel = np.ones((3,3),np.uint8)
edged = cv2.dilate(edged, kernel, iterations=1)

img_cnts, cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if not len(cnts) > 0:
    print "Contours not found"
    sys.exit()

# Sort contours according to their area
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
Sudoku_cnts = None

Sudoku_cnts = largest_square_contour(cnts)

# Do a Warp perspective on the sudoku image
gray_image = get_four_point_transform(gray, Sudoku_cnts.reshape(4, 2))

# Resize the image
gray_image = img_resize(gray_image, 450.0)

cube_array = cell_analyse(gray_image)

train_digits_ocr(cube_array)
