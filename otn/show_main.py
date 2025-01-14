import click

from otn.slot import slot
from otn.chassis import chassis
from otn.utils.utils import load_chassis_capability
from otn import alarm

def add_otn_show_commands(show):
    show.add_command(chassis.chassis)
    show.add_command(slot.slot)
    show.add_command(alarm.alarm)
    
def add_otn_show_context(ctx):
    ctx.obj = {}
    load_chassis_capability(ctx)