import socket
import threading
import sys

# this probably needs to change to be the http port #

MAX_REQUEST_LEN=1080
CONECTION_TIMEOUT=1000
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT='utf-8'

class Server:
  def __init__(self, hostname, bind_port, img_flg, attack_flg) -> None:
    self.img_flg = img_flg
    self.attack_flg = attack_flg
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serverSocket.bind((hostname, bind_port))
    self.serverSocket.listen()
    self.start_socket()
  
  # TODO remove unecessary checkings from gfg
  def handle_client(self, conn, addr):
    print(f"new thread, {conn} and {addr}")
    request = conn.recv(MAX_REQUEST_LEN).decode(FORMAT)
    first_line = request.split('/n')[0]
    print('first_line', first_line)
    url = first_line.split(' ')[1]
    print('url', url)
    http_pos = url.find("://") # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):] # get the rest of url

    port_pos = temp.find(":") # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos): 

        # default port 
        port = 80 
        webserver = temp[:webserver_pos] 

    else: # specific port 
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.settimeout(CONECTION_TIMEOUT)
    print(f"webserver is {webserver}")
    print(f"temp is {temp}")
    s.connect((webserver, port))
    s.sendall(request.encode(encoding=FORMAT))
    while 1:
    # receive data from web server
      data = s.recv(MAX_REQUEST_LEN)
      # manipulate images if needed 
      print(f"data is {data}")
      if (len(data) > 0):
          conn.send(data) # send to browser/client
      else:
          break


  def start_socket(self):
    while True:
      print(f"starting")
      conn, addr = self.serverSocket.accept()
      print("accepted address")
      thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
      thread.start()

if __name__ == '__main__':
  arguments = sys.argv[1:]
  port = 5050
  image_flg = 0
  attack_flg = 0
  if len(arguments) > 1:
    port = arguments[0]
    image_flg = arguments[1]
    attack_flg = arguments[2]

  serve = Server(SERVER, port, image_flg, attack_flg)
  serve.start_socket()