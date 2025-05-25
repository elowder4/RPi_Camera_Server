from flask import Flask, Response
from picamera2 import Picamera2
from picamera2 import Preview
import time
import cv2
import numpy as np

app = Flask(__name__)

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
        '''
        # Capture a frame from the camera
        frame = picam2.capture_array()

        # Convert the frame to JPEG format using OpenCV
        ret, jpeg_frame = cv2.imencode('.jpeg', frame)

        if not ret:
            continue  # Skip the frame if encoding failed

        # Convert the numpy array to bytes
        jpeg_frame_bytes = jpeg_frame.tobytes()

        # Yield the JPEG frame as part of the MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame_bytes + b'\r\n\r\n')'''
        
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
    return "Welcome to the Raspberry Pi Camera Stream! Visit /video_feed to watch the stream."

@app.route('/video_feed')
def video_feed():
    # Return the video stream using the generator function
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.1.96', port=5000, debug=False)
