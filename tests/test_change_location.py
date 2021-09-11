from allure import step

import helpers.ccr_gy_helper as gy
import helpers.cheats as cheats
import helpers.useful_func as uf
import server.async_server as server
from avp.CCR_gx_generator import CCR_gx_generator
from avp.CCR_gy_generator import CCR_gy_generator
from avp.RAR_generator import RAR_generator
from helpers import ccr_gx_helper, ccr_gy_helper
from tests.common.TestParent import TestParent


class TestChangeLocation(TestParent):

    def test_change_location_between_fr_and_monaco(self, request):
        test_msisdn, test_imsi = uf.get_next_msisdn()
        service_for_traffic = 'generic'

        _3gpp_data_fr = {
            'SGSN-Address': '127.0.0.1',
            '3GPP-User-Location-Info': '0102f81072067206',  # France
            '3GPP-SGSN-MCC-MNC': '20801'
        }

        _3gpp_data_mon = {
            'SGSN-Address': '127.0.0.2',
            '3GPP-User-Location-Info': '0112f201313b42a7',  # Monaco
            '3GPP-SGSN-MCC-MNC': '21210'
        }

        lambdas_fr = [gy.set_sgsn_address(_3gpp_data_fr['SGSN-Address']),
                      gy.set_3gpp_location(_3gpp_data_fr['3GPP-User-Location-Info']),
                      gy.set_3gpp_sgsn_mcc_mnc(_3gpp_data_fr['3GPP-SGSN-MCC-MNC'])]
        lambdas_mon = [gy.set_sgsn_address(_3gpp_data_mon['SGSN-Address']),
                       gy.set_3gpp_location(_3gpp_data_mon['3GPP-User-Location-Info']),
                       gy.set_3gpp_sgsn_mcc_mnc(_3gpp_data_mon['3GPP-SGSN-MCC-MNC'])]

        ccr_gx_gen_first = CCR_gx_generator(request, test_msisdn, test_imsi)
        ccr_gy_gen_first = CCR_gy_generator(request, test_msisdn, test_imsi)

        ccr_gx_helper.init_gx(ccr_gx_gen_first, custom_configuration=[
            ccr_gx_helper.set_3gpp_location(_3gpp_data_fr['3GPP-User-Location-Info']),
            ccr_gx_helper.set_3gpp_sgsn_mcc_mnc(_3gpp_data_fr['3GPP-SGSN-MCC-MNC']),
            ccr_gx_helper.set_charging_an_gw_address(_3gpp_data_fr['SGSN-Address'])
        ])

        initial_ccr_msg_gy_u_answer = ccr_gy_helper.init_gy(ccr_gy_gen_first, service_for_traffic,
                                                            custom_configuration=lambdas_fr)
        max_traffic_consumption = ccr_gy_helper.get_max_traffic_consumption(initial_ccr_msg_gy_u_answer)

        with step(f'Тратим 5 mb трафика в первой локации'):
            uf.traffic_consumption_new(5 * 1024 * 1024, service_for_traffic, ccr_gy_gen_first, max_traffic_consumption,
                                       custom_configuration=lambdas_fr)

        with step('Отправка CCR запроса с новой локацией, триггерами и reporting_reason 6'):
            ccr_msg_gy_u = ccr_gy_gen_first.get_msg_traffic_configurable(0, 0, service_for_traffic, lambdas_mon,
                                                                         reporting_reason=6)
            ccr_gy_gen_first.add_trigger(ccr_msg_gy_u, 1)
            ccr_gy_gen_first.add_trigger(ccr_msg_gy_u, 2)
            ccr_msg_gy_u_answer = server.send_request_and_get_answer(ccr_msg_gy_u, 'gy')

        cheats.easy_rar(RAR_generator, True, False)
        max_traffic_consumption = ccr_gy_helper.get_max_traffic_consumption(ccr_msg_gy_u_answer)

        with step(f'Тратим 3 mb трафика во второй локации'):
            uf.traffic_consumption_new(3 * 1024 * 1024, service_for_traffic, ccr_gy_gen_first, max_traffic_consumption,
                                       custom_configuration=lambdas_mon)

        with step('Завершение сессии в первой локации'):
            ccr_msg_terminate_gy = ccr_gy_gen_first.test_message(terminate=True)
            for configuration in lambdas_fr:
                configuration(ccr_gy_gen_first, ccr_msg_terminate_gy)
            ccr_gy_helper.terminate_gy_with_custom_message(ccr_gy_gen_first, ccr_msg_terminate_gy)
            ccr_gx_helper.terminate_gx(ccr_gx_gen_first)
