===============
Data structures
===============

Objects from the Open States API are returned at dictionaries

.. _Metadata:

********
Metadata
********

- ``abbreviation`` - The two-letter abbreviation of the state.
- ``capitol_timezone`` - Timezone of state capitol (e.g. ``America/New_York``)
- ``chambers`` - Dictionary mapping chamber type (upper/lower) to an object with the following fields:
   - ``name`` - Short name of the chamber (e.g. ``House``, ``Senate``)
   - ``title`` - Title of legislators in this chamber (e.g. ``Senator``)
- ``feature_flags`` - A list of which optional features are available, options include:
    - ``subjects`` - bills have categorized subjects
    - ``influenceexplorer`` - legislators have influence explorer ids
    - ``events`` - event data is present
- ``latest_csv_date`` - Date that the CSV file at ``latest_csv_url`` was generated.
- ``latest_csv_url`` - URL from which a CSV dump of all data for this state can be obtained.
- ``latest_json_date`` - Date that the JSON file at ``latest_json_url`` was generated.
- ``latest_json_url`` - URL from which a JSON dump of all data for this state can be obtained.
- ``latest_update`` - Last time a successful scrape was run.
- ``legislature_name`` - Full name of legislature (e.g. ``North Carolina General Assembly``)
- ``legislature_url`` - URL to legislature’s official website.
- ``name`` - Name of state.
- ``session_details`` - Dictionary of session names to detail dictionaries with the following keys:
    - ``type`` - ``primary`` or ``special``
    - ``display_name`` - e.g. ``2009-2010 Session``
    - ``start_date`` - date session began
    - ``end_date`` - date session began
- ``terms`` - List of terms in order that they occurred. Each item in the list is comprised of the following keys:
    - ``start_year`` - Year session started.
    - ``end_year`` - Year session ended.
    - ``name`` - Display name for term (e.g. ``2009-2011``).
    - ``sessions`` - List of sessions (e.g. ``2009``). Each session will be present in session_details.

.. _Bill:

****
Bill
****

- ``state`` - State abbreviation.
- ``session`` - Session key (see State Metadata for details).
- ``bill_id`` - The official id of the bill (e.g. ``SB 27``, ``A 2111``)
- ``title`` - The official title of the bill.
- ``alternate_titles`` - List of alternate titles that the bill has had. (Often empty.)
- ``action_dates`` - Dictionary of notable action dates (useful for determining status). Contains the following fields:
    - ``first`` First action (only ``None`` if there are no actions).
    - ``last`` - Last action (only ``None`` if there are no actions).
    - ``passed_lower`` - Date that the bill seems to have passed the lower chamber (might be ``None``).
    - ``passed_upper`` - Date that the bill seems to have passed the upper chamber (might be ``None``).
    - ``signed`` - Date that the bill appears to have signed into law (might be ``None``).
- ``actions`` -  List of objects representing every recorded action for the bill. Action objects have the following fields:
    - ``date`` - Date of action.
    - ``action`` - Name of action as state provides it.
    - ``actor`` - The chamber, person, committee, etc. responsible for this action.
    - ``type`` - Open States-provided action categories, see action categorization.
- ``chamber`` - The chamber of origination (‘upper’ or ‘lower’)
- ``created_at`` - The date that this object first appeared in our system. (Note: not the date of introduction, see ``action_dates`` - for that information.)
- ``updated_at`` - The date that this object was last updated in our system. (Note: not the last action date, see ``action_dates`` for that information.)
- ``documents List`` - of associated documents, see versions for field details.
- ``id`` - Open States-assigned permanent ID for this bill.
- ``scraped_subjects`` - List of subject areas that the state categorized this bill under.
- ``subjects``` - List of Open States standardized bill subjects, see subject categorization.
- ``sources`` - List of source URLs used to compile information on this object.
- ``sponsors`` - List of bill sponsors.
    - ``name`` - Name of sponsor as it appears on state website.
    - ``leg_id`` - Open States assigned legislator ID (will be ``None`` if no match was found).
    - ``type`` - Type of sponsor (``primary`` or ``cosponsor``)
- ``type`` - List of bill types.
- ``versions`` Versions of the bill text. Both documents and versions have the following fields:
    - ``url`` - Official URL for this document.
    - ``name`` - An official name for this document.
    - ``mimetype`` - The mimetype for the document (e.g. ``text/html``)
    - ``doc_id`` - An Open States-assigned id uniquely identifying this document.
- ``votes`` - List of vote objects. A vote object consists of the following keys:
    - ``motion`` - Name of motion being voted upon (e.g. ``Passage``)
    - ``chamber`` - Chamber vote took place in (``upper``, ``lower``, ``joint``)
    - ``date`` - Date of vote.
    - ``id`` - Open States-assigned unique identifier for vote.
    - ``state`` - State abbreviation.
    - ``session`` - Session key (see State Metadata for details).
    - ``sources`` -  List of source URLs used to compile information on this object. (Can be empty if vote shares sources with bill.)
    - ``yes_count`` - Total number of yes votes.
    - ``no_count`` - Total number of no votes.
    - ``other_count`` - Total number of othe’ votes (abstain, not present, etc.).
    - ``yes_votes``, ``no_votes``, ``other_votes`` - List of roll calls of each type. Each is an object consisting of two ßkeys:
        - ``name`` - Name of voter as it appears on state website.
        - ``leg_id`` - Open States assigned legislator ID (will be ``None`` if no match was found).

.. _Legislator:

**********
Legislator
**********

- ``leg_id`` - Legislator’s permanent Open States ID. (e.g. ``ILL000555``, ``NCL000123``)
- ``state`` - Legislator’s state.
- ``active`` - Boolean value indicating whether or not the legislator is currently in office.
- ``chamber`` - Chamber the legislator is currently serving in if active (``upper`` or ``lower``)
- ``district`` - District the legislator is currently serving in if active (e.g. ``7``, ``6A``)
- ``party`` - Party the legislator is currently representing if active.
- ``email`` Legislator’s primary email address.
- ``full_name`` - Full display name for legislator.
- ``first_name``  - First name of legislator.
- ``middle_name`` -  Middle name of legislator.
- ``last_name`` - Last name of legislator.
- ``suffixes`` - Name suffixes (e.g. ``Jr.``, ``III``) of legislator.
- ``photo_url`` URL of an official photo of this legislator.
- ``url`` - URL of an official webpage for this legislator.
- ``created_at`` - The date that this object first appeared in our system.
- ``updated_at`` - The date that this object was last updated in our system.
- ``created_at`` - Date at which this legislator was added to our system.
- ``updated_at`` - Date at which this legislator was last updated.
- ``offices`` List of office objects representing contact details for the legislator. Comprised of the following fields:
    - ``type`` - ``capitol`` or ``district``
    - ``name`` - Name of the address (e.g. ‘Council Office’, ‘District Office’)
    - ``address`` - Street address.
    - ``phone`` - Phone number.
    - ``fax`` - Fax number.
    - ``email`` Email address. Any of these fields may be ``None`` if not found.
- ``roles`` - List of currently active role objects if legislator is in office.
- ``old_roles`` - Dictionary mapping term keys to lists of roles that were valid for that term.

.. _Role:

Role
----

- ``term`` - Term key for this role. (See metadata notes on terms and sessions for details.)
- ``chamber``
- ``state``
- ``start_date`` (optional)
- ``end_date`` (optional)
- ``type`` - ``member`` or ``committee member``

If the role type is ``member``:

    - ``party``
    - ``district``

And if the type is ``committee membe``:

    - ``committee`` - Name of parent committee
    - ``ubcommittee`` - Name of subcommittee (if ``None``, membership is just for a committee)
    - ``committee_id`` - Open States id for committee that legislator is a member of
    - ``position`` - Position on committee
    - ``old_roles`` - List of old roles
    - ``sources`` List of URLs used in gathering information for this legislator.

.. _Committee:

*********
Committee
*********

- ``id`` - Open States assigned committee ID.
- ``state`` - State abbreviation.
- ``chamber`` - Chamber committee belongs to: ``upper``, ``lower``, or ``joint``.
- ``committee`` - Name of committee.
- ``subcommittee`` - Name of subcommittee. (if ``None``, object describes the committee)
- ``parent_id`` - Committee id pointing to the parent committee if this is a subcommittee.
- ``sources`` - List of URLs used in gathering information for this legislator.
- ``created_at`` - The date that this object first appeared in our system.
- ``updated_at`` - The date that this object was last updated in our system.
- ``members`` - List of member objects, each has the following keys:
    - ``name`` - Name of legislator as provided by state source.
    - ``leg_id`` - Open States-assigned legislator id. (``None`` if no match found).
    - ``role`` - Member’s role on the committee (e.g. ``chair``, ``vice-chair``; default role is ``member``)

.. _Event:

*****
Event
*****

- ``id`` - Open States assigned event ID.
- ``state`` - State abbreviation.
- ``type`` - Categorized event type. (``committee:meeting`` for now)
- ``description`` - Description of event from state source.
- ``documents`` - List of related documents.
- ``Location`` - Location if known, as given by state (it is often just a room number).
- ``when`` - Time event begins.
- ``end``  - End time (``None`` if unknown).
- ``timezone`` - Timezone event occurs in (e.g. ``America/Chicago``).
- ``participants`` - List of participant objects, consisting of the following fields:
    - ``chamber`` - Chamber of participant.
    - ``type`` - Type of participants (``legislator``, ``committee``)
    - ``participant`` - String representation of participant (e.g. ``Housing Committee``, ``Jill Smith``)
    - ``id`` - Open States ID for participant if a match was found (e.g. ``TXC000150``, ``MDL000101``)
    - ``type`` - What role this participant played (will be ``host``, ``chair``, ``participant``).
- ``related_bills`` - List of related bills for this event. Comprised of the following fields:
    - ``type`` - Type of relationship (e.g. ``consideration``)
    - ``description`` - Description of how the bill is related given by the state.
    - ``bill_id`` - State’s bill id (e.g. ``HB 273``)
    - ``id`` - Open States assigned bill id (e.g. ``TXB00001234``)
- ``sources`` List of URLs used in gathering information for this legislator.
- ``created_at`` - The date that this object first appeared in our system.
- ``updated_at`` - The date that this object was last updated in our system.

.. _District:

********
District
********

- ``abbr`` - State abbreviation.
- ``boundary_id`` -  ``boundary_id`` used in District Boundary Lookup
- ``chamber`` - Whether this district belongs to the ``upper`` or ``lower`` chamber.
- ``id`` - A unique ID for this district (separate from boundary_id).
- ``legislators`` - List of legislators that serve in this district. (may be more than one if num_seats > 1)
- ``name`` - Name of the district (e.g. ``14``, ``33A``, ``Fifth Suffolk``)
- ``num_seats`` - Number of legislators that are elected to this seat. Generally one, but will be 2 or more if the seat is a multi-member district.