#!/usr/bin/env python3

import io
import sys
import time
from lib import flask_helpers
import anki_vector

###############################################################################
try:
    from flask import Flask, request
except ImportError:
    sys.exit("Cannot import from flask: Do `pip3 install --user flask` to install")

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")


###############################################################################
# Create a place-holder PIL image to use until we have a live feed from Vector"""
def create_default_image(image_width, image_height):
    image_bytes = bytearray([0x70, 0x70, 0x70]) * image_width * image_height
    image = Image.frombytes('RGB', (image_width, image_height), bytes(image_bytes))
    return image

flask_app = Flask(__name__)
_default_camera_image = create_default_image(320, 240)


###############################################################################
def get_annotated_image():
    image = flask_app.vectorstream.vector.camera.latest_image
    return image.annotate_image()

###############################################################################
# Runs a endless loop
def run_loop():
    while True:

        # Video streaming generator function
        if flask_app.vectorstream:
            image = get_annotated_image()

            img_io = io.BytesIO()
            image.save(img_io, 'PNG')
            img_io.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + img_io.getvalue() + b'\r\n')
        else:
            pass
        
         time.sleep(.1)

###############################################################################
# Erzeugt website unter 127.0.0.1:5000
@flask_app.route("/")
def handle_index_page():
    return """
    <html>
        <body>
            <img src="vectorImage" id="vectorImageId" width=100%>
        </body>
    </html>
    """

###############################################################################
@flask_app.route("/vectorImage")
def handle_vectorImage():
    return flask_helpers.stream_video(run_loop)

###############################################################################
class VectorStream:
    def __init__(self, robot):
        self.vector = robot

###############################################################################
def runFlask(robot):
    flask_app.vectorstream = VectorStream(robot)
    flask_app.display_debug_annotations = 1
    flask_app.run(
        host="192.168.0.50",
        port=5000
    )
    #flask_helpers.run_flask(flask_app)

###############################################################################
def main():

    args = anki_vector.util.parse_command_args()

    with anki_vector.Robot(args.serial, 
                           enable_face_detection=True, 
                           enable_custom_object_detection=True) as robot:

        # open camera, and release control
        robot.camera.init_camera_feed()
        robot.behavior.say_text("I restart my camera!")
        robot.conn.release_control()

        # Flask
        runFlask(robot)

###############################################################################
if __name__ == "__main__":
    main()

