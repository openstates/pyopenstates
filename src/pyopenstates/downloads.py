import csv
import io
import pathlib
import requests
import tempfile
import zipfile
from enum import Enum

from .config import ENVIRON_API_KEY

TEMP_PATH = pathlib.Path(tempfile.gettempdir()) / "OS_ZIP_CACHE"


class FileType(Enum):
    Bills = "_bills.csv"
    Actions = "_bill_actions.csv"
    Sources = "_bill_sources.csv"
    Sponsorships = "_bill_sponsorships.csv"
    Versions = "_bill_versions.csv"
    VersionLinks = "_bill_version_links.csv"
    Votes = "_votes.csv"
    VotePeople = "_vote_people.csv"
    VoteSources = "_vote_sources.csv"
    Organizations = "_organizations.csv"


def _get_download_url(jurisdiction: str, session: str) -> str:
    url = f"https://v3.openstates.org/jurisdictions/{jurisdiction}?apikey={ENVIRON_API_KEY}&include=legislative_sessions"
    sessions = requests.get(url).json()["legislative_sessions"]
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


def load_session_csv(state: str, session: str, file_type: FileType):
    data = _load_session_data(state, session, file_type)
    return csv.DictReader(io.StringIO(data))
