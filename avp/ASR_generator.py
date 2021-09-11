from copy import deepcopy

from avp.BaseGenerator import BaseGenerator
from avp.CER_generator import msg_generator
from helpers.debug_functions import set_avp_value, find_avp_by_name


class ASR_generator:

    @staticmethod
    def make_answer(msg):
        asr_ans = deepcopy(msg)
        asr_ans.clearRequestFlag()
        set_avp_value(asr_ans, 'Origin-Host', find_avp_by_name(asr_ans, 'Destination-Host').getAVPValue())
        set_avp_value(asr_ans, 'Origin-Realm', find_avp_by_name(asr_ans, 'Destination-Realm').getAVPValue())

        BaseGenerator.remover(asr_ans, 'Auth-Application-Id')
        BaseGenerator.remover(asr_ans, 'Destination-Host')
        BaseGenerator.remover(asr_ans, 'Destination-Realm')
        BaseGenerator.remover(asr_ans, 'Abort-Cause')

        asr_ans.getAVPs().append(msg_generator.get_avp('uint', 268, 2001))
        return asr_ans
