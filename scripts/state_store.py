"""Durable portfolio and encrypted OAuth state, isolated from website source."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '_sync_state'
BRANCH = 'etsy-sync-state'


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd or ROOT, check=True, capture_output=True, text=True).stdout


def prepare():
    remote = git('ls-remote', '--heads', 'origin', BRANCH).strip()
    if remote:
        git('fetch', 'origin', BRANCH)
        git('worktree', 'add', '--detach', str(STATE), 'FETCH_HEAD')
    else:
        git('worktree', 'add', '--detach', str(STATE), 'HEAD')
        git('rm', '-r', '--ignore-unmatch', '.', cwd=STATE)


def save():
    git('add', '-A', cwd=STATE)
    if not git('diff', '--cached', '--name-only', cwd=STATE).strip():
        return
    git('-c', 'user.name=github-actions[bot]', '-c',
        'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        'commit', '-m', 'Preserve Etsy portfolio and encrypted connection state', cwd=STATE)
    git('push', 'origin', f'HEAD:refs/heads/{BRANCH}', cwd=STATE)


if __name__ == '__main__':
    try:
        {'prepare': prepare, 'save': save}[sys.argv[1]]()
    except (subprocess.CalledProcessError, KeyError, IndexError):
        sys.exit('Unable to persist synchronization state; deployment stopped.')
