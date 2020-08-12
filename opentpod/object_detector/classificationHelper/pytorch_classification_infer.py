# License: BSD
# Author: Sasank Chilamkurthy
# © Copyright 2017, PyTorch
# https://github.com/pytorch/tutorials/blob/master/beginner_source/transfer_learning_tutorial.py
# https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html#sphx-glr-beginner-transfer-learning-tutorial-py

# Modified: Zhen Luan zluan@andrew.cmu.edu
import torch
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
from PIL import Image
import os

# ---------Required Info------------
MODELDIR = '<Model Path>'
IMAGEPATH = '<Image Path>'
# ----------------------------------

MODELPATH = os.path.join(MODELDIR, 'result.pth')
INFOPATH = os.path.join(MODELDIR, 'info.txt')

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def getItemInfo():
    infodict = {}
    fp = open(INFOPATH, 'r')
    info = fp.read().split()
    for i in info:
        index2item = i.split(':')
        # print(index2item)
        infodict[int(index2item[0])] = index2item[1]
    fp.close()
    return infodict

def classified(image_path):
    infodict = getItemInfo()
    model_ft = torch.load(MODELPATH)
    input_image = Image.open(image_path)

    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

    # move the input and model to GPU for speed if available
    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model_ft.to('cuda')

    with torch.no_grad():
        output = model_ft(input_batch).numpy()[0]

    resultIndex = np.argmax(output)
    return infodict[resultIndex]

item = classified(IMAGEPATH)
print(item)
