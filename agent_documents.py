"""
Agent IA capable de lire PDF, Word (.docx) et TXT.
Il peut rechercher dans les documents et extraire des passages précis.
"""

import ollama
import os
import json
from datetime import datetime

# ================== CONFIGURATION ==================
MODEL = "qwen2.5:3b"  # ou "qwen2.5:7b" si vous avez 8+ Go VRAM
DOCS_FOLDER = "documents"
DB_PATH = "chroma_db_docs"
# ===================================================

# --- Imports optionnels (PDF, Word) ---
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


# --- Outils classiques ---
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


def rechercher_documents(requete: str, n_resultats: int = 5) -> str:
    """
    Outil : fouille dans la base de documents (ChromaDB) et retourne
    les passages les plus pertinents avec leurs sources exactes.
    """
    global _collection
    if _collection is None:
        return "Erreur : la base de documents n'est pas initialisée."

    try:
        n_resultats = int(n_resultats)
    except Exception:
        n_resultats = 5

    if n_resultats < 1:
        n_resultats = 1
    if n_resultats > 10:
        n_resultats = 10

    try:
        results = _collection.query(
            query_texts=[requete],
            n_results=n_resultats
        )
    except Exception as e:
        return f"Erreur lors de la recherche : {e}"

    if not results or not results["documents"] or not results["documents"][0]:
        return "Aucun passage pertinent trouvé dans les documents."

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


AVAILABLE_FUNCTIONS = {
    "calculer": calculer,
    "heure_actuelle": heure_actuelle,
    "rechercher_documents": rechercher_documents,
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
    },
    {
        "type": "function",
        "function": {
            "name": "rechercher_documents",
            "description": (
                "Recherche des passages pertinents dans les documents locaux "
                "(PDF, Word, TXT). Utilise cet outil dès que l'utilisateur pose une question "
                "concernant les documents, demande un résumé, une extraction, ou cite des informations "
                "qui pourraient se trouver dans la bibliothèque."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "requete": {
                        "type": "string",
                        "description": "La question ou le sujet à chercher dans les documents (ex: 'clause de confidentialité', 'chiffre d'affaires 2024')."
                    },
                    "n_resultats": {
                        "type": "integer",
                        "description": "Nombre de passages à retourner (entre 1 et 10, défaut 5)."
                    }
                },
                "required": ["requete"]
            }
        }
    }
]


# --- Lecture des documents ---

def load_all_documents():
    """
    Lit tous les fichiers .txt, .pdf, .docx du dossier 'documents/'.
    Retourne une liste de dicts : {source, type, page, content}
    """
    if not os.path.exists(DOCS_FOLDER):
        print(f"📁 Création du dossier '{DOCS_FOLDER}/'...")
        os.makedirs(DOCS_FOLDER)
        return []

    docs = []
    files = [f for f in os.listdir(DOCS_FOLDER) if f.lower().endswith((".txt", ".pdf", ".docx"))]

    if not files:
        print(f"⚠️  Aucun fichier trouvé dans '{DOCS_FOLDER}/'")
        print("   Placez-y des fichiers .txt, .pdf ou .docx")
        return []

    for filename in files:
        filepath = os.path.join(DOCS_FOLDER, filename)
        ext = filename.lower().split(".")[-1]

        try:
            if ext == "txt":
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                # Découpage en blocs de 500 caractères avec chevauchement 100
                for i in range(0, len(text), 400):
                    chunk = text[i:i+500]
                    if chunk.strip():
                        docs.append({
                            "source": filename,
                            "type": "txt",
                            "page": i // 400,
                            "content": chunk.strip()
                        })
                print(f"   ✅ TXT lu : {filename}")

            elif ext == "pdf":
                if not HAS_PYPDF:
                    print(f"   ❌ {filename} ignoré (installez 'pypdf' : pip install pypdf)")
                    continue
                reader = PdfReader(filepath)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        # Si une page fait plus de 800 caractères, on la découpe
                        if len(text) > 800:
                            for j in range(0, len(text), 700):
                                chunk = text[j:j+800]
                                if chunk.strip():
                                    docs.append({
                                        "source": filename,
                                        "type": "pdf",
                                        "page": f"{i+1}-{j//700}",
                                        "content": chunk.strip()
                                    })
                        else:
                            docs.append({
                                "source": filename,
                                "type": "pdf",
                                "page": i + 1,
                                "content": text.strip()
                            })
                print(f"   ✅ PDF lu : {filename} ({len(reader.pages)} pages)")

            elif ext == "docx":
                if not HAS_DOCX:
                    print(f"   ❌ {filename} ignoré (installez 'python-docx' : pip install python-docx)")
                    continue
                doc = Document(filepath)
                # Regroupe les paragraphes par blocs de 500 caractères
                buffer = ""
                para_idx = 0
                block_idx = 0
                for para in doc.paragraphs:
                    txt = para.text
                    if not txt.strip():
                        continue
                    buffer += txt + "\n"
                    if len(buffer) >= 500:
                        docs.append({
                            "source": filename,
                            "type": "docx",
                            "page": f"{para_idx}-{block_idx}",
                            "content": buffer.strip()
                        })
                        buffer = ""
                        block_idx += 1
                    para_idx += 1
                if buffer.strip():
                    docs.append({
                        "source": filename,
                        "type": "docx",
                        "page": f"{para_idx}-{block_idx}",
                        "content": buffer.strip()
                    })
                print(f"   ✅ DOCX lu : {filename}")

        except Exception as e:
            print(f"   ❌ Erreur lecture {filename} : {e}")

    return docs


# --- Base de données vectorielle (ChromaDB) ---

_collection = None

def build_chroma_database(docs):
    """
    Construit (ou reconstruit) la base ChromaDB avec les documents fournis.
    """
    global _collection
    client = chromadb.PersistentClient(path=DB_PATH)
    # Supprimer l'ancienne collection si elle existe pour être sûr d'être à jour
    try:
        client.delete_collection(name="bibliotheque")
    except Exception:
        pass

    collection = client.get_or_create_collection(name="bibliotheque")

    if not docs:
        print("   ⚠️  Aucun document à indexer.")
        _collection = collection
        return collection

    all_texts = []
    all_ids = []
    all_metas = []

    for idx, d in enumerate(docs):
        all_texts.append(d["content"])
        all_ids.append(f"doc_{idx}")
        all_metas.append({
            "source": d["source"],
            "type": d["type"],
            "page": str(d["page"])
        })

    collection.add(documents=all_texts, ids=all_ids, metadatas=all_metas)
    print(f"   ✅ {len(all_texts)} morceaux indexés dans ChromaDB.")
    _collection = collection
    return collection


# --- Fonction utilitaire : parse arguments ---

def _parse_args(args):
    """Gère le cas où Ollama envoie les arguments en dict ou en string JSON."""
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            return json.loads(args)
        except Exception:
            return {}
    return {}


# --- Conversation avec tool calling ---

def run_agent(user_msg, history):
    """
    Gère un tour de conversation avec les outils (calcul, heure, recherche docs).
    history est la liste des messages de la session (list, modifiée en place).
    """
    # On injecte un message système subtil si l'historique est vide
    if not history:
        system_prompt = (
            "Tu es un assistant intelligent. Tu as accès à des outils : "
            "une calculatrice, une horloge, et une base de documents (PDF, Word, TXT). "
            "Utilise l'outil 'rechercher_documents' dès que la question de l'utilisateur "
            "concerne le contenu de ses documents, même s'il ne le précise pas explicitement. "
            "Cite toujours la source exacte (nom du fichier et page/paragraphe) quand tu utilises un document."
        )
        history.append({"role": "system", "content": system_prompt})

    history.append({"role": "user", "content": user_msg})

    response = ollama.chat(model=MODEL, messages=history, tools=TOOLS)

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

            print(f"  [Outil: {func_name}({func_args}) -> {len(str(result))} caractères]")
            history.append({
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })

        response = ollama.chat(model=MODEL, messages=history, tools=TOOLS)

    final = response.message.content or "(pas de réponse)"
    history.append({"role": "assistant", "content": final})
    return final


# --- Programme principal ---

def main():
    print("=" * 60)
    print("  🤖 Agent IA - Lecteur de documents (PDF, Word, TXT)")
    print(f"  Modèle : {MODEL}")
    print("=" * 60)

    # Vérifier les dépendances critiques
    if not HAS_CHROMADB:
        print("\n❌ Erreur : la bibliothèque 'chromadb' n'est pas installée.")
        print("   Tapez :  pip install chromadb")
        return

    missing = []
    if not HAS_PYPDF:
        missing.append("pypdf")
    if not HAS_DOCX:
        missing.append("python-docx")
    if missing:
        print(f"\n⚠️  Attention : {', '.join(missing)} non installé(s). Les fichiers correspondants seront ignorés.")
        print(f"   Tapez :  pip install {' '.join(missing)}")

    # 1. Lire les documents
    print(f"\n📖 Lecture des documents dans '{DOCS_FOLDER}/'...")
    docs = load_all_documents()

    # 2. Construire la base de données
    print("\n🔨 Indexation des documents...")
    build_chroma_database(docs)

    # 3. Démarrer la conversation
    print("\n💬 Posez vos questions. L'agent peut :")
    print("   - Répondre avec ses connaissances générales")
    print("   - Utiliser la calculatrice / l'horloge")
    print("   - Fouiller dans vos documents (PDF, Word, TXT)")
    print("   Tapez 'quit' ou 'exit' pour sortir.\n")

    chat_history = []

    while True:
        try:
            user = input("Vous > ").strip()
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
            answer = run_agent(user, chat_history)
        except Exception as e:
            answer = f"[ERREUR] {e}"
        print(answer)


if __name__ == "__main__":
    main()
