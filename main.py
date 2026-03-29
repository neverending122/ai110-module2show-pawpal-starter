from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create pets ---
dog = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
cat = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5)

# --- Create owner with both pets ---
owner = Owner(name="Alex", time_available=90, pets=[dog, cat])

# --- Add tasks to Buddy (dog) ---
dog.add_task(Task(name="Morning Walk", category="walk", duration=30, priority="high"))
dog.add_task(Task(name="Feeding", category="feeding", duration=10, priority="high"))
dog.add_task(Task(name="Flea Medication", category="meds", duration=5, priority="medium"))
dog.add_task(Task(name="Fetch/Play", category="enrichment", duration=20, priority="low"))

# --- Add tasks to Whiskers (cat) ---
cat.add_task(Task(name="Feeding", category="feeding", duration=10, priority="high"))
cat.add_task(Task(name="Grooming", category="grooming", duration=15, priority="medium"))
cat.add_task(Task(name="Laser Toy", category="enrichment", duration=10, priority="low"))

# --- Schedule and display plans ---
for pet in owner.pets:
    print(f"\n{'='*40}")
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    scheduler.display()
    print()
    print(scheduler.explain_plan())
