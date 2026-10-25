"""验证预构建保留作者封面，同时继续为缺少封面的页面生成占位图。"""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def featured(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "setup_featured_images", Path(__file__).with_name("setup-featured-images.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CONTENT", tmp_path / "content")
    monkeypatch.setattr(module, "PHOTOS", tmp_path / "assets/img/photos")
    module.PHOTOS.mkdir(parents=True)
    (module.PHOTOS / module.DEFAULT_PHOTO).write_bytes(b"default photo")
    return module


@pytest.mark.parametrize("image", ["featured.jpg", "gallery/cover.jpg", "img/cover.jpg"])
def test_preserves_explicit_local_cover_on_repeated_builds(featured, image):
    page = featured.CONTENT / "movies/shawshank-redemption"
    page.mkdir(parents=True)
    index = page / "index.md"
    index.write_text(f'---\nfeatureimage: "{image}"\n---\n', encoding="utf-8")
    cover = (featured.ROOT / "assets" if image.startswith("img/") else page) / image
    cover.parent.mkdir(parents=True, exist_ok=True)
    cover.write_bytes(b"movie cover")
    background = page / "background.jpg"
    background.write_bytes(b"movie background")

    for _ in range(2):
        featured.setup_page(page, index)
        assert cover.read_bytes() == b"movie cover"
        assert background.read_bytes() == b"movie background"


@pytest.mark.parametrize("featureimage", ["", 'featureimage: "missing.jpg"\n'])
def test_generates_fallback_when_cover_is_missing(featured, featureimage):
    page = featured.CONTENT / "movies/example"
    page.mkdir(parents=True)
    index = page / "index.md"
    index.write_text(f"---\n{featureimage}---\n", encoding="utf-8")

    featured.setup_page(page, index)

    assert (page / "featured.jpg").read_bytes() == b"default photo"


def test_remote_cover_still_removes_generated_placeholder(featured):
    page = featured.CONTENT / "movies/example"
    page.mkdir(parents=True)
    index = page / "index.md"
    index.write_text(
        '---\nfeatureimage: "https://media.example.com/cover.jpg"\n---\n',
        encoding="utf-8",
    )
    (page / "featured.jpg").write_bytes(b"old placeholder")

    featured.setup_page(page, index)

    assert not (page / "featured.jpg").exists()
