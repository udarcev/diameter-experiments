from config import crn_dicts

# Origin / Destination configs
test_origin_host_gx =           'origin.host.gx'
test_origin_host_gy =           'origin.host.gy'
test_origin_host_rx =           'origin.host.rx'

test_origin_realm_gx =          'origin.realm.gx'
test_origin_realm_gy =          'origin.realm.gy'
test_origin_realm_rx =          'origin.realm.rx'

test_destination_host_gx =      'destination.host.gx'
test_destination_host_gy =      'destination.host.gy'
test_destination_host_rx =      'destination.host.rx'

test_destination_realm_gx =     'destination.realm.gx'
test_destination_realm_gy =     'destination.realm.gy'
test_destination_realm_rx =     'destination.realm.rx'

# GX GY endpoints
HOST_GX = '127.0.0.1'
HOST_GY = '127.0.0.1'
HOST_UB = '127.0.0.1'
PORT1 = 13874
PORT2 = 13875
PORT3 = 13876

HOST_VoLTE = '127.0.0.1'
PORT1_VoLTE = 13874
PORT2_VoLTE = 13873

# server_settings
MSG_SIZE = 4096

# requests urls
basic_url_for_soap_requests =   'http://127.0.0.1/soap-api'
url_for_get_v2_profile =        'http://127.0.0.1/v2/'
url_for_get_dao_profile_login = 'http://127.0.0.1/dao/login'
url_for_get_dao_profile =       'http://127.0.0.1/dao'
url_rest =                      'http://127.0.0.1/v2/'

# time for wait CDR seconds
time_wait_cdr = 50

# KAFKA settings
kafka_endpoint = '127.0.0.1:9092'
kafka_topic = 'FIRED-EVENTS'

# MSISDN generator base part
msisdn_starter = '7000000'

current_stand = None

crn_names = crn_dicts.crn_names_sdp
