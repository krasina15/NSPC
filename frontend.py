#!/usr/bin/env python3
import json
import os
import pdfkit
import redis
import random
import logging
import lxml.html
import time
import sys, os, socket
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import pika

if sys.argv[1:]:
    http_port = int(sys.argv[1])
else:
    http_port = 8013

logfile = 'nspp.log'
rabbit_host = 'ubuntu05.sandbox'
rabbit_queue = 'hello'
redis_host  = 'ubuntu06.sandbox'
redis_port = '6379'
redis_db = '0'
message_202 = 'still working'
message_404 = 'retry post'

logging.basicConfig(level=logging.DEBUG,format='%(asctime)-15s - %(threadName)-10s - %(message)s',filename=logfile)
credentials = pika.PlainCredentials('badass', 'iseedeadpeople')

def reqest_pdf(msg_id):
    m = msg_id.split('.')
    n = m[0]
    msg_id = n.strip("/")
    logging.debug(msg_id + ' requested')
    redis_server = redis.Redis(redis_host, port=redis_port, db=redis_db)
    response = redis_server.get("R_" + msg_id)
    http_code = 200
    content_type = "application/pdf"
    if response is None:
        if redis_server.get("Q_" + msg_id) is None:
            logging.debug(msg_id + ' not found')
            response = (message_404).encode()
            http_code = 404 

            content_type = "text/plain"
        else:
            logging.debug(msg_id + ' shit happend!')
            response = (message_202).encode()
            http_code = 202
            content_type = "text/plain"
    logging.debug(msg_id + ' ready')
    return content_type, http_code, response;

def render_html(input_file):
    koreanrandom = 'Q_' + str(random.randrange(0, 1000000001, 2))
#    try:
    redis_server = redis.Redis(redis_host, port=redis_port, db=redis_db)
    redis_server.set(koreanrandom, input_file)
    rabbit_server = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host,credentials=credentials))
    channel = rabbit_server.channel()
    channel.queue_declare(queue=rabbit_queue)
    channel.basic_publish(exchange='', routing_key='hello',body=koreanrandom)
    rabbit_server.close()
    o = koreanrandom.split('_')
    koreanrandom = o[1]
    logging.debug(koreanrandom + ' task created')
    #except:
    #    logging.debug(koreanrandom + ' task creatin failed')
    #    redis_response = (message_404).encode()
    return (koreanrandom).encode('utf-8');

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = self.headers['content-length']
        data = self.rfile.read(int(length))
        html_contents = data.decode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Server", "the Non-Sucking Pdf Processor, early beta")
        self.end_headers()
        self.wfile.write(render_html(html_contents))
        self.wfile.flush()
        return

    def do_GET(self):
        if self.path.endswith(".request"):
            content_type, http_code, response = reqest_pdf(self.path)
            self.send_response(http_code)
            self.send_header("Server", "the Non-Sucking Pdf Processor, early beta")
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(response)
            self.wfile.flush()
        else:
            response = ("i'm a teapot!").encode()
            self.send_response(418)
            self.send_header("Server", "the Non-Sucking Pdf Processor, early beta")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(response)
            self.wfile.flush()
        return

if __name__ == '__main__':

    HTTPDeamon = ThreadingSimpleServer(('', http_port), HTTPRequestHandler)
    print("frontend node started at port" , http_port)

    try:
        HTTPDeamon.serve_forever()
    except KeyboardInterrupt:
        pass
    HTTPDeamon.server_close()
    logging.debug('frontend daemon stopt')
    print ("frontend node stopt")
