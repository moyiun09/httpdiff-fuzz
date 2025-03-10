import socket
import threading
import re
import sys
import base64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 8080))
s.listen()


def handle_connection(conn):
    data = b''
    try:
        conn.settimeout(3)
        while True:
            try:
                conn_data = conn.recv(2048)
                if not conn_data:
                    break
                else:
                    data += conn_data
            except socket.timeout:
                break

       
       
        req = base64.b64encode(conn_data)
        response_body = b"This is a test message!!!"
    
        response_headers = b"HTTP/1.1 200 OK\r\nConnection: close\r\nserver-name: someserver\r\nX-Req-Byte: "+req+"Content-Length: " + str(len(response_body)).encode() + b"\r\n\r\n"
        conn.sendall(response_headers + response_body)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    except Exception as exception:
        print(data)
        print("exception: {}".format(exception))

while True:
    try:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_connection, args=(conn,))
        thread.start()
    except Exception as exception:
        print("exception: {}".format(exception))
    
s.close()