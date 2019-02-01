import socket, traceback, random, requests
import cPickle as pickle
from contextlib import closing
from thread import start_new_thread

def get_ip(mode = "local"):
    if mode != "local":
        try:
            return requests.get('http://ip.42.pl/raw').text
        except:
            return get_ip("global")
    else:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return get_ip()

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

get_free_port = find_free_port #can use either

def echoSend(data): #echo function
    try:
        return random.choice((data.title(), data.upper(), data.lower()))
    except: #if not a string
        return data

def newLobby(portNo=find_free_port(), serverSend=echoSend):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #s.bind((get_ip(), portNo))
    s.bind(("", portNo))
    s.listen(1)
    while True:
        try:
            conn, addr = s.accept()
            newPort = find_free_port()
            conn.sendall("*reconnect* " + str(newPort))
            conn.close()
            start_new_thread(newServer, (newPort,serverSend))
        except:
            traceback.print_exc()

def newServer(portNo, serverSend):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", portNo))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        while True:
            try:
                data = get_data(conn)
                send_data(conn, serverSend(data))
            except:
                print(traceback.print_exc())
                return

def connectServer(host, port):
    try:
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((host, port))
        data = get_text(s1)
        if data.startswith("*reconnect* "):
            s1.close()
            newport = int(data.split("*reconnect* ")[1])
            s2.connect((host, newport))
            return s2
        else:
            raise Exception("Server didn't request reconnect")
    except Exception: #
        raise Exception("Invalid Hostname / Port.\nIf connecting to a server with the global hostname, check for forgetting to port forward")

def send_text(mysock, data):
    mysock.sendall(data)

def send_data(mysock, obj):
    my_object = pickle.dumps(obj)
    send_text(mysock, my_object)

def get_data(mysock):
    obj = get_text(mysock)
    return pickle.loads(obj)
    
def get_text(mysock):
    alldata = ""
    while True:
        data = mysock.recv(1024)
        if data:
            alldata = alldata + data
        else:
            return alldata
            
        if len(data) != 1024:
            return alldata
    return alldata
