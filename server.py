from picamera2 import Picamera2
from flask import Flask, render_template, Response

app = Flask(__name__)

# Initialize picamera2
picam2 = Picamera2()

# Configure the camera (using the default preview configuration)
picam2.configure(picam2.create_preview_configuration())

# Start the camera (start capturing frames)
picam2.start()

def video_stream():
    while True:
        # Capture a frame from picamera2
        frame = picam2.capture_array()

        # Convert the captured frame to JPEG (picamera2 supports this natively)
        frame = picam2.encode_frame(frame, "jpeg")

        # Yield the frame in the correct multipart format for MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/siteTest')
def siteTest():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
