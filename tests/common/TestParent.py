import datetime
import os
import time

from allure import step

import helpers.debug_functions as df
import helpers.useful_func as uf
import server.async_server as server
from avp.CCR_gx_generator import CCR_gx_generator
from avp.CCR_gy_generator import CCR_gy_generator
from avp.CER_generator import CER_gx_msg, CER_gy_msg
from config.crn_dicts import CrnNames
from config.global_temp_config import crn_names
from helpers import ccr_gy_helper, ccr_gx_helper


class TestParent:

    # noinspection PyMethodMayBeStatic
    def cers(self):
        worker_name = os.getenv('PYTEST_XDIST_WORKER', '0')
        ident = f"{worker_name}_{time.time()}"
        auth_msg_gx = CER_gx_msg(ident)
        auth_msg_gy = CER_gy_msg(ident)

        with step('Отправка CER запроса: gx'):
            cer_test_gx = server.send_request_and_get_answer(auth_msg_gx, 'gx')
            assert df.find_avp_by_name(cer_test_gx, "Result-Code").getAVPValue() == 2001, \
                "Код ответа сервера не равен 2001 (diameter_success)"

        with step('Отправка CER запроса: gy'):
            cer_test_gy = server.send_request_and_get_answer(auth_msg_gy, 'gy')
            assert df.find_avp_by_name(cer_test_gy, "Result-Code").getAVPValue() == 2001, \
                "Код ответа сервера не равен 2001 (diameter_success)"

    def setup(self):
        with step("Запуск диаметр клиента"):
            server.init_server()
            self.cers()

    # noinspection PyMethodMayBeStatic
    def teardown(self):
        with step("Остановка диаметр клиента"):
            server.finalize_server()

    # noinspection PyMethodMayBeStatic
    def consumption(self, request, msisdn, imsi, quota, service, tc, day, need_reauth=False,
                    crbn=crn_names[CrnNames.BASE]):
        ccr_gx_gen_first = CCR_gx_generator(request, msisdn, imsi)
        ccr_gy_gen_first = CCR_gy_generator(request, msisdn, imsi)

        ccr_test_gx = ccr_gx_helper.init_gx(ccr_gx_gen_first, crbn)

        initial_ccr_msg_gy_u_answer = ccr_gy_helper.init_gy(ccr_gy_gen_first, service, custom_configuration=[
            ccr_gy_helper.set_current_date(datetime.datetime.utcnow() + datetime.timedelta(days=day))
        ])

        max_traffic_consumption = ccr_gy_helper.get_max_traffic_consumption(initial_ccr_msg_gy_u_answer)

        with step(f'Потребляем {quota} kb {day} день'):
            uf.traffic_consumption_new(quota * 1024, service, ccr_gy_gen_first, max_traffic_consumption, tc,
                                       date_time=datetime.datetime.utcnow() + datetime.timedelta(days=day),
                                       need_reauth=need_reauth)

        with step('Завершение работы'):
            ccr_gy_helper.terminate_gy(ccr_gy_gen_first)
            ccr_gx_helper.terminate_gx(ccr_gx_gen_first)
