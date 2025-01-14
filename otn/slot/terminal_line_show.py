import click

from tabulate import tabulate
from otn.utils.utils import *
from otn.utils.pm import *
from otn.slot.terminal_line_command_info import *
from . import terminal_line_upgrade
from otn.slot.terminal_line_utils import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('line'), required=True)
def line(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'line'

@line.command()
@click.pass_context
def module(ctx):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    show_modules_info(slot_id, line_ids)

@line.command()
@click.pass_context
def state(ctx):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    show_modules_state(slot_id, line_ids)

@line.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    show_modules_config(slot_id, line_ids)
    
line.add_command(terminal_line_upgrade.show_upgrade)

#################################### pm ############################################################
@line.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    show_modules_pm_current(slot_id, line_ids, ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    show_modules_pm_history(slot_id, line_ids, ctx.obj['pm_type'], bin_idx)
################################################################################################
def get_line_current_pm_table_key(slot_id, module_id, table_name, pm_field, pm_type):
    if table_name == OTN:
        return f"{get_line_OTU_logical_channel_id(slot_id, module_id)}_{pm_field}:{pm_type}_pm_current"
    else:
        return f"{table_name}-1-{slot_id}-L{module_id}_{pm_field}:{pm_type}_pm_current"

def get_line_history_pm_table_key(slot_id, module_id, table_name, pm_field, pm_type, history_stamp):
    if table_name == OTN:
        return f"{get_line_OTU_logical_channel_id(slot_id, module_id)}_{pm_field}:{pm_type}_pm_history_{history_stamp}"
    else:
        return f"{table_name}-1-{slot_id}-C{module_id}_{pm_field}:{pm_type}_pm_history_{history_stamp}"
   
def show_module_pm_instant(slot_id, module_id, pm_list):
    section_str = ""
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_name = field['Module']
        pm_type = '15'
        table_key = get_line_current_pm_table_key(slot_id, module_id, table_name, field["Field"], pm_type)
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_modules_state(slot_id, module_ids):
    for module_id in module_ids:
        show_module_state(slot_id, module_id)
        show_module_pm_instant(slot_id, module_id, PM_LIST)

def show_module_state(slot_id, module_id):
    db = get_state_db_by_slot(slot_id)
    trans_dict = get_line_transceiver_data(db, slot_id, module_id)
    port_dict = get_line_port_data(db, slot_id, module_id)
    OTU_dict = get_line_OTU_channel_data(db, slot_id, module_id)
    OCH_dict = get_line_OCH_data(db, slot_id, module_id)
    OTN_dict = get_line_OTU_channel_OTN_data(db, slot_id, module_id)
    all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL:OTU_dict, PORT: port_dict, OCH: OCH_dict, OTN: OTN_dict}
    show_key_value_list_with_module(STATE_LIST, all_dict)

def show_modules_info(slot_id, module_ids):
    for module_id in module_ids:
        db = get_state_db_by_slot(slot_id)
        trans_dict = get_line_transceiver_data(db, slot_id, module_id)
        OTU_dict = get_line_OTU_channel_data(db, slot_id, module_id)
        OCH_dict = get_line_OCH_data(db, slot_id, module_id)
        all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL: OTU_dict, OCH: OCH_dict}
        show_key_value_list_with_module(MODULE_LIST, all_dict)
    
def show_modules_config(slot_id, module_ids):
    for module_id in module_ids:
        db = get_config_db_by_slot(slot_id)
        trans_dict = get_line_transceiver_data(db, slot_id, module_id)
        port_dict = get_line_port_data(db, slot_id, module_id)
        OTU_dict = get_line_OTU_channel_data(db, slot_id, module_id)
        OCH_dict = get_line_OCH_data(db, slot_id, module_id)
        OTN_dict = get_line_OTU_channel_OTN_data(db, slot_id, module_id)
        all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL:OTU_dict, PORT: port_dict, OCH: OCH_dict, OTN: OTN_dict}
        show_key_value_list_with_module(CONFIG_LIST, all_dict)

def show_line_pm_current(slot_id, module_id, pm_list, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_name = field['Module']
        table_key = get_line_current_pm_table_key(slot_id, module_id, table_name, field["Field"], pm_type)
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_line_OTU_pm_current(slot_id, module_id, pm_list, pm_type): 
    counter_db = get_counter_db_by_slot(slot_id)
    trans_dict = get_line_transceiver_current_counter_pm(counter_db, slot_id, module_id, pm_type)
    OTU_dict = get_line_OTU_current_counter_pm(counter_db, slot_id, module_id, pm_type)
    OCH_dict = get_line_OCH_current_counter_pm(counter_db, slot_id, module_id, pm_type)
    OTN_dict = get_line_OTN_current_counter_pm(counter_db, slot_id, module_id, pm_type)
    all_dict = {TRANSCEIVER:trans_dict, LOGICAL_CHANNEL: OTU_dict, OCH: OCH_dict, OTN: OTN_dict}
    print(f"<OTUCN-1-{slot_id}-L{module_id}>")
    show_key_value_list_with_module(pm_list, all_dict)

def show_line_OTU_pm_history(slot_id, module_id, pm_list, pm_type, bin_idx): 
    counter_db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    trans_dict = get_line_transceiver_history_counter_pm(counter_db, slot_id, module_id, pm_type, history_stamp)
    OTN_dict = get_line_OTN_history_counter_pm(counter_db, slot_id, module_id, pm_type, history_stamp)
    all_dict = {TRANSCEIVER:trans_dict, OTN: OTN_dict}
    print(f"<OTUCN-1-{slot_id}-L{module_id}>")
    show_key_value_list_with_module(pm_list, all_dict)
           
def show_modules_pm_current(slot_id, module_ids, pm_type):
    for module_id in module_ids:
        show_module_pm_current_head_with_entity(f"PORT-1-{slot_id}-L{module_id}", pm_type)
        show_line_pm_current(slot_id, module_id, PM_LIST, pm_type)
        show_line_OTU_pm_current(slot_id, module_id, OTU_PM_LIST, pm_type) 

def show_line_pm_history(slot_id, module_id, pm_list,pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        table_name = field['Module']
        table_key = get_line_history_pm_table_key(slot_id, module_id, table_name, field["Field"], pm_type, history_stamp)
        pm = get_db_table_fields(db, table_name, table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_modules_pm_history(slot_id, module_ids, pm_type, bin_idx):
    for module_id in module_ids:
        show_module_pm_history_head_with_entity(f"PORT-1-{slot_id}-L{module_id}", pm_type, bin_idx)
        show_line_pm_history(slot_id, module_id, PM_LIST, pm_type, bin_idx)
        show_line_OTU_pm_history(slot_id, module_id, OTU_PM_LIST, pm_type, bin_idx)
