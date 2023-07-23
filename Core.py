import socket
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from libcamera import controls

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

pwm = GPIO.PWM(12, 100)
pwm.start(50)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.settimeout(15.0)
ip_address = "10.0.5.1"
server_address = (ip_address, 23456)
sock.bind(server_address)

sock.listen(1)

lens_position = 2
picam2 = Picamera2()

while True:
    connection, client_address = sock.accept()

    while True:
        try:
            recieved = connection.recv(1024).decode("utf-8")

            CMD = recieved.split('~', 9)
            # CMD[0]: A = capture image, B = set fan speed
            # CMD[1]: X resolution
            # CMD[2]: Y resolution
            # CMD[3]: autofocus flag
            # CMD[4]: manual focus ajustment
            # CMD[5]: manual focus increment
            # CMD[6]: digital zoom
            # CMD[7]: file format

            if(CMD[0] == 'A'):
                # print("recieved: ", recieved)
                picam2.still_configuration.main.size = (int(CMD[1]), int(CMD[2]))
                picam2.configure("still")

                picam2.options["quality"] = 95
                picam2.options["compress_level"] = 0

                picam2.start()

                if int(CMD[3]):
                    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
                    picam2.autofocus_cycle()
                    lens_position = picam2.capture_metadata()["LensPosition"]

                if int(CMD[4]) :
                    lens_position += 0.001*int(CMD[5])
    
                full_res = picam2.camera_properties['PixelArraySize']
                zoom_size = [int(r * (1 - int(CMD[6]) / 100)) for r in full_res]
                offset = [(r - s) // 2 for r, s in zip(full_res, zoom_size)]

                picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": lens_position})
                picam2.capture_metadata()
                picam2.set_controls({"ScalerCrop": offset + zoom_size})
                picam2.capture_metadata()
                if int(CMD[7]):
                    capture_file = "capture.jpg"
                else:
                    capture_file = "capture.png"
                
                picam2.capture_file(capture_file)

                if int(CMD[3]) or int(CMD[4]) or int(CMD[5]):
                    lens_position = picam2.capture_metadata()["LensPosition"]
                    response="A~"+ str(lens_position)
                    connection.send(response.encode("utf-8"))
                picam2.stop()

                with open(capture_file, "rb") as f:
                    data = f.read(512)
                    while data:
                        connection.send(data)
                        data = f.read(512)
                print("transmit complete")
                break

            if CMD[0] == 'B':
                pwm.ChangeDutyCycle(int(CMD[1]))
                break

        except Exception as e:
            print(e)

    connection.close()
