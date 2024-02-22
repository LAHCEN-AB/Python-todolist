from flask import Flask, redirect, render_template, request
import json

app = Flask(__name__)

path = "taches.json"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/current")
def todosIndex():
    todos = json.load(open(path))
    statut_non = "non assignee"
    statut_current = "en cours"
    todos_current = list(filter(lambda x: x['statut'] == statut_current, todos))
    todos_non_assigne = list(filter(lambda x: x['statut'] == statut_non, todos))
    
    return render_template('current.html', todos_current=todos_current, todos_non_assigne=todos_non_assigne)

@app.route("/current/delete/<titre>", methods=['GET'])
def todosDelete(titre):
    todos = json.load(open(path))
    
    # Remove the task with the given title
    todos = [todo for todo in todos if todo['titre'] != titre]

    # Rewrite the file with the filtered list
    json.dump(todos, open(path, 'w'))

    return redirect('/current')

@app.route("/current/edit/<titre>", methods=['GET'])
def todosEdit(titre):
    todos = json.load(open(path))
    
    # Find the task with the given title
    todo = next((todo for todo in todos if todo['titre'] == titre), None)

    if todo is None:
        return render_template('task_not_found.html')

    return render_template('todosEdit.html', todo=todo)

@app.route("/current/edit/<titre>", methods=['POST'])
def todosEditPOST(titre):
    todos = json.load(open(path))
    
    # Find the task with the given title
    todo = next((todo for todo in todos if todo['titre'] == titre), None)

    if todo is None:
        return render_template('task_not_found.html')

    # Update task details
    todo['titre'] = request.form['titre']
    todo['description'] = request.form['description']
    todo['statut'] = request.form['statut']
    # todo['employe'] = request.form['employe']

    # Rewrite the file with the updated list
    json.dump(todos, open(path, 'w'))

    return redirect('/current')

if __name__ == "__main__":
    app.run(port=8080)
