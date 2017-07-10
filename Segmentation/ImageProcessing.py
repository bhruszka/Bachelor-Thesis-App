import numpy as np
import math
import os.path
import Segmentation as sg
import Utility as uti
import ImageTranformation as iT
import cv2
import SaveToDB as sb


red = (0, 0, 255)
green = (0, 255, 0)
nStripes = 12
minStripes = 5

toothWidth = [0.126493324, 0.098383696, 0.114546732,
              0.105411103, 0.099789178, 0.151791989,
              0.151791989, 0.151791989]

def processImage(imagePath, writePath, bTest):

    img = cv2.imread(imagePath, 1)

    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    img = iT.cutImage(img)
    # Resize:

    hFactor = 1000 / img.shape[0]
    print(hFactor)
    print(img.shape)
    img = cv2.resize(img, (0, 0), fx=hFactor, fy=hFactor)


    tempImg = np.empty((img.shape[0] + 16 - (img.shape[0] % 16), img.shape[1] + 16 - (img.shape[1] % 16), 3), dtype=np.uint8)

    tempImg.fill(0)
    tempImg[0:img.shape[0],0:img.shape[1],0:3] = img
    img = np.array(tempImg, copy=True)
    #img = cv2.GaussianBlur(img,(3,3),0)
    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #if(img.shape[1] % 16 != 0):
    image = np.array(img, copy=True)



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


    # 1.c Finding gap ends:
    # image = iT.findGapEnds(image, startingPoint)
    # img = np.array(image, copy=True)
    # gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # gray = cv2.equalizeHist(gray)
    gapLine = np.empty(image.shape[1], dtype=np.uint16)
    gapLine.fill(0)
    # noseline = gray.shape[1] // 2

    # 1.d  Left side gap line:
    L4 = iT.laplacePyramid(image).L2
    L4 = cv2.cvtColor(L4, cv2.COLOR_RGB2GRAY)
    ret, mask = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
    # mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # mask = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #         cv2.THRESH_BINARY,11,2)
    #afterLaplace = cv2.bitwise_and(gray, gray, mask=mask)
    afterLaplace = gray
    afterLaplace = cv2.add(L4, afterLaplace)

    #afterLaplace = cv2.bitwise_and(L4, L4, mask=mask)
    #afterLaplace = L4


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

        l = int( oldStartingPoint - 6.0/100.0 * afterLaplace.shape[0])
        u = int( oldStartingPoint + 2.0/100.0 * afterLaplace.shape[0])

        for i in range(l, u):
            if histogram[startingPoint] > histogram[i]:
                startingPoint = i

        # print(histogram[startingPoint] / stripeSize)
        if histogram[startingPoint] / stripeSize < 100 or k < minStripes:
            # cv2.line(image, (noseline - (k - 1) * stripeSize, oldStartingPoint),
            #          (noseline - (k) * stripeSize, startingPoint), red)
            m = 0
            dY = abs((startingPoint - oldStartingPoint) / (stripeSize))
            for i in range(noseline - (k) * stripeSize, noseline - (k - 1) * stripeSize):
                gapLine[i] = math.floor(startingPoint + dY * m)
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
        l = int( oldStartingPoint - 6.0/100.0 * afterLaplace.shape[0])
        u = int( oldStartingPoint + 2.0/100.0 * afterLaplace.shape[0])

        for i in range(l, u):
            if histogram[startingPoint] > histogram[i]:
                startingPoint = i

        # print(histogram[startingPoint] / stripeSize)
        if histogram[startingPoint] / stripeSize < 100 or k < minStripes:
            # cv2.line(image, (noseline + (k - 1) * stripeSize, oldStartingPoint),
            #          (noseline + (k) * stripeSize, startingPoint), red)
            m = 0
            dY = (oldStartingPoint - startingPoint) / (stripeSize)

            for i in range(noseline + (k - 1) * stripeSize, noseline + (k) * stripeSize):
                gapLine[i] = math.floor(oldStartingPoint - dY * m)
                m += 1
        else:
            break
    # 2. Calculating gap width, start of the gap, the gap center and tooth width:
    gapWidth = 0
    gapStart = 0
    gapEnd = gapLine.shape[0] - 1
    gapCenter = 0
    squareSize = 1;
    for i in range(0, int(30.0/100.0 * gapLine.shape[0])):
        if gapLine[i] > 0 and np.average(afterLaplace[(gapLine[i]-squareSize):(gapLine[i]+squareSize), (i-squareSize):(i+squareSize)]) < 80:
            gapStart = i
            break

    for j in range(0, int(30.0/100.0 * gapLine.shape[0])):
        i = gapLine.shape[0] - j - 1
        if gapLine[i] > 0 and np.average(afterLaplace[(gapLine[i] - squareSize):(gapLine[i] + squareSize), (i - squareSize):(i + squareSize)]) < 80:
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

    #updownDjImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) + L4
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
            #print("change")

        all_sum_up_dJ.append(sum_up_dJ)

    #down_dJ = gray.shape[0] // 15
    #up_dJ = -gray.shape[0] // 15


    # 4. Calculating background area
    backGround = np.empty(gray.shape, dtype=np.uint16)
    backGround.fill(0)

    markers = np.empty(gray.shape, dtype=np.uint16)
    markers.fill(0)
    for i in range(int(gapStart), int(gapStart + 2 * gapWidth)):
        markers[(gapLine[i] + up_dJ):(gapLine[i] + down_dJ), i] = 1
        backGround[(gapLine[i] + 2 * up_dJ ):(gapLine[i] + 2 * down_dJ), i] = 255
        backGround[(gapLine[i] -1):(gapLine[i] + 10), i] = 0
    #img = cv2.cvtColor(afterLaplace,cv2.COLOR_GRAY2RGB)
    #img = cv2.bitwise_and(img, img, mask=np.uint8(backGround))


    dirName, imageHead = os.path.split(imagePath)
    imageName = os.path.splitext(imageHead)[0]
    saveFolderDir = writePath + "/" + imageName

    afterLaplace = cv2.cvtColor(afterLaplace, cv2.COLOR_GRAY2RGB)
    print(afterLaplace.shape)
    resultImage, thresh = sg.makeWaterShed(afterLaplace, toothWidth, up_dJ, down_dJ, gapLine, gapCenter, saveFolderDir, backGround, bTest)
    writePath = "./PracaInzWebApp/media/"


    if bTest:
        cv2.imwrite(writePath + "/" + imageName + ".jpg", resultImage)

    else:
        imageFileName = imageName + ".jpg"
        writePathImage = writePath + "Images"
        writePathOutputImages = writePath + "OutputImages"
        writePathThreshImages = writePath + "ThreshImages"

        if not os.path.exists(writePathImage):
            os.makedirs(writePathImage)
        cv2.imwrite(saveFolderDir + "/" + imageFileName, img)

        if not os.path.exists(writePathOutputImages):
            os.makedirs(writePathOutputImages)
        cv2.imwrite(saveFolderDir + "/" + imageFileName, resultImage)

        if not os.path.exists(writePathThreshImages):
            os.makedirs(writePathThreshImages)
        cv2.imwrite(saveFolderDir + "/" + imageFileName, thresh)

        sb.addImageToDb(imageName, "1111111111111111")


# imagePathArg = "D:\\Projects\\Images\\P20140512_132024_0000.jpg"
# writePathArg = "D:\\Projects\\Results"
# processImage(imagePathArg, writePathArg)