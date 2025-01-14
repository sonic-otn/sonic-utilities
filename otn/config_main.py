import click

from swsscommon.swsscommon import ConfigDBConnector, SonicDBConfig
from swsscommon.swsscommon import SonicV2Connector

from otn.slot import slot
from otn.chassis import chassis
from otn.utils.utils import load_chassis_capability

def add_otn_config_commands(config):
    config.add_command(chassis.cfg_chassis)
    config.add_command(slot.cfg_slot)

def add_otn_config_context(ctx):
    ctx.obj = {}
    load_chassis_capability(ctx)
