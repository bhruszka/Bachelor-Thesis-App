import glob, os
import sqlite3

def importImages():
    #Check how many images are in the dir:

    #Create database/ get reference to database and add table:
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    #Add all paths to db:
    i = 1
    presentTeeth = "11111111111111111111111111111111"
    os.chdir("media/Images")
    for file in glob.glob("*.jpg"):
        dirName, imageHead = os.path.split(file)
        imageName = os.path.splitext(imageHead)[0]
        print("Adding file number " + str(i))
        c.execute("INSERT INTO imageDisp_pantomograminfo (present_teeth_text, input_image, image_name_text, pub_date) VALUES (?,?,?,?)", ( presentTeeth, "/Images/{}.jpg".format(imageName), imageName, "2017-07-02"))
        i += 1

    conn.commit()
    conn.close()


importImages()