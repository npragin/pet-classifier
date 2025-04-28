import zmq
import base64
import atexit


# Port to receive images from the web server
port = 98703


def cleanup_resources(zmq_context, zmq_socket):
    print("Cleaning up resources...")
    if zmq_socket:
        zmq_socket.close()
    if zmq_context:
        zmq_context.term()
    print("Cleanup complete. Exiting.")


def main():
    # Set up the ZeroMQ context and socket
    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.SUB)
    zmq_socket.connect(f"tcp://localhost:{port}")
    zmq_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    # Register the cleanup function with atexit
    atexit.register(cleanup_resources, zmq_context, zmq_socket)

    print("Listening for images. Press Ctrl+C to exit.")

    while True:
        try:
            # Receive and decode the image data
            encoded_image = zmq_socket.recv()
            image_data = base64.b64decode(encoded_image)

            # Save the received image
            with open("received_image.png", "wb") as image_file:
                image_file.write(image_data)

            print("Image received and saved as 'received_image.png'")

        except KeyboardInterrupt:
            print("\nReceived KeyboardInterrupt, shutting down gracefully...")
            break

        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()
