import socket
import sys
import threading
import time

from pyDiameter.pyDiaMessage import DiaMessage

from config.global_temp_config import *
from server.reassemble_helper import decodeMessageHeader


def connect(host, port, timeout=7):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.settimeout(timeout)
    return sock


sockets = {}
buffers = {}
client_handlers = {}

received_requests = dict()
received_answers = dict()

sent_requests = dict()
sent_answers = dict()

route_info = dict()

incoming_requests = []

stop = False

timeout_timer = 0.1
receive_timer = 0.05


def send_request(msg, server):
    global sent_requests
    global sent_answers

    if server in sockets:
        sockets[server].send(msg.encode())
    else:
        raise NotImplementedError(f'Доступны только следующие названия: {" ".join(sockets.keys())}')

    if msg.getRequestFlag():
        sent_requests[msg.getHBHID()] = msg
    else:
        sent_answers[msg.getHBHID()] = msg


# TODO перейти на неблокирующее чтение, а то костыли с time.sleep чтобы не было полного busy wait при recv()
def __request_handler_template(server_name):
    def request_handler():
        print(f'started {server_name}')
        global received_requests
        global received_answers
        global incoming_requests
        while not stop:
            try:
                received = sockets[server_name].recv(MSG_SIZE)
                if len(received) > 0:
                    # Буфферы применены с той целью, что иногда, когда сообщение довольно большое,
                    # TCP протокол дробит его на несколько частей, и соответственно recv читает лишь часть сообщение, но
                    # этой части достаточно, чтобы достать хедер сообщения и узнать его длину

                    buffers[server_name] += received
                    msg_len = decodeMessageHeader(bytes(buffers[server_name]))
                    while msg_len <= len(buffers[server_name]):
                        msg_bytes = buffers[server_name][:msg_len]
                        buffers[server_name][:msg_len] = b''

                        msg_ans = DiaMessage()
                        msg_ans.decode(bytes(msg_bytes))
                        if msg_ans.getRequestFlag():
                            received_requests[msg_ans.getHBHID()] = msg_ans
                            route_info[msg_ans.getHBHID()] = server_name
                            incoming_requests.append(msg_ans)
                        else:
                            received_answers[msg_ans.getHBHID()] = msg_ans

                        if len(buffers[server_name]) > 0:
                            msg_len = decodeMessageHeader(bytes(buffers[server_name]))
                        else:
                            break

                time.sleep(receive_timer)
            except socket.timeout as t:
                time.sleep(timeout_timer)
            except ConnectionAbortedError as e:
                pass
            except Exception as e:
                print(e, file=sys.stderr)
                pass
        print(f'finish {server_name}')

    return request_handler


def send_request_and_get_answer(msg, server):
    send_request(msg, server)
    ans = get_answer_by_hbh(msg.getHBHID())
    return ans


def init_server():
    global sockets
    global client_handlers
    global incoming_requests
    global stop
    stop = False

    incoming_requests = []

    buffers['gx'] = bytearray()
    sockets['gx'] = connect(HOST_GX, PORT1)
    buffers['gy'] = bytearray()
    sockets['gy'] = connect(HOST_GY, PORT2)

    client_handlers['gx'] = threading.Thread(target=__request_handler_template('gx'), args=())
    client_handlers['gy'] = threading.Thread(target=__request_handler_template('gy'), args=())
    client_handlers['gx'].start()
    client_handlers['gy'].start()
    print('start server')


def finalize_server():
    global stop
    stop = True

    for k in client_handlers.keys():
        print(f'join thread {k}')
        client_handlers[k].join()

    print('finish server')


# так как сервер крутится в другом треде, тест, посылая сообщение, вообще не знает, когда вернется ответ
# так что это блокирующее ожидание ответа с таймаутом в 15 секунд
def get_answer_by_hbh(hbh):
    for _ in range(150):
        if hbh in received_answers:
            return received_answers[hbh]
        time.sleep(0.1)
    return None


# Аналогично, но немного другое. Так ловится входящее сообщение, когда не тест является его инициатором
def get_incoming_request(code, server):
    for _ in range(25):
        for msg in incoming_requests:
            if msg.getCommandCode() == code and route_info[msg.getHBHID()] == server:
                return msg
        time.sleep(0.1)
    return None


def get_incoming_request_no_wait(code, server):
    for msg in incoming_requests:
        if msg.getCommandCode() == code and route_info[msg.getHBHID()] == server:
            return msg
    return None


def handle_incoming_request(msg):
    global incoming_requests
    incoming_requests.remove(msg)
