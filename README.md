# BreedCheckerService Microservice

## ℹ️ Overview
BreedCheckerService is a ZeroMQ-based Python microservice that provides information about various cat and dog breeds. It listens on TCP port `5555` and responds to serialized requests using Python's `pickle` module.

---

## 📡 Communication Contract

This microservice accepts two types of requests:

### 1. Request breed details by class ID
```python
request = {"class": 0}
```

### 2. Request the full list of breeds

```python
request = {"list": ""}
```
All requests must be serialized using pickle and sent over a ZeroMQ REQ socket.

## ✅ How to Programmatically REQUEST Data

### Example: Request breed info for class ID 0
```python
import zmq
import pickle

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

request = {"class": 0}
socket.send(pickle.dumps(request))
```

### Example: Request breed list
```python
request = {"list": ""}
socket.send(pickle.dumps(request))
```

## ⬇️ How to Programmatically RECEIVE Data

### Example: Receive and decode the response
```python
response = pickle.loads(socket.recv())
print(response)
```

Expected output:
```python
{
  "species": "Cat",
  "breed": "Abyssinian",
  "description": "The Abyssinian is a medium-sized cat with a lean, muscular body and a short coat, known for being extremely active and playful.",
  "link": "https://en.wikipedia.org/wiki/Abyssinian"
}
```

## 📊 UML Sequence Diagram that shows how client and microservice interact
The diagram below illustrates the interaction between the client and the BreedCheckerService microservice

./UML_BreedChecker.png


## 🔨 Setup Instructions

### Prerequisites
- Python 3.x
- ZeroMQ (`pyzmq` library)
- `pickle` library (standard in Python)

### Installation
```python
pip install pyzmq
```

### Running Microservice
```python
python BreedCheckerService.py
```

### Writing Your Own CLient
You must write your own client code to interact with the microservice using the communication contract above. Do not rely on the test program provided.

### Notes
- The microservice and client are decoupled and communicate only via ZeroMQ sockets.
- All data is serialized using pickle. Ensure both sides use compatible Python versions.

    



