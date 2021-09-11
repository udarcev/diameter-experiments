from pyDiameter.pyDiaAVPTools import address_to_bytes
from pyDiameter.pyDiaAVPTypes import *
from pyDiameter.pyDiaMessage import DiaMessage

from config.global_temp_config import *


class msg_generator:

    def __init__(self, command_code, application_id):
        self.msg = DiaMessage()
        self.msg.setRequestFlag()
        self.msg.generateHBHID()
        self.msg.generateE2EID()
        self.msg.setCommandCode(command_code)
        self.msg.setApplicationID(application_id)

    def add_origin_host(self, value, flags=-1):
        origin_host = DiaAVPStr()
        origin_host.setAVPCode(264)
        if flags == -1:
            origin_host.setAVPMandatoryFlag()
        else:
            origin_host.setAVPFlags(flags)
        origin_host.setAVPValue(value)
        self.msg.getAVPs().append(origin_host)
        return self

    def add_origin_realm(self, value, flags=-1):
        origin_realm = DiaAVPStr()
        origin_realm.setAVPCode(296)
        if flags == -1:
            origin_realm.setAVPMandatoryFlag()
        else:
            origin_realm.setAVPFlags(flags)
        origin_realm.setAVPValue(value)
        self.msg.getAVPs().append(origin_realm)
        return self

    def add_vendor_id(self, value, flags=-1):
        vendor_id = DiaAVPUInt32()
        vendor_id.setAVPCode(266)
        if flags == -1:
            vendor_id.setAVPMandatoryFlag()
        else:
            vendor_id.setAVPFlags(flags)
        vendor_id.setAVPValue(value)
        self.msg.getAVPs().append(vendor_id)
        return self

    def add_result_code(self, value, flags=-1):
        result_code = DiaAVPUInt32()
        result_code.setAVPCode(268)
        if flags == -1:
            result_code.setAVPMandatoryFlag()
        else:
            result_code.setAVPFlags(flags)
        result_code.setAVPValue(value)
        self.msg.getAVPs().append(result_code)
        return self

    def add_session_id(self, value, flags=-1):
        session_id = DiaAVPInt32()
        session_id.setAVPCode(263)
        if flags == -1:
            session_id.setAVPMandatoryFlag()
        else:
            session_id.setAVPFlags(flags)
        session_id.setAVPValue(value)
        self.msg.getAVPs().append(session_id)
        return self

    def add_avp(self, type, code, value, flags=-1):
        if type == 'str':
            avp = DiaAVPStr()
        elif type == 'int':
            avp = DiaAVPInt32()
        elif type == 'uint':
            avp = DiaAVPUInt32()
        elif type == 'uint64':
            avp = DiaAVPUInt64()
        elif type == 'group':
            avp = DiaAVPGroup()
        else:
            raise NotImplementedError("Такой тип поля AVP не поддерживается")

        avp.setAVPCode(code)
        if flags == -1:
            avp.setAVPMandatoryFlag()
        else:
            avp.setAVPFlags(flags)
        avp.setAVPValue(value)
        self.msg.getAVPs().append(avp)
        return self

    def add_avp_str(self, code, value, flags=-1):
        return self.add_avp('str', code, value, flags)

    def add_avp_int(self, code, value, flags=-1):
        return self.add_avp('int', code, value, flags)

    def add_avp_uint(self, code, value, flags=-1):
        return self.add_avp('uint', code, value, flags)

    @staticmethod
    def get_avp(type, code, value, flags=-1, vendor=None):
        if type == 'str':
            avp = DiaAVPStr()
        elif type == 'int':
            avp = DiaAVPInt32()
        elif type == 'uint':
            avp = DiaAVPUInt32()
        elif type == 'uint64':
            avp = DiaAVPUInt64()
        elif type == 'group':
            avp = DiaAVPGroup()
        else:
            raise NotImplementedError("Такой тип поля AVP не поддерживается")

        avp.setAVPCode(code)
        if flags == -1:
            avp.setAVPMandatoryFlag()
        else:
            avp.setAVPFlags(flags)
        avp.setAVPValue(value)
        if vendor:
            avp.setAVPVendor(vendor)
        return avp

    def get_message(self):
        return self.msg


def CER_gx_msg(rand_part):
    app_id = 16777238
    auth_msg = msg_generator(257, app_id). \
        add_origin_host((test_origin_host_gx + rand_part).encode('utf-8')). \
        add_origin_realm((test_origin_realm_gx + rand_part).encode('utf-8')). \
        add_avp_int(258, app_id). \
        add_avp_str(257, address_to_bytes(('ipv4', '127.0.0.1'))). \
        add_vendor_id(3). \
        add_avp_str(269, b'Diameter OLC'). \
        add_avp('group', 260, [msg_generator.get_avp('int', 266, 3), msg_generator.get_avp('int', 259, 4)]). \
        get_message()
    return auth_msg


def CER_gy_msg(rand_part):
    app_id = 4
    auth_msg_gy = msg_generator(257, app_id). \
        add_origin_host((test_origin_host_gy + rand_part).encode('utf-8')). \
        add_origin_realm((test_origin_realm_gy + rand_part).encode('utf-8')). \
        add_avp_int(258, app_id). \
        add_avp_str(257, address_to_bytes(('ipv4', '127.0.0.1'))). \
        add_vendor_id(3). \
        add_avp_str(269, b'Diameter OLC'). \
        add_avp('group', 260, [msg_generator.get_avp('int', 266, 3), msg_generator.get_avp('int', 259, 4)]). \
        get_message()
    return auth_msg_gy


def CER_rx_msg(rand_part):
    app_id = 16777236
    auth_msg_gy = msg_generator(257, app_id). \
        add_origin_host((test_origin_host_rx + rand_part).encode('utf-8')). \
        add_origin_realm((test_origin_realm_rx + rand_part).encode('utf-8')). \
        add_avp_int(258, app_id). \
        add_avp_str(257, address_to_bytes(('ipv4', '127.0.0.1'))). \
        add_vendor_id(3). \
        add_avp_str(269, b'Diameter OLC'). \
        add_avp('group', 260, [msg_generator.get_avp('int', 266, 3), msg_generator.get_avp('int', 259, 4)]). \
        get_message()
    return auth_msg_gy
