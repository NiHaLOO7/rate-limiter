import socket
class RedisClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = self._connect(host, port)

    def _connect(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, port))
        return server
    
    def _parse_response(self, response):
        response = response.strip()
        if response ==  '$None':
            return None
        if response.startswith('-ERR'):
            return None
        return response[1:]
    
    def _parse_list(self, lst):
        if not lst:
            return None
        lst =  lst.strip('[').strip(']').replace("'","")
        return [] if lst == '' else lst.split(", ")

    
    def _send(self, command):
        self.server.send(command.encode())
        response = self.server.recv(1024).decode()
        return self._parse_response(response)

    def set(self, key, value):
        command = "SET" + " " + key + " " + value+ "\n"
        return self._send(command)

    def get(self, key):
        command = "GET" + " " + key + "\n"
        return self._send(command)
    
    def incr(self, key):
        command = "INCR" + " " + key + "\n"
        return self._send(command)
    
    def lpush(self, key, value):
        command = "LPUSH" + " " + key + " " + value +"\n"
        return self._send(command)
    
    def lrange(self, key, start, end):
        command = "LRANGE" + " " + key + " " + start  + " " + end +"\n"
        return self._parse_list(self._send(command))
    
    def ltrim(self, key, start, end):
        command = "LTRIM" + " " + key + " " + start  + " " + end +"\n"
        return self._send(command)
    
    def close(self):
        self.server.close()


        