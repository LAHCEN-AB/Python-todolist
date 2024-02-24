from flask import Flask, redirect, render_template, url_for, flash, request, jsonify
import json

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Secret key for flash messages

# Paths to JSON files
path = "taches.json"
path_employes = "employes.json"

# Route for the homepage
@app.route("/")
def index():
    return render_template('index.html')

# Route for listing tasks in progress
@app.route("/current")
def todosIndex():
    todos = json.load(open(path))
    statut_current = "en cours"
    todos_current = [task for task in todos if task['statut'] == statut_current]
    todos_non_assigne = [task for task in todos if task['statut'] == "non assignee"]
    confirm_delete = True
    delete_route = "/current/delete/"
    return render_template('current.html', todos_current=todos_current, todos_non_assigne=todos_non_assigne,confirm_delete=confirm_delete, delete_route=delete_route)

# Route for deleting a task
@app.route("/current/delete/<titre>", methods=['GET'])
def todosDelete(titre):
    todos = json.load(open(path))
    todos = [task for task in todos if task['titre'] != titre]
    json.dump(todos, open(path, 'w'))
    return redirect('/current')

# Route for editing a task (GET request)
@app.route("/current/edit/<titre>", methods=['GET'])
def todosEdit(titre):
    todos = json.load(open(path))
    employees = json.load(open(path_employes))
    todo = next((task for task in todos if task['titre'] == titre), None)
    if todo:
        return render_template('todosEdit.html', todo=todo, employees=employees)
    else:
        flash("Task with title '{}' not found.".format(titre), "error")
        return redirect('/current')

# Route for editing a task (POST request)
@app.route("/current/edit/<titre>", methods=['POST'])
def todosEditPOST(titre):
    todos = json.load(open(path))
    employees = json.load(open(path_employes))
    todo = next((task for task in todos if task['titre'] == titre), None)
    if request.method == 'POST' and todo:
        employe_email = request.form['employe']
        selected_employee = next((employee for employee in employees if employee['email'] == employe_email), None)
        if not selected_employee:
            flash("Selected employee not found.", "error")
            return redirect('/current')
        tasks_in_progress_count = sum(1 for task in todos if task.get('employe') and task['employe'].get('email') == employe_email and task['statut'] == 'en cours')
        if tasks_in_progress_count >= 3:
            flash("Employee '{}' already has 3 tasks in progress. Cannot assign more tasks.".format(selected_employee['nom']), "error")
            return redirect('/current')
        todo.update({
            'titre': request.form['titre'],
            'description': request.form['description'],
            'statut': request.form['statut'],
            'employe': selected_employee
        })
        json.dump(todos, open(path, 'w'), indent=4)
        flash("Task '{}' updated successfully.".format(todo['titre']), "success")
        return redirect('/current')
    return render_template('todosEdit.html', todo=todo, employees=employees)

# Route for listing all tasks
@app.route("/all")
def all():
    todos = json.load(open(path))
    confirm_delete = True
    delete_route = "/all/delete/"
    return render_template('all.html', todos=todos, confirm_delete=confirm_delete, delete_route=delete_route)

# Route for deleting a task from all tasks
@app.route("/all/delete/<titre>", methods=['GET'])
def todosDeleteall(titre):
    todos = json.load(open(path))
    todos = [task for task in todos if task['titre'] != titre]
    json.dump(todos, open(path, 'w'))
    return redirect('/all')

# Route for displaying the task creation form
@app.route("/create", methods=['GET'])
def createTaskForm():
    employees = json.load(open(path_employes))
    return render_template('create.html', employees=employees)

# Route for creating a task
@app.route("/create", methods=['POST'])
def createTask():
    titre = request.form['titre']
    description = request.form['description']
    statut = request.form['statut']
    employe_email = request.form['employe']
    employees = json.load(open(path_employes))
    selected_employee = next((employee for employee in employees if employee['email'] == employe_email), None)
    if not selected_employee:
        flash("Selected employee not found.", "error")
        return redirect('/create')
    new_task = {
        'titre': titre,
        'description': description,
        'statut': statut,
        'employe': selected_employee
    }
    tasks = json.load(open(path))
    tasks.append(new_task)
    json.dump(tasks, open(path, 'w'), indent=4)
    flash("Task '{}' created successfully.".format(titre), "success")
    return redirect('/create')

# Route for listing all employees
@app.route("/employees")
def listEmployees():
    employes = json.load(open(path_employes))
    confirm_delete = True
    delete_route = "/employees/delete/"
    tasks = json.load(open(path))
    employees_with_stats = []
    for employee in employes:
        email = employee['email']
        total_tasks = sum(1 for task in tasks if task.get('employe') and task['employe']['email'] == email)
        tasks_in_progress = sum(1 for task in tasks if task.get('employe') and task['employe']['email'] == email and task['statut'] == 'en cours')
        employee['total_tasks'] = total_tasks
        employee['tasks_in_progress'] = tasks_in_progress
        employees_with_stats.append(employee)
    return render_template("employees.html", employes=employees_with_stats, confirm_delete=confirm_delete, delete_route=delete_route)

# Route for exporting all employees as JSON
@app.route("/employees/export")
def exportEmployees():
    employees = json.load(open(path_employes))
    return jsonify(employees)

# Route for deleting an employee
@app.route("/employees/delete/<email>")
def deleteEmployee(email):
    todos = json.load(open(path))
    employe_tasks = [task for task in todos if task['employe']['email'] == email]
    if employe_tasks:
        todo_tasks = [task for task in employe_tasks if task['statut'] == 'todo']
        if todo_tasks:
            for task in todo_tasks:
                task['employe'] = None
            json.dump(todos, open(path, 'w'), indent=4)
    employes = json.load(open(path_employes))
    employes = [employee for employee in employes if employee['email'] != email]
    json.dump(employes, open(path_employes, 'w'))
    return redirect("/employees")

# Run the Flask application
if __name__ == "__main__":
    app.run(port=8080)
