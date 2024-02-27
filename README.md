# Python-todolist

# Description
Ce projet Python est une application de liste de tâches avec une interface utilisateur conviviale. Il permet de gérer les tâches en cours, toutes les tâches, la création et l'édition de tâches, la gestion des employés, ainsi que la création et l'édition d'employés.

# Menu de Navigation
Chaque page comporte un menu de navigation avec les liens suivants :

Taches en cours
Toutes les taches
Nouvelle tache
Gestion des employés
Ajout d'un employé
Écrans
# Écran 1: Taches en cours
Affiche une liste des tâches en cours. Les tâches sont triées par statut ('non assignée', puis 'en cours'). Les tâches terminées ne sont pas affichées.
Pour chaque tâche sont affichés :

Titre
Description
Employé assigné
Lien pour éditer la tâche
Lien pour supprimer la tâche (avec confirmation).
# Écran 2 : Toutes les taches
Affiche une liste de toutes les tâches.
En haut de l'écran, un lien permet d'exporter toutes les tâches au format JSON.
Pour chaque tâche sont affichés :

Titre
Description
Statut
Employé assigné
Lien pour éditer la tâche
Lien pour supprimer la tâche (avec confirmation).

# Écran 3 : Création d'une tâche
Permet de créer une nouvelle tâche avec les champs suivants :

Titre
Description
Statut : 'non assignée', 'en cours', 'terminée'.
Employé assigné
Après la création d'une tâche, un message de confirmation est affiché et le formulaire de création de tâche est vidé pour faciliter la création de plusieurs tâches.

# Écran 4 : Édition d'une tâche
Permet d'éditer une tâche avec les champs suivants :

Titre
Description
Statut : 'non assignée', 'en cours', 'terminée'.
Employé assigné
Après la modification d'une tâche, l'utilisateur est redirigé vers l'écran d'accueil (écran 1) et un message de confirmation est affiché.

# Écran 5 : Liste des employés
Affiche une liste de tous les employés.
En haut de l'écran, un lien permet d'exporter tous les employés au format JSON.
Pour chaque employé sont affichés :

Prénom
Nom
Email
Icône
Nombre de tâches en cours
Nombre total de tâches
Lien d'édition
Lien de suppression

# Écran 6 : Créer un employé
Permet de créer un nouvel employé avec les champs suivants :

Prénom
Nom
Email
Icône
Après la création d'un employé, l'utilisateur est redirigé vers l'écran de liste des employés et un message de confirmation est affiché.

# Écran 7 : Éditer un employé
Permet d'éditer un employé avec les champs suivants :

Prénom
Nom
Email
Icône
Après la modification d'un employé, l'utilisateur est redirigé vers l'écran de liste des employés et un message de confirmation est affiché.
Règles de Gestion pour les Employés
L'email d'un employé est unique, donc un employé ne peut pas être créé sans adresse email ou avec une adresse email déjà existante.
Un employé ne peut pas être assigné à plus de 3 tâches en cours.
Il n'est pas possible de supprimer un employé s'il a des tâches en cours. En cas de suppression d'un employé, toutes les tâches en cours qui lui sont assignées sont désassignées.