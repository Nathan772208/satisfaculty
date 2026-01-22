#!/usr/bin/env python3
"""
Example script demonstrating lexicographic optimization with configurable constraints.

This shows how to define custom constraints and objective priorities for schedule optimization.
Each user can create their own script with different constraint and objective configurations.
"""

from satisfaculty import *

scheduler = InstructorScheduler(solver_verbose=True)
scheduler.load_rooms('rooms.csv')
scheduler.load_courses('courses.csv')
scheduler.load_time_slots('time_slots.csv')

# Find all 2000-level and 3000-level courses
courses_2000 = [c for c in scheduler.courses_df['Course'] if c.startswith('DEPT-2')]
courses_3000 = [c for c in scheduler.courses_df['Course'] if c.startswith('DEPT-3')]

# Add constraints (required for a valid schedule)
scheduler.add_constraints([
    AssignAllCourses(),
    NoInstructorOverlap(),
    NoRoomOverlap(),
    RoomCapacity(),
    ForceRooms(),
    ForceTimeSlots(),
    NoCourseOverlap(courses_2000, name="2000-level"),
    NoCourseOverlap(courses_3000, name="3000-level"),
])

# Define lexicographic optimization objectives (in priority order)
objectives = [
    MinimizeClassesAfter('17:00'),
    MinimizeClassesBefore('9:00'),
]

scheduler.lexicographic_optimize(objectives)
scheduler.save_schedule('schedule.csv')
scheduler.visualize_schedule('schedule_visual.png')
