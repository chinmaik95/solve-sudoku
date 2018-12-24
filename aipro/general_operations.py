import cv2
import numpy as np

# Find the largest square contour which will be the sudoku
def largest_square_contour(cnts_fn):
    for c in cnts_fn:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        if len(approx) == 4:
            Sudoku_cnts_fun = approx
            break
    return Sudoku_cnts_fun


# Function to order a list of coordinates that will be ordered
# such that the first entry in the list is the top-left,
# the second entry is the top-right,
# the third is the bottom-right, and
# the fourth is the bottom-left
def get_ordered_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


# Function to get birds eye view of the image
def get_four_point_transform(image, pts):
    rect = get_ordered_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped_image = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped_image


# Function to resize image
def img_resize(img_to_resize, h):
    ratio = h / img_to_resize.shape[0]
    dim = (int(img_to_resize.shape[1] * ratio), int(h))

    resized = cv2.resize(img_to_resize, dim, interpolation=cv2.INTER_AREA)
    return resized