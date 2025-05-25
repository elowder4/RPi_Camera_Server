from flask import Flask, Response, render_template, jsonify
from picamera2 import Picamera2
from picamera2 import Preview
import RPi.GPIO as gpio
from time import time
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
fps_times = []
WINDOW_SIZE = 30  # number of frames to average over
fps_capture = 0.0

def generate_video():
    global fps_capture
    
    while True:
        start_time = time()

        request = picam2.capture_request()
        frame = request.make_array("main")
        request.release()

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        ret, jpeg_frame = cv2.imencode('.jpg', frame, encode_param)

        if not ret:
            continue

        end_time = time()
        frame_time = end_time - start_time

        fps_times.append(frame_time)
        if len(fps_times) > WINDOW_SIZE:
            fps_times.pop(0)

        if len(fps_times) > 1:
            avg_time = sum(fps_times) / len(fps_times)
            fps_capture = 1.0 / avg_time

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame.tobytes() + b'\r\n\r\n')
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_fps')
def get_fps():
    return jsonify(round(fps_capture, 2))

@app.route('/video_feed')
def video_feed():
    # Turn on Light if needed 
    gpio.output(26, gpio.HIGH)
    # Return the video stream using the generator function
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.1.96', port=5000, debug=False)
