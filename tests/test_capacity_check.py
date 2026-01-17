#!/usr/bin/env python3
"""
Tests for the capacity_check method.
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from satisfaculty import InstructorScheduler


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


def test_capacity_check_no_warnings():
    """Test that a feasible problem produces no warnings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\nRoom2,50,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,40,Lecture,Lecture\nC2,Jones,30,Lecture,Lecture\n',
            slots_data='Slot,Days,Start,End,Slot Type\nMWF-0830,MWF,08:30,09:20,Lecture\nMWF-0935,MWF,09:35,10:25,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)

        warnings = scheduler.capacity_check()
        assert warnings == [], f'Expected no warnings, got: {warnings}'


def test_capacity_check_not_enough_slots():
    """Test warning when there aren't enough (slot, room) pairs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,40,Lecture,Lecture\nC2,Jones,30,Lecture,Lecture\nC3,Brown,25,Lecture,Lecture\n',
            slots_data='Slot,Days,Start,End,Slot Type\nMWF-0830,MWF,08:30,09:20,Lecture\nMWF-0935,MWF,09:35,10:25,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)

        # 3 courses, 1 room, 2 slots = 2 pairs, but need 3
        warnings = scheduler.capacity_check()
        assert len(warnings) == 1
        assert 'Slot type' in warnings[0]
        assert '3 courses' in warnings[0]
        assert '2 (time slot, room)' in warnings[0]


def test_capacity_check_course_too_large():
    """Test warning when a course exceeds the largest room capacity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\nRoom2,50,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\nC1,Smith,150,Lecture,Lecture\nC2,Jones,30,Lecture,Lecture\n',
            slots_data='Slot,Days,Start,End,Slot Type\nMWF-0830,MWF,08:30,09:20,Lecture\nMWF-0935,MWF,09:35,10:25,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)

        warnings = scheduler.capacity_check()
        assert any("C1" in w and "150" in w and "100" in w for w in warnings), \
            f'Expected warning about C1 exceeding capacity, got: {warnings}'


def test_capacity_check_too_many_large_courses():
    """Test warning when too many courses need the largest room."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\nRoom2,50,Lecture\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\n'
                        'C1,Smith,80,Lecture,Lecture\n'
                        'C2,Jones,75,Lecture,Lecture\n'
                        'C3,Brown,70,Lecture,Lecture\n',
            slots_data='Slot,Days,Start,End,Slot Type\nMWF-0830,MWF,08:30,09:20,Lecture\nMWF-0935,MWF,09:35,10:25,Lecture\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)

        # 3 courses with enrollment > 50 (need Room1), but only 2 slots for Room1
        warnings = scheduler.capacity_check()
        assert any('enrollment > 50' in w or 'capacity > 50' in w for w in warnings), \
            f'Expected warning about courses needing large rooms, got: {warnings}'


def test_capacity_check_different_room_types():
    """Test that checks are done per room type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nLectureRoom,100,Lecture\nLabRoom,50,Lab\n',
            courses_data='Course,Instructor,Enrollment,Slot Type,Room Type\n'
                        'C1,Smith,40,Lecture,Lecture\n'
                        'C2,Jones,40,Lab,Lab\n'
                        'C3,Brown,40,Lab,Lab\n'
                        'C4,White,40,Lab,Lab\n',
            slots_data='Slot,Days,Start,End,Slot Type\n'
                      'MWF-0830,MWF,08:30,09:20,Lecture\n'
                      'M-0830,M,08:30,10:20,Lab\n'
                      'M-1040,M,10:40,12:30,Lab\n',
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)

        # Lecture: 1 course, 1 room, 1 slot = OK
        # Lab: 3 courses, 1 room, 2 slots = 2 pairs, need 3 -> warning
        warnings = scheduler.capacity_check()
        assert any("Lab" in w and "3 courses" in w for w in warnings), \
            f'Expected warning about Lab slot type, got: {warnings}'
        assert not any("Lecture" in w and "courses" in w for w in warnings), \
            f'Did not expect warning about Lecture, got: {warnings}'


def test_capacity_check_raises_without_data():
    """Test that capacity_check raises error if data not loaded."""
    scheduler = InstructorScheduler()

    try:
        scheduler.capacity_check()
        assert False, 'Expected an exception'
    except (ValueError, AttributeError):
        pass  # Expected - either ValueError or AttributeError is acceptable


def run_all_tests():
    """Run all tests."""
    print('Running capacity_check tests...\n')

    test_capacity_check_no_warnings()
    print('✓ test_capacity_check_no_warnings passed')

    test_capacity_check_not_enough_slots()
    print('✓ test_capacity_check_not_enough_slots passed')

    test_capacity_check_course_too_large()
    print('✓ test_capacity_check_course_too_large passed')

    test_capacity_check_too_many_large_courses()
    print('✓ test_capacity_check_too_many_large_courses passed')

    test_capacity_check_different_room_types()
    print('✓ test_capacity_check_different_room_types passed')

    test_capacity_check_raises_without_data()
    print('✓ test_capacity_check_raises_without_data passed')

    print('\n' + '='*50)
    print('All capacity_check tests passed!')
    print('='*50)


if __name__ == '__main__':
    run_all_tests()
