# comnetsemu-router
Steps:
1. Copy the entire `_additions` folder in the main folder of comnetsemu

Inside comnetsemu-VM:

2. Launch `_additions/docker/buildall.sh` to build the required docker images
3. Run `_additions/basicRouterTopo06.py` to load an example where Xterms will show up for each node
4. Once loaded, on each Xterm that represents a router, run `home/main.py`
