# 📄 Guide : Créer et exporter des documents avec l'Agent IA

> **Date** : 18 juin 2026  
> **Objectif** : L'agent génère des fichiers (TXT, CSV, JSON, Word, PDF) et les sauvegarde dans un dossier `outputs/`.

---

## 🏠 L'analogie du secrétaire

Jusqu'ici, votre agent était un **consultant** qui répondait à vos questions.  
Maintenant, il devient un **secrétaire** qui, en plus de répondre, peut :
- **Rédiger une lettre** et la sauvegarder dans un fichier Word
- **Créer un tableau** (CSV) avec les résultats de ses recherches
- **Exporter une conversation** en PDF pour l'imprimer
- **Générer un JSON** structuré à partir de données extraites

---

## 📦 Ce que l'agent peut créer

| Format | Extension | Usage | Bibliothèque Python |
|---|---|---|---|
| **Texte brut** | `.txt` | Notes, rapports simples, extraits | Aucune (fichier natif) |
| **Markdown** | `.md` | Documents structurés avec titres, listes | Aucune |
| **CSV** | `.csv` | Tableaux de données (Excel compatible) | `csv` (natif Python) |
| **JSON** | `.json` | Données structurées (API, configurations) | `json` (natif Python) |
| **Word** | `.docx` | Documents professionnels, lettres, rapports | `python-docx` |
| **PDF simple** | `.pdf` | Documents à imprimer, factures, rapports | `fpdf2` (léger) |

> **Pourquoi pas Excel `.xlsx` ?** C'est possible avec `openpyxl`, mais c'est plus lourd. CSV s'ouvre parfaitement dans Excel et suffit pour 95% des usages.

---

## 🛡️ Sécurité : le bac à sable (`outputs/`)

L'agent ne peut écrire que dans un dossier spécifique : **`outputs/`**. C'est une règle de sécurité absolue.

**Pourquoi ?** Imaginez que vous demandiez : *"Crée un fichier sur mon bureau"*. L'agent pourrait écraser un fichier important. Le bac à sable l'empêche de sortir de son terrain de jeu.

```
mon-projet/
├── outputs/          ← ✅ L'agent peut écrire ici
│   ├── rapport.txt
│   ├── données.csv
│   └── lettre.docx
├── documents/        ← 🔒 L'agent ne peut PAS écrire ici (lecture seule)
├── venv/             ← 🔒 Interdit
└── memory.json       ← 🔒 Interdit
```

---

## 🎯 Exemples concrets d'utilisation

### 1. Rédiger un rapport à partir d'une analyse
```
Vous > Analyse mon contrat de location et crée un résumé en Word
[Agent lit le PDF via RAG, analyse, puis génère un .docx]
Agent > J'ai créé le résumé dans outputs/resume_contrat.docx
```

### 2. Extraire des données en tableau
```
Vous > Cherche dans mes documents tous les montants mentionnés et crée un CSV
[Agent fouille via RAG, compile les données, génère un CSV]
Agent > Tableau créé : outputs/montants.csv (3 lignes, colonnes : Source, Montant, Contexte)
```

### 3. Sauvegarder la conversation
```
Vous > Exporte notre conversation en PDF
[Agent compile l'historique, génère un PDF structuré]
Agent > Conversation exportée : outputs/conversation_2026-06-19.pdf
```

### 4. Générer une configuration JSON
```
Vous > Crée un JSON avec mes préférences : thème sombre, langue français, modèle qwen2.5
[Agent génère un fichier JSON structuré]
Agent > Fichier créé : outputs/config.json
```

### 5. Lettre type
```
Vous > Rédige une lettre de motivation pour un poste de développeur IA et sauvegarde-la
[Agent rédige le texte, formate en Word avec en-tête/pied de page]
Agent > Lettre créée : outputs/lettre_motivation.docx
```

---

## 📋 Détail des formats

### TXT / Markdown (natif)
Aucune bibliothèque externe. L'agent écrit directement du texte.

### CSV (natif)
Le module `csv` de Python est inclus d'office. Parfait pour tableaux.

### Word (.docx)
`python-docx` permet de créer des documents avec :
- Titres, paragraphes, listes à puces
- Mise en forme (gras, italique, couleur)
- En-têtes et pieds de page
- Tableaux

### PDF simple
`fpdf2` est la bibliothèque la plus légère pour créer des PDF. Elle gère :
- Texte avec polices
- Titres, paragraphes
- Tableaux simples
- Images (si besoin)

> **Pourquoi pas `reportlab` ?** Plus puissant mais beaucoup plus lourd à installer. `fpdf2` suffit pour 95% des usages.

---

## ⚠️ Limites importantes

| Limite | Explication |
|---|---|
| **Bac à sable** | L'agent ne peut écrire que dans `outputs/`. Les chemins comme `../../fichier.txt` ou `C:\Windows\` sont bloqués. |
| **PDF complexes** | `fpdf2` ne fait pas de mise en page magazine. Pour des PDF très complexes, il faudrait `reportlab` ou convertir un Word en PDF avec LibreOffice. |
| **Word avancé** | `python-docx` ne gère pas les macros, les formules Excel intégrées, ou les styles très complexes. |
| **Écrasement** | Si vous demandez deux fois le même nom de fichier, l'ancien est écrasé. L'agent peut ajouter un timestamp automatique. |
| **Taille** | Un document de 100 pages généré par l'IA sera lent à écrire (mais fonctionnera). |

---

## 🚀 Installation

```bash
# Pour Word
pip install python-docx

# Pour PDF (optionnel, léger)
pip install fpdf2
```

> **Note** : si vous n'installez pas `fpdf2` ou `python-docx`, l'agent générera du TXT/Markdown/CSV/JSON à la place. C'est gracieux.

---

## 🧠 Le nouvel outil : `creer_document`

L'agent dispose d'un outil dans son menu :

```json
{
  "type": "function",
  "function": {
    "name": "creer_document",
    "description": "Crée un fichier texte, CSV, JSON, Word ou PDF dans le dossier outputs/.",
    "parameters": {
      "type": "object",
      "properties": {
        "nom_fichier": {"type": "string", "description": "Nom du fichier avec extension (ex: rapport.txt)"},
        "contenu": {"type": "string", "description": "Contenu texte du document"},
        "format": {"type": "string", "description": "Format : txt, md, csv, json, docx, pdf"}
      },
      "required": ["nom_fichier", "contenu"]
    }
  }
}
```

Quand l'agent décide de créer un document, il appelle cet outil. Le programme vérifie la sécurité, formate le contenu, et sauvegarde.
