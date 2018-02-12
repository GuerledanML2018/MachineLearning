from __future__ import print_function # Use a function definition from future version (say 3.x from 2.7 interpreter)

import matplotlib.pyplot as plt
import numpy as np
import PIL
import sys
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

import cntk as C
import sklearn.metrics as metrics

from PIL import Image

DATASET_NAME = 'data_guerledan_metz_dangers'
SAVEFILE_NAME = 'guerledan_save_8.model'

# model dimensions
image_height = 128
image_width  = 72
num_channels = 3
num_classes  = 2

def compute_confusion_matrix(pred):
    # Load the true labels
    true_labels = []
    images = []
    for l in open("../../" + DATASET_NAME + "/test.txt", "r") :
        images.append(l.split('\t')[0])
        true_labels.append(int(l.split('\t')[1][:-1]))

    # evaluate all the images
    ev_labels = []
    for im_name in images:
        result = eval_single_image(pred, im_name, (3, 224, 224))
        ev_labels.append(np.argmax(result))

    # compute confusion matrix
    conf_mat = metrics.confusion_matrix(true_labels, ev_labels)
    return conf_mat


def eval_single_image(loaded_model, image_path, image_dims):
    # load and format image (resize, RGB -> BGR, CHW -> HWC)
    try:
        img = Image.open(image_path)

        if image_path.endswith("png"):
            temp = Image.new("RGB", img.size, (255, 255, 255))
            temp.paste(img, img)
            img = temp
        resized = img.resize((image_dims[2], image_dims[1]), Image.ANTIALIAS)
        bgr_image = np.asarray(resized, dtype=np.float32)[..., [2, 1, 0]]
        hwc_format = np.ascontiguousarray(np.rollaxis(bgr_image, 2))

        # compute model output
        arguments = {loaded_model.arguments[0]: [hwc_format]}
        output = loaded_model.eval(arguments)

        # return softmax probabilities
        sm = C.softmax(output[0])
        return sm.eval()
    except FileNotFoundError:
        print("Could not open (skipping file): ", image_path)
        return ['None']



mod = "temp/Output/" + SAVEFILE_NAME
z = C.load_model(mod)
print("Modèle chargé :", mod)
# pred = C.softmax(z)


# eval(pred, myimg)
conf_mat = compute_confusion_matrix(z)
print(conf_mat)
print("Pourcentage de réussite :", 100*sum(np.diag(conf_mat))/np.sum(
    conf_mat), "%")