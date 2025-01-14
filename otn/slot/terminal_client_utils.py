from otn.utils.utils import *

admin_dict = {'enable':'ENABLED', 'disable':'DISABLED', 'maintenance': 'MAINT'}
loopback_dict = {'facility':'FACILITY', 'terminal':'TERMINAL', 'none':'NONE'}

def get_client_GE_logical_channel_id(slot_id, module_id):
    return f"CH{slot_id}0{module_id}"

def get_client_ODU_logical_channel_id(slot_id, module_id):
    OTN_CLINET_ODU_OFFSET = 16
    return f"CH{slot_id}{int(module_id) + OTN_CLINET_ODU_OFFSET}"

def get_client_transceiver_data(db, slot_id, module_id):
    table_name = "TRANSCEIVER"
    table_key = f'{table_name}-1-{slot_id}-C{module_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_port_data(db, slot_id, module_id):
    table_name = "PORT"
    table_key = f'{table_name}-1-{slot_id}-C{module_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_GE_channel_data(db, slot_id, module_id):
    table_name = "LOGICAL_CHANNEL"
    channel_id = get_client_GE_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_ODU_channel_OTN_data(db, slot_id, module_id):
    table_name = "OTN"
    channel_id = get_client_ODU_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_GE_channel_ETHERNET_data(db, slot_id, module_id):
    table_name = "ETHERNET"
    channel_id = get_client_GE_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_GE_channel_ETHERNET_rmon(db, slot_id, module_id):
    table_name = "ETHERNET"
    channel_id = get_client_GE_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}:current'
    return get_db_table_fields(db, table_name, table_key)

def get_client_GE_channel_ETHERNET_current_counter_pm(db, slot_id, module_id, pm_type):
    table_name = "ETHERNET"
    channel_id = get_client_GE_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}:{pm_type}_pm_current'
    return get_db_table_fields(db, table_name, table_key)

def get_client_transceiver_current_counter_pm(db, slot_id, module_id, pm_type):
    table_name = "TRANSCEIVER"
    table_key = f'{table_name}-1-{slot_id}-C{module_id}:{pm_type}_pm_current'
    return get_db_table_fields(db, table_name, table_key)

def get_client_GE_channel_ETHERNET_history_counter_pm(db, slot_id, module_id, pm_type, history_stamp):
    table_name = "ETHERNET"
    channel_id = get_client_GE_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}:{pm_type}_pm_history_{history_stamp}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_transceiver_history_counter_pm(db, slot_id, module_id, pm_type, history_stamp):
    table_name = "TRANSCEIVER"
    table_key = f'{table_name}-1-{slot_id}-C{module_id}:{pm_type}_pm_history_{history_stamp}'
    return get_db_table_fields(db, table_name, table_key)

def get_client_GE_channel_LLDP_data(db, slot_id, module_id):
    table_name = "LLDP"
    channel_id = get_client_GE_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    return get_db_table_fields(db, table_name, table_key)