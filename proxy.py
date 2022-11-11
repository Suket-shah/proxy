import socket
import sys
import threading

HOST = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
BUFFER_SIZE = 4096
URL_OFFSET = 3


def start_socket(port, image_flag, attack_flag):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('', port))
            sock.listen(10)
            print(f"listening on {port}")
        except Exception:
            print("Unable to initialize socket")
            print(Exception)
            sys.exit(2)
        while True:
            try:
                conn, addr = sock.accept()
                print(f"connected with {addr}")
                client_host, client_port = addr
                if attack_flag:
                    conn.recv(1000) # should receive request from client. (GET ....)
                    conn.send(b'HTTP/1.0 200 OK\n')
                    conn.send(b'Content-Type: text/html\n')
                    conn.send(b'\n') # header and body should be separated by additional newline
                    conn.send(b"""
                        <html>
                        <body>
                        <h1>You are being attacked</h1> 
                        </body>
                        </html>
                    """) # Use triple-quote string.
                    conn.close()
                else: 
                    data = conn.recv(BUFFER_SIZE)
                    thread = threading.Thread(target=proxy_connect, args=(conn, data, addr))
                    thread.start()
            except KeyboardInterrupt:
                sock.close()
                print("Closing socket")
                sys.exit(1)

def proxy_connect(conn, data, addr):
    if data.find(b"GET") == -1:
        print("invalid request")
        return
    decoded_data = data.decode(FORMAT)
    url = decoded_data.split('\n')[0].split(' ')[1]
    http_pos = url.find('://')
    if http_pos != -1:
        url = url[(URL_OFFSET+http_pos):]
    server = ""
    port = -1
    port_pos = url.find(':')
    server_pos = url.find('/')
    if server_pos == -1:
        server = len(url)
    server = url[:port_pos]
    pre_port = url[(port_pos+1):]
    port = int(pre_port[:server_pos-port_pos-1])
    print('req_server', server)
    print('req_port', port)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as second_sock:
            second_sock.connect((server, port))
            second_sock.sendall(data.encode(FORMAT)) # should this be encoded in utf-8?
            while True:
                sock_reply = second_sock.recv(BUFFER_SIZE)
                if len(sock_reply) > 0:
                    conn.send(sock_reply)
                else:
                    break
        conn.close()
            
    except socket.error:
        second_sock.close()
        conn.close()
        print(second_sock.error)
        sys.exit(1)



if __name__ == '__main__':
    # TODO: check if argv is the correct way to handle input on Piazza
    arguments = sys.argv[1:]
    port = 5050
    image_flg = 0
    attack_flg = 0
    if len(arguments) > 0:
        port = int(arguments[0])
    if len(arguments) > 1:
        image_flg = int(arguments[1])
    if len(arguments) > 2:
        attack_flg = int(arguments[2])
    print(f"Image flag is {image_flg}")
    print(f"Attack flag is {attack_flg}")
    start_socket(port, image_flg, attack_flg)

    