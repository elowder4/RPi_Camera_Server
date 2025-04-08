from flask import Flask, Response
from picamera2 import Picamera2
import time

app = Flask(__name__)

# Initialize Picamera2
picam2 = Picamera2()

# Configure the camera for video capture
config = picam2.create_video_configuration()
picam2.configure(config)

# Start the camera preview (preview is required to initialize the camera)
picam2.start_preview()

# Function to capture video frame by frame
def generate_video():
    while True:
        # Capture the current frame from the camera
        frame = picam2.capture_array()

        # Convert the frame to JPEG format for streaming
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue  # Skip the frame if it couldn't be encoded

        # Yield the frame as a part of the MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    return "Welcome to the Raspberry Pi Camera Stream! Visit /video_feed to watch the stream."

@app.route('/video_feed')
def video_feed():
    # Return the video stream using the generator function
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
