"""Satisfaculty - A course scheduling optimization tool."""

from .scheduler import InstructorScheduler
from .objectives import (
    MinimizeClassesBefore,
    MinimizeClassesAfter,
    MinimizeMinutesAfter,
    MaximizeClassesInSlots,
    MaximizePreferredRooms,
    MinimizePreferredRooms,
    MaximizeBackToBackCourses,
    MinimizeBackToBack,
    TargetFill,
    MinimizeScheduleChanges,
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
    LimitRoomTimeSlots,
    InstructorTravelBuffer,
)
from .visualize_schedule import visualize_schedule

__all__ = [
    "InstructorScheduler",
    # Objectives
    "MinimizeClassesBefore",
    "MinimizeClassesAfter",
    "MinimizeMinutesAfter",
    "MaximizeClassesInSlots",
    "MaximizePreferredRooms",
    "MinimizePreferredRooms",
    "MaximizeBackToBackCourses",
    "MinimizeBackToBack",
    "TargetFill",
    "MinimizeScheduleChanges",
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
    "LimitRoomTimeSlots",
    "InstructorTravelBuffer",
    # Utilities
    "visualize_schedule",
]
