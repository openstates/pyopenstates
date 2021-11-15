# -*- coding: utf-8 -*-

"""Unit tests for openstatesclient"""

import pytest
from datetime import datetime
from time import sleep
import pyopenstates


# def setUp(self):
#     pyopenstates.set_user_agent("test-suite")

# def tearDown(self):
#     # Wait between tests to avoid hitting the API limit
#     sleep(0.5)


def testOpenStatesMetadata():
    """Calling the metadata method without specifying a state returns a
    list of 52 dictionaries: One for each state, plus DC and Puerto Rico"""
    metadata = pyopenstates.get_metadata()
    assert len(metadata) == 52


def testStateMetadata():
    """All default state metadata fields are returned"""
    state_code = "NC"
    fields = ["id", "name", "classification", "division_id", "url"]
    metadata = pyopenstates.get_metadata(state_code)
    keys = metadata.keys()
    for field in fields:
        assert field in keys
    assert metadata["name"] == "North Carolina"


def testSubsetStateMetadataFields():
    """Requesting specific fields in state metadata returns only those
    fields"""
    requested_fields = ["id", "name", "url"]
    metadata = pyopenstates.get_metadata("OH", fields=requested_fields)
    returned_fields = metadata.keys()

    for field in requested_fields:
        assert field in returned_fields
    for field in returned_fields:
        assert field in requested_fields


def testGetOrganizations():
    """Get all organizations for a given state"""
    state_code = "NC"
    orgs = pyopenstates.get_organizations(state_code)
    names = [org["name"] for org in orgs]
    assert "North Carolina General Assembly" in names


def testInvalidState():
    """Specifying an invalid state raises a NotFound exception"""
    with pytest.raises(pyopenstates.NotFound):
        pyopenstates.get_metadata(state="ZZ")


def testBillSearchFullText():
    """A basic full-text search returns results that contain the query
    string"""
    query = "taxi"
    results = pyopenstates.search_bills(state="ny", q=query)
    assert len(results) > 1
    match = False
    for result in results:
        if query.lower() in result["title"].lower():
            match = True
            break
    assert match


def testBillDetails():
    """Bill details"""
    state = "nc"
    session = "2019"
    bill_id = "HB 1105"

    bill = pyopenstates.get_bill(state=state, session=session, bill_id=bill_id)

    assert bill["identifier"] == bill_id


def testBillDetailsByUID():
    """Bill details by UID"""
    _id = "6dc08e5d-3d62-42c0-831d-11487110c800"
    title = "Coronavirus Relief Act 3.0."

    bill = pyopenstates.get_bill(_id)

    assert bill["title"] == title


def testBillDetailInputs():
    """Bill detail inputs"""
    state = "nc"
    session = "2019"
    bill_id = "HB 1105"
    _id = "6dc08e5d-3d62-42c0-831d-11487110c800"

    with pytest.raises(ValueError):
        pyopenstates.get_bill(_id, state, session, bill_id)
    with pytest.raises(ValueError):
        pyopenstates.get_bill(_id, state)


def testBillSearchMissingFilter():
    """Searching for bills with no filters raises APIError"""
    with pytest.raises(pyopenstates.APIError):
        pyopenstates.search_bills()


def testLegislatorSearch():
    """Legislator search"""
    state = "dc"
    org_classification = "legislature"
    results = pyopenstates.search_legislators(jurisdiction=state, org_classification=org_classification)
    assert len(results) > 2
    for legislator in results:
        assert legislator["jurisdiction"]["name"] == "District of Columbia"
        assert legislator["current_role"]["org_classification"] == org_classification


def testLegislatorDetails():
    """Legislator details"""
    _id = "adb58f21-f2fd-4830-85b6-f490b0867d14"
    name = "Bryce E. Reeves"
    assert pyopenstates.get_legislator(_id)["name"] == name


def testLegislatorGeolocation():
    """Legislator geolocation"""
    lat = 35.79
    lng = -78.78
    results = pyopenstates.locate_legislators(lat, lng)
    assert len(results) == 3
    for legislator in results:
        assert legislator["jurisdiction"]["name"] in (
            "North Carolina",
            "United States",
        )


def testDistrictSearch():
    """District search"""
    state = "nc"
    chamber = "lower"
    results = pyopenstates.search_districts(state, chamber)
    assert len(results) > 2
    for district in results:
        assert district["role"] == "Representative"


def testTimestampConversionInList():
    """Timestamp conversion in a list"""
    bill = pyopenstates.search_bills(state="oh", q="HB 1")[0]
    assert isinstance(bill["created_at"], datetime)


def testTimestampConversionInDict():
    """Timestamp conversion in a dictionary"""
    oh = pyopenstates.get_metadata(state="oh")
    assert isinstance(oh["latest_people_update"], datetime)
