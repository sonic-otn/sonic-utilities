import click
import operator
import json
import pexpect
import netaddr
import os
import otn
import subprocess
import sys

from datetime import datetime 
from otn.utils.db import *
from otn.utils.constants import *
from sonic_py_common import logger, device_info

from tabulate import tabulate

log = logger.Logger("cli")

class DynamicLinecardTypeChoice(click.Choice):
    def __init__(self):
        super().__init__([])

    def convert(self, value, param, ctx):
        if('linecard_type' in ctx.obj):
            # update the card_type context, will use it in board mode choice
            ctx.obj['card_type'] = value
            # Copy the list and don't modify the context
            linecard_type_list = ctx.obj['linecard_type'].copy()
            linecard_type_list.append(CARD_TYPE_NONE)
            super().__init__(linecard_type_list)
            return super().convert(value, param, ctx)
        else:
            raise click.ClickException(f"Haven't defined linecard type in CLI.")

class DynamicBoardModeChoice(click.Choice):
    def __init__(self):
        super().__init__([])

    def convert(self, value, param, ctx):  
        card_type = ctx.obj['card_type']
        slot_id = ctx.obj['slot_idx']
        load_slot_capability_with_card_with_cardtype(ctx, slot_id, card_type)
        
        if('board_mode_list' in ctx.obj):
            board_mode_list = ctx.obj['board_mode_list']
            super().__init__(board_mode_list)
            return super().convert(value, param, ctx)
        else:
            raise click.ClickException(f"Haven't defined board mode in CLI.")


class DynamicModuleIdxChoice(click.Choice):
    def __init__(self, module_name):
        self.module_name = module_name
        super().__init__([])

    def convert(self, value, param, ctx):
        if((self.module_name in ctx.obj)):
            str_list =[str(module['id']) for module in ctx.obj[self.module_name]]
            super().__init__(str_list)
            return super().convert(value, param, ctx)
        else:
            raise click.ClickException(f"Don't support module {self.module_name}.")

class DynamicModuleIdxAllChoice(click.Choice):
    def __init__(self, module_name):
        self.module_name = module_name
        super().__init__([])
    
    def convert(self, value, param, ctx):
        if(self.module_name in ctx.obj):
            str_list =[str(module['id']) for module in ctx.obj[self.module_name]]
            str_list.append("all")
            super().__init__(str_list)
            return super().convert(value, param, ctx)
        else:
            raise click.ClickException(f"Don't support module {self.module_name}.")

class DynamicFieldFloatRange(click.FloatRange):
    def __init__(self, field_name):
        self.field_name = field_name
        super().__init__(0.0, 0.0)
    
    def convert(self, value, param, ctx):
        if self.field_name not in ctx.obj:
            raise click.ClickException(f"Don't support field {self.field_name}.")
        
        field_range_low = ctx.obj[self.field_name][0]
        field_range_high= ctx.obj[self.field_name][1]
        super().__init__(field_range_low, field_range_high)
        if len(str(value).split('.')) > 1 and len(str(value).split('.')[1]) > 1:
            self.fail(f"{value} is not 0.1 step", param, ctx)
        return super().convert(value, param, ctx)

class DynamicFieldIntRange(click.IntRange):
    def __init__(self, field_name):
        self.field_name = field_name
        super().__init__(0, 0)
    
    def convert(self, value, param, ctx):
        if self.field_name not in ctx.obj:
            raise click.ClickException(f"Don't support field {self.field_name}.")
        
        field_range_low = ctx.obj[self.field_name][0]
        field_range_high= ctx.obj[self.field_name][1]
        super().__init__(field_range_low, field_range_high)
        return super().convert(value, param, ctx)

# Callback for confirmation prompt. Aborts if user enters "n"
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

def echo_log_exit(msg):
    click.echo(msg)
    log.log_error(msg)
    raise click.Abort()
        
def load_slot_capability(ctx, slot_idx):
    ctx.obj.update(get_chassis_capability()) 
    ctx.obj.update(get_linecard_capability(slot_idx))

def load_slot_capability_with_card_with_cardtype(ctx, slot_idx, card_type):
    ctx.obj.update(get_chassis_capability()) 
    ctx.obj.update(get_linecard_capability_with_cardtype(slot_idx, card_type))
    
def load_chassis_capability(ctx):
    ctx.obj.update(get_chassis_capability()) 
    
def get_max_chassis_slots():
    chassis_info = get_chassis_capability()
    return chassis_info["max_slot_id"]

def get_linecard_slot_range():
    chassis_info = get_chassis_capability()
    slot_id_list =[slot['id'] for slot in chassis_info['slot']]
    return slot_id_list

def slot_is_linecard(slot_id):
    return slot_id in get_linecard_slot_range()

def slot_is_psu(slot_id):
    chassis_info = get_chassis_capability()
    return slot_id in chassis_info["psu_id_list"]

def slot_is_fan(slot_id):
    chassis_info = get_chassis_capability()
    return slot_id in chassis_info["fan_id_list"]

def get_linecard_capability(slot_idx):
    card_type = get_slot_card_type(slot_idx).upper()
    platform = get_chassis_config_db().hget('DEVICE_METADATA|localhost', 'platform')
    path = f'/usr/share/sonic/device/{platform}/linecards/{card_type}/cli_capability.json'
    if os.path.isfile(path):
        return json.load(open(path, encoding='utf-8'))
    else:
        return {}

def get_linecard_capability_with_cardtype(slot_idx, card_type):
    platform = get_chassis_config_db().hget('DEVICE_METADATA|localhost', 'platform')
    path = f'/usr/share/sonic/device/{platform}/linecards/{card_type}/cli_capability.json'
    if os.path.isfile(path):
        return json.load(open(path, encoding='utf-8'))
    else:
        return {}

def get_chassis_capability():
    platform = get_chassis_config_db().hget('DEVICE_METADATA|localhost', 'platform')
    path = f'/usr/share/sonic/device/{platform}/chassis_cli_capability.json'
    if os.path.isfile(path):
        return json.load(open(path, encoding='utf-8'))
    else:
        return {}

def get_card_is_present(slot_id):
    db = get_state_db_by_slot(slot_id)
    value = get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", "empty")
    if value == "false":
        return True
    else:
        return False

def get_card_type(slot_id):
    db = get_state_db_by_slot(slot_id)
    return get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", "linecard-type")

def get_slot_software_version(slot_id):
    db = get_state_db_by_slot(slot_id)
    return get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", "software-version")

def slot_is_ready(slot_id):
    db = get_state_db_by_slot(slot_id)
    value = get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", "slot-status")
    return value.upper() == 'READY'

def get_chassis_pn():
    db = get_chassis_state_db()
    return get_db_table_field(db, "CHASSIS", f"CHASSIS-1", "part-no")

def get_slot_card_type(slot_id):
    db = get_state_db_by_slot(slot_id)
    return get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", 'linecard-type')

def get_slot_board_mode(slot_id):
    db = get_state_db_by_slot(slot_id)
    return get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", 'board-mode')

def is_card_type_mismatch(slot_id):
    db = get_state_db_by_slot(slot_id)
    value = get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", 'slot-status')
    if value in ('Mismatch','PowerOff'):
        return True
    else:
        return False

def get_slot_board_mode(slot_id):
    db = get_state_db_by_slot(slot_id)
    value = get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", 'board-mode')
    if value:
        return value
    else:
        return "NONE"

def get_asic_type():
    try:
        version_info = device_info.get_sonic_version_info()        
        return version_info['asic_type']
    except (KeyError, TypeError) as e:
        log.log_error("failed to get asic type.")
        return None

def is_slot_present(slot_id):
    db = get_state_db_by_slot(slot_id)
    value = get_db_table_field(db, "LINECARD", f"LINECARD-1-{slot_id}", 'empty')
    if value == "false":
        return True
    else:
        return False
    
def get_module_ids(ctx):
    module_name = ctx.obj['module_type']
    value = ctx.obj['module_idx']
    
    if(module_name in ctx.obj):
        str_id_list =[str(module['id']) for module in ctx.obj[module_name]]
        if value == "all":
            return str_id_list
        else:
            return [value]

def show_key_value_list(target_list, dict_kvs):
    section_str = ""
    for field in target_list:
        field_name = field['Field']
        value = dict_kvs[field_name]
        section_str += field['show_name'].ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_module_info_data(slot_id, module_id, data_list, table_name):
    table_key = f'{table_name}-1-{slot_id}-{module_id}'
    dbs = get_state_db_by_slot(slot_id)
    dict_kvs = get_db_table_fields(dbs, table_name, table_key)
    show_key_value_list(data_list, dict_kvs)

def show_module_config_data(slot_id, module_id, data_list, table_name):
    table_key = f'{table_name}-1-{slot_id}-{module_id}'
    dbs = get_config_db_by_slot(slot_id)
    dict_kvs = get_db_table_fields(dbs, table_name, table_key)
    show_key_value_list(data_list, dict_kvs)

def show_module_pm_instant(slot_id, module_id, pm_list, table_name):
    section_str = ""
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_key = f"{table_name}-1-{slot_id}-{module_id}_{field['Field']}:15_pm_current"
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def run_cmd(cmd):
    print(cmd)

def show_slot_alarm_current(slot_id):
    db = get_state_db_by_slot(slot_id)
    show_db_entity_alarm_current(db, f'Slot {slot_id} Current Alarm', CURALARM)

def show_slot_alarm_history(slot_id):
    db = get_history_db_by_slot(slot_id)
    show_db_entity_alarm_history(db, f'Slot {slot_id}')
    show_db_entity_alarm_current(db, f'Slot {slot_id} History Event', HISEVENT)
    
def show_chassis_alarm_current():
    db = get_chassis_state_db()
    show_db_entity_alarm_current(db, f'System Current Alarm', CURALARM)

def show_chassis_alarm_history():
    db = get_chassis_history_db()
    show_db_entity_alarm_history(db, f'System History Alarm')
    show_db_entity_alarm_current(db, f'System History Event', HISEVENT)

def get_system_alarm_profile():
    platform = get_chassis_config_db().hget('DEVICE_METADATA|localhost', 'platform')
    path = f'/usr/share/sonic/device/{platform}/alarm_profile.json'
    if os.path.isfile(path):
        return json.load(open(path, encoding='utf-8'))

def show_db_entity_alarm_current(db, entity_name, talbe_name):
    keys = get_db_table_keys(db, talbe_name)
    click.echo(f'{entity_name} Total num: {len(keys)}')
    if not keys:
        return
    
    alarm_profile_dic = get_system_alarm_profile()
    alarms = []
    for key in keys:
        alarm = get_db_table_fields(db, talbe_name, key)
        alarm['time-created'] = int(alarm['time-created'])
        NANOSECONDS = 1000000000
        alarm['time-created-str'] = datetime.fromtimestamp(alarm['time-created']/NANOSECONDS).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        if alarm['type-id'] in alarm_profile_dic:
            alarm['sa'] = alarm_profile_dic[alarm['type-id']]["SA"]
            alarm['type'] = alarm_profile_dic[alarm['type-id']]["Type"]
            alarms.append(alarm)
        else:
            click.echo(f"Warning: invalid alarm type {alarm['type-id']}")
    sorted_alarms = sorted(alarms, key=operator.itemgetter('time-created'),reverse=True)
    
    current_alarm_header = ['id','time-created','resource','severity','type-id','text','sa','type']
    current_alarm_info = []
    index = 1
    for alarm in sorted_alarms:
        current_alarm_info.append([index, alarm['time-created-str'], alarm['resource'], alarm['severity'], alarm['type-id'], alarm['text'], alarm['sa'], alarm['type']])
        index = index + 1     
    click.echo(tabulate(current_alarm_info, current_alarm_header, tablefmt="simple"))
    click.echo("")

def show_db_entity_alarm_history(db, entity_name):
    keys = get_db_table_keys(db, HISALARM)
    click.echo(f'{entity_name} History Alarm Total num: {len(keys)}')
    if not keys:
        return
    
    alarms = []
    alarm_profile_dic = get_system_alarm_profile()
    for key in keys:
        alarm = get_db_table_fields(db, HISALARM, key)
        if(len(alarm['id'].split('#')) != 2):
            log.log_error(f"Error: invalid alarm id {alarm['id']}")
            continue
        alarm['type-id'] = alarm['id'].split('#')[1]
        alarm['time-created'] = int(alarm['time-created'])
        alarm['time-cleared'] = int(alarm['time-cleared'])
        NANOSECONDS = 1000000000
        alarm['time-created-str'] = datetime.fromtimestamp(alarm['time-created']/NANOSECONDS).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        alarm['time-cleared-str'] = datetime.fromtimestamp(alarm['time-cleared']/NANOSECONDS).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        alarm['sa'] = alarm_profile_dic[alarm['type-id']]["SA"]
        alarm['type'] = alarm_profile_dic[alarm['type-id']]["Type"]
        alarms.append(alarm)
    sorted_alarms = sorted(alarms, key=operator.itemgetter('time-created'),reverse=True)
    
    current_alarm_header = ['id','time-created','time-cleared', 'resource','severity','type-id','text','sa','type']
    current_alarm_info = []
    index = 1
    for alarm in sorted_alarms:
        current_alarm_info.append([index, alarm['time-created-str'], alarm['time-cleared-str'], alarm['resource'], alarm['severity'], alarm['type-id'], alarm['text'], alarm['sa'], alarm['type']])
        index = index + 1     
    click.echo(tabulate(current_alarm_info, current_alarm_header, tablefmt="simple"))
    click.echo("")

def show_key_value_list_with_module(target_list, dict_kvs):
    section_str = ""
    for field in target_list:
        field_name = field['Field']
        module_name = field['Module']
        if module_name in dict_kvs:
            value = dict_kvs[module_name][field_name]
            section_str += field['show_name'].ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)
   
def run_system_command(command):
    try:
        run_command(command)
    except Exception as e:
        click.echo(e)
        
def get_chassis_software_version():
    if os.path.exists('/host/aonos_installer/upgradecfg'):
        json_list = json.load(open('/host/aonos_installer/upgradecfg', encoding='utf-8'))
        upgrade_version = json_list['chassis']['ver']
    else:
        upgrade_version = ''
    return upgrade_version
    
def get_chassis_serial_number():
    db = get_chassis_state_db()
    return get_db_table_field(db, "CHASSIS", f"CHASSIS-1", 'serial-no')
    
def is_valid_time(dat,day):
    if not day:
        day = '0:0:0'
    else:
        if ':' not in day:
            day = f'{day}:0:0'
        elif len(day.split(':')) == 2:
            day = f"{day.split(':')[0]}:{day.split(':')[1]}:0"
    s_datatime = datetime.strptime(f'{dat} {day}', "%Y-%m-%d %H:%M:%S")
    l_datetime = datetime.strptime(SYSTIME_LOW, "%Y-%m-%d %H:%M:%S")
    h_datetime = datetime.strptime(SYSTIME_HIGH, "%Y-%m-%d %H:%M:%S")
    if s_datatime < l_datetime or s_datatime > h_datetime:
        return False
    return True

def is_ipaddress(val):
    """ Validate if an entry is a valid IP """
    if not val:
        return False
    try:
        netaddr.IPAddress(str(val))
    except netaddr.core.AddrFormatError:
        return False
    return True

def get_pm_instant(db, table_name, table_key):
    return get_db_table_field(db, table_name, table_key, "instant")

def run_OLSS_utils_set(slot_id, table_name, table_key, field,value):
    cmd = f'sudo test_cmd cmd -n {slot_id -1} set {table_name} {table_key} {field}={value}'
    run_command(cmd, return_cmd=True)

def run_OLSS_utils_get(slot_id, table_name, table_key, field):
    cmd = f'sudo test_cmd cmd -n {slot_id -1} get {table_name} {table_key} {field}'
    return run_command(cmd, return_cmd=True)

def run_OLSS_utils_upgrade_transceiver_download(slot_id, line_id):
    cmd = f'sudo test_cmd upgrade_transceiver -n {slot_id -1} download -s {slot_id} -l {line_id}'
    run_command(cmd, return_cmd=True)
    
def run_OLSS_utils_upgrade_transceiver_switch(slot_id, line_id, model):
    cmd = f'sudo test_cmd upgrade_transceiver -n {slot_id -1} switch -s {slot_id} -l {line_id} -p {model}'
    run_command(cmd, return_cmd=True)
    
def run_OLSS_utils_upgrade_transceiver_backup(slot_id, line_id, model):
    cmd = f'sudo test_cmd upgrade_transceiver -n {slot_id -1} backup -s {slot_id} -l {line_id} -p {model}'
    run_command(cmd, return_cmd=True)
    
def run_OLSS_utils_upgrade_transceiver_state(slot_id, line_id):
    cmd = f'sudo test_cmd upgrade_transceiver -n {slot_id -1} state -s {slot_id} -l {line_id}'
    run_command(cmd, return_cmd=True)

def run_command(command, display_cmd=False, ignore_error=False, return_cmd=False, interactive_mode=False):
    """
    Run bash command. Default behavior is to print output to stdout. If the command returns a non-zero
    return code, the function will exit with that return code.

    Args:
        display_cmd: Boolean; If True, will print the command being run to stdout before executing the command
        ignore_error: Boolean; If true, do not exit if command returns a non-zero return code
        return_cmd: Boolean; If true, the function will return the output, ignoring any non-zero return code
        interactive_mode: Boolean; If true, it will treat the process as a long-running process which may generate
                          multiple lines of output over time
    """

    if display_cmd == True:
        click.echo(click.style("Running command: ", fg='cyan') + click.style(command, fg='green'))

    proc = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE)

    if return_cmd:
        output = proc.communicate()[0]
        return output

    if not interactive_mode:
        (out, err) = proc.communicate()

        if len(out) > 0:
            if out == '{}\n':
                click.echo('get info empty')
            else:
                click.echo(out.rstrip('\n'))

        if proc.returncode != 0 and not ignore_error:
            sys.exit(proc.returncode)

        return

    # interactive mode
    while True:
        output = proc.stdout.readline()
        if output == "" and proc.poll() is not None:
            break
        if output:
            click.echo(output.rstrip('\n'))

    rc = proc.poll()
    if rc != 0:
        sys.exit(rc)
