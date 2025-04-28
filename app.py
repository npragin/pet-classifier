from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import zmq
import base64

# Port to send images to the data ingestion service
port = 6620

app = Flask(__name__)
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

# Ensure the necessary directories exist for static assets
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/css", exist_ok=True)

# Set up ZeroMQ context and publisher socket
context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.bind(f"tcp://*:{port}")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/data-profile")
def data_profile():
    return render_template("data_profile.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash(
            "There was an error uploading your file. Please refresh the page and try again.",
            "error",
        )
        return

    file = request.files["file"]

    if file.filename == "":
        flash("Please select a file to upload before submitting.", "error")
        return

    if file and allowed_file(file.filename):
        # Read the file data
        file_data = file.read()

        # Encode the image data as base64
        encoded_image = base64.b64encode(file_data)

        # Send the encoded image over ZeroMQ
        publisher.send(encoded_image)

        print(f"Image '{file.filename}' sent to processing service")

        # Redirect back to the home page
        return redirect(url_for("home"))

    # If we get here, the file type is not allowed
    flash("File type not allowed. Please upload a PNG, JPG, or JPEG file.", "error")
    return


if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        # Clean up ZeroMQ resources when the application exits
        publisher.close()
        context.term()
