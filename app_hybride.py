"""
🤖👁️ Agent Hybride Web — Texte + Vision + Outils + Mémoire

Interface Streamlit qui route automatiquement :
  - Texte seul      → qwen2.5:3b (avec outils : calcul, heure, recherche docs)
  - Image présente  → llava-phi3 (analyse visuelle, OCR, description)

INSTALLATION :
  pip install streamlit pillow ollama
  ollama pull qwen2.5:3b
  ollama pull llava-phi3   (ou moondream)

Pour la recherche documents (optionnel) :
  pip install chromadb pypdf python-docx
  Et avoir lancé agent_documents.py une fois pour créer la base.
"""

import streamlit as st
import ollama
import os
import json
import base64
import re
from datetime import datetime
from io import BytesIO

# ========================= CONFIGURATION =========================
MODEL_TEXT = "qwen2.5:3b"
MODEL_VISION = "llava-phi3"
MEMORY_FILE = "memory_hybride.json"
MAX_TEXT_HISTORY = 20          # Avant résumage
MAX_VISION_HISTORY = 10        # Messages max pour le modèle vision
MAX_IMAGE_SIZE = 1024          # Redimensionnement côté client
RAG_DB_PATH = "chroma_db_docs"
RAG_COLLECTION = "bibliotheque"
# ================================================================


# --- Imports optionnels ---
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


# ------------------------------------------------------------------
# 1. OUTILS TEXTE
# ------------------------------------------------------------------

def calculer(expression: str) -> str:
    if not re.match(r'^[0-9+\-*/.() ]+$', expression):
        return "Erreur : caractères non autorisés."
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Erreur de calcul : {e}"


def heure_actuelle() -> str:
    return datetime.now().strftime("%A %d %B %Y, %H:%M:%S")


# --- Outil RAG optionnel ---
_rag_collection = None

def init_rag():
    """Initialise la connexion ChromaDB si la base existe."""
    global _rag_collection
    if not HAS_CHROMADB:
        return False
    try:
        client = chromadb.PersistentClient(path=RAG_DB_PATH)
        _rag_collection = client.get_collection(name=RAG_COLLECTION)
        return True
    except Exception:
        _rag_collection = None
        return False


def rechercher_documents(requete: str, n_resultats: int = 5) -> str:
    """Fouille dans les documents PDF/Word/TXT indexés."""
    if _rag_collection is None:
        return "Base de documents non initialisée."
    try:
        n_resultats = int(n_resultats)
        if n_resultats < 1:
            n_resultats = 1
        if n_resultats > 10:
            n_resultats = 10
    except Exception:
        n_resultats = 5

    try:
        results = _rag_collection.query(query_texts=[requete], n_results=n_resultats)
    except Exception as e:
        return f"Erreur recherche : {e}"

    if not results or not results["documents"] or not results["documents"][0]:
        return "Aucun passage pertinent trouvé."

    passages = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i] if results.get("metadatas") else {}
        source = meta.get("source", "inconnu")
        doc_type = meta.get("type", "?")
        page = meta.get("page", "?")

        if doc_type == "pdf":
            loc = f"page {page}"
        elif doc_type == "docx":
            loc = f"paragraphe {page}"
        elif doc_type == "txt":
            loc = f"bloc {page}"
        else:
            loc = f"position {page}"

        passages.append(f"---\nSource: {source} ({loc})\n{doc}")

    return "\n".join(passages)


# --- Menu des outils pour le modèle texte ---
AVAILABLE_FUNCTIONS = {
    "calculer": calculer,
    "heure_actuelle": heure_actuelle,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique simple.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Expression mathématique"}},
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "heure_actuelle",
            "description": "Retourne la date et l'heure actuelle.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# On ajoute l'outil RAG si la collection est accessible
if HAS_CHROMADB:
    TOOLS.append({
        "type": "function",
        "function": {
            "name": "rechercher_documents",
            "description": (
                "Recherche des passages dans les documents locaux (PDF, Word, TXT). "
                "À utiliser si la question concerne un document, un contrat, un rapport, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "requete": {"type": "string", "description": "Sujet à chercher"},
                    "n_resultats": {"type": "integer", "description": "Nombre de passages (1-10)"}
                },
                "required": ["requete"]
            }
        }
    })
    AVAILABLE_FUNCTIONS["rechercher_documents"] = rechercher_documents


# ------------------------------------------------------------------
# 2. MÉMOIRE PERSISTANTE
# ------------------------------------------------------------------

def load_memory():
    """Charge l'historique depuis le fichier JSON."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_memory(messages):
    """Sauvegarde l'historique texte dans le fichier JSON."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.sidebar.warning(f"Erreur sauvegarde mémoire : {e}")


def summarize_text_history(messages):
    """Résumé automatique des anciens messages pour éviter la saturation."""
    if len(messages) <= MAX_TEXT_HISTORY:
        return messages

    recent = messages[-6:]
    old = messages[:-6]

    summary_prompt = [
        {"role": "system", "content": "Résume en quelques phrases les informations clés (prénom, préférences, sujets, décisions). Sois très concis."},
        {"role": "user", "content": "Historique à résumer :\n\n" + "\n".join(
            f"{m.get('role','?')}: {m.get('content','')}" for m in old if m.get("content")
        )}
    ]

    try:
        resp = ollama.chat(model=MODEL_TEXT, messages=summary_prompt)
        summary_text = resp.message.content or "(pas de résumé)"
    except Exception as e:
        summary_text = f"(erreur résumé: {e})"

    new_msgs = [{"role": "system", "content": f"Résumé des conversations précédentes : {summary_text}"}]
    new_msgs.extend(recent)
    return new_msgs


# ------------------------------------------------------------------
# 3. ENCODAGE IMAGE
# ------------------------------------------------------------------

def encode_image(uploaded_file):
    """
    Lit un fichier uploadé Streamlit, redimensionne si nécessaire,
    et retourne la chaîne base64.
    """
    raw = uploaded_file.getvalue()

    if HAS_PIL:
        try:
            img = Image.open(BytesIO(raw))
            w, h = img.size
            if w > MAX_IMAGE_SIZE or h > MAX_IMAGE_SIZE:
                ratio = min(MAX_IMAGE_SIZE / w, MAX_IMAGE_SIZE / h)
                new_w = int(w * ratio)
                new_h = int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                st.sidebar.info(f"Image redimensionnée : {w}x{h} → {new_w}x{new_h}")

            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")

            buf = BytesIO()
            img.save(buf, format="PNG")
            raw = buf.getvalue()
        except Exception as e:
            st.sidebar.warning(f"Erreur redimensionnement image : {e}")
    else:
        st.sidebar.info("Pillow non installé. Image envoyée telle quelle.")

    return base64.b64encode(raw).decode("utf-8")


# ------------------------------------------------------------------
# 4. AGENT TEXTE (avec tool calling)
# ------------------------------------------------------------------

def _parse_args(args):
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            return json.loads(args)
        except Exception:
            return {}
    return {}


def run_text_agent(history, user_msg):
    """
    Gère un tour de conversation texte avec tool calling (calcul, heure, RAG).
    Modifie 'history' en place.
    """
    # Ajouter la question utilisateur
    history.append({"role": "user", "content": user_msg})

    response = ollama.chat(model=MODEL_TEXT, messages=history, tools=TOOLS)

    while response.message.tool_calls:
        assistant_msg = {
            "role": "assistant",
            "content": response.message.content or "",
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response.message.tool_calls
            ]
        }
        history.append(assistant_msg)

        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            func_args = _parse_args(tool_call.function.arguments)
            func = AVAILABLE_FUNCTIONS.get(func_name)

            if func is None:
                result = f"Erreur : outil '{func_name}' introuvable."
            else:
                try:
                    result = func(**func_args)
                except Exception as e:
                    result = f"Erreur : {e}"

            # Log silencieux dans l'interface (on ne montre pas les tool calls à l'utilisateur)
            history.append({"role": "tool", "name": func_name, "content": str(result)})

        response = ollama.chat(model=MODEL_TEXT, messages=history, tools=TOOLS)

    final = response.message.content or "(pas de réponse)"
    history.append({"role": "assistant", "content": final})
    return final


# ------------------------------------------------------------------
# 5. AGENT VISION (analyse d'image)
# ------------------------------------------------------------------

def run_vision_agent(vision_history, user_msg, image_b64):
    """
    Envoie une image + question au modèle multimodal (llava-phi3).
    'vision_history' est une liste de messages texte {role, content} sans images.
    """
    # Garder les derniers échanges pour le contexte (sans images, allégé)
    msgs = vision_history[-(MAX_VISION_HISTORY - 2):]
    msgs.append({"role": "user", "content": user_msg, "images": [image_b64]})

    try:
        response = ollama.chat(model=MODEL_VISION, messages=msgs)
        reply = response.message.content or "(pas de réponse)"
    except Exception as e:
        reply = f"[ERREUR Vision] {e}"

    # Mettre à jour l'historique vision (texte uniquement, pas d'image)
    vision_history.append({"role": "user", "content": user_msg})
    vision_history.append({"role": "assistant", "content": reply})

    # Limiter la taille
    while len(vision_history) > MAX_VISION_HISTORY:
        vision_history.pop(0)

    return reply


# ------------------------------------------------------------------
# 6. INTERFACE STREAMLIT
# ------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Agent Hybride IA",
        page_icon="🤖",
        layout="centered"
    )

    st.title("🤖👁️ Agent Hybride IA")
    st.caption("Texte + Vision + Outils | 100% local via Ollama")

    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.markdown(f"**Modèle texte** : `{MODEL_TEXT}`")
        st.markdown(f"**Modèle vision** : `{MODEL_VISION}`")

        st.divider()

        # Upload image
        uploaded_file = st.file_uploader(
            "📁 Uploader une image",
            type=["png", "jpg", "jpeg", "gif", "bmp", "webp"]
        )

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Image prête", use_container_width=True)
            st.success("Image détectée → mode vision activé")

        st.divider()

        # Checkboxes
        use_memory = st.checkbox("🧠 Mémoire persistante", value=False,
                                 help="Sauvegarde l'historique dans memory_hybride.json")
        use_rag = st.checkbox("📄 Recherche documents", value=False,
                              help="Nécessite ChromaDB + dossier 'documents/' indexé")

        if use_rag:
            if init_rag():
                st.success("Base de documents connectée.")
            else:
                st.warning("Base de documents introuvable. Lancez agent_documents.py d'abord.")

        st.divider()

        if st.button("🗑️ Nouvelle conversation", use_container_width=True):
            for key in ["messages", "internal_history", "vision_history", "current_image_b64", "current_image_name"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # ==================== INIT ÉTAT ====================
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "internal_history" not in st.session_state:
        st.session_state.internal_history = []
    if "vision_history" not in st.session_state:
        st.session_state.vision_history = []
    if "current_image_b64" not in st.session_state:
        st.session_state.current_image_b64 = None
    if "current_image_name" not in st.session_state:
        st.session_state.current_image_name = None

    # Charger mémoire si demandé et historique vide
    if use_memory and not st.session_state.messages:
        loaded = load_memory()
        if loaded:
            # Séparer texte et vision (on ne sait pas vraiment, on met tout dans internal_history)
            st.session_state.internal_history = loaded
            # Reconstruire les messages affichables (simplifié : juste les pairs user/assistant)
            for i in range(0, len(loaded), 2):
                if i < len(loaded) and loaded[i].get("role") == "user":
                    st.session_state.messages.append({"role": "user", "content": loaded[i].get("content", "")})
                if i + 1 < len(loaded) and loaded[i+1].get("role") == "assistant":
                    st.session_state.messages.append({"role": "assistant", "content": loaded[i+1].get("content", "")})
            st.sidebar.info(f"Mémoire chargée : {len(loaded)} messages")

    # ==================== AFFICHAGE HISTORIQUE ====================
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("image_b64"):
                st.image(BytesIO(base64.b64decode(msg["image_b64"])), use_container_width=True)
            if msg.get("content"):
                st.markdown(msg["content"])

    # ==================== INPUT ====================
    user_input = st.chat_input("Posez votre question ou décrivez l'image...")

    # ==================== TRAITEMENT ====================
    if user_input or uploaded_file:

        # --- Encoder l'image si uploadée ---
        if uploaded_file is not None:
            b64 = encode_image(uploaded_file)
            st.session_state.current_image_b64 = b64
            st.session_state.current_image_name = uploaded_file.name

        # Déterminer le mode
        has_image = st.session_state.current_image_b64 is not None
        is_vision = has_image and (user_input or uploaded_file is not None)

        # --- Afficher le message utilisateur ---
        user_display_text = user_input if user_input else "Analyse cette image."
        with st.chat_message("user"):
            if has_image:
                st.image(BytesIO(base64.b64decode(st.session_state.current_image_b64)), use_container_width=True)
            st.markdown(user_display_text)

        st.session_state.messages.append({
            "role": "user",
            "content": user_display_text,
            "image_b64": st.session_state.current_image_b64 if has_image else None
        })

        # --- Générer la réponse ---
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                try:
                    if is_vision:
                        reply = run_vision_agent(
                            st.session_state.vision_history,
                            user_display_text,
                            st.session_state.current_image_b64
                        )
                    else:
                        # Résumage automatique si trop long
                        if len(st.session_state.internal_history) > MAX_TEXT_HISTORY:
                            st.session_state.internal_history = summarize_text_history(
                                st.session_state.internal_history
                            )
                            st.sidebar.info("Historique texte résumé automatiquement.")

                        reply = run_text_agent(
                            st.session_state.internal_history,
                            user_display_text
                        )
                except Exception as e:
                    reply = f"❌ Erreur : {e}"

            st.markdown(reply)

        # --- Sauvegarder la réponse ---
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # --- Sauvegarder mémoire ---
        if use_memory:
            # On sauvegarde l'historique texte (le vision est trop lourd avec base64)
            save_memory(st.session_state.internal_history)

        # Rerun pour rafraîchir l'affichage (notamment l'image dans la sidebar reste)
        # Mais en fait Streamlit gère bien le state sans rerun forcé ici.


if __name__ == "__main__":
    main()
