#!/usr/bin/env python3
"""
Utility functions for the scheduling system.
"""


def time_to_minutes(time_str):
    """Convert time string HH:MM to minutes since midnight."""
    h, m = map(int, time_str.split(':'))
    return h * 60 + m


def minutes_to_time(minutes):
    """Convert minutes since midnight to time string HH:MM."""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def expand_days(days_str):
    """Expand day codes to individual days. e.g. MWF -> [M, W, F], TTH -> [T, TH]"""
    result = []
    i = 0
    while i < len(days_str):
        # Check for TH (Thursday) first since it's two characters
        if i + 1 < len(days_str) and days_str[i:i+2] == 'TH':
            result.append('TH')
            i += 2
        else:
            result.append(days_str[i])
            i += 1
    return result
