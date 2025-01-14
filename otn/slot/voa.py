import click
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.utils.db import *
from otn.utils.pm import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('voa'), required=True)
def voa(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'voa'
       
@voa.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    voa_ids = get_module_ids(ctx)
    show_modules_info(slot_id, voa_ids, "ATTENUATOR")

@voa.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    voa_ids = get_module_ids(ctx)
    show_modules_config(slot_id, voa_ids, "ATTENUATOR")
#################################### pm ############################################################
@voa.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    voa_ids = get_module_ids(ctx)
    show_modules_pm_current(slot_id, voa_ids, "ATTENUATOR", ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    voa_ids = get_module_ids(ctx)
    show_modules_pm_history(slot_id, voa_ids, "ATTENUATOR", ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("voa")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('voa'), required=True)
def cfg_voa(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'voa'

@cfg_voa.command()
@click.pass_context
@click.argument('att',type=DynamicFieldFloatRange('voa_attenuation'),required=True)
def att(ctx, att):
    slot_id = ctx.obj['slot_idx']
    voa_ids = get_module_ids(ctx)
    config_voas(slot_id, voa_ids, 'attenuation',att)
################################################################################################
def show_modules_info(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_info_data(slot_id, module_id, STATE_LIST, table_name)

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
        
def config_voa(slot_id,voa_id, field, value):
    table_name = 'ATTENUATOR'
    table_key = f'ATTENUATOR-1-{slot_id}-{voa_id}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)

def config_voas(slot_id, voa_ids, field, value):
    for voa_id in voa_ids:
        config_voa(slot_id, voa_id, field,value)         
        click.echo('Succeeded')
  
STATE_LIST = [
    {'Field': 'name',               'show_name': 'Module Name'},
    {'Field': 'attenuation',        'show_name': 'VOA Attenuation(dB)'},
    {'Field': 'fix-attenuation',    'show_name': 'VOA fix Attenuation(dB)'}]

CONFIG_LIST = [
    {'Field': 'component',          'show_name': 'Module Name'},
    {'Field': 'attenuation',        'show_name': 'VOA Attenuation(dB)'},]

PM_LIST = [
    {'Field': 'ActualAttenuation',  'show_name': 'VOA Attenuation(dB)'},
    ]