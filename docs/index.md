# satisfaculty

Are you a faculty member or administrator trying to create a schedule that obeys tricky constraints and satisfies many objectives? Satisfaculty can help!

`satisfaculty` is a python package that uses lexicographic mixed-integer linear programming to create academic schedules like the one below:

Note for CU Boulder AERO Faculty: the actual optimization for Fall 2026 can be found [on sharepoint](https://o365coloradoedu.sharepoint.com/:f:/r/sites/AEROENGR-Curriculum/Shared%20Documents/Course%20Scheduling%20Documents/2026-27%20Scheduling/Fall%202026/Fa26%20Algorithm%20Outputs/Latest%20Schedule?csf=1&web=1&e=eG59bR). See the optimize.py script specifically.

![Example schedule output](schedule_visual.png)

## Installation

```bash
pip install satisfaculty
```

## Quick Start

```python
from satisfaculty import *

scheduler = InstructorScheduler()

scheduler.load_rooms('rooms.csv')
scheduler.load_courses('courses.csv')
scheduler.load_time_slots('time_slots.csv')

# Add constraints (required for a valid schedule)
scheduler.add_constraints([
    AssignAllCourses(),
    NoInstructorOverlap(),
    NoRoomOverlap(),
    RoomCapacity(),
    ForceRooms(), # You can always manually override!
    ForceTimeSlots()
])

objectives = [
    MinimizeMinutesAfter('17:00'),
    MinimizeClassesBefore("9:00"),
]
scheduler.lexicographic_optimize(objectives)
scheduler.visualize_schedule()
```

This will output the schedule above.

## Example

Example data files and a script are available in the [`example/`](https://github.com/zsunberg/satisfaculty/tree/main/example) directory of the repository.

## Contents

```{toctree}
:maxdepth: 2

formulation
objectives_guide
```
