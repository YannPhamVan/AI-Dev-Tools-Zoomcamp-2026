# Spécification Fonctionnelle : ShareTrip
## Application de Partage de Dépenses pour Voyages entre Amis

### 1. Vue d'ensemble du Projet
L'application est une plateforme full-stack conçue pour simplifier la gestion et l'équilibrage des dépenses lors de voyages en groupe. L'objectif principal est de permettre à un groupe d'amis de saisir leurs dépenses au fil de l'eau et d'obtenir un calcul d'équilibrage final optimisé, réduisant au strict minimum le nombre de transactions/virements nécessaires entre les participants.

L'interface se veut ultra-simple, épurée et centrée sur l'efficacité (utilisable facilement sur mobile pendant un voyage).

### 2. Fonctionnalités Clés (Périmètre MVP)

#### A. Gestion du Groupe et des Participants
*   Création d'un voyage avec un nom (ex: "Weekend à Rome").
*   Ajout rapide des membres du groupe par leur prénom (pas de système d'inscription lourd pour le MVP).

#### B. Gestion des Dépenses
*   Formulaire de saisie ultra-simple :
    *   Qui a payé ? (Sélection du membre).
    *   Combien ? (Montant en valeur numérique).
    *   Pour quoi ? (Description courte, ex: "Restaurant").
*   Par défaut, la dépense est partagée équitablement entre tous les membres du groupe.
*   Historique chronologique des dépenses affiché sous forme de liste simple.

#### C. Calcul d'Équilibrage Optimisé (Algorithme de Règlement)
*   Calcul en temps réel ou sur demande du solde de chaque participant (Dépenses payées - Part due).
*   Génération d'un plan de remboursement optimisé : l'application calcule "Qui doit combien à qui" en utilisant un algorithme glouton (Greedy Algorithm) pour minimiser le nombre total de virements.

### 3. Architecture Technique Prévue
*   **Frontend :** Application Node.js (générée de manière simplifiée pour le UI).
*   **Backend :** API Python managée avec le gestionnaire de paquets ultra-rapide `uv`.
*   **Base de données :** Stockage relationnel simple pour les utilisateurs, les voyages et les transactions.

### 4. Interface Utilisateur (UI) - Maquette Conceptuelle
L'application tiendra sur un écran principal divisé en trois sections :
1.  **En-tête :** Nom du voyage et liste des participants.
2.  **Flux Central :** Liste des dépenses passées + Bouton "+" pour ouvrir un formulaire de saisie rapide.
3.  **Pied de page / Onglet Résolution :** Un tableau "Équilibrez vos comptes" affichant les lignes de transfert requises (ex: *Yann doit 15€ à Marc*).
