#!/usr/bin/env python
# coding: utf-8


import requests
import pandas as pd

from . import load_data as gen


#! todo: add data save functionality from ipynb (referencing saving api response data)


def create_csv_files(user_name: str):
    """Creates three csv files from API processing.

    Args:
        user_name: Team user name.

    Returns:
        True
    """
    matches, timeseries = gen.load_base_data(user_name)

    # Creates dataframes
    match_df = pd.DataFrame(
        matches
    ).convert_dtypes()  # auto converts (avoids object type)
    ts_df = pd.DataFrame(
        timeseries
    ).convert_dtypes()  # auto converts (avoids object type)

    match_df = match_df[match_df.match_id.notna()].fillna(0).reset_index(drop=True)

    match_df.to_csv("analytics/resources/spreadsheets/matches.csv", index=False)
    ts_df.to_csv("analytics/resources/spreadsheets/timeseries.csv", index=False)