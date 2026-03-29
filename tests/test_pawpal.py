from pawpal_system import Task, Pet, Owner, Scheduler, detect_owner_conflicts


def test_task_completion_changes_status():
    task = Task(name="Morning Walk", category="walk", duration=30, priority="high")
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Feeding", category="feeding", duration=10, priority="high"))
    assert len(pet.get_tasks()) == 1


# --- Scheduling / Sorting ---

def make_scheduler(time_available, tasks):
    owner = Owner(name="Alex", time_available=time_available)
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    for t in tasks:
        pet.add_task(t)
    return Scheduler(owner=owner, pet=pet)


def test_generate_plan_exact_budget_fit():
    s = make_scheduler(40, [
        Task(name="Walk", category="walk", duration=30, priority="high"),
        Task(name="Feed", category="feeding", duration=10, priority="medium"),
    ])
    s.generate_plan()
    assert len(s.scheduled_tasks) == 2
    assert s.is_over_budget() is False


def test_generate_plan_single_task_exceeds_budget_is_skipped():
    s = make_scheduler(20, [
        Task(name="Long Walk", category="walk", duration=60, priority="high"),
    ])
    s.generate_plan()
    assert len(s.scheduled_tasks) == 0


def test_generate_plan_low_priority_fits_high_priority_skipped():
    # High-priority task is too long; low-priority fits. Greedy never backfills.
    s = make_scheduler(15, [
        Task(name="Long Walk", category="walk", duration=60, priority="high"),
        Task(name="Quick Feed", category="feeding", duration=10, priority="low"),
    ])
    s.generate_plan()
    names = [t.name for t in s.scheduled_tasks]
    assert "Long Walk" not in names
    assert "Quick Feed" in names


def test_generate_plan_unknown_priority_scheduled_last():
    s = make_scheduler(60, [
        Task(name="Mystery Task", category="enrichment", duration=10, priority="unknown"),
        Task(name="Walk", category="walk", duration=10, priority="high"),
    ])
    s.generate_plan()
    assert s.scheduled_tasks[0].name == "Walk"
    assert s.scheduled_tasks[1].name == "Mystery Task"


def test_generate_plan_all_same_priority_all_fit():
    s = make_scheduler(60, [
        Task(name="Task A", category="walk", duration=10, priority="medium"),
        Task(name="Task B", category="feeding", duration=10, priority="medium"),
        Task(name="Task C", category="meds", duration=10, priority="medium"),
    ])
    s.generate_plan()
    assert len(s.scheduled_tasks) == 3


# --- Recurring Tasks ---

def test_next_occurrence_daily_advances_one_day():
    task = Task(name="Walk", category="walk", duration=30, priority="high",
                date="2025-03-01", recurrence="daily")
    next_task = task.next_occurrence()
    assert next_task.date == "2025-03-02"
    assert next_task.is_completed is False


def test_next_occurrence_weekly_advances_seven_days():
    task = Task(name="Grooming", category="grooming", duration=60, priority="medium",
                date="2025-03-01", recurrence="weekly")
    next_task = task.next_occurrence()
    assert next_task.date == "2025-03-08"


def test_next_occurrence_weekly_crosses_year_boundary():
    task = Task(name="Walk", category="walk", duration=30, priority="high",
                date="2025-12-28", recurrence="weekly")
    next_task = task.next_occurrence()
    assert next_task.date == "2026-01-04"


def test_next_occurrence_no_date_returns_empty_date():
    task = Task(name="Walk", category="walk", duration=30, priority="high",
                date="", recurrence="daily")
    next_task = task.next_occurrence()
    assert next_task.date == ""


def test_complete_task_one_off_returns_none():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=60)
    task = Task(name="Walk", category="walk", duration=30, priority="high", recurrence="")
    pet.add_task(task)
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    result = s.complete_task(task)
    assert result is None
    assert len(s.scheduled_tasks) == 1  # no new task added


def test_complete_task_recurring_adds_next_occurrence():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=60)
    task = Task(name="Walk", category="walk", duration=30, priority="high",
                date="2025-03-01", recurrence="daily")
    pet.add_task(task)
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    next_task = s.complete_task(task)
    assert next_task is not None
    assert next_task.date == "2025-03-02"
    assert next_task in s.scheduled_tasks
    assert next_task in pet.get_tasks()


# --- Chronological ordering ---

def test_generate_plan_tasks_sorted_chronologically():
    s = make_scheduler(120, [
        Task(name="Evening Meds", category="meds", duration=10, priority="high", time="18:00"),
        Task(name="Morning Walk", category="walk", duration=30, priority="high", time="07:00"),
        Task(name="Midday Feed", category="feeding", duration=15, priority="high", time="12:00"),
    ])
    s.generate_plan()
    times = [t.time for t in s.scheduled_tasks]
    assert times == sorted(times)


# --- Conflict Detection ---

def test_detect_conflicts_overlapping_tasks():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=60, priority="high",
                      time="08:00", date="2025-03-01"))
    pet.add_task(Task(name="Feed", category="feeding", duration=30, priority="high",
                      time="08:30", date="2025-03-01"))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    assert len(s.conflicts) == 1
    assert "Walk" in s.conflicts[0]
    assert "Feed" in s.conflicts[0]


def test_detect_conflicts_adjacent_tasks_no_conflict():
    # Task A ends at 08:30, Task B starts at 08:30 — interval test a_start < b_end
    # evaluates 450 < 450 = False, so no conflict expected.
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=30, priority="high",
                      time="08:00", date="2025-03-01"))
    pet.add_task(Task(name="Feed", category="feeding", duration=30, priority="high",
                      time="08:30", date="2025-03-01"))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    assert s.conflicts == []


def test_detect_conflicts_same_start_time():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=30, priority="high",
                      time="08:00", date="2025-03-01"))
    pet.add_task(Task(name="Feed", category="feeding", duration=20, priority="high",
                      time="08:00", date="2025-03-01"))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    assert len(s.conflicts) == 1


def test_detect_conflicts_same_start_time_undated():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=30, priority="high",
                      time="08:00", date=""))
    pet.add_task(Task(name="Feed", category="feeding", duration=20, priority="high",
                      time="08:00", date=""))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    assert len(s.conflicts) == 1


def test_detect_conflicts_different_dates_no_conflict():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=60, priority="high",
                      time="08:00", date="2025-03-01"))
    pet.add_task(Task(name="Feed", category="feeding", duration=60, priority="high",
                      time="08:00", date="2025-03-02"))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    assert s.conflicts == []


def test_detect_conflicts_undated_tasks_always_compared():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=60, priority="high",
                      time="08:00", date=""))
    pet.add_task(Task(name="Feed", category="feeding", duration=60, priority="high",
                      time="08:30", date=""))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    assert len(s.conflicts) == 1


# --- Cross-pet Conflict Detection ---

def test_detect_owner_conflicts_cross_pet_overlap():
    owner = Owner(name="Alex", time_available=120)

    pet1 = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    pet1.add_task(Task(name="Dog Walk", category="walk", duration=60, priority="high",
                       time="08:00", date="2025-03-01"))

    pet2 = Pet(name="Whiskers", species="Cat", breed="Siamese", age=2)
    pet2.add_task(Task(name="Cat Feed", category="feeding", duration=30, priority="high",
                       time="08:30", date="2025-03-01"))

    s1 = Scheduler(owner=owner, pet=pet1)
    s2 = Scheduler(owner=owner, pet=pet2)
    s1.generate_plan()
    s2.generate_plan()

    warnings = detect_owner_conflicts([s1, s2])
    assert len(warnings) == 1
    assert "Buddy" in warnings[0]
    assert "Whiskers" in warnings[0]


def test_detect_owner_conflicts_no_overlap():
    owner = Owner(name="Alex", time_available=120)

    pet1 = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    pet1.add_task(Task(name="Dog Walk", category="walk", duration=30, priority="high",
                       time="08:00", date="2025-03-01"))

    pet2 = Pet(name="Whiskers", species="Cat", breed="Siamese", age=2)
    pet2.add_task(Task(name="Cat Feed", category="feeding", duration=30, priority="high",
                       time="09:00", date="2025-03-01"))

    s1 = Scheduler(owner=owner, pet=pet1)
    s2 = Scheduler(owner=owner, pet=pet2)
    s1.generate_plan()
    s2.generate_plan()

    assert detect_owner_conflicts([s1, s2]) == []


# --- filter_by_status ---

def test_filter_by_status_pending():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    task = Task(name="Walk", category="walk", duration=30, priority="high")
    pet.add_task(task)
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    pending = s.filter_by_status(completed=False)
    assert len(pending) == 1
    task.mark_complete()
    assert s.filter_by_status(completed=False) == []


def test_filter_by_status_unknown_pet_name_returns_empty():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    owner = Owner(name="Alex", time_available=120)
    pet.add_task(Task(name="Walk", category="walk", duration=30, priority="high"))
    s = Scheduler(owner=owner, pet=pet)
    s.generate_plan()
    result = s.filter_by_status(completed=False, pet_name="NoSuchPet")
    assert result == []
