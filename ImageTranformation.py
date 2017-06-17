import numpy as np
import cv2
import math
import matplotlib.pyplot as plt


from collections import namedtuple



def cutImage(image):

    borderGrey = cv2.adaptiveThreshold(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY),255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
    borderGrey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    histogram = []
    for i in range(0,borderGrey.shape[1]):
        temp = 0
        # Considering only lower half:
        for j in range(borderGrey.shape[0]//3, borderGrey.shape[0]):
            temp += borderGrey[j][i]
        histogram.append(temp)
    histogram = np.array(histogram)
    procent = borderGrey.shape[1]/100
    borderLeft = int(histogram[int(15 * procent):int(25 * procent)].argmin(axis=0) + 15 * procent)
    borderRight = int(histogram[int(75 * procent):int(90 * procent)].argmin(axis=0) + 75 * procent)
    print([borderGrey.shape[1], 75 *procent, borderLeft,borderRight])
    roi = image[0:image.shape[0], (borderLeft+16-borderLeft%16):(borderRight-borderRight%16)]

    histogram = histogram / (borderGrey.shape[0]//2)
    plt.plot(histogram)
    plt.axis([0, borderGrey.shape[1], 0, 255])
    #plt.show()

    return roi

def findGapEnds(image, hStart):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    histogram = []
    # vertical procent:
    hP = gray.shape[1] / 100
    vP = gray.shape[0] / 100
    for i in range(0,gray.shape[1]):
        temp = 0
        # Considering only lower half:
        for j in range(int(hStart - 15 * hP), int(hStart + 15 * hP)):
            temp += gray[j][i]
        histogram.append(temp)

    histogram = np.array(histogram)

    gapLeft = int(histogram[int(10*vP):int(25*vP)].argmin(axis=0) + 10*vP)
    gapRight = int(histogram[int(75*vP):int(90*vP)].argmin(axis=0) + 75 * vP)

    result = namedtuple('gapBorder', 'gapLeft gapRight')
    return image[:, (gapLeft+16-gapLeft%16):(gapRight-gapRight%16)]
def laplacePyramid(X0):
    # Laplacian Pyramid:
    # 1st layer:
    X1 = cv2.pyrDown(cv2.GaussianBlur(X0,(5,5),0))
    L1 = cv2.subtract(X0, cv2.pyrUp(X1))

    # 2nd layer:
    X2 = cv2.pyrDown(cv2.GaussianBlur(X1,(5,5),0))
    L2 = cv2.subtract(X1,cv2.pyrUp(X2))

    L2 = cv2.pyrUp(L2)
    L2 = cv2.resize(L2,None,fx=X0.shape[1]/L2.shape[1], fy=X0.shape[0]/L2.shape[0])

    # 3rd layer:
    X3 = cv2.pyrDown(cv2.GaussianBlur(X2,(5,5),0))
    L3 = cv2.subtract(X2, cv2.pyrUp(X3))

    L3 = cv2.pyrUp(L3)
    L3 = cv2.pyrUp(L3)
    L3 = cv2.resize(L3,None,fx=X0.shape[1]/L3.shape[1], fy=X0.shape[0]/L3.shape[0])

    # 4th layer:
    X4 = cv2.pyrDown(cv2.GaussianBlur(X3,(5,5),0))
    L4 = cv2.subtract(X3, cv2.pyrUp(X4))

    L4 = cv2.pyrUp(L4)
    L4 = cv2.pyrUp(L4)
    L4 = cv2.pyrUp(L4)
    L4 = cv2.resize(L4,None,fx=X0.shape[1]/L4.shape[1], fy=X0.shape[0]/L4.shape[0])

    result = namedtuple('result', 'L1 L2 L3 L4')

    return result(L1, L2, L3, L4)

