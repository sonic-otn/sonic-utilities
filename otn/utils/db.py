import time

from swsscommon import swsscommon
from .constants import *

def connect_muti_db_common(slot_id, db_id):
    slot_idx = int(slot_id)
    if slot_idx == 0:
        redis_unix_socket_path = "/var/run/redis/redis.sock"
    else:
        redis_unix_socket_path = f"/var/run/redis{slot_idx - 1}/redis.sock"
    return swsscommon.DBConnector(db_id, redis_unix_socket_path, 0)

def set_table_field(db,table_name,table_key,field,value):
    table = swsscommon.Table(db, table_name)
    data = [(field, str(value))]
    fvs = swsscommon.FieldValuePairs(data)
    table.set(table_key, fvs)

def set_table_fields(db,table_name,table_key, field_value_touple_list):
    table = swsscommon.Table(db, table_name)
    fvs = swsscommon.FieldValuePairs(field_value_touple_list)
    table.set(table_key, fvs)

def set_table_expire(db,table_name,table_key, expire_time):
    table = swsscommon.Table(db, table_name)
    table.expire(table_key,expire_time)

def del_table_field(db,table_name,table_key,field):
    table = swsscommon.Table(db, table_name)
    table.hdel(table_key, field)

def del_table_key(db, table_name, table_key):
    table = swsscommon.Table(db, table_name)
    table.delete(table_key)

def flush_db_except_table_key(db, table_name, except_key, seperator):
    keys = get_db_keys(db, "*")
    for key in keys:
        if key != table_name + seperator + except_key:
            db.delete(key)

def flush_db_except_table_key_fields(db, table_name, except_key, seperator, fields_list):
    flush_db_except_table_key(db, table_name, except_key, seperator)
    dict_data = get_db_table_fields(db, table_name, except_key)
    for field in dict_data.keys():
        if field not in fields_list:
            del_table_field(db, table_name, except_key, field)

def get_db_table_field(db, table_name, table_key, field_name):
    dict_data = get_db_table_fields(db, table_name, table_key)
    return dict_data.get(field_name, NA_VALUE)    
class rdict(dict):
    def __init__(self, *args, **kwargs):
        self.update(dict(*args, **kwargs))

    #return NA if key not exist   
    def __getitem__(self, key):
        return dict.get(self, key, NA_VALUE)
        
def get_db_table_fields(db, table_name, table_key):
    table = swsscommon.Table(db, table_name)
    err, data = table.get(table_key)
    
    return rdict(data)

def get_db_table_keys(db, table_name):
    table = swsscommon.Table(db, table_name)
    return table.getKeys()

def get_db_keys(db, pattern):
    return db.keys(pattern)

def get_state_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id,DB_STATE_IDX) 

def get_counter_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_COUNTER_IDX) 

def get_config_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_CONFIG_IDX) 

def get_history_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_HISTORY_IDX) 

def get_chassis_state_db():
    return get_state_db_by_slot(0) 

def get_chassis_counter_db():
    return get_counter_db_by_slot(0) 

def get_chassis_config_db():
    return get_config_db_by_slot(0) 

def get_chassis_history_db():
    return get_history_db_by_slot(0) 

def subscribe_channel(db, channel, timeout):
    db_pubsub = db.pubsub()
    db_pubsub.psubscribe(channel)
    idle = 0
    while True and idle < timeout:
        message = db_pubsub.get_message()
        if message:
            if "Failed" in message['data']:
                err_msg = int(message['data'].split(",")[0][2:-1])
                return CONFIG_ERROR,err_msg
            else:
                return 0, ''
        else:
            time.sleep(1)
            idle += 1
    return CONFIG_ERROR, "Configuration timeout!"