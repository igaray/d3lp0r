import socket
import sys
import time
from MessageHandling import auth_request
from MessageHandling import parse

MAX_CONNECTION_TRIES = 10

class MASSimConnection:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port, username, password):
        self.host     = host
        self.port     = port
        self.username = username
        self.password = password
        print "@Connection: connecting to " + host + ":" + str(port)
        code = self.sock.connect_ex((host, port))
        if (code == 0):
            self.connected = True
        else:
            self.connected = False
            print "@Connection: failed. error:", code
        #time.sleep(2)
        self.authenticate(username, password)

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.connected = False

    def send(self, msg):
        """
        Calcula la longitud del mensaje a enviar, y mantiene la cantidad de 
        bytes enviados en cada llamada a send(), y sigue llamando hasta que se 
        hayan enviado todos los bytes. El string debe terminar en un byte nulo
        para que el server sepa que termino la transmision. 
        """
        if (self.connectionValid()):
            msg_length = len(msg)
            bytes_sent = 0
            while (bytes_sent < msg_length):
                sent = self.sock.send(msg[bytes_sent:])
                bytes_sent += sent
                print "@Connection: sent %s bytes: %s" % (sent, msg[:bytes_sent])
                if (sent == 0):
                    self.connected = False
                    raise RuntimeError("Server connection lost!")
        else:
            raise RuntimeError("Server connection lost!")


    def receive(self):
        """
        Recibe del socket de a bloques de 2048 bytes. Mientras no se detecte el 
        final del mensaje, que deberia ser un byte 0, intenta recibir mas 
        informacion. Devuelve el string recibido por el socket.
        """
        if (self.connectionValid()):
            stop = False
            msg  = ''
            while (not stop):
                msg += self.sock.recv(2048)
                if (len(msg) > 0):
                    stop = (msg[-1] == '\0')
                else:
                    print "@Connection: the message received was empty!"
                    stop = True
            return msg
        else:
            raise RuntimeError("Server connection lost")

    def connectionValid(self):
        i = 0
        while (not self.connected) and (i < MAX_CONNECTION_TRIES):
            self.connect(self.host, self.port, self.username, self.password)
            i += 1
            # Si no logramos conectarnos, hacemos espera progresiva.
            sleep(i)
        return self.connected
            
    def authenticate(self, username, password):
        # TODO: validate reply message, and return True or False according 
        # to result.
        # arreglar el tema del header que queda horrendo asi, hay que usar la libreria de MessageHandling, hay que usar la libreria de MessageHandling
        if (self.connectionValid()):
            print "@Connection: sending authentication message."
            self.send(auth_request(username, password))
            print "@Connection: waiting for reply."
            auth_reply = self.receive()
            result = parse(auth_reply)
            if (result['result'] != 'ok'):
                raise RuntimeError("Authentication failed.")
            else:
                print "@Connection: succesfully authenticated."
        else:
            raise RuntimeError("Server connection lost")
