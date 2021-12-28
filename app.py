import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from itertools import accumulate, islice
from math import isclose
from typing import List

from interval import Interval


def read_intervals(filepath: str) -> List[Interval]:
    with open(filepath, 'r') as file:
        return [Interval(mid, rad) for (mid, rad) in map(lambda line: map(float, line.split()), file.readlines())]


def generate_subintervals(intervals: List[Interval]) -> List[Interval]:
    bounds = [[interval.min, interval.max] for interval in intervals]
    points = sorted(set(bound for interval in bounds for bound in interval))
    i = 0
    for j, point in enumerate(islice(points, 1, len(points))):
        if not isclose(point, points[i]):
            i += 1
            points[i] = points[j + 1]
    return [Interval((points[idx - 1] + points[idx]) / 2, abs(points[idx - 1] - points[idx]) / 2)
            for idx in range(1, i + 1)]


def calculate_frequencies(intervals: List[Interval], subintervals: List[Interval]) -> List[int]:
    subintervals_mids = [subinterval.mid for subinterval in subintervals]
    return [sum(1 for interval in intervals if subinterval_mid in interval) for subinterval_mid in subintervals_mids]


def calculate_median_by_frequencies(subintervals: List[Interval], frequencies: List[int]) -> Interval:
    frequencies_cumsum = list(accumulate(frequencies))
    m = frequencies_cumsum[-1] / 2.
    idx, _ = max(enumerate(frequencies_cumsum), key=lambda f: f[1] >= m)
    if isclose(frequencies_cumsum[idx], m):
        return (subintervals[idx] + subintervals[idx + 1]) / 2
    return subintervals[idx]


def calculate_median_by_distances_to_intervals(intervals: List[Interval], subintervals: List[Interval]) -> Interval:
    distances_sum = [sum(subinterval.distance_to(interval) for interval in intervals) for subinterval in subintervals]
    idx, _ = min(enumerate(distances_sum), key=lambda d: d[1])
    return subintervals[idx]


def calculate_median_by_distances_and_frequencies(subintervals: List[Interval], frequencies: List[int]) -> Interval:
    distances_sum = [sum(subinterval_i.distance_to(subinterval_j) * frequencies[j]
                         for j, subinterval_j in enumerate(subintervals) if j != i)
                     for i, subinterval_i in enumerate(subintervals)]
    idx, _ = min(enumerate(distances_sum), key=lambda d: d[1])
    return subintervals[idx]


def main():
    intervals = read_intervals('intervals')
    subintervals = generate_subintervals(intervals)
    frequencies = calculate_frequencies(intervals, subintervals)
    frequency_median = calculate_median_by_frequencies(subintervals, frequencies)
    distance_median = calculate_median_by_distances_to_intervals(intervals, subintervals)
    distance_frequency_median = calculate_median_by_distances_and_frequencies(subintervals, frequencies)

    print(frequency_median)
    print(distance_median)
    print(distance_frequency_median)

    df = pd.DataFrame(columns=['interval', 'e', 'y', 'type'])
    for i, interval in enumerate(intervals):
        df = df.append(dict(interval=interval.mid, e=interval.rad, y=i + 1, type='interval'), ignore_index=True)
    for subinterval in subintervals:
        df = df.append(dict(interval=subinterval.mid, e=subinterval.rad, y=0, type='subinterval'), ignore_index=True)
    df = df.append(dict(interval=frequency_median.mid, e=frequency_median.rad, y=-1, type='Me1'), ignore_index=True)
    df = df.append(dict(interval=distance_median.mid, e=distance_median.rad, y=-2, type='Me2'), ignore_index=True)
    df = df.append(dict(interval=distance_frequency_median.mid, e=distance_frequency_median.rad, y=-3, type='Me3'),
                   ignore_index=True)
    fig = px.scatter(df, x='interval', y='y', color='type', error_x='e')
    intervals_count = len(intervals)
    fig.add_trace(go.Scatter(x=[subintervals[0].min, subintervals[0].min], y=[-3, intervals_count], mode='lines',
                             line=dict(color='black', width=1, dash='dash'), showlegend=False))
    for subinterval in subintervals:
        fig.add_trace(go.Scatter(x=[subinterval.max, subinterval.max], y=[-3, intervals_count], mode='lines',
                                 line=dict(color='black', width=1, dash='dash'), showlegend=False))
    fig.update_layout(xaxis=dict(dtick=1, title=''), yaxis=dict(showticklabels=False, visible=False))
    fig.write_html('intervals.html')


if __name__ == '__main__':
    main()
