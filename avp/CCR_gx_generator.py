from pyDiameter.pyDiaAVPTools import address_to_bytes
from pyDiameter.pyDiaMessage import DiaMessage

import helpers.debug_functions as df
from avp.BaseGenerator import BaseGenerator
from config.global_temp_config import *


class CCR_gx_generator(BaseGenerator):
    def __init__(self, request, msisdn, imsi, test_called_station='internet.youroperator.ru'):
        super().__init__(request, msisdn, imsi, test_called_station)
        self.generator_name = 'gx'

    def test_message(self, terminate=False, crr=False):
        msg_bytes = 'if u wanna use it, capture a real packet of your mobile operator with wireshark'
        msg = DiaMessage()
        msg.decode(bytes.fromhex(msg_bytes))

        msg.setFlags(0)
        msg.setRequestFlag()
        msg.setProxyableFlag()
        msg.generateHBHID()
        msg.generateE2EID()

        df.set_avp_value(msg, 'Session-Id', self.session_id)
        df.set_avp_value(msg, 'Origin-Host', test_origin_host_gx.encode('utf-8'))
        df.set_avp_value(msg, 'Origin-Realm', test_origin_realm_gx.encode('utf-8'))
        df.set_avp_value(msg, 'Destination-Host', test_destination_host_gx.encode('utf-8'))
        df.set_avp_value(msg, 'Destination-Realm', test_destination_realm_gx.encode('utf-8'))
        df.set_avp_value(msg, 'Called-Station-Id', self.test_called_station.encode('utf-8'))

        next_cc = self.get_next_cc()
        if next_cc == 0:
            df.set_avp_value(msg, 'CC-Request-Type', 1)
        elif not terminate:
            df.set_avp_value(msg, 'CC-Request-Type', 2)
        else:
            df.set_avp_value(msg, 'CC-Request-Type', 3)

        df.set_avp_value(msg, 'CC-Request-Number', next_cc)
        self.set_subscription_data(msg)

        return msg

    @staticmethod
    def set_charging_rule_report(msg, error_value, injector):
        df.set_avp_value(msg, 'Charging-Rule-Name', injector)
        df.set_avp_value(msg, 'Rule-Failure-Code', error_value)

    @staticmethod
    def set_3gpp_location(msg, location):
        location = bytes.fromhex(location)
        df.set_avp_value(msg, '3GPP-User-Location-Info', location)

    @staticmethod
    def set_imei(msg, imei):
        df.set_avp_value(msg, 'User-Equipment-Info-Value', imei.encode('utf-8'))

    @staticmethod
    def set_3gpp_sgsn_mcc_mnc(msg, location):
        location = bytes(location, 'utf-8')
        df.set_avp_value(msg, '3GPP-SGSN-MCC-MNC', location)

    @staticmethod
    def set_charging_an_gw_address(msg, address):
        df.set_avp_value(msg, 'AN-GW-Address', address_to_bytes(('ipv4', address)))

    @staticmethod
    def set_rat_type(msg, rat_type):
        df.set_avp_value(msg, 'RAT-Type', rat_type)

    @staticmethod
    def set_mnr(msg, mnr):
        CCR_gx_generator.set_3gpp_sgsn_mcc_mnc(msg, mnr.value['3GPP-SGSN-MCC-MNC'])
        CCR_gx_generator.set_charging_an_gw_address(msg, mnr.value['SGSN-Address'])
        CCR_gx_generator.set_3gpp_location(msg, mnr.value['3GPP-User-Location-Info'])

    @staticmethod
    def add_5g_avps_in_qos_information(msg, type_extend, value):
        if type_extend == 'Extended-APN-AMBR':
            dl = df.construct_avp('uint', 2848, value, 192, 10415)
            ul = df.construct_avp('uint', 2849, value, 192, 10415)
        elif type_extend == 'Extended-Max-Requested-BW':
            dl = df.construct_avp('uint', 554, value, 192, 10415)
            ul = df.construct_avp('uint', 555, value, 192, 10415)
        elif type_extend == 'Extended-GBR':
            dl = df.construct_avp('uint', 2850, value, 192, 10415)
            ul = df.construct_avp('uint', 2851, value, 192, 10415)
        else:
            raise AssertionError("Выберите правильный type_extend")
        qos_information = df.find_avp_by_name(msg, 'QoS-Information')

        if qos_information:
            qos_information.addAVP(dl)
            qos_information.addAVP(ul)

    @staticmethod
    def add_5g_avps_supported_features(msg):
        vendor_id = df.construct_avp('int', 266, 10415, 64)
        feature_list_id = df.construct_avp('uint', 629, 2, 128, 10415)
        feature_list = df.construct_avp('uint', 630, 128, 128, 10415)
        sf = df.construct_avp('group', 628, [vendor_id, feature_list_id, feature_list], 192, 10415)
        msg.getAVPs().append(sf)

    @staticmethod
    def add_event_trigger(msg, trigger_value):
        et = df.construct_avp('uint', 1006, trigger_value, 192, 10415)
        msg.getAVPs().append(et)
