from pyopenstates.downloads import load_session_csv, FileType


def test_load_session_csv():
    data = list(load_session_csv("al", "2021s1", FileType.Bills))
    assert len(data) == 37
