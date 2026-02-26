#!/usr/bin/env python3
"""
Tests for the merge_rows visualization feature.
"""

import os
import tempfile
import pandas as pd

from satisfaculty import InstructorScheduler, AssignAllCourses, NoRoomOverlap
from satisfaculty.visualize_schedule import _intervals_overlap, _compute_merged_rows


def test_intervals_overlap_true():
    """Test that overlapping intervals are detected."""
    # Overlapping intervals
    assert _intervals_overlap([(100, 200)], [(150, 250)]) is True
    assert _intervals_overlap([(100, 200)], [(50, 150)]) is True
    assert _intervals_overlap([(100, 200)], [(100, 200)]) is True
    assert _intervals_overlap([(100, 200)], [(50, 250)]) is True  # One contains other


def test_intervals_overlap_false():
    """Test that non-overlapping intervals are not flagged."""
    # Non-overlapping intervals
    assert _intervals_overlap([(100, 200)], [(200, 300)]) is False  # Adjacent
    assert _intervals_overlap([(100, 200)], [(250, 350)]) is False  # Gap
    assert _intervals_overlap([(100, 200)], [(50, 100)]) is False   # Adjacent before


def test_intervals_overlap_multiple():
    """Test overlap detection with multiple intervals."""
    # Multiple intervals, one overlaps
    assert _intervals_overlap([(100, 150), (200, 250)], [(140, 160)]) is True
    # Multiple intervals, none overlap
    assert _intervals_overlap([(100, 150), (200, 250)], [(160, 190)]) is False


def test_compute_merged_rows_no_overlap():
    """Test that non-overlapping rooms are merged into same row."""
    # Create mock day schedule with two rooms at different times
    day_schedule = pd.DataFrame([
        {'Room': 'RoomA', 'StartMin': 480, 'EndMin': 530},   # 8:00-8:50
        {'Room': 'RoomB', 'StartMin': 600, 'EndMin': 650},   # 10:00-10:50
    ])
    rooms = ['RoomA', 'RoomB']
    room_capacity = {'RoomA': 50, 'RoomB': 50}

    merged_rows, room_to_row_idx = _compute_merged_rows(day_schedule, rooms, room_capacity, None)

    # Should merge into single row since no overlap
    assert len(merged_rows) == 1
    assert room_to_row_idx['RoomA'] == room_to_row_idx['RoomB']


def test_compute_merged_rows_with_overlap():
    """Test that overlapping rooms stay in separate rows."""
    # Create mock day schedule with two rooms at same time
    day_schedule = pd.DataFrame([
        {'Room': 'RoomA', 'StartMin': 480, 'EndMin': 530},   # 8:00-8:50
        {'Room': 'RoomB', 'StartMin': 500, 'EndMin': 550},   # 8:20-9:10 (overlaps)
    ])
    rooms = ['RoomA', 'RoomB']
    room_capacity = {'RoomA': 50, 'RoomB': 50}

    merged_rows, room_to_row_idx = _compute_merged_rows(day_schedule, rooms, room_capacity, None)

    # Should stay in separate rows due to overlap
    assert len(merged_rows) == 2
    assert room_to_row_idx['RoomA'] != room_to_row_idx['RoomB']


def test_compute_merged_rows_three_rooms():
    """Test merging with three rooms where two can merge."""
    day_schedule = pd.DataFrame([
        {'Room': 'RoomA', 'StartMin': 480, 'EndMin': 530},   # 8:00-8:50
        {'Room': 'RoomB', 'StartMin': 500, 'EndMin': 550},   # 8:20-9:10 (overlaps A)
        {'Room': 'RoomC', 'StartMin': 600, 'EndMin': 650},   # 10:00-10:50 (no overlap)
    ])
    rooms = ['RoomA', 'RoomB', 'RoomC']
    room_capacity = {'RoomA': 50, 'RoomB': 50, 'RoomC': 50}

    merged_rows, room_to_row_idx = _compute_merged_rows(day_schedule, rooms, room_capacity, None)

    # RoomA and RoomC can share a row (no overlap), RoomB must be separate
    assert len(merged_rows) == 2
    # RoomA comes first, gets row 0. RoomB overlaps A, gets row 1.
    # RoomC doesn't overlap A, so joins row 0.
    assert room_to_row_idx['RoomA'] == room_to_row_idx['RoomC']
    assert room_to_row_idx['RoomA'] != room_to_row_idx['RoomB']


def test_compute_merged_rows_with_mergeable_list():
    """Test that only specified rooms are merged."""
    day_schedule = pd.DataFrame([
        {'Room': 'RoomA', 'StartMin': 480, 'EndMin': 530},   # 8:00-8:50
        {'Room': 'RoomB', 'StartMin': 600, 'EndMin': 650},   # 10:00-10:50 (no overlap with A)
        {'Room': 'RoomC', 'StartMin': 700, 'EndMin': 750},   # 11:40-12:30 (no overlap)
    ])
    rooms = ['RoomA', 'RoomB', 'RoomC']
    room_capacity = {'RoomA': 50, 'RoomB': 50, 'RoomC': 50}

    # Only allow RoomA and RoomB to merge
    mergeable = {'RoomA', 'RoomB'}
    merged_rows, room_to_row_idx = _compute_merged_rows(day_schedule, rooms, room_capacity, mergeable)

    # RoomA and RoomB should merge, RoomC should stay separate
    assert room_to_row_idx['RoomA'] == room_to_row_idx['RoomB']
    assert room_to_row_idx['RoomC'] != room_to_row_idx['RoomA']
    assert len(merged_rows) == 2


def test_compute_merged_rows_mergeable_but_overlap():
    """Test that mergeable rooms still don't merge if they overlap."""
    day_schedule = pd.DataFrame([
        {'Room': 'RoomA', 'StartMin': 480, 'EndMin': 530},   # 8:00-8:50
        {'Room': 'RoomB', 'StartMin': 500, 'EndMin': 550},   # 8:20-9:10 (overlaps A)
    ])
    rooms = ['RoomA', 'RoomB']
    room_capacity = {'RoomA': 50, 'RoomB': 50}

    # Both rooms are mergeable, but they overlap
    mergeable = {'RoomA', 'RoomB'}
    merged_rows, room_to_row_idx = _compute_merged_rows(day_schedule, rooms, room_capacity, mergeable)

    # Should stay in separate rows due to overlap
    assert len(merged_rows) == 2
    assert room_to_row_idx['RoomA'] != room_to_row_idx['RoomB']


def test_visualize_with_merge_rows():
    """Test that visualization runs without errors with merge_rows=True."""
    sched = InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('DEPT-1001-001,Smith,30,Lecture,Lecture\n')
            f.write('DEPT-2001-001,Jones,30,Lecture,Lecture\n')

        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')
            f.write('Room2,50,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

        sched.add_constraints([AssignAllCourses(), NoRoomOverlap()])
        result = sched.lexicographic_optimize([])
        assert result is not None

        # Test visualization with merge_rows
        output_file = os.path.join(tmpdir, 'test_merged.png')
        sched.visualize_schedule(output_file, merge_rows=True)
        assert os.path.exists(output_file)


def test_visualize_with_merge_rows_list():
    """Test that visualization runs with merge_rows as a list of room names."""
    sched = InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')
            f.write('MWF-1200,MWF,12:00,12:50,Lecture\n')

        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('DEPT-1001-001,Smith,30,Lecture,Lecture\n')
            f.write('DEPT-2001-001,Jones,30,Lecture,Lecture\n')
            f.write('DEPT-3001-001,Brown,30,Lecture,Lecture\n')

        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')
            f.write('Room2,50,Lecture\n')
            f.write('Room3,50,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

        sched.add_constraints([AssignAllCourses(), NoRoomOverlap()])
        result = sched.lexicographic_optimize([])
        assert result is not None

        # Test visualization with merge_rows as a list (only merge Room1 and Room2)
        output_file = os.path.join(tmpdir, 'test_merged_list.png')
        sched.visualize_schedule(output_file, merge_rows=['Room1', 'Room2'])
        assert os.path.exists(output_file)


if __name__ == '__main__':
    test_intervals_overlap_true()
    test_intervals_overlap_false()
    test_intervals_overlap_multiple()
    test_compute_merged_rows_no_overlap()
    test_compute_merged_rows_with_overlap()
    test_compute_merged_rows_three_rooms()
    test_compute_merged_rows_with_mergeable_list()
    test_compute_merged_rows_mergeable_but_overlap()
    test_visualize_with_merge_rows()
    test_visualize_with_merge_rows_list()
    print('\n' + '=' * 50)
    print('All merge_rows visualization tests passed!')
    print('=' * 50)
