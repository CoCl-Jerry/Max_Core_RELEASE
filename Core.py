import socket
from time import sleep
from picamera import PiCamera

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = "10.0.5.1"
server_address = (ip_address, 23456)
sock.bind(server_address)

sock.listen(1)

while True:
    connection, client_address = sock.accept()

    while True:
        try:
            recieved = connection.recv(1024).decode("utf-8")
            print(recieved)

            CMD = recieved.split('~', 9)

            if(CMD[0] == 'A'):
                with PiCamera() as camera:
                    camera.resolution = (int(CMD[1]), int(CMD[2]))
                    camera._set_rotation(90 * int(CMD[3]))
                    camera.zoom = (
                        int(CMD[4]) / 100, int(CMD[5]) / 100, int(CMD[6]) / 100, int(CMD[7]) / 100)
                    sleep(2)
                    if(int(CMD[8]) == 1):
                        camera.capture("out.jpg")
                    else:
                        camera.capture("out.png")

                if(int(CMD[8]) == 1):
                    f = open("out.jpg", "rb")
                else:
                    f = open("out.png", "rb")
                l = f.read(512)
                i=0
                while (l):
                    connection.send(l)
                    l = f.read(512)
                    i++
                    print(i+"\n")
                f.close()
                break
        except Exception as e:
            print(e)

    connection.close()
