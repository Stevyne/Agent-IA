# 🤖🌟 Agent IA Local Ultime — Suite Complète 100% Offline

> **Votre assistant intelligence artificielle complet, qui tourne entièrement sur votre PC.**  
> Aucune donnée ne quitte votre ordinateur. Conversation, vision, voix, documents, mémoire — tout est local.

---

## ✨ Ce que fait ce projet

Cette suite d'agents IA vous permet de discuter avec une intelligence artificielle, de lui montrer des images, de lui faire lire vos documents, de l'entendre parler, et même de lui dicter vos questions — **sans jamais envoyer quoi que ce soit sur Internet** (ou avec des options 100% offline).

| Capacité | Disponible | Description |
|----------|------------|-------------|
| 💬 **Chat texte** | ✅ | Conversation avec modèle local (Qwen 2.5) |
| 🧮 **Outils** | ✅ | Calculatrice, horloge, recherche dans documents |
| 🖼️ **Vision** | ✅ | Analyse d'images, OCR, description de photos |
| 🔊 **Voix (TTS)** | ✅ | L'IA vous répond à voix haute (pyttsx3 ou Piper naturel) |
| 🎤 **Micro (STT)** | ✅ | Parlez à l'IA (Faster-Whisper offline ou Google) |
| 📝 **Export documents** | ✅ | Génère TXT, CSV, JSON, Word, PDF dans `outputs/` |
| 🧠 **Mémoire** | ✅ | Se souvient de vos conversations entre sessions |
| 📄 **RAG Documents** | ✅ | Lit et fouille vos PDF, Word, TXT |
| 🌐 **Recherche web** | ✅ | Recherche en temps réel sur DuckDuckGo (si connecté) |
| 🎭 **Personnalités** | ✅ | 8 personnalités : Assistant, Professeur, Développeur, Coach, Poète, Sarcastic, Scientifique, Enfant |
| 🤖 **Détection auto personnalité** | ✅ | Change de ton automatiquement selon vos questions |
| 🛡️ **GitHub Safe** | ✅ | Assistant pour publier votre code sans fuiter vos données |

---

## 🖥️ Prérequis matériels

Ce projet est optimisé pour les PC modestes avec un **GPU NVIDIA ancien** (GTX 10xx).

| Configuration | Minimum | Recommandé |
|---------------|---------|------------|
| **Processeur** | Intel i5 / Ryzen 5 (4 cœurs) | i5-10xxx+ / Ryzen 5 3600+ |
| **RAM** | 16 Go | 32 Go |
| **GPU** | NVIDIA GTX 1060 **6 Go** | GTX 1070/1080 **8 Go** ou 1080 Ti **11 Go** |
| **Stockage** | SSD 128 Go | SSD 256 Go+ |
| **OS** | Windows 10/11, Linux (Ubuntu) | Linux pour meilleures perfs CUDA |

> ⚠️ **Important** : les modèles multimodaux (vision) et vocaux consomment de la VRAM. Avec un GTX 1060 6 Go, privilégiez les modèles 3B (Qwen 3B, Moondream, LLaVA-Phi3).

---

## 📦 Installation complète

### 1. Prérequis logiciels

- **Python 3.11+** : https://www.python.org/downloads/
- **Ollama** : https://ollama.com (téléchargez et installez pour votre OS)
- **Drivers NVIDIA** à jour : https://www.nvidia.fr/drivers/

### 2. Cloner et préparer l'environnement

```bash
# Cloner le projet (ou créer votre dossier)
git clone https://github.com/VOTRE_NOM/mon-agent-ia.git
cd mon-agent-ia

# Créer l'environnement virtuel Python
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux / macOS :
source venv/bin/activate

# Installer toutes les dépendances
pip install -r requirements.txt
```

### 3. Télécharger les modèles Ollama

```bash
# Modèle texte (obligatoire)
ollama pull qwen2.5:3b

# Modèle vision (optionnel, pour l'analyse d'images)
ollama pull llava-phi3

# Alternative vision très légère (GTX 1060 6 Go)
# ollama pull moondream
```

> **Choix du modèle** : `qwen2.5:3b` pour 6 Go VRAM, `qwen2.5:7b` pour 8+ Go VRAM.

### 4. (Optionnel) Voix naturelle offline — Piper-TTS

Pour une voix humaine réaliste sans Internet :

1. Téléchargez **Piper** sur https://github.com/rhasspy/piper/releases
2. Dézippez dans `models/piper/` (créez le dossier)
3. Téléchargez une voix française (`.onnx` + `.onnx.json`) : https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/fr
4. Placez les deux fichiers dans `models/piper/`

### 5. (Optionnel) Reconnaissance vocale offline — Faster-Whisper

Déjà installé via `pip install -r requirements.txt`. Le modèle `tiny` (39 Mo) se télécharge automatiquement au premier lancement.

### 6. (Optionnel) Recherche dans documents — ChromaDB

Placez vos fichiers `.pdf`, `.docx`, `.txt` dans un dossier `documents/` puis lancez une fois :
```bash
python agent_documents.py
```
Cela crée la base de données vectorielle `chroma_db_docs/`.

---

## 🚀 Lancer les agents

### Interface web ultime (recommandé)
```bash
streamlit run app_ultime.py
```
Ouvre automatiquement `http://localhost:8501` dans votre navigateur.

### Interface web hybride (texte + vision + documents)
```bash
streamlit run app_hybride_v2.py
```

### Agent en ligne de commande (texte + outils)
```bash
python agent_terminal.py
```

### Agent avec mémoire persistante
```bash
python agent_avec_memoire.py
```

### Agent lecteur de documents (PDF, Word, TXT)
```bash
python agent_documents.py
```

### Agent vocal offline (Piper + Whisper)
```bash
python agent_vocal_offline.py
```

### Agent vision (analyse d'images)
```bash
python agent_images.py
```

### Assistant GitHub (publication sécurisée)
```bash
python agent_git.py
```

---

## 📁 Structure du projet

```
mon-agent-ia/
│
├── 🤖 AGENTS (programmes principaux)
│   ├── app_ultime.py              ← 🌟 TOUT-EN-UN (web : texte + vision + voix + micro + documents + mémoire)
│   ├── app_hybride_v2.py         ← Web : texte + vision + documents + mémoire
│   ├── app_hybride.py            ← Web : texte + vision + mémoire
│   ├── app_web.py                ← Web : chat simple Streamlit
│   ├── agent_terminal.py         ← Terminal : chat simple
│   ├── agent_avec_memoire.py     ← Terminal : chat + mémoire persistante
│   ├── agent_documents.py        ← Terminal : lecture PDF/Word/TXT + recherche
│   ├── agent_images.py           ← Terminal : analyse d'images (vision)
│   ├── agent_vocal.py            ← Terminal : voix pyttsx3 + micro Google
│   ├── agent_vocal_offline.py    ← Terminal : voix Piper + micro Whisper (offline)
│   └── agent_git.py              ← Terminal : assistant publication GitHub
│
├── 📚 GUIDES (documentation)
│   ├── GUIDE_INSTALLATION.md     ← Installation pas à pas
│   ├── EXPLICATION_CODE.md       ← Cours : comment fonctionnent les codes
│   ├── APPRENDRE_A_IA.md         ← Comment faire apprendre l'IA (mémoire + RAG)
│   ├── AGENT_PDF_WORD_GUIDE.md  ← Guide lecture PDF/Word
│   ├── GUIDE_VOIX.md             ← Guide voix (TTS/STT)
│   ├── GUIDE_VOIX_OFFLINE.md    ← Guide voix 100% offline (Piper + Whisper)
│   ├── GUIDE_IMAGES.md          ← Guide analyse d'images
│   ├── GUIDE_DOCUMENTS.md        ← Guide création de documents
│   ├── GUIDE_GITHUB.md          ← Guide publication GitHub
│   └── IDEES_AMELIORATIONS.md   ← Feuille de route futures fonctionnalités
│
├── ⚙️ CONFIGURATION
│   ├── README.md                 ← Ce fichier (vitrine GitHub)
│   ├── requirements.txt          ← Dépendances Python
│   └── .gitignore              ← Fichiers exclus de Git (sécurité)
│
├── 📁 DOSSIERS DE TRAVAIL (créés automatiquement, ignorés par Git)
│   ├── documents/              ← Vos PDF, Word, TXT privés (🔒 jamais publié)
│   ├── outputs/                ← Documents générés par l'IA (🔒 jamais publié)
│   ├── chroma_db_docs/         ← Base de données vectorielle (🔒 jamais publié)
│   ├── memory*.json            ← Mémoires de conversation (🔒 jamais publié)
│   ├── models/                 ← Modèles locaux (Piper, etc.)
│   └── venv/                   ← Environnement Python (🔒 jamais publié)
│
└── 🔒 SÉCURITÉ
    └── .gitignore contient : documents/, outputs/, memory*.json, chroma_db*, venv/
```

---

## 🎮 Utilisation rapide de `app_ultime.py` (l'interface web complète)

### La sidebar (barre latérale)

| Élément | Fonction |
|---------|----------|
| **📁 Uploader une image** | Glissez une photo → l'IA passe en mode **vision** et peut la décrire |
| **🧠 Mémoire persistante** | Cochez pour que l'IA se souvienne de vos conversations d'hier |
| **📄 Recherche documents** | Cochez si vous avez indexé des fichiers dans `documents/` |
| **🔊 Lire les réponses** | Cochez pour entendre l'IA parler à voix haute |
| **🎤 Activer le micro** | Cochez pour faire apparaître le bouton **"Parler maintenant"** |
| **🎙️ Parler maintenant** | Cliquez, parlez, l'IA transcrit et répond automatiquement |
| **🗑️ Nouvelle conversation** | Efface l'historique et recommence à zéro |
| **📁 Documents créés** | Liste les fichiers que l'IA a générés dans `outputs/` |

### Exemples de requêtes

```markdown
# Conversation simple
Vous > Quelle heure est-il ?
Agent > Il est lundi 20 juin 2026, 14 heures 30.

# Analyse d'image
[Uploader facture_scan.jpg]
Vous > Extrais tout le texte visible
Agent > Facture n°104 — Date : 15/06/2026 — Montant : 1240,00 € TTC...

# Recherche documentaire
[Cocher "Recherche documents"]
Vous > Que dit mon contrat sur la clause de confidentialité ?
Agent > Dans contrat.docx (paragraphe 12) : "Le salarié s'engage à garder confidentiel..."

# Création de document
Vous > Résume notre conversation et sauvegarde-la dans un PDF
Agent > J'ai créé le résumé : outputs/resume_conversation.pdf

# Question de suivi sur image
Vous (après upload) > De quelle couleur est l'objet à droite ?
Agent > L'objet à droite est un vase bleu.

# Voix (avec micro activé)
[🎙️ Parler maintenant]
Vous (voix) > "Calcule 15 fois 4"
Agent (voix) > 15 multiplié par 4 égale 60.
```

---

## 🛡️ Sécurité & Confidentialité

- **100% offline** : vos conversations, vos documents, vos images ne quittent jamais votre PC (sauf si vous utilisez le micro Google SpeechRecognition, qui envoie un court extrait audio à Google).
- **Fichiers privés exclus** : le dossier `documents/`, `outputs/`, `memory*.json`, `chroma_db_docs/` sont dans `.gitignore` — ils ne seront **jamais** publiés sur GitHub par accident.
- **Bac à sable** : l'agent ne peut créer de fichiers que dans `outputs/`. Aucun accès à vos fichiers système.
- **GitHub Safe** : lancez `python agent_git.py` pour un assistant qui vérifie vos commits avant publication.

---

## 🎓 Apprentissage & Cours

Ce projet est aussi un **cours d'informatique**. Les fichiers `GUIDE_*.md` et `EXPLICATION_*.md` expliquent :
- Comment fonctionne le code (ligne par ligne, analogies simples)
- Comment faire apprendre l'IA (mémoire + RAG)
- Comment publier sur GitHub en sécurité
- Les idées d'améliorations futures

Lisez `EXPLICATION_CODE.md` pour comprendre le fonctionnement comme si vous n'aviez jamais programmé.

---

## 🐛 Dépannage rapide

| Problème | Solution |
|----------|----------|
| **Ollama ne répond pas** | Vérifiez qu'Ollama est lancé (icône dans la barre des tâches). Tapez `ollama --version` dans un terminal. |
| **Out of memory / crash** | Votre modèle est trop gros pour votre VRAM. Baissez vers `qwen2.5:3b` ou `moondream`. Fermez les jeux/navigateurs. |
| **L'IA ne voit pas mon image** | Vérifiez que vous avez bien `llava-phi3` ou `moondream` installé (`ollama list`). |
| **La voix ne marche pas** | Vérifiez `pip install pyttsx3`. Pour Piper, vérifiez que `models/piper/` contient le binaire et la voix `.onnx`. |
| **Le micro ne comprend rien** | Parlez près du micro, dans un endroit calme. Vérifiez que `pyaudio` est installé. |
| **ChromaDB introuvable** | Lancez une fois `python agent_documents.py` pour créer la base. |
| **Piper-TTS introuvable** | Vérifiez le chemin `models/piper/piper.exe` (Windows) ou `models/piper/piper` (Linux). |

---

## 📜 Licence & Utilisation

Projet personnel et éducatif. Utilisez-le librement pour votre usage privé. Les modèles de langage (Qwen, LLaVA, Moondream) et les bibliothèques utilisées ont leurs propres licences open-source.

---

## 🙏 Crédits & Bibliothèques

- **Ollama** : moteur d'inférence local (https://ollama.com)
- **Qwen** : modèle de langage Alibaba (https://qwenlm.github.io)
- **LLaVA** : modèle vision-langage (https://llava-vl.github.io)
- **Moondream** : modèle vision léger (https://moondream.ai)
- **Piper** : synthèse vocale offline (https://github.com/rhasspy/piper)
- **Faster-Whisper** : reconnaissance vocale offline (https://github.com/SYSTRAN/faster-whisper)
- **ChromaDB** : base de données vectorielle (https://www.trychroma.com)
- **Streamlit** : interface web (https://streamlit.io)

---

**Bonne conversation avec votre agent !** 🤖💬
