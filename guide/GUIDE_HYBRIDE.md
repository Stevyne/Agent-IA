# 🤖👁️ Guide : Agent Hybride Web (Texte + Vision)

> **Date** : 18 juin 2026  
> **Objectif** : Une interface web unique qui discute avec vous, analyse vos images, calcule, donne l'heure, et se souvient de vos conversations.

---

## 🎭 Qu'est-ce qu'un "agent hybride" ?

Jusqu'ici, vous aviez **plusieurs agents séparés** :
- `agent_terminal.py` : discute en texte (Qwen 2.5)
- `agent_images.py` : regarde les images (LLaVA / Moondream)
- `agent_vocal_offline.py` : parle et écoute (Piper + Whisper)

L'**agent hybride** est un **chef d'orchestre** qui réunit tout dans une **interface web** (Streamlit). Il détecte automatiquement ce que vous voulez :

| Vous faites... | L'agent détecte... | Il utilise... | Pour... |
|---|---|---|---|
| **Tapez du texte** | Mode texte | `qwen2.5:3b` + outils | Répondre, calculer, donner l'heure |
| **Uploader une image** | Mode vision | `llava-phi3` | Décrire, lire l'OCR, analyser la photo |
| **Texte + image** | Mode vision | `llava-phi3` | Répondre en se basant sur l'image |
| **Redemandez sur l'image précédente** | Mode vision (mémoire image) | `llava-phi3` + historique | Répondre à une question de suivi |

> **Analogie** : c'est comme un hôpital avec un **triage**. Le médecin généraliste (Qwen) gère les questions classiques. Le radiologue (LLaVA) examine les images. L'agent hybride vous dirige automatiquement vers le bon spécialiste.

---

## 🏗️ Architecture du système hybride

```
┌─────────────────────────────────────┐
│         Interface Streamlit           │
│   (chat, upload image, sidebar)      │
└─────────────┬───────────────────────┘
              │
      ┌───────┴───────┐
      │   ROUTEUR     │  Détecte : texte seul ? ou image présente ?
      └───────┬───────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌────────────┐   ┌──────────────┐
│  Modèle    │   │  Modèle      │
│  TEXTE     │   │  VISION      │
│  qwen2.5   │   │  llava-phi3  │
│  (GPU)     │   │  (GPU)       │
└────────────┘   └──────────────┘
     │                 │
     ▼                 ▼
┌────────────┐   ┌──────────────┐
│  Outils    │   │  Analyse     │
│  calcul    │   │  d'image     │
│  heure     │   │  OCR visuel  │
│  docs(RAG) │   │  description │
└────────────┘   └──────────────┘
```

---

## ⚠️ Contraintes matérielles (votre GTX 10xx)

L'agent hybride peut **charger les deux modèles** (texte + vision), mais pas simultanément dans le GPU. Heureusement, Ollama gère la mémoire : il décharge le modèle inutilisé quand on switch.

| Modèle | VRAM estimée | Comportement avec Ollama |
|---|---|---|
| `qwen2.5:3b` (texte) | ~2-3 Go | Chargé quand vous discutez |
| `llava-phi3` (vision) | ~4-5 Go | Chargé quand vous envoyez une image |

> **La première réponse après un switch** peut être plus lente (2-3 secondes) car Ollama doit charger le nouveau modèle en GPU. Ensuite, c'est fluide.

---

## 📦 Installation

Vous avez déjà installé la plupart des bibliothèques. Il manque juste :

```bash
pip install streamlit pillow
ollama pull qwen2.5:3b     # si pas déjà fait
ollama pull llava-phi3      # ou moondream pour plus léger
```

> **Optionnel** : pour la mémoire persistante, rien de plus à installer.  
> **Optionnel** : pour la recherche dans documents, assurez-vous d'avoir `chromadb` + un dossier `documents/` (voir `agent_documents.py`).

---

## 🚀 Lancer l'interface

```bash
streamlit run app_hybride.py
```

Votre navigateur s'ouvre sur `http://localhost:8501`.

---

## 🎮 Comment utiliser l'interface

### La barre latérale (Sidebar)

| Élément | À quoi ça sert ? |
|---|---|
| **📁 Uploader une image** | Sélectionnez une photo, capture d'écran, scan PDF, graphique... |
| **🧠 Mémoire persistante** | Cochez pour que l'IA se souvienne de vos conversations (fichier `memory.json`) |
| **📄 Recherche documents** | Cochez si vous avez un dossier `documents/` indexé (ChromaDB) |
| **🗑️ Nouvelle conversation** | Efface l'historique et recommence à zéro |
| **ℹ️ Infos** | Voir quels modèles sont utilisés |

### La zone de chat

**1. Conversation texte normale**
```
Vous > Quelle heure est-il ?
[Agent détecte : mode TEXTE → qwen2.5]
Agent > Il est 19 juin 2026, 16 heures 42.
[Outil: heure_actuelle → ...]
```

**2. Analyse d'image**
```
[Uploader une image dans la sidebar]
Vous > Décris ce que tu vois
[Agent détecte : image présente → llava-phi3]
Agent > C'est une photographie d'un chat roux allongé...
```

**3. Question de suivi sur l'image**
```
Vous > De quelle couleur est le canapé ?
[Agent détecte : image mémorisée → llava-phi3 avec historique]
Agent > Le canapé est bleu marine.
```

**4. Retour au texte**
```
Vous > Calcule 15 * 4
[Agent détecte : pas d'image → qwen2.5 avec outil calcul]
Agent > 15 × 4 = 60.
```

> **Astuce** : l'image reste "chargée" dans la sidebar jusqu'à ce que vous en uploadiez une autre ou que vous cliquiez sur "Nouvelle conversation". Vous pouvez poser plusieurs questions sur la même image.

---

## 🧠 La mémoire persistante (optionnelle)

Quand la checkbox **"Mémoire persistante"** est cochée :
- L'agent sauvegarde l'historique dans `memory_hybride.json`
- Au prochain lancement, il relit ce fichier et se souvient de vous
- Les images ne sont pas sauvegardées (trop lourdes), seulement le texte des conversations

> **Sécurité** : `memory_hybride.json` est dans le `.gitignore` pour ne pas être publié sur GitHub.

---

## 📚 La recherche documentaire (optionnelle)

Quand la checkbox **"Recherche documents"** est cochée :
- L'agent vérifie si vous avez un dossier `documents/` et une base ChromaDB
- Si oui, il ajoute l'outil `rechercher_documents` au modèle texte
- Vous pouvez demander : *"Que dit mon contrat sur la clause de confidentialité ?"*
- L'agent fouille dans vos PDF/Word/TXT et cite les sources

> **Prérequis** : avoir lancé `agent_documents.py` au moins une fois pour créer la base `chroma_db_docs/`, ou copier/coller la logique RAG de `agent_documents.py`.

---

## ⚠️ Limites et comportements

| Situation | Comportement | Explication |
|---|---|---|
| **Image uploadée + question texte** | Le modèle **vision** répond en se basant sur l'image ET le texte | C'est le cerveau qui voit le mieux |
| **Image uploadée, question hors sujet** | Le modèle vision répond quand même (il voit l'image) | Il peut dire *"Je ne vois pas de lien avec votre question"* |
| **Question de suivi sans image** | Le modèle texte prend le relais. Il ne voit plus l'image. | Seul le texte de la description reste dans l'historique. |
| **Switch lent** | La première réponse après un changement de modèle peut prendre 2-3s | Ollama décharge/charge le modèle dans le GPU. |
| **Plusieurs images** | La sidebar n'accepte qu'une image à la fois. | Streamlit `file_uploader` limite à 1 fichier. Pour comparer 2 images, décrivez-les séparément. |

---

## 🎓 Extensibilité : ajouter d'autres modèles

Vous pouvez modifier `app_hybride.py` pour ajouter :
- **Modèle audio** : détecter un fichier audio uploadé → envoyer à Whisper (transcription) → puis modèle texte
- **Modèle vocal** : bouton "Parler" qui enregistre le micro (comme `agent_vocal_offline.py`)
- **Pipeline avancé** : image → modèle vision (OCR) → modèle texte (analyse des données extraites)

---

**Bon chat visuel !** 🎉
