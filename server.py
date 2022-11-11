import socket
import threading
import sys
import time

# can't cache across different test cases.
# but, you can cache within the same test case for the image. 

# MAX_REQUEST_LEN=1080
# CONECTION_TIMEOUT=100
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT='utf-8'
URL_OFFSET = 3

def start_socket(port, image_flag, attack_flag):
  try: 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER, port))
    sock.listen(100)
  except Exception:
    print("Socket was unable to be initialized")
    print(Exception)
  
  while True:
    try:
      conn, addr = sock.accept()
      client_host, client_port = addr
      if attack_flag:
        # conn, (client_host, client_port) = sock.accept()
        print('Got connection from', client_host, client_port)
        #c.send('Server Online\n') # This is invalid HTTP header
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
        data = conn.recv(4084).decode(FORMAT)
        print('receiving data ', data)
        thread = threading.Thread(target=handle_client, args=(conn, addr, data, image_flag, attack_flag), daemon=True)
        thread.start()
    except KeyboardInterrupt:
      sock.close()
      print("Shutting down")
      sys.exit(1)
    except UnicodeDecodeError:
      sock.close()
      print("some non utf-8 encoding was used")
      sys.exit(1)

def handle_client(conn, addr, data, image_flag, attack_flag):
  if data.find("GET") == -1:
    return
  print(f"starting thread with addr {addr}")
  url = data.split('\n')[0].split(' ')[1]
  http_pos = url.find("://")
  temp = url[(URL_OFFSET+http_pos):]
  server = ""
  port = -1
  port_position = temp.find(":") # find the port pos (if any)
  web_position = temp.find("/")
  if web_position == -1:
      web_position = len(temp)
  if (port_position==-1 or web_position < port_position): 
    port = 80 
    server = temp[:web_position] 
  else: # specific port 
    port = int((temp[(port_position+1):])[:web_position-port_position-1])
    server = temp[:port_position]
  print('address is ', temp)
  print('server is ', server)
  # now create proxy and send data back
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, port))
    sock.send(data.encode(encoding=FORMAT))
    # print('sending data ', data)
    fail_ct = 0
    while 1:
      reply = sock.recv(5000)
      if len(reply) > 0:
        print("we have sent reply")
        conn.sendall(reply)
        fail_ct = 0
      elif len(reply) <= 0 and fail_ct < 2:
        time.sleep(.5)
        fail_ct += 1
      else:
        print("we are breaking")
        break
    sock.close()
    conn.close()
  except socket.error:
    sock.close()
    conn.close()
    print(sock.error)
    sys.exit(1)
  pass

if __name__ == '__main__':
  arguments = sys.argv[1:]
  port = 5050
  image_flg = 0
  attack_flg = 0
  if len(arguments) > 0:
    port = arguments[0]
  if len(arguments) > 1:
    image_flg = arguments[1]
  if len(arguments) > 2:
    attack_flg = arguments[2]
  print(f"Listening to port {port}")
  start_socket(port, image_flg, attack_flg)

