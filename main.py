from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, detect_owner_conflicts

TODAY = date.today().isoformat()  # e.g. "2026-03-29"

# --- Create pets ---
dog = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
cat = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5)

# --- Create owner with both pets ---
owner = Owner(name="Alex", time_available=90, pets=[dog, cat])

# --- Add tasks to Buddy (dog) out of time order ---
# Feeding and Morning Walk recur daily; Flea Medication recurs weekly
dog.add_task(Task(name="Fetch/Play",      category="enrichment", duration=20, priority="low",    time="15:00", date=TODAY, recurrence=""))
dog.add_task(Task(name="Morning Walk",    category="walk",       duration=30, priority="high",   time="07:00", date=TODAY, recurrence="daily"))
dog.add_task(Task(name="Flea Medication", category="meds",       duration=5,  priority="medium", time="12:00", date=TODAY, recurrence="weekly"))
dog.add_task(Task(name="Feeding",         category="feeding",    duration=10, priority="high",   time="08:30", date=TODAY, recurrence="daily"))

# --- Add tasks to Whiskers (cat) out of time order ---
cat.add_task(Task(name="Laser Toy", category="enrichment", duration=10, priority="low",    time="18:00", date=TODAY, recurrence=""))
cat.add_task(Task(name="Grooming",  category="grooming",   duration=15, priority="medium", time="10:00", date=TODAY, recurrence="weekly"))
cat.add_task(Task(name="Feeding",   category="feeding",    duration=10, priority="high",   time="07:30", date=TODAY, recurrence="daily"))

# --- Schedule, display, and filter ---
for pet in owner.pets:
    print(f"\n{'='*40}")
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    scheduler.display()

    # --- Recurrence demo: complete every task and show what gets re-queued ---
    print(f"\n--- Completing tasks for {pet.name} ---")
    for task in list(scheduler.scheduled_tasks):
        next_task = scheduler.complete_task(task)
        recur_label = f"  -> next occurrence queued at {next_task.time}" if next_task else "  -> one-off, not re-queued"
        print(f"  Completed: {task.name} [{task.recurrence or 'one-off'}]{recur_label}")

    # --- Filter: all done, show re-queued pending tasks ---
    done    = scheduler.filter_by_status(completed=True)
    pending = scheduler.filter_by_status(completed=False)
    print(f"\nCompleted ({len(done)}): {[t.name for t in done]}")
    print(f"Pending / re-queued ({len(pending)}):")
    for t in pending:
        print(f"  - {t.date} {t.time}  {t.name} [{t.recurrence}]")

# ── Conflict detection demo ───────────────────────────────────────────────────

print(f"\n{'='*40}")
print("CONFLICT DETECTION DEMO")
print('='*40)

conflict_owner = Owner(name="Alex", time_available=120)

# Scenario 1 — overlapping tasks (should produce warnings)
print("\nScenario 1: overlapping time windows (expect warnings)")
dog_conflicts = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
dog_conflicts.add_task(Task(name="Morning Walk", category="walk",       duration=30, priority="high",   time="07:00", date=TODAY))
dog_conflicts.add_task(Task(name="Feeding",      category="feeding",    duration=10, priority="high",   time="07:15", date=TODAY))  # starts during Morning Walk
dog_conflicts.add_task(Task(name="Flea Meds",    category="meds",       duration=5,  priority="medium", time="07:20", date=TODAY))  # starts during both above
dog_conflicts.add_task(Task(name="Play",         category="enrichment", duration=20, priority="low",    time="09:00", date=TODAY))  # no overlap

sched_conflicts = Scheduler(owner=conflict_owner, pet=dog_conflicts)
sched_conflicts.generate_plan()
sched_conflicts.display()
if sched_conflicts.conflicts:
    for w in sched_conflicts.conflicts:
        print(f"  {w}")
else:
    print("  No conflicts found.")

# Scenario 2 — clean schedule (should produce no warnings)
print("\nScenario 2: no overlapping time windows (expect no warnings)")
dog_clean = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
dog_clean.add_task(Task(name="Morning Walk", category="walk",       duration=30, priority="high",   time="07:00", date=TODAY))  # ends 07:30
dog_clean.add_task(Task(name="Feeding",      category="feeding",    duration=10, priority="high",   time="08:00", date=TODAY))  # starts after gap
dog_clean.add_task(Task(name="Play",         category="enrichment", duration=20, priority="low",    time="09:00", date=TODAY))  # no overlap

sched_clean = Scheduler(owner=conflict_owner, pet=dog_clean)
sched_clean.generate_plan()
sched_clean.display()
if sched_clean.conflicts:
    for w in sched_clean.conflicts:
        print(f"  {w}")
else:
    print("  No conflicts found.")

# ── Owner-level conflict detection demo ──────────────────────────────────────

print(f"\n{'='*40}")
print("OWNER-LEVEL CONFLICT DETECTION DEMO")
print('='*40)

multi_owner = Owner(name="Alex", time_available=120)

# Dog has a walk 07:00-07:30 and feeding 08:00-08:10
multi_dog = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
multi_dog.add_task(Task(name="Morning Walk", category="walk",    duration=30, priority="high", time="07:00", date=TODAY))
multi_dog.add_task(Task(name="Feeding",      category="feeding", duration=10, priority="high", time="08:00", date=TODAY))

# Cat has feeding 07:10 — overlaps with the dog's walk (owner can't do both)
multi_cat = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5)
multi_cat.add_task(Task(name="Feeding",  category="feeding",    duration=10, priority="high",   time="07:10", date=TODAY))
multi_cat.add_task(Task(name="Grooming", category="grooming",   duration=15, priority="medium", time="09:00", date=TODAY))

sched_dog = Scheduler(owner=multi_owner, pet=multi_dog)
sched_dog.generate_plan()

sched_cat = Scheduler(owner=multi_owner, pet=multi_cat)
sched_cat.generate_plan()

print("\nBuddy's plan:")
sched_dog.display()
print("\nWhiskers' plan:")
sched_cat.display()

print("\nOwner-level conflicts (across all pets):")
owner_conflicts = detect_owner_conflicts([sched_dog, sched_cat])
if owner_conflicts:
    for w in owner_conflicts:
        print(f"  {w}")
else:
    print("  No conflicts found.")
