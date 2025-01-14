import click
from otn.utils.utils import *
from otn.utils.db import *
from otn.utils.pm import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('otdr'), required=True)
def otdr(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'otdr'

@otdr.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    show_modules_info(slot_id, otdr_ids, "OTDR")

@otdr.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    show_modules_config(slot_id, otdr_ids, "OTDR")
#################################### show event  #####################################################
@otdr.command("baseline-info")
@click.pass_context
def baseline(ctx):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    show_otdrs_baseline(slot_id, otdr_ids)

@otdr.command("current-info")
@click.pass_context
def current_info(ctx):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    show_otdrs_current_scan(slot_id, otdr_ids)

@otdr.command("history-info")
@click.pass_context
def history_info(ctx):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    show_otdrs_history_scan(slot_id, otdr_ids)
    
#################################### config ############################################################
@click.group("otdr")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('otdr'), required=True)
def cfg_otdr(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'otdr'

@cfg_otdr.command("refractive-index")
@click.argument('refractive_index',type=float, required=True)
@click.pass_context
def refractive_index(ctx, refractive_index):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'refractive-index', refractive_index)

@cfg_otdr.command("backscatter-index")
@click.argument('backscatter_index',type=float, required=True)
@click.pass_context
def backscatter_index(ctx, backscatter_index):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'backscatter-index', backscatter_index)

@cfg_otdr.command("reflection-threshold")
@click.argument('reflection-threshold',type=float, required=True)
@click.pass_context
def reflection_threshold(ctx, reflection_threshold):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'reflection-threshold', reflection_threshold)

@cfg_otdr.command("splice-loss-threshold")
@click.argument('splice_loss_threshold',type=float, required=True)
@click.pass_context
def splice_loss_threshold(ctx, splice_loss_threshold):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'splice-loss-threshold', splice_loss_threshold)

@cfg_otdr.command("fiber-end-threshold")
@click.argument('fiber_end_threshold',type=float, required=True)
@click.pass_context
def fiber_end_threshold(ctx, fiber_end_threshold):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'fiber-end-threshold', fiber_end_threshold)

@cfg_otdr.command("fiber-distance-threshold")
@click.argument('fiber_distance_threshold',type=float, required=True)
@click.pass_context
def fiber_distance_threshold(ctx, fiber_distance_threshold):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'fiber-distance-threshold', fiber_distance_threshold)

@cfg_otdr.command("fiber-loss-threshold")
@click.argument('fiber_loss_threshold',type=float, required=True)
@click.pass_context
def fiber_loss_threshold(ctx, fiber_loss_threshold):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'fiber-loss-threshold', fiber_loss_threshold)

@cfg_otdr.group("distance-range")
@click.argument('distance_range',type=int, required=True)
@click.pass_context
def distance_range(ctx, distance_range):
    ctx.obj['distance_range'] = distance_range
    
@distance_range.group("pulse-width")
@click.argument('pulse_width',type=int, required=True)
@click.pass_context
def pulse_width(ctx, pulse_width):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    distance_range = ctx.obj['distance_range']
    config_otdrs(slot_id, otdr_ids, 'distance_range', distance_range)
    config_otdrs(slot_id, otdr_ids, 'pulse-width', pulse_width)

@cfg_otdr.command("average-time")
@click.argument('average_time',type=float, required=True)
@click.pass_context
def average_time(ctx, average_time):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'average-time', average_time)

@cfg_otdr.command("repetition-enable")
@click.argument('repetition_enable',type=click.Choice(['true', 'false']), required=True)
@click.pass_context
def repetition_enable(ctx, repetition_enable):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'repetition-enable', repetition_enable)

@cfg_otdr.command("repetition-start-time")
@click.argument('repetition_start_time',type=str, required=True)
@click.pass_context
def repetition_start_time(ctx, repetition_start_time):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'start-time', repetition_start_time)

@cfg_otdr.command("repetition-period")
@click.argument('repetition_period',type=int, required=True)
@click.pass_context
def repetition_period(ctx, repetition_period):
    slot_id = ctx.obj['slot_idx']
    otdr_ids = get_module_ids(ctx)
    config_otdrs(slot_id, otdr_ids, 'period', repetition_period)
                            
################################################################################################
def config_otdr(slot_id, otdr_id, field, value):
    table_name = 'OTDR'
    table_key = f'OTDR-1-{slot_id}-{otdr_id}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)
    click.echo('Succeeded')

def config_otdrs(slot_id, otdr_ids, field, value):
    for otdr_id in otdr_ids:
        config_otdr(slot_id, otdr_id, field,value)         

def show_modules_info(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_info_data(slot_id, module_id, STATE_LIST, table_name)
    
def show_modules_config(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_config_data(slot_id, module_id, CONFIG_LIST, table_name)
        
def show_otdrs_baseline(slot_id, otdr_ids):
    for otdr_id in otdr_ids:
        show_otdr_scan(slot_id, otdr_id, 'BASELINE')
        
def show_otdrs_current_scan(slot_id, otdr_ids):
    for otdr_id in otdr_ids:
        show_otdr_scan(slot_id, otdr_id, 'CURRENT')

def show_otdrs_history_scan(slot_id, otdr_ids):
    for otdr_id in otdr_ids:
        show_otdr_history_scan(slot_id, otdr_id)

def show_otdr_history_scan(slot_id, otdr_id):
    db = get_state_db_by_slot(slot_id)
    keys = get_db_table_keys(db, f'OTDR|OTDR-1-{slot_id}-{otdr_id}|20*')
    keys = [] if keys is None else keys
    click.echo(f'Total history scan num: {len(keys)}')
    scans = []
    for key in keys:
        scan = get_db_table_fields(db, 'OTDR', key)
        scans.append(scan)
    sorted_scans = sorted(scans, key=operator.itemgetter('scan-time'),reverse=True)
    for scan in sorted_scans:
        show_key_value_list(SCAN_LIST, scan)
        
def show_otdr_scan(slot_id, otdr_id, scan_type):
    db = get_state_db_by_slot(slot_id)
    baseline = get_db_table_fields(db, 'OTDR', f'OTDR-1-{slot_id}-{otdr_id}|{scan_type}')
    show_key_value_list(SCAN_LIST, baseline)
    click.echo("")
    
    keys = get_db_table_keys(db, f'OTDR_EVENT|OTDR-1-{slot_id}-{otdr_id}|{scan_type}|*')
    keys = [] if keys is None else keys
    click.echo(f'Total event num: {len(keys)}')
    events = []
    for key in keys:
        event = get_db_table_fields(db, 'OTDR_EVENT', key)
        events.append(event)
    sorted_events = sorted(events, key=operator.itemgetter('index'),reverse=True)
    for event in sorted_events:
        show_key_value_list(EVENT_LIST, baseline)

STATE_LIST = [
        {'Field': 'name',                       'show_name': 'Module Name'},
        {'Field': 'part-no',                    'show_name': 'Module PN'},
        {'Field': 'serial-no',                  'show_name': 'Module SN'},
        {'Field': 'vendor',                     'show_name': 'Module Vendor'},
        {'Field': 'mfg-data',                   'show_name': 'Mfg Date'},
        {'Field': 'firmware-version',           'show_name': 'Firmware version'},
        {'Field': 'oper-status',                'show_name': 'Oper Status'},
        
        {'Field': 'refractive-index',            'show_name': 'Refractive Index'},
        {'Field': 'backscatter-index',           'show_name': 'Backscatter Index'},
        {'Field': 'reflection-threshold',        'show_name': 'Reflection Threshold(dB)'},
        {'Field': 'splice-loss-threshold',       'show_name': 'Splice Loss Threshold(dB)'},
        {'Field': 'end-of-fiber-threshold',      'show_name': 'Fiber End Threshold(dB)'},
        {'Field': 'distance-range',              'show_name': 'Distance Range(km)'},
        {'Field': 'pulse-width',                 'show_name': 'Pulse Width(ns)'},
        {'Field': 'fiber-distance-threshold',    'show_name': 'Fiber Distance Threshold(km)'},
        {'Field': 'fiber-loss-threshold',        'show_name': 'Fiber Loss Threshold(dBm)'},
        {'Field': 'average-time',               'show_name': 'Average Time(s)'},
        {'Field': 'repetition-enable',           'show_name': 'Repetition Enable'},
        {'Field': 'start-time',                  'show_name': 'Repetition Start Time'},
        {'Field': 'period',                      'show_name': 'Repetition Period(s)'},
        {'Field': 'update-baseline',             'show_name': 'Update Baseline'},
        
        {'Field': 'output-frequency',             'show_name': 'Frequency(MHz)'},
        {'Field': 'dynamic-range',                'show_name': 'Dynamic Range(dB)'},
        {'Field': 'distance-accuracy',            'show_name': 'Distance Accuracy(m)'},
        {'Field': 'loss-dead-zone',               'show_name': 'Loss Dead Zone(m)'},
        {'Field': 'reflection-dead-zone',         'show_name': 'Reflection Dead Zone(m)'},
        {'Field': 'sampling-resolution',          'show_name': 'Sampling Resolution(m)'},
        {'Field': 'scanning-status',              'show_name': 'Scanning Status'},       
    ]

CONFIG_LIST = [
        {'Field': 'name',                        'show_name': 'Module Name'},
        {'Field': 'refractive-index',            'show_name': 'Refractive Index'},
        {'Field': 'backscatter-index',           'show_name': 'Backscatter Index'},
        {'Field': 'reflection-threshold',        'show_name': 'Reflection Threshold(dB)'},
        {'Field': 'splice-loss-threshold',       'show_name': 'Splice Loss Threshold(dB)'},
        {'Field': 'end-of-fiber-threshold',      'show_name': 'Fiber End Threshold(dB)'},
        {'Field': 'distance-range',              'show_name': 'Distance Range(km)'},
        {'Field': 'pulse-width',                 'show_name': 'Pulse Width(ns)'},
        {'Field': 'fiber-distance-threshold',    'show_name': 'Fiber Distance Threshold(km)'},
        {'Field': 'fiber-loss-threshold',        'show_name': 'Fiber Loss Threshold(dBm)'},
        {'Field': 'average-time',               'show_name': 'Average Time(s)'},
        {'Field': 'repetition-enable',           'show_name': 'Repetition Enable'},
        {'Field': 'start-time',                  'show_name': 'Repetition Start Time'},
        {'Field': 'period',                      'show_name': 'Repetition Period(s)'},
        {'Field': 'update-baseline',             'show_name': 'Update Baseline'},
    ]

SCAN_LIST = [
        {'Field': 'scan-time',                        'show_name': 'Scan Time'},
        {'Field': 'update-time',                      'show_name': 'Trace Update Time'},
        {'Field': 'span-distance',                    'show_name': 'Span Distance(km)'},
        {'Field': 'span-loss',                        'show_name': 'Span Loss(dB)'},
    ]

EVENT_LIST = [
        {'Field': 'scan-time',                        'show_name': 'Event Idex'},
        {'Field': 'type',                             'show_name': 'Event Type'},
        {'Field': 'length',                           'show_name': 'Event Length(km)'},
        {'Field': 'loss',                             'show_name': 'Event Loss(dB)'},
        {'Field': 'reflection',                       'show_name': 'Event reflection(dB)'},
        {'Field': 'accumulate-loss',                  'show_name': 'Event Accumulate Loss(dB)'},
    ]