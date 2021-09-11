import enum

from pyDiameter.pyDiaMessage import DiaMessage

from avp.BaseGenerator import BaseGenerator
from avp.IpMode import IpMode
from config.global_temp_config import *
from helpers.debug_functions import set_avp_value, find_all_avps_by_name, scan_avp, scan_avp_all, construct_avp


class Mcd(enum.Enum):
    audio = 0
    video = 1


class AAR_rx_generator(BaseGenerator):

    def __init__(self, request, msisdn, imsi, test_called_station_id, ip_mode=IpMode.ipv4, ip='127.0.0.1'):
        super().__init__(request, msisdn, imsi, test_called_station_id)
        self.ip_mode = ip_mode
        self.ip = ip
        self.generator_name = 'rx'

    def init_msg(self):
        # шаблон сообщения
        msg_bytes = 'if u wanna use it, capture a real packet of your mobile operator with wireshark'
        msg = DiaMessage()
        msg.decode(bytes.fromhex(msg_bytes))

        msg.setFlags(0)
        msg.setRequestFlag()
        msg.setProxyableFlag()
        msg.generateHBHID()
        msg.generateE2EID()

        set_avp_value(msg, 'Session-Id', self.session_id)
        set_avp_value(msg, 'Origin-Host', test_origin_host_rx.encode('utf-8'))
        set_avp_value(msg, 'Origin-Realm', test_origin_realm_rx.encode('utf-8'))
        set_avp_value(msg, 'Destination-Host', test_destination_host_rx.encode('utf-8'))
        set_avp_value(msg, 'Destination-Realm', test_destination_realm_rx.encode('utf-8'))
        # RX-INIT
        set_avp_value(msg, 'Rx-Request-Type', 0)

        BaseGenerator.remover(msg, 'Route-Record')
        self.set_subscription_data_volte(msg)
        self.set_ip_mode(msg)

        return msg

    def update_msg(self):
        # шаблон сообщения
        msg_bytes = 'if u wanna use it, capture a real packet of your mobile operator with wireshark'
        msg = DiaMessage()
        msg.decode(bytes.fromhex(msg_bytes))

        msg.setFlags(0)
        msg.setRequestFlag()
        msg.setProxyableFlag()
        msg.generateHBHID()
        msg.generateE2EID()

        set_avp_value(msg, 'Session-Id', self.session_id)
        set_avp_value(msg, 'Origin-Host', test_origin_host_rx.encode('utf-8'))
        set_avp_value(msg, 'Origin-Realm', test_origin_realm_rx.encode('utf-8'))
        set_avp_value(msg, 'Destination-Host', test_destination_host_rx.encode('utf-8'))
        set_avp_value(msg, 'Destination-Realm', test_destination_realm_rx.encode('utf-8'))
        # RX-UPDATE
        set_avp_value(msg, 'Rx-Request-Type', 1)

        BaseGenerator.remover(msg, 'Route-Record')
        self.set_subscription_data_volte(msg)
        self.set_ip_mode(msg)

        return msg

    def terminate_msg(self):
        msg_bytes = 'if u wanna use it, capture a real packet of your mobile operator with wireshark'
        msg = DiaMessage()
        msg.decode(bytes.fromhex(msg_bytes))

        msg.setFlags(0)
        msg.setRequestFlag()
        msg.setProxyableFlag()
        msg.generateHBHID()
        msg.generateE2EID()

        set_avp_value(msg, 'Session-Id', self.session_id)
        set_avp_value(msg, 'Origin-Host', test_origin_host_rx.encode('utf-8'))
        set_avp_value(msg, 'Origin-Realm', test_origin_realm_rx.encode('utf-8'))
        set_avp_value(msg, 'Destination-Host', test_destination_host_rx.encode('utf-8'))
        set_avp_value(msg, 'Destination-Realm', test_destination_realm_rx.encode('utf-8'))
        # RX-TERMINATE
        set_avp_value(msg, 'Rx-Request-Type', 2)

        BaseGenerator.remover(msg, 'Route-Record')
        self.close_session()
        return msg

    def set_ip_mode(self, msg):
        if self.ip_mode == IpMode.ipv6:
            self.remover(msg, 'Framed-IP-Address')
            avp = construct_avp('str', 97, self.ip)
            msg.getAVPs().append(avp)

    def get_audio_video_mcd(self, message):
        MCDs = find_all_avps_by_name(message, "Media-Component-Description")
        mcd_a = None
        mcd_v = None
        for mcd in MCDs:
            mt = scan_avp(mcd, "Media-Type").getAVPValue()
            if mt == 0:
                mcd_a = mcd
            elif mt == 1:
                mcd_v = mcd

        return mcd_a, mcd_v

    def set_flow_status(self, message, status, mcd):  # default значение = 2
        audio, video = self.get_audio_video_mcd(message)
        if mcd is Mcd.audio:
            scan_avp(audio, 'Flow-Status').setAVPValue(status)
        elif mcd is Mcd.video:
            scan_avp(video, 'Flow-Status').setAVPValue(status)

    def set_codecs(self, message, codec_name):
        audio, video = self.get_audio_video_mcd(message)
        codecs = []
        scan_avp_all(audio, "Codec-Data AVP", codecs)
        codecs[0].setAVPValue(b'uplink codec data')
        if codec_name == 'short':
            codecs[1].setAVPValue(b'downlink codec data')
        elif codec_name == 'long':
            codecs[1].setAVPValue(b'downlink codec data')

    def set_subscription_data_volte(self, message):
        data = f"sip:+{self.msisdn}@ims.mnc.mcc.org".encode('utf-8')
        set_avp_value(message, 'Subscription-Id-Data', data)
