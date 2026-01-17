#!/usr/bin/env python3
"""
Tests for utility functions.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from satisfaculty.utils import expand_days, time_to_minutes, minutes_to_time


def test_expand_days_mwf():
    """Test MWF expands to Monday, Wednesday, Friday."""
    assert expand_days('MWF') == ['M', 'W', 'F']


def test_expand_days_tth():
    """Test TTH expands to Tuesday, Thursday."""
    assert expand_days('TTH') == ['T', 'TH']


def test_expand_days_mw():
    """Test MW expands to Monday, Wednesday."""
    assert expand_days('MW') == ['M', 'W']


def test_expand_days_single_day():
    """Test single days return as single-element list."""
    assert expand_days('M') == ['M']
    assert expand_days('T') == ['T']
    assert expand_days('W') == ['W']
    assert expand_days('TH') == ['TH']
    assert expand_days('F') == ['F']


def test_expand_days_mwth():
    """Test MWTH expands correctly."""
    assert expand_days('MWTH') == ['M', 'W', 'TH']


def test_expand_days_all_days():
    """Test all five days expand correctly."""
    assert expand_days('MTWTHF') == ['M', 'T', 'W', 'TH', 'F']


def test_time_to_minutes():
    """Test time string to minutes conversion."""
    assert time_to_minutes('00:00') == 0
    assert time_to_minutes('01:00') == 60
    assert time_to_minutes('08:30') == 510
    assert time_to_minutes('12:00') == 720
    assert time_to_minutes('23:59') == 1439


def test_minutes_to_time():
    """Test minutes to time string conversion."""
    assert minutes_to_time(0) == '00:00'
    assert minutes_to_time(60) == '01:00'
    assert minutes_to_time(510) == '08:30'
    assert minutes_to_time(720) == '12:00'
    assert minutes_to_time(1439) == '23:59'


def run_all_tests():
    """Run all tests."""
    print('Running utils tests...\n')

    test_expand_days_mwf()
    print('✓ test_expand_days_mwf passed')

    test_expand_days_tth()
    print('✓ test_expand_days_tth passed')

    test_expand_days_mw()
    print('✓ test_expand_days_mw passed')

    test_expand_days_single_day()
    print('✓ test_expand_days_single_day passed')

    test_expand_days_mwth()
    print('✓ test_expand_days_mwth passed')

    test_expand_days_all_days()
    print('✓ test_expand_days_all_days passed')

    test_time_to_minutes()
    print('✓ test_time_to_minutes passed')

    test_minutes_to_time()
    print('✓ test_minutes_to_time passed')

    print('\n' + '='*50)
    print('All utils tests passed!')
    print('='*50)


if __name__ == '__main__':
    run_all_tests()
