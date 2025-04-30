import zmq
import pickle
import uuid
import atexit
import sqlite3
import datetime
import os

from config.config import ZMQ_PORT_RESULTS_INGESTOR


# Limit OpenBLAS threads to avoid hitting process limits
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

# SQLite configuration
DB_PATH = "pet_classifier_results.db"


def cleanup_zmq(zmq_context, zmq_ingestor_socket):
    print("Cleaning up resources...")
    if zmq_ingestor_socket:
        zmq_ingestor_socket.close()
    if zmq_context:
        zmq_context.term()
    print("Cleanup complete. Exiting.")


def setup_zmq():
    print("Setting up ZeroMQ resources...")
    # Set up the ZeroMQ context
    zmq_context = zmq.Context()

    # Set up the socket to receive from the data ingestion service
    zmq_ingestor_socket = zmq_context.socket(zmq.REP)
    zmq_ingestor_socket.bind(f"tcp://*:{ZMQ_PORT_RESULTS_INGESTOR}")

    # Register the cleanup function with atexit
    atexit.register(cleanup_zmq, zmq_context, zmq_ingestor_socket)

    return zmq_ingestor_socket


def setup_database():
    print("Setting up SQLite database...")
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    # Register adapter for datetime objects
    sqlite3.register_adapter(datetime.datetime, lambda dt: dt.isoformat())
    sqlite3.register_converter(
        "datetime", lambda b: datetime.datetime.fromisoformat(b.decode())
    )

    # Create a cursor with datetime support
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS classification_results (
        uuid TEXT PRIMARY KEY,
        class INTEGER,
        confidence REAL,
        image TEXT,
        timestamp DATETIME
    )
    """
    )

    conn.commit()
    return conn

def insert_result(db_conn, req):
    print(
        f"Received request: class={req['class']}, confidence={req['confidence']}"
    )

    # Generate a UUID for this record
    record_uuid = str(uuid.uuid4())

    # Insert the data into SQLite
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO classification_results (uuid, class, confidence, image, timestamp) VALUES (?, ?, ?, ?, ?)",
        (
            record_uuid,
            int(req["class"]),
            float(req["confidence"]),
            req["image"],
            datetime.datetime.now(),
        ),
    )
    db_conn.commit()

    print(f"Stored record with UUID: {record_uuid}")

    return {"uuid": record_uuid}

def get_single_result(db_conn, req):
    # Get the UUID from the request
    request_uuid = req["uuid"]
    
    # Query the database for this UUID
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT class, confidence, image FROM classification_results WHERE uuid = ?",
        (request_uuid,)
    )
    result = cursor.fetchone()
    
    if result:
        return {
            "class": result[0],
            "confidence": result[1], 
            "image": result[2]
        }
    else:
        print(f"No record found for UUID: {request_uuid}")
        return {"error": f"No record found for UUID: {request_uuid}"}

def get_history(db_conn, req):
    # Get the length parameter from the request
    length = int(req["length"])
    
    # Query the database for most recent entries
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT class, confidence, image FROM classification_results ORDER BY timestamp DESC LIMIT ?",
        (length,)
    )
    results = cursor.fetchall()
    
    # Convert results to list of dictionaries
    return [
        {
            "class": result[0],
            "confidence": result[1],
            "image": result[2]
        }
        for result in results
    ]

def main():
    zmq_ingestor_socket = setup_zmq()
    db_conn = setup_database()

    print("Results service started. Waiting for messages...")

    while True:
        try:
            # Receive the message
            message = zmq_ingestor_socket.recv()
            req = pickle.loads(message)

            if "class" in req and "confidence" in req and "image" in req:
                response = insert_result(db_conn, req)
            elif "uuid" in req:
                response = get_single_result(db_conn, req)
            elif "length" in req:
                response = get_history(db_conn, req)
            else:
                print(f"Received invalid request: {req}")
                response = {"error": "Invalid request"}

            zmq_ingestor_socket.send(pickle.dumps(response))

        except KeyboardInterrupt:
            print("\nReceived KeyboardInterrupt, shutting down gracefully...")
            break

        except Exception as e:
            print(f"Error: {e}")
            # Send an error response back to the data ingestion service
            error_response = {"error": str(e)}
            zmq_ingestor_socket.send(pickle.dumps(error_response))

    # Close the database connection when done
    db_conn.close()


if __name__ == "__main__":
    main()
