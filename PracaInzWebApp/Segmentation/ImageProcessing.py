import base64
import math
import cv2
import numpy as np
from PIL import Image
from Segmentation import ImageTranformation as iT
from Segmentation import Utility as uti
from Segmentation import WatershedMaker as sg

red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
nStripes = 12
minStripes = 5

toothWidth = [0.126493324, 0.098383696, 0.114546732,
              0.105411103, 0.099789178, 0.151791989,
              0.151791989, 0.151791989]


def mat2base64(mat):
    """Ecodes image array to Base64"""
    encoded = cv2.imencode(".jpg", mat)[1]
    b64 = base64.b64encode(encoded)
    return Image.fromarray(mat).convert("RGB")


def processImage(inputimg, writePath="", bTest=False):
    img = np.array(inputimg)
    img = iT.cutImage(img)

    process_images = [None] * 32

    # Resize:

    hFactor = 1000 / img.shape[0]
    img = cv2.resize(img, (0, 0), fx=hFactor, fy=hFactor)
    tempImg = np.empty((img.shape[0] + 16 - (img.shape[0] % 16), img.shape[1] + 16 - (img.shape[1] % 16), 3),
                       dtype=np.uint8)
    tempImg.fill(0)
    tempImg[0:img.shape[0], 0:img.shape[1], 0:3] = img
    img = np.array(tempImg, copy=True)

    image = np.array(img, copy=True)
    img_line_copy = np.copy(image)
    img_gap_copy = np.copy(image)

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)

    # 1. Find the gap valley line:

    # 1.a Finding vertical starting point(nose line):
    noseline = 0
    bHist = 0
    for i in range(45 * gray.shape[1] // 100, 55 * gray.shape[1] // 100):
        hist = 0

        for j in range(20 * gray.shape[0] // 100, 45 * gray.shape[0] // 100):
            for k in range(-2, 2):
                if gray[j, i] > 200:
                    hist += gray[j, i + k]
        hist *= uti.gaussian(i, gray.shape[1] // 2, 10 * gray.shape[1] // 100)
        if (hist > bHist):
            noseline = i
            bHist = hist

    if (bHist / (25 * gray.shape[0] // 100)) < 300:
        noseline = image.shape[1] // 2
    cv2.line(img_line_copy, (noseline, 20 * gray.shape[0] // 100),
             (noseline, 45 * gray.shape[0] // 100), green)


    # 1.b Finding horizontal starting point:
    histogram = []
    startingPoint = gray.shape[0] // 2

    for i in range(0, gray.shape[0]):
        temp = 0
        for j in range(4 * image.shape[1] // 10, 6 * image.shape[1] // 10):
            temp += gray[i, j]
        histogram.append(temp)

    for i in range((50 * image.shape[0]) // 100, (80 * image.shape[0]) // 100):
        if histogram[startingPoint] > histogram[i]:
            startingPoint = i

    cv2.line(img_line_copy, (4 * image.shape[1] // 10, startingPoint),
             (6 * image.shape[1] // 10, startingPoint), blue)

    cv2.circle(img_line_copy, (noseline, startingPoint), 5, red, 1)
    cv2.circle(img_gap_copy, (noseline, startingPoint), 5, red, 1)

    # 1.c Finding gap ends:

    gapLine = np.empty(image.shape[1], dtype=np.uint16)
    gapLine.fill(0)
    gapLineSlope = np.empty(image.shape[1], dtype=np.double)
    gapLineSlope.fill(0.0)


    # 1.d  Left side gap line:
    L4 = iT.laplacePyramid(image).L2
    L4 = cv2.cvtColor(L4, cv2.COLOR_RGB2GRAY)

    afterLaplace = gray
    afterLaplace = cv2.add(L4, afterLaplace)
    afterLaplace_Copy = cv2.cvtColor(np.copy(afterLaplace), cv2.COLOR_GRAY2BGR)
    cv2.circle(afterLaplace_Copy, (noseline, startingPoint), 5, red, 1)
    stripeSize = (gray.shape[1] // nStripes)
    startingPointTemp = startingPoint

    for k in range(1, nStripes // 2):
        histogram = []

        for i in range(0, image.shape[0]):
            temp = 0
            dY = (startingPoint - i) / stripeSize
            m = 0
            for j in range(noseline - (k) * stripeSize, noseline - (k - 1) * stripeSize):
                temp += afterLaplace[int(math.floor(i + dY * m)), j]
                m += 1
            histogram.append(temp)
        oldStartingPoint = startingPoint

        l = int(oldStartingPoint - 6.0 / 100.0 * afterLaplace.shape[0])
        u = int(oldStartingPoint + 2.0 / 100.0 * afterLaplace.shape[0])

        for i in range(l, u):
            if histogram[startingPoint] > histogram[i]:
                startingPoint = i

        # print(histogram[startingPoint] / stripeSize)
        if histogram[startingPoint] / stripeSize < 100 or k < minStripes:
            cv2.line(afterLaplace_Copy, (noseline - (k - 1) * stripeSize, oldStartingPoint),
                     (noseline - (k) * stripeSize, startingPoint), green)
            cv2.line(img_gap_copy, (noseline - (k - 1) * stripeSize, oldStartingPoint),
                     (noseline - (k) * stripeSize, startingPoint), green)
            m = 0
            dY = (startingPoint - oldStartingPoint) / (stripeSize)
            for i in range(noseline - (k) * stripeSize, noseline - (k - 1) * stripeSize):
                gapLine[i] = math.floor(startingPoint - dY * m)
                gapLineSlope[i] = dY
                m += 1
        else:
            break
    # cv2.imshow('afterLaplace', afterLaplace)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # Right side gap line:
    startingPoint = startingPointTemp

    for k in range(1, nStripes // 2):
        histogram = []

        for i in range(0, image.shape[0]):
            temp = 0
            dY = (i - startingPoint) / (stripeSize)
            m = 0

            for j in range(noseline + (k - 1) * stripeSize, noseline + (k) * stripeSize):
                temp += afterLaplace[int(math.floor(startingPoint + dY * m)), j]
                m += 1

            histogram.append(temp)
        oldStartingPoint = startingPoint
        l = int(oldStartingPoint - 6.0 / 100.0 * afterLaplace.shape[0])
        u = int(oldStartingPoint + 2.0 / 100.0 * afterLaplace.shape[0])

        for i in range(l, u):
            if histogram[startingPoint] > histogram[i]:
                startingPoint = i

        # print(histogram[startingPoint] / stripeSize)
        if histogram[startingPoint] / stripeSize < 100 or k < minStripes:
            cv2.line(afterLaplace_Copy, (noseline + (k - 1) * stripeSize, oldStartingPoint),
                     (noseline + (k) * stripeSize, startingPoint), green)
            cv2.line(img_gap_copy, (noseline + (k - 1) * stripeSize, oldStartingPoint),
                     (noseline + (k) * stripeSize, startingPoint), green)
            m = 0
            dY = (oldStartingPoint - startingPoint) / (stripeSize)

            for i in range(noseline + (k - 1) * stripeSize, noseline + (k) * stripeSize):
                gapLine[i] = math.floor(oldStartingPoint - dY * m)
                gapLineSlope[i] = -dY
                m += 1
        else:
            break
    # 2. Calculating gap width, start of the gap, the gap center and tooth width:
    gapWidth = 0
    gapStart = 0
    gapEnd = gapLine.shape[0] - 1
    gapCenter = 0
    squareSize = 1;
    for i in range(0, int(30.0 / 100.0 * gapLine.shape[0])):
        if gapLine[i] > 0 and np.average(afterLaplace[(gapLine[i] - squareSize):(gapLine[i] + squareSize),
                                         (i - squareSize):(i + squareSize)]) < 80:
            gapStart = i
            break

    for j in range(0, int(30.0 / 100.0 * gapLine.shape[0])):
        i = gapLine.shape[0] - j - 1
        if gapLine[i] > 0 and np.average(afterLaplace[(gapLine[i] - squareSize):(gapLine[i] + squareSize),
                                         (i - squareSize):(i + squareSize)]) < 80:
            gapEnd = i
            break
    gapLine[:gapStart] = 0
    gapLine[gapEnd:] = 0
    gapWidth = gapEnd - gapStart

    gapWidth /= 2
    gapCenter = int(gapStart + gapWidth)

    toothWidth = np.array(
        [[0.120682116, 0.100422679, 0.108439003, 0.106398484, 0.103191955, 0.153621921, 0.153621921, 0.153621921]
            , [0.080737641, 0.096079343, 0.102432977, 0.111730978, 0.113900511, 0.165039517, 0.165039517, 0.165039517]],
        dtype=np.double)

    toothWidth = toothWidth * (gapWidth - 1)

    # 3. Finding upper and lower jaw lines:

    # the amount of pixels that the vertical position of every point belonging to the spline separating jaws should be moved
    # for in order to receive the spline that passes through dental pulps of teeth in each jaw:

    down_dJ = 0
    min_sum_down_dJ = 0
    max_p_down_dJ = 0
    all_sum_down_dJ = []

    # finding up_dJ:
    # min_sum_up_dJ
    updownDjImage = cv2.add(L4, cv2.cvtColor(image, cv2.COLOR_RGB2GRAY))

    ret, updownDjImage = cv2.threshold(updownDjImage, 90, 255, cv2.THRESH_BINARY)

    # cv2.imshow('afterLaplace', updownDjImage)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # updownDjImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) + L4
    for i in range(gray.shape[0] // 20, gray.shape[0] // 10):
        index_down_dJ = i
        sum_down_dJ = 0
        p_down_dJ = 0
        down_Cool_Down = 0
        for j in range(int(noseline - 0.3 * gray.shape[1]), int(noseline + 0.3 * gray.shape[1])):
            if gapLine[j] > 0:
                sum_down_dJ += updownDjImage[gapLine[j] + index_down_dJ, j]

                if down_Cool_Down < 0 and updownDjImage[gapLine[j] + index_down_dJ, j - 1] == 255 and \
                                updownDjImage[gapLine[j] + index_down_dJ, j] == 0:
                    p_down_dJ += 1
                    down_Cool_Down = gray.shape[1] // 100

                down_Cool_Down -= 1

        if (min_sum_down_dJ > sum_down_dJ) or (min_sum_down_dJ == 0):
            min_sum_down_dJ = sum_down_dJ
            down_dJ = index_down_dJ

        all_sum_down_dJ.append(sum_down_dJ)

    up_dJ = 0
    min_sum_up_dJ = 0
    max_p_up_dJ = 0

    all_sum_up_dJ = []

    for i in range(gray.shape[0] // 20, gray.shape[0] // 10):
        index_up_dJ = -i
        sum_up_dJ = 0
        p_up_dJ = 0
        up_Cool_Down = 0

        for j in range(int(noseline - 0.3 * gray.shape[1]), int(noseline + 0.3 * gray.shape[1])):
            if gapLine[j] > 0:
                sum_up_dJ += updownDjImage[gapLine[j] + index_up_dJ, j]

                if up_Cool_Down < 0 and updownDjImage[gapLine[j] + index_up_dJ, j - 1] == 255 and \
                                updownDjImage[gapLine[j] + index_up_dJ, j] == 0:
                    p_up_dJ += 1
                    up_Cool_Down = gray.shape[1] // 100

                up_Cool_Down -= 1
        # print("min:")
        # print(min_sum_up_dJ)
        # print(sum_up_dJ)
        if (min_sum_up_dJ > sum_up_dJ) or (min_sum_up_dJ == 0):
            min_sum_up_dJ = sum_up_dJ
            up_dJ = index_up_dJ
            # print("change")

        all_sum_up_dJ.append(sum_up_dJ)

    # down_dJ = gray.shape[0] // 15
    # up_dJ = -gray.shape[0] // 15


    # 4. Calculating background area
    backGround = np.empty(gray.shape, dtype=np.uint16)
    backGround.fill(0)

    bG_up_dj = int(1.5 * up_dJ)
    bG_down_dj = int(1.5 * down_dJ)
    gapEnd = int(gapStart + 2 * gapWidth)
    for i in range(gapStart, gapEnd):
        backGround[(gapLine[i] + bG_up_dj):(gapLine[i] + bG_down_dj), i] = 255
        backGround[(gapLine[i] - 1):(gapLine[i] + 10), i]  = 0
        img_gap_copy[gapLine[i] + up_dJ, i] = (255, 0, 0)
        img_gap_copy[gapLine[i] + down_dJ, i] = (0, 0, 255)
    backGround[(gapLine[gapStart] + bG_up_dj):(gapLine[gapStart] + bG_down_dj), :int(gapStart)] = 255
    backGround[
    (gapLine[gapEnd - 1] + bG_up_dj):(gapLine[gapEnd - 1] + bG_down_dj),
    (gapEnd - 1):] = 255

    backGround[(gapLine[int(gapStart)] - 1):(gapLine[int(gapStart)] + 10), :int(gapStart)] = 0
    backGround[(gapLine[(gapEnd - 1)] - 1):(gapLine[(gapEnd - 1)] + 10),
    (gapEnd - 1):] = 0


    # img = cv2.cvtColor(afterLaplace,cv2.COLOR_GRAY2RGB)
    # img = cv2.bitwise_and(img, img, mask=np.uint8(backGround))


    afterLaplace = cv2.cvtColor(afterLaplace, cv2.COLOR_GRAY2RGB)
    resultImage, thresh, thisToothPossition, bTeeth, teethImages = sg.makeWaterShed(afterLaplace, toothWidth, up_dJ,
                                                                                    down_dJ, gapLine, gapLineSlope, gapCenter,
                                                                                    backGround)
    process_images[0] = mat2base64(img_line_copy)
    process_images[1] = mat2base64(afterLaplace_Copy)
    process_images[2] = mat2base64(img_gap_copy)

    return mat2base64(tempImg), mat2base64(resultImage), mat2base64(thresh), thisToothPossition, bTeeth, teethImages, process_images


def redoWatershed(inputimg, threshimg, thisToothPossition):
    img = np.array(inputimg)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)

    L4 = iT.laplacePyramid(img).L2
    L4 = cv2.cvtColor(L4, cv2.COLOR_RGB2GRAY)

    afterLaplace = gray
    afterLaplace = cv2.add(L4, afterLaplace)

    thisToothPossitionCopy = np.copy(thisToothPossition)
    thisToothPossition[:, 0:8] = thisToothPossitionCopy[:, range(7, -1, -1)] #good
    thisToothPossition[:, 16:24] = thisToothPossitionCopy[:, range(15, 7, -1)]#good
    thisToothPossition[:, 8:16] = thisToothPossitionCopy[:, range(24, 32, 1)]
    thisToothPossition[:, 24:32] = thisToothPossitionCopy[:, range(16, 24, 1)]


    thresh = np.array(threshimg)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    afterLaplace = cv2.cvtColor(afterLaplace, cv2.COLOR_GRAY2RGB)
    resultimg, thresh, thisToothPossition, bTeeth, teethImages = sg.waterShed(afterLaplace, thisToothPossition, thresh)
    return mat2base64(resultimg), bTeeth, teethImages
