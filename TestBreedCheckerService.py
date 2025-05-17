import zmq
import pickle

def send_request(request_data):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")  # Adjust if needed
    socket.send(pickle.dumps(request_data))
    response = pickle.loads(socket.recv())
    socket.close()
    return response

def test_class_lookup():
    print("Testing class lookup for class 0...")
    response = send_request({"class": 0})
    assert isinstance(response, dict), "Response should be a dictionary"
    assert response["species"] == "Cat", "Expected species 'Cat'"
    assert response["breed"] == "Abyssinian", "Expected breed 'Abyssinian'"
    assert "description" in response, "Missing description"
    assert "link" in response, "Missing link"
    print("✅ Class lookup test passed.")

def test_breed_list():
    print("Testing breed list retrieval...")
    response = send_request({"list": ""})
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "list" in response, "Missing 'list' key in response"
    assert isinstance(response["list"], list), "'list' should be a list"
    assert response["list"][0] == "Cat - Abyssinian", "First breed mismatch"
    assert len(response["list"]) == 37, "Expected 37 breeds"
    print("✅ Breed list test passed.")

def test_invalid_class_id():
    print("Testing invalid class ID handling...")
    response = send_request({"class": -1})
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "error" in response, "Expected an error key in response"
    assert isinstance(response["error"], dict), "Error should be a dictionary"
    assert response["error"]["short"] == "Invalid ID", "Expected short error message"
    assert "suggestion" in response["error"], "Expected suggestion in error message"
    print("✅ Invalid class ID test passed.")

def test_class_id_out_of_range():
    print("Testing class ID above valid range...")
    response = send_request({"class": 100})
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "error" in response, "Expected an error key in response"
    assert response["error"]["short"] == "Invalid ID", "Expected short error message"
    assert "Valid class IDs" in response["error"]["suggestion"], "Expected helpful suggestion"
    print("✅ Out-of-range class ID test passed.")


if __name__ == "__main__":
    test_class_lookup()
    test_breed_list()
    test_invalid_class_id()
    test_class_id_out_of_range()
