import socket
import sys

HOST = 'hal'
PORT = 6600
for remote_socket in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = remote_socket
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except OSError as msg:
        s.close
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)
with s:
    data = s.recv(1024)
    print('Received:', data)
    command = sys.argv[1] + "\n"
    print('sending:', command)
    s.send(command.encode())
    while True:
        data = s.recv(1024)

        print(data.decode())
