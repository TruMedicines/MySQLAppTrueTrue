import tensorflow as tf
import tflite_runtime.interpreter as tflite
from PIL import Image
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import cv2
import numpy as np


IOU = 0.45 # intersection over union threshold for detection
SCORE = 0.25 # confidence threshold for detection

'''
Functions for running tensorflow objection detection models
'''

#TODOS:
# Adjust model checkpoint based on packet type
# Adjust getXYData output based on packet type


'''
Helper function to turn the model output into usable data
'''
def filter_boxes(box_xywh, scores, score_threshold=0.4, input_shape = tf.constant([416,416])):
    scores_max = tf.math.reduce_max(scores, axis=-1)

    mask = scores_max >= score_threshold
    class_boxes = tf.boolean_mask(box_xywh, mask)
    pred_conf = tf.boolean_mask(scores, mask)
    class_boxes = tf.reshape(class_boxes, [tf.shape(scores)[0], -1, tf.shape(class_boxes)[-1]])
    pred_conf = tf.reshape(pred_conf, [tf.shape(scores)[0], -1, tf.shape(pred_conf)[-1]])

    box_xy, box_wh = tf.split(class_boxes, (2, 2), axis=-1)

    input_shape = tf.cast(input_shape, dtype=tf.float32)

    box_yx = box_xy[..., ::-1]
    box_hw = box_wh[..., ::-1]

    box_mins = (box_yx - (box_hw / 2.)) / input_shape
    box_maxes = (box_yx + (box_hw / 2.)) / input_shape
    boxes = tf.concat([
        box_mins[..., 0:1],  # y_min
        box_mins[..., 1:2],  # x_min
        box_maxes[..., 0:1],  # y_max
        box_maxes[..., 1:2]  # x_max
    ], axis=-1)
    # return tf.concat([boxes, pred_conf], axis=-1)
    return (boxes, pred_conf)


'''
Runs the tensorflow model on the given image
'''
def getPreds(image, model):
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
    #STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(FLAGS)
    input_size = 416

    original_image = image
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    image_data = cv2.resize(original_image, (input_size, input_size))
    image_data = image_data / 255.

    images_data = []
    for i in range(1):
        images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)

    if model == "persona":
        interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/persona.tflite')
    elif model == "nurish":
        #interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/nurish2.tflite')
        interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/nurishUpright.tflite')
    elif model == "easyVit":
        interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/easyVitaminTwo.tflite')
    #interpreter = tf.lite.Interpreter(model_path=FLAGS.weights)
    #interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/nurish2.tflite')
    #interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/easyVitamin.tflite')
    #interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/easyVit.tflite')
    #interpreter.reset_all_variables()
    #interpreter = tflite.Interpreter(model_path='/home/pi/MySQLApp/webapp/checkpoints/easyVitaminTwo.tflite')
    

    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], images_data)
    interpreter.invoke()
    pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]

    boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))


    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=50,
        max_total_size=50,
        iou_threshold=IOU,
        score_threshold=SCORE
    )

    pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
    #pred_bbox = [boxes.eval(session), scores.eval(session), classes.eval(session), valid_detections.eval(session)]
    #pred_bbox = [session.run(boxes), session.run(scores), session.run(classes), session.run(valid_detections)]

    session.close()
    return pred_bbox

'''
Wrapper for the getPreds function.
Handles loading and labelling of image and interpreting results.
'''
def getXYData(im, model, label=True):
    cv2.imwrite('SegmentImages/initial.jpg', im)
    if label:
        imbox = im.copy()
    out_boxes, out_scores, out_classes, num_boxes = getPreds(im, model)


    image_h, image_w, _ = im.shape
    #print(image_h, image_w)

    # ADJUST PER PACKET TYPE

    if model == "persona":
        num_classes = 4 #Persona packs have 4 different classes in the dictionary
        classes = {0: "barcode", 1: "perfline", 2: "pill", 3: "text"} #Persona/Pillpack Dictionary
    elif model == "nurish":
        num_classes = 3 #Nurish packs have 3 different classes in the dictions
        classes = {0: "perfline", 1: "pill", 2: "text"} #Nurish Classes Dictionary
    elif model == "easyVit":
        num_classes = 3 #Easy Vitamin packs have 3 clases in the dictionary
        classes = {0: "perfline", 1: "pill", 2: "text"} # Easy Vitamin Classes Dictionary
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
        
        if label:
            imbox = cv2.rectangle(imbox, (x1,y1), (x2,y2), colors[classes[it]], 2)
        
        res[classes[it]].append(((x1,x2), (y1,y2)))

    if label:
        cv2.imwrite('SegmentImages/labelled.jpg', imbox)

    return res




