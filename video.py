import os
import pickle
import re
import socket
import time

import cv2
import numpy as np

from lib import utils

cameras = {1: 5001,
           2: 5002}
folder_name = 'images'


def udp_receive_jpg(host="127.0.0.1", port=5000, formatter=lambda x: x):
    """
    Receives UDP packets containing a frame of a video stream and displays the frame
    :param formatter:
    :param host: the host IP address
    :param port: the port number
    :return: the frame of the video stream added to the socket queue
    """
    # Create a UDP socket and bind it to the host and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    max_length = 65540

    # Print a message indicating that the server is waiting for a connection
    buffer = None

    # Continuously receive UDP packets and display the decoded image
    while True:

        # Receive a UDP packet
        data, address = sock.recvfrom(max_length)

        # If the packet is less than 100 bytes, it contains the frame info
        if len(data) < 100:

            # If the frame info is valid, receive the rest of the packets
            try:
                frame_info = pickle.loads(data)
                if frame_info:
                    nums_of_packs = frame_info["packs"]
                    for i in range(nums_of_packs):
                        data, address = sock.recvfrom(max_length)
                        if i == 0:
                            buffer = data
                        else:
                            buffer += data

                    yield formatter(buffer)
            except:
                print("can't unpickle")


def html_img(buffer):
    """
    Formats the frame of the video stream as HTML
    :param buffer: the raw frame of the video stream
    :return: the formatted frame of the video stream formatted as HTML
    """
    return b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer + b'\r\n'


def opencv_img(buffer):
    """
    Formats the frame of the video stream as an openCV image
    :param buffer: the raw frame of the video stream
    :return: the formatted frame of the video stream formatted as an openCV image
    """
    # Convert the buffer to a NumPy array and reshape it
    frame = np.frombuffer(buffer, dtype=np.uint8)
    frame = frame.reshape(frame.shape[0], 1)

    # Decode the image and flip it horizontally
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    return cv2.flip(frame, 1)


def save_frame_udp(host="127.0.0.1", port=5000):
    """
    Saves an OpenCV image frame to a folder called 'images' every minute.
    :return: None
    """

    # Get and save current frame
    frame = next(udp_receive_jpg(host=host, port=port, formatter=opencv_img))
    hostname = re.sub(r'\.', '-', host)
    __save_frame(frame, "{hostname}_{time}".format(hostname=hostname, time=utils.est_time_now()))


def save_frame_local():
    """
    Saves an image from the webcam
    :return: None
    """
    # initialize video capture object
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret: return
    __save_frame(frame, utils.est_time_now())


def __save_frame(frame, filename):
    """
    Saves a given frame with the given file name
    :param frame: frame to save
    :param filename: the filename to save as
    :return: None
    """
    name = "{folder_name}/{filename}.jpg".format(folder_name=folder_name, filename=filename)
    if cv2.imwrite(name, frame, [cv2.IMWRITE_JPEG_QUALITY, 90]):
        print("Saved {filename}".format(filename=filename))
    else:
        print("error saving {filename}".format(filename=filename))


if __name__ == "__main__":
    # If images folder does not exist, create it
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Take an image every minute
    while True:
        save_frame_local()
        time.sleep(60)
