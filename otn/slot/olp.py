from tabulate import tabulate
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_synchronized_save
from otn.utils.db import *
from otn.utils.pm import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('olp'), required=True)
def olp(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'olp'
       
@olp.command()
@click.pass_context
def info(ctx):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    show_modules_info(slot_id, olp_ids, "APS")

@olp.command()
@click.pass_context
def config(ctx):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    show_modules_config(slot_id, olp_ids, "APS")

@olp.command("switch-info")
@click.pass_context
def switch_info(ctx):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    
    for olp_id in olp_ids:
        outputs = run_OLSS_utils_set(slot_id, 'APS', f'APS-1-{slot_id}-{olp_id}', 'collect-switch-info', f'true')
        if 'failed' in outputs:
            click.echo(outputs)
        time.sleep(2)
        state_db = get_state_db_by_slot(slot_id)
        get_keys = sorted(list(state_db.keys(f'OLP_SWITCH_INFO|APS-1-{slot_id}-{olp_ids}*')),reverse=True)[:10]
        for i,key in enumerate(get_keys):
            table_name = key.split('|')[0]
            table_key = key.split('|')[1]
            # datas = ConnectDb(state_db).get_table_infos(table_name,table_key)[0]
            # pattern = r'primary_in'
            # nums = len(re.findall(pattern, str(datas)))
            # state_list = StructDatas().show_shitch_info()
            # TablesViews().filter_switch_info_data(datas,state_list,nums,i+1)
            # TablesViews().filter_switch_info_datas(datas,nums)
#################################### pm ############################################################
@olp.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    show_olp_pm_current(slot_id, olp_ids, "APS", ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    show_olps_pm_history(slot_id, olp_ids, "APS", ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("olp")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('olp'), required=True)
def cfg_olp(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'olp'

@cfg_olp.group()
@click.pass_context
def alarm(ctx):
    pass
    
@alarm.command("hysteresis")
@click.argument('hysteresis',type=DynamicFieldFloatRange('alarm_hysteresis'), required=True)
@click.pass_context
def alarm_hysteresis(ctx, hysteresis):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'alarm-hysteresis', hysteresis)

@cfg_olp.group()
@click.pass_context
def switch(ctx):
    pass
    
@switch.command("hysteresis")
@click.argument('hysteresis',type=DynamicFieldFloatRange('switch_hysteresis'), required=True)
@click.pass_context
def switch_hysteresis(ctx, hysteresis):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'primary-switch-hysteresis', hysteresis)

@cfg_olp.group()
@click.pass_context
def primary_switch(ctx):
    pass

@primary_switch.command('threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('primary_switch_threshold'), required=True)
@click.pass_context
def primary_switch_threshold(ctx, threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'primary-switch-threshold', threshold)

@cfg_olp.group()
@click.pass_context
def secondary_switch(ctx):
    pass

@secondary_switch.command('threshold')
@click.argument('threshold',type=DynamicFieldFloatRange('secondary_switch_threshold'), required=True)
@click.pass_context
def secondary_switch_threshold(ctx, threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'secondary-switch-threshold', threshold)

@cfg_olp.group()
@click.pass_context
def primary_in(ctx):
    pass

@primary_in.command("alarm-threshold")
@click.argument('alarm_threshold',type=DynamicFieldFloatRange('primary_in_alarm_threshold'), required=True)
@click.pass_context
def primary_in_alarm_threshold(ctx, alarm_threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps_port(slot_id, olp_ids, 'LinePrimaryIn', 'power-low-threshold', alarm_threshold)

@cfg_olp.group()
@click.pass_context
def primary_out(ctx):
    pass

@primary_out.command("alarm-threshold")
@click.argument('alarm_threshold',type=DynamicFieldFloatRange('primary_out_alarm_threshold'), required=True)
@click.pass_context
def primary_out_alarm_threshold(ctx, alarm_threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps_port(slot_id, olp_ids, 'LinePrimaryOut', 'power-low-threshold', alarm_threshold)

@cfg_olp.group()
@click.pass_context
def secondary_in(ctx):
    pass

@secondary_in.command("alarm-threshold")
@click.argument('alarm_threshold',type=DynamicFieldFloatRange('secondary_in_alarm_threshold'), required=True)
@click.pass_context
def secondary_in_alarm_threshold(ctx, alarm_threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps_port(slot_id, olp_ids, 'LineSecondaryIn', 'power-low-threshold', alarm_threshold)

@cfg_olp.group()
@click.pass_context
def secondary_out(ctx):
    pass

@secondary_out.command("alarm-threshold")
@click.argument('alarm_threshold',type=DynamicFieldFloatRange('secondary_out_alarm_threshold'), required=True)
@click.pass_context
def secondary_out_alarm_threshold(ctx, alarm_threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps_port(slot_id, olp_ids, 'LineSecondaryOut', 'power-low-threshold', alarm_threshold)

@cfg_olp.group()
@click.pass_context
def common_in(ctx):
    pass

@common_in.command("alarm-threshold")
@click.argument('alarm_threshold',type=DynamicFieldFloatRange('common_in_alarm_threshold'), required=True)
@click.pass_context
def common_in_alarm_threshold(ctx, alarm_threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps_port(slot_id, olp_ids, 'CommonIn', 'power-low-threshold', alarm_threshold)

@cfg_olp.group()
@click.pass_context
def common_out(ctx):
    pass

@common_out.command("alarm-threshold")
@click.argument('alarm_threshold',type=DynamicFieldFloatRange('common_out_alarm_threshold'), required=True)
@click.pass_context
def common_out_alarm_threshold(ctx, alarm_threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps_port(slot_id, olp_ids, 'CommonOutput', 'power-low-threshold', alarm_threshold)

@cfg_olp.command()
@click.argument('mode',type=click.Choice(['auto-nonreversion', 'auto-reversion']), required=True)
@click.pass_context
def workmode(ctx, mode):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    work_mode = 'true' if mode == 'auto-reversion' else 'false'
    config_olps(slot_id, olp_ids, 'revertive', work_mode)

@cfg_olp.command("relative-diff-threshold")
@click.argument('threshold',type=DynamicFieldFloatRange('relative_diff_threshold'), required=True)
@click.pass_context
def relative_diff_threshold(ctx, threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'relative-switch-threshold', threshold)

@cfg_olp.command('relative-diff-threshold-offset')
@click.argument('threshold',type=DynamicFieldFloatRange('relative_diff_threshold_offset'), required=True)
@click.pass_context
def relative_diff_threshold_offset(ctx, threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'relative-switch-threshold-offset', threshold)


@cfg_olp.command("wait-to-restore-time")
@click.argument('threshold',type=DynamicFieldIntRange('wait_to_restore_time'), required=True)
@click.pass_context
def wait_to_restore_time(ctx, threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'wait-to-restore-time', threshold)

@cfg_olp.command()
@click.argument('port',type=click.Choice(['none', 'primary', 'secondary']), required=True)
@click.pass_context
def forcetoport(ctx, port):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'force-to-port', port.upper())

@cfg_olp.command()
@click.argument('work_line',type=click.Choice(['primary', 'secondary']), required=True)
@click.pass_context
def workline(ctx, work_line):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    
    for olp_id in olp_ids:
        outputs = run_OLSS_utils_set(slot_id, 'APS', f'APS-1-{slot_id}-{olp_id}', 'active-path', f'work_line.upper()')
        if 'failed' in outputs:
            click.echo(outputs)
        else:
            time.sleep(2)
            click.echo(f'Succeeded Config Olp workline {work_line}.')

@cfg_olp.command('hold-off-time')
@click.argument('threshold',type=DynamicFieldIntRange('hold_off_time'), required=True)
@click.pass_context
def hold_off_time(ctx, threshold):
    slot_id = ctx.obj['slot_idx']
    olp_ids = get_module_ids(ctx)
    config_olps(slot_id, olp_ids, 'hold-off-time', threshold)
        
################################################################################################
def config_olp(slot_id, olp_id, field, value):
    table_name = 'APS'
    table_key = f'APS-1-{slot_id}-{olp_id}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)

def config_olp_port(slot_id, olp_id, port, field, value):
    table_name = 'APS_PORT'
    table_key = f'APS-1-{slot_id}-{olp_id}_{port}'
    set_slot_synchronized_save(slot_id,table_name,table_key,field, value)

def config_olps(slot_id, olp_ids, field, value):
    for olp_id in olp_ids:
        config_olp(slot_id, olp_id, field,value)         
        click.echo('Succeeded')

def config_olps_port(slot_id, olp_ids, port, field, value):
    for olp_id in olp_ids:
        config_olp_port(slot_id, olp_id, port, field,value)         
        click.echo('Succeeded')
            
def show_modules_info(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_info_data(slot_id, module_id, STATE_LIST, table_name)
        show_olp_port_info(slot_id, module_id, "APS_PORT")

def show_olp_port_info(slot_id, module_id, table_name):
    section_str = ""
    state_db = get_state_db_by_slot(slot_id)
    db = get_counter_db_by_slot(slot_id)
    for port in OLP_PORTS:
        for field in PORT_STATE_LIST:
            table_key = f"APS-1-{slot_id}-{module_id}_{port}"
            dict_kvs = get_db_table_fields(state_db, table_name, table_key)
            field_name = field['Field']
            if field_name in dict_kvs:
                value = dict_kvs[field_name]
                section_str += (port+ " " + field['show_name']).ljust(FIELD_WITH)+ ": " + value + "\n"
        for field in PM_LIST:
            table_key = f"APS-1-{slot_id}-{module_id}_{port}_{field['Field']}:15_pm_current"
            value = get_pm_instant(db, table_name, table_key)
            section_str += (port+ " " + field['show_name']).ljust(FIELD_WITH)+ ": " + value + "\n"    
    click.echo(section_str)
    
def show_modules_config(slot_id, module_ids, table_name):
    for module_id in module_ids:
        show_module_config_data(slot_id, module_id, CONFIG_LIST, table_name)
        show_olp_port_config(slot_id, module_id, "APS_PORT")

def show_olp_port_config(slot_id, module_id, table_name):
    section_str = ""
    config_db = get_config_db_by_slot(slot_id)
    for port in OLP_PORTS:
        for field in PORT_CONFIG_LIST:
            table_key = f"APS-1-{slot_id}-{module_id}_{port}"
            dict_kvs = get_db_table_fields(config_db, table_name, table_key)
            field_name = field['Field']
            if field_name in dict_kvs:
                value = dict_kvs[field_name]
                section_str += (port+ " " + field['show_name']).ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)
    
def show_module_olp_pm_current(slot_id, module_id, pm_list, table_name, pm_type): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_counter_db_by_slot(slot_id)
    for port in OLP_PORTS:
        for field in pm_list:
            table_key = f"APS-1-{slot_id}-{module_id}_{port}_{field['Field']}:{pm_type}_pm_current"
            pm = get_db_table_fields(db, table_name, table_key)
            key = port+" "+field['show_name']
            pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_olp_pm_current(slot_id, olp_ids, table_name, pm_type):
    for module_id in olp_ids:
        show_module_pm_current_head(slot_id, module_id, table_name, pm_type)
        show_module_olp_pm_current(slot_id, module_id, PM_LIST, "APS_PORT", pm_type)

def show_module_olp_pm_history(slot_id, module_id, pm_list, table_name, pm_type, bin_idx): 
    pm_header = ['Name','Instant','Avg','Min','Max','Min-time','Max-time','Valid']
    pm_table = []
    db = get_history_db_by_slot(slot_id)
    history_stamp = get_pm_history_bin_start_time(pm_type, bin_idx)
    for port in OLP_PORTS:
        for field in pm_list:
            table_key = f"APS-1-{slot_id}-{module_id}_{port}_{field['Field']}:{pm_type}_pm_history_{history_stamp}"
            pm = get_db_table_fields(db, table_name, table_key)
            key = port+" "+field['show_name']
            pm_table.append([key, pm['instant'],pm['avg'],pm['min'],pm['max'], format_timestamp(pm['min-time']), format_timestamp(pm['max-time']),pm['validity']])
    print(tabulate(pm_table, pm_header, numalign="left")+"\n")

def show_olps_pm_history(slot_id, module_ids, table_name, pm_type, bin_idx):
    for module_id in module_ids:
        show_module_pm_history_head(slot_id, module_id, table_name, pm_type, bin_idx)
        show_module_olp_pm_history(slot_id, module_id, PM_LIST, "APS_PORT", pm_type, bin_idx)

OLP_PORTS = ["LinePrimaryIn", "LinePrimaryOut","LineSecondaryIn", "LineSecondaryOut", "CommonIn", "CommonOutput"]
    
STATE_LIST = [
        {'Field': 'name',                               'show_name': 'Module Name'},
        {'Field': 'revertive',                          'show_name': 'Work Mode (Revertive)'},
        {'Field': 'active-path',                        'show_name': 'Work Line'},
        {'Field': 'wait-to-restore-time',               'show_name': 'Wait-to-restore-time(ms)'},
        {'Field': 'hold-off-time',                      'show_name': 'Hold-off-time(ms)'},
        {'Field': 'primary-switch-hysteresis',          'show_name': 'Switch Hysteresis(dB)'},
        {'Field': 'alarm-hysteresis',                   'show_name': 'Alarm Hysteresis(dB)'},
        {'Field': 'relative-switch-threshold',          'show_name': 'Relative Diff Threshold(dB)'},
        {'Field': 'relative-switch-threshold-offset',   'show_name': 'Relative Diff Threshold Offset(dB)'},
        {'Field': 'force-to-port',                      'show_name': 'Force-to-port'},
        {'Field': 'primary-switch-threshold',           'show_name': 'primary-in Switch Th.(dBm)'},
        {'Field': 'secondary-switch-threshold',         'show_name': 'secondary-in Switch Th.(dBm)'},]

PORT_STATE_LIST = [
        {'Field': 'power-los-threshold',           'show_name': 'Los Th.(dBm)'},
        {'Field': 'power-low-threshold',           'show_name': 'Low Th.(dBm)'},
]

CONFIG_LIST = STATE_LIST

PORT_CONFIG_LIST = PORT_STATE_LIST

PM_LIST = [
        {'Field': 'OpticalPower',                'show_name': 'Optical Power(dBm)'},
    ]