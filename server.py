import time
import io
import picamera
from flask import Flask, render_template, Response

app = Flask(__name__)

# Initialize the Pi Camera
camera = picamera.PICamera()

def video_stream():
    # Create a memory buffer to store the image
    stream = io.BytesIO()

    while True:
        # Capture an image to the stream in JPEG format
        camera.capture(stream, format='jpeg')

        # Get the byte data from the buffer
        frame = stream.getvalue()

        # Reset the stream for the next frame
        stream.seek(0)
        stream.truncate()

        # Yield the image in multipart format
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
    # Start Flask app on 192.168.1.96:5000
    app.run(host='192.168.1.96', port=5000, debug=True)
