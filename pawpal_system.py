from dataclasses import dataclass, field
from datetime import date, timedelta


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    name: str
    category: str  # walk / feeding / meds / grooming / enrichment
    duration: int  # in minutes
    priority: str  # "high" / "medium" / "low"
    time: str = "00:00"  # scheduled time in HH:MM format
    date: str = ""       # scheduled date in YYYY-MM-DD format
    pet_name: str = ""
    recurrence: str = ""  # "daily", "weekly", or "" for one-off
    is_completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

    def next_occurrence(self) -> "Task":
        """Return a fresh copy of this task scheduled for the next recurrence date.

        Calculates the next date by adding 1 day (daily) or 7 days (weekly) to
        the current date using timedelta. If no date is set, the copy inherits
        the same empty date. The new task is always created with is_completed=False
        so it is ready to be scheduled again.

        Returns:
            A new Task instance with the same fields but an updated date and
            is_completed reset to False.
        """
        if self.date and self.recurrence in ("daily", "weekly"):
            delta = timedelta(days=1 if self.recurrence == "daily" else 7)
            next_date = (date.fromisoformat(self.date) + delta).isoformat()
        else:
            next_date = self.date
        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            time=self.time,
            date=next_date,
            pet_name=self.pet_name,
            recurrence=self.recurrence,
        )

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_tasks(self) -> list[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    time_available: int  # in minutes
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def get_available_time(self) -> int:
        """Return the owner's total available time in minutes."""
        return self.time_available


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: list[Task] = []
        self.reasoning: str = ""
        self.conflicts: list[str] = []

    def generate_plan(self):
        """Schedule tasks by priority, fitting as many as possible within the owner's time budget.

        Uses a two-pass greedy algorithm:
          1. Sort all pet tasks by priority (high -> medium -> low). Tasks with
             an unrecognised priority are placed last.
          2. Iterate in priority order and include each task only if its duration
             fits within the remaining time budget. Tasks that don't fit are
             collected in a skipped list — they are never revisited.
          3. Re-sort the accepted tasks by their HH:MM time so the final schedule
             reads in chronological order for the owner.

        After fitting, builds a plain-English reasoning string and runs
        detect_conflicts() so self.conflicts is always up to date.
        """
        self.scheduled_tasks = []
        skipped = []
        time_remaining = self.owner.get_available_time()

        sorted_tasks = sorted(
            self.pet.get_tasks(),
            key=lambda t: PRIORITY_ORDER.get(t.priority, 99)
        )

        for task in sorted_tasks:
            if task.duration <= time_remaining:
                self.scheduled_tasks.append(task)
                time_remaining -= task.duration
            else:
                skipped.append(task)

        self.scheduled_tasks = sorted(
            self.scheduled_tasks,
            key=lambda t: tuple(map(int, t.time.split(":")))
        )

        self._build_reasoning(skipped, time_remaining)
        self.conflicts = self.detect_conflicts()

    def _build_reasoning(self, skipped: list[Task], time_remaining: int):
        """Build a human-readable explanation of what was scheduled and what was skipped."""
        lines = [
            f"Scheduled {len(self.scheduled_tasks)} task(s) for {self.owner.name}'s pet {self.pet.name}.",
            f"Time budget: {self.owner.get_available_time()} min — {time_remaining} min remaining after scheduling.",
        ]

        if self.scheduled_tasks:
            lines.append("Included tasks (by priority):")
            for task in self.scheduled_tasks:
                lines.append(f"  - {task.name} [{task.priority}] ({task.duration} min)")

        if skipped:
            lines.append("Skipped (not enough time remaining):")
            for task in skipped:
                lines.append(f"  - {task.name} [{task.priority}] ({task.duration} min)")

        self.reasoning = "\n".join(lines)

    def explain_plan(self) -> str:
        """Return the reasoning string from the last generated plan."""
        return self.reasoning

    def display(self):
        """Print the scheduled plan to the terminal."""
        if not self.scheduled_tasks:
            print("No tasks scheduled. Run generate_plan() first or add tasks to the pet.")
            return

        total = sum(t.duration for t in self.scheduled_tasks)
        print(f"Daily Plan for {self.pet.name}")
        print("=" * 30)
        for i, task in enumerate(self.scheduled_tasks, start=1):
            status = "done" if task.is_completed else "pending"
            print(f"{i}. {task.name} ({task.category}) — {task.duration} min [{task.priority}] [{status}]")
        print("=" * 30)
        print(f"Total: {total} min / {self.owner.get_available_time()} min available")
        if self.is_over_budget():
            print("Warning: plan exceeds available time.")

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and, if it recurs, queue the next occurrence.

        Calls mark_complete() on the task, then checks its recurrence field.
        For recurring tasks, next_occurrence() is called to produce a new Task
        with the calculated next date. That task is added to both the pet's
        master task list and scheduled_tasks, then scheduled_tasks is re-sorted
        by time to keep chronological order intact.

        Args:
            task: A Task instance that is currently in scheduled_tasks.

        Returns:
            The newly created Task for the next occurrence, or None if the
            task is a one-off (recurrence == "").
        """
        task.mark_complete()
        if not task.recurrence:
            return None
        next_task = task.next_occurrence()
        self.pet.add_task(next_task)
        self.scheduled_tasks.append(next_task)
        self.scheduled_tasks = sorted(
            self.scheduled_tasks,
            key=lambda t: tuple(map(int, t.time.split(":")))
        )
        return next_task

    def _time_to_minutes(self, t: str) -> int:
        """Convert a HH:MM string to total minutes since midnight.

        Used internally by detect_conflicts to turn time strings into plain
        integers so overlap ranges can be compared with simple arithmetic.

        Args:
            t: A time string in "HH:MM" format, e.g. "07:30".

        Returns:
            An integer representing the number of minutes elapsed since 00:00,
            e.g. "07:30" -> 450.
        """
        h, m = map(int, t.split(":"))
        return h * 60 + m

    def detect_conflicts(self) -> list[str]:
        """Return a warning message for every pair of scheduled tasks whose time windows overlap.

        Two tasks conflict when one starts before the other finishes on the same date.
        Tasks with no date set are compared regardless of date.
        """
        warnings = []
        tasks = self.scheduled_tasks
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                a, b = tasks[i], tasks[j]
                if a.date and b.date and a.date != b.date:
                    continue
                a_start = self._time_to_minutes(a.time)
                b_start = self._time_to_minutes(b.time)
                a_end = a_start + a.duration
                b_end = b_start + b.duration
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Warning: '{a.name}' ({a.time}, {a.duration} min) "
                        f"overlaps with '{b.name}' ({b.time}, {b.duration} min)"
                    )
        return warnings

    def filter_by_status(self, completed: bool, pet_name: str = "") -> list[Task]:
        """Return scheduled tasks filtered by completion status and optionally by pet name.

        Args:
            completed: True to return completed tasks, False for pending ones.
            pet_name: If provided, only return tasks belonging to this pet.
        """
        return [
            t for t in self.scheduled_tasks
            if t.is_completed == completed
            and (not pet_name or t.pet_name == pet_name)
        ]

    def is_over_budget(self) -> bool:
        """Return True if scheduled tasks exceed the owner's available time."""
        total = sum(t.duration for t in self.scheduled_tasks)
        return total > self.owner.get_available_time()


def detect_owner_conflicts(schedulers: list["Scheduler"]) -> list[str]:
    """Return warnings for every cross-pet task overlap across all schedulers.

    Flattens all scheduled tasks from every scheduler into a single list, then
    checks every unique pair for time window overlap using the same interval
    test as detect_conflicts: a_start < b_end and b_start < a_end.
    Tasks on different dates are skipped so recurring tasks from separate days
    do not produce false positives. Each warning includes the pet name of both
    tasks so the owner can tell which pets are involved.

    Args:
        schedulers: A list of Scheduler instances, one per pet, each with
                    generate_plan() already called.

    Returns:
        A list of warning strings describing each overlapping pair. Returns
        an empty list if no conflicts are found.
    """
    all_tasks = [task for sched in schedulers for task in sched.scheduled_tasks]
    warnings = []
    for i in range(len(all_tasks)):
        for j in range(i + 1, len(all_tasks)):
            a, b = all_tasks[i], all_tasks[j]
            if a.date and b.date and a.date != b.date:
                continue
            h, m = map(int, a.time.split(":"))
            a_start = h * 60 + m
            h, m = map(int, b.time.split(":"))
            b_start = h * 60 + m
            a_end = a_start + a.duration
            b_end = b_start + b.duration
            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f"Warning: '{a.name}' ({a.pet_name}, {a.time}, {a.duration} min) "
                    f"overlaps with '{b.name}' ({b.pet_name}, {b.time}, {b.duration} min)"
                )
    return warnings
