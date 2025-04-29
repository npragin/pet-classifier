# Ports for communication between services
ZMQ_PORT_FRONTEND_INGESTOR = 98700
ZMQ_PORT_MODEL_INGESTOR = 98701
ZMQ_PORT_RESULTS_INGESTOR = 98702

# Hostnames for communication between services
# RELATIVE TO THE DATA INGESTOR
ZMQ_HOSTNAME_FRONTEND = "localhost"
ZMQ_HOSTNAME_MODEL = "cn-gpu3.hpc.engr.oregonstate.edu"
ZMQ_HOSTNAME_RESULTS = "localhost"

# RELATIVE TO THE WEB FRONTEND
ZMQ_HOSTNAME_INGESTOR = "localhost"