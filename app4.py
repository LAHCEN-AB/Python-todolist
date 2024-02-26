from flask import Flask, redirect, render_template, url_for, jsonify, flash
import json
from flask import request

app = Flask(__name__)

path = "taches.json"
path_employes = "employes.json"


@app.route("/")
def index():
    return render_template('index.html')


# Ecran 1: Taches en cours
@app.route("/current")
def todosIndex():
    todos = json.load(open(path))
    statut_non = "non assignee"
    statut_current = "en cours"
    todos_current = list(filter(lambda x: x['statut'] == statut_current, todos))
    todos_non_assigne = list(filter(lambda x: x['statut'] == statut_non, todos))
    confirm_delete = True
    delete_route = "/current/delete/"

    return render_template('current.html', todos_current=todos_current, todos_non_assigne=todos_non_assigne,
                           confirm_delete=confirm_delete, delete_route=delete_route)


@app.route("/current/delete/<titre>", methods=['GET'])
def todosDelete(titre):
    print(titre)
    todos = json.load(open(path))

    # on enleve l'element avec l'id id
    todos = list(filter(lambda x: x['titre'] != titre, todos))

    # on ecrase le fichier avec la liste filtree
    json.dump(todos, open(path, 'w'))

    return redirect('/current')


@app.route("/current/edit/<titre>", methods=['GET'])
def todosEdit(titre):
    todos = json.load(open(path))
 # Load employees data
    employees = json.load(open(path_employes))
   
    filtered_todos = list(filter(lambda x: x['titre'] == titre, todos))
    if filtered_todos:
        todo = filtered_todos[0]
        return render_template('todosEdit.html', todo=todo, employees=employees)
    else:
        # Handle the case where no matching todo is found
        flash("Task with title '{}' not found.".format(titre), "error")
        return redirect('/current')  # Redirect to the current page or another relevant page
    
@app.route("/current/edit/<titre>", methods=['POST'])
def todosEditPOST(titre):
    # Load todos and employees from JSON files
    todos = json.load(open(path))
    employees = json.load(open(path_employes))
    tasks_in_progress_count = 0
    # Get the selected todo by its title
    todo = next((task for task in todos if task['titre'] == titre), None)
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the selected employee's email from the form
        employe_email = request.form['employe']
        
        # Find the selected employee in the employees list
        selected_employee = next((employee for employee in employees if employee['email'] == employe_email), None)
        
        # Check if the selected employee exists
        if not selected_employee:
            flash("Selected employee not found.", "error")
            return redirect('/current')
    # Count the number of tasks in progress for the selected employee    
    for task in todos:
        if task.get('employe') and task['employe'].get('email'):
            if task['employe']['email'] == employe_email and task['statut'] == 'en cours':
                tasks_in_progress_count += 1
    # Limit the number of tasks in progress to 3 for each employee           
     # Check if the employee has exceeded the task limit
        if has_exceeded_task_limit(employe_email):
            flash("Employee '{}' already has 3 tasks in progress. Cannot assign more tasks.".format(selected_employee['nom']), "error")
            return redirect('/current')
        
        # Update the task if it exists
        if todo:
            todo['titre'] = request.form['titre']
            todo['description'] = request.form['description']
            todo['statut'] = request.form['statut']
            todo['employe'] = selected_employee  # Update the task's employee details
            json.dump(todos, open(path, 'w'), indent=4)  # Ensure proper indentation
            flash("Task '{}' updated successfully.".format(todo['titre']), "success")  # Flash the success message
            return redirect('/current')
    
    # If it's not a POST request or if there's an issue, render the edit template again with the todo data
    return render_template('todosEdit.html', todo=todo, employees=employees)

# Ecran 2 : Toutes les taches
@app.route("/all")
def all():
    todos = json.load(open(path))
    confirm_delete = True
    delete_route = "/all/delete/"
    return render_template('all.html', todos=todos, confirm_delete=confirm_delete, delete_route=delete_route)

@app.route("/all/delete/<titre>", methods=['GET'])
def todosDeleteall(titre):
    print(titre)
    todos = json.load(open(path))

    # on enleve l'element avec l'id id
    todos = list(filter(lambda x: x['titre'] != titre, todos))

    # on ecrase le fichier avec la liste filtree
    json.dump(todos, open(path, 'w'))

    return redirect('/all')

# Ecran 3 : Creation d'une tache
#Check if an employee has exceeded the limit of 3 tasks in progress
def has_exceeded_task_limit(employe_email):
    # Load existing tasks from JSON file
    tasks = json.load(open("taches.json"))

    # Count the number of tasks in progress for the selected employee
    tasks_in_progress_count = sum(1 for task in tasks if task.get('employe') and task['employe'].get('email') == employe_email and task['statut'] == 'en cours')

    return tasks_in_progress_count >= 3

# Flask route for displaying the task creation form
@app.route("/create", methods=['GET'])
def createTaskForm():
    employees = json.load(open("employes.json"))
    return render_template('create.html', employees=employees)

@app.route("/create", methods=['POST'])
def createTask():
    # Extract task details from the form data
    titre = request.form['titre']
    description = request.form['description']
    statut = request.form['statut']
    employe_email = request.form['employe']  # Get the selected employee's email from the form
    
    # Load employees from JSON file
    employees = json.load(open("employes.json"))

    # Find the selected employee in the employees list
    selected_employee = None
    for employee in employees:
        if employee['email'] == employe_email:
            selected_employee = employee
            break
 # Check if the employee has exceeded the task limit
    if has_exceeded_task_limit(employe_email):
        error_message = "Employee '{}' already has 3 tasks in progress. Cannot assign more tasks.".format(selected_employee['nom'])
        flash(error_message, "error")
        return render_template('create.html', employees=employees, confirmation_message=error_message)

    # Create a new task object
    new_task = {
        'titre': titre,
        'description': description,
        'statut': statut,
        'employe': selected_employee  # Assign the selected employee details to the 'employe' key
    }

    # Load existing tasks from JSON file
    tasks = json.load(open("taches.json"))
    
    # Add the new task to the task list
    tasks.append(new_task)

    # Write the updated task list back to the JSON file
    with open('taches.json', 'w') as f:
        json.dump(tasks, f, indent=4)

    # Render a confirmation message
    confirmation_message = "Task '{}' created successfully.".format(titre)
    return render_template('create.html', confirmation_message=confirmation_message, employees=employees)

# Ecran 5 : Lister les employes
@app.route("/employees")
def listEmployees():
    employes = json.load(open(path_employes))  # Load employees from JSON file
    confirm_delete = True
    delete_route = "/employees/delete/"
    
    # Load tasks from the tasks JSON file
    tasks = json.load(open(path))
    
    employees_with_stats = []
    for employee in employes:
        email = employee['email']
        
        # Initialize total tasks and tasks in progress for each employee
        total_tasks = 0
        tasks_in_progress = 0
        
        # Calculate the number of total tasks and tasks in progress for the employee
        for task in tasks:
            if isinstance(task['employe'], dict) and task['employe']['email'] == email:
                total_tasks += 1
                if task['statut'] == 'en cours':
                    tasks_in_progress += 1
        
        # Add the calculated statistics to the employee dictionary
        employee['total_tasks'] = total_tasks
        employee['tasks_in_progress'] = tasks_in_progress
        employees_with_stats.append(employee)
        
    return render_template("employees.html", employes=employees_with_stats, confirm_delete=confirm_delete, delete_route=delete_route)

# Flask route for exporting all employees as JSON
@app.route("/employees/export")
def exportEmployees():
    employees = json.load(open(path_employes))  # Load employees from JSON file
    return jsonify(employees)

def calculer_statistiques_employe(email):
    todos = json.load(open(path))
    nombre_taches_en_cours = 0
    nombre_taches_total = 0
    for todo in todos:
        if todo['employe'] and todo['employe']['email'] == email:
            if todo['statut'] == 'en cours':
                nombre_taches_en_cours += 1
            nombre_taches_total += 1
    return nombre_taches_en_cours, nombre_taches_total

# Ecran 6 : Cree un employee
# Route pour afficher le formulaire de création d'un employé
@app.route("/creer_employe", methods=["GET"])
def creer_employe_form():
    employes = json.load(open(path_employes))
    return render_template("creer_employe.html")


# Vérifier si l'email de l'employé est unique
def is_email_unique(email):
    employes = json.load(open(path_employes))
    for employe in employes:
        if employe["email"] == email:
            return False
    return True

app.secret_key = "super_secret_key"  # Clé secrète pour les messages flash
# Route pour traiter la création d'un employé
@app.route("/creer_employe", methods=["POST"])
def creer_employe():
    # Ajouter l'employé à la liste des employés
    
    if request.method == "POST":
        employes = json.load(open(path_employes))
        # Récupérer les données du formulaire
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        email = request.form["email"]
        icone = request.form["icone"]

        # Vérifier si l'email est unique
        if not is_email_unique(email):
            flash("L'email doit être unique.", "error")
            return redirect("/creer_employe")
        else:
            # Créer un nouvel employé
            nouvel_employe = {
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "icone": icone
            }
            employes.append(nouvel_employe)
            json.dump(employes, open(path_employes, "w"))
            # Rediriger vers la liste des employés avec un message de confirmation
            flash("L'employé a été créé avec succès.", "success")
            return redirect("/employees")
    # return render_template("employees.html", employes=employes)
    return render_template("creer_employe.html")

# Ecran 7 : Editer un employe

@app.route("/edit_employee/<email>", methods=["GET", "POST"])
def edit_employee(email):
    # Recherche de l'employé à éditer par son email
    employes = json.load(open(path_employes))
    employee_to_edit = None
    for employee in employes:
        if employee["email"] == email:
            employee_to_edit = employee
            break

    if request.method == "POST":
        # Mise à jour des informations de l'employé avec les données du formulaire
        employee_to_edit["prenom"] = request.form["prenom"]
        employee_to_edit["nom"] = request.form["nom"]
        employee_to_edit["email"] = request.form["email"]
        employee_to_edit["icone"] = request.form["icone"]

        # Sauvegarde des modifications dans le fichier JSON
        with open(path_employes, "w") as f:
            json.dump(employes, f, indent=4)

        # Redirection vers l'écran de listing des employés avec un message de confirmation
        # return redirect("/list_employees?message=employees+updated+successfully")
        flash("Employee '{}' updated successfully.".format(email), "success")
        return redirect("/employees")  # Redirection vers l'écran de listing des employés
    # return render_template("employees.html", employes=employes)
    # Affichage du formulaire d'édition avec les données de l'employé
    return render_template("edit_employee.html", employee=employee_to_edit)

@app.route('/employees/delete/<email>', methods=['GET'])
def delete_employee(email):
    todos = json.load(open(path))
    employe_tasks = [task for task in todos if task.get('employe') and task['employe'].get('email') == email]
    # Check if there are tasks assigned to the employee
    if employe_tasks:
        todo_tasks = [task for task in employe_tasks if task['statut'] == 'en cours']
        if todo_tasks:
            flash("Cannot delete employee '{}' because they have tasks in progress.".format(email), "error")
            return redirect("/employees")
        # If there are 'todo' tasks, unassign them
        if todo_tasks:
            for task in todo_tasks:
                task['employe'] = None
            json.dump(todos, open(path, 'w'), indent=4)
    # Remove the employee from the list of employees
    employes = json.load(open(path_employes))
    employes = [employee for employee in employes if employee["email"] != email]
    json.dump(employes, open(path_employes, 'w'))
    
    flash("Employee '{}' deleted successfully.".format(email), "success")
    return redirect("/employees")

app.run(port=8080)