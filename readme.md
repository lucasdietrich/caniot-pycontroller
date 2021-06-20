# Remote Developpement of Python CAN Controller for Raspberry Pi 2

Commands :

Run python script interactively : `/usr/bin/python3 -i /home/pi/Controller/test.py`


# HTTP server

- aiohttp : https://docs.aiohttp.org/en/stable/
- flask : https://flask.palletsprojects.com/en/1.1.x/quickstart/

# gRPC

## Command 

```
python -m grpc_tools.protoc -Icancontroller/ipc --python_out=cancontroller/ipc --grpc_python_out=cancontroller/ipc model.proto
```
