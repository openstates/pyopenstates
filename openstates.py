# -*- coding: utf-8 -*-

"""A simple client for the Open States API"""

from __future__ import unicode_literals, print_function, absolute_import

from sys import version_info

from datetime import datetime

from requests import Session

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

__version__ = "1.0.0"

API_ROOT = "https://openstates.org/api/v1/"
DEFUALT_USER_AGENT = "openstates-python/{}".format(__version__)

session = Session()
session.headers.update({"User-Agent": DEFUALT_USER_AGENT})


#  Python 2 comparability hack
if version_info[0] >= 3:
    unicode = str


class APIError(RuntimeError):
    """
    Raised when the Open States API returns an error
    """
    pass


def _get(uri, params=None):
    """
    An internal method for making API calls and error handling easy and consistent
    Args:
        uri: API URI
        params: GET parameters

    Returns:
        JSON as a Python dictionary
    """

    def _convert_timestamps(result):
        """Converts a string timestamps from an api result API to a datetime"""
        if type(result) == dict:
            for key in result.keys():
                if type(result[key]) == unicode:
                    try:
                        result[key] = datetime.strptime(result[key], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            result[key] = datetime.strptime(result[key], "%Y-%m-%d")
                        except ValueError:
                            pass
                elif type(result[key]) == dict:
                    result[key] = _convert_timestamps(result[key])
                elif type(result) == list:
                    result = list(map(lambda r: _convert_timestamps(r)), result)
        elif type(result) == list:
            result = list(map(lambda r: _convert_timestamps(r), result))

        return result

    def _convert(result):
        """Convert results to standard Python data structures"""
        result = _convert_timestamps(result)

        return result

    url = "{}/{}/".format(API_ROOT.strip("/"), uri.strip("/"))
    if "fields" in params.keys() and type(params["fields"]) == list:
        params["fields"] = ",".join(params["fields"]).lower()
    response = session.get(url, params=params)
    if response.status_code != 200:
        if response.status_code == 404:
            raise APIError("Not found: {}".format(response.url))
        else:
            raise APIError(response.text)
    return _convert(response.json())


def set_user_agent(user_agent):
    """Appends a custom string to the default User-Agent string"""
    session.headers.update({"User-Agent": "{} {}".format(DEFUALT_USER_AGENT, user_agent)})


def metadata(state=None, fields=None):
    """
        Returns a list of all states with data available, and basic metadata about their status.
        Can also get detailed metadata for a particular state.

    Args:
        state: The state to get detailed metadata on, or leave as None to get
        high-level metadata on all states.

        fields: An optional list of fields to return; returns all fields by default

        The following fields are available on metadata objects:

            abbreviation The two-letter abbreviation of the state.
            capitol_timezone Timezone of state capitol (e.g. ‘America/New_York’)
            chambers Dictionary mapping chamber type (upper/lower) to an object with the following fields:
                name Short name of the chamber (e.g. ‘House’, ‘Senate’)
                title Title of legislators in this chamber (e.g. ‘Senator’)
            feature_flags A list of which optional features are available, options include:
                ‘subjects’ - bills have categorized subjects
                ‘influenceexplorer’ - legislators have influence explorer ids
                ‘events’ - event data is present
            latest_csv_date Date that the CSV file at latest_csv_url was generated.
            latest_csv_url URL from which a CSV dump of all data for this state can be obtained.
            latest_json_date Date that the JSON file at latest_json_url was generated.
            latest_json_url URL from which a JSON dump of all data for this state can be obtained.
            latest_update Last time a successful scrape was run.
            legislature_name Full name of legislature (e.g. ‘North Carolina General Assembly’)
            legislature_url URL to legislature’s official website.
            name Name of state.
            session_details Dictionary of session names to detail dictionaries with the following keys:
                type ‘primary’ or ‘special’
                display_name e.g. ‘2009-2010 Session’
                start_date date session began
                end_date date session began
            terms List of terms in order that they occurred. Each item in the list is comprised of the following keys:
                start_year Year session started.
                end_year Year session ended.
                name Display name for term (e.g. ‘2009-2011’).
                sessions List of sessions (e.g. ‘2009’). Each session will be present in session_details.


    Returns:
        The requested metadata as a dictionary

    """
    uri = "/metadata/"
    if state:
        uri += "{}/".format(state.lower())
    return _get(uri, params=dict(fields=fields))


def download_csv(state, file_object):
    """
    Downloads a zip containing bulk data on a given state in CSV format to a given file object

    Args:
        state: The postal code of the state
        file_object: A file object

    Examples:
        # Saving Ohio's data to a file on disk
        with open("ohio-csv.zip", "wb") as ohio_zip_file:
            openstates.download_csv("OH", ohio_zip_file)

        # Or download it to memory
        from io import BytesIO
        mem_zip = BytesIO()
        openstates.download_csv("OH", mem_zip)
    """
    field = "latest_csv_url"
    url = metadata(state, fields=field)[field]
    file_object.write(session.get(url).content)


def download_json(state, file_object):
    """
        Downloads a zip containing bulk data on a given state in JSON format to a given file object

        Args:
            state: The postal code of the state
            file_object: A file object

        Examples:
            # Saving Ohio's data to a file on disk
            with open("ohio-json.zip", "wb") as ohio_zip_file:
                openstates.download_json("OH", ohio_zip_file)

            # Or download it to memory
            from io import BytesIO
            mem_zip = BytesIO()
            openstates.download_json("OH", mem_zip)
        """
    field = "latest_json_url"
    url = metadata(state, fields=field)[field]
    file_object.write(session.get(url).content)


def search_bills(**kwargs):
    """
    Find fills matching a given set of filters

    Args:
        **kwargs: The following parameters filter the returned set of bills, at least one must be provided.

    state Only return bills from a given state (e.g. ‘nc’)
    chamber Only return bills matching the provided chamber (‘upper’ or ‘lower’)
    bill_id Only return bills with a given bill_id.
    bill_id__in Accepts a pipe (|) delimited list of bill ids.
    q Only return bills matching the provided full text query.
    search_window By default all bills are searched, but if a time window is desired the following options can be passed
    to search_window:
        search_window=all Default, include all sessions.
        search_window=term Only bills from sessions within the current term.
        search_window=session Only bills from the current session.
        search_window=session:2009 Only bills from the session named 2009.
        search_window=term:2009-2011 Only bills from the sessions in the 2009-2011 session.
    updated_since Only bills updated since a provided date (provided in YYYY-MM-DD format)
    sponsor_id Only bills sponsored by a given legislator id (e.g. ‘ILL000555’)
    subject Only bills categorized by Open States as belonging to this subject.
    type Only bills of a given type (e.g. ‘bill’, ‘resolution’, etc.)


    Returns:
        A list of matching bills

    Notes:
        This method returns just a subset (state, chamber, session, subjects, type, id, bill_id, title, created_at,
        updated_at) of the bill fields by default. You can specify the fields to return in the fields keyword argument/

        The following fields are available on bill objects:

            state State abbreviation.
            session Session key (see State Metadata for details).
            bill_id The official id of the bill (e.g. ‘SB 27’, ‘A 2111’)
            title The official title of the bill.
            alternate_titles List of alternate titles that the bill has had. (Often empty.)
            action_dates Dictionary of notable action dates (useful for determining status). Contains the following
            fields:
                first First action (only null if there are no actions).
                last Last action (only null if there are no actions).
                passed_lower Date that the bill seems to have passed the lower chamber (might be null).
                passed_upper Date that the bill seems to have passed the upper chamber (might be null).
                signed Date that the bill appears to have signed into law (might be null).
            actions List of objects representing every recorded action for the bill. Action objects have the following
            fields:
                date Date of action.
                action Name of action as state provides it.
                actor The chamber, person, committee, etc. responsible for this action.
                type Open States-provided action categories, see action categorization.
            chamber The chamber of origination (‘upper’ or ‘lower’)
            created_at The date that this object first appeared in our system. (Note: not the date of introduction, see
            action_dates for that information.)
            updated_at The date that this object was last updated in our system. (Note: not the last action date, see
            action_dates for that information.)
            documents List of associated documents, see versions for field details.
            id Open States-assigned permanent ID for this bill.
            scraped_subjects List of subject areas that the state categorized this bill under.
            subjects List of Open States standardized bill subjects, see subject categorization.
            sources List of source URLs used to compile information on this object.
            sponsors List of bill sponsors.
                name Name of sponsor as it appears on state website.
                leg_id Open States assigned legislator ID (will be null if no match was found).
                type Type of sponsor (‘primary’ or ‘cosponsor’)
            type List of bill types.
            versions Versions of the bill text. Both documents and versions have the following fields:
                url Official URL for this document.
                name An official name for this document.
                mimetype The mimetype for the document (e.g. ‘text/html’)
                doc_id An Open States-assigned id uniquely identifying this document.
            votes List of vote objects. A vote object consists of the following keys:
                motion Name of motion being voted upon (e.g. ‘Passage’)
                chamber Chamber vote took place in (‘upper’, ‘lower’, ‘joint’)
                date Date of vote.
                id Open States-assigned unique identifier for vote.
                state State abbreviation.
                session Session key (see State Metadata for details).
                sources List of source URLs used to compile information on this object. (Can be empty if vote shares
                sourceswith bill.)
                yes_count Total number of yes votes.
                no_count Total number of no votes.
                other_count Total number of ‘other’ votes (abstain, not present, etc.).
                yes_votes, no_votes, other_votes List of roll calls of each type. Each is an object consisting of two
                keys:
                    name Name of voter as it appears on state website.
                    leg_id Open States assigned legislator ID (will be null if no match was found).

        You can specify sorting using the hollowing sort keyword argument values:

        first
        last
        signed
        passed_lower
        passed_upper
        updated_at
        created_at
    """
    uri = "bills/"
    if "per_page" in kwargs.keys():
        results = []
        kwargs["page"] = 1
        new_results = _get(uri, params=kwargs)
        while len(new_results) > 0:
            results += new_results
            kwargs["page"] += 1
            new_results = _get(uri, params=kwargs)
    else:
        results = _get(uri, params=kwargs)
    return results


def get_bill(uid=None, state=None, term=None, bill_id=None, **kwargs):
    """
    Returns details of a specific bill Can be identified my the Open States unique bill id (uid), or by specifying
    the state, term, and legislative bill ID

    Args:
        uid: The Open States unique bill ID
        state: The postal code of the state
        term: The legislative term (see state metadata)
        bill_id: Yhe legislative bill ID (e.g. HR 42)
        **kwargs: Additional, optional keyword argument options, such as:
        fields, which specifies the fields to return

    Returns:
        The details of the bill as a dictionary
    """
    if uid:
        if state or term or bill_id:
            raise ValueError("Must specify an Open States bill (uid), or the state, term, and bill ID")
        return _get("/bills/{}".format(uid), params=kwargs)
    else:
        if not state or not term or not bill_id:
            raise ValueError("Must specify an Open States bill (uid), or the state, term, and bill ID")
        return _get("/bills/{}/{}/{}/".format(state.lower(), term, bill_id), params=kwargs)


def search_legislators(**kwargs):
    """
    Search for legislators
    Args:
        **kwargs: Filters to search by:
            state Filter by state.
            first_name Filter by first name.
            last_name Filter by last name.
            chamber Only legislators with a role in the specified chamber.
            active ‘true’ (default) to only include current legislators, ‘false’ will include all legislators
            term Only legislators that have a role in a certain term.
            district Only legislators that have represented the specified district.
            party Only legislators that have been associated with a specified party.

            Additionally, the list of fields to return can be customized with the fields keyword argument
                leg_id Legislator’s permanent Open States ID. (e.g. ‘ILL000555’, ‘NCL000123’)
                state Legislator’s state.
                active Boolean value indicating whether or not the legislator is currently in office.
                chamber Chamber the legislator is currently serving in if active (‘upper’ or ‘lower’)
                district District the legislator is currently serving in if active (e.g. ‘7’, ‘6A’)
                party Party the legislator is currently representing if active.
                email Legislator’s primary email address.
                full_name Full display name for legislator.
                first_name First name of legislator.
                middle_name Middle name of legislator.
                last_name Last name of legislator.
                suffixes Name suffixes (e.g. ‘Jr.’, ‘III’) of legislator.
                photo_url URL of an official photo of this legislator.
                url URL of an official webpage for this legislator.
                created_at The date that this object first appeared in our system.
                updated_at The date that this object was last updated in our system.
                created_at Date at which this legislator was added to our system.
                updated_at Date at which this legislator was last updated.
                offices List of office objects representing contact details for the legislator. Comprised of the
                following fields:
                    type ‘capitol’ or ‘district’
                    name Name of the address (e.g. ‘Council Office’, ‘District Office’)
                    address Street address.
                    phone Phone number.
                    fax Fax number.
                    email Email address. Any of these fields may be ``null`` if not found.
                roles List of currently active role objects if legislator is in office.
                old_roles Dictionary mapping term keys to lists of roles that were valid for that term.

Roles

roles and old_roles are comprised of role objects.

Role objects can have the following fields:

    term Term key for this role. (See metadata notes on terms and sessions for details.)
    chamber
    state
    start_date (optional)
    end_date (optional)
    type ‘member’ or ‘committee member’

If the role type is ‘member’:

    party
    district

And if the type is ‘committee member’:

    committee name of parent committee
    subcommittee name of subcommittee (if null, membership is just for a committee)
    committee_id Open States id for committee that legislator is a member of
    position position on committee
    old_roles
    sources List of URLs used in gathering information for this legislator.

    Returns:
        A list of legislators

    """
    return _get("/legislators/", params=kwargs)


def get_legislator(leg_id, fields=None):
    """
    Gets a legislator's details
    Args:
        leg_id: The Legislator's Open States ID
        fields: An optional custom list of fields to return

    Returns:
        The requested legislator details as a dictionary
    """
    return _get("/legislators/{}/".format(leg_id), params=dict(fields=fields))


def locate_legislators(lat, long, fields=None):
    """
    Returns a list of legislators for the given latitude/longitude coordinates
    Args:
        lat: Latitude
        long: Longitude
        fields: An optional custom list of fields to return

    Returns:
        A list of legislators

    """
    return _get("/legislators/geo/", params=dict(lat=lat, long=long, fields=fields))


def search_committees(**kwargs):
    """
    Search for and return a list of matching committees
    Args:
        **kwargs: One or more filter keyword arguments:
            committee
            subcommittee
            chamber
            state

            Additionally, the list of fields to return can be customized with the fields keyword argument.
            The following fields are available on committee objects:

                id Open States assigned committee ID.
                state State abbreviation.
                chamber Chamber committee belongs to: ‘upper’, ‘lower’, ‘joint’.
                committee Name of committee.
                subcommittee Name of subcommittee. (if null, object describes the committee)
                parent_id Committee id pointing to the parent committee if this is a subcommittee.
                sources List of URLs used in gathering information for this legislator.
                created_at The date that this object first appeared in our system.
                updated_at The date that this object was last updated in our system.
                members List of member objects, each has the following keys:
                    name Name of legislator as provided by state source.
                    leg_id Open States-assigned legislator id. (null if no match found).
                    role Member’s role on the committee (e.g. ‘chair’, ‘vice-chair’, default role is ‘member’)

    Returns:
        A list of committees
    """
    return _get("/committees/", params=kwargs)


def get_committee(com_id, fields=None):
    """
    Gets committee details
    Args:
        com_id: Open States committee ID
        fields: An optional, custom set of fields to return

    Returns:
        Committee details as a dictionary
    """
    return _get("/committees/{}/".format(com_id), params=dict(fields=fields))


def search_events(**kwargs):
    """
    Searches events

    Events are not available in all states, to ensure that events are available check the feature_flags list in a
    states’ State Metadata.

    Args:
        **kwargs: Fields that can be filtered om:
            state
            type

        This method also allows specifying an alternate output format, by specifying format=rss or format=ics.

        By using the optional keyword argument fields, you can specify which field should be returned.

            The following fields are available on event objects:

            id Open States assigned event ID.
            state State abbreviation.
            type Categorized event type. (‘committee:meeting’ for now)
            description Description of event from state source.
            documents List of related documents.
            location Location if known, as given by state (is often just a room number).
            when Time event begins.
            end End time (null if unknown).
            timezone Timezone event occurs in (e.g. ‘America/Chicago’).
            participants List of participant objects, consisting of the following fields:
                chamber Chamber of participant.
                type Type of participants (‘legislator’, ‘committee’)
                participant String representation of participant (e.g. ‘Housing Committee’, ‘Jill Smith’)
                id Open States id for participant if a match was found (e.g. ‘TXC000150’, ‘MDL000101’)
                type What role this participant played (will be ‘host’, ‘chair’, ‘participant’).
            related_bills List of related bills for this event. Comprised of the following fields:
                type Type of relationship (e.g. ‘consideration’)
                description Description of how the bill is related given by the state.
                bill_id State’s bill id (e.g. ‘HB 273’)
                id Open States assigned bill id (e.g. ‘TXB00001234’)
            sources List of URLs used in gathering information for this legislator.
            created_at The date that this object first appeared in our system.
            updated_at The date that this object was last updated in our system.


    Returns:
        A list of events
    """
    return _get("/events/", params=kwargs)


def get_event(event_id, fields=None):
    """
    Get event details
    Args:
        event_id: The Openstates Event UUID
        fields: An optional list of fields to return

    Returns:
        The event as a dictionary
    """
    return _get("/events/{}/".format(event_id), params=dict(fields=fields))


def search_districts(state, chamber, fields=None):
    """
    Search for districts
    Args:
        state: The state to search in
        chamber: the upper or lower legislative chamber
        fields: Optionally specify a custom list of fields to return

        District objects contain the following fields:
            abbr State abbreviation.
            boundary_id boundary_id used in District Boundary Lookup
            chamber Whether this district belongs to the upper or lower chamber.
            id A unique ID for this district (separate from boundary_id).
            legislators List of legislators that serve in this district. (may be more than one if num_seats > 1)
            name Name of the district (e.g. ‘14’, ‘33A’, ‘Fifth Suffolk’)
            num_seats Number of legislators that are elected to this seat. Generally one, but will be 2 or more if the
            seat is a multi-member district.


    Returns:
        A list of districts
    """
    uri = "/districts/{}/".format(state.lower())
    if chamber:
        chamber = chamber.lower()
        uri += "{}/".format(chamber)
        if chamber not in ["upper", "lower"]:
            raise ValueError('Chamber must be "upper" or "lower"')
        return _get(uri, params=dict(fields=fields))


def get_district_boundary(boundary_id, fields=None):
    """
    Get district boundary details
    Args:
        boundary_id: The boundary ID
        fields: Optionally specify a custom list of fields to return

    Returns:
        District details as a dictionary
    """
    uri = "/districts/boundary/{}/".format(boundary_id)
    return _get(uri, params=dict(fields=fields))
