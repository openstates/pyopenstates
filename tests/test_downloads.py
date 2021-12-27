from pyopenstates.downloads import (
    load_csv,
    FileType,
    load_merged_dataframe,
)


def test_load_csv():
    data = list(load_csv("al", "2021s1", FileType.Bills))
    assert len(data) == 37


def test_load_merged_dataframe_bills():
    bills_df = load_merged_dataframe("al", "2021s1", FileType.Bills)
    assert len(bills_df) == 37
    assert "title" in list(bills_df.columns)


def test_load_merged_dataframe_bills_joins():
    actions_df = load_merged_dataframe("al", "2021s1", FileType.Actions)
    assert len(actions_df) == 170
    assert "description" in list(actions_df.columns)

    sponsors_df = load_merged_dataframe("al", "2021s1", FileType.Sponsorships)
    assert len(sponsors_df) == 37
    assert "name" in list(sponsors_df.columns)

    sources_df = load_merged_dataframe("al", "2021s1", FileType.Sources)
    assert len(sources_df) == 74
    assert "url" in list(sources_df.columns)

    versions_df = load_merged_dataframe("al", "2021s1", FileType.Versions)
    assert len(versions_df) == 53
    assert "note" in list(versions_df.columns)


def test_load_merged_dataframe_version_links():
    df = load_merged_dataframe("al", "2021s1", FileType.VersionLinks)
    assert len(df) == 53
    assert "url" in list(df.columns)


def test_load_merged_dataframe_votes_joins():
    votes_df = load_merged_dataframe("al", "2021s1", FileType.Votes)
    assert len(votes_df) == 19
    assert "motion_text" in list(votes_df.columns)

    vp_df = load_merged_dataframe("al", "2021s1", FileType.VotePeople)
    assert len(vp_df) == 1480
    assert "voter_name" in list(vp_df.columns)

    vs_df = load_merged_dataframe("al", "2021s1", FileType.VoteSources)
    assert len(vs_df) == 19
    assert "url" in list(vs_df.columns)

    vs_df = load_merged_dataframe("al", "2021s1", FileType.VoteCounts)
    assert len(vs_df) == 19 * 3
    assert "option" in list(vs_df.columns)
