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

def test_class_lookup_0():
    # Request breed info by class ID 0
    print("=========== Testing class lookup for class 0 ===========")
    response = send_request({"class": 0})
    print("Response for class 0:", response)
    assert isinstance(response, dict), "Response should be a dictionary"
    assert response["species"] == "Cat", "Expected species 'Cat'"
    assert response["breed"] == "Abyssinian", "Expected breed 'Abyssinian'"
    assert response["description"] == "The Abyssinian is a medium-sized cat with a lean, muscular body and a short coat, known for being extremely active and playful.", "Expected description 'The Abyssinian is a medium-sized cat with a lean, muscular body and a short coat, known for being extremely active and playful.'"
    assert response["link"] == "https://en.wikipedia.org/wiki/Abyssinian", "Expected link 'https://en.wikipedia.org/wiki/Abyssinian'"
    print("✅ Class 0 lookup test passed.")

def test_class_lookup_22():
    # Request breed info by class ID 22
    print("=========== Testing class lookup for class 22 ===========")
    response = send_request({"class": 22})
    print("Response for class 22:", response)
    assert isinstance(response, dict), "Response should be a dictionary"
    assert response["species"] == "Dog", "Expected species 'Dog'"
    assert response["breed"] == "Newfoundland", "Expected breed 'Newfoundland'"
    assert response["description"] == "Massive and gentle, great swimmer.", "Expected description 'Massive and gentle, great swimmer.'"
    assert response["link"] == "https://en.wikipedia.org/wiki/Newfoundland_(dog)", "Expected link 'https://en.wikipedia.org/wiki/Newfoundland_(dog)'"
    print("✅ Class 22 lookup test passed.")

def test_breed_list():
    # Request breed list
    print("=========== Testing breed list retrieval ===========")
    response = send_request({"list": ""})
    print("Response for list:", response)
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "list" in response, "Missing 'list' key in response"
    assert isinstance(response["list"], list), "'list' should be a list"
    assert response["list"][0] == "Cat - Abyssinian", "First breed mismatch"
    assert len(response["list"]) == 37, "Expected 37 breeds"
    print("✅ Breed list test passed.")

def test_invalid_class_id():
    # Test invalid class ID
    print("=========== Testing invalid class ID: -1 ===========")
    response = send_request({"class": -1})
    print("Response for invalid class ID -1:", response)
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "error" in response, "Expected an error key in response"
    assert isinstance(response["error"], dict), "Error should be a dictionary"
    assert response["error"]["short"] == "Invalid ID", "Expected short error message"
    assert "suggestion" in response["error"], "Expected suggestion in error message"
    print("✅ Invalid class ID test passed.")

def test_class_id_out_of_range():
    # Test class ID above valid range
    print("=========== Testing class ID above valid range: 100 ===========")
    response = send_request({"class": 100})
    print("Response for out-of-range class ID 100:", response)
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "error" in response, "Expected an error key in response"
    assert response["error"]["short"] == "Invalid ID", "Expected short error message"
    assert "Valid class IDs" in response["error"]["suggestion"], "Expected helpful suggestion"
    print("✅ Out-of-range class ID test passed.")


if __name__ == "__main__":
    test_class_lookup_0()
    test_class_lookup_22()
    test_breed_list()
    test_invalid_class_id()
    test_class_id_out_of_range()
