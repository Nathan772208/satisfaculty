#!/usr/bin/env python3
"""
Example script demonstrating lexicographic optimization with configurable constraints.

This shows how to define custom constraints and objective priorities for schedule optimization.
Each user can create their own script with different constraint and objective configurations.
"""

from satisfaculty import *

scheduler = InstructorScheduler(solver_verbose=True)
scheduler.load_rooms('aes-rooms.csv')
scheduler.load_courses('aes-courses.csv')
scheduler.load_time_slots('aes-time_slots.csv')

# Add constraints (required for a valid schedule)
scheduler.add_constraints([
    AssignAllCourses(),
    NoInstructorOverlap(),
    NoRoomOverlap(),
    RoomCapacity(),
    ForceRooms(),
    ForceTimeSlots(),
])

# Define lexicographic optimization objectives (in priority order)
objectives = [
     MinimizeClassesAfter('17:00'),
    #MinimizeMinutesAfter('17:00'),
    #MinimizeMinutesAfter('16:00'),
    #MinimizeClassesBefore('9:00'),
]

scheduler.lexicographic_optimize(objectives)
scheduler.save_schedule('schedule.csv')
scheduler.visualize_schedule('schedule_visual.png')
