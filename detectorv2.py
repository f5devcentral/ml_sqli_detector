#!/usr/bin/env python3

import argparse, os, random, sys, requests, ktrain
import numpy as np
from ktrain import text
#import pickle
import urllib.parse
from tensorflow.keras.models import load_model
from tensorflow.keras import layers
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID";
os.environ["CUDA_VISIBLE_DEVICES"]="0";
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading


def set_header():
    headers = {
        'Host': hostname
    }

    return headers
def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    parser.add_argument('--port', dest='port', type=int, default=8081,
                        help='serve HTTP requests on specified port (default: random)')
    parser.add_argument('--origin', dest='origin', type=str, default='arcadia.f5ase.net',
                        help='hostname of the origin (default: arcadia.f5ase.net)')
    parser.add_argument('--host', dest='hostname', type=str, default='arcadia.f5ase.net',
                        help='host header to send (default: same as origin)')
    parser.add_argument('--ip', dest='ip', type=str, default='127.0.0.1',
                        help='listen on IP (default: 127.0.0.1')
    parser.add_argument('--proto', dest='protocol', type=str, default='http',
                        help='protocol - either http or https (default: http')
    parser.add_argument('--model', dest='load_my_model', type=str, default='detector_model_distilbert',
                        help='Predictor model to use (default: detector_model_distilbert)')
    args = parser.parse_args(argv)
    return args
args = parse_args()
print(args)

def proc(req):
 # loading preprocess and model file
        #features = pickle.load(open('/home/jupyter/Jupyter/notebook/ml_sqli_detector/predictor_distilbert/tf_model.preproc',
        #                    'rb'))
        #predictor = ktrain.load_predictor(load_my_model)
        #new_model = ktrain.get_predictor(predictor.model, predictor.preproc)
        #labels = ['benign', 'sqli', 'xss']
        path = urllib.parse.unquote(req)
        try:
            text = path.split('?')[1]
        except:
            text = path
        #list = text.split()
        #preproc_text = features.preprocess(list)
        new_model = ml_model()
        result = new_model.predict(text)
        #label = labels[result[0].argmax(axis=0)]
        #score = ('{:.2f}'.format(round(np.max(result[0]), 2)*100))
        #resp = print('LABEL :', label, 'SCORE :', score)
        print(result)
        resp = result
        return resp

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def do_HEAD(self):
        self.do_GET(body=False)
        return

    def do_GET(self, body=True):
        result = proc(self.path)
        if result != "normal":
            self.send_response(403, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()
        else:
            sent = False
            try:
                url = '{}://{}{}'.format(args.protocol, args.origin, self.path)
                req_header = self.parse_headers()

                #print(req_header)
                print(url)
                resp = requests.get(url, headers=req_header, verify=False)
                sent = True

                self.send_response(resp.status_code)
                self.send_resp_headers(resp)
                msg = resp.text
                if body:
                    self.wfile.write(resp.content)
                return
            finally:
                if not sent:
                    self.send_error(404, 'error trying to proxy')



    def do_POST(self, body=True):
        result = proc(self.path)
        if result != "benign":
            self.send_response(403, "Payload is %s" % result)
            #self.send_header("Set-Cookie", "foo=bar")
            self.end_headers()
        else:
            sent = False
            try:
                url = '{}://{}{}'.format(args.protocol, args.origin, self.path)
                content_len = int(self.headers.get('Content-Length', 0))
                post_body = self.rfile.read(content_len)
                req_header = self.parse_headers()
                print(url)
                resp = requests.post(url, data=post_body, headers=req_header, verify=False)
                sent = True

                self.send_response(resp.status_code)
                self.send_resp_headers(resp)
                if body:
                    self.wfile.write(resp.content)
                return
            finally:
                if not sent:
                    self.send_error(404, 'error trying to proxy')

    do_PUT  = do_POST
    do_DELETE=do_POST

    def parse_headers(self):
            req_header = {}
            for line in self.headers:
                line_parts = [o.strip() for o in line.split(':', 1)]
                if len(line_parts) == 2:
                    req_header[line_parts[0]] = line_parts[1]
            return req_header

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        #print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                #print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        """Handle requests in a separate thread."""
def main(argv=sys.argv[1:]):
    global hostname
    global protocol
    args = parse_args(argv)
    hostname = args.hostname
    print('http server is starting on {} port {}...'.format(args.ip, args.port))
    server_address = (args.ip, args.port)
    protocol = args.protocol
    httpd = ThreadedHTTPServer(server_address, ProxyHTTPRequestHandler)
    httpd.serve_forever()
def ml_model():
    predictor = ktrain.load_predictor(args.load_my_model)
    new_model = ktrain.get_predictor(predictor.model, predictor.preproc)
    return new_model
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
