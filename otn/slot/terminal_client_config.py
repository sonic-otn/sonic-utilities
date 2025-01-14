import click
import time
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.utils.db import *
from otn.slot.terminal_client_command_info import *
from otn.slot.terminal_client_utils import *

################################### config #########################################################
@click.group("client")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('client'), required=True)
def cfg_client(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'client'

@cfg_client.command()
@click.pass_context
@click.argument('admin_state', type=click.Choice(["enable","disable","maintenance"]), required = True)
def admin(ctx, admin_state):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    admin_value = admin_dict[admin_state]
    config_clients_logical_channel(slot_id, client_ids, 'admin-state', admin_value)

@cfg_client.command()
@click.argument('als_type', type = click.Choice(['client-tx','client-rx','line-rx']), required = True)
@click.argument('mode', type=click.Choice(["enable", "disable"]), required=True)
@click.pass_context
def als(ctx, als_type, mode):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    als_dict = {'enable':'LASER_SHUTDOWN', 'disable':'ETHERNET'}
    als_value = als_dict[mode]
    table_field = ['client-als' if als_type != 'client-rx' else 'client-rx-als'][0]
    config_clients_ethernet(slot_id, client_ids, table_field, als_value)

@cfg_client.command("als-holdoff")
@click.argument('als_type', type = click.Choice(['client-tx','client-rx','line-rx']), required = True)
@click.argument('hold_off_time', type = click.IntRange(0, 2000), required = True)
@click.pass_context
def als_holdoff(ctx, als_type, hold_off_time):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    table_field = ['als-delay' if als_type != 'client-rx' else 'client-rx-als-delay'][0]
    config_clients_ethernet(slot_id, client_ids, table_field, str(hold_off_time))

@cfg_client.command("auto-delay-meas")
@click.argument('delay_mode', type = click.Choice(["enable", "disable"]), required = True)
@click.pass_context
def auto_delay_meas(ctx, delay_mode):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    table_field = "delay-measurement-enabled"
    dm_value = bool_common_dict[delay_mode]
    config_clients_OTN(slot_id, client_ids, table_field, dm_value)

@cfg_client.command("fec")
@click.argument('fec_status', type=click.Choice(["enable","disable","auto"]), required = True)
@click.pass_context
def fec(ctx, fec_status):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    fec_dict = {'enable':'FEC_ENABLED', 'disable':'FEC_DISABLED', 'auto': 'FEC_AUTO'}
    value = fec_dict[fec_status]
    config_clients_transceiver(slot_id, client_ids, "fec-mode", value)

@cfg_client.group("link-down-delay")
@click.pass_context
def link_down_delay(ctx):
    pass

@link_down_delay.command("enalbe")
@click.pass_context
def link_down_delay_enable(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    mode  = 'true'
    config_clients_logical_channel(slot_id, client_ids, "link-down-delay-mode", mode)

@link_down_delay.command("disable")
@click.pass_context
def link_down_delay_disable(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    mode  = 'false'
    config_clients_logical_channel(slot_id, client_ids, "link-down-delay-mode", mode)

@link_down_delay.command('hold-off-time')
@click.argument('hold_off_time', type=click.IntRange(0,2000), required=False, default=50)
@click.pass_context
def link_down_delay_holdoff(ctx, hold_off_time):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    # TODO 10 step check
    config_clients_logical_channel(slot_id, client_ids, "link-down-delay-hold-off", str(hold_off_time))

@cfg_client.group("link-up-delay")
@click.pass_context
def link_up_delay(ctx):
    pass

@link_up_delay.command("enable")
@click.pass_context
def link_up_delay_enable(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    mode = 'true'
    config_clients_logical_channel(slot_id, client_ids, "link-up-delay-mode", mode)

@link_up_delay.command("disable")
@click.pass_context
def link_up_delay_disable(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    mode = 'false'
    config_clients_logical_channel(slot_id, client_ids, "link-up-delay-mode", mode)

@link_up_delay.command('hold-off-time')
@click.argument('hold_off_time', type=click.IntRange(0, 86400), required=True)
@click.pass_context
def link_up_delay_holdoff(ctx, hold_off_time):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    config_clients_logical_channel(slot_id, client_ids, "link-up-delay-hold-off", str(hold_off_time))

@link_up_delay.command('threshold-time')
@click.argument('active_threshold', type=click.IntRange(0,2000), required=False, default=50)
@click.pass_context
def link_up_delay_threshold_time(ctx, active_threshold):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    config_clients_logical_channel(slot_id, client_ids, "link-up-delay-active-threshold", str(active_threshold))

@cfg_client.command("lldp")
@click.argument('lldp', type = click.Choice(["disable", "enable"]), required=True)
@click.pass_context
def lldp(ctx, lldp):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    lldp_value = bool_common_dict[lldp]
    config_clients_LLDP(slot_id, client_ids, "enabled", lldp_value)

@cfg_client.command("loopback")
@click.argument('loopback', type = click.Choice(["facility", "terminal", "none"]), required = True)
@click.pass_context
def loopback(ctx, loopback):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    loopback_value = loopback_dict[loopback]
    config_clients_logical_channel(slot_id, client_ids, "loopback-mode", loopback_value)

@cfg_client.command("maintenance")
@click.argument('maintenance', type=click.Choice(["lf", "rf", "idle", "none"]), required=True)
@click.pass_context
def maintenance(ctx, maintenance):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    maint_signal_dict = {'lf':'LF', 'rf':'RF', 'idle':'IDLE', 'none':'NONE'}
    maint_signal = maint_signal_dict[maintenance]
    config_clients_ethernet(slot_id, client_ids, "maintenance", maint_signal)

@cfg_client.command("power-mode")
@click.argument('power_mode', type = click.Choice(["normal", "low-power"]), required = True)
@click.pass_context
def power_mode(ctx, power_mode):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    power_mode_dict = {'normal':'NORMAL', 'low-power':'LOW_POWER'}
    power_mode_value = power_mode_dict[power_mode]
    config_clients_transceiver(slot_id, client_ids, "power-mode", power_mode_value)

pmd_list = ['ETH_100GBASE_SR4', 'ETH_100GBASE_LR4', 'ETH_100GBASE_ER4', 'ETH_100GBASE_CWDM4',
            'ETH_200GBASE_SR4', 'ETH_200GBASE_DR4', 'ETH_200GBASE_FR4', 'ETH_AUTO']

@cfg_client.command("pre-configuration")
@click.argument('pre_configuration', type = click.Choice(pmd_list), required = True)
@click.pass_context
def pre_configuration(ctx, pre_configuration):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    config_clients_transceiver(slot_id, client_ids, "ethernet-pmd-preconf", pre_configuration)

@cfg_client.command("reset-qsfp")
@click.pass_context
def reset_qsfp(ctx):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    table_name = "REBOOT"
    table_field = "reboot-type"
    db = get_state_db_by_slot(slot_id)
    for client_id in client_ids:
        table_key = f'{table_name}-1-{slot_id}-C{client_id}'
        set_table_field(db, table_name, table_key, table_field, "WARM")
        click.echo('  Succeeded')
    
@cfg_client.group('temperature-threshold')
@click.pass_context
def temeprature_threshold(ctx):
    pass

@temeprature_threshold.group('low-alarm')
@click.argument('la_value',type=DynamicFieldFloatRange('slot_temp_low_alarm'),required=True)
@click.pass_context
def low_alarm(ctx,la_value):
    ctx.obj['la_value'] = la_value

@low_alarm.group('low-warning')
@click.argument('lw_value',type=DynamicFieldFloatRange('slot_temp_low_warning'),required=True)
@click.pass_context
def low_warning(ctx,lw_value):
    ctx.obj['lw_value'] = lw_value

@low_warning.group('hi-alarm')
@click.argument('ha_value',type=DynamicFieldFloatRange('slot_temp_hi_alarm'),required=True)
@click.pass_context
def hi_alarm(ctx,ha_value):
    ctx.obj['ha_value'] = ha_value

@hi_alarm.command('hi-warning')
@click.argument('hw_value',type=DynamicFieldFloatRange('slot_temp_hi_warning'),required=True)
@click.pass_context
def hi_warning(ctx,hw_value):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    la_value = ctx.obj['la_value']
    lw_value = ctx.obj['lw_value']
    ha_value = ctx.obj['ha_value']
    if ha_value < hw_value:
        click.echo(f"Error, high alarm threshold should be greater than high warning threshold.")
        return
    
    if la_value > lw_value:
        click.echo(f"Error, low alarm threshold should be less than low warning threshold.")
        return
    
    config_clients_transceiver(slot_id, client_ids, "temp-low-alarm-threshold", la_value)
    config_clients_transceiver(slot_id, client_ids, "temp-low-warn-threshold", lw_value)
    config_clients_transceiver(slot_id, client_ids, "temp-high-alarm-threshold", ha_value)
    config_clients_transceiver(slot_id, client_ids, "temp-high-warn-threshold", hw_value)

@cfg_client.command("tx-laser")
@click.argument('tx_laser', type=click.Choice(["on", "off"]), required = True)
@click.pass_context
def tx_laser(ctx, tx_laser):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    tx_laser_dict = {'on':'true', 'off':'false'}
    tx_laser_value = tx_laser_dict[tx_laser]
    config_clients_transceiver(slot_id, client_ids, "enabled", tx_laser_value)
#################################### clear pm ############################################################
@cfg_client.group("clear-pm")
@click.argument('pm_type',type=click.Choice(['15','24', 'all']),required=True)
@click.pass_context
def clear_pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@clear_pm.command()
@click.pass_context
def current(ctx):
    pm_type = ctx.obj['pm_type']
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    clear_clients_pm(slot_id, client_ids, pm_type)

@cfg_client.command("clear-rmon")
@click.argument('rmon_type',type=click.Choice(['remote', 'local']), required=True)
@click.pass_context
def clear_rmon(ctx, rmon_type):
    slot_id = ctx.obj['slot_idx']
    client_ids = get_module_ids(ctx)
    if rmon_type == 'remote':
        clear_clients_rmon_remote(slot_id, client_ids)
    else:
        clear_clients_rmon_local(slot_id, client_ids)
################################################################################################
def config_clients_logical_channel(slot_id, client_ids, field, value):
    table_name = LOGICAL_CHANNEL
    for client_id in client_ids:
        table_key = get_client_GE_logical_channel_id(slot_id, client_id)
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)  
        click.echo('Succeeded')       

def config_clients_ethernet(slot_id, client_ids, field, value):
    table_name = ETHERNET
    for client_id in client_ids:
        table_key = get_client_GE_logical_channel_id(slot_id, client_id)
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def config_clients_OTN(slot_id, client_ids, field, value):
    table_name = OTN
    for client_id in client_ids:
        table_key = get_client_ODU_logical_channel_id(slot_id, client_id)
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')
    
def config_clients_transceiver(slot_id, client_ids, field, value):
    table_name = TRANSCEIVER
    for client_id in client_ids:
        table_key = f'{table_name}-1-{slot_id}-C{client_id}'
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def config_clients_LLDP(slot_id, client_ids, field, value):
    table_name = LLDP
    for client_id in client_ids:
        table_key = get_client_GE_logical_channel_id(slot_id, client_id)
        set_slot_synchronized_save(slot_id,table_name,table_key,field, value)         
        click.echo('Succeeded')

def clear_clients_pm(slot_id, client_ids, pm_type):
    state_db = get_state_db_by_slot(slot_id)
    for client_id in client_ids:
        keys = [f'PORT:PORT-1-{slot_id}-C{client_id}', 
                     f'TRANSCEIVER:TRANSCEIVER-1-{slot_id}-C{client_id}',
                     f'OTN:{get_client_ODU_logical_channel_id(slot_id, client_id)}']

        for table_key in keys:
            set_table_field(state_db,"CLEANPM",table_key,'period', pm_type)
            set_table_field(state_db,"CLEANPM",table_key,'type', 'gauge')

        for ch_idx in range(1, 5):
            table_key = f'TRANSCEIVER:TRANSCEIVER-1-{slot_id}-C{client_id}|CH-{ch_idx}'
            set_table_field(state_db,"CLEANPM",table_key,'period', pm_type)
            set_table_field(state_db,"CLEANPM",table_key,'type', 'gauge')
        click.echo('Succeeded')  

def clear_clients_rmon_remote(slot_id, client_ids):
    state_db = get_state_db_by_slot(slot_id)
    for client_id in client_ids:
        GE_ch = get_client_GE_logical_channel_id(slot_id, client_id)
        run_OLSS_utils_set(slot_id, 'ETHERNET', f'{GE_ch}', 'clear-rmon', 'true')
        set_table_field(state_db,'ETHERNET',f'{GE_ch}:current','last-clean-up', f"{time.time()}")
        click.echo('Succeeded')

def clear_clients_rmon_local(slot_id, client_ids):
    state_db = get_state_db_by_slot(slot_id)
    for client_id in client_ids:
        GE_ch = get_client_GE_logical_channel_id(slot_id, client_id)
        keys = [f'TRANSCEIVER:TRANSCEIVER-1-{slot_id}-C{client_id}', 
                     f'ETHERNET:{GE_ch}',
                     f'INTERFACE:INTERFACE-1-{slot_id}-C{client_id}']
        for table_key in keys:
            set_table_field(state_db,"CLEANPM",table_key,'period', 'all')
            set_table_field(state_db,"CLEANPM",table_key,'type', 'gauge')
        set_table_field(state_db,'ETHERNET',f'{GE_ch}:current','last-clean-up', f"{time.time()}")
        click.echo('Succeeded')