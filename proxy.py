import socket
import sys
import threading

HOST = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
BUFFER_SIZE = 8192
URL_OFFSET = 3
CHANGE_URL = 'http://ocna0.d2.comp.nus.edu.sg:50000/change.jpg'


def start_socket(port, image_flag, attack_flag):
    threads = [None] * 10
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
                    total_bytes = [0]
                    thread = threading.Thread(target=proxy_connect, args=(conn, data, addr, image_flag, total_bytes))
                    thread.start()

            except KeyboardInterrupt:
                sock.close()
                print("Keyboard interrupt detected, closing socket.")
                sys.exit(1)

def proxy_connect(conn, data, addr, image_flag, total_bytes):
    if data.find(b"GET") == -1:
        print("invalid request")
        return
    decoded_data = data.decode(FORMAT)
    url = decoded_data.split('\n')[0].split(' ')[1]
    if image_flag and (url.find('jpg') != -1 or url.find('jpeg') != -1 or url.find('png') != -1):
        url = 'http://ocna0.d2.comp.nus.edu.sg:50000/change.jpg'
        line_split_data = decoded_data.split('\n')
        split_decode_url = line_split_data[0].split(' ') 
        split_decode_url[1] = url
        joint_img_url = " ".join(split_decode_url)
        line_split_data[0] = joint_img_url
        data = "\n".join(line_split_data).encode(FORMAT)
    http_pos = url.find('://')
    if http_pos != -1:
        url = url[(URL_OFFSET+http_pos):]
    server = ""
    port = -1
    port_pos = url.find(':')
    server_pos = url.find('/')
    if server_pos == -1:
        server_pos = len(url)
    if(port_pos == -1):
        port = 80
        server = url[:server_pos]
    else:
        pre_port = url[(port_pos+1):]
        port = int(pre_port[:server_pos-port_pos-1])
        server = url[:port_pos]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as second_sock:
            second_sock.settimeout(5)
            second_sock.connect((server, port))
            second_sock.sendall(data) # should this be encoded in utf-8?
            while True:
                sock_reply = second_sock.recv(BUFFER_SIZE)
                total_bytes[0] += len(sock_reply)
                if len(sock_reply) > 0:
                    conn.send(sock_reply)
                else:
                    break
        conn.close()
            
    except socket.error:
        second_sock.close()
        conn.close()
        print(f"{url}, {total_bytes[0]}")



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
    start_socket(port, image_flg, attack_flg)

    