import math
import pickle
import socket

import cv2

if __name__ == "__main__":
    # set maximum length of UDP packet and specify host and port
    max_length = 8192
    host = "127.0.0.1"
    port = 5000

    # create a UDP socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Socket created on {host}:{port}")

    # initialize video capture object
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    # loop until unable to read more frames
    while ret:
        # compress the frame using JPEG
        retval, buffer = cv2.imencode(".jpg", frame)

        # check if compression was successful
        if retval:
            # convert the compressed frame to a byte array
            buffer = buffer.tobytes()

            # determine the size of the compressed frame
            buffer_size = len(buffer)

            # calculate the number of packets required to send the frame
            num_of_packs = 1
            if buffer_size > max_length:
                num_of_packs = math.ceil(buffer_size / max_length)
            frame_info = {"packs": num_of_packs}
            sock.sendto(pickle.dumps(frame_info), (host, port))
            print("Number of packets:", num_of_packs)

            # split the compressed frame into smaller packets and send each packet to the specified host and port
            left = 0
            right = max_length
            for i in range(num_of_packs):
                # truncate the compressed frame to the appropriate packet size
                data = buffer[left:right]

                # update the indices for the next packet
                left = right
                right += max_length

                # send the packet to the specified host and port
                sock.sendto(data, (host, port))

        # read the next frame from the camera
        ret, frame = cap.read()

    # once all frames have been sent, print "done"
    print("done")
