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


# 2000-level courses that cannot overlap
asen2401_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-2401-")
]

asen2402_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-2402-")
]

asen2403_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-2403-")
]
asen2501_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-2501-")
]

asen2502_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-2502-")
]

#appm2360_section = ["APPM-2360-001"]

# 3000-level courses that cannot overlap (block 1)
asen3401_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3401-")
]

asen3402_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3402-")
]

asen3404_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3404-")
]

asen3501_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3501-")
]

# 3000-level courses that cannot overlap (block 2)
asen3403_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3403-")
]

asen3405_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3405-")
]

asen3502_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3502-")
]

asen3503_section = [c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-3503-")
]

# 4000-level courses that cannot overlap
asen4018_sections = [
    c for c in scheduler.courses_df["Course"]
    if c.startswith("ASEN-4018-")
]
asen4013 = ["ASEN-4013-001"]

# Add constraints (required for a valid schedule)
scheduler.add_constraints([
    AssignAllCourses(),
    NoInstructorOverlap(),
    NoRoomOverlap(),
    RoomCapacity(),
    ForceRooms(),
    ForceTimeSlots(),
    NoCourseOverlap(asen2401_section + asen2402_section + asen2403_section + asen2501_section + asen2502_section, name="ASEN-2401, ASEN-2402, ASEN-2403, ASEN-2501, and ASEN-2502"),
    NoCourseOverlap(asen4013 + asen4018_sections, name="ASEN-4013 and ASEN-4018"),
    NoCourseOverlap(asen3401_section + asen3402_section + asen3404_section + asen3501_section, name="ASEN-3401, ASEN-3402, ASEN-3404, and ASEN-3501"),
    NoCourseOverlap(asen3403_section + asen3405_section + asen3502_section + asen3503_section, name="ASEN-3403, ASEN-3405, ASEN-3502, and ASEN-3503"),
])

# Define lexicographic optimization objectives (in priority order)
objectives = [
    MaximizeBackToBackCourses(
        courses=["ASEN-2502-011", "ASEN-2502-012"],
        same_days=True,
        same_room=True,
        tolerance=0.0
    ),
    MaximizeBackToBackCourses(
        courses=["ASEN-2501-011", "ASEN-2501-012"],
        same_days=True,
        same_room=True,
        tolerance=0.0
    ),
    MaximizeBackToBackCourses(
        courses=["ASEN-3501-011", "ASEN-3501-012", "ASEN-3501-013"],
        same_days=True,
        same_room=True,
        tolerance=0.0
    ),
    MaximizeBackToBackCourses(
        courses=["ASEN-3502-011", "ASEN-3502-012", "ASEN-3502-013"],
        same_days=True,
        same_room=True,
        tolerance=0.0
    ),
    MaximizeBackToBackCourses(
        courses=["ASEN-3503-011", "ASEN-3503-012", "ASEN-3503-013"],
        same_days=True,
        same_room=True,
        tolerance=0.0
    ),
    MinimizePreferredRooms(['MAIN 120']),
    MaximizePreferredRooms(['AERO 120']),
    MinimizeClassesAfter('17:00'),
    MinimizeClassesBefore('9:00'),   
]

scheduler.lexicographic_optimize(objectives)
scheduler.save_schedule('schedule.csv')
scheduler.visualize_schedule('schedule_visual.png')
