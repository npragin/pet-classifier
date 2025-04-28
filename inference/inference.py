from onnx_helper import ONNXClassifierWrapper
import numpy as np
import zmq
import pickle
import atexit

from config import ZMQ_PORT_MODEL_INGESTOR


def cleanup_zmq(zmq_context, zmq_ingestor_socket):
    print("Cleaning up resources...")
    if zmq_ingestor_socket:
        zmq_ingestor_socket.close()
    if zmq_context:
        zmq_context.term()
    print("Cleanup complete. Exiting.")

def setup_zmq():
    # Set up the ZeroMQ context
    zmq_context = zmq.Context()
    
    # Set up the ingestor socket
    zmq_ingestor_socket = zmq_context.socket(zmq.REP)
    zmq_ingestor_socket.bind(f"tcp://*:{ZMQ_PORT_MODEL_INGESTOR}")
    
    # Register the cleanup function with atexit
    atexit.register(cleanup_zmq, zmq_context, zmq_ingestor_socket)
    
    return zmq_ingestor_socket

def softmax(x):
    # Subtract the maximum value for numerical stability
    exp_x = np.exp(x - np.max(x))
    return exp_x / np.sum(exp_x)

def main():
    # Load the model
    model = ONNXClassifierWrapper("breed_classifier.trt", num_classes=37, target_dtype=np.float16)
    
    # Set up ZMQ socket
    zmq_ingestor_socket = setup_zmq()
    
    print(f"Model service listening on port {ZMQ_PORT_MODEL_INGESTOR}. Press Ctrl+C to exit.")
    
    while True:
        try:
            # Receive the serialized tensor
            serialized_tensor = zmq_ingestor_socket.recv()
            tensor = pickle.loads(serialized_tensor)
            
            # Process the tensor through the model
            output = model.predict(tensor)
            
            # Get the predicted class and confidence
            predicted_class = np.argmax(output)
            confidence = np.max(softmax(output))
            
            # Create a response dictionary
            response = {
                "class": int(predicted_class),
                "confidence": confidence,
            }
            
            # Serialize and send the response back to the data ingestor
            serialized_response = pickle.dumps(response)
            zmq_ingestor_socket.send(serialized_response)
            
            print(f"Processed image. Class: {predicted_class}, Confidence: {confidence:.4f}")
            
        except KeyboardInterrupt:
            print("\nReceived KeyboardInterrupt, shutting down gracefully...")
            break
            
        except Exception as e:
            print(f"Error: {e}")
            # Send an error response
            error_response = {
                "error": str(e)
            }
            try:
                zmq_ingestor_socket.send(pickle.dumps(error_response))
            except:
                pass
            break

if __name__ == "__main__":
    main()