#!/usr/bin/env python3

import pika
import sys, os
import time
import threading
import logging
import redis
import queue
import pdfkit

xrange=range

if sys.argv[1:]:
    max_threads = int(sys.argv[1])
else:
    max_threads = 4

logfile = 'nspp.log'
rabbit_host = 'ubuntu05.sandbox'
rabbit_queue = 'hello'
redis_host  = 'ubuntu06.sandbox'
redis_port = '6379'
redis_db = '0'
logging.basicConfig(level=logging.DEBUG,format='%(asctime)-15s - %(threadName)-10s - %(message)s',filename=logfile)

def render_pdf(msg_id):
    output_file = '/tmp/' + msg_id + '.pdf'
    input_file = '/tmp/' + msg_id + '.html'
    logging.debug('loading html from redis')
    redis_server = redis.Redis(redis_host, port=redis_port, db=redis_db)
    redis_response = redis_server.get(msg_id)
    logging.debug('html loaded')
    m = open(input_file, "wb")
    m.write(redis_response)
    m.close()
    logging.debug('html writed')
    start_time = time.time()
    sys_output = pdfkit.from_file(input_file, output_file)
    finish_time = time.time()
    input_size = str(os.path.getsize(input_file)/1024) #.decode('utf-8')
    output_size = str(os.path.getsize(output_file)/1024) #.decode('utf-8')
    dbg_mesg = '[R] Render [msg.id:' + msg_id + '] ' + '[rend.time:' + str(finish_time-start_time) + 'sec]' + '[in.fle:' + input_file + '(' + input_size + 'kb)]' + '[ou.fle:' + output_file + '(' + output_size + 'kb)]'
    logging.debug(dbg_mesg)
    n = open(output_file, "rb")
    binary_data = n.read()
    n.close()
    logging.debug('pdf loaded')
    msg_out = msg_id.split('_')
    msg = 'R_' + msg_out[1]
    redis_server.set(msg, binary_data)
    logging.debug('pdf writed')
    redis_server.delete(msg_id)
    logging.debug('db record removed: ' + msg_id)
    os.remove(output_file)
    logging.debug('tmp file removed: ' + input_file)
    os.remove(input_file)
    logging.debug('tmp file removed: ' + output_file)
    logging.debug('render done')
    if not sys_output:
        return True, output_file
    return False, sys_output

logging.debug('backend node starting...')
TQ = queue.Queue()
logging.debug('threads pool starting...')

def catcher(q):
    while True:
        try:
            item = q.get()
        except Empty:
            break

        logging.debug('render get task: ' + item.strip().decode('utf-8'))
        render_pdf(item.strip().decode('utf-8'))
        q.task_done()

for i in xrange(max_threads):
    wrkr_T = threading.Thread(target = catcher, args=(TQ,))
    wrkr_T.daemon = True
    wrkr_T.start()
    logging.debug('thread: ' + str(i) + ' started')

logging.debug('consumer started...')
credentials = pika.PlainCredentials('badass', 'iseedeadpeople')
try:
    rabbit_server = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host,credentials=credentials))
    channel = rabbit_server.channel()
    channel.queue_declare(queue=rabbit_queue)
    def callback(ch, method, properties, body):
        TQ.put(body)
        logging.debug('consumer got task: ' + body.strip().decode('utf-8'))
    channel.basic_consume(callback, queue = rabbit_queue, no_ack = True)
    channel.start_consuming()

except KeyboardInterrupt:
    logging.debug('backen daemon stopt')
    print ("backend node stopt")


