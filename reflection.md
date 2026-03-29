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
My UML includes 4 classes: owner, pet,task, scheduler.
Owner has a pet, a name, preferences, and the available time. 
Pet has a name, species, breed, age, owner and tasks associated with it.
Scheduler has an owner, pet, tasks, reasoning, and functions such as add/edit/display plan
Task has a name, category, duration, priority, and whether it is completed or not.
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Slightly changed around how the classes interact with one another, now scheduler does not have a connection straight to the tasks but only has it through the owner or the pet
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
