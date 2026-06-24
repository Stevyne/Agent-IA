"""
Agent IA conversationnel en mode terminal.
Utilise Ollama + un modèle local (Qwen 2.5 recommandé) avec tool calling.
"""

import ollama
import re
from datetime import datetime

# ================== CONFIGURATION ==================
# Changez selon votre VRAM :
# - GTX 1060 6 Go  -> "qwen2.5:3b" ou "llama3.2:3b"
# - GTX 1070/1080 8 Go -> "qwen2.5:7b"
# - GTX 1080 Ti 11 Go  -> "qwen2.5:7b"
MODEL = "qwen2.5:3b"
# ===================================================


def calculer(expression: str) -> str:
    """Évalue une expression mathématique simple en toute sécurité."""
    if not re.match(r'^[0-9+\-*/.() ]+$', expression):
        return "Erreur : caractères non autorisés. Utilisez uniquement des chiffres et + - * / ( ) ."
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Erreur de calcul : {e}"


def heure_actuelle() -> str:
    """Retourne la date et l'heure actuelle."""
    return datetime.now().strftime("%A %d %B %Y, %H:%M:%S")


# Dictionnaire des outils disponibles pour l'agent
AVAILABLE_FUNCTIONS = {
    "calculer": calculer,
    "heure_actuelle": heure_actuelle,
}

# Schéma des outils pour Ollama (function calling)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique simple (ex: 15 * 4 + 2, 100 / 5).",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Expression mathématique à évaluer"
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


def run_agent(user_msg: str) -> str:
    """
    Envoie le message à Ollama et gère la boucle de tool calling.
    Retourne la réponse finale de l'assistant.
    """
    messages = [{"role": "user", "content": user_msg}]
    
    response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
    
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
        messages.append(assistant_msg)
        
        # 2. Exécuter chaque outil demandé et ajouter le résultat
        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments or {}
            
            func = AVAILABLE_FUNCTIONS.get(func_name)
            if func is None:
                result = f"Erreur : outil '{func_name}' introuvable."
            else:
                try:
                    if isinstance(func_args, dict) and func_args:
                        result = func(**func_args)
                    else:
                        result = func()
                except Exception as e:
                    result = f"Erreur lors de l'exécution : {e}"
            
            print(f"  [Outil: {func_name}({func_args}) -> {result}]")
            messages.append({
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })
        
        # 3. Re-demander à l'agent avec les résultats des outils
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
    
    return response.message.content or "(L'agent n'a pas généré de réponse)"


def main():
    print("=" * 60)
    print("  Agent IA local - Mode Terminal")
    print(f"  Modèle : {MODEL}")
    print("  Tapez 'quit' ou 'exit' pour sortir")
    print("=" * 60)
    
    while True:
        try:
            user = input("\nVous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break
        
        if user.lower() in ("quit", "exit", "q", "bye"):
            print("Au revoir !")
            break
        if not user:
            continue
        
        print("Agent > ", end="", flush=True)
        try:
            answer = run_agent(user)
        except Exception as e:
            answer = f"[ERREUR] {e}"
        print(answer)


if __name__ == "__main__":
    main()
