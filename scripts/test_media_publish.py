"""离线验证上传、校验、Markdown 改写使用相同对象键。"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("page", "prefix", "key"),
    [
        ("life/trip", "life", "life/trip"),
        ("drinkzen/manner/coffee", "life", "life/drinkzen/manner/coffee"),
        ("office/email", "life", "life/office/email"),
        ("office/email", "/docs/", "docs/office/email"),
        ("docs/guide", "docs", "docs/guide"),
    ],
)
def test_publish_upload_verify_rewrite_agree(tmp_path, page, prefix, key):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "lib").mkdir()
    for name in ("media-publish.sh", "upload-media-cos.sh", "rewrite-media-urls.py", "lib/cos-config.sh"):
        shutil.copy2(ROOT / "scripts" / name, scripts / name)
    article = tmp_path / "content" / page
    (article / "gallery").mkdir(parents=True)
    (article / "gallery" / "photo.jpg").write_bytes(b"test image")
    index = article / "index.md"
    index.write_text('{{< carousel images="gallery/*" interval="4500" >}}\n')
    mock_bin = tmp_path / "bin"
    mock_bin.mkdir()
    for name, body in {
        "coscli": 'printf "%s\\n" "$@" > "$TEST_LOG_DIRECTORY/upload"',
        "curl": 'printf "%s\\n" "$@" > "$TEST_LOG_DIRECTORY/verify"; printf "HTTP/1.1 200 OK\\r\\n"',
    }.items():
        executable = mock_bin / name
        executable.write_text("#!/usr/bin/env bash\n" + body + "\n")
        executable.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{mock_bin}:{os.environ['PATH']}",
        "COS_CONFIG_PATH": str(tmp_path / "missing-config.yaml"),
        "COS_BUCKET_ALIAS": "test-bucket",
        "COS_BUCKET_NAME": "test-bucket",
        "COS_ENDPOINT": "cos.example.com",
        "COS_PREFIX": prefix,
        "MEDIA_CDN_BASE": "https://media.example.com",
        "TEST_LOG_DIRECTORY": str(tmp_path),
    }
    subprocess.run(
        ["bash", str(scripts / "media-publish.sh"), str(article), "--rewrite"],
        env=env, check=True, capture_output=True, text=True,
    )
    assert f"cos://test-bucket/{key}/" in (tmp_path / "upload").read_text().splitlines()
    url = f"https://media.example.com/{key}/photo.jpg"
    assert url in (tmp_path / "verify").read_text().splitlines()
    assert f'images="{{{url}}}"' in index.read_text()
    assert 'interval="4500"' in index.read_text()
