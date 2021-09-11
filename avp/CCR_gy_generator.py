import copy

from pyDiameter.pyDiaAVPFactory import DiaAVPFactory
from pyDiameter.pyDiaAVPTools import time_to_bytes, address_to_bytes
from pyDiameter.pyDiaMessage import DiaMessage

import config.global_temp_config as gtc
from avp.BaseGenerator import BaseGenerator
from avp.CER_generator import msg_generator
from helpers.debug_functions import find_avp_by_name, get_current_date_parsed, set_avp_value, get_date_parsed, \
    find_all_avps_by_name_non_recursive, scan_avp


class CCR_gy_generator(BaseGenerator):
    # пример msg из wireshark, в ней изменим нужные поля и можно юзать
    # для нового примера берем готовый msg для шаблона, и делаем msg.encode().hex()
    def __init__(self, request, msisdn, imsi, test_called_station='internet.youroperator.ru'):
        super().__init__(request, msisdn, imsi, test_called_station)
        self.example_msg = 'if u wanna use it, capture a real packet of your mobile operator with wireshark'
        self.generator_name = 'gy'
        self.avpFactory = DiaAVPFactory()

    def test_message(self, terminate=False, need_req=True, sgsn_address=0):
        msg = DiaMessage()
        msg.decode(bytes.fromhex(self.example_msg))

        msg.setFlags(0)
        msg.setRequestFlag()
        msg.generateHBHID()
        msg.generateE2EID()

        """ ### msg настройка полей ### """
        set_avp_value(msg, 'Session-Id', self.session_id)
        set_avp_value(msg, 'Origin-Host', gtc.test_origin_host_gy.encode('utf-8'))
        set_avp_value(msg, 'Origin-Realm', gtc.test_origin_realm_gy.encode('utf-8'))
        set_avp_value(msg, 'Destination-Host', gtc.test_destination_host_gy.encode('utf-8'))
        set_avp_value(msg, 'Destination-Realm', gtc.test_destination_realm_gy.encode('utf-8'))

        self.next_cc = self.get_next_cc()
        set_avp_value(msg, 'CC-Request-Type', 1)
        if self.next_cc == 0:
            set_avp_value(msg, 'CC-Request-Type', 1)
            msg.getAVPs().append(msg_generator.get_avp('int', 455, 1))  # Multiple-Services-Indicator
        elif not terminate:
            set_avp_value(msg, 'CC-Request-Type', 2)
            if not need_req:
                MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
                MSCC.getAVPValue().remove(find_avp_by_name(msg, 'Requested-Service-Unit'))
        else:
            set_avp_value(msg, 'CC-Request-Type', 3)
            MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
            MSCC.getAVPValue().remove(find_avp_by_name(msg, 'Requested-Service-Unit'))

        set_avp_value(msg, 'CC-Request-Number', self.next_cc)
        set_avp_value(msg, 'User-Name', str(self.msisdn + '@' + self.test_called_station).encode('utf-8'))
        set_avp_value(msg, 'Event-Timestamp', time_to_bytes(**get_current_date_parsed()))
        set_avp_value(msg, 'Called-Station-Id', self.test_called_station.encode('utf-8'))
        self.set_subscription_data(msg)

        if sgsn_address != 0:
            self.set_sgsn_address(msg, sgsn_address)

        return msg

    def add_mscc(self, msg, service_description, reporting_reason=5):
        MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
        mscc_new = copy.deepcopy(MSCC)
        msg.getAVPs().append(mscc_new)
        msccs = find_all_avps_by_name_non_recursive(msg, 'Multiple-Services-Credit-Control')
        x = 0
        for mscc in msccs:
            service = service_description[x]
            x += 1
            scan_avp(mscc, 'Service-Identifier').setAVPValue(service["service"])
            scan_avp(mscc, 'Rating-Group').setAVPValue(service["service"])

            if self.next_cc >= 1:
                req_avps_1, req_avps_2 = self.__get_traffic_avps(service["_input"],
                                                                 service["_output"],
                                                                 reporting_reason)
                mscc.getAVPValue().append(req_avps_1)
                mscc.getAVPValue().append(req_avps_2)

    def __get_traffic_avps(self, _input, _output, reporting_reason=5):
        req_avps_1 = msg_generator.get_avp('group', 446, [
            msg_generator.get_avp('uint', 420, 0),  # CC-Time
            msg_generator.get_avp('uint64', 412, _input),  # CC-Input-Octets
            msg_generator.get_avp('uint64', 414, _output),  # CC-Output-Octets
            msg_generator.get_avp('uint64', 417, 0),  # CC-Service-Specific-Units
            msg_generator.get_avp('int', 872, reporting_reason, 192, 10415),  # Reporting-Reason
        ])
        req_avps_2 = msg_generator.get_avp('group', 446, [
            msg_generator.get_avp('uint64', 421, _input + _output),  # CC-Total-Octets
            msg_generator.get_avp('int', 872, 0, 192, 10415),  # Reporting-Reason
        ])
        return req_avps_1, req_avps_2

    def add_traffic(self, msg, _input, _output, need_used=True, reporting_reason=5):
        if self.next_cc >= 1 and need_used:
            req_avps_1, req_avps_2 = self.__get_traffic_avps(_input, _output, reporting_reason)
            MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
            MSCC.getAVPValue().append(req_avps_1)
            MSCC.getAVPValue().append(req_avps_2)

    def add_reauth_info(self, msg, reporting_reason=7):
        MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
        MSCC.getAVPValue().append(msg_generator.get_avp('uint', 872, reporting_reason, 192, 10415))

    def add_trigger(self, msg, trigger_value):
        MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
        MSCC.getAVPValue().append(msg_generator.get_avp('group', 1264, [
            msg_generator.get_avp('int', 870, trigger_value, 192, 10415),  #
        ], 192, 10415))

    def set_service(self, msg, new_service):
        set_avp_value(msg, 'Service-Identifier', new_service)
        set_avp_value(msg, 'Rating-Group', new_service)

    # custom_configuration - это массив лямбд или методов, которые надо применить к шаблону сгенерированного сообщения
    # для получения необходимого результата (простой пример - перемещение абонента в другую локацию или дату)
    def get_msg_traffic_configurable(self, input, output, service, custom_configuration=None, reporting_reason=5,
                                     date_time=None, need_used=True, need_reath=False, reath_rep_reason=7,
                                     need_req=True):
        msg = self.test_message(need_req=need_req)
        self.add_traffic(msg, input, output, need_used, reporting_reason)
        self.set_service(msg, service)
        if date_time:
            self.set_current_date(msg, date_time)
        if need_reath:
            self.add_reauth_info(msg, reath_rep_reason)
        if custom_configuration is not None:
            for configuration in custom_configuration:
                configuration(self, msg)
        return msg

    def get_msg_reauth(self):
        msg = self.test_message()
        self.add_reauth_info(msg)
        return msg

    def set_current_date(self, msg, date_to_set):
        set_avp_value(msg, 'Event-Timestamp', time_to_bytes(**get_date_parsed(date_to_set)))

    def set_cc_request_type(self, msg, value):
        set_avp_value(msg, 'CC-Request-Type', value)

    def set_sgsn_address(self, msg, address):
        set_avp_value(msg, 'SGSN-Address', address_to_bytes(('ipv4', address)))

    def add_tariff_change_usage(self, msg, traffic_amount_1, traffic_amount_2, reporting_reason):
        if self.next_cc >= 1:
            req_avps_1 = msg_generator.get_avp('group', 446, [
                msg_generator.get_avp('uint64', 421, traffic_amount_1),  # CC-Total-Octets
                msg_generator.get_avp('int', 872, reporting_reason, 192, 10415),  # Reporting-Reason
                msg_generator.get_avp('int', 452, 0)  # tariff-change-usage
            ])
            req_avps_2 = msg_generator.get_avp('group', 446, [
                msg_generator.get_avp('uint64', 421, traffic_amount_2),  # CC-Total-Octets
                msg_generator.get_avp('int', 872, reporting_reason, 192, 10415),  # Reporting-Reason
                msg_generator.get_avp('int', 452, 1)  # tariff-change-usage
            ])
            MSCC = find_avp_by_name(msg, 'Multiple-Services-Credit-Control')
            MSCC.getAVPValue().append(req_avps_1)
            MSCC.getAVPValue().append(req_avps_2)

    def set_3gpp_location(self, msg, location):
        location = bytes.fromhex(location)
        set_avp_value(msg, '3GPP-User-Location-Info', location)

    def set_3gpp_sgsn_mcc_mnc(self, msg, location):
        location = bytes(location, 'utf-8')
        set_avp_value(msg, '3GPP-SGSN-MCC-MNC', location)

    def set_3gpp_RAT_type(self, msg, rattype):
        set_avp_value(msg, '3GPP-RAT-Type', rattype)

    def set_mnr(self, msg, mnr):
        self.set_3gpp_sgsn_mcc_mnc(msg, mnr.value['3GPP-SGSN-MCC-MNC'])
        self.set_sgsn_address(msg, mnr.value['SGSN-Address'])
        self.set_3gpp_location(msg, mnr.value['3GPP-User-Location-Info'])

    def remove_avp(self, msg, avp_name):
        msg.getAVPs().remove(find_avp_by_name(msg, avp_name))
