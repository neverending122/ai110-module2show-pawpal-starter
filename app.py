import streamlit as st
from pawpal_system import Task,Pet,Owner,Scheduler
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    pet = Pet(name=pet_name, species=species, breed="", age=0)
    owner = Owner(name=owner_name, time_available=int(time_available), pets=[pet])
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Created owner {owner_name} with pet {pet_name}.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    task_time = st.text_input("Time (HH:MM)", value="08:00")

if st.button("Add task"):
    task = Task(name=task_title, category="general", duration=int(duration), priority=priority, time=task_time)
    if st.session_state.pet:
        st.session_state.pet.add_task(task)
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority, "time": task_time}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if st.session_state.owner and st.session_state.pet:
        scheduler = Scheduler(owner=st.session_state.owner, pet=st.session_state.pet)
        scheduler.generate_plan()
        st.subheader("Schedule")
        for task in scheduler.scheduled_tasks:
            st.write(f"- {task.name} ({task.duration} min) [{task.priority}]")
        st.text(scheduler.explain_plan())
    else:
        st.warning("Add a pet first before generating a schedule.")
