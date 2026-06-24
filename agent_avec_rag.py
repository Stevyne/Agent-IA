"""
Agent IA capable de lire des documents (RAG).
Vous placez des fichiers .txt dans le dossier 'documents/',
et l'IA peut répondre en se basant sur leur contenu.
"""

import ollama
import os
import json
from datetime import datetime

# ================== CONFIGURATION ==================
MODEL = "qwen2.5:3b"
DOCS_FOLDER = "documents"
DB_PATH = "chroma_db"  # Dossier où ChromaDB stocke les données
# ===================================================

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

# --- Partie RAG : lecture des documents ---

def load_documents():
    """
    Lit tous les fichiers .txt du dossier 'documents/'.
    Retourne une liste de textes.
    """
    if not os.path.exists(DOCS_FOLDER):
        print(f"📁 Dossier '{DOCS_FOLDER}' non trouvé. Création...")
        os.makedirs(DOCS_FOLDER)
        return []

    texts = []
    for filename in os.listdir(DOCS_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_FOLDER, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    texts.append({
                        "source": filename,
                        "content": f.read()
                    })
                print(f"   ✅ Lu : {filename}")
            except Exception as e:
                print(f"   ❌ Erreur lecture {filename} : {e}")
    return texts


def split_text(text, chunk_size=500, overlap=100):
    """
    Découpe un texte en morceaux de 'chunk_size' caractères,
    avec un chevauchement de 'overlap' caractères.
    C'est comme couper un long film en épisodes qui se chevauchent un peu,
    pour ne pas perdre le contexte entre deux morceaux.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += (chunk_size - overlap)
    return chunks


def build_vector_database(documents):
    """
    Construit la base de données vectorielle avec ChromaDB.
    'documents' est une liste de dicts {"source": ..., "content": ...}.
    """
    import chromadb

    # Création du client ChromaDB (stockage local)
    client = chromadb.PersistentClient(path=DB_PATH)

    # On crée ou récupère une collection (une "table" de documents)
    collection = client.get_or_create_collection(name="mes_documents")

    # Si la collection est déjà remplie et que les documents n'ont pas changé,
    # on pourrait skipper. Mais pour simplifier, on vide et on réindexe.
    # (Pour un vrai projet, on comparerait les dates de modification.)
    existing = collection.count()
    if existing > 0:
        print(f"   🗑️ Base existante ({existing} chunks). Réindexation...")
        client.delete_collection(name="mes_documents")
        collection = client.get_or_create_collection(name="mes_documents")

    print("   🔨 Découpage et indexation des documents...")
    all_chunks = []
    all_ids = []
    all_metadatas = []

    id_counter = 0
    for doc in documents:
        chunks = split_text(doc["content"], chunk_size=500, overlap=100)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"id_{id_counter}")
            all_metadatas.append({"source": doc["source"], "chunk_index": i})
            id_counter += 1

    if all_chunks:
        # ChromaDB va automatiquement télécharger un petit modèle d'embedding
        # (all-MiniLM-L6-v2, ~80 Mo) pour transformer les textes en nombres.
        collection.add(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadatas
        )
        print(f"   ✅ {len(all_chunks)} morceaux indexés dans la base.")
    else:
        print("   ⚠️ Aucun document à indexer.")

    return collection


def search_documents(collection, question, n_results=3):
    """
    Cherche les 'n_results' morceaux de documents les plus pertinents
    pour la question posée.
    """
    if collection is None or collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )

    passages = []
    # results["documents"][0] contient les textes trouvés
    for i, doc in enumerate(results["documents"][0]):
        source = results["metadatas"][0][i]["source"]
        passages.append(f"[Source: {source}]\n{doc}")

    return passages


# --- Partie conversation avec RAG ---

def run_agent_rag(user_msg, collection, chat_history):
    """
    Gère un tour de conversation en injectant les documents pertinents
    dans le contexte système.
    """
    # 1. Chercher les documents pertinents
    passages = search_documents(collection, user_msg, n_results=3)

    # 2. Construire le prompt système avec les documents
    system_content = "Tu es un assistant amical."
    if passages:
        context = "\n\n---\n\n".join(passages)
        system_content += (
            "\n\nVoici des extraits de documents qui pourraient t'aider à répondre. "
            "Base-toi principalement sur ces extraits, mais tu peux aussi utiliser tes connaissances générales.\n\n"
            f"{context}"
        )
        print(f"   📚 {len(passages)} passages trouvés dans les documents.")
    else:
        print("   📚 Aucun document pertinent trouvé (réponse sans aide externe).")

    # 3. Préparer les messages
    messages = [{"role": "system", "content": system_content}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_msg})

    # 4. Appel à Ollama avec tool calling
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
            messages.append({
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })

        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)

    final = response.message.content or "(pas de réponse)"
    chat_history.append({"role": "user", "content": user_msg})
    chat_history.append({"role": "assistant", "content": final})
    return final


def main():
    print("=" * 60)
    print("  Agent IA avec mémoire de documents (RAG)")
    print(f"  Modèle : {MODEL}")
    print(f"  Dossier documents : {DOCS_FOLDER}/")
    print("=" * 60)

    # 1. Lire les documents
    print("\n📖 Lecture des documents...")
    docs = load_documents()

    if not docs:
        print(f"\n⚠️  Aucun document trouvé dans '{DOCS_FOLDER}/'")
        print("   Placez des fichiers .txt dans ce dossier et relancez.")
        print("   L'agent fonctionnera quand même, mais sans mémoire de documents.\n")
        collection = None
    else:
        # 2. Installer chromadb si besoin
        try:
            import chromadb
        except ImportError:
            print("\n❌ Le module 'chromadb' n'est pas installé.")
            print("   Tapez : pip install chromadb")
            print("   Puis relancez le programme.\n")
            return

        # 3. Construire la base vectorielle
        print("\n🔨 Construction de la base de connaissances...")
        collection = build_vector_database(docs)

    # 4. Démarrer la conversation
    chat_history = []  # Historique de la session actuelle (sans persistance ici, pour simplifier)

    print("\n💬 Posez vos questions. L'IA consulte vos documents si besoin.")
    print("   Tapez 'quit' ou 'exit' pour sortir.\n")

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
            answer = run_agent_rag(user, collection, chat_history)
        except Exception as e:
            answer = f"[ERREUR] {e}"
        print(answer)


if __name__ == "__main__":
    main()
