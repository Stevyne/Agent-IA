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
| 🧠 **Mémoire (conversation)** | ✅ | Se souvient de vos conversations entre sessions |
| 🧠 **Mémoire vectorielle** | ✅ | Souvenirs à long terme : nom, préférences, projets (illimité) |
| 📄 **RAG Documents** | ✅ | Lit et fouille vos PDF, Word, TXT |
| 🌐 **Recherche web** | ✅ | Recherche en temps réel sur DuckDuckGo (si connecté) |
| 🎭 **Personnalités** | ✅ | 8 personnalités : Assistant, Professeur, Développeur, Coach, Poète, Sarcastic, Scientifique, Enfant |
| 🤖 **Détection auto personnalité** | ✅ | Change de ton automatiquement selon vos questions |
| 🧮 **Bac à sable Python** | ✅ | Exécute du code Python sécurisé : calculs complexes, graphiques, analyses de données |
| 📅 **Agenda / TODO** | ✅ | Gère vos tâches, rappels et liste de courses dans un fichier local |
| 🔍 **Pipeline Vision → Analyse** | ✅ | Uploadez une image de données → l'agent extrait les chiffres et les analyse avec Python |
| 📡 **API REST** | ✅ | Accédez à l'agent depuis n'importe quel appareil sur votre réseau local (téléphone, tablette, autre PC) |
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

### 6. (Optionnel) Recherche web — DuckDuckGo

Pour que l'agent puisse chercher des informations à jour sur Internet (météo, actualités, cours boursiers) :
```bash
pip install duckduckgo-search
```

> **Gratuit, sans clé API, sans compte.** Seule la requête de recherche part sur Internet (ex: `"météo Paris"`). Votre conversation reste 100% locale.

### 7. (Optionnel) Bac à sable Python — Calculs & Graphiques

Pour que l'agent puisse exécuter du code Python (calculs complexes, graphiques matplotlib, analyses statistiques) :
```bash
pip install matplotlib numpy pandas
```

> Le bac à sable est **sécurisé** : pas d'accès au système, au réseau, ou à vos fichiers personnels. Les graphiques s'affichent directement dans l'interface.

### 8. (Optionnel) Mémoire vectorielle (souvenirs)

Pour que l'agent se souvienne de faits précis sur vous à long terme (prénom, projets, préférences) :
```bash
pip install sentence-transformers
```

> Le modèle `all-MiniLM-L6-v2` (~80 Mo) se télécharge automatiquement au premier lancement. Vos souvenirs sont stockés dans `chroma_souvenirs/` (exclu de Git).

### 9. (Optionnel) Agenda / TODO — natif

L'agenda fonctionne sans installation supplémentaire. Les tâches sont stockées dans `agenda.json` (exclu de Git).

### 10. (Optionnel) API REST — accès depuis d'autres appareils

Pour accéder à l'agent depuis votre téléphone, tablette, ou un autre PC sur le réseau local :
```bash
pip install fastapi uvicorn python-multipart
```

> Le serveur API expose l'agent via HTTP sur votre réseau Wi-Fi. **Ne pas exposer sur Internet** sans sécurisation.

### 11. (Optionnel) Recherche dans documents — ChromaDB

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

### Serveur API REST (accès depuis téléphone/autre PC)
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```
Ouvrez ensuite `http://localhost:8000/docs` pour tester, ou accédez depuis un autre appareil sur `http://VOTRE_IP:8000/chat`.

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
│   ├── agent_git.py              ← Terminal : assistant publication GitHub
│   └── api_server.py             ← API REST : serveur FastAPI pour accès multi-appareils
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
│   ├── GUIDE_PERSONNALITES.md   ← Guide personnalités (manuel + auto-détection)
│   ├── GUIDE_BAC_A_SABLE.md    ← Guide exécution de code Python sécurisée
│   ├── GUIDE_AGENDA.md         ← Guide agenda / TODO list
│   ├── GUIDE_MEMOIRE_VECTORIELLE.md ← Guide mémoire vectorielle (souvenirs long terme)
│   ├── GUIDE_PIPELINE.md         ← Guide pipeline Vision → Analyse de données
│   └── IDEES_AMELIORATIONS.md   ← Feuille de route futures fonctionnalités
│
├── ⚙️ CONFIGURATION
│   ├── README.md                 ← Ce fichier (vitrine GitHub)
│   ├── requirements.txt          ← Dépendances Python
│   ├── personnalites.json       ← Fichier des personnalités (personnalisable)
│   └── .gitignore              ← Fichiers exclus de Git (sécurité)
│
├── 📁 DOSSIERS DE TRAVAIL (créés automatiquement, ignorés par Git)
│   ├── documents/              ← Vos PDF, Word, TXT privés (🔒 jamais publié)
│   ├── outputs/                ← Documents générés par l'IA (🔒 jamais publié)
│   ├── chroma_db_docs/         ← Base de données vectorielle (🔒 jamais publié)
│   ├── memory*.json            ← Mémoires de conversation (🔒 jamais publié)
│   ├── chroma_souvenirs/       ← Mémoire vectorielle long terme (🔒 jamais publié)
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
| **🌐 Activer recherche web** | Cochez pour chercher des infos à jour sur Internet (DuckDuckGo) |
| **🤖 Détection auto personnalités** | Cochez pour que l'IA change de ton selon vos questions |
| **🎭 Personnalité** | Choisissez manuellement (si auto désactivée) ou laissez la détection auto choisir |
| **🌐 Connexion Internet** | Indicateur : vert (OK) ou orange (hors ligne) |
| **🔊 Lire les réponses** | Cochez pour entendre l'IA parler à voix haute |
| **🎤 Activer le micro** | Cochez pour faire apparaître le bouton **"Parler maintenant"** |
| **🎙️ Parler maintenant** | Cliquez, parlez, l'IA transcrit et répond automatiquement |
| **🗑️ Nouvelle conversation** | Efface l'historique et recommence à zéro |
| **📁 Documents créés** | Liste les fichiers que l'IA a générés dans `outputs/` |

### Exemples de requêtes

```markdown
# Conversation simple (🎭 Assistant par défaut)
Vous > Quelle heure est-il ?
Agent > Il est lundi 20 juin 2026, 14 heures 30.

# Analyse d'image
[Uploader facture_scan.jpg]
Vous > Extrais tout le texte visible
Agent > Facture n°104 — Date : 15/06/2026 — Montant : 1240,00 € TTC...

# Recherche web (🌐 connexion Internet requise)
[Cocher "Activer recherche web"]
Vous > Quel temps fait-il à Paris aujourd'hui ?
Agent > [recherche web : météo Paris] D'après les résultats, il fait 24°C...

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

# Bac à sable Python (calculs & graphiques)
Vous > Simule 1000 lancers de dé et affiche un histogramme
Agent > [exécute Python + matplotlib]
     📊 Graphique généré : outputs/sandbox/figure_1.png
     [L'histogramme s'affiche directement dans le chat]

Vous > Calcule la moyenne, médiane, écart-type de : 12, 15, 18, 22, 5, 9, 30
Agent > [exécute numpy]
     Moyenne : 15.8, Médiane : 15.0, Écart-type : 8.3

Vous > Crée un graphique en barres avec les ventes : Janvier 120, Février 150, Mars 110
Agent > [exécute matplotlib]
     📊 Graphique en barres généré

# Pipeline Vision → Analyse (🔍 auto-détecté)
[Uploader image_tableau.png avec des chiffres]
Vous > "Fais un graphique en barres avec les données de cette image"
Agent > 🔍 Extraction des données de l'image...
     [LLaVA extrait : "Mois,Ventes\nJanvier,120\nFévrier,150\nMars,110"]
Agent > [exécute Python avec matplotlib]
     📊 Graphique en barres généré : outputs/sandbox/figure_1.png
     [Image affichée dans le chat]
     Moyenne : 126.7, Max : 150 (Février)

Vous > "Calcule la moyenne des montants sur cette facture"
[Uploader facture.png]
Agent > 🔍 Extraction des données...
     [LLaVA extrait les montants : 1240, 850, 3200]
Agent > [exécute Python]
     Moyenne : 1763.33 €, Total : 5290 €

# Agenda / TODO (📅 natif, pas d'installation)
Vous > Rappelle-moi d'appeler le dentiste demain à 14h
Agent > ✅ Tâche ajoutée : "Appeler le dentiste" (demain, priorité normale)

Vous > Ajoute "Acheter du lait" à ma liste de courses avec priorité haute
Agent > ✅ Tâche ajoutée : "Acheter du lait" (priorité haute)

Vous > Que dois-je faire aujourd'hui ?
Agent > 📋 Vos tâches :
     1. ⬜ Acheter du lait [haute]
     2. ⬜ Appeler le dentiste (demain 14h)

Vous > J'ai acheté le lait
Agent > ✅ Tâche "Acheter du lait" marquée comme faite.

# Personnalités auto-détectées (🤖 Détection auto activée)
Vous > Apprends-moi les boucles while
🎭 👨‍🏫 Professeur détecté
Agent > Imagine que tu comptes des bonbons dans un bocal...

Vous > Écris-moi un script Python
🎭 👨‍💻 Développeur détecté
Agent > for i in range(10): print(i)

Vous > Raconte-moi une blague sur les informaticiens
🎭 😏 Sarcastic détecté
Agent > Oh, une blague ? Pourquoi les programmeurs confondent-ils Noël et Halloween ?

# Mémoire vectorielle (🧠 souvenirs automatiques)
Vous > Mon chat s'appelle Rouxy et il a 3 ans
Agent > Quel joli nom ! Rouxy est un chat de 3 ans.
🧠 2 souvenir(s) stocké(s).

... (50 conversations plus tard, l'agent a résumé 3 fois) ...

Vous > Comment s'appelle mon chat ?
[Agent cherche dans ses souvenirs vectoriels]
Agent > Votre chat s'appelle Rouxy ! 🐱

Vous > Quel projet je travaille en ce moment ?
[Agent cherche dans ses souvenirs]
Agent > Vous travaillez sur votre jardinage automatisé avec Arduino.

# API REST (📡 depuis téléphone/autre PC)
# 1. Lancer le serveur : uvicorn api_server:app --host 0.0.0.0 --port 8000
# 2. Depuis un autre appareil sur le même Wi-Fi :

curl -X POST http://192.168.1.10:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quelle heure est-il ?"}'
# Réponse : {"reply": "Il est lundi 20 juin 2026, 14 heures 30.", ...}

# Depuis Python (téléphone, autre PC) :
import requests
r = requests.post("http://192.168.1.10:8000/chat", json={"message": "Calcule 15 * 4"})
print(r.json()["reply"])  # 15 × 4 = 60

# Avec image (base64) :
with open("photo.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
requests.post("http://192.168.1.10:8000/chat",
    json={"message": "Décris cette image", "image_b64": b64})
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
| **Recherche web grisée** | Vérifiez votre connexion Internet (l'indicateur dans la sidebar). Installez `pip install duckduckgo-search`. |
| **Personnalité ne change pas** | Vérifiez que vous avez bien activé "Détection auto" ou changé le menu manuel. L'IA ne change pas de rôle en pleine réponse. |
| **La personnalité auto est fausse** | La détection est basée sur des mots-clés. Ajoutez des mots explicites (ex: "apprends-moi", "code Python", "blague"). Vous pouvez créer vos propres règles dans `personnalites.json`. |
| **Bac à sable : "élément interdit"** | Le code contenait une commande système (os, subprocess, socket, etc.) ou un mot-clé bloqué. Demandez à l'IA de réécrire le code sans ces éléments. |
| **Bac à sable : timeout / lent** | Le code a dépassé 30 secondes (boucle infinie ?). Vérifiez que matplotlib, numpy sont installés (`pip install matplotlib numpy`). |
| **Agenda introuvable** | Le fichier `agenda.json` est créé automatiquement au premier ajout. Si vous ne le voyez pas, demandez à l'agent : *"Ajoute une tâche test"*. |
| **L'agent ne trouve pas ma tâche** | L'agent identifie les tâches par leur ID unique (ex: `t_1234_5678`). Si vous ne le connaissez pas, dites le **nom** exact : *"Marque 'Appeler le dentiste' comme fait"*. L'agent peut faire une recherche partielle. |
| **Mémoire vectorielle : pas de souvenirs** | Vérifiez que `sentence-transformers` est installé (`pip install sentence-transformers`). Le modèle `all-MiniLM-L6-v2` (~80 Mo) se télécharge au premier lancement. |
| **L'agent oublie mes souvenirs** | La mémoire vectorielle fonctionne par similarité. Si vous posez une question très différente de ce que vous avez dit avant, l'agent peut ne pas trouver le souvenir. Essayez avec des mots plus proches. |
| **Pipeline Vision : "aucune donnée extraite"** | L'image est peut-être floue, le texte est trop petit, ou LLaVA ne reconnaît pas les chiffres. Essayez avec une image plus nette (contraste élevé, texte noir sur blanc). |
| **Pipeline Vision : données erronées** | LLaVA est un modèle de vision, pas un OCR professionnel. Il peut confondre des chiffres (ex: `120` → `128`). Vérifiez toujours les données extraites avant d'agir sur elles. |
| **Pipeline Vision : le graphique est vide** | L'extraction a peut-être échoué ou les données n'étaient pas au format attendu. Demandez "Extrais les données brutes d'abord" pour vérifier. |
| **API REST : "Connexion refusée"** | Vérifiez que `uvicorn api_server:app --host 0.0.0.0 --port 8000` est lancé. Vérifiez que vous utilisez la bonne IP (`ipconfig` sur Windows). |
| **API REST : lenteur** | L'API partage le GPU avec l'interface web. Ne les utilisez pas simultanément. |
| **API REST : pas d'accès depuis l'extérieur** | Par défaut, l'API est uniquement sur votre réseau local (Wi-Fi). Ne la forward pas sur Internet sans sécurisation (authentification, HTTPS). |

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
- **DuckDuckGo Search** : recherche web gratuite (https://github.com/deedy5/duckduckgo-search)
- **Matplotlib** : graphiques Python (https://matplotlib.org)
- **NumPy** : calculs scientifiques (https://numpy.org)
- **Pandas** : manipulation de données (https://pandas.pydata.org)
- **Sentence-Transformers** : embeddings vectoriels pour la mémoire long terme (https://www.sbert.net)
- **Streamlit** : interface web (https://streamlit.io)

---

**Bonne conversation avec votre agent !** 🤖💬
