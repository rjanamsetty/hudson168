import os
import pickle
import re
import socket
import time

import cv2
import numpy as np

cameras = {1: ("127.0.0.1", 5000)}


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


def save_frame(host=None, port=None, target=float('inf')):
    """
    Saves an OpenCV image frame to a folder called 'images' every minute.
    :return: None
    """
    # Set the default values
    if host is None:
        host = ["127.0.0.1"]
    if port is None:
        port = [5000]
    count = 0
    folder_name = 'images'

    while True:
        # Get current time and create a filename
        timestamp = int(time.time())

        # Get the current frame
        for h, p in zip(host, port):
            frame = next(udp_receive_jpg(host=h, port=p, formatter=opencv_img))
            hostname = re.sub(r'\.', '-', h)
            filename = f"{folder_name}/{hostname}_{timestamp}.jpg"
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            print(f"Saved {filename}")

        # Increment the count and break if the target number of frames has been reached
        count += 1
        if count == target:
            break

        # Wait for 1 minute before saving the next frame
        time.sleep(60)


if __name__ == "__main__":
    # If images folder does not exist, create it
    if not os.path.exists('images'):
        os.makedirs('images')
    save_frame()
