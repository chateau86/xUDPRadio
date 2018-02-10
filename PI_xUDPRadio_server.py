#! python2

import socket
import XPLMProcessing
import XPLMDataAccess

interval_short = 0.1
interval_long = 10
client_addr = "127.0.0.1"
client_port = 13337

class PythonInterface:
    def XPluginStart(self):
        print "XPluginStart called"
        self.Name = "xUDPRadio_server"
        self.Sig = ""
        self.Desc = "Radio stack datarefs UDP transmitter."
        #set up socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.sendto("XPluginStart called", (client_addr, client_port))
        #set up datarefs
        self.radios = dict()
        for r in ['nav1','nav2','com1','com2','adf1','adf2']:
            self.radios[r] = Radio(r)
            print 'Added {:}: {:}'.format(r, self.radios[r])
        #add callback
        self.short_callback = self.short_callback
        self.long_callback = self.long_callback
        return self.Name, self.Sig, self.Desc
        
    def XPluginStop(self):
        print "XPluginStop called"
        pass
    def XPluginEnable(self):
        print "XPluginEnable called"
        self.sock.sendto("XPluginEnable called", (client_addr, client_port))
        XPLMProcessing.XPLMRegisterFlightLoopCallback(self, self.short_callback, interval_short, 0)
        XPLMProcessing.XPLMRegisterFlightLoopCallback(self, self.long_callback, interval_short, 0)
        return 1
    def XPluginDisable(self):
        print "XPluginDisable called"
        XPLMProcessing.XPLMUnregisterFlightLoopCallback(self, self.short_callback, 0)
        pass
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass
        
    def short_callback(self, elapsedMe, elapsedSim, counter, refcon):
        #self.sock.sendto("loopCallback called", (client_addr, client_port))
        for r in self.radios:
            chg = self.radios[r].read_sim()
            if not len(chg) == 0:
                for c in chg:
                    self.sock.sendto("{:}: {:}->{:}".format(r, c, chg[c]), (client_addr, client_port))
        #continue looping
        return interval_short
        
    def long_callback(self, elapsedMe, elapsedSim, counter, refcon):
        self.sock.sendto("-----{:}".format(elapsedSim), (client_addr, client_port))
        for r in self.radios:
            for c in self.radios[r].state_vct:
                self.sock.sendto("\t{:}: {:}={:}".format(r, c, self.radios[r].state_vct[c]), (client_addr, client_port))
        #continue looping
        self.sock.sendto("-----", (client_addr, client_port))
        return interval_long
class Radio:
    def __init__(self, name):
        self.name = name #{nav1/2, com1/2, adf1/2}
        self.type = name[0:3] #com/nav/adf
        self.state_vct_dref = dict()
        self.state_vct_reader = dict()
        self.state_vct = None
        self.dref_name = "sim/cockpit/radios/{:}".format(name)
        #
        self.state_vct_dref['freq'] = XPLMDataAccess.XPLMFindDataRef(self.dref_name+'_freq_hz')
        self.state_vct_dref['stdby_freq'] = XPLMDataAccess.XPLMFindDataRef(self.dref_name+'_stdby_freq_hz')
        self.state_vct_reader['freq'] = (lambda: XPLMDataAccess.XPLMGetDatai(self.state_vct_dref['freq']))
        self.state_vct_reader['stdby_freq'] = (lambda: XPLMDataAccess.XPLMGetDatai(self.state_vct_dref['stdby_freq']))
        if self.type == 'nav':
            self.state_vct_dref['obs'] = XPLMDataAccess.XPLMFindDataRef(self.dref_name+'_obs_degm')
            self.state_vct_dref['obs2'] = XPLMDataAccess.XPLMFindDataRef(self.dref_name+'_obs_degm2')
            self.state_vct_reader['obs'] = (lambda: XPLMDataAccess.XPLMGetDataf(self.state_vct_dref['obs']))
            self.state_vct_reader['obs2'] = (lambda: XPLMDataAccess.XPLMGetDataf(self.state_vct_dref['obs2']))
    
    def __str__(self):
        return '{:}, Type:{:}'.format(self.name, self.type)
    
    def read_sim(self): #return dict of changed states
        new_vct = dict()
        chg_dict = dict()
        if self.state_vct is None:
            for dref in self.state_vct_reader:
                new_vct[dref] = self.state_vct_reader[dref]()
        else:
            for dref in self.state_vct_reader:
                new_vct[dref] = self.state_vct_reader[dref]()
                if not new_vct[dref] == self.state_vct[dref]:
                    chg_dict[dref] = new_vct[dref]
        self.state_vct = new_vct
        return chg_dict