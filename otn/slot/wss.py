import click

from otn.utils.utils import DynamicModuleIdxAllChoice

@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('wss'), required=True)
def wss(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'wss'

@wss.command()
@click.pass_context
def info(ctx):
    click.echo(f"show slot {ctx.obj['slot_idx']} {ctx.obj['module_type']} {ctx.obj['module_idx']} info")
