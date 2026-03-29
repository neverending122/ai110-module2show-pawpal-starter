from dataclasses import dataclass, field


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    name: str
    category: str  # walk / feeding / meds / grooming / enrichment
    duration: int  # in minutes
    priority: str  # "high" / "medium" / "low"
    is_completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

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

    def generate_plan(self):
        """Schedule tasks by priority, fitting as many as possible within the owner's time budget."""
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

        self._build_reasoning(skipped, time_remaining)

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

    def is_over_budget(self) -> bool:
        """Return True if scheduled tasks exceed the owner's available time."""
        total = sum(t.duration for t in self.scheduled_tasks)
        return total > self.owner.get_available_time()
