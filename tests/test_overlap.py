#!/usr/bin/env python3
"""
Tests for time overlap constraints.
"""

import os

from satisfaculty import scheduler
from satisfaculty.constraints import AssignAllCourses, NoRoomOverlap, NoInstructorOverlap, NoCourseOverlap

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

def test_course_overlap():
    """Test that NoCourseOverlap prevents specified courses from overlapping."""
    import tempfile
    from satisfaculty import MinimizeClassesBefore

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Two non-overlapping time slots
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        # Three courses with different instructors
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Jones,30,Lecture,Lecture\n')
            f.write('Course3,Brown,30,Lecture,Lecture\n')

        # Three rooms so room overlap isn't the constraint
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')
            f.write('Room2,50,Lecture\n')
            f.write('Room3,50,Lecture\n')

        sched.load_time_slots(time_slots_file)
        sched.load_courses(courses_file)
        sched.load_rooms(rooms_file)

    # Prevent Course1 and Course2 from overlapping (Course3 is not constrained)
    sched.add_constraints([
        AssignAllCourses(),
        NoInstructorOverlap(),
        NoRoomOverlap(),
        NoCourseOverlap(['Course1', 'Course2'])
    ])

    # Use MinimizeClassesBefore to push courses to the later slot (10:00).
    # Without the NoCourseOverlap constraint, all courses would be scheduled
    # at 10:00. The constraint forces Course1 and Course2 to different times.
    result = sched.lexicographic_optimize([MinimizeClassesBefore("9:00")])
    assert result is not None, "Expected a valid solution"

    # Verify Course1 and Course2 are scheduled at different times
    course1_start = result[result['Course'] == 'Course1']['Start'].values[0]
    course2_start = result[result['Course'] == 'Course2']['Start'].values[0]
    assert course1_start != course2_start, "Constrained courses should be at different times"


def test_multiple_instructors_overlap():
    """Test that co-taught courses don't overlap with either instructor's other courses."""
    import tempfile

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Two non-overlapping time slots
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        # Co-taught course (Smith and Jones) plus individual courses for each
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('CoTaught,Smith; Jones,30,Lecture,Lecture\n')
            f.write('SmithOnly,Smith,30,Lecture,Lecture\n')

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

    # Verify co-taught course and Smith's solo course are at different times
    cotaught_start = result[result['Course'] == 'CoTaught']['Start'].values[0]
    smith_start = result[result['Course'] == 'SmithOnly']['Start'].values[0]
    assert cotaught_start != smith_start, "Co-taught course should not overlap with Smith's solo course"


def test_multiple_instructors_unrelated_can_overlap():
    """Test that unrelated instructors can still have courses at the same time."""
    import tempfile

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Only one time slot
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')

        # Two courses with unrelated instructors
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('Course1,Smith,30,Lecture,Lecture\n')
            f.write('Course2,Jones,30,Lecture,Lecture\n')

        # Two rooms
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
    assert result is not None, "Expected a valid solution - unrelated instructors can teach at same time"

    # Both courses should be scheduled at the same time (only time available)
    course1_start = result[result['Course'] == 'Course1']['Start'].values[0]
    course2_start = result[result['Course'] == 'Course2']['Start'].values[0]
    assert course1_start == course2_start, "Unrelated instructors should be able to teach at same time"


def test_multiple_instructors_both_blocked():
    """Test that co-taught course blocks both instructors' time slots."""
    import tempfile

    sched = scheduler.InstructorScheduler()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Two non-overlapping time slots
        time_slots_file = os.path.join(tmpdir, 'time_slots.csv')
        with open(time_slots_file, 'w') as f:
            f.write('Slot,Days,Start,End,Slot Type\n')
            f.write('MWF-0800,MWF,08:00,08:50,Lecture\n')
            f.write('MWF-1000,MWF,10:00,10:50,Lecture\n')

        # Co-taught course plus individual courses for both instructors
        courses_file = os.path.join(tmpdir, 'courses.csv')
        with open(courses_file, 'w') as f:
            f.write('Course,Instructor,Enrollment,Slot Type,Room Type\n')
            f.write('CoTaught,Smith; Jones,30,Lecture,Lecture\n')
            f.write('SmithOnly,Smith,30,Lecture,Lecture\n')
            f.write('JonesOnly,Jones,30,Lecture,Lecture\n')

        # Three rooms so room overlap isn't the constraint
        rooms_file = os.path.join(tmpdir, 'rooms.csv')
        with open(rooms_file, 'w') as f:
            f.write('Room,Capacity,Room Type\n')
            f.write('Room1,50,Lecture\n')
            f.write('Room2,50,Lecture\n')
            f.write('Room3,50,Lecture\n')

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

    # All three courses should be at different times (but we only have 2 slots,
    # so Smith and Jones individual courses can share a slot since they're different instructors)
    cotaught_start = result[result['Course'] == 'CoTaught']['Start'].values[0]
    smith_start = result[result['Course'] == 'SmithOnly']['Start'].values[0]
    jones_start = result[result['Course'] == 'JonesOnly']['Start'].values[0]

    # Co-taught must be different from both individual courses
    assert cotaught_start != smith_start, "Co-taught should not overlap with Smith's solo course"
    assert cotaught_start != jones_start, "Co-taught should not overlap with Jones's solo course"

    # Smith and Jones individual courses CAN be at the same time (different instructors)
    # They should be at the same time since co-taught takes one slot
    assert smith_start == jones_start, "Smith and Jones individual courses should be at same time"


def run_all_tests():
    test_time_overlap()
    test_instructor_overlap()
    test_instructor_overlap_different_days()
    test_course_overlap()
    test_multiple_instructors_overlap()
    test_multiple_instructors_unrelated_can_overlap()
    test_multiple_instructors_both_blocked()

    print('\n' + '='*50)
    print('All overlap tests passed!')
    print('='*50)

if __name__ == '__main__':
    run_all_tests()
