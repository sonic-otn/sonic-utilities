import click
from tabulate import tabulate
from otn.utils.utils import *
from otn.utils.db import *
from otn.utils.pm import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('ocm'), required=True)
def ocm(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'ocm'

@ocm.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    ocm_ids = get_module_ids(ctx)
    show_modules_info(slot_id, ocm_ids, "OCM")

@ocm.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    ocm_ids = get_module_ids(ctx)
    show_modules_config(slot_id, ocm_ids, "OCM")
#################################### show spectrum  #####################################################
@ocm.command()
@click.pass_context
def spectrum(ctx):
    slot_id = ctx.obj['slot_idx']
    ocm_ids = get_module_ids(ctx)
    show_ocms_spectrum(slot_id, ocm_ids)

#################################### config ############################################################
@click.group("ocm")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('ocm'), required=True)
def cfg_ocm(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'ocm'

@cfg_ocm.command("monitor-port")
@click.argument('monitor_port',type=str, required=True)
@click.pass_context
def monitor_port(ctx, monitor_port):
    slot_id = ctx.obj['slot_idx']
    ocm_ids = get_module_ids(ctx)
    config_ocms(slot_id, ocm_ids, 'monitor-port', monitor_port)

@cfg_ocm.command("spectrum-grid")
@click.argument('spectrum_grid',type=click.Choice([12.5, 50, 100]), required=True)
@click.pass_context
def monitor_port(ctx, spectrum_grid):
    slot_id = ctx.obj['slot_idx']
    ocm_ids = get_module_ids(ctx)
    config_ocms(slot_id, ocm_ids, 'frequency-granularity', spectrum_grid)
    
################################################################################################
def config_ocm(slot_id, ocm_id, field, value):
    table_name = 'OCM'
    table_key = f'OCM-1-{slot_id}-{ocm_id}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)
    click.echo('Succeeded')

def config_ocms(slot_id, ocm_ids, field, value):
    for ocm_id in ocm_ids:
        config_ocm(slot_id, ocm_id, field,value)         

def show_modules_info(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_info_data(slot_id, module_id, STATE_LIST, table_name)
    
def show_modules_config(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_config_data(slot_id, module_id, CONFIG_LIST, table_name)
        
def show_ocms_spectrum(slot_id, ocm_ids):
    for ocm_id in ocm_ids:
        show_ocm_spectrum(slot_id, ocm_id)
        
def show_ocm_spectrum(slot_id, ocm_id):
    db = get_state_db_by_slot(slot_id)
    monitor_port = get_db_table_field(db, 'OCM', f'OCM-1-{slot_id}-{ocm_id}', 'monitor-port')
    name = get_db_table_field(db, 'OCM', f'OCM-1-{slot_id}-{ocm_id}', 'name')

    keys = get_db_table_keys(db, f'OCM|OCM-1-{slot_id}-{ocm_id}|*')
    keys = [] if keys is None else keys
    click.echo(f'{name} monitor {monitor_port} Total spectrum num: {len(keys)}')
    spectrums = []
    for key in keys:
        spectrum = get_db_table_fields(db, 'OCM', key)
        spectrums.append(spectrum)
    sorted_spectrums = sorted(spectrums, key=operator.itemgetter('lower-frequency'),reverse=True)
    
    spectrum_header = ['id','lower-frequency(MHz)','upper-frequency(MHz)','power(dBm)']
    spectrums_info = []
    index = 1
    for spectrum in sorted_spectrums:
        spectrums_info.append([index, spectrum['lower-frequency'], spectrum['upper-frequency'], spectrum['power']])
        index = index + 1     
    click.echo(tabulate(spectrums_info, spectrum_header, tablefmt="simple"))
    click.echo("")
 
STATE_LIST = [
        {'Field': 'name',                       'show_name': 'Module Name'},
        {'Field': 'part-no',                    'show_name': 'Module PN'},
        {'Field': 'serial-no',                  'show_name': 'Module SN'},
        {'Field': 'vendor',                     'show_name': 'Module Vendor'},
        {'Field': 'mfg-data',                   'show_name': 'Mfg Date'},
        {'Field': 'firmware-version',           'show_name': 'Firmware version'},
        {'Field': 'oper-status',                'show_name': 'Oper Status'},
        {'Field': 'monitor-port',               'show_name': 'Monitor Port'},
        {'Field': 'frequency-granularity',      'show_name': 'Frequency Grid(MHz)'},
    ]

CONFIG_LIST = [
        {'Field': 'name',                       'show_name': 'Module Name'},
        {'Field': 'monitor-port',               'show_name': 'Monitor Port'},
        {'Field': 'frequency-granularity',      'show_name': 'Frequency Grid(MHz)'},
    ]