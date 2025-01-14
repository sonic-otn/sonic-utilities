import click

from tabulate import tabulate
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.utils.pm import *

IN = "IN"
OUT = "OUT"

@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('port'), required=True)
def port(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'port'

@port.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    ports = get_module_ids(ctx)
    show_ports_info(slot_id, ports)

@port.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    ports = get_module_ids(ctx)
    show_ports_config(slot_id, ports)
#################################### pm ############################################################
@port.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    ports = get_module_ids(ctx)
    show_ports_pm_current(slot_id, ports, ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    ports = get_module_ids(ctx)
    show_ports_pm_history(slot_id, ports, ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("port")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('client_port'), required=True)
def cfg_port(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'client_port'

@cfg_port.group()
@click.pass_context
def input(ctx):
    pass

@input.command('low-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_low_threshold'),required=True)
@click.pass_context
def low_alarm_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    port_ids = get_module_ids(ctx)
    config_ports(slot_id, port_ids, 'low-threshold',threshold)

@input.command('high-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_high_threshold'),required=True)
@click.pass_context
def high_alarm_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    port_ids = get_module_ids(ctx)
    config_ports(slot_id, port_ids, 'high-threshold',threshold)
    
@input.command('los-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_los_threshold'),required=True)
@click.pass_context
def high_alarm_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    port_ids = get_module_ids(ctx)
    config_ports(slot_id, port_ids, 'los-threshold',threshold)
################################################################################################
def show_ports_info(slot_id, ports):
    for port in ports:
        show_port_info_data(slot_id, port, STATE_LIST)
        show_port_pm_instant(slot_id, port, PM_LIST)

def show_ports_config(slot_id, ports):
    for port in ports:
        show_port_config_data(slot_id, port, CONFIG_LIST)
        
def show_port_info_data(slot_id, port, state_list):
    db = get_state_db_by_slot(slot_id)
    port_in_dict = get_port_data(db, slot_id, port, IN)
    port_out_dict = get_port_data(db, slot_id, port, OUT)
    all_dict = {IN:port_in_dict, OUT:port_out_dict}
    click.echo("Name".ljust(FIELD_WITH)+ ": "+ f'PORT-1-{slot_id}-{port.upper()}')
    show_key_value_list_with_direction(state_list, all_dict)

def show_port_config_data(slot_id, port, state_list):
    db = get_config_db_by_slot(slot_id)
    port_in_dict = get_port_data(db, slot_id, port, IN)
    port_out_dict = get_port_data(db, slot_id, port, OUT)
    all_dict = {IN:port_in_dict, OUT:port_out_dict}
    click.echo("Name".ljust(FIELD_WITH)+ ": "+ f'PORT-1-{slot_id}-{port.upper()}')
    show_key_value_list_with_direction(state_list, all_dict)

def get_port_data(db, slot_id, port, direction):
    table_name = "PORT"
    port = port.upper()
    table_key = f'{table_name}-1-{slot_id}-{port}{direction}'
    return get_db_table_fields(db, table_name, table_key)

def show_ports_pm_current(slot_id, ports, pm_type):
    for port in ports:
        show_module_pm_current_head_with_entity(f"PORT-1-{slot_id}-{port}", pm_type)
        show_port_pm_current(slot_id, port, PM_LIST, pm_type)

def show_port_pm_current(slot_id, port, pm_list, pm_type):
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        direction = field['Direction']
        full_name = (port + direction).upper()
        table_key = get_port_current_pm_table_key(slot_id, full_name, field["Field"], pm_type)
        pm = get_db_table_fields(db, "PORT", table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")    

def show_ports_pm_history(slot_id, ports, pm_type, bin_idx):
    for port in ports:
        show_module_pm_history_head_with_entity(f"PORT-1-{slot_id}-{port}", pm_type, bin_idx)
        show_port_pm_history(slot_id, port, PM_LIST, pm_type, bin_idx)

def get_port_current_pm_table_key(slot_id, port, pm_field, pm_type):
    return f"PORT-1-{slot_id}-{port}_{pm_field}:{pm_type}_pm_current"

def get_port_history_pm_table_key(slot_id, port, pm_field, pm_type, history_stamp):
    return f"PORT-1-{slot_id}-{port}_{pm_field}:{pm_type}_pm_history_{history_stamp}"

def show_port_pm_history(slot_id, module_id, pm_list,pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for field in pm_list:
        direction = field['Direction']
        full_name = (module_id + direction).upper()
        table_key = get_port_history_pm_table_key(slot_id, full_name, field["Field"], pm_type, history_stamp)
        pm = get_db_table_fields(db, "PORT", table_key)
        key = field['show_name']
        pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_port_pm_instant(slot_id, port, pm_list):
    section_str = ""
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        direction = field['Direction']
        full_name = (port + direction).upper()
        pm_type = '15'
        table_key = get_port_current_pm_table_key(slot_id, full_name, field["Field"], pm_type)
        value = get_pm_instant(db, "PORT", table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_key_value_list_with_direction(target_list, dict_kvs):
    section_str = ""
    for field in target_list:
        field_name = field['Field']
        dirction = field['Direction']
        if dirction in dict_kvs:
            value = dict_kvs[dirction][field_name]
            section_str += field['show_name'].ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def config_port_RX(slot_id, port_id, field, value):
    table_name = 'PORT'
    table_key = f'PORT-1-{slot_id}-{port_id}IN'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)
    click.echo('Succeeded')

def config_ports(slot_id, port_ids, field, value):
    for port_id in port_ids:
        config_port_RX(slot_id, port_id, field,value)      

STATE_LIST = [
    {'Direction': IN,         'Field': 'oper-status',                      'show_name': 'Oper Status'},
    {'Direction': IN,         'Field': 'los-threshold',                    'show_name': 'LOS Threshold'},
    {'Direction': IN,         'Field': 'low-threshold',                    'show_name': 'LOW Threshold'},
    {'Direction': IN,         'Field': 'high-threshold',                   'show_name': 'High Threshold'},
    {'Direction': IN,         'Field': 'led-color',                        'show_name': 'Alarm Led State'},
]

CONFIG_LIST = [
    {'Direction': IN,         'Field': 'los-threshold',                    'show_name': 'LOS Threshold'},
    {'Direction': IN,         'Field': 'low-threshold',                    'show_name': 'LOW Threshold'},
    {'Direction': IN,         'Field': 'high-threshold',                   'show_name': 'High Threshold'},
]

PM_LIST = [
    {'Direction': IN,           'Field': 'InputPower',                 'show_name': 'InputPower(dBm)'},
    {'Direction': OUT,          'Field': 'OutputPower',                'show_name': 'OutputPower(dBm)'},
    {'Direction': IN,           'Field': 'OSC_InputPower',             'show_name': 'OSC InputPower(dBm)'},
    {'Direction': OUT,          'Field': 'OSC_OutputPower',            'show_name': 'OSC OutputPower(dBm)'},
]