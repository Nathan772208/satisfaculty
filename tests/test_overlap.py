#!/usr/bin/env python3
"""
Tests for time overlap constraints.
"""

import os

from satisfaculty import scheduler
from satisfaculty.constraints import AssignAllCourses, NoRoomOverlap, NoInstructorOverlap

def test_time_overlap():
    """Test that room overlap constraints work correctly with different day patterns."""
    import tempfile

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test time slots with overlapping times but different days
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('T-0830,T,08:30,10:20,Lab\n')
            f.write('TH-0830,TH,08:30,10:20,Lab\n')
            f.write('TTH-0830,TTH,08:30,9:45,Lecture\n')

        # 2 Courses with same instructor
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Lab1,Smith,30,Lab,Lab\n')
            f.write('Lab2,Smith,30,Lab,Lab\n')
            f.write('Course1,Johnson,80,Lecture,Lecture\n')

        # Just 1 room per type
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lab\n')
            f.write('Room2,100,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoRoomOverlap()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"


def test_instructor_overlap():
    """Test that instructor overlap prevents same instructor from teaching at same time."""
    import tempfile

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Two non-overlapping slots (with enough gap for the 15-min buffer)
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')  # 70-min gap, no overlap

        # Two courses with same instructor - must be at different times
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Smith,30,Lecture,Lecture\n')

        # Two rooms so room overlap isn't the constraint
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')
            f.write('Room2,50,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoInstructorOverlap(),
        NoRoomOverlap()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution"

    # Verify the two courses are scheduled at different times
    course1_slot = result[result['Course'] == 'Course1']['Start'].values[0]
    course2_slot = result[result['Course'] == 'Course2']['Start'].values[0]
    assert course1_slot != course2_slot, "Same instructor's courses should be at different times"


def test_instructor_overlap_different_days():
    """Test that instructor can teach at same time on different days."""
    import tempfile

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Two slots at same time but different days
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('T-0800,T,08:00,09:15,Lecture\n')
            f.write('TH-0800,TH,08:00,09:15,Lecture\n')

        # Two courses with same instructor - can be at same time if different days
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Smith,30,Lecture,Lecture\n')

        # Only one room - forces different time slots
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    sched.add_constraints([
        AssignAllCourses(),
        NoInstructorOverlap(),
        NoRoomOverlap()
    ])

    result = sched.lexicographic_optimize([])
    assert result is not None, "Expected a valid solution - same time on different days is allowed"

def run_all_tests():
    test_time_overlap()
    test_instructor_overlap()
    test_instructor_overlap_different_days()

    print('\n' + '='*50)
    print('All overlap tests passed!')
    print('='*50)

if __name__ == '__main__':
    run_all_tests()
