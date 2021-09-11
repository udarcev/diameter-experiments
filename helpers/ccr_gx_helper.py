from allure import step

from config.crn_dicts import CrnNames
from config.global_temp_config import crn_names
from helpers import debug_functions as df
from server import async_server as server


def init_gx(ccr_gx_gen, base_name=crn_names[CrnNames.BASE], result_code=2001, custom_configuration=None):
    if custom_configuration is None:
        custom_configuration = []
    with step("Работа с gx сервером"):
        with step('Отправка CCR-I на gx'):
            ccr_msg_gx = ccr_gx_gen.test_message()
            for configuration in custom_configuration:
                configuration(ccr_gx_gen, ccr_msg_gx)
            ccr_test_gx = server.send_request_and_get_answer(ccr_msg_gx, 'gx')
            current_result = df.find_avp_by_name(ccr_test_gx, "Result-Code").getAVPValue()
            assert current_result == result_code, f'Код ответа сервера не равен {result_code}, а равен {current_result}'
            if current_result == 2001:
                assert df.find_avp_by_name(ccr_test_gx, "Charging-Rule-Base-Name").getAVPValue() == base_name, \
                    f'CRBN не установлен в {base_name}, значение {df.find_avp_by_name(ccr_test_gx, "Charging-Rule-Base-Name").getAVPValue().decode("utf-8")}'
        return ccr_test_gx


def update_gx(ccr_gx_gen, custom_configuration=None):
    ccr_msg_gx = ccr_gx_gen.test_message()
    if custom_configuration is None:
        custom_configuration = []
    for configuration in custom_configuration:
        configuration(ccr_gx_gen, ccr_msg_gx)
    gx_answ = server.send_request_and_get_answer(ccr_msg_gx, 'gx')
    assert df.find_avp_by_name(gx_answ, "Result-Code").getAVPValue() == 2001, \
        "Код ответа сервера не равен 2001 (diameter_success)"
    return gx_answ


def terminate_gx(ccr_gx_gen):
    ccr_msg_terminate_gx = ccr_gx_gen.test_message(terminate=True)
    terminate_gx_answer = terminate_gx_with_custom_message(ccr_gx_gen, ccr_msg_terminate_gx)
    return terminate_gx_answer


def terminate_gx_with_custom_message(ccr_gx_gen, test_message):
    with step('Завершение работы сессии по gx'):
        ccr_msg_terminate_gx_answer = server.send_request_and_get_answer(test_message, 'gx')
        assert df.find_avp_by_name(ccr_msg_terminate_gx_answer, "Result-Code").getAVPValue() == 2001, \
            "Код ответа сервера не равен 2001 (diameter_success)"
        ccr_gx_gen.close_session()
    return ccr_msg_terminate_gx_answer


def add_event_trigger(value):
    return lambda gx_gen, msg: gx_gen.add_event_trigger(msg, value)


def set_imei(value):
    return lambda gx_gen, msg: gx_gen.set_imei(msg, value)


def set_charging_an_gw_address(value):
    return lambda gx_gen, msg: gx_gen.set_charging_an_gw_address(msg, value)


def set_3gpp_location(value):
    return lambda gx_gen, msg: gx_gen.set_3gpp_location(msg, value)


def set_mnr(value):
    return lambda gx_gen, msg: gx_gen.set_mnr(msg, value)


def set_3gpp_sgsn_mcc_mnc(value):
    return lambda gx_gen, msg: gx_gen.set_3gpp_sgsn_mcc_mnc(msg, value)


def set_rat_type(value):
    return lambda gx_gen, msg: gx_gen.set_rat_type(msg, value)
