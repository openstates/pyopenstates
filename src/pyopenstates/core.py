import warnings
import dateutil.parser
from requests import Session
from time import sleep
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
    warnings.warn(f"Warning: No API Key found, set {API_KEY_ENV_VAR}")


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


def get_metadata(state=None, include=None, fields=None):
    """
        Returns a list of all states with data available, and basic metadata
        about their status. Can also get detailed metadata for a particular
        state.

    Args:
        state: The abbreviation of state to get detailed metadata on, or leave
        as None to get high-level metadata on all states.

        include: Additional includes.

        fields: An optional list of fields to return; returns all fields by
            default

    Returns:
       Dict: The requested :ref:`Metadata` as a dictionary
    """
    uri = "jurisdictions"
    params = dict()
    if include:
        params["include"] = _include_list(include)
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


def _alt_parameter(param, other_param, param_name, other_param_name):
    """ensure that only one name was specified"""
    if param and other_param:
        raise ValueError(
            f"cannot specify both {param_name} and variant {other_param_name}"
        )
    elif other_param:
        warnings.warn(f"{other_param_name} is deprecated, use {param_name}")
        return other_param
    return param


def search_bills(
    jurisdiction=None,
    identifier=None,
    session=None,
    chamber=None,
    classification=None,
    subject=None,
    updated_since=None,
    created_since=None,
    action_since=None,
    sponsor=None,
    sponsor_classification=None,
    q=None,
    # control params
    sort=None,
    include=None,
    page=1,
    per_page=10,
    all_pages=True,
    # alternate names for other parameters
    state=None,
):
    """
    Find bills matching a given set of filters

    For a list of each field, example values, etc. see
    https://v3.openstates.org/docs#/bills/bills_search_bills_get
    """
    uri = "bills/"
    args = {}

    jurisdiction = _alt_parameter(state, jurisdiction, "state", "jurisdiction")

    if jurisdiction:
        args["jurisdiction"] = jurisdiction
    if session:
        args["session"] = session
    if chamber:
        args["chamber"] = chamber
    if classification:
        args["classification"] = classification
    if subject:
        args["subject"] = subject
    if updated_since:
        args["updated_since"] = updated_since
    if created_since:
        args["created_since"] = created_since
    if action_since:
        args["action_since"] = action_since
    if sponsor:
        args["sponsor"] = sponsor
    if sponsor_classification:
        args["sponsor_classification"] = sponsor_classification
    if q:
        args["q"] = q
    if sort:
        args["sort"] = sort
    if include:
        args["include"] = include

    results = []

    if all_pages:
        args["per_page"] = 20
        args["page"] = 1
    else:
        args["per_page"] = per_page
        args["page"] = page

    resp = _get(uri, params=args)
    results += resp["results"]

    if all_pages:
        while resp["pagination"]["page"] < resp["pagination"]["max_page"]:
            args["page"] += 1
            sleep(1)
            resp = _get(uri, params=args)
            results += resp["results"]

    return results


def get_bill(uid=None, state=None, session=None, bill_id=None, include=None):
    """
    Returns details of a specific bill Can be identified by the Open States
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
    args = {"include": include} if include else {}

    if uid:
        if state or session or bill_id:
            raise ValueError(
                "Must specify an Open States bill (uid), or the "
                "state, session, and bill ID"
            )
        uid = _fix_id_string("ocd-bill/", uid)
        return _get(f"bills/{uid}", params=args)
    else:
        if not state or not session or not bill_id:
            raise ValueError(
                "Must specify an Open States bill (uid), "
                "or the state, session, and bill ID"
            )
        return _get(f"bills/{state.lower()}/{session}/{bill_id}", params=args)


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


def _include_list(include):
    if include is None:
        return None
    elif isinstance(include, str):
        return [include]
    elif isinstance(include, (list, tuple)):
        return include
    else:
        raise ValueError("include must be a str or list")
