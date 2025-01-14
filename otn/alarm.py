import os
import click

from tabulate import tabulate
from otn.utils.utils import *

################################### show #########################################################
@click.group()
@click.pass_context
def alarm(ctx):
    pass

@alarm.command()
def current():
    for slot_id in get_linecard_slot_range():
        show_slot_alarm_current(slot_id)
    show_chassis_alarm_current()

@alarm.command()
def history():
    for slot_id in get_linecard_slot_range():
        show_slot_alarm_history(slot_id)
    show_chassis_alarm_history()

@alarm.command()
def profile():
    alarm_profile_dic = get_system_alarm_profile()
    alarm_profile_header = ['Name','Severity','SA','Type', 'Detail']
    alarm_profile_info = []
    for alarm, profile in alarm_profile_dic.items():
        alarm_profile_info.append([alarm, profile['Severity'], profile['SA'], profile['Type'], profile['Detail']])
    click.echo(tabulate(alarm_profile_info, alarm_profile_header, tablefmt="simple"))
    click.echo("")