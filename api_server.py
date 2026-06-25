"""
📡 API REST — Serveur FastAPI pour l'Agent Ultime

Exécutez :
    uvicorn api_server:app --host 0.0.0.0 --port 8000

Puis accédez à :
    http://localhost:8000/docs  (interface de test interactive)
    http://VOTRE_IP:8000/chat   (endpoint principal)

NOTE : ce serveur partage le GPU avec l'interface web (app_ultime.py).
Ne les faites pas tourner simultanément si vous avez peu de VRAM.
"""

import os
import sys
import json
import base64
import re
import tempfile
import subprocess
from datetime import datetime
from io import BytesIO
from typing import Optional, List

from fastapi import FastAPI
from pydantic import BaseModel
import ollama

# ========================= CONFIGURATION =========================
MODEL_TEXT = "qwen2.5:3b"
MODEL_VISION = "llava-phi3"
MAX_TEXT_HISTORY = 20
MAX_IMAGE_SIZE = 1024
OUTPUTS_DIR = "outputs"
# ================================================================

# --- Détection imports optionnels ---
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ========================= OUTILS DE BASE =========================

def calculer(expression: str) -> str:
    if not re.match(r'^[0-9+\-*/.() ]+$', expression):
        return "Erreur : caractères non autorisés."
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Erreur de calcul : {e}"


def heure_actuelle() -> str:
    return datetime.now().strftime("%A %d %B %Y, %H:%M:%S")


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


# ========================= FONCTIONS DE TRAITEMENT =========================

def _parse_args(args):
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            return json.loads(args)
        except Exception:
            return {}
    return {}


def encode_image(image_b64: str) -> str:
    """Redimensionne une image base64 si nécessaire."""
    if not HAS_PIL:
        return image_b64
    try:
        raw = base64.b64decode(image_b64)
        img = Image.open(BytesIO(raw))
        w, h = img.size
        if w > MAX_IMAGE_SIZE or h > MAX_IMAGE_SIZE:
            ratio = min(MAX_IMAGE_SIZE / w, MAX_IMAGE_SIZE / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return image_b64


def run_text_agent(history: list, user_msg: str, system_prompt: str = None) -> tuple:
    """
    Gère un tour de conversation texte avec tool calling.
    Retourne (reply, new_history).
    """
    if system_prompt:
        has_system = any(m.get("role") == "system" for m in history)
        if not has_system:
            history = [{"role": "system", "content": system_prompt}] + history
        else:
            for i, m in enumerate(history):
                if m.get("role") == "system":
                    history[i]["content"] = system_prompt
                    break

    history = history + [{"role": "user", "content": user_msg}]
    response = ollama.chat(model=MODEL_TEXT, messages=history, tools=TOOLS)

    tools_used = []

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

            tools_used.append(func_name)
            history.append({"role": "tool", "name": func_name, "content": str(result)})

        response = ollama.chat(model=MODEL_TEXT, messages=history, tools=TOOLS)

    final = response.message.content or "(pas de réponse)"
    history.append({"role": "assistant", "content": final})
    return final, history, tools_used


def run_vision_agent(user_msg: str, image_b64: str) -> str:
    """Gère une analyse d'image avec LLaVA."""
    msgs = [
        {"role": "user", "content": user_msg, "images": [image_b64]}
    ]
    try:
        response = ollama.chat(model=MODEL_VISION, messages=msgs)
        return response.message.content or "(pas de réponse)"
    except Exception as e:
        return f"[ERREUR Vision] {e}"


# ========================= FASTAPI APP =========================

app = FastAPI(
    title="Agent IA Local API",
    description="API REST pour l'agent conversationnel local (Ollama).",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str
    image_b64: Optional[str] = None
    history: Optional[List[dict]] = []  # historique précédent (optionnel)
    system_prompt: Optional[str] = None  # personnalité (optionnel)


class ChatResponse(BaseModel):
    reply: str
    tools_used: List[str] = []
    model_used: str = ""


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Agent IA Local API",
        "models": {"text": MODEL_TEXT, "vision": MODEL_VISION},
        "docs": "/docs"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_msg = req.message.strip()
    if not user_msg:
        return ChatResponse(reply="Message vide.", tools_used=[], model_used=MODEL_TEXT)

    # Si image présente : mode vision
    if req.image_b64:
        image_b64 = encode_image(req.image_b64)
        reply = run_vision_agent(user_msg, image_b64)
        return ChatResponse(reply=reply, tools_used=[], model_used=MODEL_VISION)

    # Mode texte
    history = req.history or []
    reply, new_history, tools_used = run_text_agent(
        history,
        user_msg,
        system_prompt=req.system_prompt
    )

    return ChatResponse(
        reply=reply,
        tools_used=tools_used,
        model_used=MODEL_TEXT
    )


# Point d'entrée direct
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
