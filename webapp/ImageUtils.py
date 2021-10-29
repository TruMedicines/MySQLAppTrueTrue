'''
Image transformation convenience functions
'''

import cv2
import numpy as np

'''
Convert image to grayscale
'''
def toGrayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def crop_to_circle(img):
    '''
    Crops an image to a circle
    Used to remove additional white space around pill image - TODO
    Args
        img: input image to crop
    Returns
        f: cropped image 
    '''
    if type(img) is 'str':
        img = cv2.imread(img)
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    __, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    circles = cv2.HoughCircles(th,cv2.HOUGH_GRADIENT,1,50,
                            param1=20,param2=10,minRadius=0,maxRadius=0)
    #circimg = cv2.circle(img.copy(),(circles[0,0,0],circles[0,0,1]),circles[0,0,2],(255,0,0),5)

    mask = np.zeros(img.shape[:3], np.uint8)
    x = int(circles[0,0,0])
    y = int(circles[0,0,1])
    r = int(circles[0,0,2])

    cv2.circle(mask,(x,y),r,(255,255,255),-1)
    mask_inv = cv2.bitwise_not(mask)
    out = cv2.add(img, mask_inv)

    xs = max(x - r, 0)
    xe = min(x + r, img.shape[0])
    ys = y - r
    if ys > 200 or ys < 0: ys = 0
    ye = min(y + r, img.shape[1])

    f = out[ys:ye, xs:xe]
    f = cv2.resize(f, (440,440))
    cv2.imwrite('cropped_again.jpg', f)

    return f

def flatten(im, ac=0, tc=0):
    '''
	Returns rectangular flattened image from round image - TODO
	Args
		im: input image
		ac: amount to crop from the bottom of the input image
		tc: amount to crop from the top of the input image
	Returns
		cropped_polar_im: flattened image
	'''
    #im = Image.open(src)
    #im = im.resize((440,440))
    pim = Cartesian2Polar.project_cartesian_image_into_polar_image(im, origin=None)
    
    crop_height=min(310,pim.height)
    crop_width=min(10000,pim.width)
    cropped_polar_im = pim.crop(box=(0,0+tc,crop_width,crop_height-ac))
    
    return cropped_polar_im
    
def rotate(gc, angle):
    '''
    Rotates an image clockwise
    Args
        gc: input image
        angle: amount to rotate
    Returns
        rotated image
    '''
    M = cv2.getRotationMatrix2D((gc.shape[1]//2, gc.shape[0]//2), angle, 1.0)
    rot = cv2.warpAffine(gc, M, (gc.shape[1], gc.shape[0]),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rot

def order_points(pts):
    '''
     Puts points in order such that the first entry in the list is the top-left,
     the second entry is the top-right, the third is the bottom-right, 
     and the fourth is the bottom-left. Used for perspective transform.
     Args
        pts: list of 4 points (x,y)
    Returns
        rect: list of 4 ordered points
    '''
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    '''
    Applies opencvs perspective transform function
    Args
        image: input image to transform
        pts: list of pts of the 4 corners of the object to transform
    Returns
        warped: the perspective corrected image
    '''

    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped
