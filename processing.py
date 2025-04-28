import zmq
import base64
import atexit


# Port to receive images from the web server
port = 6620


def cleanup_resources(context, socket):
    print("Cleaning up resources...")
    if socket:
        socket.close()
    if context:
        context.term()
    print("Cleanup complete. Exiting.")


def main():
    # Set up the ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    # Register the cleanup function with atexit
    atexit.register(cleanup_resources, context, socket)

    print("Listening for images. Press Ctrl+C to exit.")

    while True:
        try:
            # Receive and decode the image data
            encoded_image = socket.recv()
            image_data = base64.b64decode(encoded_image)

            # Save the received image
            with open("received_image.png", "wb") as image_file:
                image_file.write(image_data)

            print("Image received and saved as 'received_image.png'")

        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()
