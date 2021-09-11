import sys

from helpers.debug_functions import generate_session_id, find_all_avps_by_name, scan_avp, \
    find_all_avps_by_name_non_recursive

generator_dict = {}


class BaseGenerator:
    def __init__(self, request, msisdn, imsi, test_called_station):
        global generator_dict

        self.test_called_station = test_called_station
        self.cc_request_num = -1
        self.msisdn = msisdn
        self.imsi = imsi
        self.session_id = generate_session_id(self.msisdn)
        self.status = True
        self.generator_name = None

        if request.node.name not in generator_dict:
            generator_dict[request.node.name] = []
        generator_dict[request.node.name].append(self)

    def close_session(self):
        self.status = False

    def test_message(self, terminate, need_req):
        pass

    def get_next_cc(self):
        self.cc_request_num += 1
        return self.cc_request_num

    def set_subscription_data(self, msg):
        subscriptions_ids = find_all_avps_by_name(msg, 'Subscription-Id')

        if len(subscriptions_ids) != 2:
            raise AssertionError('Нет обеих нужных AVP')

        tmp_avp = scan_avp(subscriptions_ids[0], 'Subscription-Id-Type')
        if tmp_avp.getAVPValue() == 1:
            imsi_data = subscriptions_ids[0]
            msisdn_data = subscriptions_ids[1]
        else:
            imsi_data = subscriptions_ids[1]
            msisdn_data = subscriptions_ids[0]

        scan_avp(msisdn_data, 'Subscription-Id-Data').setAVPValue(self.msisdn.encode('utf-8'))
        scan_avp(imsi_data, 'Subscription-Id-Data').setAVPValue(self.imsi.encode('utf-8'))

    @staticmethod
    def remover(msg, remove_item):
        try:
            avps = find_all_avps_by_name_non_recursive(msg, remove_item)
            for avp in avps:
                msg.getAVPs().remove(avp)
        except Exception as e:
            print("Remover error", file=sys.stderr)
            print(e, file=sys.stderr)
            pass
