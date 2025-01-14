import click
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.utils.db import *
from otn.utils.pm import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('osc'), required=True)
def osc(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'osc'
       
@osc.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    show_modules_info(slot_id, osc_ids, "OSC")

@osc.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    show_modules_config(slot_id, osc_ids, "OSC")

@osc.command()
@click.pass_context
def lldp(ctx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    show_oscs_lldp(slot_id, osc_ids)
#################################### pm ############################################################
@osc.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    show_modules_pm_current(slot_id, osc_ids, "OSC", ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    show_modules_pm_history(slot_id, osc_ids, "OSC", ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("osc")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('osc'), required=True)
def cfg_osc(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'osc'

@cfg_osc.command()
@click.pass_context
def enable(ctx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    config_oscs(slot_id, osc_ids, 'enabled','true')
    
@cfg_osc.command()
@click.pass_context
def disable(ctx):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    config_oscs(slot_id, osc_ids, 'enabled','false')
    
@cfg_osc.group()
@click.pass_context
def input(ctx):
    pass

@input.command('low-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_low_threshold'),required=True)
@click.pass_context
def low_alarm_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    config_oscs(slot_id, osc_ids, 'rx-low-threshold',threshold)

@input.command('high-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_high_threshold'),required=True)
@click.pass_context
def high_alarm_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    config_oscs(slot_id, osc_ids, 'rx-high-threshold',threshold)

@cfg_osc.group()
@click.pass_context
def output(ctx):
    pass

@output.command('low-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('output_low_threshold'),required=True)
@click.pass_context
def low_alarm_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    osc_ids = get_module_ids(ctx)
    config_oscs(slot_id, osc_ids, 'tx-low-threshold',threshold)
        
################################################################################################
def show_osc_interface(slot_id, module_id, counter_list):
    table_name = "INTERFACE"
    table_key = f'INTERFACE-1-{slot_id}-{module_id}-OSC:current'
    db = get_counter_db_by_slot(slot_id)
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    show_key_value_list(counter_list ,dict_kvs)

def show_modules_info(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_info_data(slot_id, module_id, STATE_LIST, table_name)
        show_module_pm_instant(slot_id, module_id, PM_LIST, table_name)
        show_osc_interface(slot_id, module_id, COUNTER_LIST)

def show_modules_config(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_config_data(slot_id, module_id, CONFIG_LIST, table_name)

def show_osc_lldp(slot_id, module_id):
    table_key = f'INTERFACE-1-{slot_id}-{module_id}-OSC'
    db = get_state_db_by_slot(slot_id)
    dict_kvs = get_db_table_fields(db, "LLDP", table_key)
    show_key_value_list(LLDP_LIST ,dict_kvs)
        
def show_oscs_lldp(slot_id, module_ids):
    for module_id in module_ids:
        show_osc_lldp(slot_id, module_id)

def show_modules_pm_current(slot_id, module_ids, table_name, pm_type):
    for module_id in module_ids:
        show_module_pm_current_head(slot_id, module_id, table_name, pm_type)
        show_module_pm_current(slot_id, module_id, PM_LIST, table_name, pm_type)

def show_modules_pm_history(slot_id, module_ids, table_name, pm_type, bin_idx):
    for module_id in module_ids:
        show_module_pm_history_head(slot_id, module_id, table_name, pm_type, bin_idx)
        show_module_pm_history(slot_id, module_id, PM_LIST, table_name, pm_type, bin_idx)
        
def config_osc(slot_id,osc_id, field, value):
    table_name = 'OSC'
    table_key = f'OSC-1-{slot_id}-{osc_id}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)
    click.echo('Succeeded')

def config_oscs(slot_id, osc_ids, field, value):
    for osc_id in osc_ids:
        config_osc(slot_id, osc_id, field,value)         
  
STATE_LIST = [
    {'Field': 'name',               'show_name': 'Module Name'},
    {'Field': 'part-no',            'show_name': 'Module PN'},
    {'Field': 'serial-no',          'show_name': 'Module SN'},
    {'Field': 'mfg-name',           'show_name': 'Vendor'},
    {'Field': 'output-frequency',   'show_name': 'Frequency(MHz)'},
    {'Field': 'enabled',            'show_name': 'Tx Laser State'},
    {'Field': 'oper-status',        'show_name': 'link-status'},
    {'Field': 'rx-low-threshold',   'show_name': 'Rx Low AlmTh(dBm)'},
    {'Field': 'rx-high-threshold',  'show_name': 'Rx High AlmTh(dBm)'},
    {'Field': 'tx-low-threshold',   'show_name': 'Tx Low AlmTh(dBm)'}
]

CONFIG_LIST = [
    {'Field': 'name',               'show_name': 'Module Name'},
    {'Field': 'enabled',            'show_name': 'Tx Laser State'},
    {'Field': 'rx-low-threshold',   'show_name': 'Rx Low AlmTh(dBm)'},
    {'Field': 'rx-high-threshold',  'show_name': 'Rx High AlmTh(dBm)'},
    {'Field': 'tx-low-threshold',   'show_name': 'Tx Low AlmTh(dBm)'}
]

PM_LIST = [
    {'Field': 'Temperature',        'show_name': 'temperatue(C)'},
    {'Field': 'LaserBiasCurrent',   'show_name': 'Tx Bias Current(ma)'},
    {'Field': 'OutputPower',        'show_name': 'Tx Power(dBm)'},
    {'Field': 'InputPower',         'show_name': 'Rx Power(dBm)'},
    ]

COUNTER_LIST = [
    {'Field': 'in-pkts',        'show_name': 'in-pkts'},
    {'Field': 'in-errors',      'show_name': 'in-errors'},
    {'Field': 'out-pkts',       'show_name': 'out-pkts'},
    ]

LLDP_LIST = [
    {'Field': 'name',                               'show_name': 'Name'},
    {'Field': 'enabled',                            'show_name': 'Enabled'},
    {'Field': 'snooping',                           'show_name': 'Snooping'},
    {'Field': 'neighbor-id',                        'show_name': 'id'},
    {'Field': 'neighbor-system-name',               'show_name': 'System Name'},
    {'Field': 'neighbor-system-description',        'show_name': 'System Description'},
    {'Field': 'neighbor-chassis-id',                'show_name': 'Chassis ID'},
    {'Field': 'neighbor-chassis-id-type',           'show_name': 'Chassis ID Type'},
    {'Field': 'neighbor-management-address',        'show_name': 'Management Address'},
    {'Field': 'neighbor-management-address-type',   'show_name': 'Management Address Type'},
    {'Field': 'neighbor-port-id',                   'show_name': 'Port ID'},
    {'Field': 'neighbor-port-id-type',              'show_name': 'Port ID Type'},
    {'Field': 'neighbor-last-update',               'show_name': 'Last Update(s)'},
    ]