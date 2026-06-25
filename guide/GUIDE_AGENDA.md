# 📅 Guide : Agenda / TODO List Intégré

> **Objectif** : Transformer votre agent en organisateur personnel. Il gère vos tâches, rappels et liste de courses dans un fichier `agenda.json`.

---

## 🏠 Analogie : le Secrétaire Personnel

Jusqu'ici, votre agent était un **consultant** qui répondait à vos questions.  
Avec l'agenda, il devient un **secrétaire personnel** qui :
- Prend des notes quand vous lui dites : *"Rappelle-moi d'appeler le dentiste demain"*
- Vous lit votre emploi du temps quand vous demandez : *"Que dois-je faire aujourd'hui ?"*
- Coche les tâches faites : *"J'ai appelé le dentiste"*
- Oublie les tâches vieilles de plusieurs semaines

---

## 📦 Fonctionnalités

| Outil | Ce qu'il fait | Exemple |
|---|---|---|
| **ajouter_tache** | Crée une nouvelle tâche | *"Rappelle-moi d'appeler le dentiste demain"* |
| **lister_taches** | Affiche les tâches (filtrables) | *"Que dois-je faire aujourd'hui ?"* |
| **marquer_fait** | Coche une tâche comme terminée | *"J'ai fini la tâche du dentiste"* |
| **supprimer_tache** | Supprime une tâche | *"Annule le rappel pour le dentiste"* |

---

## 🎯 Exemples de requêtes

```markdown
Vous > Rappelle-moi d'appeler le dentiste demain à 14h
Agent > ✅ Tâche ajoutée : "Appeler le dentiste" (demain, 14h, priorité normale)

Vous > Ajoute "Acheter du lait" à ma liste de courses avec priorité haute
Agent > ✅ Tâche ajoutée : "Acheter du lait" (priorité haute)

Vous > Que dois-je faire aujourd'hui ?
Agent > 📋 Vos tâches pour aujourd'hui :
     1. [ ] Appeler le dentiste (14h) — priorité normale
     2. [ ] Acheter du lait — priorité haute

Vous > J'ai acheté le lait
Agent > ✅ Tâche "Acheter du lait" marquée comme faite.

Vous > Annule le rendez-vous chez le dentiste
Agent > 🗑️ Tâche "Appeler le dentiste" supprimée.

Vous > Montre-moi toutes mes tâches
Agent > 📋 Toutes vos tâches :
     1. [✓] Acheter du lait — fait aujourd'hui
     2. [ ] Finir le rapport — pour demain
```

---

## 🛡️ Sécurité

- Le fichier `agenda.json` est stocké localement (hors Git via `.gitignore`)
- Seul l'agent peut le modifier via ses outils
- Les tâches ont un **ID unique** pour éviter les confusions

---

## ⚠️ Limites

1. **Pas de notification** : l'agent ne peut pas vous envoyer de notification push ou sonore quand une tâche est due. Il faut lui demander *"Que dois-je faire aujourd'hui ?"*.
2. **Pas de calendrier visuel** : c'est une liste de tâches, pas un agenda avec créneaux horaires précis.
3. **Pas de récurrence** : une tâche quotidienne (ex: *"Prendre mon médicament tous les jours"*) doit être ajoutée manuellement chaque jour pour l'instant.

---

## 📝 Format du fichier `agenda.json`

```json
{
  "taches": [
    {
      "id": "t_001",
      "nom": "Appeler le dentiste",
      "description": "Prendre rendez-vous pour le contrôle",
      "date": "2026-06-25",
      "priorite": "normale",
      "fait": false,
      "date_creation": "2026-06-20T10:15:00"
    }
  ]
}
```

| Champ | Description |
|---|---|
| `id` | Identifiant unique (ex: `t_001`) |
| `nom` | Titre court de la tâche |
| `description` | Détails optionnels |
| `date` | Date d'échéance (YYYY-MM-DD) ou `null` |
| `priorite` | `basse`, `normale`, `haute`, `urgente` |
| `fait` | `true` ou `false` |
| `date_creation` | Quand la tâche a été créée |
