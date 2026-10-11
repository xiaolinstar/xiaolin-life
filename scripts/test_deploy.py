"""离线验证部署顺序与提交绑定，不连接生产服务器。"""

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("pull_fails", [False, True])
def test_deploy_pins_sha_and_pulls_before_checkout(tmp_path, pull_fails):
    workflow = (ROOT / ".github/workflows/cd-ghcr.yml").read_text()
    script = textwrap.dedent(workflow.split("          script: |\n", 1)[1])
    script = script.replace("${{ env.SERVER_DIR }}", f'"{tmp_path}"')
    mock_bin = tmp_path / "bin"
    mock_bin.mkdir()
    for name, body in {
        "git": 'printf "git %s\\n" "$*" >> "$TEST_LOG"',
        "docker": (
            'printf "docker tag=%s %s\\n" "$WEBSITE_IMAGE_TAG" "$*" >> "$TEST_LOG"\n'
            'if [[ "$1" == pull && "$TEST_PULL_FAILS" == yes ]]; then exit 1; fi'
        ),
    }.items():
        executable = mock_bin / name
        executable.write_text("#!/usr/bin/env bash\n" + body + "\n")
        executable.chmod(0o755)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "wait-healthy.sh").write_text('printf "healthy\\n" >> "$TEST_LOG"\n')
    sha = "a" * 40
    env = {
        **os.environ,
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "DEPLOY_SHA": sha,
        "TEST_LOG": str(tmp_path / "operations"),
        "TEST_PULL_FAILS": "yes" if pull_fails else "no",
    }
    result = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
    operations = (tmp_path / "operations").read_text().splitlines()
    assert operations[0] == f"docker tag=sha-{sha} pull ghcr.nju.edu.cn/xiaolinstar/xiaolin-life:sha-{sha}"
    if pull_fails:
        assert result.returncode != 0
        assert len(operations) == 1
    else:
        assert result.returncode == 0, result.stderr
        assert operations[2] == f"git -c submodule.recurse=false checkout --detach {sha}"
        assert operations[3] == f"docker tag=sha-{sha} compose -f compose.yaml up -d"
        assert operations[4] == "healthy"
