DB_APP_IDX = 0
DB_ASIC_IDX = 1
DB_COUNTER_IDX = 2
DB_CONFIG_IDX = 4
DB_FLEX_COUNTER_IDX = 5
DB_STATE_IDX = 6
DB_HISTORY_IDX = 10

CARD_TYPE_NONE = "NONE"
FLUSH_DB_IDX_LIST = [DB_APP_IDX, DB_ASIC_IDX, DB_COUNTER_IDX, DB_CONFIG_IDX, DB_FLEX_COUNTER_IDX, DB_HISTORY_IDX]

CONFIG_ERROR = 255
CONFIG_TIMEOUT = 120  #configuration timeout in seconds

PM_CYCLE_15M = 15* 60 * 1000 #15 minutes in ms
PM_CYCLE_24H = 24 * 60 * 60 * 1000 # 24 hours in ms

NA_VALUE = "NA"

bool_common_dict = {'enable': 'true', 'disable':'false'}
OSC_INTERFACE={"osc1":"eth0.3","osc2":"eth0.4","osc3":"eth0.5","osc4":"eth0.6"}

FIELD_WITH = 45
NA = 'N/A'
CURALARM = 'CURALARM'
HISALARM = 'HISALARM'
HISEVENT = 'HISEVENT'
OBX1100E_LINECARDS = ['P230C', 'E120C', 'E110C', 'E100C']
LINECARD_IP_PREFIX = '117.103.88.'
CU_IP_INTERNAL = '117.103.88.243'
SYSTIME_LOW = '2000-01-01 0:0:0'
SYSTIME_HIGH = '2038-01-19 0:0:0'

IDLE            =    "IDLE"
DOWNLOADING     =    "DOWNLOADING"
DOWNLOAD_FINISH =    "DOWNLOAD_FINISH"
COMMITING       =    "COMMITING"
COMMIT_FINISH   =    "COMMIT_FINISH"
REBOOTING       =    "REBOOTING"
COMMIT_PAUSE    =    "COMMIT_PAUSE"
ROLLBACKING     =    "ROLLBACKING"
COMMIT_ERROR    =    "COMMIT_ERROR"
REBOOT_ERROR    =    "REBOOT_ERROR"
COMMIT_STOP     =    "COMMIT_STOP"