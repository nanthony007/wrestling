import plotly.express as px
import pandas as pd

margin = dict(l=0, r=0, b=0, t=0, pad=0)


# MAIN CHARTS
def draw_results_hist(match_dicts):
    df = pd.DataFrame.from_records(match_dicts)
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
        legend=dict(xanchor='center', yanchor='top', x=0.5, y=1.0),
        legend_orientation="h",
        legend_title_text=None,
    )


def draw_match_timeseries(match_dicts):
    tdf = pd.DataFrame.from_records(match_dicts)
    df = pd.melt(
        tdf,
        id_vars=["time", "str_label"],
        value_vars=["focus_score", "opp_score"],
    )
    focus_name = tdf.focus_name.iloc[0]
    opp_name = tdf.opp_name.iloc[0]
    df.columns = ["Main Time", "Label", "Wrestler", "Points"]
    df['Wrestler'] = df.Wrestler.apply(
        lambda x: focus_name if x == 'focus_score' else opp_name)
    df['Time'] = df['Main Time'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
    return px.scatter(
        df,
        x='Time',
        y='Points',
        color='Wrestler',
        symbol='Wrestler',
        color_discrete_sequence=["gold", "black"],
        hover_name='Label',
        text='Main Time'
    ).update_traces(
        mode='markers+lines',
        marker=dict(size=10),
        hovertemplate='<b>Event: %{hovertext}</b><br><i>Time: %{text}</i><br>Points: %{y}<extra></extra>'
    ).update_xaxes(
        showticklabels=False,
    ).update_layout(
        margin=margin,
        legend=dict(xanchor='center', yanchor='top', x=0.5, y=1.0),
        legend_orientation="h",
        legend_title_text=None,
        hovermode='x'
    )


def draw_results_sunburst(match_dicts):
    df = pd.DataFrame.from_records(match_dicts)
    df['method'] = df.text_result.apply(lambda x: x.split()[1])
    df['result'] = df.text_result.apply(lambda x: x.split()[0])
    return px.sunburst(
        df,
        path=["result", "method"],
        color_discrete_sequence=["gold", "black"],
        labels=dict(result="Result", method="Method", ),
    ).update_layout(margin=margin, )


def draw_points_sunburst(ts_dicts):
    ts_dicts.pop(0)  # drops START
    df = pd.DataFrame.from_records(ts_dicts)
    return px.sunburst(
        df,
        path=["period", "str_label"]
    ).update_layout(
        showlegend=True,
        legend_title_text="Athlete"
    )


def draw_results_timeseries(match_dicts):
    df = pd.DataFrame.from_records(match_dicts)
    return px.scatter(
        df,
        x='date',
        y='num_result',
        color_discrete_sequence=["gold", "black"],
        hover_name='text_result',
        hover_data={
            'date': True,
            'event_name': True,
            'num_result': False,
        },
    ).update_traces(
        mode='markers+lines',
        marker=dict(size=10),
        hovertemplate="<b>%{hovertext}</b><br>Date=%{customdata[0]}<br>Event=%{customdata[1]}<extra></extra>"
    ).update_yaxes(
        range=[-4.5, 4.5],
        title_text="Result",
    ).update_layout(
        margin=margin,
        legend=dict(xanchor='center', yanchor='top', x=0.5, y=1.0),
        legend_orientation="h",
        legend_title_text=None,
        hovermode='x',
        xaxis_title="Date",
        yaxis_title="Numeric Result",
    )


# todo: fix using moves_df when that logic is created
# needs work!
def draw_points_hist(ts_dicts, points_toggle):
    ts_dicts.pop(0)  # drops START
    df = pd.DataFrame.from_records(ts_dicts)
    return px.bar(
        df,
        x="move",
        y="points" if points_toggle else "count",
        color="wrestler",
        barmode="group",
        orientation="v",
        category_orders=dict(
            move=list(df.move.sort_values()), wrestler=["Focus", "Opponent"]
        ),
        color_discrete_sequence=["gold", "black"],
    ).update_layout(
        xaxis_title="Technique",
        yaxis_title="Points" if points_toggle else "Count",
        margin=margin,
        legend=dict(xanchor='center', yanchor='top', x=0.5, y=1.0),
        legend_orientation="h",
        legend_title_text=None,
    )
