#! python2

import socket

client_addr = '127.0.0.1'
client_port = 13337

class PythonInterface:
    def XPluginStart(self):
        self.Name = "xUDPRadio_server"
        self.Sig = ""
        self.Desc = "Radio stack datarefs UDP transmitter."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.sendto("XPluginStart called", (client_addr, client_port))
        return self.Name, self.Sig, self.Desc
    def XPluginStop(self):
        pass
    def XPluginEnable(self):
        return 1
    def XPluginDisable(self):
        pass
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass