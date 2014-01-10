import httplib
import socket
from websocket import create_connection

class TimeoutHTTPConnection(httplib.HTTPConnection):
    """A customised HTTPConnection allowing a per-connection
    timeout, specified at construction."""
    timeout = None

    def connect(self):
        """Override HTTPConnection.connect to connect to
        host/port specified in __init__."""

        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port,
                0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                if self.timeout:   # this is the new bit
                    self.sock.settimeout(self.timeout)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg

class TimeoutHTTPSConnection(httplib.HTTPSConnection):
    timeout = None
    
    def connect(self):
        "Connect to a host on a given (SSL) port."

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.timeout:
            self.sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        ssl = socket.ssl(sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(sock, ssl)

class WSResponse:
    def __init__(self, ws, status, reason):
        self.ws = ws
        self.status = status
        self.reason = reason

    def read(self):
        if self.status == 101:
            return self.ws.recv()
        else:
            return ""

class TimeoutWSConnection:
    def __init__(self,hostport):
        self.hostport = hostport
        self.status = 101
        self.reason = "OK"
        self.ws = None

    def request(self,method,path):
        try:
            self.ws = create_connection('ws://' + self.hostport + path)
            self.ws.send("Hello, World")
        except ValueError, e:
            self.status = 500
            self.reason = str(e)

    def getresponse(self):
        return WSResponse(self.ws, self.status, self.reason)

    def __call__(self, port):
        return self

    def __del__(self):
        if self.ws is not None:
            self.ws.close()

