# Instructions

Get the hostname of the HPC node you run `inference.py` on using `echo "CUDA_NODE_HOSTNAME=$(hostname)"` and update config.py accordingly

Be sure to run `pip install -e .` to install the config package

Be sure to load the CUDA module on the HPC node

## Note
Microservices, used to be separate repos combined into this monorepo using submodules, then switched to subtree for organization after project completion.
