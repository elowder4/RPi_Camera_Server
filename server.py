import time
import io
from picamera2 import Picamera2
from flask import Flask, render_template, Response

app = Flask(__name__)

# Initialize the Picamera2 camera object
picam2 = Picamera2()

# Configure the camera (you can customize settings as needed)
picam2.configure(picam2.create_still_configuration())

# Start the camera
picam2.start()

def video_stream():
    # Create a memory buffer to store the image
    while True:
        # Capture a still image (a frame) from the camera
        frame = picam2.capture_array()

        # Convert the frame to a JPEG format
        _, buffer = cv2.imencode('.jpeg', frame)
        frame = buffer.tobytes()

        # Yield the frame in multipart format
        yield (b'--frame\r\n' 
               b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/siteTest')
def siteTest():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.1.96', port=5000, debug=True)
