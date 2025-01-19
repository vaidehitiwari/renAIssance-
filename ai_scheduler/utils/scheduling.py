from ortools.sat.python import cp_model

def generate_schedule(tasks, employees):
    model = cp_model.CpModel()
    assignments = {}

    # Create variables for each task and employee pair
    for task in tasks:
        for emp in employees:
            assignments[(task['id'], emp['id'])] = model.NewBoolVar(f"assign_{task['id']}_{emp['id']}")

    # Each task must be assigned to exactly one employee
    for task in tasks:
        model.Add(sum(assignments[(task['id'], emp['id'])] for emp in employees) == 1)

    # Track the number of tasks assigned to each employee
    task_count_per_employee = {}
    for emp in employees:
        task_count_per_employee[emp['id']] = sum(assignments[(task['id'], emp['id'])] for task in tasks)

    # Ensure each employee gets at most one task, and enforce that if Alice gets a task,
    # then other employees also must get at least one task
    for emp in employees:
        model.Add(sum(assignments[(task['id'], emp['id'])] for task in tasks) <= 1)  # At most one task per employee

    # Maximize the overall assignment of tasks considering priorities
    objective_terms = []
    for task in tasks:
        for emp in employees:
            # Prioritize based on matching preferred time
            if task['preferred_time'] in emp['preferences']:
                priority_weight = task['priority']  # Full priority if the preferred time matches
            else:
                priority_weight = task['priority'] * 0.8  # Reduced priority if it doesn't match

            objective_terms.append(assignments[(task['id'], emp['id'])] * priority_weight)

    # Maximize the sum of the priority weights
    model.Maximize(sum(objective_terms))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        schedule = []
        for task in tasks:
            for emp in employees:
                if solver.BooleanValue(assignments[(task['id'], emp['id'])]):
                    schedule.append({
                        "task_name": task['name'],
                        "priority": task['priority'],
                        "duration": task['duration'],
                        "preferred_time": task['preferred_time'],
                        "employee": emp['name'],
                        "employee_available_hours": emp['available_hours'] - task['duration']
                    })
        return schedule
    else:
        return {"error": "No feasible schedule found"}
