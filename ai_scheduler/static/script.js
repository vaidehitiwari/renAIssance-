window.onload = function() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(tasks => {
            const taskContainer = document.getElementById('taskCheckboxes');
            tasks.forEach(task => {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = task.id;
                checkbox.id = `task_${task.id}`;  // Correctly formatted ID
                const label = document.createElement('label');
                label.htmlFor = `task_${task.id}`;  // Correctly formatted HTMLFor
                label.innerText = `${task.name} (Priority: ${task.priority}, Duration: ${task.duration} hours)`;
                const div = document.createElement('div');
                div.appendChild(checkbox);
                div.appendChild(label);
                taskContainer.appendChild(div);
            });
        })
        .catch(error => console.error('Error fetching tasks:', error));
};

// Generate the schedule based on selected tasks
function generateSchedule() {
    const selectedTasks = [];
    const checkboxes = document.querySelectorAll('#taskCheckboxes input:checked');
    checkboxes.forEach(checkbox => selectedTasks.push(parseInt(checkbox.value)));

    if (selectedTasks.length === 0) {
        alert("Please select at least one task.");
        return;
    }

    // Send the selected tasks to the backend for scheduling
    fetch('/generate-schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tasks: selectedTasks })
    })
    .then(response => response.json())
    .then(data => {
        const outputDiv = document.getElementById('output');
        outputDiv.innerHTML = ''; // Clear previous results
        if (data.error) {
            outputDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } else {
            // Generate table from the result
            const table = document.createElement('table');
            const headerRow = document.createElement('tr');
            headerRow.innerHTML = '<th>Task</th><th>Employee</th><th>Priority</th><th>Duration</th><th>Available Hours Left</th>';
            table.appendChild(headerRow);

            data.forEach(entry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${entry.task_name}</td>
                    <td>${entry.employee}</td>
                    <td>${entry.priority}</td>
                    <td>${entry.duration}</td>
                    <td>${entry.employee_available_hours}</td>
                `;
                table.appendChild(row);
            });

            outputDiv.appendChild(table);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
