import click
import socket
import struct

from otn.utils.utils import *
#####################################upgrade########################################################
@click.group("upgrade")
@click.pass_context
def slot_upgrade(ctx):
    pass

@slot_upgrade.command('auto')
@click.argument('file',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def slot_upgrade_auto(ctx, file, uname, password):
    slot_id = ctx.obj['slot_idx']
    ip_addr = CU_IP_INTERNAL
    ip = struct.unpack('I', socket.inet_aton(ip_addr))[0]
    
    try:
        file_path = os.path.dirname(file)
        file_name = os.path.basename(file)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'host-ip', ip)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'user-name', uname)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'user-password', password)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-file-name', file_name)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-file-path', file_path)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-auto', 'true')
    except Exception as e:
        click.echo(e)

@slot_upgrade.command('download')
@click.argument('file',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def slot_upgrade_download(ctx, file, uname, password):
    slot_id = ctx.obj['slot_idx']
    ip_addr = CU_IP_INTERNAL
    ip = struct.unpack('I', socket.inet_aton(ip_addr))[0]
    try:
        file_path = os.path.dirname(file)
        file_name = os.path.basename(file)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'host-ip', ip)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'user-name', uname)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'user-password', password)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-file-name', file_name)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-file-path', file_path)
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-download', 'true')
        click.echo(f'slot {slot_id} Download Successed')
    except Exception as e:
        click.echo(e)


@slot_upgrade.command("commit")
@click.pass_context
def slot_upgrade_commit(ctx):
    slot_id = ctx.obj['slot_idx']
    try:
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-commit', 'true')
        click.echo(f'Trigger slot {slot_id} Committing Successed')
    except Exception as e:
        click.echo(e)

@slot_upgrade.command("reboot")
@click.pass_context
def slot_upgrade_reboot(ctx):
    slot_id = ctx.obj['slot_idx']
    try:
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-reboot', 'true')
        click.echo(f'Reboot slot {slot_id}...wait for a moment')
    except Exception as e:
        click.echo(e)

@slot_upgrade.command('commit-pause')
@click.pass_context
def slot_upgrade_commit_pause(ctx):
    slot_id = ctx.obj['slot_idx']
    try:
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-commit-pause', 'true')
        click.echo(f'Trigger slot {slot_id} Commit-pause Successed')
    except Exception as e:
        click.echo(e)

@slot_upgrade.command('commit-resume')
@click.pass_context
def slot_upgrade_commit_resume(ctx):
    slot_id = ctx.obj['slot_idx']
    try:
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-commit-resume', 'true')
        click.echo(f'Trigger slot {slot_id} Commit-resume Successed')
    except Exception as e:
        click.echo(e)

@slot_upgrade.command('rollback')
@click.pass_context
def slot_upgrade_rollback(ctx):
    slot_id = ctx.obj['slot_idx']
    try:
        run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-rollback', 'true')
        click.echo(f'Trigger slot {slot_id} Rollback Successed')
    except Exception as e:
        click.echo(e)

@click.group("upgrade")
@click.pass_context
def show_slot_upgrade(ctx):
    pass

@show_slot_upgrade.command('state')
@click.pass_context
def slot_upgrade_state(ctx):
    try:
        slot_id = ctx.obj['slot_idx']
        value = get_slot_upgrade_state(slot_id)
        click.echo(f"Slot {slot_id} "+'Upgrade State'.ljust(40) + f":  {value}")
    except Exception as e:
        click.echo(f'{e}  Query Failed, Wait for a moment and then try again.')

def get_slot_upgrade_state(slot_id):
    state = run_OLSS_utils_get(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'upgrade-state')
    return state.strip()