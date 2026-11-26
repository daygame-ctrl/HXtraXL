"""The whole build from stock 3.80.0 firmware. Set HX_STOMP_HXF or HX_EFFECTS_HXF
to your stock file. The build is deterministic, so the output's
MD5 is pinned: a change to any byte of the firmware fails here until BUILT_MD5
is updated on purpose."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.firmware

# The ten-knob NAM A2 Lite with its tone stack in Amp > NAM on Xenomorph Fuzz Mono's ID 555 (build.py's STEPS),
# the kernel's --mid-sweep, DSP cost 2275, tools/patch_menu.py's HXtra entry and boot screen.
BUILT_MD5 = {
    "HX_STOMP_HXF": "a070c1ddaf5d656d195f16d3e784a540",
    "HX_EFFECTS_HXF": "1c6c0ac2cf65cd42a4a74d57542d56f1",
}


@pytest.mark.parametrize("env", BUILT_MD5)
def test_build(tmp_path, env):
    stock = os.environ.get(env)
    if not stock:
        pytest.skip(f"{env} is not set")
    out = tmp_path / "out.hxf"
    r = subprocess.run([sys.executable, str(ROOT / "build.py"), stock, "-o", str(out), "--no-check"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ALL OK" in r.stdout
    assert hashlib.md5(out.read_bytes()).hexdigest() == BUILT_MD5[env]

