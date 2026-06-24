"""
Agent IA avec mémoire persistante.
L'IA se souvient de vos conversations même après redémarrage.
"""

import ollama
import json
import os
from datetime import datetime

# ================== CONFIGURATION ==================
MODEL = "qwen2.5:3b"
# Combien de messages garder avant de résumer (évite de saturer la mémoire du modèle)
MAX_HISTORY_MESSAGES = 20
# Fichier où sauvegarder la mémoire
MEMORY_FILE = "memory.json"
# ===================================================

def calculer(expression: str) -> str:
    import re
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
                "properties": {
                    "expression": {"type": "string", "description": "Expression mathématique"}
                },
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


def load_memory():
    """
    Charge la mémoire depuis le fichier JSON.
    Retourne une liste de messages (historique) ou une liste vide.
    """
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # data doit être une liste de messages
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_memory(messages):
    """
    Sauvegarde la mémoire dans le fichier JSON.
    """
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def summarize_old_messages(messages):
    """
    Quand l'historique devient trop long, on demande au modèle de le résumer.
    On garde les messages récents intacts, et on remplace les vieux par un résumé.
    """
    if len(messages) <= MAX_HISTORY_MESSAGES:
        return messages

    # On garde les 6 derniers messages tels quels (contexte récent important)
    recent = messages[-6:]
    old = messages[:-6]

    # On demande au modèle de résumer les anciens messages
    summary_prompt = [
        {"role": "system", "content": "Tu es un assistant qui résume des conversations. Résume en quelques phrases les informations clés (prénom, préférences, sujets abordés, décisions prises). Sois très concis."},
        {"role": "user", "content": "Voici l'historique de conversation à résumer :\n\n" + format_history_for_summary(old)}
    ]

    try:
        resp = ollama.chat(model=MODEL, messages=summary_prompt)
        summary_text = resp.message.content or "(pas de résumé)"
    except Exception as e:
        summary_text = f"(erreur de résumé: {e})"

    # Nouvel historique : [résumé des vieux] + [messages récents]
    new_messages = [
        {"role": "system", "content": f"Résumé des conversations précédentes : {summary_text}"}
    ]
    new_messages.extend(recent)
    return new_messages


def format_history_for_summary(messages):
    """Transforme la liste de messages en texte simple pour le résumé."""
    lines = []
    for m in messages:
        role = m.get("role", "?")
        content = m.get("content", "")
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def run_agent_with_memory(user_msg, history):
    """
    Gère un tour de conversation avec tool calling et mémoire.
    'history' est la liste de messages persistante.
    """
    # Ajouter le message utilisateur
    history.append({"role": "user", "content": user_msg})

    response = ollama.chat(model=MODEL, messages=history, tools=TOOLS)

    # Boucle tool calling
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
                    result = f"Erreur : {e}"

            print(f"  [Outil: {func_name}({func_args}) -> {result}]")
            history.append({
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })

        response = ollama.chat(model=MODEL, messages=history, tools=TOOLS)

    final = response.message.content or "(pas de réponse)"
    history.append({"role": "assistant", "content": final})
    return final


def main():
    print("=" * 60)
    print("  Agent IA avec mémoire persistante")
    print(f"  Modèle : {MODEL}")
    print(f"  Fichier mémoire : {MEMORY_FILE}")
    print("  Tapez 'quit' ou 'exit' pour sortir")
    print("=" * 60)

    # 1. Charger la mémoire précédente
    history = load_memory()

    if history:
        print(f"\n📂 Mémoire chargée : {len(history)} messages en mémoire.")
        # Si l'historique est trop long, on résume
        history = summarize_old_messages(history)
        print(f"   Après résumage : {len(history)} messages.")
    else:
        print("\n📂 Aucune mémoire précédente trouvée. Nouvelle conversation.")
        history = []

    # Optionnel : injecter un rôle/personnalité si vous voulez
    # history.insert(0, {"role": "system", "content": "Tu es un assistant amical et patient."})

    while True:
        try:
            user = input("\nVous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n💾 Sauvegarde de la mémoire...")
            save_memory(history)
            print("Au revoir !")
            break

        if user.lower() in ("quit", "exit", "q", "bye"):
            print("\n💾 Sauvegarde de la mémoire...")
            save_memory(history)
            print("✅ Mémoire sauvegardée. Au revoir !")
            break
        if not user:
            continue

        # Résumage automatique si l'historique devient trop grand
        history = summarize_old_messages(history)

        print("Agent > ", end="", flush=True)
        try:
            answer = run_agent_with_memory(user, history)
        except Exception as e:
            answer = f"[ERREUR] {e}"
        print(answer)

        # Sauvegarde automatique après chaque réponse (sécurité)
        save_memory(history)


if __name__ == "__main__":
    main()
