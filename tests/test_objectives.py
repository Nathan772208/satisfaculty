#!/usr/bin/env python3
"""
Tests for objective classes.
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from satisfaculty import (
    InstructorScheduler,
    AssignAllCourses,
    NoRoomOverlap,
    MinimizeMinutesAfter,
    MaximizeBackToBackCourses,
    MinimizeBackToBack,
    MinimizeClassesBefore,
    MinimizeClassesAfter,
    MinimizePreferredRooms,
    TargetFill,
    MinimizeTeachingDaysOver,
)


def create_test_files(tmpdir, rooms_data, courses_data, slots_data):
    """Helper to create test CSV files."""
    rooms_file = os.path.join(tmpdir, 'rooms.csv')
    with open(rooms_file, 'w') as f:
        f.write(rooms_data)

    courses_file = os.path.join(tmpdir, 'courses.csv')
    with open(courses_file, 'w') as f:
        f.write(courses_data)

    slots_file = os.path.join(tmpdir, 'time_slots.csv')
    with open(slots_file, 'w') as f:
        f.write(slots_data)

    return rooms_file, courses_file, slots_file


def test_minimize_classes_before_filters_by_days():
    """Test that MinimizeClassesBefore only counts classes on specified days."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
            ),
            # One MWF slot before 10:00 and one TTH slot before 10:00
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0900,MWF,09:00,09:50,Lecture\n'
                'TTH-0900,TTH,09:00,09:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # Minimize classes before 10:00 on M/W/F only
        # Should prefer TTH-0900 (not on M/W/F) over MWF-0900 (on M/W/F)
        result = scheduler.lexicographic_optimize([
            MinimizeClassesBefore('10:00', days=['M', 'W', 'F']),
        ])

        assert result is not None
        assert len(result) == 1
        # Should pick TTH slot since it's not on M/W/F
        assert result.iloc[0]['Days'] == 'TTH'


def test_minimize_classes_after_filters_by_days():
    """Test that MinimizeClassesAfter only counts classes on specified days."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
            ),
            # One MWF slot after 16:00 and one TTH slot after 16:00
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-1600,MWF,16:00,16:50,Lecture\n'
                'TTH-1600,TTH,16:00,16:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # Minimize classes after 16:00 on M/W/F only
        # Should prefer TTH-1600 (not on M/W/F) over MWF-1600 (on M/W/F)
        result = scheduler.lexicographic_optimize([
            MinimizeClassesAfter('16:00', days=['M', 'W', 'F']),
        ])

        assert result is not None
        assert len(result) == 1
        # Should pick TTH slot since it's not on M/W/F
        assert result.iloc[0]['Days'] == 'TTH'


def test_minimize_minutes_after_prefers_earlier_slot():
    """Test that MinimizeMinutesAfter prefers earlier time slots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,50,Lecture,Lecture\n',
            # One slot ends at 15:00, another at 17:00
            slots_data='Slot,Days,Start,End,Slot Type\n'
                      'MWF-1400,MWF,14:00,15:00,Lecture\n'
                      'MWF-1600,MWF,16:00,17:00,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # Minimize minutes after 16:00
        result = scheduler.lexicographic_optimize([MinimizeMinutesAfter('16:00')])

        assert result is not None
        assert len(result) == 1
        # Should pick the 14:00 slot since it ends at 15:00 (before 16:00)
        assert result.iloc[0]['Start'] == '14:00'


def test_minimize_minutes_after_accounts_for_days():
    """Test that MinimizeMinutesAfter multiplies by number of days."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,50,Lecture,Lecture\n',
            # MWF slot ends 30 min after threshold = 30 * 3 = 90 minutes
            # TTH slot ends 40 min after threshold = 40 * 2 = 80 minutes
            slots_data='Slot,Days,Start,End,Slot Type\n'
                      'MWF-1600,MWF,16:00,16:30,Lecture\n'
                      'TTH-1600,TTH,16:00,16:40,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # Minimize minutes after 16:00
        result = scheduler.lexicographic_optimize([MinimizeMinutesAfter('16:00')])

        assert result is not None
        assert len(result) == 1
        # Should pick TTH (80 total minutes) over MWF (90 total minutes)
        assert result.iloc[0]['Days'] == 'TTH'


def test_minimize_minutes_after_zero_when_before_threshold():
    """Test that slots ending before threshold contribute zero."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,50,Lecture,Lecture\n',
            # Both slots end before 17:00
            slots_data='Slot,Days,Start,End,Slot Type\n'
                      'MWF-0800,MWF,08:00,09:00,Lecture\n'
                      'MWF-1400,MWF,14:00,15:00,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # Minimize minutes after 17:00 - both slots should have 0 contribution
        result = scheduler.lexicographic_optimize([MinimizeMinutesAfter('17:00')])

        assert result is not None
        # Either slot is valid since both contribute 0 minutes after 17:00

def test_back_to_back_prefers_consecutive_slots():
    """Test that MaximizeBackToBackCourses prefers consecutive time slots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Jones,50,Lecture,Lecture\n'
            ),
            # S1 and S2 are conscutive and S3 is later
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0905,MWF,09:05,09:55,Lecture\n'
                'MWF-1010,MWF,10:10,11:00,Lecture\n'
                'TTH-1300,TTH,13:00,14:00,Lecture\n'
            ),
        )
        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # Result should prefer back to back time slots of MWF-0905 and MWF-1010
        result = scheduler.lexicographic_optimize([
            MaximizeBackToBackCourses(['C1', 'C2']),
            MinimizeClassesBefore("10:00")
        ])

        assert result is not None
        assert len(result) == 2

        # Extract the assigned start times for C1 and C2
        starts = sorted(result['Start'].tolist())
        # Expect the consecutive pair (09:05, 10:10)
        assert starts == ['09:05', '10:10']


def test_minimize_back_to_back():
    """Test that MinimizeBackToBack avoids consecutive slots for same instructor."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            # One instructor teaches two courses
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Smith,50,Lecture,Lecture\n'
            ),
            # Three consecutive time slots: 9:00, 10:00, 11:00
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0900,MWF,09:00,09:50,Lecture\n'
                'MWF-1000,MWF,10:00,10:50,Lecture\n'
                'MWF-1100,MWF,11:00,11:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # First: MinimizeBackToBack to spread out courses
        # Second: MinimizeClassesAfter("10:00") which would prefer early slots
        #
        # If MinimizeBackToBack works, courses should be in non-adjacent slots
        # (e.g., 9:00 and 11:00) even though MinimizeClassesAfter prefers early times
        # which would push both to 9:00 and 10:00 if unconstrained
        result = scheduler.lexicographic_optimize([
            MinimizeBackToBack(),
            MinimizeClassesAfter("10:00"),
        ])

        assert result is not None
        assert len(result) == 2

        # Extract the assigned start times
        starts = sorted(result['Start'].tolist())
        # Should be 9:00 and 11:00 (non-adjacent) rather than 9:00 and 10:00
        assert starts == ['09:00', '11:00']


def test_target_fill_prefers_correct_room_size():
    """Test that TargetFill prefers rooms matching the target fill ratio."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Room1: 100 capacity, Room2: 50 capacity
        # Course enrollment: 75
        # With 75% target fill:
        #   Room1: target = 75, penalty = (75-75)^2 = 0 (perfect)
        #   Room2: target = 37.5, penalty = (75-37.5)^2 = 1406.25 (bad)
        #
        # MinimizePreferredRooms(['Room1']) would prefer Room2 to avoid Room1,
        # but TargetFill as the primary objective should override this.
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\nRoom2,50,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,75,Lecture,Lecture\n',
            slots_data='Slot,Days,Start,End,Slot Type\nMWF-0900,MWF,09:00,09:50,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # TargetFill wants Room1 (perfect fit), MinimizePreferredRooms wants Room2
        # TargetFill should win since it's first in lexicographic order
        result = scheduler.lexicographic_optimize([
            TargetFill(0.75),
            MinimizePreferredRooms(['Room1']),
        ])

        assert result is not None
        assert result.iloc[0]['Room'] == 'Room1'  # TargetFill should override


def test_minimize_teaching_days_over_prefers_fewer_days():
    """Test that MinimizeTeachingDaysOver prefers MWF (3 days) over MWF+TTH (5 days)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup: One instructor teaches 2 courses
        # Slots: MWF-0900, MWF-1100, TTH-0900
        # Expected: Both courses on MWF slots (3 days total) rather than split (5 days)
        # Note: Need 20+ min gap between MWF slots due to 15-min buffer in NoRoomOverlap
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Smith,50,Lecture,Lecture\n'
            ),
            # MWF slots (3 days) with sufficient gap, and TTH slot (2 additional days if used)
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0900,MWF,09:00,09:50,Lecture\n'
                'MWF-1100,MWF,11:00,11:50,Lecture\n'
                'TTH-0900,TTH,09:00,09:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # MinimizeTeachingDaysOver should prefer keeping both courses on MWF (3 days)
        # rather than splitting across MWF and TTH (5 days)
        result = scheduler.lexicographic_optimize([
            MinimizeTeachingDaysOver(threshold=3, instructors=['Smith']),
        ])

        assert result is not None
        assert len(result) == 2

        # Both courses should be assigned to MWF slots
        days_list = result['Days'].tolist()
        assert all(days == 'MWF' for days in days_list), f"Expected all MWF, got {days_list}"


def test_minimize_teaching_days_over_filters_by_instructor():
    """Test that MinimizeTeachingDaysOver only affects specified instructors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Two instructors, but only Smith should be limited
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\nRoom2,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Smith,50,Lecture,Lecture\n'
                'C3,Jones,50,Lecture,Lecture\n'
                'C4,Jones,50,Lecture,Lecture\n'
            ),
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0900,MWF,09:00,09:50,Lecture\n'
                'MWF-1100,MWF,11:00,11:50,Lecture\n'
                'TTH-0900,TTH,09:00,09:50,Lecture\n'
                'TTH-1100,TTH,11:00,11:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        result = scheduler.lexicographic_optimize([
            MinimizeTeachingDaysOver(threshold=3, instructors=['Smith']),
        ])

        assert result is not None
        assert len(result) == 4

        # Smith should have courses on same day pattern (MWF or TTH)
        smith_courses = result[result['Instructor'] == 'Smith']
        smith_days = smith_courses['Days'].unique()
        assert len(smith_days) == 1, f"Smith should teach on one day pattern, got {list(smith_days)}"


def test_minimize_teaching_days_over_applies_to_all_when_no_instructors():
    """Test that MinimizeTeachingDaysOver applies to all instructors when instructors is None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Note: Need 20+ min gap between MWF slots due to 15-min buffer in NoRoomOverlap
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Smith,50,Lecture,Lecture\n'
            ),
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0900,MWF,09:00,09:50,Lecture\n'
                'MWF-1100,MWF,11:00,11:50,Lecture\n'
                'TTH-0900,TTH,09:00,09:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([AssignAllCourses(), NoRoomOverlap()])

        # With instructors=None, should apply to all instructors
        result = scheduler.lexicographic_optimize([
            MinimizeTeachingDaysOver(threshold=3, instructors=None),
        ])

        assert result is not None
        assert len(result) == 2

        # Both courses should be on MWF (3 days) rather than split
        days_list = result['Days'].tolist()
        assert all(days == 'MWF' for days in days_list), f"Expected all MWF, got {days_list}"


def run_all_tests():
    """Run all tests."""
    print('Running objectives tests...\n')

    test_minimize_classes_before_filters_by_days()
    print('✓ test_minimize_classes_before_filters_by_days passed')

    test_minimize_classes_after_filters_by_days()
    print('✓ test_minimize_classes_after_filters_by_days passed')

    test_minimize_minutes_after_prefers_earlier_slot()
    print('✓ test_minimize_minutes_after_prefers_earlier_slot passed')

    test_minimize_minutes_after_accounts_for_days()
    print('✓ test_minimize_minutes_after_accounts_for_days passed')

    test_minimize_minutes_after_zero_when_before_threshold()
    print('✓ test_minimize_minutes_after_zero_when_before_threshold passed')

    test_back_to_back_prefers_consecutive_slots()
    print('✓ test_maximize_back_to_back_prefers_consecutive_slots passed')

    test_minimize_back_to_back()
    print('✓ test_minimize_back_to_back passed')

    test_target_fill_prefers_correct_room_size()
    print('✓ test_target_fill_prefers_correct_room_size passed')

    test_minimize_teaching_days_over_prefers_fewer_days()
    print('✓ test_minimize_teaching_days_over_prefers_fewer_days passed')

    test_minimize_teaching_days_over_filters_by_instructor()
    print('✓ test_minimize_teaching_days_over_filters_by_instructor passed')

    test_minimize_teaching_days_over_applies_to_all_when_no_instructors()
    print('✓ test_minimize_teaching_days_over_applies_to_all_when_no_instructors passed')

    print('\n' + '='*50)
    print('All objectives tests passed!')
    print('='*50)


if __name__ == '__main__':
    run_all_tests()
