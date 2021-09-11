import datetime
import time

from pyDiameter.pyDiaAVPBasicTypes import DiaAVPStr, DiaAVPInt32, DiaAVPUInt32, DiaAVPUInt64, DiaAVPGroup
from pyDiameter.pyDiaAVPTools import bytes_to_address

from config.global_temp_config import *


def scan_avp(avp, avp_search_name):
    avp_name = avp.getAVPName()
    value = avp.getAVPValue()

    if avp_name == avp_search_name:
        return avp

    if type(value) is list:
        for sub in value:
            sub_avp = scan_avp(sub, avp_search_name)
            if sub_avp:
                return sub_avp
    return None


def find_avp_by_name(msg, avp_name):
    avps = msg.getAVPs()
    for avp in avps:
        avp = scan_avp(avp, avp_name)
        if avp:
            return avp
    return None


def find_avp_by_name_non_recursive(msg, avp_search_name):
    avps = msg.getAVPs()
    for avp in avps:
        avp_name = avp.getAVPName()

        if avp_name == avp_search_name:
            return avp

    return None


def scan_avp_all(avp, avp_search_name, array):
    avp_name = avp.getAVPName()
    value = avp.getAVPValue()

    if avp_name == avp_search_name:
        array.append(avp)

    if type(value) is list and avp not in array:
        for sub in value:
            scan_avp_all(sub, avp_search_name, array)


def find_all_avps_by_name(msg, avp_name):
    res = []
    avps = msg.getAVPs()
    for avp in avps:
        scan_avp_all(avp, avp_name, res)
    return res


def find_all_avps_by_name_non_recursive(msg, avp_search_name):
    res = []
    avps = msg.getAVPs()
    for avp in avps:
        avp_name = avp.getAVPName()

        if avp_name == avp_search_name:
            res.append(avp)

    return res


def set_avp_value(msg, avp_name, value):
    avp = find_avp_by_name(msg, avp_name)
    avp.setAVPValue(value)


# noinspection PyUnboundLocalVariable
def construct_avp(type_avp, code, value, flags=-1, vendor=None):  # type - str int
    if type_avp == 'str':
        avp = DiaAVPStr()
    elif type_avp == 'int':
        avp = DiaAVPInt32()
    elif type_avp == 'uint':
        avp = DiaAVPUInt32()
    elif type_avp == 'uint64':
        avp = DiaAVPUInt64()
    elif type_avp == 'group':
        avp = DiaAVPGroup()

    avp.setAVPCode(code)
    if flags == -1:
        avp.setAVPMandatoryFlag()
    else:
        avp.setAVPFlags(flags)
    if vendor:
        avp.setAVPVendor(vendor)
    avp.setAVPValue(value)
    return avp


def visit_avp(avp, tab=''):
    print(tab, end='')
    print('name:  ', avp.getAVPName())
    print(tab, end='')
    print('type:  ', avp.getAVPType())
    print(tab, end='')
    print('code:  ', avp.getAVPCode())
    print(tab, end='')
    print('flags: ', avp.getAVPFlags())
    print(tab, end='')
    print('len:   ', len(avp))
    value = avp.getAVPValue()
    if avp.getAVPVSFlag():
        print(tab, end='')
        print('vendor:', avp.getAVPVendor())
    if type(value) is list:
        print(tab, end='')
        print('====>')
        for sub in value:
            visit_avp(sub, tab + '    ')
        print(tab, end='')
        print('<====')
    else:
        print(tab, end='')
        print('value: ', value)
        if avp.getAVPName() == "Host-IP-Address":
            print("decoded: ", bytes_to_address(value))
    print(tab, end='')
    print('-------')


def visit_message(msg):
    print('len:   ', len(msg))
    print('flags: ', msg.getFlags())
    print('code:  ', msg.getCommandCode())
    print('app:   ', msg.getApplicationID())
    print('hbh:   ', msg.getHBHID())
    print('e2e:   ', msg.getE2EID())
    avps = msg.getAVPs()
    for avp in avps:
        visit_avp(avp)


session_saver = 0


def generate_session_id(msisdn):
    global session_saver
    res = ";".join([test_origin_host_gy, msisdn, str(int(time.time())), str(session_saver)])
    session_saver += 1
    return res.encode('utf-8')


def get_current_date_parsed(delta_day=0):
    date = datetime.datetime.utcnow() + datetime.timedelta(days=delta_day)
    return {'year': date.year, 'month': date.month, 'day': date.day,
            'hour': date.hour, 'minute': date.minute, 'second': date.second}


def get_date_parsed(date):
    return {'year': date.year, 'month': date.month, 'day': date.day,
            'hour': date.hour, 'minute': date.minute, 'second': date.second}
