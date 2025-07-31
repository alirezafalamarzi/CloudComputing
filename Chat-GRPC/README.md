### Run Locally without docker:
- `pip install grpcio grpcio-tools`
- `python -m grpc_tools.protoc -I./ --python_out=. --pyi_out=. --grpc_python_out=. ./chat.proto`
- `python server.py`
- `python client.py`
