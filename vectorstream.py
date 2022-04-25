#!/usr/bin/env python3

import io
import sys
import anki_vector

###############################################################################
try:
   from flask import Flask, Response
except ImportError:
   sys.exit("Cannot import from flask: Do `pip3 install --user flask` to install")

flask_app = Flask(__name__)

###############################################################################
# runs a endless loop
def run_loop():

   while True:
      # Video streaming generator function
      if flask_app.vectorstream:
         image_raw = flask_app.vectorstream.vector.camera.latest_image
         image = image_raw.annotate_image()
         img_io = io.BytesIO()
         image.save(img_io, 'JPEG')
         img_io.seek(0)

         yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img_io.getvalue() + b'\r\n')        
      else:
         pass

###############################################################################
# creates website 127.0.0.1:5000
@flask_app.route("/")
def handle_index_page():
   return """
   <html>
      <body>
         <img src="video" id="vectorVideoId" width=100%>
      </body>
   </html>
   """

###############################################################################
@flask_app.route("/video")
def video_feed():
   return Response(run_loop(), mimetype='multipart/x-mixed-replace; boundary=frame')

###############################################################################
class vector_stream:
   def __init__(self, robot):
      self.vector = robot


###############################################################################
def run_flask(robot):
   flask_app.vectorstream = vector_stream(robot)
   flask_app.run(
      host="192.168.0.50",
      port=5000
   )

###############################################################################
def main():

   args = anki_vector.util.parse_command_args()

   with anki_vector.Robot(args.serial, 
                          enable_face_detection=True, 
                          cache_animation_lists=False,
                          enable_custom_object_detection=True) as robot:

      # open camera and release control
      robot.camera.init_camera_feed()
      #robot.behavior.say_text("I'm restart my camera!")
      robot.audio.stream_wav_file('/home/ubuntu/Apps/Vectorstream/vector_bell_whistle.wav')
      robot.conn.release_control()

      # Flask
      run_flask(robot)
     
###############################################################################
if __name__ == "__main__":
   main()

