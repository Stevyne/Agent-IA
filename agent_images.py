"""
🖼️ Agent IA Vision — Analyse d'images locales (100% offline).

Décrivez, interprétez, extrayez le texte (OCR visuel) de vos photos,
captures d'écran, documents scannés, graphiques, etc.

MODÈLES OLLAMA RECOMMANDÉS (choisissez selon votre VRAM) :
  - moondream       → très léger (~2 Go VRAM), rapide, qualité modeste
  - llava-phi3      → léger (~4-5 Go VRAM), bon équilibre
  - llava           → standard (~6-8 Go VRAM), meilleure qualité
  - llava:34b       → très lourd, réservé aux GPU récents

INSTALLATION :
  pip install pillow
  ollama pull llava-phi3   (ou moondream, llava, etc.)
"""

import os
import sys
import base64
from io import BytesIO
from datetime import datetime

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ================== CONFIGURATION ==================
MODEL_VISION = "llava-phi3"        # Modèle multimodal Ollama
# MODEL_VISION = "moondream"     # Alternative très légère
# MODEL_VISION = "llava"         # Alternative plus lourde (7B)

MAX_IMAGE_SIZE = 1024            # Redimensionne si largeur/hauteur > 1024 px
MAX_HISTORY_LEN = 6              # Garde max 6 échanges (images en base64 sont lourdes en contexte)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff")
# ===================================================


def print_header():
    print("=" * 60)
    print("  🖼️  Agent IA Vision — Analyse d'images")
    print(f"  Modèle : {MODEL_VISION}")
    print("-" * 60)
    print("  COMMANDES :")
    print("    !load <chemin>  → charger une image en mémoire")
    print("    !clear          → vider l'image et l'historique")
    print("    !info           → voir l'image chargée et le modèle")
    print("    quit / exit     → quitter")
    print("=" * 60)


def is_image_file(path: str) -> bool:
    """Vérifie si le chemin pointe vers une image (extension connue)."""
    if not path or not isinstance(path, str):
        return False
    ext = os.path.splitext(path.lower())[1]
    return ext in IMAGE_EXTENSIONS


def encode_image(path: str) -> str | None:
    """
    Charge une image depuis le disque, la redimensionne si trop grande,
    et la retourne sous forme de texte base64 (format PNG).
    """
    if not os.path.exists(path):
        print(f"  ❌ Fichier introuvable : {path}")
        return None

    if not is_image_file(path):
        print(f"  ⚠️  Extension non reconnue comme image : {path}")
        return None

    try:
        with open(path, "rb") as f:
            raw_bytes = f.read()

        # Si Pillow est disponible, vérifier/redimensionner
        if HAS_PIL:
            img = Image.open(BytesIO(raw_bytes))
            w, h = img.size

            if w > MAX_IMAGE_SIZE or h > MAX_IMAGE_SIZE:
                ratio = min(MAX_IMAGE_SIZE / w, MAX_IMAGE_SIZE / h)
                new_w = int(w * ratio)
                new_h = int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                print(f"  📐 Image redimensionnée : {w}x{h} → {new_w}x{new_h}")

            # Convertir en RGB si nécessaire (certains formats ont des canaux alpha ou palette)
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            raw_bytes = buffer.getvalue()
        else:
            print("  ℹ️  Pillow non installé (pip install pillow). Image envoyée telle quelle.")

        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        print(f"  ✅ Image encodée : {len(b64):,} caractères base64")
        return b64

    except Exception as e:
        print(f"  ❌ Erreur chargement image : {e}")
        return None


def extract_image_path(text: str) -> str | None:
    """
    Essaie de trouver un chemin de fichier image dans le texte.
    Retourne le premier chemin valide trouvé, ou None.
    """
    # Stratégie simple : on regarde si un token du texte est un chemin existant
    # On teste aussi le texte entier (chemins avec espaces)
    candidates = [text.strip()]

    # Découper par guillemets pour attraper les chemins avec espaces
    for delim in ('"', "'", "`"):
        parts = text.split(delim)
        # Les chemins sont souvent entre guillemets
        for i in range(1, len(parts), 2):
            candidates.append(parts[i].strip())

    # Découper par espaces pour les chemins sans espaces
    candidates.extend(text.split())

    for c in candidates:
        if not c:
            continue
        # Nettoyer les quotes restants
        c = c.strip("'\"")
        if os.path.exists(c) and is_image_file(c):
            return c
    return None


def send_message(history: list, user_text: str, image_b64: str | None = None) -> str:
    """
    Envoie un message à Ollama (modèle vision).
    Si image_b64 est fourni, l'ajoute au message utilisateur.
    Retourne la réponse texte de l'IA.
    """
    msg = {"role": "user", "content": user_text}
    if image_b64:
        msg["images"] = [image_b64]

    history.append(msg)

    # Limiter la taille de l'historique (les images base64 sont énormes en mémoire contextuelle)
    while len(history) > MAX_HISTORY_LEN * 2:
        # On retire les deux plus vieux messages (question + réponse)
        # Mais on ne retire jamais le premier message s'il contient une image,
        # sinon l'IA perd le contexte visuel. C'est une heuristique simple.
        removed = history.pop(0)
        # Si on a retiré l'image initiale, l'IA deviendra "aveugle" pour les questions suivantes.
        # On affiche un avertissement si c'est le cas.
        if removed.get("images"):
            print("  ⚠️  L'image initiale a été retirée de l'historique (mémoire pleine).")
            print("     Tapez !load pour recharger l'image si vous posez encore des questions dessus.")

    try:
        response = ollama.chat(model=MODEL_VISION, messages=history)
        reply = response.message.content or "(pas de réponse)"
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        err_msg = f"[ERREUR Ollama] {e}"
        history.append({"role": "assistant", "content": err_msg})
        return err_msg


def main():
    print_header()

    if not HAS_OLLAMA:
        print("\n❌ Le module 'ollama' Python n'est pas installé.")
        print("   Tapez :  pip install ollama")
        sys.exit(1)

    if not HAS_PIL:
        print("\n⚠️  Pillow non installé. L'agent fonctionnera mais ne pourra pas redimensionner les images.")
        print("   Tapez :  pip install pillow")

    history = []
    current_image_b64: str | None = None
    current_image_path: str | None = None

    while True:
        try:
            user_input = input("\nVous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break

        if not user_input:
            continue

        # --- Commandes spéciales ---
        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print("Au revoir !")
            break

        if user_input.lower() == "!clear":
            history.clear()
            current_image_b64 = None
            current_image_path = None
            print("  🧹 Image et historique effacés.")
            continue

        if user_input.lower() == "!info":
            print(f"  ℹ️  Modèle : {MODEL_VISION}")
            if current_image_path:
                print(f"  🖼️  Image chargée : {current_image_path}")
            else:
                print("  🖼️  Aucune image chargée.")
            print(f"  📜 Historique : {len(history)} messages")
            continue

        if user_input.lower().startswith("!load "):
            path = user_input[6:].strip().strip('"\'')
            b64 = encode_image(path)
            if b64:
                current_image_b64 = b64
                current_image_path = path
                # Réinitialiser l'historique pour repartir sur une nouvelle image
                history.clear()
                print(f"  ✅ Image chargée : {path}")
                print("  💬 Posez maintenant votre question sur cette image.")
            else:
                print("  ❌ Échec du chargement.")
            continue

        # --- Détection automatique d'un chemin d'image dans la phrase ---
        auto_path = extract_image_path(user_input)
        if auto_path and auto_path != current_image_path:
            print(f"  📁 Image détectée dans votre message : {auto_path}")
            b64 = encode_image(auto_path)
            if b64:
                current_image_b64 = b64
                current_image_path = auto_path
                history.clear()
                print("  ✅ Image chargée. Posez votre question.")
            # On ne continue pas ici : l'utilisateur a peut-être aussi posé une question dans le même texte.
            # Exemple : "Décris cette image C:\\Users\\photo.jpg"
            # On retire le chemin du texte pour ne pas le confondre avec la question ?
            # Non, on peut laisser le chemin, le modèle vision est habitué aux chemins dans le texte.
            # Sauf si on veut être propre. Gardons simple : on envoie le texte tel quel avec l'image.

        # --- Vérifier qu'on a une image ---
        if current_image_b64 is None:
            # Pas d'image : est-ce une question sans image ?
            # On peut quand même envoyer (le modèle vision répondra en texte, mais moins bien que Qwen)
            print("  ℹ️  Aucune image chargée. Utilisez !load <chemin> ou glissez un chemin d'image.")
            print("  💡 Je vais quand même envoyer votre message au modèle (mode texte basique).")

        # --- Envoyer à l'IA ---
        print("  ⏳ L'agent analyse...")
        reply = send_message(history, user_input, current_image_b64)
        print(f"\nAgent > {reply}")


if __name__ == "__main__":
    main()
