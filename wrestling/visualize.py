import plotly.express as px
import pandas as pd
from collections import Counter
from .enumerations import CollegeLabel, HighSchoolLabel

margin = dict(l=0, r=0, b=0, t=0, pad=0)


# MAIN CHARTS
def draw_results_hist(match_list):
    df = pd.DataFrame.from_records((m.to_dict() for m in match_list))
    return px.histogram(
        df,
        x="method",
        histfunc="count",
        color="result",
        barmode="group",
        category_orders=dict(
            method=["Decision", "Major", "Tech", "Fall", "Forfeit"],
            result=["Win", "Loss"],
        ),
        color_discrete_sequence=["gold", "black"],
        labels=dict(method="Method", result="Result"),
    ).update_layout(
        xaxis_title="Result",
        yaxis_title="Count",
        margin=margin,
        legend=dict(xanchor="center", yanchor="top", x=0.5, y=1.0),
        legend_orientation="h",
        legend_title_text=None,
    )


def draw_match_timeseries(match_list):
    # import add points function and run it on dict!
    # (m.to_dict(time_series_only=True) for m in match_list)
    # add START to dict!
    # add points!
    # make df
    temp_df = pd.DataFrame.from_records((m.to_dict() for m in match_list))
    df = pd.melt(
        temp_df, id_vars=["time", "str_label"], value_vars=["focus_score", "opp_score"],
    )
    focus_name = temp_df.focus_name.iloc[0]
    opp_name = temp_df.opp_name.iloc[0]
    del temp_df
    df.columns = ["Main Time", "Label", "Wrestler", "Points"]
    df["Wrestler"] = df.Wrestler.apply(
        lambda x: focus_name if x == "focus_score" else opp_name
    )
    df["Time"] = df["Main Time"].apply(
        lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1])
    )
    return (
        px.scatter(
            df,
            x="Time",
            y="Points",
            color="Wrestler",
            symbol="Wrestler",
            color_discrete_sequence=["gold", "black"],
            hover_name="Label",
            text="Main Time",
        )
            .update_traces(
            mode="markers+lines",
            marker=dict(size=10),
            hovertemplate="<b>Event: %{hovertext}</b><br><i>Time: %{text}</i><br>Points: %{y}<extra></extra>",
        )
            .update_xaxes(showticklabels=False, )
            .update_layout(
            margin=margin,
            legend=dict(xanchor="center", yanchor="top", x=0.5, y=1.0),
            legend_orientation="h",
            legend_title_text=None,
            hovermode="x",
        )
    )


def draw_results_sunburst(match_list):
    df = pd.DataFrame.from_records((m.to_dict() for m in match_list))
    df["method"] = df.text_result.apply(lambda x: x.split()[1])
    df["result"] = df.text_result.apply(lambda x: x.split()[0])
    return px.sunburst(
        df,
        path=["result", "method"],
        color_discrete_sequence=["gold", "black"],
        labels=dict(result="Result", method="Method", ),
    ).update_layout(margin=margin, )


def draw_results_timeseries(match_list):
    df = pd.DataFrame.from_records((m.to_dict() for m in match_list))
    return (
        px.scatter(
            df,
            x="date",
            y="num_result",
            color_discrete_sequence=["gold", "black"],
            hover_name="text_result",
            hover_data={"date": True, "event_name": True, "num_result": False, },
        )
            .update_traces(
            mode="markers+lines",
            marker=dict(size=10),
            hovertemplate="<b>%{hovertext}</b><br>Date=%{customdata[0]}<br>Event=%{customdata[1]}<extra></extra>",
        )
            .update_yaxes(range=[-4.5, 4.5], title_text="Result", )
            .update_layout(
            margin=margin,
            legend=dict(xanchor="center", yanchor="top", x=0.5, y=1.0),
            legend_orientation="h",
            legend_title_text=None,
            hovermode="x",
            xaxis_title="Date",
            yaxis_title="Numeric Result",
        )
    )


def draw_points_sunburst(match_list):
    dicts = (m.to_dict(time_series_only=True) for m in match_list)
    df = pd.DataFrame.from_records(tuple(sum(dicts, ())))  # flattens
    return px.sunburst(
        df, path=["period", "str_label"], color_discrete_sequence=["gold", "black"],
    ).update_layout(margin=margin, showlegend=True, legend_title_text="Athlete")


# needs work!
def draw_points_hist(match_list, points_toggle, level):
    dicts = (m.to_dict(time_series_only=True) for m in match_list)
    counter = Counter((d["str_label"] for d in tuple(sum(dicts, ()))))
    if level == "college" and points_toggle:
        counter = {
            key: CollegeLabel[key[1:]].value * val
            for key, val in counter.items()
            if key[-1] in ("1", "2", "4")
        }
    elif level == "high school" and points_toggle:
        counter = {
            key: HighSchoolLabel[key[1:]].value * val
            for key, val in counter.items()
            if key[-1] in ("1", "2", "3")
        }
    else:  # points toggle false
        counter = {
            key: val
            for key, val in counter.items()
            if key[-1] not in ("1", "2", "3", "4")
        }
    df = (
        pd.DataFrame.from_dict(counter, orient="index")
            .reset_index()
            .rename(columns={"index": "move", 0: "points"})
    )
    df["wrestler"] = df.move.apply(
        lambda x: "Focus" if x.startswith("f") else "Opponent"
    )
    df["move"] = df.move.apply(lambda x: x[1:])  # strips f/o
    return px.bar(
        df,
        x="points",
        y="move",
        color="wrestler",
        barmode="group",
        orientation="h",
        category_orders=dict(
            # alphabetical sort
            move=list(df.move.sort_values()),
            wrestler=["Opponent", "Focus"],
        ),
        color_discrete_sequence=["black", "gold"],
    ).update_layout(
        margin=margin,
        xaxis_title="Points" if points_toggle else "Counts",
        yaxis_title="Technique",
        legend=dict(
            traceorder="reversed", xanchor="center", yanchor="bottom", x=0.5, y=1.0
        ),
        legend_orientation="h",
        legend_title_text=None,
    )
