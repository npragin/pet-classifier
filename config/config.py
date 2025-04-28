# Ports for communication between services
ZMQ_PORT_FRONTEND_INGESTOR = 98700
ZMQ_PORT_MODEL_INGESTOR = 98701

# IPs for communication between services
# NOTE: Only use localhost if the service is on the same machine as the data ingestor
ZMQ_HOSTNAME_FRONTEND = "localhost"
ZMQ_HOSTNAME_MODEL = "cn-gpu3.hpc.engr.oregonstate.edu"