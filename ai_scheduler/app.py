from flask import Flask, request, render_template, jsonify
import json
import os

app = Flask(__name__)

# Path to the data folder
DATA_FOLDER = os.path.join(os.getcwd(), 'data')

# Route to serve the main HTML page
@app.route('/')
def welcome():
    return render_template('welcom.html')  # Serve welcom.html by default

@app.route('/index')
def index():
    return render_template('index.html')  # This will serve the index.html page

# Route to serve the About Us page
@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')  # Serve the aboutus.html page

# Route to serve the Contact Us page
@app.route('/contact')
def contact_us():
    return render_template('contact.html')  # Serve the contact.html page

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

# Route to serve the tasks data to the frontend (for checkboxes)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        with open(os.path.join(DATA_FOLDER, 'tasks.json'), 'r') as tasks_file:
            tasks_data = json.load(tasks_file)
        return jsonify(tasks_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to serve the employees data to the frontend (for radio buttons, not used now)
@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        with open(os.path.join(DATA_FOLDER, 'employees.json'), 'r') as employees_file:
            employees_data = json.load(employees_file)
        return jsonify(employees_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to generate the schedule based on selected tasks
@app.route('/generate-schedule', methods=['POST'])
def schedule():
    data = request.json
    selected_task_ids = data.get('tasks')  # List of selected task IDs

    # Validate if tasks are selected
    if not selected_task_ids:
        return jsonify({"error": "No tasks selected."}), 400

    try:
        # Load tasks and employees data
        with open(os.path.join(DATA_FOLDER, 'tasks.json'), 'r') as tasks_file:
            tasks_data = json.load(tasks_file)

        with open(os.path.join(DATA_FOLDER, 'employees.json'), 'r') as employees_file:
            employees_data = json.load(employees_file)

        # Filter tasks based on selected IDs
        selected_tasks = [task for task in tasks_data if task['id'] in selected_task_ids]

        # Initialize schedule list
        schedule = []

        for task in selected_tasks:
            assigned = False
            # Try assigning to each employee
            for employee in employees_data:
                # Check if employee has enough hours and has available time for the task
                if employee['available_hours'] >= task['duration']:
                    # Assign the task to the employee
                    schedule.append({
                        'task_name': task['name'],
                        'priority': task['priority'],
                        'duration': task['duration'],
                        'preferred_time': task['preferred_time'],
                        'employee': employee['name'],
                        'employee_available_hours': employee['available_hours'] - task['duration'],  # Remaining hours
                    })

                    # Decrease employee's available hours by the task's duration
                    employee['available_hours'] -= task['duration']
                    assigned = True
                    break  # Exit after assigning the task to the first eligible employee

            # If no employee could be assigned, raise an error
            if not assigned:
                return jsonify({"error": f"Could not assign task '{task['name']}' due to insufficient employee hours."}), 400

        # Return the generated schedule
        return jsonify(schedule)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)
