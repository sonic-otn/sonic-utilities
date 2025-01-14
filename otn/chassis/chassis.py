import click

from tabulate import tabulate
from otn.utils.db import *
from otn.utils.utils import *
from otn.utils.pm import *
from otn.utils.config_utils import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxChoice('chassis'))
def chassis(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'chassis'
       
@chassis.command()
@click.pass_context
def info(ctx):
    chassis_id = ctx.obj['module_idx']
    show_chassis_info_impl(chassis_id)

@chassis.command()
@click.pass_context
def config(ctx):
    chassis_id = ctx.obj['module_idx']
    show_chassis_config_impl(chassis_id)
    
@chassis.command()
@click.pass_context
def slots(ctx):
    chassis_id = ctx.obj['module_idx']
    show_chassis_slots_impl(chassis_id)

#################################### alarm ############################################################
@chassis.group()
@click.pass_context
def alarm(ctx):
    pass

@alarm.command()
@click.pass_context
def current(ctx):
    show_chassis_alarm_current()

@alarm.command()
@click.pass_context
def history(ctx):
    show_chassis_alarm_history()
    
#################################### pm ############################################################
@chassis.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    chassis_id = ctx.obj['module_idx']
    show_chassis_pm_current_impl(chassis_id, ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    chassis_id = ctx.obj['module_idx']
    show_chassis_pm_history_impl(chassis_id, ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("chassis")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxChoice('chassis'))
def cfg_chassis(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'chassis'

@cfg_chassis.group('temperature-threshold')
@click.pass_context
def temeprature_threshold(ctx):
    pass

@temeprature_threshold.group('low-alarm')
@click.argument('la_value',type=DynamicFieldFloatRange('chassis_temp_low_alarm_threshold'),required=True)
@click.pass_context
def low_alarm(ctx,la_value):
    ctx.obj['la_value'] = la_value

@low_alarm.group('low-warning')
@click.argument('lw_value',type=DynamicFieldFloatRange('chassis_temp_low_warning_threshold'),required=True)
@click.pass_context
def low_warning(ctx,lw_value):
    ctx.obj['lw_value'] = lw_value

@low_warning.group('hi-alarm')
@click.argument('ha_value',type=DynamicFieldFloatRange('chassis_temp_hi_alarm_threshold'),required=True)
@click.pass_context
def hi_alarm(ctx,ha_value):
    ctx.obj['ha_value'] = ha_value

@hi_alarm.command('hi-warning')
@click.argument('hw_value',type=DynamicFieldFloatRange('chassis_temp_hi_warning_threshold'),required=True)
@click.pass_context
def hi_warning(ctx,hw_value):
    chassis_id = ctx.obj['module_idx']
    la_value = ctx.obj['la_value']
    lw_value = ctx.obj['lw_value']
    ha_value = ctx.obj['ha_value']
    if ha_value < hw_value:
        click.echo(f"Error, high alarm threshold should be greater than high warning threshold.")
        return
    
    if la_value > lw_value:
        click.echo(f"Error, low alarm threshold should be less than low warning threshold.")
        return
    
    config_chassis(chassis_id, "temp-low-alarm-threshold", la_value)
    config_chassis(chassis_id, "temp-low-warn-threshold", lw_value)
    config_chassis(chassis_id, "temp-high-alarm-threshold", ha_value)
    config_chassis(chassis_id, "temp-high-warn-threshold", hw_value) 
    click.echo('Succeeded')
    
#################################### clear pm ############################################################
@cfg_chassis.group("clear-pm")
@click.argument('pm_type',type=click.Choice(['15','24', 'all']),required=True)
@click.pass_context
def clear_pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@clear_pm.command()
@click.pass_context
def current(ctx):
    pm_type = ctx.obj['pm_type']
    state_db = get_chassis_state_db()
    thrift_clear_chassis_pm(pm_type)
    click.echo('Succeeded')
    
################################################################################################
def show_chassis_info_impl(chassis_id):
    table_name = "CHASSIS"
    show_chassis_info(chassis_id, table_name)
    show_chassis_pm_instant(chassis_id, PM_LIST, table_name)
    
def show_chassis_info(chassis_id, table_name):
    table_key = f'{table_name}-{chassis_id}'
    db = get_chassis_state_db()
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    show_key_value_list(STATE_LIST,dict_kvs)

def show_chassis_config(chassis_id, table_name):
    table_key = f'{table_name}-{chassis_id}'
    db = get_chassis_config_db()
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    show_key_value_list(CONFIG_LIST,dict_kvs)
    
def show_chassis_config_impl(chassis_id):
    table_name = "CHASSIS"
    show_chassis_config(chassis_id, table_name)
    
def show_chassis_pm_instant(chassis_id, pm_list, table_name):
    section_str = ""
    db = get_chassis_counter_db()
    for field in pm_list:
        table_key = f"{table_name}-{chassis_id}_{field['Field']}:15_pm_current"
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_chassis_pm_current_impl(chassis_id, pm_type):
    show_entity_pm_current_head("CHASSIS-1", pm_type)
    show_chassis_pm_current(chassis_id, PM_LIST, "CHASSIS", pm_type)

def show_chassis_pm_history_impl(chassis_id, pm_type, bin_idx):
    show_entity_pm_history_head("CHASSIS-1", pm_type, bin_idx)
    show_chassis_pm_history(chassis_id, PM_LIST, "CHASSIS", pm_type, bin_idx)

def config_chassis(chassis_id, field, value):
    table_name = 'CHASSIS'
    table_key = f'CHASSIS-{chassis_id}'
    set_chassis_configuration_save(table_name,table_key,field, value)

def show_chassis_slots_impl(chassis_id):
    chassis_slots_header = ['Slot','Prov','Status','PN','SN','Hard-Ver','Soft-Ver','Temp(C)']
    chassis_slots_info = []
    for slot_id in range(1, get_max_chassis_slots()+1):
        chassis_slots_info.append(get_chassis_slot_info(chassis_id, slot_id))
        
    print(tabulate(chassis_slots_info, chassis_slots_header, tablefmt="simple", floatfmt='.2f'))

def get_chassis_slot_info(chassis_id, slot_id):
    if(slot_is_linecard(slot_id)):
        return get_chassis_linecard_info(slot_id)
    else:
        return [slot_id, NA, NA, NA, NA, NA, NA, NA]

def get_chassis_linecard_info(slot_id):
    table_key = f'LINECARD-1-{slot_id}'
    cfg_db = get_config_db_by_slot(slot_id)
    c_kvs = get_db_table_fields(cfg_db, "LINECARD", table_key)
    
    db = get_state_db_by_slot(slot_id)
    s_kvs = get_db_table_fields(db, "LINECARD", table_key)
    
    counter_db = get_counter_db_by_slot(slot_id)
    table_key = f"LINECARD-1-{slot_id}_Temperature:15_pm_current"
    temp = get_pm_instant(counter_db, "LINECARD", table_key)
    return [slot_id, c_kvs['linecard-type'], s_kvs['slot-status'], 
            s_kvs['part-no'], s_kvs['serial-no'], s_kvs['hardware-version'], 
            s_kvs['software-version'], temp]
           
STATE_LIST = [
    {'Field': 'part-no',                    'show_name': 'Part no'},
    {'Field': 'serial-no',                  'show_name': 'Serial no'},
    {'Field': 'hardware-version',           'show_name': 'Hardware ver'},
    {'Field': 'software-version',           'show_name': 'Software ver'},
    {'Field': 'mfg-name',                   'show_name': 'Mfg name'},
    {'Field': 'mfg-date',                   'show_name': 'Mfg date'},
]

CONFIG_LIST = [
    {'Field': 'temp-high-alarm-threshold',  'show_name': 'Temp Hi-Alarm(C)'},
    {'Field': 'temp-high-warn-threshold',   'show_name': 'Temp Hi-Warning(C)'},
    {'Field': 'temp-low-alarm-threshold',   'show_name': 'Temp Low-Alarm(C)'},
    {'Field': 'temp-low-warn-threshold',    'show_name': 'Temp Low-Warning(C)'},
]

PM_LIST = [
    {'Field': 'Temperature',                'show_name': 'Temperature(C)'},
    {'Field': 'InLet',                      'show_name': 'Inlet(C)'},
    {'Field': 'OutLet',                     'show_name': 'Outlet(C)'},
]