#!/usr/bin/env python3

import os
import numpy as np
import ktrain
from ktrain import text
import pickle
import urllib.parse
from tensorflow.keras.models import load_model
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID";
os.environ["CUDA_VISIBLE_DEVICES"]="0"; 
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "10.1.1.4"
serverPort = 8081

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
            self.send_response(200, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()

    def do_POST(self):
        result = proc(self.path)
        if result != "benign":
            self.send_response(403, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()
        else:
            self.send_response(200, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()
    

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
