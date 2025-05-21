# Ports for communication between services
ZMQ_PORT_INGESTOR = 98700
ZMQ_PORT_MODEL = 98701
ZMQ_PORT_RESULTS = 98702
ZMQ_PORT_BREED_INFO = 98703

# Hostnames for communication between services
# RELATIVE TO THE DATA INGESTOR
ZMQ_HOSTNAME_FRONTEND = "localhost"
ZMQ_HOSTNAME_MODEL = "cn-gpu4.hpc.engr.oregonstate.edu"
ZMQ_HOSTNAME_RESULTS = "localhost"

# RELATIVE TO THE WEB FRONTEND
ZMQ_HOSTNAME_INGESTOR = "localhost"
ZMQ_HOSTNAME_RESULTS_FRONTEND = "localhost"
ZMQ_HOSTNAME_BREED_INFO_FRONTEND = "localhost"