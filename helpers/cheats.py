import allure

import server.async_server as server
from helpers.debug_functions import visit_message


def easy_rar(rar_generator, need_gx=False, need_gy=False, need_visit=False, need_attach=True):
    was_gx = False
    was_gy = False
    msg_gx = None
    msg_gy = None

    for _ in range(2):
        incoming_request = server.get_incoming_request(258, 'gx')
        if incoming_request is not None:
            if was_gx:
                allure.attach(f'', name='2 request gx', attachment_type=allure.attachment_type.TEXT)
            send_rar_answer(rar_generator, incoming_request, msg_type='gx')
            was_gx = True
            if msg_gx is None:
                msg_gx = incoming_request
            if need_visit:
                visit_message(msg_gx)

        incoming_request = server.get_incoming_request(258, 'gy')
        if incoming_request is not None:
            if was_gy:
                allure.attach(f'', name='2 request gy', attachment_type=allure.attachment_type.TEXT)
            send_rar_answer(rar_generator, incoming_request, msg_type='gy')
            was_gy = True
            if msg_gy is None:
                msg_gy = incoming_request
            if need_visit:
                visit_message(msg_gy)

    if not was_gx and need_gx:
        raise AssertionError('Не пришел входящий RAR запрос gx')
    elif not was_gx and need_attach:
        allure.attach(f'', name='Не пришел входящий запрос по gx', attachment_type=allure.attachment_type.TEXT)

    if not was_gy and need_gy:
        raise AssertionError('Не пришел входящий RAR запрос gy')
    elif not was_gy and need_attach:
        allure.attach(f' ', name='Не пришел входящий запрос по gy', attachment_type=allure.attachment_type.TEXT)

    return msg_gx, msg_gy


def send_rar_answer(rar_generator, incoming_request, status=2001, msg_type='gx'):
    if msg_type == 'gx':
        rar_ans = rar_generator.make_rar_answer_gx(incoming_request, status)
    else:
        rar_ans = rar_generator.make_rar_answer_gy(incoming_request, status=status)
    server.send_request(rar_ans, server.route_info[rar_ans.getHBHID()])
    server.handle_incoming_request(incoming_request)
