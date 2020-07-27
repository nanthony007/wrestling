#!/usr/bin/env python
# coding: utf-8

from collections import Counter
import datetime
import pickle
from scipy import stats


# ! these all take an aggregated ser (summed!) which is a series
# ! this means calculate once then only access values --> faster than multiple calcs
def calculate_bottom_pts(ser):
    numerator = ser.focus_E1 + ser.focus_R2 * 2 - ser.opp_N2 * 2 + ser.opp_N4 * 4  # pts
    denominator = ser.opp_T2 + ser.opp_R2 + ser.focus_BOT + ser.opp_TOP  # bottom chances
    if denominator > 0:
        return (numerator / denominator)
    else:
        return None  # no bottom chances


def calculate_top_pts(ser):
    numerator = ser.focus_N2 * 2 + ser.focus_N4 * 4 - ser.opp_E1 + ser.opp_R2 * 2
    denominator = (
        ser.focus_T2 + ser.focus_R2 + ser.focus_TOP + ser.opp_BOT
    )  # top chances
    if denominator > 0:
        return (numerator / denominator)
    else:
        return None  # no top chances


def calculate_neutral_pts(ser):
    numerator = ser.focus_T2 * 2 - ser.opp_T2 * 2
    denominator = (
        ser.focus_E1 + ser.opp_E1 + ser.focus_NEU + ser.opp_NEU + 1 + ser.overtime
    )  # neutral chances
    return (numerator / denominator)


def calculate_escape_per(ser):
    numerator = ser.focus_E1 + ser.focus_R2  # num of escapes
    denominator = (
        ser.opp_T2 + ser.opp_R2 + ser.focus_BOT + ser.opp_TOP
    )  # bottom chances
    if denominator > 0:
        return (numerator / denominator) * 100
    else:
        return None  # no bottom chances


def calculate_turn_per(ser):
    numerator = ser.focus_N2 + ser.focus_N4  # num of turns
    denominator = (
        ser.focus_T2 + ser.focus_R2 + ser.focus_TOP + ser.opp_BOT
    )  # top chances
    if denominator > 0:
        return (numerator / denominator) * 100
    else:
        return None  # no top chances


def calculate_ride_per(ser):
	numerator = ser.opp_E1 + ser.opp_R2  # num of opp escapes
	denominator = (
			ser.focus_T2 + ser.focus_R2 + ser.focus_TOP + ser.opp_BOT
	)  # top chances
	if denominator > 0:
		return (1 - numerator / denominator) * 100
	else:
		return None  # no top chances


# todo: KPI related calcs, deal with later
# KPI visual stuff, deal with later.
def get_metric_pretty_label(metric_label):
	label_dict = {
		'matches': '# Matches',
		'num_result': 'Numeric Result',
		'binary_result': 'Win %',
		'bonus': 'Bonus %',
		'pin': 'Pin %',
		'mov': 'MoV',
		'td_diff': 'Takedown Diff',
		'neutral': 'Neutral Pts',
        'bottom': 'Bottom Pts', 
        'top': 'Top Pts', 
        'escape': 'Escape %', 
        'ride': 'Ride %', 
        'turn': 'Turn %', 
    }
    return label_dict.get(metric_label)


def calculate_metric_change(df, metric_label, value_passthrough):
    two_weeks_ago = df.date.max() - datetime.timedelta(weeks=2)
    ref_df = df[df.date < two_weeks_ago]
    # easier slicing
    _neutral_cols = ["focus_T2", "opp_T2", "focus_E1", "opp_E1", "focus_NEU", "opp_NEU", "overtime"]
    _bottom_cols = ["focus_E1", "focus_R2", "focus_BOT", "opp_TOP", "opp_N2", "opp_N4", "opp_T2", "opp_R2"]
    _top_cols = ["focus_T2", "focus_R2", "focus_TOP", "opp_BOT", "focus_N2", "focus_N4", "opp_E1", "opp_R2"]
    _escape_cols = ["focus_E1", "focus_R2", "opp_T2", "opp_R2", "focus_BOT", "opp_TOP"]
    _ride_cols = ["opp_E1", "opp_R2", "focus_T2", "focus_R2", "focus_TOP", "opp_BOT"]
    _turn_cols = ["focus_N2", "focus_N4", "focus_T2", "focus_R2", "focus_TOP", "opp_BOT"]
    if metric_label == "neutral":
        val = calculate_neutral_pts(
            ref_df[_neutral_cols].sum()
        )
    elif metric_label == "bottom":
        val = calculate_bottom_pts(
            ref_df[_bottom_cols].sum()
        )
    elif metric_label == "top":
        val = calculate_top_pts(
            ref_df[_top_cols].sum()
        )
    elif metric_label == "escape":
        val = calculate_escape_per(
                ref_df[_escape_cols].sum()
            )
    elif metric_label == "ride":
        val = calculate_ride_per(
                ref_df[_ride_cols].sum()
            )
    elif metric_label == "turn":
        val = calculate_turn_per(ref_df[_turn_cols].sum())
    elif metric_label in ['binary_result', 'bonus', 'pin']:
        val = ref_df[metric_label].mean() * 100  # for percentages
    elif metric_label in ['num_result', 'td_diff', 'mov']:
        val = ref_df[metric_label].mean()
    elif metric_label == 'matches':
        val = len(ref_df)
    else:
        val = "Error"

    # math to determine % change
    percent_change = (value_passthrough - val) / val * 100
    return percent_change


def calculate_percentage(value, baseline, metric_label, level):
    # check if comparing to teams or wrestlers
    if baseline == 'individual' and 'College' in level:
        with open('data/college/wrestler_metrics.p', 'rb') as f:
            metrics = pickle.load(f)
        return stats.percentileofscore(metrics[metric_label], value)
    elif baseline == 'team' and 'College' in level:
        with open('data/college/team_metrics.p', 'rb') as f:
            metrics = pickle.load(f)
        return stats.percentileofscore(metrics[metric_label], value)
    # check if comparing to teams or wrestlers
    elif baseline == 'individual' and 'High' in level:
        with open('data/high_school/wrestler_metrics.p', 'rb') as f:
            metrics = pickle.load(f)
        return stats.percentileofscore(metrics[metric_label], value)
    elif baseline == 'team' and 'High' in level:
        with open('data/high_school/team_metrics.p', 'rb') as f:
            metrics = pickle.load(f)
        return stats.percentileofscore(metrics[metric_label], value)
    else:
        return ValueError


def get_rank_from_percentile(percentile):
    rank = ''
    if percentile <= 25:
        rank = 'Poor'
    elif percentile <= 50:
        rank = 'Below Average'
    elif percentile <= 75:
        rank = 'Above Average'
    elif percentile <= 90:
        rank = 'Great'
    elif percentile <= 100:
        rank = 'Excellent'
    return rank


def get_metric_value(df, metric_label):
    # easier slicing
    _neutral_cols = ["focus_T2", "opp_T2", "focus_E1", "opp_E1", "focus_NEU", "opp_NEU", "overtime"]
    _bottom_cols = ["focus_E1", "focus_R2", "focus_BOT", "opp_TOP", "opp_N2", "opp_N4", "opp_T2", "opp_R2"]
    _top_cols = ["focus_T2", "focus_R2", "focus_TOP", "opp_BOT", "focus_N2", "focus_N4", "opp_E1", "opp_R2"]
    _escape_cols = ["focus_E1", "focus_R2", "opp_T2", "opp_R2", "focus_BOT", "opp_TOP"]
    _ride_cols = ["opp_E1", "opp_R2", "focus_T2", "focus_R2", "focus_TOP", "opp_BOT"]
    _turn_cols = ["focus_N2", "focus_N4", "focus_T2", "focus_R2", "focus_TOP", "opp_BOT"]
    if metric_label == "neutral":
        val = calculate_neutral_pts(
            df[_neutral_cols].sum()
        )
    elif metric_label == "bottom":
        val = calculate_bottom_pts(
            df[_bottom_cols].sum()
        )
    elif metric_label == "top":
        val = calculate_top_pts(
            df[_top_cols].sum()
        )
    elif metric_label == "escape":
        val = calculate_escape_per(
                df[_escape_cols].sum()
            )
    elif metric_label == "ride":
        val = calculate_ride_per(
                df[_ride_cols].sum()
            )
    elif metric_label == "turn":
        val = calculate_turn_per(
                df[_turn_cols].sum()
            )
    elif metric_label in ['binary_result', 'bonus', 'pin']:
        val = df[metric_label].mean() * 100  # for percentages
    elif metric_label in ['num_result', 'td_diff', 'mov']:
        val = df[metric_label].mean()
    elif metric_label == 'matches':
        val = len(df)
    else:
        val = "Error"
    return val


def generate_kpi_metric(df, baseline, metric_label, level):
    label = get_metric_pretty_label(metric_label)
    value = get_metric_value(df, metric_label)
    change = calculate_metric_change(df, metric_label, value)
    percentile = calculate_percentage(value, baseline, metric_label, level)
    rank = get_rank_from_percentile(percentile)

    return {
        'label': label,
        'value': value,
        'change': change,
        'percentile': percentile,
        'rank': rank,
    }
