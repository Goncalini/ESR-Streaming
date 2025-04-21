# ESR-Streaming
Repositório para os trabalhos de ESR 24/25

## Prerequisites
- Python 3.8 or higher
- Core

## How to run
- Open Core (sudo core-gui)
- Open in core the topology file `tp2est.imn`
- Open BootServer Bash
- Run `su-core`
- cd to the directory where the code is located
- Repeat the last 3 steps for each node and client you wish to run
- Then run on the BootServer `python3 BootServer.py`
- Run on the nodes `python3 oNode.py <node_ip> <node_id> ` example: `python3 Node.py 10.0.22.2 n2`
- Run on the clients `export DISPLAY=:0.0 ` and then `python3 oClient.py <client_name> <client_ip> <filename>` example: `python3 oClient.py Jojo 10.0.35.20 videos/video_BrskEdu.mp4`

## Features
- Dynamic choice of the best route
- Dynamic choice of the best point of presence
- Multicast streaming
- Synchronization of the video
- Packet loss tolerance
- For more information you can read the report