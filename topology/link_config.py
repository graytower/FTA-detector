import socket
import sys
import os
import time

import link_status_pb2

def ConfigLink(node_1, node_2, status):

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("../topology/link_status_socket")
    cmd = link_status_pb2.LinkStatus()
    cmd.node_1 = node_1
    cmd.node_2 = node_2
    cmd.status = status
    message = cmd.SerializeToString()
    sock.sendall(message)
    print("Config link %s--%s--%s" % (node_1, node_2, status))
    sock.close()


if __name__ == "__main__":
    ConfigLink(sys.argv[1], sys.argv[2], sys.argv[3])
