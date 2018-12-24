import sys
import argparse
from general_operations import *
from pprint import pprint


# Function to analyze  each cell
def cell_analyse(img_to_analyze):
    tx = img_to_analyze.shape[1]
    ty = img_to_analyze.shape[0]

    x_unit = int(tx / 9)
    y_unit = int(ty / 9)

    y_ind = 0

    cube_array_fun = []
    cube_is_digit_fun = []

    while y_ind + 9 < ty:
        x_ind = 0;
        while x_ind + 9 < tx:

            # Remove s pixels from each direction to isolate the digit
            ry = y_ind + 5
            ryy = y_unit + y_ind - 5
            rx = x_ind + 5
            rxx = x_unit + x_ind - 5

            # Store each cell
            roi = img_to_analyze[ry:ryy, rx:rxx]
            cube_array_fun.append(roi)
            cube_is_digit_fun.append(0)

            x_ind += x_unit

        y_ind += y_unit
    return cube_array_fun, cube_is_digit_fun


# Check if cell contains a digit
# If a digit is present extract it
def get_digits_ocr(cube_array, cube_is_digit):
    samples = np.loadtxt('samples.data', np.float32)
    responses = np.loadtxt('responses.data', np.float32)
    responses = responses.reshape((responses.size, 1))

    model = cv2.ml.KNearest_create()
    model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    cells_val_fun = [[0 for i in xrange(9)] for i in xrange(9)]
    for x in xrange(0, len(cube_array)):

        cube_array[x] = cv2.medianBlur(cube_array[x], 5)
        cube_array[x] = cv2.adaptiveThreshold(cube_array[x], 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13,
                                              5)

        kernel = np.ones((3, 3), np.uint8)
        cube_array[x] = cv2.morphologyEx(cube_array[x], cv2.MORPH_OPEN, kernel)

        cube_array[x] = cube_array[x][2:cube_array[x].shape[0], 2:cube_array[x].shape[1]]

        total = cv2.countNonZero(cube_array[x])
        x_val = int(x / 9)
        y_val = x % 9

        if total > 100:

            cell_im = cube_array[x].copy()
            img_cnts, cnts, _ = cv2.findContours(cell_im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnt = sorted(cnts, key=cv2.contourArea, reverse=True)
            cnt = cnt[0]

            [xq, y, w, h] = cv2.boundingRect(cnt)

            roi = cell_im[y:y + h, xq:xq + w]
            roismall = cv2.resize(roi, (15, 15))
            roismall = roismall.reshape((1, 225))
            roismall = np.float32(roismall)
            retval, results, neigh_resp, dists = model.findNearest(roismall, k=3)
            text = str(int((results[0][0])))

            cube_is_digit[x] = 1

            cells_val_fun[x_val][y_val] = int(text)

        else:
            cells_val_fun[x_val][y_val] = 0

    return cells_val_fun


def get_solved_image(image_text, cells_val_fun, cube_is_digit_fun):
    tx = gray_image.shape[1]
    ty = gray_image.shape[0]

    x_unit = int(tx / 9)
    y_unit = int(ty / 9)

    font = cv2.FONT_HERSHEY_SIMPLEX
    y_pos = y_unit - int(y_unit / 4)
    check_filled = 0

    for i in xrange(0, len(cells_val_fun[0])):
        x_pos = int(x_unit / 4)

        for j in xrange(0, len(cells_val_fun[i])):
            k = str(cells_val_fun[i][j])
            if not cube_is_digit_fun[check_filled] is 1:
                cv2.putText(image_text, k, (x_pos, y_pos), font, 1, (150, 0, 0), 2, cv2.LINE_AA)
            x_pos += x_unit
            check_filled += 1
        y_pos += y_unit
    return image_text


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
perspective = cv2.Canny(blurred, 75, 200)

kernel = np.ones((3,3),np.uint8)
edged = cv2.dilate(perspective, kernel, iterations=1)

cv2.imshow("Perspective", perspective)
# cv2.waitKey(0)

img_cnts, cnts, _ = cv2.findContours(perspective.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if not len(cnts) > 0:
    print "Contours not found"
    sys.exit()

# Sort contours according to their area
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
Sudoku_cnts = None

Sudoku_cnts = largest_square_contour(cnts)

# Do a Warp perspective on the sudoku image
orig_image = get_four_point_transform(orig_image, Sudoku_cnts.reshape(4, 2))
gray_image = get_four_point_transform(gray, Sudoku_cnts.reshape(4, 2))

cv2.imshow("Warp", gray_image)
# cv2.waitKey(0)

# Resize the image
orig_image = img_resize(orig_image, 450.0)
gray_image = img_resize(gray_image, 450.0)

sudoku_img = gray_image.copy()

cube_array, cube_is_digit = cell_analyse(sudoku_img)

cells_val = get_digits_ocr(cube_array, cube_is_digit)
pprint("Sudoku : ")
pprint(cells_val)

cv2.imshow("Original", orig_image)
print(cells_val)
cv2.waitKey(0)