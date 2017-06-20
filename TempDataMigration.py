import argparse
import glob, os
import sqlite3


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--ReadPath", required = True, help = "Path to the images")
parser.add_argument("-w", "--DbName", required = True, help = "Name of database")

args = vars(parser.parse_args())


def DataMigration():
    #Check how many images are in the dir:
    os.chdir(args["ReadPath"])
    numberOfImages = len(glob.glob("*.jpg"))
    # Ask user if he/she wants to proceed with that many images:
    print("Number of images: " + str(numberOfImages))
    x = input("Do you want to proceed Y/n ")
    if x != "Y":
        return

    #Create database/ get reference to database and add table:
    conn = sqlite3.connect(args["DbName"])
    c = conn.cursor()
    # c.execute('''CREATE TABLE images
    #              (name text, path text)''')
    conn.commit()
    #Add all paths to db:
    i = 1
    for file in glob.glob("*.jpg"):
        dirName, imageHead = os.path.split(file)
        imageName = os.path.splitext(imageHead)[0]
        print("Adding file number " + str(i))
        c.execute("INSERT INTO images VALUES (?,?)", (imageName,file))

    conn.commit()
    conn.close()
DataMigration()