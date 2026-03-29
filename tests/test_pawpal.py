from pawpal_system import Task, Pet


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
