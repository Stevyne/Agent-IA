# 🧮 Guide : Bac à Sable Python (Exécution de Code Sécurisée)

> **Objectif** : Permettre à l'agent d'écrire et d'exécuter du code Python pour résoudre des problèmes complexes, créer des graphiques, ou transformer des données — sans risque pour votre PC.

---

## 🏰 Analogie : le Laboratoire de Chimie Scolaire

Imaginez un **laboratoire de chimie scolaire** :
- Vous avez des **tubes à essai**, des **béchers** et des **réactifs** (Python, NumPy, Matplotlib)
- Les **produits dangereux** (acides forts = commandes système) sont **enfermés dans une armoire** (interdits)
- Si une expérience **explose**, elle casse juste le **tube à essai** (fichier temporaire), pas le **bâtiment** (votre PC)
- Vous voyez le **résultat** (couleur, précipité) à travers la **vitre** (l'interface Streamlit)

Le bac à sable Python est exactement cela : un **laboratoire isolé** où l'IA peut expérimenter sans risquer votre système.

---

## 🔒 Sécurité : ce qui est interdit

Le code exécuté par l'agent **ne peut pas** :
- Accéder à Internet (`socket`, `urllib`, `requests`)
- Exécuter des commandes système (`os.system`, `subprocess`)
- Supprimer ou modifier vos fichiers personnels (`os.remove`, `shutil.rmtree`)
- Lire des fichiers hors du dossier `outputs/sandbox/`
- Utiliser `eval()` ou `exec()` (code dynamique dangereux)

**Ce qui est autorisé** :
- `numpy`, `pandas`, `matplotlib` (installés par défaut)
- `json`, `csv`, `math`, `random`, `statistics`
- Créer des fichiers **uniquement** dans `outputs/sandbox/`

---

## 🧪 Ce que l'agent peut faire maintenant

### 1. Calculs complexes et statistiques
```
Vous > Calcule la moyenne, médiane, écart-type de : 12, 15, 18, 22, 5, 9, 30
Agent > [exécute numpy]
       Moyenne : 15.8
       Médiane : 15.0
       Écart-type : 8.3
```

### 2. Graphiques et visualisations
```
Vous > Crée un graphique en barres avec les ventes : Janvier 120, Février 150, Mars 110
Agent > [exécute matplotlib]
       📊 Graphique sauvegardé : outputs/sandbox/figure_1.png
       [L'image s'affiche directement dans le chat]
```

### 3. Transformation de données
```
Vous > Convertis cette liste en JSON structuré : [{"nom":"Alice","age":30}, ...]
Agent > [exécute Python]
       ```json
       { "personnes": [ {"nom": "Alice", "age": 30}, ... ] }
       ```
```

### 4. Simulations et modélisations
```
Vous > Simule 1000 lancers de dé et montre la distribution
Agent > [exécute numpy + matplotlib]
       📊 Histogramme sauvegardé : outputs/sandbox/figure_1.png
```

---

## 📦 Installation

Les bibliothèques scientifiques sont nécessaires :

```bash
pip install matplotlib numpy pandas
```

> **Note** : si elles ne sont pas installées, l'agent peut quand même exécuter du Python pur (calculs, transformations), mais pas de graphiques ni de calculs matriciels avancés.

---

## ⚠️ Limites à connaître

1. **Timeout** : le code est interrompu après **30 secondes** (boucle infinie protégée)
2. **Pas de persistance** : les variables ne survivent pas entre deux exécutions. Chaque appel est indépendant.
3. **Pas d'accès à vos fichiers** : le code ne peut pas lire votre `documents/` ni votre bureau. Il vit dans sa cage.
4. **Matplotlib non-interactif** : les graphiques sont sauvegardés en `.png`, pas affichés dans une fenêtre.
5. **Mémoire** : le code est limité par la mémoire de votre PC, mais sans privilèges système.

---

## 🎓 Pourquoi c'est utile

Les LLM locaux (comme Qwen 2.5) sont **mauvais en calculs exacts** et **ne peuvent pas générer d'images**. Le bac à sable compense ces deux faiblesses :
- **Calculs** : NumPy calcule exactement (pas d'hallucination)
- **Graphiques** : Matplotlib génère des images réelles
- **Données** : Pandas manipule des tableaux complexes

C'est comme donner une **calculatrice graphique** à un étudiant intelligent.
