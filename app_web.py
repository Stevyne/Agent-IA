"""
Interface web de l'Agent IA (Streamlit).
Utilise Ollama + un modèle local avec tool calling (function calling).
"""

import streamlit as st
import ollama
from datetime import datetime
import re

# ================== CONFIGURATION ==================
# Changez selon votre VRAM :
# - GTX 1060 6 Go  -> "qwen2.5:3b"
# - GTX 1070/1080 8 Go -> "qwen2.5:7b"
# - GTX 1080 Ti 11 Go  -> "qwen2.5:7b"
MODEL = "qwen2.5:3b"
# ===================================================


def _safe_calc(expression: str) -> str:
    """Calcule une expression mathématique en toute sécurité."""
    if not re.match(r'^[0-9+\-*/.() ]+$', expression):
        return "Erreur : caractères non autorisés. Utilisez uniquement + - * / ( ) et chiffres."
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Erreur de calcul : {e}"


# Outils disponibles pour l'agent
AVAILABLE_FUNCTIONS = {
    "calculer": lambda expr: _safe_calc(expr),
    "heure_actuelle": lambda: datetime.now().strftime("%A %d %B %Y, %H:%M:%S"),
}

# Schéma des outils (format Ollama function calling)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique simple (ex: 15 * 4 + 2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Expression mathématique à évaluer, ex: 25 * 4 + 10"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "heure_actuelle",
            "description": "Retourne la date et l'heure actuelle de l'ordinateur.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def _get_args(args):
    """Helper : s'assure que les arguments sont un dict."""
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        import json
        try:
            return json.loads(args)
        except Exception:
            return {}
    return {}


def run_agent_turn(internal_history: list) -> str:
    """
    Gère un tour complet de conversation avec tool calling.
    Modifie internal_history en place (ajoute les tool calls + la réponse finale).
    Retourne la réponse finale pour l'affichage.
    """
    response = ollama.chat(model=MODEL, messages=internal_history, tools=TOOLS)
    
    # Boucle : tant que l'assistant demande à utiliser un outil
    while response.message.tool_calls:
        # 1. Ajouter la demande d'outil de l'assistant à l'historique
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
        internal_history.append(assistant_msg)
        
        # 2. Exécuter chaque outil demandé
        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            func_args = _get_args(tool_call.function.arguments)
            func = AVAILABLE_FUNCTIONS.get(func_name)
            
            if func is None:
                result = f"Erreur : outil '{func_name}' introuvable."
            else:
                try:
                    if func_args:
                        result = func(**func_args)
                    else:
                        result = func()
                except Exception as e:
                    result = f"Erreur : {e}"
            
            internal_history.append({
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })
        
        # 3. Re-demander à l'agent avec les résultats
        response = ollama.chat(model=MODEL, messages=internal_history, tools=TOOLS)
    
    # Réponse finale textuelle
    final_content = response.message.content or "(L'agent n'a pas généré de réponse)"
    internal_history.append({"role": "assistant", "content": final_content})
    return final_content


# ===================== INTERFACE STREAMLIT =====================

st.set_page_config(page_title="Agent IA Local", page_icon="🤖", layout="centered")

st.title("🤖 Agent IA Local")
st.caption(f"Modèle : `{MODEL}` | Inférence 100% locale via Ollama | GPU NVIDIA")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.write(f"**Modèle actuel :** `{MODEL}`")
    st.write("**Outils disponibles :**")
    st.markdown("- 🔢 Calculatrice")
    st.markdown("- 🕐 Heure / Date")
    st.divider()
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.internal_history = []
        st.rerun()

# Initialisation des états
if "messages" not in st.session_state:
    st.session_state.messages = []
if "internal_history" not in st.session_state:
    st.session_state.internal_history = []

# Affichage de l'historique (visible par l'utilisateur)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Saisie utilisateur
if user_input := st.chat_input("Posez votre question..."):
    # 1. Afficher le message utilisateur
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Ajouter à l'historique interne (envoyé à Ollama)
    st.session_state.internal_history.append({"role": "user", "content": user_input})
    
    # 3. Générer la réponse de l'agent
    with st.chat_message("assistant"):
        with st.spinner("L'agent réfléchit..."):
            try:
                reply = run_agent_turn(st.session_state.internal_history)
            except Exception as e:
                reply = f"❌ Erreur : {e}"
        st.markdown(reply)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
