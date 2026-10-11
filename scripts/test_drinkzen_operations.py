"""验证台账的版本漂移、发布历史和未知指标语义，全程离线。"""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("drinkzen_operations", Path(__file__).with_name("drinkzen-operations.py"))
ops = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ops)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(ops, "ROOT", tmp_path)
    article = tmp_path / "content/drinkzen/brand/coffee/index.md"
    article.parent.mkdir(parents=True)
    article.write_text("---\ntitle: Coffee\n---\n\n已核实原稿\n\n## plog 分发版\n\n共用文案\n")
    return tmp_path, article, tmp_path / "ledger.json"


def invoke(monkeypatch, ledger, *args):
    monkeypatch.setattr("sys.argv", ["drinkzen-operations.py", "--ledger", str(ledger), *args])
    ops.main()


def record(monkeypatch, ledger, article, platform="xiaohongshu"):
    domain = "www.xiaohongshu.com" if platform == "xiaohongshu" else "www.dianping.com"
    invoke(monkeypatch, ledger, "record", "--article", str(article), "--platform", platform,
           "--url", f"https://{domain}/test", "--published-at", "2026-10-11T11:30:00+08:00", "--note", "离线测试记录")


def test_missing_records_do_not_infer_publication(workspace):
    _, _, ledger = workspace
    rows = ops.collect_status(ops.load_ledger(ledger))
    assert rows[0]["product_id"] is None
    assert set(rows[0]["platforms"].values()) == {"未登记"}
    assert not ledger.exists()


@pytest.mark.parametrize("changed", ["origin", "plog"])
def test_changes_make_both_platforms_stale(workspace, monkeypatch, changed):
    _, article, ledger = workspace
    record(monkeypatch, ledger, article)
    record(monkeypatch, ledger, article, "dianping")
    assert set(ops.collect_status(ops.load_ledger(ledger))[0]["platforms"].values()) == {"已登记当前版本"}
    source = article.read_text()
    article.write_text(source.replace("已核实原稿", "更新原稿") if changed == "origin" else source + "更新共用文案\n")
    assert set(ops.collect_status(ops.load_ledger(ledger))[0]["platforms"].values()) == {"待同步"}
    record(monkeypatch, ledger, article)
    row = ops.collect_status(ops.load_ledger(ledger))[0]
    assert row["platforms"] == {"xiaohongshu": "已登记当前版本", "dianping": "待同步"}
    entry = next(iter(ops.load_ledger(ledger)["articles"].values()))
    assert len(entry["platforms"]["xiaohongshu"]["history"]) == 2


def test_metrics_preserve_unknowns_and_history(workspace, monkeypatch):
    _, article, ledger = workspace
    record(monkeypatch, ledger, article)
    for likes in (0, 5):
        invoke(monkeypatch, ledger, "metrics", "--article", str(article), "--platform", "xiaohongshu",
               "--observed-at", "2026-10-12T11:30:00+08:00", "--likes", str(likes), "--note", "测试观测")
    entry = next(iter(ops.load_ledger(ledger)["articles"].values()))
    metrics = entry["platforms"]["xiaohongshu"]["metrics"]
    assert [m["likes"] for m in metrics] == [0, 5]
    assert metrics[0]["views"] is None
    assert metrics[0]["publication_index"] == 0


def test_invalid_record_does_not_modify_ledger(workspace, monkeypatch):
    _, article, ledger = workspace
    record(monkeypatch, ledger, article)
    original = ledger.read_bytes()
    with pytest.raises(SystemExit):
        invoke(monkeypatch, ledger, "record", "--article", str(article), "--platform", "xiaohongshu",
               "--url", "https://xiaohongshu.com.evil.example/test", "--published-at", "2026-10-11T11:30:00+08:00", "--note", "错误链接")
    assert ledger.read_bytes() == original
    with pytest.raises(ValueError):
        ops.timestamp("2026-10-11T11:30:00")


def test_followup_and_product_link_do_not_mark_platform_published(workspace, monkeypatch):
    _, article, ledger = workspace
    invoke(monkeypatch, ledger, "link", "--article", str(article), "--product-id", "p1",
           "--menu-evidence", "menu.png", "--menu-checked-at", "2026-10-11")
    invoke(monkeypatch, ledger, "note", "--article", str(article), "--text", "菜单变化待核对")
    row = ops.collect_status(ops.load_ledger(ledger))[0]
    assert row["product_id"] == "p1"
    assert row["followup"] == "菜单变化待核对"
    assert set(row["platforms"].values()) == {"未登记"}
    invoke(monkeypatch, ledger, "note", "--article", str(article), "--resolved")
    assert ops.collect_status(ops.load_ledger(ledger))[0]["followup"] is None


def test_deleted_article_remains_actionable(workspace, monkeypatch):
    _, article, ledger = workspace
    record(monkeypatch, ledger, article)
    article.unlink()
    row = ops.collect_status(ops.load_ledger(ledger))[0]
    assert row["problem"]
    assert row["platforms"]["xiaohongshu"] == "待同步"


def test_partial_menu_evidence_keeps_product_unknown(workspace, monkeypatch):
    _, article, ledger = workspace
    invoke(monkeypatch, ledger, "link", "--article", str(article),
           "--menu-evidence", "menu.png", "--menu-checked-at", "2026-10-11")
    row = ops.collect_status(ops.load_ledger(ledger))[0]
    assert row["product_id"] is None
    assert row["menu_checked_at"] == "2026-10-11"


def test_metrics_require_publication_and_valid_time(workspace, monkeypatch):
    _, article, ledger = workspace
    args = ("metrics", "--article", str(article), "--platform", "xiaohongshu",
            "--observed-at", "2026-10-10T11:30:00+08:00", "--likes", "2", "--note", "测试")
    with pytest.raises(SystemExit):
        invoke(monkeypatch, ledger, *args)
    assert not ledger.exists()
    record(monkeypatch, ledger, article)
    original = ledger.read_bytes()
    with pytest.raises(SystemExit):
        invoke(monkeypatch, ledger, *args)
    assert ledger.read_bytes() == original
