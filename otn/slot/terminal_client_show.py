import click

from tabulate import tabulate
from otn.utils.utils import *
from otn.utils.pm import *
from otn.slot.terminal_client_command_info import *
from otn.slot.terminal_client_utils import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('client'), required=True)
def client(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'client'

@client.command()
@click.pass_context
def module(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_info(slot_id, client_ids)

@client.command()
@click.pass_context
def state(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_state(slot_id, client_ids)

@client.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_config(slot_id, client_ids)

@client.command()
@click.pass_context
def lldp(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_lldp(slot_id, client_ids)

@client.command()
@click.pass_context
def rmon(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_rmon(slot_id, client_ids)

#################################### pm ############################################################
@client.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_pm_current(slot_id, client_ids, ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    show_modules_pm_history(slot_id, client_ids, ctx.obj['pm_type'], bin_idx)
################################################################################################
def get_client_current_pm_table_key(slot_id, module_id, table_name, pm_field, pm_type):
    if table_name == OTN:
        return f"{get_client_ODU_logical_channel_id(slot_id, module_id)}_{pm_field}:{pm_type}_pm_current"
    else:
        return f"{table_name}-1-{slot_id}-C{module_id}_{pm_field}:{pm_type}_pm_current"

def get_client_history_pm_table_key(slot_id, module_id, table_name, pm_field, pm_type, history_stamp):
    if table_name == OTN:
        return f"{get_client_ODU_logical_channel_id(slot_id, module_id)}_{pm_field}:{pm_type}_pm_history_{history_stamp}"
    else:
        return f"{table_name}-1-{slot_id}-C{module_id}_{pm_field}:{pm_type}_pm_history_{history_stamp}"

def get_client_lane_current_pm_table_key(slot_id, module_id, lane_id, table_name, pm_field, pm_type):
    return f"{table_name}-1-{slot_id}-C{module_id}:CH-{lane_id}_{pm_field}:{pm_type}_pm_current"

def get_client_lane_history_pm_table_key(slot_id, module_id, lane_id, table_name, pm_field, pm_type, history_stamp):
    return f"{table_name}-1-{slot_id}-C{module_id}:CH-{lane_id}_{pm_field}:{pm_type}_pm_history_{history_stamp}"
    
def show_module_pm_instant(slot_id, module_id, pm_list):
    section_str = ""
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_name = field['Module']
        pm_type = '15'
        table_key = get_client_current_pm_table_key(slot_id, module_id, table_name, field["Field"], pm_type)
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_client_lane_pm_instant(slot_id, module_id, lane_pm_list):
    section_str = ""
    db = get_counter_db_by_slot(slot_id)
    for lane_id in range(1, CLIENT_LANE_NUM + 1):
        section_str +=f"<Lane-{lane_id}>\n"
        for field in lane_pm_list:
            table_name = field['Module']
            pm_type = '15'
            table_key = get_client_lane_current_pm_table_key(slot_id, module_id, lane_id, table_name, field["Field"], pm_type)
            value = get_pm_instant(db, table_name, table_key)
            key = field['show_name']
            section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_modules_state(slot_id, module_ids):
    for module_id in module_ids:
        show_module_state(slot_id, module_id)
        show_module_pm_instant(slot_id, module_id, PM_LIST)
        show_client_lane_pm_instant(slot_id, module_id, LANE_PM_LIST)

def show_module_state(slot_id, module_id):
    db = get_state_db_by_slot(slot_id)
    trans_dict = get_client_transceiver_data(db, slot_id, module_id)
    GE_dict = get_client_GE_channel_data(db, slot_id, module_id)
    port_dict = get_client_port_data(db, slot_id, module_id)
    OTN_dict = get_client_ODU_channel_OTN_data(db, slot_id, module_id)
    Eth_dict = get_client_GE_channel_ETHERNET_data(db, slot_id, module_id)
    LLDP_dict = get_client_GE_channel_LLDP_data(db, slot_id, module_id)
    all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL:GE_dict, PORT: port_dict, OTN:OTN_dict, ETHERNET:Eth_dict, LLDP:LLDP_dict}
    show_key_value_list_with_module(STATE_LIST, all_dict)

def show_modules_lldp(slot_id, module_ids):
    for module_id in module_ids:
        show_module_lldp(slot_id, module_id)
        
def show_module_lldp(slot_id, module_id):
    db = get_state_db_by_slot(slot_id)
    GE_dict = get_client_GE_channel_data(db, slot_id, module_id)
    LLDP_dict = get_client_GE_channel_LLDP_data(db, slot_id, module_id)
    all_dict = {LOGICAL_CHANNEL:GE_dict, LLDP: LLDP_dict}
    show_key_value_list_with_module(LLDP_LIST, all_dict)

def show_modules_rmon(slot_id, module_ids):
    for module_id in module_ids:
        show_module_rmon(slot_id, module_id)
        
def show_module_rmon(slot_id, module_id):
    counter_db = get_counter_db_by_slot(slot_id)
    state_db = get_state_db_by_slot(slot_id)
    GE_dict = get_client_GE_channel_data(state_db, slot_id, module_id)
    ETHERNET_dict = get_client_GE_channel_ETHERNET_rmon(counter_db, slot_id, module_id)
    all_dict = {LOGICAL_CHANNEL:GE_dict, ETHERNET: ETHERNET_dict}
    show_key_value_list_with_module(RMON_LIST, all_dict)

def show_modules_info(slot_id, module_ids):
    for module_id in module_ids:
        db = get_state_db_by_slot(slot_id)
        trans_dict = get_client_transceiver_data(db, slot_id, module_id)
        GE_dict = get_client_GE_channel_data(db, slot_id, module_id)
        all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL:GE_dict}
        show_key_value_list_with_module(MODULE_LIST, all_dict)
    
def show_modules_config(slot_id, module_ids):
    for module_id in module_ids:
        db = get_config_db_by_slot(slot_id)
        trans_dict = get_client_transceiver_data(db, slot_id, module_id)
        GE_dict = get_client_GE_channel_data(db, slot_id, module_id)
        OTN_dict = get_client_ODU_channel_OTN_data(db, slot_id, module_id)
        Eth_dict = get_client_GE_channel_ETHERNET_data(db, slot_id, module_id)
        LLDP_dict = get_client_GE_channel_LLDP_data(db, slot_id, module_id)
        all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL:GE_dict, OTN:OTN_dict, ETHERNET:Eth_dict, LLDP:LLDP_dict}
        show_key_value_list_with_module(CONFIG_LIST, all_dict)

def show_client_pm_current(slot_id, module_id, pm_list, lane_pm_list, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_name = field['Module']
        table_key = get_client_current_pm_table_key(slot_id, module_id, table_name, field["Field"], pm_type)
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    
    for lane_id in range(1, CLIENT_LANE_NUM + 1):
        pm_table.append([f"<Lane-{lane_id}>"])
        for field in lane_pm_list:
            table_name = field['Module']
            table_key = get_client_lane_current_pm_table_key(slot_id, module_id, lane_id, table_name, field["Field"], pm_type)
            pm = get_db_table_fields(db, table_name, table_key)
            key = field['show_name']
            pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_client_GE_pm_current(slot_id, module_id, pm_list, pm_type): 
    counter_db = get_counter_db_by_slot(slot_id)
    trans_dict = get_client_transceiver_current_counter_pm(counter_db, slot_id, module_id, pm_type)
    ETHERNET_dict = get_client_GE_channel_ETHERNET_current_counter_pm(counter_db, slot_id, module_id, pm_type)
    all_dict = {TRANSCEIVER:trans_dict, ETHERNET: ETHERNET_dict}
    print(f"<GE-1-{slot_id}-C{module_id}>")
    show_key_value_list_with_module(pm_list, all_dict)

def show_client_GE_pm_history(slot_id, module_id, pm_list, pm_type, bin_idx): 
    counter_db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    trans_dict = get_client_transceiver_history_counter_pm(counter_db, slot_id, module_id, pm_type, history_stamp)
    ETHERNET_dict = get_client_GE_channel_ETHERNET_history_counter_pm(counter_db, slot_id, module_id, pm_type, history_stamp)
    all_dict = {TRANSCEIVER:trans_dict, ETHERNET: ETHERNET_dict}
    print(f"<GE-1-{slot_id}-C{module_id}>")
    show_key_value_list_with_module(pm_list, all_dict)
           
def show_modules_pm_current(slot_id, module_ids, pm_type):
    for module_id in module_ids:
        show_module_pm_current_head_with_entity(f"PORT-1-{slot_id}-C{module_id}", pm_type)
        show_client_pm_current(slot_id, module_id, PM_LIST, LANE_PM_LIST, pm_type)
        show_client_GE_pm_current(slot_id, module_id, GE_PM_LIST, pm_type) 

def show_client_pm_history(slot_id, module_id, pm_list, lane_pm_list,pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        table_name = field['Module']
        table_key = get_client_history_pm_table_key(slot_id, module_id, table_name, field["Field"], pm_type, history_stamp)
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    
    for lane_id in range(1, CLIENT_LANE_NUM + 1):
        pm_table.append([f"<Lane-{lane_id}>"])
        for field in lane_pm_list:
            table_name = field['Module']
            table_key = get_client_lane_history_pm_table_key(slot_id, module_id, lane_id, table_name, field["Field"], pm_type, history_stamp)
            pm = get_db_table_fields(db, table_name, table_key)
            key = field['show_name']
            pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_modules_pm_history(slot_id, module_ids, pm_type, bin_idx):
    for module_id in module_ids:
        show_module_pm_history_head_with_entity(f"PORT-1-{slot_id}-C{module_id}", pm_type, bin_idx)
        show_client_pm_history(slot_id, module_id, PM_LIST, LANE_PM_LIST, pm_type, bin_idx)
        show_client_GE_pm_history(slot_id, module_id, GE_PM_LIST, pm_type, bin_idx)
