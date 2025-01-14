import click
import uuid
from otn.utils.db import *
from otn.utils.utils import is_slot_present, log, get_linecard_slot_range, run_command

def set_slot_synchronized_save(slot_id,table_name,table_key,table_field,value):
    if not is_slot_present(slot_id):
        set_slot_configuration_save(slot_id,table_name,table_key,table_field,value)
    else:
        set_slot_configuration_sync(slot_id,table_name,table_key,table_field,value)    

def set_chassis_configuration_save(table_name,table_key,table_field,value):
    cfg_db = get_chassis_config_db()
    set_table_field(cfg_db, table_name,table_key,table_field,value)
    config_save(0)

def set_chassis_multi_configuration_save(table_name,table_key,field_value_touple_list):
    cfg_db = get_chassis_config_db()
    set_table_fields(cfg_db, table_name,table_key,field_value_touple_list)
    config_save(0)

def delete_chassis_configuration_save(table_name,table_key):
    cfg_db = get_chassis_config_db()
    del_table_key(cfg_db, table_name,table_key)
    config_save(0)
     
def set_slot_configuration_save(slot_id,table_name,table_key,table_field,value):
    cfg_db = get_config_db_by_slot(slot_id)
    set_table_field(cfg_db, table_name,table_key,table_field,value)
    config_save(slot_id)

def set_slot_configuration_sync(slot_id,table_name,table_key,table_field,value):
    cfg_db = get_config_db_by_slot(slot_id)
    
    uuid_value = str(uuid.uuid1())
    old_value = get_db_table_field(cfg_db, table_name,table_key,table_field)
    
    field_value_touple_list = [(table_field, str(value)), ('operation-id', uuid_value)]
    set_table_fields(cfg_db, table_name,table_key,field_value_touple_list)
    
    response_channel = table_field + "-" + uuid_value
    err, msg = subscribe_channel(cfg_db,response_channel,CONFIG_TIMEOUT)
    if err != 0:
        print(f"Failed, error msg: {msg}")
        log.log_info(f"Failed, error msg: {msg}, table_name: {table_name}, table_field: {table_field}, table_key: {table_key}, uuid: {uuid_value}, value: {value}")
        rollback_configuration(slot_id,table_name,table_key,table_field, old_value)
    else:
        config_save(slot_id)
        log.log_info(f"Succeeded, error msg: {msg}, table_name: {table_name}, table_field: {table_field}, table_key: {table_key}, uuid: {uuid_value}, value: {value}")

def rollback_configuration(db,table_name,table_key,table_field, old_value):
    if old_value == NA_VALUE:
        del_table_field(db,table_name,table_key,table_field)
    else:
        set_table_field(db, table_name,table_key,table_field,old_value)
  
def config_save(slot_id = 0):
    SLOTS_DEFAULT_CONFIG_DB_FILE = '/etc/sonic/config_db{}.json'
    HOST_DEFAULT_CONFIG_DB_FILE = '/etc/sonic/config_db.json'
    SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
    try:
        if slot_id in get_linecard_slot_range():
            db_id = slot_id - 1
            command = "sudo {} -n asic{} -d --print-data > {}".format(SONIC_CFGGEN_PATH,db_id, SLOTS_DEFAULT_CONFIG_DB_FILE.format(db_id))
        else:
            command = "sudo {} -d --print-data > {}".format(SONIC_CFGGEN_PATH, HOST_DEFAULT_CONFIG_DB_FILE)
        run_command(command)
    except Exception as e:
        click.echo(e)
        

