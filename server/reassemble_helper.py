from pyDiameter.pyDiaMessage import DiaMessage
from pyDiameter.pyDiaMessageConst import MSG_APPLICATION_ID_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_COMMAND_CODE_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_E2E_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_FLAGS_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_HBH_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_LENGTH_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_VERSION_BUFF_LEN


def decodeMessageHeader(headerBytesBuff):
    p = 0
    version = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_VERSION_BUFF_LEN])
    p += MSG_VERSION_BUFF_LEN
    if 0x01 != version:
        raise RuntimeError("Diameter version is not 1 but", version)

    msg_len = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_LENGTH_BUFF_LEN])
    p += MSG_LENGTH_BUFF_LEN
    flags = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_FLAGS_BUFF_LEN])
    p += MSG_FLAGS_BUFF_LEN
    cmdCode = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_COMMAND_CODE_BUFF_LEN])
    p += MSG_COMMAND_CODE_BUFF_LEN
    appID = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_APPLICATION_ID_BUFF_LEN])
    p += MSG_APPLICATION_ID_BUFF_LEN
    hbhID = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_HBH_BUFF_LEN])
    p += MSG_HBH_BUFF_LEN
    e2eID = DiaMessage.decodeUIntValue(headerBytesBuff[p:p + MSG_E2E_BUFF_LEN])

    return msg_len
