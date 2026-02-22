#!/usr/bin/env python3
"""
Tests for room type handling, including multiple room types per room.
"""

import os
import tempfile

from satisfaculty import scheduler
from satisfaculty.constraints import AssignAllCourses, NoRoomOverlap, RoomCapacity


def test_multiple_room_types():
    """Test that a room with multiple types can be used for either type of course."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # One time slot for each type
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('T-0800,T,08:00,10:50,Lab\n')

        # One lecture course and one lab course
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('LectureCourse,Smith,30,Lecture,Lecture\n')
            f.write('LabCourse,Jones,30,Lab,Lab\n')

        # One room that can be either Lecture or Lab
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('FlexRoom,50,Lecture; Lab\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap(),
        RoomCapacity()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"

    # Both courses should be assigned to FlexRoom
    lecture_room = result[result['Course'] == 'LectureCourse']['Room'].values[0]
    lab_room = result[result['Course'] == 'LabCourse']['Room'].values[0]
    assert lecture_room == 'FlexRoom', "Lecture course should be in FlexRoom"
    assert lab_room == 'FlexRoom', "Lab course should be in FlexRoom"


def test_room_type_still_restricts():
    """Test that a room without a matching type cannot be used."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')

        # Lecture course
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('LectureCourse,Smith,30,Lecture,Lecture\n')

        # Only a Lab room (no Lecture type)
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('LabOnly,50,Lab\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap()
    ])

    # This should fail because there's no valid room for the lecture course
    try:
        sched.lexicographic_optimize([])
        assert False, "Should have raised an error for no feasible assignments"
    except ValueError as e:
        assert "No feasible assignments" in str(e)


def test_mixed_room_types():
    """Test scheduling with a mix of single-type and multi-type rooms."""
    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        # Two lecture courses
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Jones,30,Lecture,Lecture\n')

        # One lecture-only room and one flex room
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('LectureRoom,50,Lecture\n')
            f.write('FlexRoom,50,Lecture; Lab\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"

    # Both courses should be scheduled (rooms can be either)
    rooms_used = set(result['Room'].values)
    assert len(result) == 2, "Both courses should be scheduled"
    # At least one of the rooms should be used
    assert rooms_used.issubset({'LectureRoom', 'FlexRoom'})


if __name__ == '__main__':
    test_multiple_room_types()
    test_room_type_still_restricts()
    test_mixed_room_types()
    print('\n' + '='*50)
    print('All room type tests passed!')
    print('='*50)
