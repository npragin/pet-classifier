import zmq
import base64
import signal


# Port to receive images from the web server
port = 6620

# Flag to control the main loop
running = True


def signal_handler(sig, _):
    global running
    signal_name = signal.Signals(sig).name
    print(f"\nReceived {signal_name}, shutting down gracefully...")
    running = False


def main():
    # Set up the ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    # Set up signal handlers for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Listening for images. Press Ctrl+C to exit.")

    while running:
        try:
            # Set a timeout on the socket to allow checking the running flag
            socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout

            # Receive and decode the image data
            encoded_image = socket.recv()
            image_data = base64.b64decode(encoded_image)

            # Save the received image
            with open("received_image.png", "wb") as image_file:
                image_file.write(image_data)

            print("Image received and saved as 'received_image.png'")

        except zmq.Again:
            # Timeout occurred, just continue the loop
            continue

        except Exception as e:
            print(f"Error: {e}")
            break

    # Clean up
    print("Cleaning up resources...")
    socket.close()
    context.term()
    print("Cleanup complete. Exiting.")


if __name__ == "__main__":
    main()
