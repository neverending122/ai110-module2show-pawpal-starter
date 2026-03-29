# PawPal+ Project Reflection

## 1. System Design
3 core functions:
- Add the pet
- Add tasks
- Show the schedule
**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My UML design contains all of the objects that could be added with their main characteristics: pet, task. It also includes the owner who has the pets, and scheduler which contains tasks.
My UML includes 4 classes: owner, pet, task, scheduler.
Owner has a pet, a name, preferences, and the available time.
Pet has a name, species, breed, age, owner and tasks associated with it.
Scheduler has an owner, pet, tasks, reasoning, and functions such as add/edit/display plan
Task has a name, category, duration, priority, and whether it is completed or not.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, the design changed in a few ways. The biggest one is that Owner now holds a list of pets instead of just one. This was needed to support multiple pets and to make the cross-pet conflict detection work. Task also gained new fields like time, date, recurrence, and pet_name that weren't in the original UML — those were added once I started implementing the scheduler and realized it needed that information to sort and detect conflicts properly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The scheduler considers priority (high/medium/low) and the owner's available time in minutes. It sorts tasks by priority first and uses a greedy approach — it takes each task in order and only includes it if there is enough time left. Priority was the most important constraint because some tasks like meds and feeding can't be skipped, while enrichment tasks are optional.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The greedy algorithm never backtracks — if a high-priority task doesn't fit, it gets skipped and lower-priority tasks that do fit are still included. The tradeoff is that a high-priority task could be skipped even if a combination of smaller tasks could have made room for it. For daily pet care this is reasonable because it keeps the logic simple and predictable, and the owner gets a warning about what was skipped.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI to review code for bugs, generate test cases, and update the README and help reflection. The most helpful prompts were specific ones like asking it to list edge cases for the scheduler or to check what functions from pawpal_system.py were not yet used in app.py. Asking it to compare the UML to the actual code was also useful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
When the AI generated tests it included one for chronological ordering that I had to verify manually — I checked that the tasks in the test were actually out of order before the sort and that the assertion matched what generate_plan() was supposed to do. I also reviewed the conflict detection tests to make sure the adjacent-task case (no gap, no overlap) was testing the right boundary condition.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
The tests cover priority-based scheduling staying within the time budget, chronological ordering of the final plan, recurring task date calculation for both daily and weekly recurrence including year boundaries, conflict detection for overlapping and adjacent tasks, cross-pet conflict detection, and status filtering. These were important because they are the core behaviors the scheduler promises — if any of them break the plan becomes wrong or misleading to the owner.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
Fairly confident. The test suite covers the main paths and several edge cases. If I had more time I would test what happens when an owner has zero time available, when a pet has no tasks at all, and when two recurring tasks with different recurrence types end up on the same date after several completions.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The conflict detection ended up working well for both single-pet and multi-pet scenarios using the same interval logic. Adding detect_owner_conflicts as a module-level function that just flattens all the schedulers kept it clean without having to change any of the existing classes.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add a way to remove tasks from the UI — right now you can only add them. I would also improve the scheduler to try harder to fit high-priority tasks, for example by swapping out a low-priority task if it would make room for a high-priority one that was skipped.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Starting with a UML diagram even if it changes later is worth it. It forces you to think about what each class is responsible for before writing any code. The AI was most useful when I already had a clear structure and used it to fill in details or catch things I missed, rather than asking it to design from scratch.
