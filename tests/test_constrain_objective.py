#!/usr/bin/env python3
"""
Tests for ConstrainObjective constraint.
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from satisfaculty import (
    InstructorScheduler,
    AssignAllCourses,
    NoRoomOverlap,
    MinimizeClassesBefore,
    MinimizeClassesAfter,
    MaximizePreferredRooms,
    ConstrainObjective,
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


def test_constrain_objective_minimize_defaults_to_lte():
    """Test that minimize objectives default to <= comparison."""
    obj = MinimizeClassesBefore('09:00')
    constraint = ConstrainObjective(obj, 0)

    assert constraint.comparison == '<='
    assert 'at most' in constraint.name


def test_constrain_objective_maximize_defaults_to_gte():
    """Test that maximize objectives default to >= comparison."""
    obj = MaximizePreferredRooms(['Room1'])
    constraint = ConstrainObjective(obj, 3)

    assert constraint.comparison == '>='
    assert 'at least' in constraint.name


def test_constrain_objective_explicit_comparison():
    """Test that explicit comparison overrides default."""
    obj = MinimizeClassesBefore('09:00')
    constraint = ConstrainObjective(obj, 2, comparison='==')

    assert constraint.comparison == '=='
    assert 'exactly' in constraint.name


def test_constrain_objective_invalid_comparison():
    """Test that invalid comparison raises ValueError."""
    obj = MinimizeClassesBefore('09:00')
    try:
        ConstrainObjective(obj, 0, comparison='!=')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "'!='" in str(e)


def test_constrain_objective_enforces_no_classes_before():
    """Test that ConstrainObjective enforces no classes before a time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
            ),
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0800,MWF,08:00,08:50,Lecture\n'
                'MWF-1000,MWF,10:00,10:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([
            AssignAllCourses(),
            NoRoomOverlap(),
            # No classes before 9am
            ConstrainObjective(MinimizeClassesBefore('09:00'), 0),
        ])

        result = scheduler.lexicographic_optimize([])

        assert result is not None
        assert len(result) == 1
        # Must pick the 10:00 slot since 8:00 would violate the constraint
        assert result.iloc[0]['Start'] == '10:00'


def test_constrain_objective_enforces_minimum_preferred_rooms():
    """Test that ConstrainObjective enforces minimum classes in preferred rooms."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data=(
                'Room,Capacity,Room Type\n'
                'Room1,100,Lecture\n'
                'Room2,100,Lecture\n'
            ),
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Jones,50,Lecture,Lecture\n'
            ),
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0900,MWF,09:00,09:50,Lecture\n'
                'MWF-1100,MWF,11:00,11:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([
            AssignAllCourses(),
            NoRoomOverlap(),
            # At least 2 classes in Room1
            ConstrainObjective(MaximizePreferredRooms(['Room1']), 2),
        ])

        result = scheduler.lexicographic_optimize([])

        assert result is not None
        assert len(result) == 2
        # Both must be in Room1 to satisfy >= 2
        assert all(result['Room'] == 'Room1')


def test_constrain_objective_exact_count():
    """Test that ConstrainObjective with == enforces exact count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
                'C2,Jones,50,Lecture,Lecture\n'
            ),
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0800,MWF,08:00,08:50,Lecture\n'
                'MWF-1000,MWF,10:00,10:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([
            AssignAllCourses(),
            NoRoomOverlap(),
            # Exactly 1 class before 9am
            ConstrainObjective(MinimizeClassesBefore('09:00'), 1, comparison='=='),
        ])

        result = scheduler.lexicographic_optimize([])

        assert result is not None
        assert len(result) == 2
        # Exactly one should be before 9am
        starts = result['Start'].tolist()
        assert '08:00' in starts
        assert '10:00' in starts


def test_constrain_objective_makes_problem_infeasible():
    """Test that impossible constraints make the problem infeasible."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rooms_file, courses_file, slots_file = create_test_files(
            tmpdir,
            rooms_data='Room,Capacity,Room Type\nRoom1,100,Lecture\n',
            courses_data=(
                'Course,Instructor,Enrollment,Slot Type,Room Type\n'
                'C1,Smith,50,Lecture,Lecture\n'
            ),
            # Only one slot, and it's before 9am
            slots_data=(
                'Slot,Days,Start,End,Slot Type\n'
                'MWF-0800,MWF,08:00,08:50,Lecture\n'
            ),
        )

        scheduler = InstructorScheduler()
        scheduler.load_rooms(rooms_file)
        scheduler.load_courses(courses_file)
        scheduler.load_time_slots(slots_file)
        scheduler.add_constraints([
            AssignAllCourses(),
            NoRoomOverlap(),
            # No classes before 9am - but only slot is before 9am!
            ConstrainObjective(MinimizeClassesBefore('09:00'), 0),
        ])

        result = scheduler.lexicographic_optimize([])

        # Should be infeasible
        assert result is None


def run_all_tests():
    """Run all tests."""
    print('Running ConstrainObjective tests...\n')

    test_constrain_objective_minimize_defaults_to_lte()
    print('✓ test_constrain_objective_minimize_defaults_to_lte passed')

    test_constrain_objective_maximize_defaults_to_gte()
    print('✓ test_constrain_objective_maximize_defaults_to_gte passed')

    test_constrain_objective_explicit_comparison()
    print('✓ test_constrain_objective_explicit_comparison passed')

    test_constrain_objective_invalid_comparison()
    print('✓ test_constrain_objective_invalid_comparison passed')

    test_constrain_objective_enforces_no_classes_before()
    print('✓ test_constrain_objective_enforces_no_classes_before passed')

    test_constrain_objective_enforces_minimum_preferred_rooms()
    print('✓ test_constrain_objective_enforces_minimum_preferred_rooms passed')

    test_constrain_objective_exact_count()
    print('✓ test_constrain_objective_exact_count passed')

    test_constrain_objective_makes_problem_infeasible()
    print('✓ test_constrain_objective_makes_problem_infeasible passed')

    print('\n' + '='*50)
    print('All ConstrainObjective tests passed!')
    print('='*50)


if __name__ == '__main__':
    run_all_tests()
