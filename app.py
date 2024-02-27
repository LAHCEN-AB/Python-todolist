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
        # Gérer le cas où aucune tâche correspondante n'est trouvée.
        flash("Task with title '{}' not found.".format(titre), "error")
        return redirect('/current')  # Rediriger vers la page actuelle ou une autre page pertinente
    
@app.route("/current/edit/<titre>", methods=['POST'])
def todosEditPOST(titre):
    # Charger les tâches et les employés à partir de fichiers JSON
    todos = json.load(open(path))
    employees = json.load(open(path_employes))
    tasks_in_progress_count = 0
    # Obtenir la tâche sélectionnée par son titre
    todo = next((task for task in todos if task['titre'] == titre), None)
    
    # Vérifier si la méthode de la requête est POST
    if request.method == 'POST':
        # Obtenir l'email de l'employé sélectionné à partir du formulaire
        employe_email = request.form['employe']
        
        # Trouver l'employé sélectionné dans la liste des employés
        selected_employee = next((employee for employee in employees if employee['email'] == employe_email), None)
        
        # Vérifier si l'employé sélectionné existe
        if not selected_employee:
            flash("Selected employee not found.", "error")
            return redirect('/current')
    # Compter le nombre de tâches en cours pour l'employé sélectionné   
    for task in todos:
        if task.get('employe') and task['employe'].get('email'):
            if task['employe']['email'] == employe_email and task['statut'] == 'en cours':
                tasks_in_progress_count += 1
    # Limit the number of tasks in progress to 3 for each employee           
     # Vérifier si l'employé a dépassé la limite de tâches
        if has_exceeded_task_limit(employe_email):
            flash("Employee '{}' already has 3 tasks in progress. Cannot assign more tasks.".format(selected_employee['nom']), "error")
            return redirect('/current')
        
        # Mettre à jour la tâche si elle existe
        if todo:
            todo['titre'] = request.form['titre']
            todo['description'] = request.form['description']
            todo['statut'] = request.form['statut']
            todo['employe'] = selected_employee  # Mettre à jour les détails de l'employé assigné à la tâche
            json.dump(todos, open(path, 'w'), indent=4)  
            flash("Task '{}' updated successfully.".format(todo['titre']), "success")  # Afficher le message de réussite (flash message).
            return redirect('/current')
    
    # Si ce n'est pas une requête POST ou s'il y a un problème
    # affichez à nouveau le modèle d'édition avec les données de la tâche
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
#Vérifier si un employé a dépassé la limite de 3 tâches en cours
def has_exceeded_task_limit(employe_email):
    # Charger les tâches existantes à partir du fichier JSON
    tasks = json.load(open("taches.json"))

    # Compter le nombre de tâches en cours pour l'employé sélectionné
    tasks_in_progress_count = sum(1 for task in tasks if task.get('employe') and task['employe'].get('email') == employe_email and task['statut'] == 'en cours')

    return tasks_in_progress_count >= 3

# Route Flask pour afficher le formulaire de création de tâche
@app.route("/create", methods=['GET'])
def createTaskForm():
    employees = json.load(open("employes.json"))
    return render_template('create.html', employees=employees)

@app.route("/create", methods=['POST'])
def createTask():
    # Extraire les détails de la tâche à partir des données du formulaire.
    titre = request.form['titre']
    description = request.form['description']
    statut = request.form['statut']
    employe_email = request.form['employe']  # Get the selected employee's email from the form
    
    # Charger les employés à partir du fichier JSON
    employees = json.load(open("employes.json"))

    # Trouver l'employé sélectionné dans la liste des employés
    selected_employee = None
    for employee in employees:
        if employee['email'] == employe_email:
            selected_employee = employee
            break
 # Vérifier si l'employé a dépassé la limite de tâches
    if has_exceeded_task_limit(employe_email):
        error_message = "Employee '{}' already has 3 tasks in progress. Cannot assign more tasks.".format(selected_employee['nom'])
        flash(error_message, "error")
        return render_template('create.html', employees=employees, confirmation_message=error_message)

    # Créer un nouvel objet tâche
    new_task = {
        'titre': titre,
        'description': description,
        'statut': statut,
        'employe': selected_employee  # Attribuer les détails de l'employé sélectionné à la clé 'employe'
    }

    tasks = json.load(open("taches.json"))
    
    # Ajouter la nouvelle tâche à la liste des tâches
    tasks.append(new_task)

    # Écrire la liste des tâches mise à jour dans le fichier JSON
    with open('taches.json', 'w') as f:
        json.dump(tasks, f, indent=4)

    # Afficher un message de confirmation
    confirmation_message = "Task '{}' created successfully.".format(titre)
    return render_template('create.html', confirmation_message=confirmation_message, employees=employees)

# Ecran 5 : Lister les employes
@app.route("/employees")
def listEmployees():
    employes = json.load(open(path_employes))  
    confirm_delete = True
    delete_route = "/employees/delete/"
    tasks = json.load(open(path))
    
    employees_with_stats = []
    for employee in employes:
        email = employee['email']
        
        # Initialiser le nombre total de tâches et le nombre de tâches en cours pour chaque employé
        total_tasks = 0
        tasks_in_progress = 0
        
        # Calculer le nombre total de tâches et le nombre de tâches en cours pour l'employé
        for task in tasks:
            if isinstance(task['employe'], dict) and task['employe']['email'] == email:
                total_tasks += 1
                if task['statut'] == 'en cours':
                    tasks_in_progress += 1
        
        # Ajouter les statistiques calculées au dictionnaire de l'employé
        employee['total_tasks'] = total_tasks
        employee['tasks_in_progress'] = tasks_in_progress
        employees_with_stats.append(employee)
        
    return render_template("employees.html", employes=employees_with_stats, confirm_delete=confirm_delete, delete_route=delete_route)

# Route Flask pour exporter tous les employés au format JSON 
@app.route("/employees/export")
def exportEmployees():
    employees = json.load(open(path_employes))  
    return jsonify(employees)
# fontion de statistique de nombre taches
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
        flash("Employee '{}' updated successfully.".format(email), "success")
        return redirect("/employees")  # Redirection vers l'écran de listing des employés
    # Affichage du formulaire d'édition avec les données de l'employé
    return render_template("edit_employee.html", employee=employee_to_edit)

# Supprimer Emplyee (désassignée Tache)
@app.route('/employees/delete/<email>', methods=['GET'])
def delete_employee(email):
    # Charger les tâches à partir du fichier JSON
    todos = json.load(open(path))
    
    # Vérifier s'il y a des tâches assignées à l'employé
    employe_tasks = [task for task in todos if task.get('employe') and task['employe'].get('email') == email]
    if employe_tasks:
        # Vérifier s'il y a des tâches en cours assignées à l'employé
        todo_tasks_in_progress = [task for task in employe_tasks if task['statut'] == 'en cours']
        if todo_tasks_in_progress:
            flash("Cannot delete employee '{}' because they have tasks in progress.".format(email), "error")
            return redirect("/employees")
        
        # Vérifier s'il y a des tâches au statut "non assignee" assignées à l'employé
        for task in todos:
            if task.get('employe') and task['employe'].get('email'):
                if task['employe']['email'] == email and task['statut'] == 'non assignee':
                    task['employe'] = None
        
        # Écrire les modifications dans le fichier JSON après avoir parcouru toutes les tâches
        with open(path, 'w') as f:
            json.dump(todos, f, indent=4)
        
        # Flash message avec le titre de la tâche pour chaque tâche associée à l'employé
        for task in employe_tasks:
            flash("Employee '{}' for task '{}' deleted successfully.".format(email, task.get('titre')), "success")
        
        return redirect("/employees")
app.run(port=8080)