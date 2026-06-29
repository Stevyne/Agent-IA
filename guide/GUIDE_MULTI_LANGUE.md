# 🌍 Guide Architecture : Rendre votre Agent IA 100% Multi-langue (i18n)

> **Objectif** : Transformer votre agent IA (actuellement en français) en un système polyglotte complet (Français, Anglais, Espagnol, Allemand, etc.), couvrant l'interface Streamlit, les prompts, les outils, le vocal (STT/TTS), la mémoire RAG et l'API REST.

---

## 🏠 L'analogie du Restaurant International

Jusqu'ici, votre restaurant fonctionnait exclusivement en français : le **serveur** (Python/Streamlit) parlait français, le **chef cuisinier** (Ollama/Qwen 2.5) lisait des recettes en français, et le **standardiste** (Voix) ne connaissait que la langue de Molière.

Pour ouvrir votre restaurant au monde entier, voici ce que nous allons mettre en place :

| Élément du Restaurant | Équivalent technique | Transformation Multi-langue |
|---|---|---|
| **Le menu & les affiches en salle** | **Interface Streamlit** (`app_ultime.py`) | Un dictionnaire de traduction (`translations.py`) et un sélecteur de langue en direct. |
| **Les consignes données au Chef** | **Ollama & Personnalités** (`system_prompt`) | Injection dynamique de la langue cible pour forcer l'IA à changer de langue de réponse. |
| **Les ustensiles de la cuisine** | **Outils (Tool Calling)** (`heure`, `recherche`) | Adaptation des formats de date et des paramètres de recherche web selon la région. |
| **Le standard téléphonique** | **Voix (STT & TTS)** (`Whisper`, `Piper/Edge`) | Changement dynamique du modèle vocal (accent natif) et de la langue d'écoute du micro. |
| **Les archives de la bibliothèque** | **Mémoire Vectorielle RAG** (`ChromaDB`) | Adoption d'un modèle d'embedding multilingue et requêtes croisées (ex: question EN sur doc FR). |
| **Le service de livraison externe** | **API REST** (`api_server.py` / FastAPI) | Ajout d'un paramètre `language` dans les requêtes JSON pour les clients distants. |

---

## 🧱 Architecture Globale du Système Multi-langue

```
┌─────────────────────────────────────────────────────────┐
│              SÉLECTEUR DE LANGUE (Streamlit)            │
│                 [ Français │ English │ Español ]        │
└────────────────────────────┬────────────────────────────┘
                             │ (st.session_state.lang = 'en')
                             ▼
┌─────────────────────────────────────────────────────────┐
│ 1. INTERFACE : Chargement des textes via t("titre")     │
│ 2. OLLAMA    : System prompt += "Answer in English."     │
│ 3. OUTILS    : Recherche Web (kl='en-us'), Date (en_US) │
│ 4. VOIX      : Whisper(lang='en') + EdgeTTS(en-US-Voice)│
│ 5. RAG       : Embedding Multilingue + Prompt RAG en EN │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Pilier 1 : L'Interface Web (Streamlit) — Le système i18n

Pour éviter de mélanger des textes bruts partout dans votre code, nous créons un fichier dédié aux traductions et une petite fonction d'aide `t()`.

### 1.1 Créer le fichier `translations.py`

Créez un nouveau fichier `translations.py` à la racine de votre projet :

```python
# translations.py

TRANSLATIONS = {
    "fr": {
        "app_title": "🤖 Agent IA Ultime",
        "sidebar_title": "⚙️ Configuration",
        "select_lang": "🌍 Langue / Language",
        "select_persona": "🎭 Personnalité",
        "chat_placeholder": "Posez votre question ici...",
        "thinking": "En cours de réflexion...",
        "tts_checkbox": "🗣️ Activer la réponse vocale",
        "err_no_doc": "⚠️ Aucun document trouvé dans le dossier.",
        "button_clear": "🗑️ Effacer l'historique",
        "tool_search": "🔍 Recherche web en cours..."
    },
    "en": {
        "app_title": "🤖 Ultimate AI Agent",
        "sidebar_title": "⚙️ Settings",
        "select_lang": "🌍 Language / Langue",
        "select_persona": "🎭 Personality",
        "chat_placeholder": "Ask your question here...",
        "thinking": "Thinking...",
        "tts_checkbox": "🗣️ Enable voice response",
        "err_no_doc": "⚠️ No documents found in the folder.",
        "button_clear": "🗑️ Clear history",
        "tool_search": "🔍 Web search in progress..."
    },
    "es": {
        "app_title": "🤖 Agente IA Definitivo",
        "sidebar_title": "⚙️ Configuración",
        "select_lang": "🌍 Idioma / Language",
        "select_persona": "🎭 Personalidad",
        "chat_placeholder": "Haz tu pregunta aquí...",
        "thinking": "Pensando...",
        "tts_checkbox": "🗣️ Activar respuesta de voz",
        "err_no_doc": "⚠️ No se encontraron documentos en la carpeta.",
        "button_clear": "🗑️ Borrar historial",
        "tool_search": "🔍 Búsqueda web en curso..."
    }
}

# Dictionnaire pour le nom complet des langues pour l'IA
LANG_NAMES = {
    "fr": "Français",
    "en": "English",
    "es": "Español"
}
```

### 1.2 Intégration dans `app_ultime.py` (Streamlit)

Dans votre script d'interface principale, initialisez le `session_state` et utilisez une fonction `t()` pour récupérer les textes.

```python
import streamlit as st
from translations import TRANSLATIONS, LANG_NAMES

# 1. Initialisation de la langue par défaut dans la boîte à souvenirs
if "lang" not in st.session_state:
    st.session_state.lang = "fr"  # Par défaut en français

# Fonction magique pour obtenir le texte dans la bonne langue
def t(key: str) -> str:
    lang = st.session_state.lang
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)

# --- DEBUT DE L'INTERFACE ---
st.title(t("app_title"))

with st.sidebar:
    st.header(t("sidebar_title"))
    
    # Menu déroulant pour choisir la langue
    # On fait correspondre le choix propre avec le code 'fr', 'en', 'es'
    lang_display = {"fr": "🇫🇷 Français", "en": "🇬🇧 English", "es": "🇪🇸 Español"}
    
    selected_display = st.selectbox(
        t("select_lang"),
        options=list(lang_display.values()),
        index=list(lang_display.keys()).index(st.session_state.lang)
    )
    
    # Mettre à jour la langue dans session_state si l'utilisateur change
    for code, disp in lang_display.items():
        if disp == selected_display:
            if st.session_state.lang != code:
                st.session_state.lang = code
                st.rerun() # Rafraîchit l'interface immédiatement
                
    st.button(t("button_clear"), on_click=lambda: st.session_state.pop("messages", None))

# Curseur de chat
if user_input := st.chat_input(t("chat_placeholder")):
    # La suite de votre logique...
    pass
```

---

## 🧠 Pilier 2 : Le Cerveau IA (Ollama & Personnalités)

Les modèles modernes comme **Qwen 2.5** sont d'excellents polyglottes naturels. Il n'est pas nécessaire de traduire en dur toutes vos fiches de personnalités en 3 ou 4 langues. Il suffit d'**injecter dynamiquement une instruction stricte** à la fin du `system_prompt`.

### 2.1 Adaptation du constructeur de `system_prompt`

Dans votre gestionnaire de personnalités (ex. `agent_personnalites.py` ou directement dans la fonction qui prépare l'appel Ollama) :

```python
from translations import LANG_NAMES

# Exemple d'une définition de personnalité de base en français
PERSONNALITES = {
    "professeur": {
        "nom": "👨‍🏫 Professeur",
        "system_prompt_base": "Tu es un professeur patient qui explique étape par étape avec bienveillance."
    },
    "developpeur": {
        "nom": "👨‍💻 Développeur",
        "system_prompt_base": "Tu es un développeur senior direct. Tu donnes du code propre sans blabla inutile."
    }
}

def get_system_prompt(persona_key: str, current_lang: str) -> str:
    base_prompt = PERSONNALITES[persona_key]["system_prompt_base"]
    target_language_name = LANG_NAMES.get(current_lang, "Français")
    
    # 🎯 INJECTION DYNAMIQUE MULTILINGUE
    # On ajoute une directive forte en anglais (comprise de manière universelle par le LLM)
    prompt_multilangue = (
        f"{base_prompt}\n\n"
        f"--- IMPORTANT --- \n"
        f"You must strictly communicate, think, and respond to the user in this language: {target_language_name}."
    )
    return prompt_multilangue
```

> **Comment ça marche ?** L'IA lit sa fiche de rôle (même rédigée en français), puis voit l'ordre impératif final de répondre en anglais (`English`) ou espagnol (`Español`). Elle appliquera le ton du professeur directement dans la langue demandée !

---

## 🛠️ Pilier 3 : Les Outils & Appels de fonctions (Tool Calling)

Lorsque l'IA utilise des outils (calculer, heure, recherche web), le retour de l'outil doit correspondre au contexte culturel ou linguistique.

### 3.1 L'outil `heure_actuelle` multilingue

Au lieu de renvoyer une date fixe en français ("mercredi 18 juin"), adaptons-la dynamiquement sans dépendre des locales système complexes de Windows/Linux :

```python
import datetime

def heure_actuelle(lang: str = "fr") -> str:
    now = datetime.datetime.now()
    
    if lang == "en":
        return f"Current date and time: {now.strftime('%A, %B %d, %Y, %I:%M:%S %p')}"
    elif lang == "es":
        # Formattage manuel simple ou via bibliothèque babel
        return f"Fecha y hora actual: {now.strftime('%d/%m/%Y %H:%M:%S')}"
    else:
        return f"Date et heure actuelles : {now.strftime('%d/%m/%Y %H:%M:%S')}"
```

### 3.2 L'outil `recherche_web` (DuckDuckGo / Google)

Pour que la recherche web trouve des articles dans la langue de l'utilisateur, passez le paramètre de région adapté :

```python
from duckduckgo_search import DDGS

def recherche_web(query: str, lang: str = "fr") -> str:
    # Correspondance des codes régions pour DuckDuckGo
    region_map = {
        "fr": "fr-fr",
        "en": "us-en",
        "es": "es-es"
    }
    region = region_map.get(lang, "fr-fr")
    
    results = DDGS().text(query, region=region, max_results=3)
    
    if not results:
        err_msg = {"fr": "Aucun résultat.", "en": "No results found.", "es": "No hay resultados."}
        return err_msg.get(lang, "Aucun résultat.")
        
    # Formatage de la synthèse des résultats
    return "\n\n".join([f"**{r['title']}** ({r['href']})\n{r['body']}" for r in results])
```

---

## 🎙️ Pilier 4 : Le Standard Vocal (Voix STT & TTS)

Le module vocal est le composant le plus sensible à la langue : si vous envoyez du texte anglais à une voix de synthèse française, elle le lira avec un accent français incompréhensible ("ze ouaizeure toudaye").

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   VOUS PARLEZ   │ ────► │  WHISPER (STT)  │ ────► │   TTS (PIPER)   │
│ (Micro / Accent)│       │  language=lang  │       │ Voix / .onnx    │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

### 4.1 Speech-to-Text (STT) : `faster-whisper`

Whisper est capable de détecter la langue tout seul, mais cela prend du temps et peut provoquer des hallucinations au démarrage. **Forcez le paramètre `language`** :

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcrire_audio(fichier_audio: str, current_lang: str) -> str:
    # On passe explicitement 'fr', 'en', ou 'es'
    segments, info = model.transcribe(fichier_audio, language=current_lang)
    texte = "".join([segment.text for segment in segments])
    return texte.strip()
```

### 4.2 Text-to-Speech (TTS) : `edge-tts` (Online) & `piper-tts` (Offline)

Créez un catalogue de voix mappé sur le code langue.

#### Option A : Catalogue `edge-tts` (Haute qualité / Online)

```python
import edge_tts
import asyncio

VOICES_EDGE = {
    "fr": "fr-FR-HenriNeural",         # Voix française masculine
    "en": "en-US-ChristopherNeural",   # Voix américaine masculine
    "es": "es-ES-AlvaroNeural"         # Voix espagnole masculine
}

async def generer_audio_edge(texte: str, lang: str, output_path: str):
    voix = VOICES_EDGE.get(lang, VOICES_EDGE["fr"])
    communicate = edge_tts.Communicate(texte, voix)
    await communicate.save(output_path)
```

#### Option B : Catalogue `piper-tts` (100% Offline)

Téléchargez au préalable un fichier modèle `.onnx` par langue (ex. sur le repo HuggingFace de Piper) et rangez-les dans `models/voice/`.

```python
import subprocess

VOICES_PIPER = {
    "fr": "models/voice/fr_FR-siwis-medium.onnx",
    "en": "models/voice/en_US-lessac-medium.onnx",
    "es": "models/voice/es_ES-sharvard-medium.onnx"
}

def generer_audio_piper(texte: str, lang: str, output_wav: str):
    model_path = VOICES_PIPER.get(lang, VOICES_PIPER["fr"])
    
    # Commande Piper en binaire externe
    commande = f'echo "{texte}" | ./piper --model {model_path} --output_file {output_wav}'
    subprocess.run(commande, shell=True, check=True)
```

---

## 📚 Pilier 5 : Mémoire Vectorielle & Documents (RAG)

Dans votre guide d'origine (`GUIDE_MEMOIRE_VECTORIELLE.md`), vous utilisiez le modèle `all-MiniLM-L6-v2`.  
⚠️ **Le Piège** : Ce modèle a été entraîné majoritairement sur de l'anglais. Il fonctionne moyennement en français, mais perd beaucoup en précision si vous mélangez plusieurs langues.

### 5.1 Adopter un Embedding Multilingue

Pour un RAG polyglotte irréprochable, installez l'un de ces modèles dans `sentence-transformers` :
- `paraphrase-multilingual-MiniLM-L12-v2` (~470 Mo, rapide et excellent pour plus de 50 langues).
- `multilingual-e5-base` (très moderne, excellent pour la recherche sémantique croisée).

Modifiez l'initialisation dans votre code ChromaDB :

```python
import chromadb
from chromadb.utils import embedding_functions

# Remplacement par le modèle d'embedding multilingue officiel
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path="chroma_db_docs")
collection = client.get_or_create_collection(name="mes_documents", embedding_function=ef)
```

### 5.2 Le RAG Croisé (Cross-Lingual RAG)

Grâce à cet embedding multilingue, un utilisateur peut charger un document **en français**, puis poser une question **en anglais** ou **en espagnol**. Le modèle d'embedding trouvera la similarité sémantique quelle que soit la langue !

Il suffit d'indiquer à l'IA la langue de réponse dans le prompt de synthèse RAG :

```python
from translations import LANG_NAMES

def generer_prompt_rag(question: str, contextes: list, lang: str) -> str:
    contexte_texte = "\n---\n".join(contextes)
    langue_cible = LANG_NAMES.get(lang, "Français")
    
    prompt = (
        f"You are an expert assistant. Use the following background context to answer the user's question.\n\n"
        f"### CONTEXT:\n{contexte_texte}\n\n"
        f"### USER QUESTION:\n{question}\n\n"
        f"### STRICT INSTRUCTION:\n"
        f"You must analyze the context above but write your final answer entirely in {langue_cible}."
    )
    return prompt
```

---

## 🌐 Pilier 6 : L'API REST (FastAPI)

Si vous utilisez votre API (`api_server.py`) pour connecter des applications externes, ajoutez simplement le paramètre `language` dans votre modèle Pydantic de requête.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama

app = FastAPI(title="API Agent Multi-langue")

class RequêteUtilisateur(BaseModel):
    user_message: str
    language: str = "fr"  # 'fr' par défaut
    persona: str = "assistant"

@app.post("/chat")
async def chat_endpoint(requete: RequêteUtilisateur):
    try:
        # 1. Obtenir le system prompt adapté à la langue demandée
        system_prompt = get_system_prompt(requete.persona, requete.language)
        
        # 2. Appel à Ollama
        reponse = ollama.chat(
            model='qwen2.5:3b', # ou votre modèle actuel
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': requete.user_message}
            ]
        )
        
        return {
            "status": "success",
            "language": requete.language,
            "response": reponse['message']['content']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🚀 Plan de Mise en Œuvre (Checklist Étape par Étape)

Pour intégrer ces changements sans casser votre agent actuel, suivez cet ordre précis :

- [ ] **Étape 1** : Créez le fichier `translations.py` contenant le dictionnaire des textes de votre interface web.
- [ ] **Étape 2** : Modifiez `app_ultime.py` (ou `app_web.py`) pour ajouter le `st.selectbox` de langue dans la sidebar et remplacez vos chaînes de caractères brutes par `t("clé")`. Testez que le changement de langue rafraîchit bien l'UI.
- [ ] **Étape 3** : Modifiez la fonction qui génère votre `system_prompt` pour injecter la clause `You must strictly answer in {LANG_NAMES[lang]}`. Lancez une conversation pour valider que l'IA change de langue instantanément.
- [ ] **Étape 4** : Mettez à jour vos outils Python (`heure`, `recherche_web`) en acceptant l'argument `lang=st.session_state.lang`.
- [ ] **Étape 5** : *(Si vous utilisez la voix)* Configurez vos catalogues de voix `edge-tts` ou `piper-tts` et passez `language=lang` à Faster-Whisper.
- [ ] **Étape 6** : *(Si vous utilisez le RAG)* Changez le nom du modèle dans `SentenceTransformerEmbeddingFunction` par `paraphrase-multilingual-MiniLM-L12-v2`. *(Note : il faudra ré-indexer vos documents une fois)*.

🎉 **Félicitations ! Votre agent IA est désormais une plateforme véritablement internationale et polyglotte !**
