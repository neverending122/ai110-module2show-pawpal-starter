from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    category: str  # walk / feeding / meds / grooming / enrichment
    duration: int  # in minutes
    priority: str  # "high" / "medium" / "low"
    is_completed: bool = False

    def mark_complete(self):
        self.is_completed = True

    def is_high_priority(self) -> bool:
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task: Task):
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    time_available: int  # in minutes
    preferences: list[str] = field(default_factory=list)
    pet: Optional[Pet] = None

    def get_available_time(self) -> int:
        return self.time_available


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: list[Task] = []
        self.reasoning: str = ""

    def generate_plan(self):
        pass

    def explain_plan(self) -> str:
        return self.reasoning

    def display(self):
        pass

    def is_over_budget(self) -> bool:
        total = sum(t.duration for t in self.scheduled_tasks)
        return total > self.owner.get_available_time()
