#!/usr/bin/env python3
"""
Tests for the LimitRoomTimeSlots constraint.
"""

import os
import tempfile

from satisfaculty import scheduler
from satisfaculty.constraints import AssignAllCourses, NoRoomOverlap, LimitRoomTimeSlots


def test_limit_room_timeslots_basic():
    """Test that a room can be restricted to specific time slots."""
    sched = scheduler.InstructorScheduler()

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
            f.write('Course1,Smith,30,Lecture,Lecture\n')

        # Room restricted to only MWF-0800 slot
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type,Allowed Time Slots\n')
            f.write('Room1,50,Lecture,MWF-0800\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        LimitRoomTimeSlots()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"

    # Course should be in the allowed time slot
    slot = result[result['Course'] == 'Course1']['Slot'].values[0]
    assert slot == 'MWF-0800', f"Course should be in MWF-0800, got {slot}"


def test_limit_room_timeslots_multiple_slots():
    """Test that a room can be allowed multiple specific time slots."""
    sched = scheduler.InstructorScheduler()

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
            f.write('Course1,Smith,30,Lecture,Lecture\n')

        # Room restricted to MWF-0800 and MWF-1200 slots (not MWF-1000)
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type,Allowed Time Slots\n')
            f.write('Room1,50,Lecture,MWF-0800; MWF-1200\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        LimitRoomTimeSlots()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"

    # Course should be in one of the allowed time slots
    slot = result[result['Course'] == 'Course1']['Slot'].values[0]
    assert slot in ['MWF-0800', 'MWF-1200'], f"Course should be in an allowed slot, got {slot}"


def test_limit_room_timeslots_infeasible():
    """Test that scheduling fails when no allowed slots are available."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        # Two courses that need lecture slots
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Jones,30,Lecture,Lecture\n')

        # Only one room, restricted to one slot, but two courses need it
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type,Allowed Time Slots\n')
            f.write('Room1,50,Lecture,MWF-0800\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        LimitRoomTimeSlots()
    ])

    result = sched.lexicographic_optimize([])
    # Should be infeasible - only one slot allowed but two courses
    assert result is None, "Expected infeasible (None) with conflicting constraints"


def test_limit_room_timeslots_unrestricted_room():
    """Test that rooms without the column value are unrestricted."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Jones,30,Lecture,Lecture\n')

        # Room1 restricted, Room2 unrestricted (empty value)
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type,Allowed Time Slots\n')
            f.write('Room1,50,Lecture,MWF-0800\n')
            f.write('Room2,50,Lecture,\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        LimitRoomTimeSlots()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"
    assert len(result) == 2, "Both courses should be scheduled"


def test_limit_room_timeslots_no_column():
    """Test that constraint does nothing when column is missing."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')

        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')

        # No 'Allowed Time Slots' column
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        LimitRoomTimeSlots()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"


def test_limit_room_timeslots_custom_column():
    """Test that a custom column name can be used."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')

        # Using custom column name
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type,Available Slots\n')
            f.write('Room1,50,Lecture,MWF-1000\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        LimitRoomTimeSlots(column='Available Slots')
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"

    slot = result[result['Course'] == 'Course1']['Slot'].values[0]
    assert slot == 'MWF-1000', f"Course should be in MWF-1000, got {slot}"


if __name__ == '__main__':
    test_limit_room_timeslots_basic()
    test_limit_room_timeslots_multiple_slots()
    test_limit_room_timeslots_infeasible()
    test_limit_room_timeslots_unrestricted_room()
    test_limit_room_timeslots_no_column()
    test_limit_room_timeslots_custom_column()
    print('\n' + '=' * 50)
    print('All LimitRoomTimeSlots tests passed!')
    print('=' * 50)
