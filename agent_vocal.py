"""
🎙️ Agent IA Vocal — Il parle et (optionnellement) écoute.

MODES :
  - Mode clavier : vous tapez, l'IA répond à voix haute.
  - Mode micro : vous parlez, l'IA répond à voix haute.

INSTALLATION REQUISE :
    pip install pyttsx3
    pip install SpeechRecognition pyaudio   (optionnel, pour le micro)

NOTE : sur Windows, si 'pyaudio' refuse de s'installer :
    Téléchargez le .whl ici : https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    Ex : pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
"""

import ollama
import re
from datetime import datetime

# ================== CONFIGURATION ==================
MODEL = "qwen2.5:3b"  # ou "qwen2.5:7b" selon votre VRAM

# Paramètres de la voix
VITESSE_VOIX = 170        # Mots par minute (150 = lent, 200 = rapide)
VOLUME_VOIX = 1.0         # 0.0 à 1.0
# ===================================================


# ------------------------------------------------------------------
# 1. SYNTHÈSE VOCALE (TTS) — pyttsx3
# ------------------------------------------------------------------

_moteur_vocal = None

def initialiser_voix():
    """
    Prépare le moteur vocal pyttsx3.
    Retourne True si OK, False si le module n'est pas installé.
    """
    global _moteur_vocal
    try:
        import pyttsx3
        _moteur_vocal = pyttsx3.init()
        _moteur_vocal.setProperty("rate", VITESSE_VOIX)
        _moteur_vocal.setProperty("volume", VOLUME_VOIX)

        # Essayer de mettre une voix française (sur Windows, id 0 ou 1)
        voices = _moteur_vocal.getProperty("voices")
        for v in voices:
            if "french" in v.name.lower() or "franc" in v.name.lower() or "fr-FR" in v.id:
                _moteur_vocal.setProperty("voice", v.id)
                break
        return True
    except ImportError:
        print("⚠️  pyttsx3 n'est pas installé. L'agent ne pourra pas parler.")
        print("   Tapez :  pip install pyttsx3")
        return False
    except Exception as e:
        print(f"⚠️  Erreur initialisation voix : {e}")
        return False


def parler(texte: str):
    """
    Fait parler l'ordinateur avec la voix synthétique.
    Nettoie le texte pour une meilleure prononciation.
    """
    if _moteur_vocal is None:
        return

    # Petites corrections de prononciation pour pyttsx3
    clean = texte
    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", clean)   # Supprime le gras markdown **
    clean = re.sub(r"`(.+?)`", r"\1", clean)         # Supprime le code inline `
    clean = re.sub(r"#+ ", "", clean)                # Supprime les titres markdown
    clean = clean.replace("\n", " ")                 # Les retours à la ligne en espaces

    print(f"  🔊 [VOIX] {clean[:100]}{'...' if len(clean) > 100 else ''}")
    try:
        _moteur_vocal.say(clean)
        _moteur_vocal.runAndWait()
    except Exception as e:
        print(f"  ⚠️ Erreur voix : {e}")


# ------------------------------------------------------------------
# 2. RECONNAISSANCE VOCALE (STT) — SpeechRecognition + Google
# ------------------------------------------------------------------

_reconnaissance = None
_microphone = None

def initialiser_micro():
    """
    Prépare le micro et la reconnaissance vocale.
    Retourne True si OK, False sinon.
    """
    global _reconnaissance, _microphone
    try:
        import speech_recognition as sr
        _reconnaissance = sr.Recognizer()
        _microphone = sr.Microphone()
        # Petit réglage du bruit ambiant (1 seconde d'écoute du silence)
        with _microphone as source:
            print("  🎤 Calibration du micro (ne parlez pas, 1 seconde)...")
            _reconnaissance.adjust_for_ambient_noise(source, duration=1)
        print("  ✅ Micro prêt.")
        return True
    except ImportError:
        print("  ℹ️  SpeechRecognition / pyaudio non installés. Mode micro désactivé.")
        print("     Tapez :  pip install SpeechRecognition pyaudio")
        return False
    except Exception as e:
        print(f"  ⚠️  Micro non disponible : {e}")
        return False


def ecouter() -> str | None:
    """
    Écoute le micro et convertit la voix en texte.
    Retourne le texte reconnu, ou None si échec / silence.
    """
    if _reconnaissance is None or _microphone is None:
        return None

    try:
        with _microphone as source:
            print("  🎤 J'écoute... (parlez maintenant)")
            audio = _reconnaissance.listen(source, timeout=5, phrase_time_limit=10)
    except Exception as e:
        print(f"  ⚠️  Erreur micro : {e}")
        return None

    print("  🧠 Je reconnais votre voix...")
    try:
        # Reconnaissance via Google Speech API (nécessite Internet)
        texte = _reconnaissance.recognize_google(audio, language="fr-FR")
        print(f"  👤 Vous avez dit : {texte}")
        return texte
    except Exception as e:
        # Erreur de reconnaissance (bruit, silence, pas de connexion...)
        print("  🤷 Je n'ai pas compris.")
        return None


# ------------------------------------------------------------------
# 3. AGENT INTELLIGENT (Ollama + outils) — identique à agent_terminal.py
# ------------------------------------------------------------------

def calculer(expression: str) -> str:
    import re as re_local
    if not re_local.match(r'^[0-9+\-*/.() ]+$', expression):
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


def run_agent(user_msg: str) -> str:
    """Gère un tour de conversation avec tool calling."""
    messages = [{"role": "user", "content": user_msg}]
    response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)

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
        messages.append(assistant_msg)

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
            messages.append({"role": "tool", "name": func_name, "content": str(result)})

        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)

    return response.message.content or "(pas de réponse)"


# ------------------------------------------------------------------
# 4. PROGRAMME PRINCIPAL
# ------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  🤖 Agent IA Vocal")
    print(f"  Modèle : {MODEL}")
    print("-" * 60)

    # --- Initialisation voix ---
    voix_ok = initialiser_voix()
    if voix_ok:
        parler("Bonjour. Je suis prêt.")
    else:
        print("   Mode silencieux : l'IA répondra uniquement en texte.")

    # --- Initialisation micro ---
    micro_ok = initialiser_micro()
    mode_micro = False
    if micro_ok:
        parler("Le micro est disponible. Vous pouvez parler ou taper.")
    else:
        if voix_ok:
            parler("Le micro n'est pas disponible. Vous devrez taper vos questions.")
        print("   Mode clavier uniquement.")

    print("-" * 60)
    print("  COMMANDES :")
    print("    .m  → activer le mode micro (écoute vocale)")
    print("    .c  → activer le mode clavier (tapez vos questions)")
    print("    quit / exit  → quitter")
    print("=" * 60)

    while True:
        # --- Décider comment obtenir la question ---
        user_input = None

        if mode_micro and micro_ok:
            # Mode micro : on écoute
            print("\n  🎤 Mode micro activé. Parlez maintenant (ou tapez '.c' pour clavier)")
            user_input = ecouter()
            if user_input is None:
                # L'IA n'a rien compris, on propose de basculer ou réessayer
                if voix_ok:
                    parler("Je n'ai pas compris. Voulez-vous taper votre question ?")
                print("  (tapez '.c' pour passer au clavier, ou appuyez sur Entrée pour réécouter)")
                fallback = input("  > ").strip()
                if fallback.lower() == ".c":
                    mode_micro = False
                    print("  ✏️ Mode clavier activé.")
                continue
        else:
            # Mode clavier : on attend que l'utilisateur tape
            try:
                user_input = input("\nVous > ").strip()
            except (EOFError, KeyboardInterrupt):
                break

        if not user_input:
            continue

        # --- Commandes spéciales ---
        if user_input.lower() in ("quit", "exit", "bye", "q"):
            if voix_ok:
                parler("Au revoir. À bientôt.")
            print("Au revoir !")
            break

        if user_input == ".m":
            if micro_ok:
                mode_micro = True
                print("  🎤 Mode micro activé.")
                if voix_ok:
                    parler("Mode micro activé. Parlez maintenant.")
            else:
                print("  ❌ Micro non disponible.")
            continue

        if user_input == ".c":
            mode_micro = False
            print("  ✏️ Mode clavier activé.")
            if voix_ok:
                parler("Mode clavier activé.")
            continue

        # --- Envoyer à l'IA ---
        print("  ⏳ L'agent réfléchit...")
        try:
            reponse = run_agent(user_input)
        except Exception as e:
            reponse = f"[ERREUR] {e}"

        # --- Afficher la réponse ---
        print(f"\nAgent > {reponse}\n")

        # --- Faire parler l'IA ---
        if voix_ok:
            parler(reponse)


if __name__ == "__main__":
    main()
