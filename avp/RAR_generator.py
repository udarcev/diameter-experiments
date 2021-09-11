from copy import deepcopy

from pyDiameter.pyDiaAVPTools import address_to_bytes

from avp.BaseGenerator import BaseGenerator
from avp.CER_generator import msg_generator
from helpers.debug_functions import set_avp_value, find_avp_by_name


class RAR_generator:

    @staticmethod
    def make_rar_answer_gy(msg, status=2001):
        rar_ans = deepcopy(msg)
        rar_ans.clearRequestFlag()
        set_avp_value(rar_ans, 'Origin-Host', find_avp_by_name(rar_ans, 'Destination-Host').getAVPValue())
        set_avp_value(rar_ans, 'Origin-Realm', find_avp_by_name(rar_ans, 'Destination-Realm').getAVPValue())

        BaseGenerator.remover(rar_ans, 'Destination-Host')
        BaseGenerator.remover(rar_ans, 'Destination-Realm')
        BaseGenerator.remover(rar_ans, 'Session-Id')
        BaseGenerator.remover(rar_ans, 'Origin-State-Id')
        BaseGenerator.remover(rar_ans, 'Re-Auth-Request-Type')
        BaseGenerator.remover(rar_ans, 'Auth-Application-Id')

        rar_ans.getAVPs().append(msg_generator.get_avp('uint', 268, status))  # DIAMETER LIMITED SUCCESS by default
        return rar_ans

    @staticmethod
    def make_rar_answer_gx(msg, status=2001):
        rar_ans = deepcopy(msg)
        rar_ans.clearRequestFlag()
        set_avp_value(rar_ans, 'Origin-Host', find_avp_by_name(rar_ans, 'Destination-Host').getAVPValue())
        set_avp_value(rar_ans, 'Origin-Realm', find_avp_by_name(rar_ans, 'Destination-Realm').getAVPValue())

        BaseGenerator.remover(rar_ans, 'Destination-Host')
        BaseGenerator.remover(rar_ans, 'Destination-Realm')
        BaseGenerator.remover(rar_ans, 'Re-Auth-Request-Type')
        BaseGenerator.remover(rar_ans, 'Auth-Application-Id')
        BaseGenerator.remover(rar_ans, 'QoS-Information')
        BaseGenerator.remover(rar_ans, 'Default-EPS-Bearer-QoS')
        BaseGenerator.remover(rar_ans, 'Charging-Rule-Install')
        BaseGenerator.remover(rar_ans, 'Charging-Rule-Remove')

        rar_ans.getAVPs().append(msg_generator.get_avp('uint', 268, status))  # DIAMETER SUCCESS
        rar_ans.getAVPs().append(
            msg_generator.get_avp('str', 501, address_to_bytes(('ipv4', '127.0.0.1')), 0xc0, 10415)
        )
        rar_ans.getAVPs().append(msg_generator.get_avp('uint', 278, 1506120265))

        return rar_ans

    @staticmethod
    def make_rar_answer_rx(msg, status=2001):
        rar_ans = deepcopy(msg)
        rar_ans.clearRequestFlag()
        set_avp_value(rar_ans, 'Origin-Host', find_avp_by_name(rar_ans, 'Destination-Host').getAVPValue())
        set_avp_value(rar_ans, 'Origin-Realm', find_avp_by_name(rar_ans, 'Destination-Realm').getAVPValue())

        BaseGenerator.remover(rar_ans, 'Destination-Host')
        BaseGenerator.remover(rar_ans, 'Destination-Realm')
        BaseGenerator.remover(rar_ans, 'Auth-Application-Id')
        BaseGenerator.remover(rar_ans, 'Specific-Action')
        BaseGenerator.remover(rar_ans, '3GPP-User-Location-Info')
        BaseGenerator.remover(rar_ans, '3GPP-MS-TimeZone')

        rar_ans.getAVPs().append(msg_generator.get_avp('uint', 268, status))  # DIAMETER SUCCESS

        return rar_ans
