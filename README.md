# BreedChecker Microservice Communication Contract

## Overview
The **BreedChecker** microservice provides cat and dog breed information using a ZeroMQ-based request-response pattern. It supports two types of client requests:

- Retrieve detailed breed info by `class` ID.
- Retrieve a full list of all supported breeds.

---

## How to REQUEST Data Programmatically

Clients must connect to the service at `tcp://localhost:5555` using ZeroMQ and send `pickle`-serialized Python dictionaries.

### Request Breed Details by Class ID
```python
request = {"class": 0}  # Valid class IDs: 0 to 36

