## All functions for producing a serial number from an etched pill ##

import cv2
import pytesseract
import numpy as np
import webapp.ImageUtils as utils
import webapp.JSONWriter as jw

### TODOS
# Fix the search database function 

def rotated_to_text(src):
    '''
    Rotates image so text is horizontal
    Args
        src: file location of input image
    Returns
        rotated: horizontal image
    '''
    imgo = src
    imgo_big = cv2.copyMakeBorder(imgo, 5, 5,5, 5, cv2.BORDER_CONSTANT, value=(255,255,255))
    rect = get_min_rect(imgo)
    
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    #print("box: ", box)
    #imbox = cv2.drawContours(imgo_big.copy(),[box],0,(0,0,255),2)
    #plt.imshow(imbox)
    angle = rect[2]
    
    if rect[1][0] < rect[1][1]:
        if angle < -45:
            angle = (angle + 90)
        else:
            angle = angle-90        
        
    (h, w) = imgo_big.shape[:2]
    center = (w / 2.0, h / 2.0)
    #M = cv2.getRotationMatrix2D(center, angle, 1.0)
    #rotated = cv2.warpAffine(imgo_big, M, (w, h),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    rotated = utils.rotate(imgo_big, angle)
    #plt.imshow(rotated)
    return rotated

def get_cropped_from_src(src):
    '''
    Finds all possible words on an etched pill
    Args
        src: file location of input image
    Returns
        results: list of individual word images
    '''
    results = []
    fixed = rotated_to_text(src)
    cv2.imwrite('etch-images/rotated.jpg', fixed)

    rects = get_rect(fixed)

    fixed_big = cv2.copyMakeBorder(fixed, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=(255,255,255))

    for x,y,w,h in rects:
        c = fixed_big[y:y+h, x:x+w]
        results.append(c)
    return results
    
    
def get_min_rect(imgo):
    '''
    Find the minimum area rectangle around all text to correct rotation
    Args
        imgo: input pill image
    Returns
        rect: min area rectangle
    '''
    results = []
    img = cv2.medianBlur(imgo,5)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    __, th = cv2.threshold(gray, 100, 255, 0)
    #plt.imshow(th, cmap='gray')
    new = cv2.copyMakeBorder(th, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255);

    ker = np.ones((3,3))
    im = cv2.erode(new, ker, iterations=6)

    contours = cv2.findContours(im,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    cs = sorted(contours, key=cv2.contourArea)
    index = len(cs) - 2
    con = cs[index]
    img_con = cv2.drawContours(new.copy(), [con], 0, (0,0,255), 2);
    #cv2.imwrite('images/etched_results/contour.jpg', img_con)

    #plt.imshow(img_con)
    rect = cv2.minAreaRect(con)
                
    return rect
    
    
def get_rect(imgo):
    '''
    Finds the bounding box of individual words
    Args
        imgo: input pill image (with corrected rotation)
    Returns
        results: list of bounding rectangles
    '''
    results = []
    img = cv2.medianBlur(imgo,5)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    __, th = cv2.threshold(gray, 100, 255, 0)
    new = cv2.copyMakeBorder(th, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255);
    
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 3))

    gradX = cv2.morphologyEx(new, cv2.MORPH_OPEN, rectKernel)

    contours = cv2.findContours(gradX,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    cs = sorted(contours, key=cv2.contourArea)
    index = len(cs) - 2

    for c in cs:
        if cv2.contourArea(c) > 5000 and cv2.contourArea(c) < 40000:
            results.append(cv2.boundingRect(c))
                
    return results
    
def read_good(img):
    '''
    Read an image of text using pytesseract several times
    Args
        img: input image of word/text
    Returns
        string of attempted read #4
    '''
    word_found = False
    big = cv2.resize(img, (0,0), fx=2, fy=2)

    bl = cv2.medianBlur(big, 5)
    bl = cv2.medianBlur(bl, 5)

    gc = cv2.cvtColor(bl, cv2.COLOR_BGR2GRAY)     
    ret2,th = cv2.threshold(gc,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    bord = cv2.copyMakeBorder(th, 40, 40,40, 40, cv2.BORDER_CONSTANT, value=255)
    # Initial read attempt
    word = attempt_to_read(bord)
    word_found = search_database(word)
    ker = np.ones((3,3))

    if (not word_found):
        # Second attempt
        di = cv2.dilate(bord, ker, iterations=1)
        word = attempt_to_read(di)
        word_found = search_database(word)

    if (not word_found):
        # Third attempt
        di = cv2.dilate(di, ker, iterations=1)
        word = attempt_to_read(di)
        word_found = search_database(word)

    if (not word_found):
        # Fourth attempt - scaled down
        di = cv2.resize(di, (0, 0), fx=.25, fy=.25)
        word = attempt_to_read(di)
        word_found = search_database(word)
    
    if (not word_found):
        word = None

    return word

def transformAndRead(img):
    '''
    Read an image of text using pytesseract several times
    Args
        img: input image of word/text
    Returns
        string of attempted read #4
    '''
    word_found = False
    word = attempt_to_read(img)
    word_found = search_database(word)
    
    if not word_found:
        big = cv2.resize(img, (0,0), fx=2, fy=2)

        bl = cv2.medianBlur(big, 5)
        bl = cv2.medianBlur(bl, 5)

        gc = cv2.cvtColor(bl, cv2.COLOR_BGR2GRAY)     
        ret2,th = cv2.threshold(gc,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
        bord = cv2.copyMakeBorder(th, 40, 40,40, 40, cv2.BORDER_CONSTANT, value=255)
        # Initial read attempt
        word = attempt_to_read(bord)
        word_found = search_database(word)
        ker = np.ones((3,3))

    if (not word_found):
        # Second attempt
        di = cv2.dilate(bord, ker, iterations=1)
        word = attempt_to_read(di)
        word_found = search_database(word)

    if (not word_found):
        # Third attempt
        di = cv2.dilate(di, ker, iterations=1)
        word = attempt_to_read(di)
        word_found = search_database(word)

    if (not word_found):
        # Fourth attempt - scaled down
        di = cv2.resize(di, (0, 0), fx=.25, fy=.25)
        word = attempt_to_read(di)
        word_found = search_database(word)
    
    if (not word_found):
        word = None

    return word

def search_database(word):
    if len(word) > 0:
        word = word.lower().strip()
        #print("looking for: ", word)
        #code, ID = jw.get_data_from_file('json/etchDB.json', word)
        if "david" in word or "walk" in word or "exp" in word or "lot" in word:
            #print("    found word")
            return True
        else:
            #print("    no word match")
            return False
        #if ID == "not found":
        #    print("    not in database")
        #    return False
        #else:
        #    print("    Found pill ", ID, " at code ", code)
        #    return True
    
def attempt_to_read(img):
    '''
    Convenience function to run pytesseract
    Args
        letter: image of word to read
    Returns
        text output of pytesseract
    '''
    text = pytesseract.image_to_string(img)
    #print(text)
    return text
    
def read_etched_pill(src):
    '''
    Main function to crop pill image and read each word
    Args
        src: file location of pill image
    '''
    cropped = get_cropped_from_src(src)
    for word in cropped:
        res = None
        gc = word
        cv2.imwrite('AnalysisImages/cropped.jpg', gc)
        res = read_good(gc)
        if res:
            return res
        rot = utils.rotate(gc, 180)
        res = read_good(rot)
        if res:
            return res
    return res
