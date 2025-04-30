from flask import Flask, render_template, request, redirect, url_for, flash
import os
import zmq
import base64
import atexit
import pickle

from config import ZMQ_PORT_FRONTEND_INGESTOR, ZMQ_HOSTNAME_INGESTOR, ZMQ_PORT_RESULTS_INGESTOR, ZMQ_HOSTNAME_RESULTS_FRONTEND


def create_app():
    app = Flask(__name__)
    app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}
    app.config["SECRET_KEY"] = "supersecretkey"

    # Only initialize ZeroMQ in the main process, not in the reloader
    if os.environ.get("WERKZEUG_RUN_MAIN"):
        zmq_ingestor_socket, zmq_results_socket = setup_zmq()

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/history")
    def history():
        return render_template("history.html")

    @app.route("/data-profile")
    def data_profile():
        return render_template("data_profile.html")

    @app.route("/<uuid>")
    def get_result(uuid):
        try:
            # Send request to results service
            request_data = {"uuid": uuid}
            zmq_results_socket.send(pickle.dumps(request_data))
            
            # Wait for response
            response_data = zmq_results_socket.recv()
            response = pickle.loads(response_data)
            
            if "error" in response:
                flash(f"Error retrieving result: {response['error']}", "error")
                return redirect(url_for("home"))

            # Render the template with the classification results
            return render_template(
                "result.html",
                classification=response["class"],
                confidence=response["confidence"],
                image=response["image"].decode('utf-8')  # Decode the base64 image
            )
            
        except Exception as e:
            print(f"Error retrieving result: {e}")
            flash("Error retrieving result. Please try again later.", "error")
            return redirect(url_for("home"))

    @app.route("/upload", methods=["POST"])
    def upload_file():
        # Validate the request
        success, message = is_valid_request(request)
        if not success:
            flash(message, "error")
            return redirect(url_for("home"))

        # Send the image and wait for response
        file = request.files["file"]
        upload_uuid = send_image_and_get_response(file.read(), zmq_ingestor_socket)

        if upload_uuid:
            return redirect(url_for("get_result", uuid=upload_uuid))
        else:
            flash("Error processing image. Please refresh the page and try again.", "error")

        return redirect(url_for("home"))

    return app


def is_valid_request(request):
    if "file" not in request.files:
        return (
            False,
            "There was an error uploading your file. Please refresh the page and try again.",
        )

    file = request.files["file"]

    if not file or file.filename == "":
        return False, "Please select a file to upload before submitting."

    if not allowed_file(file.filename):
        return False, "File type not allowed. Please upload a PNG, JPG, or JPEG file."

    return True, None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
    }


def setup_zmq():
    """Initialize ZeroMQ resources"""
    print("Setting up ZeroMQ resources...")
    zmq_context = zmq.Context()

    zmq_ingestor_socket = zmq_context.socket(zmq.REQ)
    zmq_ingestor_socket.connect(f"tcp://{ZMQ_HOSTNAME_INGESTOR}:{ZMQ_PORT_FRONTEND_INGESTOR}")

    zmq_results_socket = zmq_context.socket(zmq.REQ)
    zmq_results_socket.connect(f"tcp://{ZMQ_HOSTNAME_RESULTS_FRONTEND}:{ZMQ_PORT_RESULTS_INGESTOR}")

    atexit.register(cleanup_zmq, zmq_context, zmq_ingestor_socket, zmq_results_socket)

    return zmq_ingestor_socket, zmq_results_socket


def cleanup_zmq(zmq_context, zmq_ingestor_socket, zmq_results_socket):
    """Clean up ZeroMQ resources"""
    try:
        if zmq_ingestor_socket:
            zmq_ingestor_socket.close()
        if zmq_results_socket:
            zmq_results_socket.close()
        if zmq_context:
            zmq_context.term()
        print("ZeroMQ resources cleaned up successfully")
    except Exception as e:
        print(f"Error cleaning up ZeroMQ resources: {e}")


def send_image_and_get_response(image, zmq_socket):
    """Encode and send an image over ZeroMQ, then wait for and return the response UUID or error"""
    encoded_image = base64.b64encode(image)
    try:
        # Send the image as a request
        zmq_socket.send(encoded_image)
        
        # Wait for the response with the UUID
        response_data = zmq_socket.recv()
        response = pickle.loads(response_data)
        
        # Check if there was an error
        if "error" in response:
            print(f"Error from ingestor: {response['error']}")
            return None
        
        # Return the UUID from the response
        return response.get('uuid')
    except Exception as e:
        print(f"Error in image processing: {e}")
        return None


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
