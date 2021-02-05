#!/usr/bn/env python
# -*- coding: utf-8 -*-

"""Unit tests for openstatesclient"""

import unittest

from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
from time import sleep
import pyopenstates

"""Copyright 2016 Sean Whalen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class Test(unittest.TestCase):
    """A test suite for pyopenstates"""

    def setUp(self):
        pyopenstates.set_user_agent("test-suite")

    def tearDown(self):
        # Wait between tests to avoid hitting the API limit
        sleep(0.5)

    def testOpenStatesMetadata(self):
        """Calling the metadata method without specifying a state returns a
        list of 52 dictionaries: One for each state, plus DC and Puerto Rico"""
        metadata = pyopenstates.get_metadata()
        self.assertEqual(len(metadata), 52)
        for obj in metadata:
            self.assertEqual(type(obj), dict)

    def testStateMetadata(self):
        """All default state metadata fields are returned"""
        state_code = "NC"
        fields = ['id', 'name', 'classification', 'division_id', 'url']
        metadata = pyopenstates.get_metadata(state_code)
        keys = metadata.keys()
        for field in fields:
            self.assertIn(field, keys)
        self.assertEqual(metadata["name"], "North Carolina")

    def testSubsetStateMetadataFields(self):
        """Requesting specific fields in state metadata returns only those
        fields"""
        requested_fields = ["id", "name", "url"]
        metadata = pyopenstates.get_metadata("OH", fields=requested_fields)
        returned_fields = metadata.keys()

        for field in requested_fields:
            self.assertIn(field, returned_fields)
        for field in returned_fields:
            self.assertIn(field, requested_fields)
    
    def testGetOrganizations(self):
        """Get all organizations for a given state"""
        state_code = "NC"
        orgs = pyopenstates.get_organizations(state_code)
        names = [org['name'] for org in orgs]
        self.assertIn('North Carolina General Assembly', names)

    # def testDownloadCSV(self):
    #     """Downloading bulk data on a state in CSV format"""
    #     zip_file = BytesIO()
    #     pyopenstates.download_bulk_data("AK", zip_file, data_format="csv")
    #     zip = ZipFile(zip_file)
    #     for filename in zip.namelist():
    #         self.assertTrue(filename.endswith(".csv"))

    # def testDownloadJSON(self):
    #     """Downloading bulk data on a state in JSON format"""
    #     zip_file = BytesIO()
    #     pyopenstates.download_bulk_data("AK", zip_file)
    #     zip = ZipFile(zip_file)
    #     self.assertIn("metadata.json", zip.namelist())


    def testInvalidState(self):
        """Specifying an invalid state raises a NotFound exception"""
        self.assertRaises(pyopenstates.NotFound, pyopenstates.get_metadata,
                          state="ZZ")

    def testBillSearchFullText(self):
        """A basic full-text search returns results that contain the query
        string"""
        query = "taxi"
        results = pyopenstates.search_bills(state="ny", q=query)
        self.assertGreater(len(results), 1)
        match = False
        for result in results:
            if query.lower() in result["title"].lower():
                match = True
                break
        self.assertTrue(match)

    def testBillDetails(self):
        """Bill details"""
        state = "nc"
        session = "2019"
        bill_id = "HB 1105"

        bill = pyopenstates.get_bill(state=state, session=session, bill_id=bill_id)

        self.assertEqual(bill["identifier"], bill_id)

    def testBillDetailsByUID(self):
        """Bill details by UID"""
        _id = "6dc08e5d-3d62-42c0-831d-11487110c800"
        title = "Coronavirus Relief Act 3.0."

        bill = pyopenstates.get_bill(_id)

        self.assertEqual(bill["title"], title)

    def testBillDetailInputs(self):
        """Bill detail inputs"""
        state = "nc"
        session = "2019"
        bill_id = "HB 1105"
        _id = "6dc08e5d-3d62-42c0-831d-11487110c800"

        self.assertRaises(ValueError, pyopenstates.get_bill, _id, state, session,
                          bill_id)
        self.assertRaises(ValueError, pyopenstates.get_bill, _id, state)

# with previous API versions, you could request 500 bills per page, but with v3,
# can only request 20 per page. this test always hits the rate limit so not sure
# this test makes sense anymore
    # def testBillSearchSort(self):
    #     """Sorting bill search results"""
    #     sorted_bills = pyopenstates.search_bills(state="dc",
    #                                              search_window="term",
    #                                              sort="created_at")
    #     self.assertGreater(sorted_bills[0]["created_at"],
    #                        sorted_bills[-1]["created_at"])

    def testBillSearchMissingFilter(self):
        """Searching for bills with no filters raises APIError"""
        self.assertRaises(pyopenstates.APIError, pyopenstates.search_bills)

    def testLegislatorSearch(self):
        """Legislator search"""
        state = "dc"
        chamber = "upper"
        results = pyopenstates.search_legislators(state=state, chamber=chamber)
        self.assertGreater(len(results), 2)
        for legislator in results:
            self.assertEqual(legislator["state"], state.lower())
            self.assertEqual(legislator["chamber"], chamber.lower())

    def testLegislatorDetails(self):
        """Legislator details"""
        _id = "adb58f21-f2fd-4830-85b6-f490b0867d14"
        name = "Bryce E. Reeves"
        self.assertEqual(pyopenstates.get_legislator(_id)["name"],
                         name)

    def testLegislatorGeolocation(self):
        """Legislator geolocation"""
        lat = 35.79
        lng = -78.78
        state = "North Carolina"
        results = pyopenstates.locate_legislators(lat, lng)
        print(results)
        self.assertGreater(len(results), 0)
        for legislator in results:
            self.assertEqual(legislator["jurisdiction"]['name'], state)

    def testDistrictSearch(self):
        """District search"""
        state = "nc"
        name = "North Carolina General Assembly"
        results = pyopenstates.search_districts(state=state, name=name)
        self.assertGreater(len(results), 2)
        for district in results:
            self.assertEqual(district["state"], state)
            self.assertEqual(district["name"], name)

    def testDistrictBoundary(self):
        """District boundary details"""
        boundary_id = "ocd-division/country:us/state:nc/sldl:10"
        _id = "nc-lower-10"
        boundry = pyopenstates.get_district(boundary_id)
        self.assertEqual(boundry["boundary_id"], boundary_id)
        self.assertEqual(boundry["id"], _id)

    def testTimestampConversionInList(self):
        """Timestamp conversion in a list"""
        bill = pyopenstates.search_bills(state="oh")[0]
        self.assertTrue(type(bill["created_at"]) == datetime)

    def testTimestampConversionInDict(self):
        """Timestamp conversion in a dictionary"""
        oh = pyopenstates.get_metadata(state="oh")
        self.assertTrue(type(oh["latest_update"]) == datetime)


if __name__ == "__main__":
    unittest.main(verbosity=2)
