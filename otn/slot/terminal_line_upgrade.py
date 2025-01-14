import click

from otn.utils.utils import *

@click.group()
@click.pass_context
def upgrade(ctx):
    pass

@upgrade.command()
@click.pass_context
def download(ctx,line_id):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    
    for line_id in line_ids:
        run_OLSS_utils_upgrade_transceiver_download(slot_id, line_id)

@upgrade.command()
@click.argument('model',type=click.Choice(['A','B']),required=True)
@click.pass_context
def switch(ctx,model):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    
    for line_id in line_ids:
        run_OLSS_utils_upgrade_transceiver_switch(slot_id, line_id, model)

@upgrade.command()
@click.argument('model',type=click.Choice(['A2B','B2A']),required=True)
@click.pass_context
def copy(ctx,line_id,model):
    if model == 'A2B':
        model = 'A'
    else:
        model = 'B'
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    
    for line_id in line_ids:
        run_OLSS_utils_upgrade_transceiver_backup(slot_id, line_id, model)

@click.group("upgrade")
@click.pass_context
def show_upgrade(ctx):
    pass

@show_upgrade.command()
@click.pass_context
def state(ctx):
    slot_id = ctx.obj['slot_idx']
    line_ids = get_module_ids(ctx)
    
    for line_id in line_ids:
        run_OLSS_utils_upgrade_transceiver_state(slot_id, line_id)