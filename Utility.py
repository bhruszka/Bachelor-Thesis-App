import numpy as np

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def setGaps(G):
    global Gaps
    Gaps = G

def generateCorners(bUp, teethsNumber):

    Corners = [(0, 0), (0, 0), (0, 0), (0, 0)]

    if Gaps is None:
        return Corners

    if( bUp == True):
        Corners = Gaps[1][teethsNumber] + Gaps[1][teethsNumber + 1]
    else:
        Corners = Gaps[0][teethsNumber] + Gaps[0][teethsNumber + 1]

    return Corners
