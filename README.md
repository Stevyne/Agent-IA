# 🤖 Agent IA Local — Lecteur de Documents (PDF, Word, TXT)

Un agent conversationnel **100% offline** qui tourne sur votre PC avec un GPU NVIDIA (même un GTX 10xx). Il peut lire vos documents, se souvenir de vos conversations, et utiliser des outils (calculatrice, horloge).

---

## ✨ Ce que fait l'agent

- 💬 **Chat conversationnel** — Discutez en local, vos données ne quittent jamais votre PC
- 📄 **Lecture de documents** — Analysez vos PDF, Word (.docx) et fichiers texte
- 🔍 **Extraction intelligente** — "Extrais tous les passages sur la clause de confidentialité"
- 🧮 **Outils intégrés** — Calculatrice et horloge en temps réel
- 🧠 **Mémoire persistante** *(optionnel)* — L'IA se souvient de vos conversations d'hier
- 🌐 **Interface web** *(optionnel)* — Une jolie page dans le navigateur via Streamlit

---

## 🚀 Installation rapide

### 1. Prérequis
- Python 3.11+
- [Ollama](https://ollama.com) installé
- Un GPU NVIDIA (GTX 1060/1070/1080 fonctionnent)
- Drivers NVIDIA à jour

### 2. Cloner et installer

```bash
# Cloner le projet
git clone https://github.com/VOTRE_NOM/mon-agent-ia.git
cd mon-agent-ia

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux / macOS :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle d'IA (choisissez selon votre VRAM)
ollama pull qwen2.5:3b   # GTX 1060 6 Go
# ollama pull qwen2.5:7b # GTX 1070/1080/1080 Ti 8-11 Go
```

### 3. Ajouter vos documents

```bash
mkdir documents
```

Placez vos fichiers `.pdf`, `.docx` ou `.txt` dans le dossier `documents/`.

> ⚠️ Ce dossier est **ignoré par Git** (`.gitignore`) — vos documents privés ne seront jamais publiés sur GitHub.

### 4. Lancer l'agent

**Mode terminal (le plus simple) :**
```bash
python agent_documents.py
```

**Mode web (interface dans le navigateur) :**
```bash
streamlit run app_web.py
```

**Avec mémoire persistante :**
```bash
python agent_avec_memoire.py
```

---

## ⚙️ Configuration

Ouvrez les fichiers Python et modifiez la variable `MODEL` selon votre carte graphique :

```python
MODEL = "qwen2.5:3b"   # GTX 1060 (6 Go VRAM)
# MODEL = "qwen2.5:7b" # GTX 1070 / 1080 / 1080 Ti (8-11 Go VRAM)
```

---

## 📁 Structure du projet

```
mon-agent-ia/
├── agent_documents.py      # 🤖 Agent principal (PDF + Word + TXT + outils)
├── agent_terminal.py       # 💬 Chat simple en terminal
├── agent_avec_memoire.py   # 🧠 Chat avec mémoire persistante
├── app_web.py              # 🌐 Interface web Streamlit
├── agent_git.py            # 🛡️ Assistant pour publier sur GitHub
├── requirements.txt        # 📦 Liste des bibliothèques
├── README.md               # 📖 Ce fichier
├── .gitignore              # 🔒 Exclusions de sécurité
├── EXPLICATION_CODE.md     # 🎓 Cours : comment fonctionne le code
├── GUIDE_INSTALLATION.md   # 🛠️ Guide d'installation pas à pas
├── AGENT_PDF_WORD_GUIDE.md # 📄 Guide lecture de documents
├── APPRENDRE_A_IA.md       # 🧠 Comment faire apprendre l'IA
└── documents/              # 📄 Vos fichiers privés (IGNORÉ par Git)
```

---

## 🛡️ Sécurité & confidentialité

- **100% local** : le modèle tourne sur votre GPU via Ollama. Aucune donnée n'est envoyée sur Internet.
- **Documents privés** : le dossier `documents/` et l'historique `memory.json` sont exclus de Git via `.gitignore`.
- **Vérification automatique** : lancez `python agent_git.py` pour un assistant qui vérifie que vous ne publiez rien de sensible.

---

## 🎓 Apprentissage

Si vous voulez comprendre comment tout fonctionne, lisez :
- `EXPLICATION_CODE.md` — Le code expliqué comme si vous aviez 5 ans
- `APPRENDRE_A_IA.md` — Comment faire apprendre l'IA (mémoire + documents)
- `AGENT_PDF_WORD_GUIDE.md` — Comment lire PDF et Word

---

## 📝 License

Projet personnel et éducatif. Utilisez-le librement pour votre usage privé.
