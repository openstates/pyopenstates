import csv
import io
import pathlib
import requests
import tempfile
import zipfile
from enum import Enum

from .core import get_metadata

TEMP_PATH = pathlib.Path(tempfile.gettempdir()) / "OS_ZIP_CACHE"


class FileType(Enum):
    """
    enum specifying the various types of files available from the CSV bulk data:

    - `Bills`
    - `Actions`
    - `Sources`
    - `Sponsorships`
    - `Versions`
    - `VersionLinks`
    - `Votes`
    - `VotePeople`
    - `VoteSources`
    - `Organizations`
    - `People`
    """

    Bills = "_bills.csv"
    Actions = "_bill_actions.csv"
    Sources = "_bill_sources.csv"
    Sponsorships = "_bill_sponsorships.csv"
    Versions = "_bill_versions.csv"
    VersionLinks = "_bill_version_links.csv"
    Votes = "_votes.csv"
    VotePeople = "_vote_people.csv"
    VoteSources = "_vote_sources.csv"
    VoteCounts = "_vote_counts.csv"
    Organizations = "_organizations.csv"
    People = "people not in zip"  # will be special cased


def _get_download_url(jurisdiction: str, session: str) -> str:
    sessions = get_metadata(jurisdiction, include="legislative_sessions")[
        "legislative_sessions"
    ]
    for ses in sessions:
        if ses["identifier"] == session:
            break
    else:
        raise ValueError("invalid session")
    return ses["downloads"][0]["url"]


def _download_zip(url: str) -> pathlib.Path:
    filename = url.split("/")[-1]
    local_path = TEMP_PATH / filename
    TEMP_PATH.mkdir(parents=True, exist_ok=True)
    if not local_path.exists():
        with open(local_path, "wb") as f:
            f.write(requests.get(url).content)
    return local_path


def _load_session_data(state: str, session: str, file_type: FileType) -> str:
    if file_type == FileType.People:
        return requests.get(
            f"https://data.openstates.org/people/current/{state}.csv"
        ).text
    url = _get_download_url(state, session)
    zip_path = _download_zip(url)
    with zipfile.ZipFile(zip_path) as zf:
        for filename in zf.namelist():
            if filename.endswith(file_type.value):
                break
        else:
            raise ValueError(f"no file of type {file_type} in {zip_path}")
        with zf.open(filename) as df:
            return df.read().decode()


def load_csv(state: str, session: str, file_type: FileType):
    """
    Returns an instantiated `csv.DictReader` to iterate over the requested file.
    """
    data = _load_session_data(state, session, file_type)
    return csv.DictReader(io.StringIO(data))


def load_merged_dataframe(state: str, session: str, which: FileType):
    """
    Returns a populated `pandas.DataFrame` with the requested content.

    `FileType.Actions`, `FileType.Sources`, `FileType.Versions`, `FileType.Sponsorships`
    will be merged against a `FileType.Bills` dataframe.

    `FileType.VersionLinks` will be  merged against both a `FileType.Versions`
    and `FileType.Bills` dataframe.

    `FileType.VotePeople`, `FileType.VoteCounts`, and `FileType.VoteSources`
    will be merged against a `FileType.Votes` dataframe.

    Other types will be returned as-is.
    """
    import pandas as pd

    other_df = pd.DataFrame(load_csv(state, session, which))

    if which in (
        FileType.Actions,
        FileType.Sources,
        FileType.Versions,
        FileType.Sponsorships,
    ):
        # these merge to Bills
        main_df = pd.DataFrame(load_csv(state, session, FileType.Bills))
        return main_df.merge(
            other_df,
            left_on="id",
            right_on="bill_id",
            how="left",
            suffixes=["_bill", ""],
        )
    elif which == FileType.VersionLinks:
        main_df = pd.DataFrame(load_csv(state, session, FileType.Bills))
        versions_df = pd.DataFrame(load_csv(state, session, FileType.Versions))
        main_df = main_df.merge(
            versions_df,
            left_on="id",
            right_on="bill_id",
            how="left",
            suffixes=["_bill", "_version"],
        )
        return main_df.merge(
            other_df,
            left_on="id_version",
            right_on="version_id",
            how="left",
            suffixes=["", "_link"],
        )
    elif which in (FileType.VotePeople, FileType.VoteSources, FileType.VoteCounts):
        main_df = pd.DataFrame(load_csv(state, session, FileType.Votes))
        return main_df.merge(
            other_df,
            left_on="id",
            right_on="vote_event_id",
            how="left",
            suffixes=["_vote", ""],
        )
    else:
        return other_df
