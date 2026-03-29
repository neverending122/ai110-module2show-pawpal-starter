import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, detect_owner_conflicts

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care planner that schedules tasks by priority and flags conflicts.")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []
if "schedulers" not in st.session_state:
    st.session_state.schedulers = {}

PRIORITY_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
CATEGORY_ICON  = {"walk": "🦮", "feeding": "🍖", "meds": "💊", "grooming": "✂️", "enrichment": "🧸"}

# ---------------------------------------------------------------------------
# SECTION 1 — Owner Info
# ---------------------------------------------------------------------------
st.subheader("1. Owner Info")

col1, col2 = st.columns(2)
with col1:
    owner_name    = st.text_input("Owner name", value="Jordan")
    time_available = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)
with col2:
    preferences = st.text_input("Preferences (comma-separated)", value="morning walks, no late feeding")

if st.button("Save owner", type="primary"):
    st.session_state.owner = Owner(
        name=owner_name,
        time_available=int(time_available),
        preferences=[p.strip() for p in preferences.split(",") if p.strip()],
        pets=st.session_state.pets,
    )
    st.session_state.schedulers = {}
    st.success(f"Owner **{owner_name}** saved with **{time_available} min** available today.")

st.divider()

# ---------------------------------------------------------------------------
# SECTION 2 — Pets
# ---------------------------------------------------------------------------
st.subheader("2. Pets")

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
    species  = st.selectbox("Species", ["dog", "cat", "other"])
with col2:
    breed = st.text_input("Breed", value="")
    age   = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet", type="primary"):
    if st.session_state.owner is None:
        st.warning("Save owner info before adding pets.")
    elif any(p.name == pet_name for p in st.session_state.pets):
        st.warning(f"A pet named **{pet_name}** already exists.")
    else:
        st.session_state.pets.append(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
        st.session_state.schedulers = {}
        st.success(f"Added **{pet_name}** ({species}).")

if st.session_state.pets:
    st.dataframe(
        [
            {
                "Name":    p.name,
                "Species": p.species.capitalize(),
                "Breed":   p.breed or "—",
                "Age":     f"{p.age} yr",
                "Tasks":   len(p.get_tasks()),
            }
            for p in st.session_state.pets
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 3 — Tasks
# ---------------------------------------------------------------------------
st.subheader("3. Add Tasks")

if not st.session_state.pets:
    st.info("Add at least one pet above before adding tasks.")
else:
    selected_pet_name = st.selectbox("Assign to pet", [p.name for p in st.session_state.pets])

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category   = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
    with col2:
        duration  = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority  = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col3:
        task_time  = st.text_input("Time (HH:MM)", value="08:00")
        task_date  = st.text_input("Date (YYYY-MM-DD, optional)", value="")
        recurrence = st.selectbox("Recurrence", ["", "daily", "weekly"])

    if st.button("Add task", type="primary"):
        target_pet = next(p for p in st.session_state.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(
            name=task_title, category=category, duration=int(duration),
            priority=priority, time=task_time, date=task_date, recurrence=recurrence,
        ))
        st.session_state.schedulers = {}
        st.success(f"Task **{task_title}** added to **{selected_pet_name}**.")

    for pet in st.session_state.pets:
        if pet.get_tasks():
            with st.expander(f"{pet.name}'s tasks — {len(pet.get_tasks())} added"):
                st.dataframe(
                    [
                        {
                            "Time":       t.time,
                            "Task":       t.name,
                            "Category":   f"{CATEGORY_ICON.get(t.category, '📋')} {t.category}",
                            "Duration":   f"{t.duration} min",
                            "Priority":   f"{PRIORITY_COLOR.get(t.priority, '⚪')} {t.priority}",
                            "Date":       t.date or "—",
                            "Recurrence": t.recurrence or "one-off",
                        }
                        for t in sorted(pet.get_tasks(), key=lambda t: t.time)
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

st.divider()

# ---------------------------------------------------------------------------
# SECTION 4 — Schedule
# ---------------------------------------------------------------------------
st.subheader("4. Build Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.owner:
        st.warning("Save owner info first.")
    elif not st.session_state.pets:
        st.warning("Add at least one pet first.")
    else:
        schedulers = {}
        for pet in st.session_state.pets:
            s = Scheduler(owner=st.session_state.owner, pet=pet)
            s.generate_plan()
            schedulers[pet.name] = s
        st.session_state.schedulers = schedulers

if st.session_state.schedulers:
    schedulers = st.session_state.schedulers
    owner      = st.session_state.owner

    # --- Cross-pet conflicts ---
    if len(schedulers) > 1:
        cross_conflicts = detect_owner_conflicts(list(schedulers.values()))
        if cross_conflicts:
            st.warning(f"**Cross-pet conflicts detected** — {owner.name} is double-booked:")
            for c in cross_conflicts:
                st.write(f"- {c}")
        else:
            st.success("No cross-pet scheduling conflicts.")

    # --- Per-pet schedule ---
    for pet_name, scheduler in schedulers.items():
        st.markdown(f"### {pet_name}'s Schedule")

        # Budget metrics
        total_scheduled = sum(t.duration for t in scheduler.scheduled_tasks)
        budget          = owner.get_available_time()
        m1, m2, m3 = st.columns(3)
        m1.metric("Time budget",     f"{budget} min")
        m2.metric("Time scheduled",  f"{total_scheduled} min",
                  delta=f"{budget - total_scheduled} min remaining",
                  delta_color="normal")
        m3.metric("Tasks scheduled", len(scheduler.scheduled_tasks))

        if scheduler.is_over_budget():
            st.error("This pet's schedule exceeds the owner's available time.")

        # Per-pet time conflicts
        if scheduler.conflicts:
            st.warning(f"**{len(scheduler.conflicts)} time conflict(s)** for {pet_name}:")
            for c in scheduler.conflicts:
                st.write(f"- {c}")
        else:
            st.success(f"No time conflicts for {pet_name}.")

        # Reasoning
        with st.expander("See scheduling reasoning"):
            st.text(scheduler.explain_plan())

        # Filter
        status_filter = st.radio(
            "Show tasks", ["All", "Pending", "Completed"],
            horizontal=True, key=f"filter_{pet_name}"
        )

        if status_filter == "Pending":
            display_tasks = scheduler.filter_by_status(completed=False, pet_name=pet_name)
        elif status_filter == "Completed":
            display_tasks = scheduler.filter_by_status(completed=True, pet_name=pet_name)
        else:
            display_tasks = scheduler.scheduled_tasks

        if not display_tasks:
            st.info(f"No {status_filter.lower()} tasks for {pet_name}.")
        else:
            for task in display_tasks:
                icon       = CATEGORY_ICON.get(task.category, "📋")
                priority_dot = PRIORITY_COLOR.get(task.priority, "⚪")
                recurrence_label = f" · {task.recurrence}" if task.recurrence else ""

                col1, col2 = st.columns([5, 1])
                with col1:
                    if task.is_completed:
                        st.success(
                            f"{icon} **{task.time}** — ~~{task.name}~~ "
                            f"({task.duration} min) {priority_dot} *completed*{recurrence_label}"
                        )
                    else:
                        st.info(
                            f"{icon} **{task.time}** — {task.name} "
                            f"({task.duration} min) {priority_dot} {task.priority}{recurrence_label}"
                        )
                with col2:
                    if not task.is_completed:
                        if st.button("✓ Done", key=f"complete_{pet_name}_{task.name}_{task.time}"):
                            next_task = scheduler.complete_task(task)
                            if next_task:
                                st.success(f"Done! Next **{task.name}** scheduled for **{next_task.date}**.")
                            else:
                                st.success(f"**{task.name}** marked complete.")
                            st.rerun()
