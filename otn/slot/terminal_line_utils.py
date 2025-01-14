from otn.utils.utils import *

admin_dict = {'enable':'ENABLED', 'disable':'DISABLED', 'maintenance': 'MAINT'}
loopback_dict = {'facility':'FACILITY', 'terminal':'TERMINAL', 'none':'NONE'}
prbs_signal_pattern = {
    '2^7': 'PRBS_PATTERN_TYPE_2E7',
    '2^9': 'PRBS_PATTERN_TYPE_2E9',
    '2^15':'PRBS_PATTERN_TYPE_2E15',
    '2^23':'PRBS_PATTERN_TYPE_2E23',
    '2^31':'PRBS_PATTERN_TYPE_2E31',
    '2^11':'PRBS_PATTERN_TYPE_2E11',
    '2^13':'PRBS_PATTERN_TYPE_2E13',
}

def get_line_OTU_logical_channel_id(slot_id, module_id):
    LINE_OTU_OFFSET = 14
    return f"CH{slot_id}{int(module_id) + LINE_OTU_OFFSET}"

def get_line_transceiver_data(db, slot_id, module_id):
    table_name = "TRANSCEIVER"
    table_key = f'{table_name}-1-{slot_id}-L{module_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_line_port_data(db, slot_id, module_id):
    table_name = "PORT"
    table_key = f'{table_name}-1-{slot_id}-L{module_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OTU_channel_data(db, slot_id, module_id):
    table_name = "LOGICAL_CHANNEL"
    channel_id = get_line_OTU_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OCH_data(db, slot_id, module_id):
    table_name = "OCH"
    table_key = f'OCH-1-{slot_id}-L{module_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OTU_channel_OTN_data(db, slot_id, module_id):
    table_name = "OTN"
    channel_id = get_line_OTU_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    return get_db_table_fields(db, table_name, table_key)

def get_line_transceiver_current_counter_pm(db, slot_id, module_id, pm_type):
    table_name = "TRANSCEIVER"
    table_key = f'{table_name}-1-{slot_id}-L{module_id}:{pm_type}_pm_current'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OTU_current_counter_pm(db, slot_id, module_id, pm_type):
    table_name = "LOGICAL_CHANNEL"
    channel_id = get_line_OTU_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}:{pm_type}_pm_current'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OCH_current_counter_pm(db, slot_id, module_id, pm_type):
    table_name = "OCH"
    table_key = f'{table_name}-1-{slot_id}-L{module_id}:{pm_type}_pm_current'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OTN_current_counter_pm(db, slot_id, module_id, pm_type):
    table_name = "OTN"
    channel_id = get_line_OTU_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    table_key = f'{table_key}:{pm_type}_pm_current'
    return get_db_table_fields(db, table_name, table_key)

def get_line_transceiver_history_counter_pm(db, slot_id, module_id, pm_type, history_stamp):
    table_name = "TRANSCEIVER"
    table_key = f'{table_name}-1-{slot_id}-C{module_id}:{pm_type}_pm_history_{history_stamp}'
    return get_db_table_fields(db, table_name, table_key)

def get_line_OTN_history_counter_pm(db, slot_id, module_id, pm_type, history_stamp):
    table_name = "OTN"
    channel_id = get_line_OTU_logical_channel_id(slot_id, module_id)
    table_key = f'{channel_id}'
    table_key = f'{table_key}:{pm_type}_pm_history_{history_stamp}'
    return get_db_table_fields(db, table_name, table_key)