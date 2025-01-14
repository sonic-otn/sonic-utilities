import click
import sys
from click import IntRange
from otn.utils.utils import *
from otn.utils.db import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.slot.terminal_line_command_info import *
from . import terminal_line_upgrade

from otn.slot.terminal_line_utils import *

################################### config #########################################################
@click.group("line")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('line'), required=True)
def cfg_line(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'line'

@cfg_line.command()
@click.pass_context
@click.argument('admin_state', type=click.Choice(["enable","disable","maintenance"]), required = True)
def admin(ctx, admin_state):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    admin_value = admin_dict[admin_state]
    config_lines_logical_channel(slot_id, line_ids, 'admin-state', admin_value)

@cfg_line.command("loopback")
@click.argument('loopback', type = click.Choice(["facility", "terminal", "none"]), required = True)
@click.pass_context
def loopback(ctx, loopback):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    loopback_value = loopback_dict[loopback]
    config_lines_logical_channel(slot_id, line_ids, "loopback-mode", loopback_value)

@cfg_line.command("maintenance")
@click.argument('maintenance', type=click.Choice(["ais", "lck", "oci", "none"]), required=True)
@click.pass_context
def maintenance(ctx, maintenance):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    maint_signal_dict = {'ais':'AIS', 'lck':'LCK', 'oci':'OCI', 'none':'NONE'}
    maint_signal = maint_signal_dict[maintenance]
    config_lines_OTN(slot_id, line_ids, "maintenance", maint_signal)

@cfg_line.command("tti-msg-auto")
@click.argument('tti_auto', type=click.Choice(["enable", "disable"]), required=True)
@click.pass_context
def tti_msg_auto(ctx, tti_auto):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    tti_auto = bool_common_dict[tti_auto]
    config_lines_OTN(slot_id, line_ids, "tti-msg-auto", tti_auto)

@cfg_line.command("tti-msg-expected")
@click.argument('tti_expected', type=str, required=True)
@click.pass_context
def tti_msg_expected(ctx, tti_expected):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    if len(tti_expected) > 32:
        click.echo(f'Error: Max char length of {tti_expected} more len 32.')
        return
    config_lines_OTN(slot_id, line_ids, "tti-msg-expected", tti_expected)

@cfg_line.command("tti-msg-transmit")
@click.argument('tti_transmit', type=str, required=True)
@click.pass_context
def tti_msg_transmit(ctx, tti_transmit):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    if len(tti_transmit) > 32:
        click.echo(f'Error: Max char length of {tti_transmit} more len 32.')
        return
    config_lines_OTN(slot_id, line_ids, "tti-msg-transmit", tti_transmit)

@cfg_line.command()
@click.argument('frequency', type=str, required=True)
@click.pass_context
def frequency(ctx, frequency):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    if not frequency.isdigit() or int(frequency) not in range(191300000, 196100001, 6250):
        click.echo(f'Invalid frequency input. The range between 191300000 ~ 196100000 .The step must be 6250 MHz')
        return
    config_lines_OCH(slot_id, line_ids, "frequency", frequency)

@cfg_line.command("vendor-expect")
@click.argument('vendor_expect', type = click.Choice(['ACACIA', 'FOC', 'ACCELINK', 'INNOLIGHT','CIENA']), required=True)
@click.pass_context
def vendor_expect(ctx, vendor_expect):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    config_lines_transceiver(slot_id, line_ids, 'vendor-expect', vendor_expect)

@cfg_line.command("rx-cd-range")
@click.argument('low_range', type = IntRange(-2000, 8000), required = True)
@click.argument('high_range', type = IntRange(-2000, 8000), required = True)
@click.pass_context
def cd_range(ctx, low_range, high_range):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    if low_range > high_range:
        click.echo(f'ValueError: {low_range} must be less then {high_range}. ')
        return
    
    for line_id in line_ids:
        vendor = get_slot_line_transceiver_vendor(slot_id, line_id)
        if vendor == 'INNOLIGHT' and (low_range < -300 or high_range > 6300):
            click.echo(f'Error: Invalid value of CD RANGE, Valid value for {vendor} DCO in range -300 ~ 6300.')
            return
    
    value = '{},{}'.format(low_range, high_range)    
    config_lines_port(slot_id, line_ids, 'rx-cd-range', value)

@cfg_line.command("tx-laser")
@click.argument('tx_laser', type=click.Choice(["on", "off"]), required = True)
@click.pass_context
def tx_laser(ctx, tx_laser):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    tx_laser_dict = {'on':'true', 'off':'false'}
    tx_laser_value = tx_laser_dict[tx_laser]
    config_lines_transceiver(slot_id, line_ids, "enabled", tx_laser_value)

@cfg_line.command("tx-power")
@click.argument('target_power', type=float, required = True)
@click.pass_context
def tx_power(ctx, target_power):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    value = float(f'{target_power:.1f}')
    config_lines_OCH(slot_id, line_ids, "target-output-power", value)
 
@cfg_line.command('prbs')
@click.argument('direction', type=click.Choice(['rx', 'tx']), required=True)
@click.argument('mode', type=click.Choice(['enable', 'disable']), required=True)
@click.argument('pattern', type=click.Choice(["2^7", "2^11", "2^15", "2^23", "2^31"]), required=False)
@click.pass_context
def prbs_signal(ctx, direction, mode, pattern):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
 
    if direction == 'tx':
        table_field = 'tx-test-signal-pattern'
    else:
        table_field = 'rx-test-signal-pattern'
    
    if mode == 'disable':
            prbs_pattern = 'PRBS_PATTERN_TYPE_NONE'
    else:
        prbs_pattern = prbs_signal_pattern[pattern]
        
    config_lines_logical_channel(slot_id, line_ids, table_field, prbs_pattern)
#################################### clear pm ############################################################
@cfg_line.group("clear-pm")
@click.argument('pm_type',type=click.Choice(['15','24', 'all']),required=True)
@click.pass_context
def clear_pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@clear_pm.command()
@click.pass_context
def current(ctx):
    pm_type = ctx.obj['pm_type']
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    clear_lines_pm(slot_id, line_ids, pm_type)

cfg_line.add_command(terminal_line_upgrade.upgrade)   
     
################################################################################################
def config_lines_logical_channel(slot_id, line_ids, field, value):
    table_name = LOGICAL_CHANNEL
    for line_id in line_ids:
        table_key = get_line_OTU_logical_channel_id(slot_id, line_id)
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def config_lines_OTN(slot_id, line_ids, field, value):
    table_name = OTN
    for line_id in line_ids:
        table_key = get_line_OTU_logical_channel_id(slot_id, line_id)
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def config_lines_OCH(slot_id, line_ids, field, value):
    table_name = OCH
    for line_id in line_ids:
        table_key = f'OCH-1-{slot_id}-L{line_id}'
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')
    
def config_lines_transceiver(slot_id, line_ids, field, value):
    table_name = TRANSCEIVER
    for line_id in line_ids:
        table_key = f'{table_name}-1-{slot_id}-L{line_id}'
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def config_lines_port(slot_id, line_ids, field, value):
    table_name = PORT
    for line_id in line_ids:
        table_key = f'{table_name}-1-{slot_id}-L{line_id}'
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def get_slot_line_transceiver_vendor(slot_id, line_id):
    db = get_state_db_by_slot(slot_id)
    return get_db_table_field(db, "TRANSCEIVER", f'TRANSCEIVER-1-{slot_id}-L{line_id}', 'vendor')

def clear_lines_pm(slot_id, line_ids, pm_type):
    state_db = get_state_db_by_slot(slot_id)
    for line_id in line_ids:
        keys = [f'PORT:PORT-1-{slot_id}-L{line_id}', 
                f'TRANSCEIVER:TRANSCEIVER-1-{slot_id}-L{line_id}',
                f'OCH:OCH-1-{slot_id}-L{line_id}',
                f'OTN:{get_line_OTU_logical_channel_id(slot_id, line_id)}']

        for table_key in keys:
            set_table_field(state_db,"CLEANPM",table_key,'period', pm_type)
            set_table_field(state_db,"CLEANPM",table_key,'type', 'gauge')
        click.echo('Succeeded')  
