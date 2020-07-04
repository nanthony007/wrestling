#!/usr/bin/env python
# coding: utf-8


"""
NAME
    Process

DESCRIPTION
    This module contains the primary process functions
    which use the requesting and formatting modules to capture data from the MatBoss API.

FUNCTIONS
    generate_match_data(match, event_list, user_level)
        Returns match values and match timeseries.

    process_api_data(s, year)
        Returns match and timeseries dataframes and roster series.

"""

from typing import Tuple, List, Dict
from collections import Counter

import pandas as pd  # type: ignore
import requests
import json

from . import api_request, parse

base_url = "http://staging.matbossapp.com/api/v1/"


def parse_match_data(
    match: Dict, event_list: List[Dict], user_info: dict
) -> Tuple[Dict, List[Dict]]:
    """Factory function calls other functions.

    Args:
        match: Match object instance.
        event_list: List of events for the team from request_team_events().
        user_level: AgeLevel from api login from request_login().

    Returns:
        Dictionary of all match values and timeseries list of dicts.
    """
    demographics = parse.parse_demographics(match, event_list, user_info)

    # Filters out practice/fake wrestlers
    fake_wrestlers = ["Wrestler, Scout", "Doe, John", "Doe,", "Wrestler, Our"]
    if demographics.get("focus_name") in fake_wrestlers:
        return dict(), list()
    if demographics.get("opp_name") in fake_wrestlers:
        return dict(), list()

    results = parse.parse_results(match, user_info['ageLevel'])
    action_dicts, action_counts = parse.parse_action_values(
        match, demographics, user_info['ageLevel']
    )  # gets action counts and timeseries from match

    if action_counts == Counter():
        return dict(), list()

    # Merges dicts
    match_dict = {**demographics, **results, **action_counts}
    timeseries_dicts = parse.add_timeseries_points(action_dicts, demographics, user_info['ageLevel'])
    return match_dict, timeseries_dicts


def process_api_data(
    session: requests.sessions.Session, season: str, user_name: str
) -> Tuple[List[dict], List[dict], List[str]]:
    """Parses preprocessing from API.
        Posts login to API, requests team matches and event then parses all preprocessing.
        Returns two lists.  One list of dicts for all the matches, one list of dicts for all
        the timeseries, and a list of the roster.

    Args:
        session: Requests session object.
        season: Season for analysis.
        user_name: User's account name.

    Returns:
        Tuple of three lists.
    """
    # THIS IS FOR PRODUCTION USE LATER
    # LOAD LOCAL DATA DURING DEVELOPMENT FOR SPEED
    user_info = api_request.request_login(
        session=session, user_name=user_name
    )
    all_team_matches = api_request.request_team_matches(
        session=session, team_id=user_info['teamID'], season=season
    )  # matches for parsing
    team_events = api_request.request_team_events(
        session=session, team_id=user_info['teamID'], season=season
    )
    roster = api_request.request_team_roster(session=session, team_id=user_info['teamID'])

    # Creates two lists of dicts
    all_matches = []
    all_timeseries = []
    for match in all_team_matches:
        match_facts = parse_match_data(match, team_events, user_info)
        if match_facts is not None:
            all_matches.append(match_facts[0])  # match_dict
            all_timeseries.extend(match_facts[1])  # timeseries_dicts

    return all_matches, all_timeseries, roster


def load_base_data(user_name):
    ses = requests.Session()
    year = "2019-2020"
    matches, timeseries, roster = process_api_data(ses, year, user_name)
    # Creates dataframes
    matchdf = pd.DataFrame(
        matches
    ) # auto converts (avoids object type)
    tsdf = pd.DataFrame(
        timeseries
    ).convert_dtypes()  # auto converts (avoids object type)
    #
    # drops matches with fake wrestlers
    # these matches returned empty data in the parsing and now need to be filtered out
    matchdf = matchdf[matchdf.match_id.notna()].fillna(0).reset_index(drop=True)
    matchdf = matchdf.convert_dtypes()

    # tempoarary for ASU
    matchdf = matchdf[matchdf.focus_name != 0]
    
    return matchdf, tsdf, roster

