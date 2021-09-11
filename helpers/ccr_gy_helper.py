from allure import step

from helpers import debug_functions as df
from server import async_server as server


def init_gy(ccr_gy_gen, service_for_traffic, custom_configuration=None):
    if custom_configuration is None:
        custom_configuration = []
    with step("Работа с gy сервером"):
        with step('Отправка CCR-I на gy'):
            initial_ccr_msg_gy_u_answer = send_ccr_with_zero_traffic(ccr_gy_gen,
                                                                     service_for_traffic,
                                                                     custom_configuration=custom_configuration)
            assert df.find_avp_by_name(initial_ccr_msg_gy_u_answer, "Result-Code").getAVPValue() == 2001, \
                "Код ответа сервера не равен 2001 (diameter_success)"
            return initial_ccr_msg_gy_u_answer


def send_ccr_with_zero_traffic(ccr_gy_gen, service_for_traffic, reporting_reason=5, custom_configuration=None):
    if custom_configuration is None:
        custom_configuration = []
    with step(f'Отправка CCR запроса с нулевым потреблением по сервису {service_for_traffic}'):
        ccr_msg_gy_u = ccr_gy_gen.get_msg_traffic_configurable(0, 0, service_for_traffic, custom_configuration,
                                                               reporting_reason, need_used=False)
        ccr_msg_gy_u_answer = server.send_request_and_get_answer(ccr_msg_gy_u, 'gy')
        return ccr_msg_gy_u_answer


def terminate_gy(ccr_gy_gen):
    ccr_msg_terminate_gy = ccr_gy_gen.test_message(terminate=True)
    terminate_gy_answer = terminate_gy_with_custom_message(ccr_gy_gen, ccr_msg_terminate_gy)
    return terminate_gy_answer


def terminate_gy_with_custom_message(ccr_gy_gen, test_message):
    with step('Завершение работы сессии по gy'):
        ccr_msg_terminate_gy_answer = server.send_request_and_get_answer(test_message, 'gy')
        assert df.find_avp_by_name(ccr_msg_terminate_gy_answer, "Result-Code").getAVPValue() == 2001, \
            "Код ответа сервера не равен 2001 (diameter_success)"
        ccr_gy_gen.close_session()
    return ccr_msg_terminate_gy_answer


def get_max_traffic_consumption(initial_ccr_msg_gy_u_answer):
    cc_total_octets = df.find_avp_by_name(initial_ccr_msg_gy_u_answer, 'CC-Total-Octets').getAVPValue()
    v_q_threshold = df.find_avp_by_name(initial_ccr_msg_gy_u_answer, 'Volume-Quota-Threshold').getAVPValue()
    assert cc_total_octets > v_q_threshold, f'Значение CC-Total-Octets {cc_total_octets} 'f'меньше Volume-Quota-Threshold {v_q_threshold}'
    max_traffic_consumption = cc_total_octets - v_q_threshold
    return max_traffic_consumption


def set_sgsn_address(value):
    return lambda gy_gen, msg: gy_gen.set_sgsn_address(msg, value)


def set_current_date(value):
    return lambda gy_gen, msg: gy_gen.set_current_date(msg, value)


def set_cc_request_type(value):
    return lambda gy_gen, msg: gy_gen.set_cc_request_type(msg, value)


def set_3gpp_location(value):
    return lambda gy_gen, msg: gy_gen.set_3gpp_location(msg, value)


def set_3gpp_sgsn_mcc_mnc(value):
    return lambda gy_gen, msg: gy_gen.set_3gpp_sgsn_mcc_mnc(msg, value)


def set_3gpp_RAT_type(value):
    return lambda gy_gen, msg: gy_gen.set_3gpp_RAT_type(msg, value)


def set_mnr(value):
    return lambda gy_gen, msg: gy_gen.set_mnr(msg, value)
