"""Generate *_pb2.py modules from src/**.proto."""

import grpc_tools.command

if __name__ == "__main__":
    grpc_tools.command.build_package_protos("src")
