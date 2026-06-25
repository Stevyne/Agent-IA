# 🚀 Guide : Publier votre Agent IA sur GitHub

## Pourquoi un `.gitignore` est indispensable ?

GitHub est un **vestiaire public** (ou privé, mais versionné). Vous ne voulez pas y ranger :
- Vos **documents confidentiels** (PDF, Word, TXT)
- Vos **conversations privées** avec l'IA (`memory.json`)
- Une **base de données de 500 Mo** (`chroma_db/`) qui se reconstruit en 10 secondes
- Les **fichiers techniques** inutiles (cache Python, environnement virtuel)

Le fichier `.gitignore` dit à Git : **"Ignore ces fichiers, ne les pousse jamais sur GitHub."**

---

## 📋 Ce que mon `.gitignore` exclut (expliqué ligne par ligne)

### 1. Python classique
```
venv/           ← Votre environnement virtuel (toutes les bibliothèques installées)
__pycache__/    ← Cache automatique créé par Python
*.pyc           ← Fichiers compilés Python
```
> **Pourquoi ?** `venv/` peut peser **plusieurs Go** (PyTorch, ChromaDB, etc.). Chaque développeur recrée le sien avec `pip install`.

### 2. IDE / Éditeurs
```
.vscode/        ← Paramètres de VS Code
.idea/          ← Paramètres de PyCharm
```
> **Pourquoi ?** Vos préférences de couleurs et de raccourcis ne concernent que vous.

### 3. SPÉCIFIQUE À VOTRE PROJET (le plus important !)

| Fichier/Dossier | Pourquoi l'ignorer ? | Analogie |
|---|---|---|
| `memory.json` | Contient **l'historique de vos conversations** avec l'IA. C'est privé. | Vous ne publiez pas votre journal intime. |
| `chroma_db_docs/` | Contient la **base de données vectorielle** (copie indexée de vos documents). Elle peut faire **100+ Mo** et se reconstruit automatiquement au lancement. | Vous ne publiez pas une photocopie de toute votre bibliothèque. |
| `documents/` | Contient vos **fichiers personnels** (PDF, Word, TXT). Ce sont VOS documents, pas le code du projet. | Vous ne laissez pas vos papiers personnels sur le bureau d'un café. |
| `.env` | Si un jour vous ajoutez une clé API (OpenAI, Google, etc.), elle reste **secrète**. | Vous ne publiez pas votre code de carte bancaire. |

---

## 📁 Structure de votre projet sur GitHub (ce qui sera visible)

```
mon-agent-ia/
├── .gitignore              ← ✅ Ignorance list
├── agent_terminal.py       ← ✅ Code source
├── agent_avec_memoire.py   ← ✅ Code source
├── agent_avec_rag.py       ← ✅ Code source
├── agent_documents.py      ← ✅ Code source
├── app_web.py              ← ✅ Code source
├── README.md               ← ✅ Description du projet (à créer !)
├── requirements.txt        ← ✅ Liste des bibliothèques nécessaires
├── EXPLICATION_CODE.md     ← ✅ Votre cours
├── GUIDE_INSTALLATION.md   ✅ Votre guide
└── documents/              ← ❌ IGNORÉ (non publié)
    ├── contrat.pdf         ← ❌ Reste sur votre PC uniquement
    └── notes.txt           ← ❌ Reste sur votre PC uniquement
```

---

## 🛠️ Étape 1 : Créer le fichier `requirements.txt`

Ce fichier dit aux autres (et à vous dans 6 mois) quelles bibliothèques installer. Dans votre terminal (venv activé) :

```bash
pip freeze > requirements.txt
```

Mais attention : `pip freeze` liste **tout**, y compris les dépendances des dépendances. Pour un projet propre, créez plutôt le fichier à la main avec l'essentiel :

**`requirements.txt`** :
```text
ollama>=0.4.0
streamlit>=1.40.0
chromadb>=0.5.0
pypdf>=5.0.0
python-docx>=1.1.0
```

> Les `>=` signifient "cette version ou plus récente". C'est plus flexible que `==` (version exacte).

---

## 🛠️ Étape 2 : Créer un `README.md` pour GitHub

Créez ce fichier à la racine. C'est la vitrine de votre projet sur GitHub :

```markdown
# 🤖 Agent IA Local (PDF, Word, TXT)

Un agent conversationnel 100% offline qui peut :
- Répondre avec un modèle de langage local (via **Ollama**)
- Utiliser des outils (calculatrice, horloge)
- **Lire et fouiller** dans vos documents PDF, Word et TXT
- **Se souvenir** de vos conversations (mémoire persistante)

## 🚀 Installation rapide

```bash
# 1. Cloner le projet
git clone https://github.com/VOTRE_NOM/mon-agent-ia.git
cd mon-agent-ia

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer Ollama et télécharger un modèle
# https://ollama.com/download
ollama pull qwen2.5:3b

# 5. Lancer
python agent_documents.py
```

## 📁 Ajouter vos documents

Créez un dossier `documents/` à la racine et placez-y vos fichiers `.pdf`, `.docx` ou `.txt`.

> ⚠️ Le dossier `documents/` est ignoré par Git (`.gitignore`) pour ne pas publier vos fichiers privés.

## 🛠️ Configuration

Modifiez la variable `MODEL` dans les fichiers Python selon votre VRAM :
- `qwen2.5:3b` → GTX 1060 (6 Go)
- `qwen2.5:7b` → GTX 1070/1080/1080 Ti (8-11 Go)
```

---

## 🛠️ Étape 3 : Initialiser Git et pousser sur GitHub

### Si vous n'avez pas encore créé le dépôt local :

```bash
# 1. Se placer dans le dossier du projet
cd mon-agent-ia

# 2. Initialiser Git
git init

# 3. Ajouter le fichier .gitignore D'ABORD (important !)
git add .gitignore

# 4. Ajouter vos fichiers sources
# ATTENTION : vérifiez que documents/ et memory.json ne sont pas listés !
git add agent_documents.py agent_terminal.py agent_avec_memoire.py app_web.py
# ou simplement : git add *.py *.md requirements.txt

# 5. Vérifier ce qui va être envoyé
git status

# 6. Créer le premier commit
git commit -m "Premier commit : agent IA local avec lecture PDF/Word"

# 7. Connecter à GitHub (créez d'abord un dépôt vide sur github.com)
git remote add origin https://github.com/VOTRE_NOM/mon-agent-ia.git

# 8. Pousser
git push -u origin main
```

### ⚠️ Vérification cruciale avant de pousser

Tapez **toujours** cette commande avant chaque commit :
```bash
git status
```

Si vous voyez `documents/` ou `memory.json` dans la liste des fichiers "à envoyer", **arrêtez-vous**. Votre `.gitignore` ne fonctionne pas.

**Si c'est le cas** :
```bash
# Retirer les fichiers de l'index (sans les supprimer de votre PC)
git rm -r --cached documents/
git rm --cached memory.json

git add .gitignore
git commit -m "Correction : ajout du .gitignore pour fichiers privés"
```

---

## 🔒 Bonnes pratiques de sécurité

| Règle | Pourquoi ? |
|---|---|
| **Jamais** `memory.json` sur GitHub | Contient vos conversations réelles avec l'IA |
| **Jamais** `documents/` sur GitHub | Vos PDF/Word peuvent être confidentiels |
| **Jamais** `chroma_db/` sur GitHub | Se reconstruit automatiquement, pèse lourd |
| **Jamais** de clé API dans le code | Si vous en ajoutez un jour, utilisez `.env` + `.gitignore` |
| **Toujours** `requirements.txt` | Permet à quelqu'un d'autre (ou à vous plus tard) de recréer le projet |

---

## 🧪 Tester que tout est propre

Après avoir poussé sur GitHub, faites ce test de confidentialité :

```bash
# Créez un dossier temporaire
mkdir /tmp/test-clone
cd /tmp/test-clone

# Clonez votre dépôt
git clone https://github.com/VOTRE_NOM/mon-agent-ia.git

# Vérifiez ce qui est présent
ls mon-agent-ia/
```

**Vous ne devez PAS voir** :
- `documents/`
- `memory.json`
- `chroma_db_docs/`
- `venv/`
- `__pycache__/`

Si vous les voyez, ils sont publics. Corrigez immédiatement.

---

## 🎓 Explication technique : pourquoi `.gitignore` ne fonctionne pas rétroactivement

**Règle d'or** : `.gitignore` ne s'applique que aux fichiers **pas encore suivis** par Git.

Si vous avez déjà fait `git add documents/` avant de créer `.gitignore`, Git **continue** de suivre ces fichiers. Il faut explicitement dire à Git d'arrêter :

```bash
git rm -r --cached documents/     # Arrête de suivre le dossier
git rm --cached memory.json       # Arrête de suivre le fichier
```

Puis committez le `.gitignore` mis à jour.

---

**Votre projet est maintenant prêt à être publié en toute sécurité !** 🎉
