from flask import Flask, redirect, render_template,url_for, jsonify, flash
import json
from flask import request
app = Flask(__name__)

path="taches.json"
path_employes = "employes.json"
@app.route("/")
def index():
    return render_template('index.html')

# Ecran 1: Taches en cours
@app.route("/current")
def todosIndex():
    todos = json.load(open(path))
    statut_non="non assignee"
    statut_current="en cours"
    todos_current = list(filter(lambda x: x['statut'] == statut_current, todos))
    todos_non_assigne = list(filter(lambda x: x['statut'] == statut_non, todos))
    confirm_delete = True
    delete_route = "/current/delete/"
    
    return render_template('current.html', todos_current=todos_current,todos_non_assigne=todos_non_assigne,confirm_delete=confirm_delete,delete_route=delete_route)

@app.route("/current/delete/<titre>", methods=['GET'])
def todosDelete(titre):
    print(titre)
    todos = json.load(open(path))
    
    # on enleve l'element avec l'id id
    todos = list(filter(lambda x: x['titre'] != titre, todos))

    # on ecrase le fichier avec la liste filtree
    json.dump(todos, open(path, 'w'))

    return redirect('/current')

@app.route("/current/edit/<titre>",  methods=['GET'])
def todosEdit(titre):
    todos = json.load(open(path))
    
    # recupere le todo avec le titre
    todo = list(filter(lambda x: x['titre'] == titre, todos))[0]
    return render_template('todosEdit.html', todo = todo)
    
    
@app.route("/current/edit/<titre>", methods=['POST'])
def todosEditPOST(titre):
    todos = json.load(open(path))
    todo = list(filter(lambda x: x['titre'] == titre, todos))[0]
    if request.method == 'POST':
        if todo:
            todo['titre'] = request.form['titre']
            todo['description'] = request.form['description']
            todo['statut'] = request.form['statut']
            json.dump(todos, open(path, 'w'))
        return redirect('/current')
    # If it's not a POST request, simply render the edit template again
    return render_template('todosEdit.html', todo=todo)

# Ecran 2 : Toutes les taches

@app.route("/all")
def all():
    todos = json.load(open(path))
    confirm_delete = True
    delete_route = "/current/delete/"
    return render_template('all.html', todos=todos,confirm_delete=confirm_delete,delete_route=delete_route)

@app.route("/export")
def export_json():
    todos =json.load(open(path))
    return jsonify(todos)

# Ecran 3 : Creation d'une tache
# Flask route for displaying the task creation form
@app.route("/create", methods=['GET'])
def createTaskForm():
    return render_template('create.html')

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
    return render_template('create.html', confirmation_message=confirmation_message)

# Ecran 5 : Lister les employes 
@app.route("/employees")
def listEmployees():
    employes = json.load(open(path_employes))  # Load employees from JSON file
    confirm_delete = True
    return render_template("employees.html", employes=employes,confirm_delete=confirm_delete)

# Flask route for exporting all employees as JSON
@app.route("/employees/export")
def exportEmployees():
    employees = json.load(open(path_employes ))  # Load employees from JSON file
    return jsonify(employees)
# Ecran 6 : Cree un employee
# Flask route for listing employees

#  Route pour afficher le formulaire de création d'un employé
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
# Route pour traiter la création d'un employé
@app.route("/creer_employe", methods=["POST"])
def creer_employe():
    # Ajouter l'employé à la liste des employés
    employes = json.load(open(path_employes))
    if request.method == "POST":
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
            "prenom": prenom,
            "nom": nom,
            "email": email,
            "icone": icone
        }
            employes.append(nouvel_employe)
            json.dump(employes, open(path_employes, "w"))
            # Rediriger vers la liste des employés avec un message de confirmation
            flash("L'employé a été créé avec succès.", "success")
            return redirect("/employees")
    return render_template("employees.html", employes=employes)

app.secret_key = "super_secret_key"  # Clé secrète pour les messages flash

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
        return redirect("/employees")
    # return render_template("employees.html", employes=employes)

    # Affichage du formulaire d'édition avec les données de l'employé
    return render_template("edit_employee.html", employee=employee_to_edit)

# Define the delete_employee endpoint
@app.route('/delete_employee/<email>', methods=['GET'])
def delete_employee(email):
    # Logic to delete the employee with the given email
    # This can include deleting associated tasks, etc.
    return "Employee with email {} has been deleted.".format(email)
app.run(port=8080)