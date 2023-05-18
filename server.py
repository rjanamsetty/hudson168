from flask import Flask, Response, render_template

from video import udp_receive_jpg, html_img, save_frame_udp, cameras

app = Flask(__name__)
host = "192.168.1.2"


@app.route("/video/<int:camera_id>")
def video(camera_id):
    """
    Returns the video frame periodically as defined in the gen_frame() function
    :param camera_id: An integer representing the ID of the camera
    :return: The current camera frame being processed as a response
    """
    if camera_id not in cameras:
        return "Invalid camera ID", 400
    port = cameras[camera_id]
    return Response(udp_receive_jpg(host=host, port=port, formatter=html_img),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/view/<int:camera_id>")
def view(camera_id):
    """
    Renders the camera frame view in HTML. You may need to refresh it once streaming to get live updates after a
    period of inactivity or on initialization
    :param camera_id: An integer representing the ID of the camera
    :return: A webpage showing the live camera feed
    """
    if camera_id not in cameras:
        return "Invalid camera ID", 400
    link = "http://{host}:8080/video/{camera_id}".format(host=host, camera_id=camera_id)
    return render_template('view.html', camera_id=camera_id, link=link)


@app.route("/save/<int:camera_id>")
def save(camera_id):
    if camera_id not in cameras:
        return "Invalid camera ID", 400
    port = cameras[camera_id]
    save_frame_udp(host=[host], port=[port])
    return "Saved"


@app.route("/")
def home():
    return render_template('home.html', cameras=cameras)


if __name__ == "__main__":
    # run install.py to install dependencies and create the database
    app.run(host=host, port=8080, debug=True)
