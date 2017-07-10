import sqlite3
import datetime

def addImage(image_name, present_teeth_text):
    # Connecting to database
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    now = datetime.datetime.now()
    input_image = "Images/{}.jpg".format(image_name)
    output_image = "OutputImages/{}.jpg".format(image_name)
    thresh_image = "ThreshImages/Images/{}.jpg".format(image_name_text)
    
    c.execute(
        "INSERT INTO imageDisp_pantomograminfo (present_teeth_text, image_name_text, input_image, output_image, thresh_image, pub_date) VALUES (?,?,?,?,?,?)",
        (present_teeth_text, image_name, input_image, output_image, thresh_image, now))


