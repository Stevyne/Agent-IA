# 🔍 Guide : Pipeline Vision → Analyse de Données

> **Objectif** : Uploadez une image contenant des données (tableau Excel, graphique, facture, capture d'écran de stats) et demandez "fais un graphique" ou "analyse ces données". L'agent extrait automatiquement les chiffres avec la vision, puis les analyse avec Python.

---

## 🏰 Analogie : le Binocliste et le Comptable

Imaginez un **binocliste** (la vision) qui regarde un document flou de loin et vous décrit ce qu'il voit : *"Il y a des colonnes avec des chiffres..."*.  
Puis un **comptable** (Python) qui prend ces chiffres, les met dans un tableau propre, et fait les calculs.

Le **pipeline** est une **chaîne d'usine** à deux postes :
1. **Poste 1 — Extraction** (LLaVA regarde l'image) : *"Voici les données brutes : Janvier:120, Février:150..."*
2. **Poste 2 — Analyse** (Python) : *"Je crée un DataFrame, je calcule la moyenne, je génère un graphique..."*

---

## 🔧 Comment ça marche

```
Vous > [Uploader image_tableau.png]
Vous > "Fais un graphique en barres avec ces données"
    ↓
DÉTECTION AUTO : image présente + mots-clés "graphique", "données"
    ↓
ÉTAPE 1 — Extraction Vision (LLaVA)
  "Extrais toutes les données de cette image sous forme brute structurée"
    ↓
  LLaVA répond : "Mois,Ventes\nJanvier,120\nFévrier,150\nMars,110"
    ↓
ÉTAPE 2 — Analyse Python (Qwen + bac à sable)
  "Voici les données : [texte extrait]. Crée un graphique en barres."
    ↓
  Qwen écrit du code Python → exécute dans le bac à sable
    ↓
  Graphique PNG généré dans outputs/sandbox/
    ↓
Agent > 📊 Graphique généré ! [Image affichée dans le chat]
     Moyenne : 126.7, Max : 150 (Février)
```

---

## 🎯 Ce que le pipeline peut faire

| Type d'image | Exemple de demande | Résultat |
|---|---|---|
| **Tableau de chiffres** | *"Fais un graphique en barres"* | Graphique PNG généré avec les données extraites |
| **Graphique existant** | *"Extrais les données et refais le graphique en ligne"* | Données récupérées, nouveau graphique différent |
| **Facture / Reçu** | *"Calcule le total et la moyenne des montants"* | Total, moyenne, stats des montants |
| **Capture d'écran Excel** | *"Convertis en CSV et affiche les 5 premières lignes"* | Fichier CSV généré + aperçu |
| **Tableau de scores** | *"Qui a le meilleur score ?"* | Analyse des scores, classement |
| **Camembert / Pie chart** | *"Extrais les pourcentages et refais un camembert"* | Nouveau graphique camembert |

---

## 🚀 Comment utiliser

1. **Uploadez une image** contenant des données dans la sidebar (comme d'habitude)
2. **Posez une question** avec des mots-clés d'analyse :
   - *"Fais un graphique"*
   - *"Analyse ces données"*
   - *"Calcule la moyenne"*
   - *"Extrais les chiffres en CSV"*
   - *"Transforme ça en tableau Python"*
3. **L'agent détecte automatiquement** le pipeline et orchestre les deux étapes

> **Important** : La qualité de l'extraction dépend de la clarté de l'image. Si les chiffres sont flous ou très petits, LLaVA peut se tromper. Vérifiez toujours les données extraites dans la réponse de l'agent.

---

## ⚠️ Limites

1. **Extraction approximative** : LLaVA est un modèle de vision, pas un OCR professionnel. Les chiffres peuvent être légèrement erronés (ex: `120` lu comme `128`). Pour des données critiques, vérifiez avant d'agir.
2. **Pas de tableaux complexes** : les tableaux avec des cellules fusionnées, des couleurs, ou des mises en page très denses sont difficiles à extraire.
3. **Mots manuscrits** : l'écriture manuscrite est mal reconnue par les modèles vision locaux.
4. **Langue** : les chiffres arabes sont bien reconnus, mais les textes en français avec accents peuvent parfois être mal transcrits.

---

## 💡 Conseils pour de meilleurs résultats

- **Image nette** : plus la résolution est bonne, plus l'extraction est fidèle
- **Contraste élevé** : texte noir sur fond blanc est idéal
- **Demandez explicitement** : *"Fais un graphique en barres avec les données de l'image"* déclenche le pipeline mieux que *"Que vois-tu ?"*
- **Vérifiez** : si les données extraites semblent fausses, dites *"Les chiffres sont erronés, voici les corrections : ..."*
