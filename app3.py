from flask import Flask, redirect, render_template, url_for, jsonify, flash
import json
from flask import request

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Set the secret key for flash messages

path = "taches.json"
path_employes = "employes.json"

# Ecran 1: Taches en cours
@app.route("/current")
def todosIndex():
    todos = json.load(open(path))
    statut_non = "non assignee"
    statut_current = "en cours"
    todos_current = [todo for todo in todos if todo['statut'] == statut_current]
    todos_non_assigne = [todo for todo in todos if todo['statut'] == statut_non]
    confirm_delete = True
    return render_template('current.html', todos_current=todos_current, todos_non_assigne=todos_non_assigne,
                           confirm_delete=confirm_delete)

@app.route("/current/delete/<titre>", methods=['GET'])
def todosDelete(titre):
    todos = json.load(open(path))
    todos = [todo for todo in todos if todo['titre'] != titre]
    json.dump(todos, open(path, 'w'))
    return redirect('/current')

@app.route("/current/edit/<titre>",  methods=['GET'])
def todosEdit(titre):
    todos = json.load(open(path))
    todo = next((t for t in todos if t['titre'] == titre), None)
    return render_template('todosEdit.html', todo=todo)

@app.route("/current/edit/<titre>", methods=['POST'])
def todosEditPOST(titre):
    todos = json.load(open(path))
    todo = next((t for t in todos if t['titre'] == titre), None)
    if request.method == 'POST' and todo:
        todo['titre'] = request.form['titre']
        todo['description'] = request.form['description']
        todo['statut'] = request.form['statut']
        json.dump(todos, open(path, 'w'))
        return redirect('/current')
    return render_template('todosEdit.html', todo=todo)

# Ecran 2 : Toutes les taches
@app.route("/all")
def all():
    todos = json.load(open(path))
    confirm_delete = True
    return render_template('all.html', todos=todos, confirm_delete=confirm_delete)

@app.route("/export")
def export_json():
    todos = json.load(open(path))
    return jsonify(todos)

# Ecran 3 : Creation d'une tache
# Flask route for displaying the task creation form
@app.route("/create", methods=['GET'])
def createTaskForm():
    # Load employee list for dropdown
    employees = json.load(open(path_employes))
    return render_template('create.html', employees=employees)

# Flask route for handling the form submission
@app.route("/create", methods=['POST'])
def createTask():
    # Extract task details from the form data
    titre = request.form['titre']
    description = request.form['description']
    statut = request.form['statut']
    employe = request.form['employe']

    # Create a new task object
    new_task = {
        'titre': titre,
        'description': description,
        'statut': statut,
        'employe': employe
    }

    # Add the new task to the task list (JSON file)
    todos = json.load(open(path))
    todos.append(new_task)
    json.dump(todos, open(path, 'w'))

    # Render a confirmation message and clear the form fields
    confirmation_message = "Task '{}' created successfully.".format(titre)
    flash(confirmation_message, "success")
    return redirect('/create')

# Ecran 5 : Lister les employes
@app.route("/employees")
def listEmployees():
    employees = json.load(open(path_employes))  # Load employees from JSON file
    return render_template("employees.html", employees=employees)

# Flask route for exporting all employees as JSON
@app.route("/employees/export")
def exportEmployees():
    employees = json.load(open(path_employes))  # Load employees from JSON file
    return jsonify(employees)

# Ecran 6 : Creer un employee
@app.route("/creer_employe", methods=["GET", "POST"])
def creer_employe():
    if request.method == "POST":
        # Récupérer les données du formulaire
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        email = request.form["email"]
        icone = request.form["icone"]

        # Vérifier si l'email est unique
        employes = json.load(open(path_employes))
        if not a
