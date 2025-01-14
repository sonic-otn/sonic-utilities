import click
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.utils.db import *
from otn.utils.pm import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('edfa'), required=True)
def edfa(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'edfa'
       
@edfa.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    show_modules_info(slot_id, edfa_ids, "AMPLIFIER")

@edfa.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    show_modules_config(slot_id, edfa_ids, "AMPLIFIER")
#################################### pm ############################################################
@edfa.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    show_modules_pm_current(slot_id, edfa_ids, "AMPLIFIER", ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    show_modules_pm_history(slot_id, edfa_ids, "AMPLIFIER", ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("edfa")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('edfa'), required=True)
def cfg_edfa(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'edfa'

@cfg_edfa.command()
@click.pass_context
def enable(ctx):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'enabled','true')
    
@cfg_edfa.command()
@click.pass_context
def disable(ctx):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'enabled','false')
    
@cfg_edfa.command('auto-shutdown')
@click.pass_context
@click.argument('status',type=click.Choice(['enable', 'disable']), required=True)
def auto_shutdown(ctx, status):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'working-state',transform_auto_shutdown(status))

@cfg_edfa.group()
@click.pass_context
def input(ctx):
    pass

@input.command('los-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_los_threshold'),required=True)
@click.pass_context
def los_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'input-los-threshold',threshold)

@input.command('low-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('input_low_threshold'),required=True)
@click.pass_context
def low_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'input-low-threshold',threshold)

@cfg_edfa.group()
@click.pass_context
def output(ctx):
    pass

@output.command('low-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('output_low_threshold'),required=True)
@click.pass_context
def output_low_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'output-low-threshold',threshold)

@cfg_edfa.group()
@click.pass_context
def gain(ctx):
    pass

@gain.command('low-threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('gain_low_threshold'),required=True)
@click.pass_context
def los_threshold(ctx,threshold):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'gain-low-threshold',threshold)

@gain.command('low-hysteresis')
@click.argument('hysteresis',type=DynamicFieldFloatRange('gain_low_hysteresis'),required=True)
@click.pass_context
def los_threshold(ctx,hysteresis):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'gain-low-hysteresis',hysteresis)

@cfg_edfa.command('los-ase-delay')
@click.argument('delay',type=DynamicFieldIntRange('los_ase_delay'),required=True)
@click.pass_context
def los_threshold(ctx,delay):
    slot_id = ctx.obj['slot_idx']
    edfa_ids = get_module_ids(ctx)
    config_edfas(slot_id, edfa_ids, 'los-ase-delay',delay)

################################################################################################
def config_edfa(slot_id, edfa_id, field, value):
    table_name = 'AMPLIFIER'
    table_key = f'AMPLIFIER-1-{slot_id}-{edfa_id}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)
    click.echo('Succeeded')

def config_edfas(slot_id, edfa_ids, field, value):
    for edfa_id in edfa_ids:
        config_edfa(slot_id, edfa_id, field,value)         

def transform_auto_shutdown(status):
    if status == 'enable':
        return 'LOS_A'
    else:
        return 'LOS_N'

def show_modules_info(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_info_data(slot_id, module_id, STATE_LIST, table_name)
        show_module_pm_instant(slot_id, module_id, PM_LIST, table_name)
    
def show_modules_config(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_config_data(slot_id, module_id, CONFIG_LIST, table_name)

def show_modules_pm_current(slot_id, module_ids, table_name, pm_type):
    for module_id in module_ids:
        show_module_pm_current_head(slot_id, module_id, table_name, pm_type)
        show_module_pm_current(slot_id, module_id, PM_LIST, table_name, pm_type)

def show_modules_pm_history(slot_id, module_ids, table_name, pm_type, bin_idx):
    for module_id in module_ids:
        show_module_pm_history_head(slot_id, module_id, table_name, pm_type, bin_idx)
        show_module_pm_history(slot_id, module_id, PM_LIST, table_name, pm_type, bin_idx)
    
STATE_LIST = [
        {'Field': 'name',                       'show_name': 'Module Name'},
        {'Field': 'part-no',                    'show_name': 'Module PN'},
        {'Field': 'serial-no',                  'show_name': 'Module SN'},
        {'Field': 'firmware-version',           'show_name': 'Firmware version'},
        {'Field': 'amp-mode',                   'show_name': 'Work mode'},
        {'Field': 'enabled',                    'show_name': 'EDFA Switch Actual'},
        {'Field': 'gain-range',                 'show_name': 'Gain Range(dB)'},
        {'Field': 'target-gain',                'show_name': 'Set gain(dB)'},
        {'Field': 'target-gain-tilt',           'show_name': 'Set Gain tilt'},
        {'Field': 'working-state',              'show_name': 'Work State'},
        {'Field': 'los-ase-delay',              'show_name': 'Los Ase Delay(ms)'},
        {'Field': 'input-los-threshold',        'show_name': 'Input LOS Th(dBm)'},
        {'Field': 'input-los-hysteresis',       'show_name': 'Input LOS Hy(dB)'},
        {'Field': 'output-los-threshold',       'show_name': 'Output LOP Th(dBm)'},
        {'Field': 'output-los-hysteresis',      'show_name': 'Output LOP Hy(dB)'},
        {'Field': 'gain-low-threshold',         'show_name': 'Gain Low Alm Th(dBm)'},
        {'Field': 'gain-low-hysteresis',        'show_name': 'Gain Low Alm Hy(dB)'},
        {'Field': 'input-low-threshold',        'show_name': 'Pin Low AlmTh(dBm)'},
        {'Field': 'output-low-threshold',       'show_name': 'Pout Low AlmTh(dBm)'}]

CONFIG_LIST = [
        {'Field': 'component',                  'show_name': 'Module Name'},
        {'Field': 'enabled',                    'show_name': 'EDFA Switch Actual'},
        {'Field': 'target-gain',                'show_name': 'Set gain(dB)'},
        {'Field': 'target-gain-tilt',           'show_name': 'Set Gain tilt'},
        {'Field': 'working-state',              'show_name': 'Work State'},
        {'Field': 'los-ase-delay',              'show_name': 'Los Ase Delay(ms)'},
        {'Field': 'input-los-threshold',        'show_name': 'Input LOS Th(dBm)'},
        {'Field': 'input-los-hysteresis',       'show_name': 'Input LOS Hy(dB)'},
        {'Field': 'output-los-threshold',       'show_name': 'Output LOP Th(dBm)'},
        {'Field': 'output-los-hysteresis',      'show_name': 'Output LOP Hy(dB)'},
        {'Field': 'gain-low-threshold',         'show_name': 'Gain Low Alm Th(dBm)'},
        {'Field': 'gain-low-hysteresis',        'show_name': 'Gain Low Alm Hy(dB)'},
        {'Field': 'input-low-threshold',        'show_name': 'Pin Low AlmTh(dBm)'},
        {'Field': 'output-low-threshold',       'show_name': 'Pout Low AlmTh(dBm)'}]

PM_LIST = [
        {'Field': 'Temperature',                'show_name': 'Module temperature(C)'},
        {'Field': 'ActualGain',                 'show_name': 'Actual gain(dB)'},
        {'Field': 'ActualGainTilt',             'show_name': 'Actual Gain tilt'},
        {'Field': 'LaserBiasCurrent',           'show_name': 'Pump Iop(mA)'},
        {'Field': 'LaserTemperature',           'show_name': 'Pump temperature(C)'},
        {'Field': 'LaserTecCurrent',            'show_name': 'Pump Itec(mA)'},
        {'Field': 'InputPowerTotal',            'show_name': 'Input power(Original)(dBm)'},
        {'Field': 'OutputPowerTotal',           'show_name': 'Output power(Original)(dBm)'}
    ]