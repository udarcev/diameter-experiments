from enum import Enum


class CrnNames(Enum):
    BASE = 1
    BASE_2048_2048 = 2
    GENERIC_16_16 = 4
    GENERIC_32_32 = 5
    GENERIC_64_64 = 6
    GENERIC_128_128 = 7


crn_names_sdp = {
    CrnNames.BASE: b'BASE',
    CrnNames.BASE_2048_2048: b'BASE_2048_2048',
    CrnNames.GENERIC_16_16: b'GENERIC_16_16',
    CrnNames.GENERIC_32_32: b'GENERIC_32_32',
    CrnNames.GENERIC_64_64: b'GENERIC_64_64',
    CrnNames.GENERIC_128_128: b'GENERIC_128_128',
}
