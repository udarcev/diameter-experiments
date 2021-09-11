from allure import step

import helpers.useful_func as uf
from avp.CCR_gx_generator import CCR_gx_generator
from avp.CCR_gy_generator import CCR_gy_generator
from helpers import ccr_gy_helper, ccr_gx_helper
from tests.common.TestParent import TestParent


class TestConsumption(TestParent):
    def test_traffic_consumption(self, request):
        test_msisdn, test_imsi = uf.get_next_msisdn()
        service_for_traffic = 'generic'

        ccr_gx_gen = CCR_gx_generator(request, test_msisdn, test_imsi)
        ccr_gy_gen = CCR_gy_generator(request, test_msisdn, test_imsi)

        ccr_gx_helper.init_gx(ccr_gx_gen)

        initial_ccr_msg_gy_u_answer = ccr_gy_helper.init_gy(ccr_gy_gen, service_for_traffic)
        max_traffic_consumption = ccr_gy_helper.get_max_traffic_consumption(initial_ccr_msg_gy_u_answer)

        granted = 1024 * 1024  # 1 GB

        with step(f'Тратим {granted} kb трафика'):
            last_msg = uf.traffic_consumption_new(granted * 1024, service_for_traffic, ccr_gy_gen, max_traffic_consumption)
            redirect_page = uf.get_redirect_page(last_msg)
            uf.allure_attach("Страница редиректа", redirect_page)

        with step('Завершение сессии'):
            ccr_gy_helper.terminate_gy(ccr_gy_gen)
            ccr_gx_helper.terminate_gx(ccr_gx_gen)
