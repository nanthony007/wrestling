#!/usr/bin/env python
# coding: utf-8


#  can this still be a factory function where we create the 5 main dfs?
#  are the dfs even needed or are we going to temporarily create them inside the
#  functions?
# PROS: less storage/memory in constant use
# CONS: more computations required (i.e. make ts_df 4 times to make graphs)
def create_dfs(user_name):
    matches, tsdf, roster = load_data.load_base_data(user_name)
    return matchdf, tsdf, roster


# add into Wrestler class :)
def generate_roster_df(roster_dicts, athlete_names, df):
    # takes roster dicts from api request
    roster = [
        wrestler for wrestler in roster_dicts if wrestler["name"] in athlete_names
    ]
    for wrestler in roster:
        dff = df[df.focus_name == wrestler["name"]]
        if len(dff) > 0:
            results = dff.result.value_counts()
            weights = dff.weight_class.unique()
            wrestler["weight"] = "/".join(weights)  # try f-strings?
            wrestler["matches"] = len(dff)
            wrestler["wins"] = results.get("Win", 0)
            wrestler["losses"] = results.get("Loss", 0)
        else:
            raise ValueError("Invalid df length", len(dff))
    return pd.DataFrame(roster)


def extend_roster_df(df, roster_dicts):
    rosterdf = generate_roster_df(roster_dicts, df.focus_name.unique(), df)
    athlete_df = df.groupby("focus_name").mean()

    # main section
    cols = ["focus_pts", "opp_pts", "td_diff", "mov"]
    temp = athlete_df[cols]
    temp.index.rename("name", inplace=True)
    main_table = rosterdf.join(temp, on="name")

    # results section
    cols = ["num_result", "duration", "team_points", "binary_result", "bonus", "pin"]
    temp = athlete_df[cols]
    temp["binary_result"] = temp.binary_result * 100
    temp["bonus"] = temp.bonus * 100
    temp["pin"] = temp.pin * 100
    temp["duration"] = temp.duration.apply(
        lambda x: f"{int(x / 60):02}:{int(x % 60):02}"
    )  # f-string formatting
    temp.index.rename("name", inplace=True)
    main_table = main_table.join(temp, on="name")

    # positions section
    _neutral_cols = [
        "focus_T2",
        "opp_T2",
        "focus_E1",
        "opp_E1",
        "focus_NEU",
        "opp_NEU",
        "overtime",
    ]
    _bottom_cols = [
        "focus_E1",
        "focus_R2",
        "focus_BOT",
        "opp_TOP",
        "opp_N2",
        "opp_N4",
        "opp_T2",
        "opp_R2",
    ]
    _top_cols = [
        "focus_T2",
        "focus_R2",
        "focus_TOP",
        "opp_BOT",
        "focus_N2",
        "focus_N4",
        "opp_E1",
        "opp_R2",
    ]
    _escape_cols = ["focus_E1", "focus_R2", "opp_T2", "opp_R2", "focus_BOT", "opp_TOP"]
    _ride_cols = ["opp_E1", "opp_R2", "focus_T2", "focus_R2", "focus_TOP", "opp_BOT"]
    _turn_cols = [
        "focus_N2",
        "focus_N4",
        "focus_T2",
        "focus_R2",
        "focus_TOP",
        "opp_BOT",
    ]

    temp = athlete_df
    for name in temp.index:
        temp.loc[name, "neutral_pts"] = calc.calculate_neutral_pts(
            df[df.focus_name == name][_neutral_cols].sum()
        )
        temp.loc[name, "bottom_pts"] = calc.calculate_bottom_pts(
            df[df.focus_name == name][_bottom_cols].sum()
        )
        temp.loc[name, "top_pts"] = calc.calculate_top_pts(
            df[df.focus_name == name][_top_cols].sum()
        )
        temp.loc[name, "escape_percent"] = calc.calculate_escape_per(
            df[df.focus_name == name][_escape_cols].sum()
        )
        temp.loc[name, "ride_percent"] = calc.calculate_ride_per(
            df[df.focus_name == name][_ride_cols].sum()
        )
        temp.loc[name, "turn_percent"] = calc.calculate_turn_per(
            df[df.focus_name == name][_turn_cols].sum()
        )
    temp.index.rename("name", inplace=True)
    main_table = main_table.join(
        athlete_df[
            [
                "neutral_pts",
                "bottom_pts",
                "top_pts",
                "escape_percent",
                "ride_percent",
                "turn_percent",
            ]
        ],
        on="name",
    )

    # diffs section
    # hacky solution to events having never occurred
    main_event_list = [
        "focus_T2",
        "opp_T2",
        "focus_E1",
        "opp_E1",
        "focus_R2",
        "opp_R2",
        "focus_N2",
        "opp_N2",
        "focus_N4",
        "opp_N4",
        "focus_WS",
        "opp_WS",
        "focus_S1",
        "opp_S1",
        "focus_C",
        "opp_C",
        "focus_P1",
        "opp_P1",
        "focus_P2",
        "opp_P2",
        "focus_RO1",
        "opp_RO1",
    ]
    temp = athlete_df
    not_columns = [col for col in main_event_list if col not in temp.columns]
    for col in not_columns:
        temp[col] = 0
    # end hacky solution
    new = pd.DataFrame()
    new["T2"] = temp["focus_T2"] - temp["opp_T2"]
    new["E1"] = temp["focus_E1"] - temp["opp_E1"]
    new["R2"] = temp["focus_R2"] - temp["opp_R2"]
    new["N2"] = temp["focus_N2"] - temp["opp_N2"]
    new["N4"] = temp["focus_N4"] - temp["opp_N4"]
    new["WS"] = temp["focus_WS"] - temp["opp_WS"]
    new["S1"] = temp["focus_S1"] - temp["opp_S1"]
    new["C"] = temp["focus_C"] - temp["opp_C"]
    new["P1"] = temp["focus_P1"] - temp["opp_P1"]
    new["P2"] = temp["focus_P2"] - temp["opp_P2"]
    new["RO1"] = temp["focus_RO1"] - temp["opp_RO1"]
    main_table = main_table.join(new, on="name").round(4)

    return main_table


def generate_date_df(df):
    tbl = (
        df[["date", "event", "num_result", "mov"]]
            .groupby("date")
            .mean()
            .round(2)
            .reset_index()
            .sort_values("date")
    )
    return tbl
