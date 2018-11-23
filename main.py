import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading
from driveupload import driveupload

email_update_interval = 100 # sends an email only once in this time interval
video_camera = VideoCamera(flip=False) # creates a camera object, flip vertically
fb_classifier = cv2.CascadeClassifier("models/fullbody_recognition_model.xml")
ub_classifier = cv2.CascadeClassifier("models/upperbody_recognition_model.xml")
face_classifier = cv2.CascadeClassifier("models/facial_recognition_model.xml") # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
last_epoch = 0

def check_for_objects():
    global last_epoch
    while True:
        try:
            frame, found_obj = video_camera.get_object(face_classifier,ub_classifier,fb_classifier)         
            if found_obj and (time.time() - last_epoch) > email_update_interval:
                t0 = time.time()
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('output.avi',fourcc, 20.0, (1280,720))
                while True:
                    imgs = video_camera.get_frame_for_video()
                    out.write(imgs)
                    t1 = time.time() # current time
                    num_seconds = t1 - t0 # diff
                    if num_seconds > 10:
                        driveupload.upload_to_drive()
                        break
                del out
                last_epoch = time.time()
                print("Sending email...")
                sendEmail(frame)
                print("done!")
        except:
            print("Error sending email: ", sys.exc_info()[0])

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False)
