# pyopenstates

A Python client for the [Open States API v3](https://v3.openstates.org/docs).

Source: [https://github.com/openstates/pyopenstates/](https://github.com/openstates/pyopenstates)

Documentation: [https://openstates.github.io/pyopenstates/](https://openstates.github.io/pyopenstates/)

Issues: [https://github.com/openstates/pyopenstates/issues](https://github.com/openstates/pyopenstates/issues)

**Note: This library was recently updated to support Open States API v3, documentation & coverage is a bit behind, but we wanted to get a release out.  Feel free to contribute issues and/or fixes.**

[![PyPI badge](https://badge.fury.io/py/pyopenstates.svg)](https://badge.fury.io/py/pyopenstates)
[![Test Python](https://github.com/openstates/pyopenstates/actions/workflows/main.yml/badge.svg)](https://github.com/openstates/pyopenstates/actions/workflows/main.yml)

## Features

- Compatible with Python 3.7+
- Automatic conversion of string dates and timestamps to ``datetime`` objects.
- Tested releases.
- Set API Key via environment variable or in code.

## API Keys

To use the Open States API you must [obtain an API Key](https://openstates.org/accounts/register/).

Once you have your key you can use it with this library by setting the ``OPENSTATES_API_KEY`` environment variable or calling ``pyopenstates.set_api_key``.

## About Open States

Open States strives to improve civic engagement at the state level by providing data and tools regarding state legislatures. We aim to serve members of the public, activist groups, journalists, and researchers with better data on what is happening in their state capital, and to provide tools to reduce barriers to participation and increase engagement.

Open States aggregates legislative information from all 50 states, Washington, D.C., and Puerto Rico. This information is then standardized, cleaned, and published to the public via OpenStates.org, a powerful API, and bulk downloads. OpenStates.org enables individuals to find out who represents them, look up information on an important bill that’s been in the news, discover how their representatives are voting, or just stay current with what is happening in their state. Additionally, our API and bulk downloads see millions of hits every month from advocacy organizations, journalists, researchers, and many others.

Legislative data is collected from official sources, linked at the bottom of relevant pages. In general bill & vote data is collected multiple times a day via our scrapers while legislator data is curated by our team & volunteers like you.

