#!/usr/bin/env python3

import os
import numpy as np
import ktrain
from ktrain import text
import pickle
import urllib.parse
import requests
from tensorflow.keras.models import load_model
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID";
os.environ["CUDA_VISIBLE_DEVICES"]="0"; 
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "10.1.1.4"
serverPort = 8081
base_url = 'https://arcadia.f5ase.net'

def proc(req):
 # loading preprocess and model file
        features = pickle.load(open('/home/jupyter/tf_model.preproc',
                            'rb'))
        new_model = load_model('/home/jupyter/tf_model.h5')
        labels = ['benign', 'sqli', 'xss']
        text = urllib.parse.unquote(req)
        preproc_text = features.preprocess([text])
        result = new_model.predict(preproc_text)
        label = labels[result[0].argmax(axis=0)]
        score = ('{:.2f}'.format(round(np.max(result[0]), 2)*100))
        resp = print('LABEL :', label, 'SCORE :', score)
        return label

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        result = proc(self.path)
        if result != "benign":
            self.send_response(403, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()
        else:
            resp = requests.get(base_url+"/"+self.path , stream=True)
            contType = resp.headers['Content-Type']
            contLength = int(resp.headers['Content-Length'])
            self.send_response(resp.status_code)
            self.send_header("Content-Type", contType)
            self.send_header("Content-Length", contLength)
            self.end_headers()
            if contLength > 0:
                content = resp.content
                self.wfile.write(content)



    def do_POST(self):
        result = proc(self.path)
        if result != "benign":
            self.send_response(403, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()
        else:
            resp = requests.post(base_url+"/"+self.path, data=self.content , stream=True)
            contType = resp.headers['Content-Type']
            contLength = int(resp.headers['Content-Length'])
            self.send_response(resp.status_code)
            self.send_header("Content-Type", contType)
            self.send_header("Content-Length", contLength)
            self.end_headers()
            if contLength > 0:
                content = resp.content
                self.wfile.write(content)
    
    do_HEAD = do_GET
    do_PUT  = do_GET
    do_DELETE=do_GET   

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
