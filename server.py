from flask import Flask, Response, render_template
from picamera2 import Picamera2
from picamera2 import Preview
import RPi.GPIO as gpio
import time
import cv2
import numpy as np

app = Flask(__name__)

# Init GPIO
gpio.setmode(gpio.BCM)
gpio.setup(26, gpio.OUT)

# Initialize Picamera2
picam2 = Picamera2()

# Configure the camera for video capture
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={"FrameDurationLimits": (33333, 33333)})
picam2.configure(config)

# Start the camera preview
picam2.start_preview(Preview.NULL)  # No physical preview needed

# Start the camera (you must start it before capturing frames)
picam2.start()

# Function to capture video frame by frame and generate the MJPEG stream
def generate_video():
    while True:     
        request = picam2.capture_request()
        frame = request.make_array("main")  # fastest way to get image
        request.release()

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]  # Lower quality = faster
        ret, jpeg_frame = cv2.imencode('.jpg', frame, encode_param)
        
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Turn on Light if needed 
    gpio.output(26, gpio.HIGH)
    # Return the video stream using the generator function
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.1.96', port=5000, debug=False)
