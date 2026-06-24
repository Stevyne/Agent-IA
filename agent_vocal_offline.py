"""
🎙️ Agent IA Vocal 100% OFFLINE.

Utilise :
  - Piper-TTS      → voix naturelle (synthèse vocale locale)
  - Faster-Whisper → reconnaissance vocale (transcription locale)
  - Ollama         → cerveau IA (GPU local)

AUCUNE donnée ne quitte votre PC (ni voix, ni texte, ni audio).

INSTALLATION :
  pip install faster-whisper pyaudio SpeechRecognition ollama
  
  PUIS téléchargez Piper + une voix française dans models/piper/
  Voir GUIDE_VOIX_OFFLINE.md pour les liens exacts.
"""

import os
import sys
import platform
import subprocess
import tempfile
import threading
import wave
import time
import re
from datetime import datetime

# ================== CONFIGURATION ==================
MODEL_OLLAMA = "qwen2.5:3b"      # ou "qwen2.5:7b"

# Piper-TTS
PIPER_DIR = "models/piper"         # Dossier contenant piper.exe + modèle .onnx
PIPER_MODEL = None                 # None = auto-detect le premier .onnx
PIPER_LENGTH_SCALE = 1.0           # 1.0 = normal, <1 = plus rapide, >1 = plus lent

# Faster-Whisper
WHISPER_MODEL = "tiny"             # "tiny" (39 Mo), "base" (74 Mo), "small" (244 Mo)
WHISPER_DEVICE = "cpu"             # "cpu" ou "cuda" (si ctranslate2 CUDA installé)
WHISPER_COMPUTE_TYPE = "int8"      # "int8" = rapide CPU, "float16" = GPU
# ===================================================


# ------------------------------------------------------------------
# 0. IMPORTS OPTIONNELS (avec détection)
# ------------------------------------------------------------------

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    print("⚠️  pyaudio non installé. L'agent ne pourra ni parler ni écouter.")
    print("   Tapez :  pip install pyaudio")

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    print("⚠️  SpeechRecognition non installé. Le micro ne fonctionnera pas.")
    print("   Tapez :  pip install SpeechRecognition")

try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("⚠️  faster-whisper non installé. La reconnaissance vocale est désactivée.")
    print("   Tapez :  pip install faster-whisper")


# ------------------------------------------------------------------
# 1. PIPER-TTS (SYNTHÈSE VOCALE)
# ------------------------------------------------------------------

class PiperTTS:
    """
    Gère la synthèse vocale avec Piper (binaire externe).
    Génère un fichier WAV temporaire, puis le lit avec pyaudio.
    """

    def __init__(self):
        self.piper_bin = self._find_binary()
        self.model_path = self._find_model()
        self.ok = self.piper_bin is not None and self.model_path is not None

        if self.ok:
            print(f"  ✅ Piper-TTS prêt : {os.path.basename(self.model_path)}")
        else:
            if self.piper_bin is None:
                print("  ❌ Binaire Piper introuvable. Cherchez dans models/piper/ ou PATH.")
            if self.model_path is None:
                print(f"  ❌ Modèle .onnx introuvable dans {PIPER_DIR}/")
                print("     Téléchargez une voix française sur https://huggingface.co/rhasspy/piper-voices")

    def _find_binary(self) -> str | None:
        """Cherche piper.exe (Windows) ou piper (Linux/Mac) dans PIPER_DIR puis PATH."""
        system = platform.system()
        name = "piper.exe" if system == "Windows" else "piper"

        # 1. Chercher dans PIPER_DIR
        local = os.path.join(PIPER_DIR, name)
        if os.path.isfile(local):
            return os.path.abspath(local)

        # 2. Chercher dans le PATH
        for path in os.environ.get("PATH", "").split(os.pathsep):
            candidate = os.path.join(path, name)
            if os.path.isfile(candidate):
                return candidate

        return None

    def _find_model(self) -> str | None:
        """Cherche le modèle .onnx dans PIPER_DIR."""
        if PIPER_MODEL is not None:
            candidate = os.path.join(PIPER_DIR, PIPER_MODEL)
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

        # Auto-detect : premier .onnx trouvé
        if not os.path.isdir(PIPER_DIR):
            return None
        for f in os.listdir(PIPER_DIR):
            if f.endswith(".onnx") and not f.endswith(".onnx.json"):
                candidate = os.path.join(PIPER_DIR, f)
                if os.path.isfile(candidate):
                    return os.path.abspath(candidate)
        return None

    def _generate_wav(self, text: str) -> str | None:
        """Génère un fichier WAV à partir du texte avec Piper. Retourne le chemin ou None."""
        # Fichier temporaire
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        # Préparer la commande
        cmd = [
            self.piper_bin,
            "--model", self.model_path,
            "--output_file", wav_path,
        ]
        if PIPER_LENGTH_SCALE != 1.0:
            cmd += ["--length_scale", str(PIPER_LENGTH_SCALE)]

        try:
            result = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                shell=False,
            )
            if result.returncode != 0:
                print(f"  ⚠️  Piper erreur : {result.stderr.decode('utf-8', errors='replace')[:200]}")
                os.remove(wav_path)
                return None
            return wav_path
        except Exception as e:
            print(f"  ⚠️  Erreur génération voix : {e}")
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return None

    def _play_wav(self, wav_path: str):
        """Lit le fichier WAV avec pyaudio + wave."""
        if not HAS_PYAUDIO:
            return

        try:
            wf = wave.open(wav_path, "rb")
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )

            chunk_size = 1024
            data = wf.readframes(chunk_size)
            while data:
                stream.write(data)
                data = wf.readframes(chunk_size)

            stream.stop_stream()
            stream.close()
            p.terminate()
            wf.close()
        except Exception as e:
            print(f"  ⚠️  Erreur lecture audio : {e}")
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

    def speak(self, text: str):
        """Fait parler l'agent."""
        if not self.ok:
            return

        # Nettoyer le texte pour la voix (supprime markdown, code, etc.)
        clean = text
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", clean)   # gras
        clean = re.sub(r"`(.+?)`", r"\1", clean)         # code inline
        clean = re.sub(r"#+ ", "", clean)                # titres markdown
        clean = clean.replace("\n", " ")

        wav_path = self._generate_wav(clean)
        if wav_path:
            self._play_wav(wav_path)


# ------------------------------------------------------------------
# 2. FASTER-WHISPER (RECONNAISSANCE VOCALE)
# ------------------------------------------------------------------

class WhisperSTT:
    """
    Gère la reconnaissance vocale avec Faster-Whisper (100% local).
    Capture le micro via SpeechRecognition, sauvegarde en WAV,
    puis transcrit avec Whisper.
    """

    def __init__(self):
        self.ok = HAS_WHISPER and HAS_SR and HAS_PYAUDIO
        self.model = None
        self.recognizer = None
        self.microphone = None

        if not self.ok:
            return

        # Charger le modèle Whisper
        print(f"  🧠 Chargement du modèle Whisper '{WHISPER_MODEL}' (premier lancement = téléchargement)...")
        try:
            self.model = WhisperModel(
                WHISPER_MODEL,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE,
            )
            print("  ✅ Modèle Whisper prêt.")
        except Exception as e:
            print(f"  ❌ Erreur chargement Whisper : {e}")
            self.ok = False
            return

        # Préparer le micro
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            with self.microphone as source:
                print("  🎤 Calibration du micro (1 seconde, ne parlez pas)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("  ✅ Micro prêt.")
        except Exception as e:
            print(f"  ⚠️  Micro non disponible : {e}")
            self.ok = False

    def listen(self) -> str | None:
        """
        Écoute le micro, enregistre un WAV, le transcrit avec Whisper.
        Retourne le texte reconnu, ou None si échec.
        """
        if not self.ok:
            return None

        try:
            with self.microphone as source:
                print("  🎤 J'écoute... (parlez maintenant)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except Exception as e:
            print(f"  ⚠️  Erreur micro : {e}")
            return None

        print("  🧠 Transcription en cours...")

        # Sauvegarder l'audio en WAV temporaire
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            with open(wav_path, "wb") as f:
                f.write(audio.get_wav_data())

            # Transcrire avec Whisper
            segments, info = self.model.transcribe(
                wav_path,
                language="fr",
                condition_on_previous_text=False,
            )
            text = " ".join([seg.text.strip() for seg in segments])
            text = text.strip()

            if text:
                print(f"  👤 Vous avez dit : {text}")
                return text
            else:
                print("  🤷 J'ai entendu, mais je n'ai pas compris.")
                return None
        except Exception as e:
            print(f"  ⚠️  Erreur transcription : {e}")
            return None
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)


# ------------------------------------------------------------------
# 3. OUTILS OLLAMA (identique aux autres agents)
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


def run_ollama(user_msg: str) -> str:
    """Gère un tour de conversation avec tool calling."""
    messages = [{"role": "user", "content": user_msg}]
    response = ollama.chat(model=MODEL_OLLAMA, messages=messages, tools=TOOLS)

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

        response = ollama.chat(model=MODEL_OLLAMA, messages=messages, tools=TOOLS)

    return response.message.content or "(pas de réponse)"


# ------------------------------------------------------------------
# 4. PROGRAMME PRINCIPAL
# ------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  🤖 Agent IA Vocal — 100% OFFLINE")
    print(f"  TTS : Piper-TTS  |  STT : Faster-Whisper  |  IA : {MODEL_OLLAMA}")
    print("=" * 60)

    if not HAS_OLLAMA:
        print("\n❌ Le module 'ollama' Python n'est pas installé.")
        print("   Tapez :  pip install ollama")
        sys.exit(1)

    # Initialisation
    print("\n🔧 Initialisation...")
    tts = PiperTTS()
    stt = WhisperSTT()

    if tts.ok:
        tts.speak("Bonjour. Je suis prêt. Vous pouvez parler ou taper.")
    else:
        print("\nℹ️  Mode silencieux : l'IA ne pourra pas parler.")

    mode_micro = False

    print("-" * 60)
    print("  COMMANDES :")
    print("    .m  → mode micro (vous parlez)")
    print("    .c  → mode clavier (vous tapez)")
    print("    quit / exit  → quitter")
    print("-" * 60)

    while True:
        user_input = None

        # --- Mode micro ---
        if mode_micro and stt.ok:
            print("\n  🎤 Mode micro. Parlez maintenant (ou tapez '.c' pour clavier)")
            user_input = stt.listen()
            if user_input is None:
                # On n'a pas compris : on bascule automatiquement sur le clavier
                print("  (je bascule sur le clavier)")
                mode_micro = False
                try:
                    user_input = input("\nVous > ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
        else:
            # --- Mode clavier ---
            try:
                user_input = input("\nVous > ").strip()
            except (EOFError, KeyboardInterrupt):
                break

        if not user_input:
            continue

        # --- Commandes spéciales ---
        if user_input.lower() in ("quit", "exit", "bye", "q"):
            if tts.ok:
                tts.speak("Au revoir. À bientôt.")
            print("Au revoir !")
            break

        if user_input == ".m":
            if stt.ok:
                mode_micro = True
                print("  🎤 Mode micro activé.")
                if tts.ok:
                    tts.speak("Mode micro activé.")
            else:
                print("  ❌ Micro non disponible. Vérifiez l'installation.")
            continue

        if user_input == ".c":
            mode_micro = False
            print("  ✏️ Mode clavier activé.")
            if tts.ok:
                tts.speak("Mode clavier activé.")
            continue

        # --- Envoyer à l'IA ---
        print("  ⏳ L'agent réfléchit...")
        try:
            reponse = run_ollama(user_input)
        except Exception as e:
            reponse = f"[ERREUR] {e}"

        print(f"\nAgent > {reponse}")

        # --- Faire parler l'IA ---
        if tts.ok:
            tts.speak(reponse)


if __name__ == "__main__":
    main()
