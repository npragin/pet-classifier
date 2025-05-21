import zmq
import base64
import atexit
from torchvision import transforms
from PIL import Image
import io
import pickle

from config import ZMQ_PORT_INGESTOR, ZMQ_PORT_MODEL, ZMQ_HOSTNAME_MODEL, ZMQ_PORT_RESULTS, ZMQ_HOSTNAME_RESULTS


def cleanup_zmq(zmq_context, zmq_frontend_socket, zmq_model_socket, zmq_results_socket):
    print("Cleaning up resources...")
    if zmq_results_socket:
        zmq_results_socket.close()
    if zmq_model_socket:
        zmq_model_socket.close()
    if zmq_frontend_socket:
        zmq_frontend_socket.close()
    if zmq_context:
        zmq_context.term()
    print("Cleanup complete. Exiting.")


def setup_zmq():
    # Set up the ZeroMQ context
    zmq_context = zmq.Context()

    # Set up the frontend socket
    zmq_frontend_socket = zmq_context.socket(zmq.REP)
    zmq_frontend_socket.bind(f"tcp://*:{ZMQ_PORT_INGESTOR}")
    
    # Set up the model socket
    zmq_model_socket = zmq_context.socket(zmq.REQ)
    zmq_model_socket.connect(f"tcp://{ZMQ_HOSTNAME_MODEL}:{ZMQ_PORT_MODEL}")
    
    # Set up the results socket
    zmq_results_socket = zmq_context.socket(zmq.REQ)
    zmq_results_socket.connect(f"tcp://{ZMQ_HOSTNAME_RESULTS}:{ZMQ_PORT_RESULTS}")

    # Register the cleanup function with atexit
    atexit.register(cleanup_zmq, zmq_context, zmq_frontend_socket, zmq_model_socket, zmq_results_socket)

    return zmq_frontend_socket, zmq_model_socket, zmq_results_socket


def transform_image_for_model(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    transformed_image = transform(image)
    transformed_batched_image = transformed_image.unsqueeze(0)
    return transformed_batched_image


def main():
    zmq_frontend_socket, zmq_model_socket, zmq_results_socket = setup_zmq()

    print("Listening for images. Press Ctrl+C to exit.")

    while True:
        try:
            # Receive and decode the image data from the frontend
            encoded_image = zmq_frontend_socket.recv()
            image_data = base64.b64decode(encoded_image)

            image = Image.open(io.BytesIO(image_data))
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            transformed_image = transform_image_for_model(image)
            
            # Serialize the tensor and send it over ZMQ to the model service
            serialized_tensor = pickle.dumps(transformed_image)
            zmq_model_socket.send(serialized_tensor)
            print(f"Sent tensor with shape {transformed_image.shape} to model process")
            
            # Wait for the result from the model service
            serialized_result = zmq_model_socket.recv()
            result = pickle.loads(serialized_result)
            
            # Check if there was an error
            if "error" in result:
                print(f"Error from model service: {result['error']}")
                # Forward the error to the frontend
                zmq_frontend_socket.send(pickle.dumps(result))
            else:
                print(f"Received result: Class {result['class']}, Confidence {result['confidence']:.4f}")
                
                # Send the result to the results service
                results_data = {
                    "class": result['class'],
                    "confidence": result['confidence'],
                    "image": encoded_image
                }
                zmq_results_socket.send(pickle.dumps(results_data))
                
                # Wait for the UUID from the results service
                serialized_uuid = zmq_results_socket.recv()
                uuid_result = pickle.loads(serialized_uuid)
                
                if "error" in uuid_result:
                    print(f"Error from results service: {uuid_result['error']}")
                else:
                    print(f"Received UUID from results service: {uuid_result['uuid']}")
                    # Add the UUID to the result
                    result['uuid'] = uuid_result['uuid']
                
                # Forward the result to the frontend
                zmq_frontend_socket.send(pickle.dumps(result))
            
        except KeyboardInterrupt:
            print("\nReceived KeyboardInterrupt, shutting down gracefully...")
            break

        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()
