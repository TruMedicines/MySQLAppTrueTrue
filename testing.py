import cv2
from webapp.yoloCore import getPreds
import webapp.pin_controller as pins
from PIL import Image
import numpy as np


#im = pins.takePhoto()
#im = Image.open('/home/pi/Pictures/EasyVitamin/evit1_15.jpg')
im = Image.open('/home/pi/MySQLApp/webapp/static/pillPic.jpg')
im = np.array(im)
#cv2.imwrite('SegmentImages/initial.jpg', im)
if True:
    imbox = im.copy()
out_boxes, out_scores, out_classes, num_boxes = getPreds(im)


image_h, image_w, _ = im.shape
#print(image_h, image_w)

# ADJUST PER PACKET TYPE
num_classes = 3 #nurish
classes = {0: "barcode", 1: "perfline", 2: "pill", 3: "text"} #Persona/pillpack
classes = {0: "perfline", 1: "pill", 2: "text"} #nurish
res = { "perfline": [], "pill": [], "text": []}
###

colors = {"barcode": (255,0,0), "text": (0,255,0), "perfline": (0,0,255), "pill": (255,255,0)}

for i in range(num_boxes[0]):
    if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > num_classes: continue
    
    it = int(out_classes[0][i])

    coord = out_boxes[0][i]
    y1 = int(coord[0] * image_h)
    y2 = int(coord[2] * image_h)
    x1 = int(coord[1] * image_w)
    x2 = int(coord[3] * image_w)
    
    if True:
        imbox = cv2.rectangle(imbox, (x1,y1), (x2,y2), colors[classes[it]], 2)
    
    res[classes[it]].append(((x1,x2), (y1,y2)))

if res["perfline"]:
    line = (res["perfline"][0][1][0]+res["perfline"][0][1][1])//2
    print("Testing Perf line at", line)
else:
    print("Testing Perf Line not Found")