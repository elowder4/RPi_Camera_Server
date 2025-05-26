from flask import Flask, Response, render_template, jsonify, abort
from picamera2 import Picamera2
from picamera2 import Preview
import RPi.GPIO as gpio
from time import time
import threading 
import adafruit_dht
import board
import cv2


app = Flask(__name__)

# Init light
light_pin = 26
gpio.setmode(gpio.BCM)
gpio.setup(light_pin, gpio.OUT)

# Init DHT11
dhtDevice = adafruit_dht.DHT11(board.D17)

# Initialize Picamera2
picam2 = Picamera2()

# Configure the camera for video capture
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={"FrameDurationLimits": (33333, 33333)})
picam2.configure(config)

# Start the camera preview
picam2.start_preview(Preview.NULL)  # No physical preview needed

# Start the camera
picam2.start()

# FPS related variables
fps_times = []
window_size = 30  # Number of frames to average over
fps_capture = 0.0

        
@app.route('/')
def index():
    gpio.output(light_pin, gpio.HIGH) # Turn on light on access to server
    global toggled
    toggled = True
    
    return render_template('index.html')


@app.route('/toggle_light', methods=['POST'])
def toggle_light():
    light_state = gpio.input(light_pin)
    
    if light_state:
        gpio.output(light_pin, gpio.LOW) # Turn off
    else:
        gpio.output(light_pin, gpio.HIGH) # Turn on 
    
    return ('', 204)  # No content, minimal response


@app.route('/get_DHT11')
def get_DHT11():
    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32

        humidity = dhtDevice.humidity
        
        return jsonify([round(temperature_f, 2), round(humidity, 2)])
    
    except RuntimeError:
        temperature_f = 0
        humidity = 0
        
        
    return jsonify([round(temperature_f, 2), round(humidity, 2)])
        

@app.route('/get_fps')
def get_fps():
    return jsonify(round(fps_capture, 1))


@app.route('/frame.jpg')
def frame():
    global fps_capture
    global end_time
    start_time = time()
    request = picam2.capture_request()
    frame = request.make_array("main")
    request.release()

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
    ret, jpeg = cv2.imencode('.jpg', frame, encode_param)
    
    if not ret:
        abort(500)
        
    end_time = time()
    frame_time = end_time - start_time

    fps_times.append(frame_time)
    
    if len(fps_times) > window_size:
        fps_times.pop(0)

    if len(fps_times) > 1:
        avg_time = sum(fps_times) / len(fps_times)
        fps_capture = 1.0 / avg_time
        
    return Response(jpeg.tobytes(), mimetype='image/jpeg')


'''
if __name__ == '__main__':
    app.run(host='192.168.1.96', port=5000, debug=False) # For development only 
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # WSGI server
