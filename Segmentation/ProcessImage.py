import argparse
import ImageProcessing as ip


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--ReadPath", required = True, help = "Path to the image")
parser.add_argument("-w", "--WritePath", required = True, help = "Path to the save dir")

args = vars(parser.parse_args())



ip.processImage(args["ReadPath"], args["WritePath"], False)