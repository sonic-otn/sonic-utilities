import time
import sys
from otn.utils.db import *
from otn.utils.pm import *
from tabulate import tabulate

def get_15m_start_end_time(bin_idx=0):
    current_stamp = (time.time()*1000 // PM_CYCLE_15M) * PM_CYCLE_15M
    start_stamp = current_stamp - bin_idx * PM_CYCLE_15M
    starttime = time.strftime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_stamp / 1000)))
    if (bin_idx > 0):
        endtime = start_stamp + PM_CYCLE_15M
        endtime = time.strftime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endtime / 1000)))
        return starttime, endtime
    else:
        endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return starttime, endtime

def get_24h_start_end_time(bin_idx=0):
    current_stamp = (time.time()*1000 // PM_CYCLE_24H) * PM_CYCLE_24H
    start_stamp = current_stamp - bin_idx * PM_CYCLE_24H
    starttime = time.strftime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_stamp / 1000)))
    if (bin_idx > 0):
        endtime = start_stamp + PM_CYCLE_24H
        endtime = time.strftime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endtime / 1000)))
        return starttime, endtime
    else:
        endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return starttime, endtime

def get_pm_history_bin_start_time(pm_type, bin_idx):
    if(pm_type == '24'):
        current_stamp = (time.time()*1000 // PM_CYCLE_24H) * PM_CYCLE_24H
        start_stamp = current_stamp - bin_idx * PM_CYCLE_24H
        return str(int(start_stamp)) + "000000"
    else:
        current_stamp = (time.time()*1000 // PM_CYCLE_15M) * PM_CYCLE_15M
        start_stamp = current_stamp - bin_idx * PM_CYCLE_15M
        return str(int(start_stamp)) + "000000"

def format_timestamp(time_value):
    if time_value != "NA":
        time_stamp = int(time_value)
        time_stame_array = time.localtime(time_stamp / 1000000000)
        return time.strftime("%Y-%m-%d %H:%M:%S", time_stame_array)
    else:
        return time_value
    
def show_entity_pm_current_head(entity_name, pm_type):
    if(pm_type == '24'):
        start_time, end_time = get_24h_start_end_time()
    else:
        start_time, end_time = get_15m_start_end_time()
        
    print(f"     Name: {entity_name}")
    print(f"StartTime: {start_time}")
    print(f"  EndTime: {end_time}")

def show_entity_pm_history_head(entity_name, pm_type, bin_idx):
    if(pm_type == '24'):
        start_time, end_time = get_24h_start_end_time(bin_idx)
    else:
        start_time, end_time = get_15m_start_end_time(bin_idx)
        
    print(f"     Name: {entity_name}")
    print(f"StartTime: {start_time}")
    print(f"  EndTime: {end_time}")
        
def show_module_pm_current_head(slot_id, module_id, table_name, pm_type):
    entity_name = f"{table_name}-1-{slot_id}-{module_id}"
    show_entity_pm_current_head(entity_name, pm_type)

def show_module_pm_current_head_with_entity(entity_name, pm_type):
    show_entity_pm_current_head(entity_name, pm_type)

def show_module_pm_history_head(slot_id, module_id, table_name, pm_type, bin_idx):
    entity_name = f"{table_name}-1-{slot_id}-{module_id}"
    show_entity_pm_history_head(entity_name, pm_type, bin_idx)

def show_module_pm_history_head_with_entity(entity_name, pm_type, bin_idx):
    show_entity_pm_history_head(entity_name, pm_type, bin_idx)
    
def show_module_pm_current(slot_id, module_id, pm_list, table_name, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_key = f"{table_name}-1-{slot_id}-{module_id}_{field['Field']}:{pm_type}_pm_current"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_module_pm_history(slot_id, module_id, pm_list, table_name, pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    db = get_history_db_by_slot(slot_id)
    for field in pm_list:
        table_key = f"{table_name}-1-{slot_id}-{module_id}_{field['Field']}:{pm_type}_pm_history_{history_stamp}"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_slot_pm_current_head(slot_id, table_name, pm_type):
    entity_name = f"{table_name}-1-{slot_id}"
    show_entity_pm_current_head(entity_name, pm_type)

def show_slot_pm_history_head(slot_id, table_name, pm_type, bin_idx):
    entity_name = f"{table_name}-1-{slot_id}"
    show_entity_pm_history_head(entity_name, pm_type, bin_idx)

def show_slot_pm_current(slot_id, pm_list, table_name, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_key = f"{table_name}-1-{slot_id}_{field['Field']}:{pm_type}_pm_current"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_slot_pm_history(slot_id, pm_list, table_name, pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        table_key = f"{table_name}-1-{slot_id}_{field['Field']}:{pm_type}_pm_history_{history_stamp}"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")
    
def show_chassis_pm_current(chassis_id, pm_list, table_name, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_chassis_counter_db()
    for field in pm_list:
        table_key = f"{table_name}-{chassis_id}_{field['Field']}:{pm_type}_pm_current"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_chassis_pm_history(chassis_id, pm_list, table_name, pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_chassis_history_db()
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        table_key = f"{table_name}-{chassis_id}_{field['Field']}:{pm_type}_pm_history_{history_stamp}"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")
    
def show_fan_pm_current(fan_id, pm_list, table_name, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_chassis_counter_db()
    for field in pm_list:
        table_key = f"{table_name}-1-{fan_id}_{field['Field']}:{pm_type}_pm_current"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_fan_pm_history(fan_id, pm_list, table_name, pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_chassis_history_db()
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        table_key = f"{table_name}-1-{fan_id}_{field['Field']}:{pm_type}_pm_history_{history_stamp}"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_psu_pm_current(psu_id, pm_list, table_name, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_chassis_counter_db()
    for field in pm_list:
        table_key = f"{table_name}-1-{psu_id}_{field['Field']}:{pm_type}_pm_current"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_psu_pm_history(psu_id, pm_list, table_name, pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_chassis_history_db()
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        table_key = f"{table_name}-1-{psu_id}_{field['Field']}:{pm_type}_pm_history_{history_stamp}"
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n") 