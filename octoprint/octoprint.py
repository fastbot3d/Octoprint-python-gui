#!/usr/bin/env python
import wx

import sys
import os
import yaml
import requests
import json
import threading

API_NAME={'JOB':"job", 'connection':"connection"}

def log_debg(s):
    print("%s" % s)
    pass 


class File_info(object):
    def __init__(self, origin, name, size, type_1):
        self._origin = origin       
        self._file_name = name
        self._file_size =  size        
        self._file_type = type_1 
        
    def get_origin(self):
        return self._origin
    
    def get_file_name(self):
        return self._file_name
    
    def get_file_size(self):
        return self._file_size
    
    def get_file_type(self):
        return self._file_type
    
    def get_file_alldata(self):
        return (str(self._file_name), str(self._file_size))

class File_api(object):
    def __init__(self, ):
        self._local_files = {}
        self._local_total_and_free = (None,None)
        self._sd_total_and_free = (None,None)
        self._sd_files = {}
        self._local_file_infos = []
        self._sd_file_infos = []
           
    def get_free_info(self, storage):       
        if storage == "local":
            return self._local_total_and_free
        elif storage == "sd":
            return self._sd_total_and_free
        
    def __get_file(self, storage):
        '''
        {u'files': [{u'origin': u'local', 
            u'prints': {u'failure': 2, 
                        u'last': {u'date': 1450433250.627245, u'success': False}, 
                        u'success': 0}, 
            u'statistics': {u'averagePrintTime': {}, 
                            u'lastPrintTime': {}}, 
            u'hash': u'764f7535e8ddfa0a478994b6bbba3c19c73f6fef', 
            u'name': u'unicorn_0616.gcode', 
            u'links': [], 
            u'refs': {u'download': u'http://127.0.0.1/downloads/files/local/unicorn_0616.gcode', 
            u'resource': u'http://127.0.0.1/api/files/local/unicorn_0616.gcode'}, 
                      u'gcodeAnalysis': {u'estimatedPrintTime': 6464.706758542536, 
                                         u'filament': {u'tool0': {u'volume': 74.79684073069205, u'length': 11724.751669999978}}}, 
                        u'date': 1450420576, u'type': u'machinecode', u'size': 2113280}, 
             {u'origin': u'local', u'prints': {u'failure': 2, u'last': {u'date': 1449820909.628222, u'success': False}, u'success': 0}, u'statistics': {u'averagePrintTime': {}, u'lastPrintTime': {}}, u'hash': u'5ab82f93191a4e4b80b7c797d549472bdc19f0a9', u'name': u'Platform_Level-slice2.gcode', u'links': [], u'refs': {u'download': u'http://127.0.0.1/downloads/files/local/Platform_Level-slice2.gcode', u'resource': u'http://127.0.0.1/api/files/local/Platform_Level-slice2.gcode'}, u'gcodeAnalysis': {u'estimatedPrintTime': 308.84741226431754, u'filament': {u'tool0': {u'volume': 0.5275976565271746, u'length': 74.63979999999985}}}, u'date': 1449820451, u'type': u'machinecode', u'size': 16760}, 
             {u'origin': u'local', u'prints': {u'failure': 1, u'last': {u'date': 1449719759.60513, u'success': False}, u'success': 0}, u'statistics': {u'averagePrintTime': {}, u'lastPrintTime': {}}, u'hash': u'6459047d91ace60147c340aa12b95f08201bda3c', u'name': u'vase_tall_vase-slic3r-delta.gcode', u'links': [], u'refs': {u'download': u'http://127.0.0.1/downloads/files/local/vase_tall_vase-slic3r-delta.gcode', u'resource': u'http://127.0.0.1/api/files/local/vase_tall_vase-slic3r-delta.gcode'}, u'gcodeAnalysis': {u'estimatedPrintTime': 12547.951704378202, u'filament': {u'tool0': {u'volume': 144.63889445201337, u'length': 60133.86452998491}}}, u'date': 1449719325, u'type': u'machinecode', u'size': 4046167}, 
             {u'origin': u'local', u'prints': {u'failure': 3, u'last': {u'date': 1451198419.945757, u'success': False}, u'success': 0}, u'statistics': {u'averagePrintTime': {}, u'lastPrintTime': {}}, u'hash': u'99aad90102d6993c7b3cd2fff29938df952be129', u'name': u'hackaday.gcode', u'links': [], u'refs': {u'download': u'http://127.0.0.1/downloads/files/local/hackaday.gcode', u'resource': u'http://127.0.0.1/api/files/local/hackaday.gcode'}, u'gcodeAnalysis': {u'estimatedPrintTime': 1048.8243956206468, u'filament': {u'tool0': {u'volume': 12.818533597831212, u'length': 2009.36459}}}, u'date': 1449820922, u'type': u'machinecode', u'size': 1293669}], u'total': 56038436864, u'free': 26465378304}        
            u'total': 56038436864, 
            u'free': 26530140160
        '''            
        ret = octoprintApi.http_get('files/' + storage)  
        print("file:%s" % str(ret))
        file_infos = []
        if ret is not None:
            if storage == "local":
                self._local_total_and_free = (ret["total"],ret["free"])
            elif storage == "sd":
                self._sd_total_and_free = (ret["total"],ret["free"])             
            for f in ret['files'] :                
                _origin = f['origin']
                _file_name = f['name']
                _file_size = f['size']
                _file_type = f['type']
                f_info = File_info(_origin, _file_name, _file_size, _file_type)
                file_infos.append(f_info)
        return file_infos        

    def get_local_file(self):
        self._local_file_infos = self.__get_file("local")  
        return self._local_file_infos 
    
    def get_sd_file(self):
        self._sd_file_infos = self.__get_file("sd")                   
        return self._sd_file_infos
       
    
    def command(self, command=None, **params):  
        valid_commands = ["select", "slice"]
        if command is not None and command not in valid_commands:
            return None   
        
        params_all = {}
        params_all.update(params)
        return octoprintApi.http_post("files/" + params_all['target'] +'/' + params_all['filename'], headers={"Content-Type":"application/json"}, data={"command":command})
    
class Print_api(object):
    def __init__(self, ):
        self._job = None
        self._progress = None 
        self._state  = None       
        
    def get_tool_temp(self): 
        '''{u'tool1': {u'actual': 70.0, u'target': 180.0, u'offset': 0}, 
            u'tool0': {u'actual': 160.0, u'target': 220.0, u'offset': 0}} ''' 
        ret = octoprintApi.http_get('printer/tool')     
        if ret is not None:
            if "tool0" in ret:
                a = ret["tool0"]["actual"]
                t = ret["tool0"]["target"]
                ret["tool0"]["actual"] = "{:.1f}".format(a)
                ret["tool0"]["target"] = "{:.1f}".format(t)
            if "tool1" in ret:
                a = ret["tool1"]["actual"]
                t = ret["tool1"]["target"]
                ret["tool1"]["actual"] = "{:.1f}".format(a)
                ret["tool1"]["target"] = "{:.1f}".format(t)       
            if "tool2" in ret:
                a = ret["tool2"]["actual"]
                t = ret["tool2"]["target"]
                ret["tool2"]["actual"] = "{:.1f}".format(a)
                ret["tool2"]["target"] = "{:.1f}".format(t)               
        return ret     
    
    def get_bed_temp(self): 
        '''{u'bed': {u'actual': 70.3, u'target': 70.3, u'offset': 0}} '''   
        ret = octoprintApi.http_get('printer/bed')  
        if ret is not None:
            if "bed" in ret:
                a = ret["bed"]["actual"]
                t = ret["bed"]["target"]
                ret["bed"]["actual"] = "{:.1f}".format(a)
                ret["bed"]["target"] = "{:.1f}".format(t)        
        return ret   
    
    def sd_init_eject(self, command=None): 
        valid_commands = ["init", "refresh", "release"]
        if command is not None and command not in valid_commands:
            return None                  
        return octoprintApi.http_post("printer/sd", headers={"Content-Type":"application/json"}, data={"command":command})    


class Job_api(object):
    def __init__(self, ):
        self._job = None
        self._progress = None 
        self._state  = None       
        

    def command(self, command):  
        valid_commands = ["start", "restart", "pause", "cancel"]
        
        if command is not None and command not in valid_commands:
            return None        
        return octoprintApi.http_post('job', headers={"Content-Type":"application/json"}, data={"command":command})

    def get_job_state(self):
        ret = octoprintApi.http_get('job')        
        '''
        job_state:{
          u'progress': {u'completion': 0.1502702777913052, u'printTime': 6, u'filepos': 1944, u'printTimeLeft': 1042},
               u'job': {u'file': {u'date': 1449820922, u'origin': u'local', u'name': u'hackaday.gcode', u'size': 1293669}, u'estimatedPrintTime': 1048.8243956206468, u'averagePrintTime': None, u'filament': {u'tool0': {u'volume': 12.818533597831212, u'length': 2009.36459}}, u'lastPrintTime': None}, 
             u'state': u'Printing'}
        '''
        if ret is not None:
            self._job = ret['job']
            self._progress =  ret['progress']
            self._state  = ret['state']                             
        return {'estimatedPrintTime':str(self._job['estimatedPrintTime']), 'printTime':str(self._progress['printTime']), 'printTimeLeft':str(self._progress['printTimeLeft'])}
    
class Connection_api(object):
    def __init__(self):
        self._state = None
        self._port = None
        self._baudrate= None
        self._printerProfile= None    
        self._all_printerProfile= None         
        pass

    def is_closed(self):
        return self._state == "Closed" or "Error" in self._state
    
    def is_operational(self):
        return self._state == "Operational"    
    
    def is_printing(self):
        return self._state == "Printing" 
    
    def is_pause(self):
        return self._state == "Paused"     
    
    def get_connection_state(self):
        return self._state       
    
    def get_connection_printerProfile(self):
        ret = None
        for p in self._all_printerProfile:
            if p["id"] == self._printerProfile:
                ret =p["name"]
        return ret     
    
    def get_connection_all_printerProfile(self):
        ret = []
        for p in self._all_printerProfile:
            ret.append(p["name"])
        return ret    
    
    def get_connection_info(self):
        ret = octoprintApi.http_get('connection')
        '''
        state:Operational,
        port:AUTO, 
        baudrate:115200, 
        printerProfile:_default, 
        all_profile:[{u'id': u'_default', u'name': u'Default'}]    
        
        state:Closed, 
        port:None, baudrate:None, 
        printerProfile:_default, 
        all_profile:[{u'id': u'_default', u'name': u'Default'}]
        '''
        self._state = ret['current']['state']
        self._port = ret['current']['port']
        self._baudrate= ret['current']['baudrate']
        self._printerProfile= ret['current']['printerProfile']         
        self._all_printerProfile= ret['options']['printerProfiles']
        
        log_debg("state:%s, port:%s, baudrate:%s, printerProfile:%s, all_profile:%s" % (str( self._state), str(self._port), str(self._baudrate), str(self._printerProfile), str(self._all_printerProfile)))
    
    def command(self, command=None, **connect_args):
        valid_commands = ["connect", "disconnect", "fake_ack"]
        if command is not None and command not in valid_commands:
            return None  
        
        data = {}
        data.update({"command":command})

        if "connect" in data["command"]:
            if "printerProfile" in connect_args:
                profile_name = connect_args.pop("printerProfile")
                profile_id = None
                for p in self._all_printerProfile:
                    if p["name"] == profile_name:
                        profile_id = p["id"]
                        break                
                data.update({"printerProfile":profile_id})
            data.update(connect_args)            
        
        return octoprintApi.http_post('connection', headers={"Content-Type":"application/json"}, data=data)           
        
class octoprint_api(object):      
    def __init__(self, configfile=None, server_ip=None):
        self._timeout_get = 3  #async ??? grequests and requests-futures.
        self._timeout_post = 3
        self._config = None
        self._api_key = None
        self._server_url = "http://" + server_ip + ":80/api/"        
        self._access_lock = threading.Lock()
        
        self._config = self.load(configfile)
        if self._config is not None and "api" in self._config:
            if "key" in self._config["api"]:
                self._api_key = self._config["api"]["key"]
        pass
    
    def is_first_run(self):
        return self._api_key is None

    def load(self, configfile):
        if os.path.exists(configfile) and os.path.isfile(configfile):
            with open(configfile, "r") as f:
                self._config = yaml.safe_load(f)
        if not self._config:
            self._config = {}
        return self._config    

    '''
    headers  for "Content-Type":"application/json"
    data for jason data.  
    params for other
    '''
    def http_post(self, node, headers=None, params=None, data=None):
        self._access_lock.acquire()
        data_all = None
        header_all = {}
        headers_api = {'X-Api-Key': self._api_key}
        header_all.update(headers_api)
        
        if headers is not None :
            header_all.update(headers)
        log_debg("post node:%s, params:%s" % (str(self._server_url + node), str(params)))
        log_debg("post header_all:%s" % (str(header_all)))
        log_debg("post data:%s" % (str(data)))
        
        #payload = {'command':'cancel'}
        #r = requests.post(self._server_url + node, headers=header_all, data=json.dumps(payload))
        if data is not None:
            data_all = json.dumps(data)           
            
        r = requests.post(self._server_url + node, headers=header_all, params=params, data=data_all, timeout=self._timeout_post)        
        log_debg("post status_code:%s" % str(r.status_code))
        if r.status_code < 400:
            #print("request get header:%s, text:%s, json:%s" % (str(r.headers), str(r.text), str(r.json()) ))
            ret = "ok"
        else:
            print("request post failed, text:%s" % (str(r.text)))            
            ret = None   
        self._access_lock.release()
        return ret

    '''
          "printer", params={"exclude":"temperature,sd"}    
    '''
    def http_get(self, node, params=None):      
        self._access_lock.acquire()
        try:
            headers = {'X-Api-Key': self._api_key}
            log_debg("get url:%s" % (str(self._server_url + node)))
            #r = requests.get(self._server_url + node, headers=headers, params={"exclude":"temperature,sd"})
            r = requests.get(self._server_url + node, headers=headers, params=params, timeout=self._timeout_get)
            if r.status_code < 400:
                #print("request get header:%s, text:%s, json:%s" % (str(r.headers), str(r.text), str(r.json()) ))
                ret = r.json()
            else:
                print("request get failed, text:%s" % (str(r.text)))  
                ret = None   
        except:
            print("get request except")  
            ret = None                   
        self._access_lock.release()
        
        return ret
        
        
global octoprintApi
octoprintApi = octoprint_api(configfile="/root/.octoprint/config.yaml", server_ip="127.0.0.1")
  
            
def main(argv):
    global octoprintApi
    octoprintApi = octoprint_api(configfile="/root/.octoprint/config.yaml", server_ip="127.0.0.1")
    log_debg("is first run:%s" % str(octoprintApi.is_first_run()))
    log_debg("config file:%s" % str(octoprintApi._config))
    log_debg("config file api key:%s" % str(octoprintApi._api_key))    
    
    r = octoprintApi.http_get("printer")    
    #r = octoprintApi.http_get("printer", params={"exclude":"temperature,sd"})    
    print("r=%s" % str(r))
    #print("j=%s" % str(r['state']['text']))
    
    #cancel
    #r = octoprintApi.http_post("job", headers={"Content-Type":"application/json"}, data={"command":"cancel"})
    #print("cancel =%s" % str(r))
    
    conn_api = Connection_api()
    conn_api.get_connection_info()
    #ret = conn_api.command(command={"command":"disconnect"})    
    #ret = conn_api.command(command={"command":"connect"}, autoconnect=False, baudrate=115200, port="AUTO", printerProfile="_default")
    #print("ret=%s" % str(ret))
    
    job_api_test = Job_api()
    ret = job_api_test.get_job_state()
    print("ret=%s" % str(ret))
    #file_api_test = File_api()
    #ret = file_api_test.get_local_file()
    #for f in ret:
    #    print("ret=%s" % str(f.get_file_alldata()))
    #ret = file_api_test.command(command={"command":"select"}, target='local', filename='unicorn_0616.gcode')
    #print("ret=%s" % str(ret))
    #job_api_test.command(command={"command":"start"})
    #job_api_test.command(command={"command":"restart"})
    #job_api_test.command(command={"command":"pause"})
    #job_api_test.command(command={"command":"cancel"})  
    
    print_api = Print_api()
    #ret = print_api.get_tool_temp()
    #print("tool temp=%s" % str(ret))
    #ret = print_api.get_bed_temp()
    #print("bed temp=%s" % str(ret))
    ret = print_api.sd_init_eject("refresh") #init, release, 
    print("sd_init_eject=%s" % str(ret))
       
        
if __name__ == "__main__":
    main(sys.argv[1:])
