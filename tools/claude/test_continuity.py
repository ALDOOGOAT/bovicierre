"""Pruebas de checkpoint.py y resume-check.py con estado/reloj simulados (no tocan la campaña real)."""
import datetime as dt
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cp = load('checkpoint', 'checkpoint.py')
rc = load('resume_check', 'resume-check.py')


def save_args(**kw):
    base = dict(status='S1_RUNNING', block=None, add_minutes=0, base=None, quota=None, done=None, pending=None,
                verification=None, next=None, risk=None, continuation=False, dispatch_transition=False, force=False)
    base.update(kw)
    return SimpleNamespace(**base)


class Continuity(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / 'repo'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)
        subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/ALDOOGOAT/bovicierre.git'], cwd=self.repo, check=True)
        subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q', '--allow-empty', '-m', 'x'], cwd=self.repo, check=True)
        (self.repo / 'docs/continuity').mkdir(parents=True)
        (self.repo / 'docs/continuity/campaign.marker').write_text('uiux-qa-claude-1.0\n')
        os.environ['BOVI_CLAUDE_STATE'] = str(self.tmp / 'state')
        self.rc = rc
        self.rc.cp = cp

    def tearDown(self):
        os.environ.pop('BOVI_CLAUDE_STATE', None)
        shutil.rmtree(self.tmp)

    def test_other_repo_does_not_activate(self):
        other = self.tmp / 'other'
        other.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=other, check=True)
        code, msg = rc.evaluate(other, 'a')
        self.assertEqual(code, 2)
        self.assertIn('no autorizado', msg)

    def test_no_checkpoint_does_not_invent_task(self):
        code, msg = rc.evaluate(self.repo, 'a')
        self.assertEqual(code, 2)
        self.assertIn('sin checkpoint', msg)

    def test_stop_blocks_resume_and_save(self):
        cp.checkpoint(save_args(next=['seguir']), self.repo)
        (cp.state_dir(self.repo) / 'STOP').touch()
        self.assertEqual(rc.evaluate(self.repo, 'a')[0], 2)
        with self.assertRaises(SystemExit):
            cp.checkpoint(save_args(), self.repo)

    def test_terminal_state_not_resumed(self):
        cp.checkpoint(save_args(status='USER_STOPPED'), self.repo)
        self.assertEqual(rc.evaluate(self.repo, 'a')[0], 2)
        with self.assertRaises(SystemExit):
            cp.checkpoint(save_args(status='S2_RUNNING'), self.repo)

    def test_two_sessions_cannot_share_lock(self):
        cp.checkpoint(save_args(next=['seguir']), self.repo)
        self.assertEqual(rc.evaluate(self.repo, 'sesion-1')[0], 0)
        self.assertEqual(rc.evaluate(self.repo, 'sesion-2')[0], 3)
        self.assertTrue(cp.release_lock('sesion-1', self.repo))
        self.assertEqual(rc.evaluate(self.repo, 'sesion-2')[0], 0)

    def test_expired_lock_is_reclaimed(self):
        old = lambda: dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        self.assertTrue(cp.acquire_lock('vieja', self.repo, clock=old))
        self.assertTrue(cp.acquire_lock('nueva', self.repo))

    def test_corrupt_checkpoint_is_not_trusted(self):
        (cp.state_dir(self.repo) / 'state.json').write_text('{"campaign": "uiux-qa')  # escritura truncada
        code, msg = rc.evaluate(self.repo, 'a')
        self.assertEqual(code, 2)
        self.assertIn('sin checkpoint', msg)

    def test_unknown_quota_stays_unknown(self):
        state = cp.checkpoint(save_args(), self.repo)
        self.assertEqual(state['quota'], 'desconocido')

    def test_minutes_accumulate_per_block_and_transition_once(self):
        cp.checkpoint(save_args(block='S1', add_minutes=30), self.repo)
        s = cp.checkpoint(save_args(block='S1', add_minutes=20, dispatch_transition=True), self.repo)
        s = cp.checkpoint(save_args(status='S2_QUEUED'), self.repo)
        self.assertEqual(s['active_minutes'], {'S1': 50})
        self.assertTrue(s['transition_dispatched'])

    def test_continuation_limit(self):
        cp.checkpoint(save_args(status='WAITING_RESET', continuation=True), self.repo)
        cp.checkpoint(save_args(status='WAITING_RESET', continuation=True), self.repo)
        self.assertEqual(rc.evaluate(self.repo, 'a')[0], 2)

    def test_atomic_write_leaves_no_temp_on_failure(self):
        target = self.tmp / 'x.json'
        with self.assertRaises(TypeError):
            cp.atomic_write(target, None)
        self.assertFalse(target.exists())
        self.assertEqual([p for p in self.tmp.iterdir() if p.name.startswith('.x.json')], [])


if __name__ == '__main__':
    unittest.main()
