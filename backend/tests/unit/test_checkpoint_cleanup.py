from types import SimpleNamespace

from langgraph.checkpoint.memory import MemorySaver
from app.modules.interview.graph import clear_session_checkpoints


def test_cleanup_releases_all_memory_stores_for_only_the_owned_thread():
    cp = MemorySaver()
    cp.storage["finished"] = {"data": "private"}
    cp.storage["other"] = {"data": "active"}
    cp.blobs[("finished", "", "channel", "1")] = ("bytes", b"private answer")
    cp.blobs[("other", "", "channel", "1")] = ("bytes", b"active answer")
    cp.writes[("finished", "", "checkpoint")] = {}
    cp.writes[("other", "", "checkpoint")] = {}
    clear_session_checkpoints(["finished"], cp)
    clear_session_checkpoints(["finished"], cp)
    assert "finished" not in cp.storage and "other" in cp.storage
    assert all(key[0] == "other" for key in cp.blobs)
    assert all(key[0] == "other" for key in cp.writes)


def test_legacy_test_double_also_removes_blobs():
    cp = SimpleNamespace(storage={"old": 1}, writes={("old", "checkpoint"): 1}, blobs={("old", "value"): b"private"})
    clear_session_checkpoints(["old"], cp)
    assert not cp.storage and not cp.writes and not cp.blobs
