import datetime
import sys

import allure

import config.global_temp_config as cf
import server.async_server as server
from avp.RAR_generator import RAR_generator
from config import msisdn_range_config
from helpers.debug_functions import find_avp_by_name, find_all_avps_by_name, scan_avp_all


def get_redirect_page(msg):
    assert find_avp_by_name(msg, 'Final-Unit-Indication') is not None, 'В ответе нет поля Final-Unit-Indication'
    assert find_avp_by_name(msg, 'Final-Unit-Action').getAVPValue() == 1, 'В ответе пришел не redirect'
    return find_avp_by_name(msg, 'Redirect-Server-Address').getAVPValue().decode('utf-8')


def get_all_CRNs(msg):
    CRN_values = find_all_avps_by_name(msg, "Charging-Rule-Name")
    return [x.getAVPValue() for x in CRN_values]


def get_all_event_triggers(msg):
    ET_values = find_all_avps_by_name(msg, "Event-Trigger")
    return [x.getAVPValue() for x in ET_values]


def get_all_gy_triggers(msg):
    Trig_values = find_all_avps_by_name(msg, "Trigger-Type")
    return [x.getAVPValue() for x in Trig_values]


def get_CRN_arrays(msg):
    CRNs_i = []
    CRNs_r = []
    try:
        install_avp = find_avp_by_name(msg, "Charging-Rule-Install")
        install_arr = []
        scan_avp_all(install_avp, "Charging-Rule-Name", install_arr)
        CRNs_i = [x.getAVPValue() for x in install_arr]
    except Exception as e:
        print(e, file=sys.stderr)
        pass
    try:
        remove_avp = find_avp_by_name(msg, "Charging-Rule-Remove")
        remove_arr = []
        scan_avp_all(remove_avp, "Charging-Rule-Name", remove_arr)
        CRNs_r = [x.getAVPValue() for x in remove_arr]
    except Exception as e:
        print(e, file=sys.stderr)
        pass
    return CRNs_i, CRNs_r


def get_CRBN_arrays(msg):
    CRBN_i = []
    CRBN_r = []
    try:
        install_avp = find_avp_by_name(msg, "Charging-Rule-Install")
        install_arr = []
        scan_avp_all(install_avp, "Charging-Rule-Base-Name", install_arr)
        CRBN_i = [x.getAVPValue() for x in install_arr]
    except Exception as e:
        print(e, file=sys.stderr)
        pass
    try:
        remove_avp = find_avp_by_name(msg, "Charging-Rule-Remove")
        remove_arr = []
        scan_avp_all(remove_avp, "Charging-Rule-Base-Name", remove_arr)
        CRBN_r = [x.getAVPValue() for x in remove_arr]
    except Exception as e:
        print(e, file=sys.stderr)
        pass
    return CRBN_i, CRBN_r


def allure_attach(name, text=''):
    allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)


def get_next_msisdn(ptype="postpaid", pblock="no", pfe_index=-1):
    msisdn = cf.msisdn_starter + next(msisdn_range_config.number_generator)
    imsi = '95001' + msisdn[-10:]
    allure.attach(f'{msisdn}', name=f'Тестовый номер - {msisdn}', attachment_type=allure.attachment_type.TEXT)
    return msisdn, imsi


def traffic_consumption_new(traffic_value, service, ccr_gy_gen, max_traffic_consumption, custom_configuration=None,
                            rep_reason=5, date_time=None, need_reauth=False, first_enter=True):
    if date_time is None:
        date_time = datetime.timedelta(0)
    elif isinstance(date_time, datetime.datetime):
        date_time = datetime.datetime.utcnow() - date_time

    if first_enter:
        print(f'Планируем потребить {traffic_value // 1024} Kb, по сервису - {service}')

    consume = min(traffic_value, max_traffic_consumption)
    ccr_msg_gy_u = ccr_gy_gen.get_msg_traffic_configurable(consume, 0, service, custom_configuration, rep_reason,
                                                           date_time=datetime.datetime.utcnow() - date_time,
                                                           need_reath=need_reauth)

    ccr_msg_gy_u_answer = server.send_request_and_get_answer(ccr_msg_gy_u, 'gy')
    assert find_avp_by_name(ccr_msg_gy_u_answer, "Result-Code").getAVPValue() == 2001, \
        "Код ответа сервера не равен 2001 (diameter_success)"
    traffic_value -= consume

    left_part = f'потребление - {consume // 1024} Kb'
    tabs = "\t\t" if len(left_part) < 23 else "\t"
    print(f'{left_part},{tabs} осталось потребить {traffic_value // 1024} Kb')

    if traffic_value <= 0:
        return ccr_msg_gy_u_answer
    else:
        cc_total_octets = find_avp_by_name(ccr_msg_gy_u_answer, 'CC-Total-Octets')
        if cc_total_octets is None:
            print('CC Total не пришел, ищем поле редиректа')
            redirect = get_redirect_page(ccr_msg_gy_u_answer)
            print(f'{redirect} Редирект получен')
            allure.attach(f'{redirect}', name='Редирект получен', attachment_type=allure.attachment_type.TEXT)
            return ccr_msg_gy_u_answer
        else:
            v_q_threshold_avp = find_avp_by_name(ccr_msg_gy_u_answer, 'Volume-Quota-Threshold')
            v_q_threshold = 0 if v_q_threshold_avp is None else v_q_threshold_avp.getAVPValue()
            assert cc_total_octets.getAVPValue() > v_q_threshold, \
                f'Значение CC-Total-Octets {cc_total_octets.getAVPValue()} меньше Volume-Quota-Threshold {v_q_threshold}'
            new_max_traffic_consumption = cc_total_octets.getAVPValue() - v_q_threshold
            assert cc_total_octets.getAVPValue() > 1024, \
                f'{cc_total_octets.getAVPValue()} cc_total_octets не должен быть меньше 1024'

            incoming_request = server.get_incoming_request_no_wait(258, 'gy')
            if incoming_request is not None:
                rar_ans = RAR_generator.make_rar_answer_gy(incoming_request)
                server.send_request(rar_ans, server.route_info[rar_ans.getHBHID()])
                server.handle_incoming_request(incoming_request)
                return traffic_consumption_new(traffic_value, service, ccr_gy_gen, new_max_traffic_consumption,
                                               custom_configuration, rep_reason, date_time=date_time,
                                               need_reauth=True, first_enter=False)
            else:
                return traffic_consumption_new(traffic_value, service, ccr_gy_gen, new_max_traffic_consumption,
                                               custom_configuration, rep_reason, date_time=date_time,
                                               need_reauth=False, first_enter=False)
