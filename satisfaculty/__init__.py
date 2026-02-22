"""Satisfaculty - A course scheduling optimization tool."""

from .scheduler import InstructorScheduler
from .objectives import (
    MinimizeClassesBefore,
    MinimizeClassesAfter,
    MinimizeMinutesAfter,
    MaximizePreferredRooms,
    MinimizePreferredRooms,
    MaximizeBackToBackCourses,
    MinimizeBackToBack,
    TargetFill,
    MinimizeTeachingDaysOver,
)
from .constraints import (
    AssignAllCourses,
    NoInstructorOverlap,
    NoRoomOverlap,
    NoCourseOverlap,
    SameTimeSlot,
    RoomCapacity,
    AvoidRoomsForCourseType,
    ForceRooms,
    ForceTimeSlots,
    InstructorTravelBuffer,
)
from .visualize_schedule import visualize_schedule

__all__ = [
    "InstructorScheduler",
    # Objectives
    "MinimizeClassesBefore",
    "MinimizeClassesAfter",
    "MinimizeMinutesAfter",
    "MaximizePreferredRooms",
    "MinimizePreferredRooms",
    "MaximizeBackToBackCourses",
    "MinimizeBackToBack",
    "TargetFill",
    "MinimizeTeachingDaysOver",
    # Constraints
    "AssignAllCourses",
    "NoInstructorOverlap",
    "NoRoomOverlap",
    "NoCourseOverlap",
    "SameTimeSlot",
    "RoomCapacity",
    "AvoidRoomsForCourseType",
    "ForceRooms",
    "ForceTimeSlots",
    "InstructorTravelBuffer",
    # Utilities
    "visualize_schedule",
]
