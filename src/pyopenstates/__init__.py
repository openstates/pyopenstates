# -*- coding: utf-8 -*-

"""A Python client for the Open States API"""

import dateutil.parser
from requests import Session
from time import sleep

"""Copyright 2016 Sean Whalen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

from .config import (  # noqa
    __version__,
    API_ROOT,
    DEFAULT_USER_AGENT,
    API_KEY_ENV_VAR,
    ENVIRON_API_KEY,
)

session = Session()
session.headers.update({"Accept": "application/json"})
session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
if ENVIRON_API_KEY:
    session.headers.update({"X-Api-Key": ENVIRON_API_KEY})
else:
    print(f"Warning: No API Key found, set {API_KEY_ENV_VAR}")


class APIError(RuntimeError):
    """
    Raised when the Open States API returns an error
    """

    pass


class NotFound(APIError):
    """Raised when the API cannot find the requested object"""

    pass


def _make_params(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


def _get(uri, params=None):
    """
    An internal method for making API calls and error handling easy and
    consistent

    Args:
        uri: API URI
        params: GET parameters

    Returns:
        JSON as a Python dictionary
    """

    def _convert_timestamps(result):
        """Converts a string timestamps from an api result API to a datetime"""
        if isinstance(result, dict):
            for key in result.keys():
                if key in (
                    "created_at",
                    "updated_at",
                    "latest_people_update",
                    "latest_bill_update",
                ):
                    try:
                        result[key] = dateutil.parser.parse(result[key])
                    except ValueError:
                        pass
                elif isinstance(result[key], dict):
                    result[key] = _convert_timestamps(result[key])
                elif isinstance(result[key], list):
                    result[key] = [_convert_timestamps(r) for r in result[key]]
        elif isinstance(result, list):
            result = [_convert_timestamps(r) for r in result]

        return result

    def _convert(result):
        """Convert results to standard Python data structures"""
        result = _convert_timestamps(result)
        return result

    url = f"{API_ROOT}/{uri}"
    for param in params.keys():
        if isinstance(params[param], list):
            params[param] = ",".join(params[param])
    response = session.get(url, params=params)
    if response.status_code != 200:
        if response.status_code == 404:
            raise NotFound(f"Not found: {response.url}")
        else:
            raise APIError(response.text)
    return _convert(response.json())


def set_user_agent(user_agent):
    """Appends a custom string to the default User-Agent string
    (e.g. ``pyopenstates/__version__ user_agent``)"""
    session.headers.update({"User-Agent": f"{DEFAULT_USER_AGENT} {user_agent}"})


def set_api_key(apikey):
    """Sets API key. Can also be set as OPENSTATES_API_KEY environment
    variable."""
    session.headers["X-Api-Key"] = apikey


def get_metadata(state=None, fields=None):
    """
        Returns a list of all states with data available, and basic metadata
        about their status. Can also get detailed metadata for a particular
        state.

    Args:
        state: The abbreviation of state to get detailed metadata on, or leave
        as None to get high-level metadata on all states.

        fields: An optional list of fields to return; returns all fields by
            default

    Returns:
       Dict: The requested :ref:`Metadata` as a dictionary
    """
    uri = "jurisdictions"
    params = dict()
    if state:
        uri += "/" + _jurisdiction_id(state)
        state_response = _get(uri, params=params)
        if fields is not None:
            return {k: state_response[k] for k in fields}
        else:
            return state_response
    else:
        params["page"] = "1"
        params["per_page"] = "52"
        return _get(uri, params=params)["results"]


def get_organizations(state):
    uri = "jurisdictions"
    uri += "/" + _jurisdiction_id(state)
    state_response = _get(uri, params={"include": "organizations"})
    return state_response["organizations"]


def search_bills(**kwargs):
    """
    Find bills matching a given set of filters

    Args:
        **kwargs: One or more search filters

    - ``state`` - Only return bills from a given state (e.g. ``nc``)
    - ``chamber`` - Only return bills matching the provided chamber
    (``upper`` or ``lower``)
    - ``bill_id`` - Only return bills with a given bill_id.
    - ``bill_id_in`` - Accepts a pipe (|) delimited list of bill ids.
    - ``q`` -  Only return bills matching the provided full text query.
    - ``search_window``- By default all bills are searched, but if a time
    window is desired the following options can be passed to
    ``search_window``:
        - ``search_window="all"`` - Default, include all sessions.
        - ``search_window="session"`` - Only bills from sessions within the
        current session.
        - ``search_window="session"`` - Only bills from the current session.
        - ``search_window="session:2009"`` - Only bills from the session named
        ``2009``.
        - ``search_window="term:2009-2011"`` - Only bills from the sessions in
        the ``2009-2011`` session.
    - ``updated_since`` - Only bills updated since a provided date (provided in
    ``YYYY-MM-DD`` format)
    - ``sponsor_id`` Only bills sponsored by a given legislator id (e.g.
    ``ILL000555``)
    - ``subject`` - Only bills categorized by Open States as belonging to this
    subject.
    - ``type`` Only bills of a given type (e.g. ``bill``, ``resolution``,
    etc.)

    You can specify sorting using the following ``sort`` keyword argument
    values:

    - ``first``
    - ``last``
    - ``signed``
    - ``passed_lower``
    - ``passed_upper``
    - ``updated_at``
    - ``created_at``

    Returns:
        A list of matching :ref:`Bill` dictionaries

    .. NOTE::
        This method returns just a subset (``state``, ``chamber``, ``session``,
        ``subjects``, ``type``, ``id``, ``bill_id``, ``title``, ``created_at``,
        ``updated_at``) of the bill fields by default.

        Use the ``fields`` parameter to specify a custom list of fields to
        return.
    """
    uri = "bills/"
    if "state" in kwargs.keys():
        kwargs["jurisdiction"] = _jurisdiction_id(kwargs["state"])

    if len(kwargs) > 0:
        kwargs["per_page"] = 20
        kwargs["page"] = 1
    results = []
    new_results = _get(uri, params=kwargs)["results"]
    while len(new_results) > 0:
        results += new_results
        kwargs["page"] += 1
        sleep(1)
        # When the search runs out of pages, the API returns not found
        try:
            new_results = _get(uri, params=kwargs)["results"]
        except NotFound:
            break

    return results


def get_bill(uid=None, state=None, session=None, bill_id=None, **kwargs):
    """
    Returns details of a specific bill Can be identified my the Open States
    unique bill id (uid), or by specifying the state, session, and
    legislative bill ID

    Args:
        uid: The Open States unique bill ID
        state: The postal code of the state
        session: The legislative session (see state metadata)
        bill_id: Yhe legislative bill ID (e.g. ``HR 42``)
        **kwargs: Optional keyword argument options, such as ``fields``,
        which specifies the fields to return

    Returns:
        The :ref:`Bill` details as a dictionary
    """
    if uid:
        if state or session or bill_id:
            raise ValueError(
                "Must specify an Open States bill (uid), or the "
                "state, session, and bill ID"
            )
        uid = _fix_id_string("ocd-bill/", uid)
        return _get(f"bills/{uid}", params=kwargs)
    else:
        if not state or not session or not bill_id:
            raise ValueError(
                "Must specify an Open States bill (uid), "
                "or the state, session, and bill ID"
            )
        return _get(f"bills/{state.lower()}/{session}/{bill_id}", params=kwargs)


def search_legislators(
    jurisdiction=None,
    name=None,
    id_=None,
    org_classification=None,
    district=None,
    include=None,
):
    """
    Search for legislators.

    Returns:
        A list of matching :ref:`Legislator` dictionaries

    """
    params = _make_params(
        jurisdiction=jurisdiction,
        name=name,
        id=id_,
        org_classification=org_classification,
        district=district,
        include=include,
    )
    return _get("people", params)["results"]


def get_legislator(leg_id):
    """
    Gets a legislator's details

    Args:
        leg_id: The Legislator's Open States ID
        fields: An optional custom list of fields to return

    Returns:
        The requested :ref:`Legislator` details as a dictionary
    """
    leg_id = _fix_id_string("ocd-person/", leg_id)
    return _get("people/", params={"id": [leg_id]})["results"][0]


def locate_legislators(lat, lng, fields=None):
    """
    Returns a list of legislators for the given latitude/longitude coordinates

    Args:
        lat: Latitude
        long: Longitude
        fields: An optional custom list of fields to return

    Returns:
        A list of matching :ref:`Legislator` dictionaries

    """
    return _get(
        "people.geo/", params=dict(lat=float(lat), lng=float(lng), fields=fields)
    )["results"]


def search_districts(state, chamber):
    """
    Search for districts

    Args:
        state: The state to search in
        chamber: the upper or lower legislative chamber
        fields: Optionally specify a custom list of fields to return

    Returns:
       A list of matching :ref:`District` dictionaries
    """
    if chamber:
        chamber = chamber.lower()
        if chamber not in ["upper", "lower"]:
            raise ValueError('Chamber must be "upper" or "lower"')
        organizations = get_organizations(state=state)
        for org in organizations:
            if org["classification"] == chamber:
                return org["districts"]


def _fix_id_string(prefix, id):
    if id.startswith(prefix):
        return id
    else:
        return prefix + id


def _jurisdiction_id(state):
    if state.startswith("ocd-jurisdiction/"):
        return state
    else:
        return f"ocd-jurisdiction/country:us/state:{state.lower()}/government"
