# 🎓 Cours : Comment fonctionne votre Agent IA (expliqué comme si vous aviez 5 ans)

---

## 🏠 L'analogie du restaurant (pour comprendre l'architecture)

Imaginez que vous voulez manger dans un restaurant. Voici qui fait quoi dans votre projet :

| Élément technique | Rôle | Analogie restaurant |
|---|---|---|
| **Votre PC / GPU** | La machine qui fait les calculs | **La cuisine** avec ses fourneaux |
| **Ollama** | Le logiciel qui fait tourner le modèle | **Le chef cuisinier** |
| **Le modèle Qwen 2.5** | Le cerveau artificiel (fichier de 2 à 8 Go) | **Le livre de recettes** du chef |
| **Python (nos fichiers)** | Le programme qui gère la conversation | **Le serveur en salle** qui prend les commandes |
| **Vous (l'utilisateur)** | La personne qui pose des questions | **Le client** qui commande |

**Le déroulement :**
1. Vous dites au serveur : *"Quelle heure est-il ?"*
2. Le serveur (Python) transmet au chef (Ollama)
3. Le chef (Ollama) lit son livre de recettes (Qwen 2.5) et réfléchit
4. Le chef répond au serveur
5. Le serveur vous annonce la réponse

---

## 🧠 Concept 1 : Pourquoi l'IA a besoin d'"outils" ?

### Le problème
Le modèle d'IA (Qwen) est comme un **étudiant très intelligent qui a passé son examen en 2024**.
- Il est très cultivé, mais il ne sait pas quelle heure il est **maintenant** (son examen date de l'année dernière).
- Il est mauvais en maths exactes (il prédit des mots, il ne calcule pas comme une calculatrice).
- Il est enfermé dans son livre : il ne peut pas sortir de votre ordinateur pour regarder une horloge.

### La solution : on lui donne des outils
On lui dit : *"Tu ne sais pas compter ? Pas de souci. Voici une calculatrice. Tu ne sais pas l'heure ? Voici une montre. Si tu en as besoin, demande-moi."*

C'est exactement ce que fait le **Tool Calling** (appel d'outils).

---

## 🔧 Concept 2 : Les 3 outils de notre boîte à outils

Regardons la "boîte à outils" que nous avons préparée :

```python
def calculer(expression: str) -> str:
    ...

def heure_actuelle() -> str:
    ...
```

### `def` = "Je crée une machine"
En Python, `def` signifie **"définir"**. C'est comme construire une petite machine qui fait une tâche précise.

- `calculer` = **La calculatrice** 🧮
  - Elle prend un texte (ex: `"15 * 4 + 2"`)
  - Elle calcule le résultat exact (62)
  - Elle retourne le résultat

- `heure_actuelle` = **La montre connectée** ⌚
  - Elle ne prend rien en entrée (pas besoin de texte)
  - Elle regarde l'horloge de votre PC
  - Elle retourne la date et l'heure exactes

### `AVAILABLE_FUNCTIONS` = L'établi où sont rangés les outils
```python
AVAILABLE_FUNCTIONS = {
    "calculer": calculer,
    "heure_actuelle": heure_actuelle,
}
```
C'est une **boîte avec des étiquettes**. Quand l'IA demande "calculer", le programme sait où trouver la machine calculatrice.

### `TOOLS` = Le menu que l'on montre à l'IA
```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique simple...",
            ...
        }
    }
]
```
C'est comme un **menu** que le serveur montre au chef : *"Voici ce que vous pouvez commander au client. Il a le droit d'utiliser la calculatrice ou la montre."*

Ce `TOOLS` est écrit en **JSON** (un langage de description très structuré). L'IA lit ce menu pour comprendre ce qu'elle a le droit de faire.

---

## 🔄 Concept 3 : La boucle de conversation (la magie du Tool Calling)

Voici le cœur du programme. C'est la danse entre vous, Python et l'IA.

### Scénario 1 : Vous posez une question simple
**Vous** : "Bonjour !"

1. Python envoie à Ollama : *"L'utilisateur a dit : Bonjour !"*
2. Ollama (l'IA) réfléchit et répond : *"Bonjour ! Comment puis-je vous aider ?"*
3. Python vous affiche la réponse.

→ **Pas besoin d'outil.** L'IA répond directement.

---

### Scénario 2 : Vous demandez l'heure
**Vous** : "Quelle heure est-il ?"

1. Python envoie à Ollama : *"L'utilisateur demande l'heure. Voici les outils que tu peux utiliser : [calculer, heure_actuelle]."*
2. Ollama réfléchit : *"Je ne connais pas l'heure actuelle. Je vais utiliser l'outil heure_actuelle."*
3. Ollama ne répond PAS en français. Il répond avec une **commande technique** :
   ```json
   {"name": "heure_actuelle", "arguments": {}}
   ```
   C'est comme s'il disait au serveur : *"Va chercher la montre pour moi."*
4. Python reçoit cette commande. Il regarde dans `AVAILABLE_FUNCTIONS`, trouve la machine `heure_actuelle()`, l'exécute.
5. La machine retourne : `"mercredi 18 juin 2026, 14:30:00"`
6. Python envoie à Ollama : *"L'utilisateur a demandé l'heure. Le résultat de l'outil est : mercredi 18 juin 2026, 14:30:00. Formule une réponse agréable."*
7. Ollama réfléchit et répond : *"Il est mercredi 18 juin 2026, 14:30:00."*
8. Python affiche cette phrase à l'écran.

---

### Scénario 3 : Vous demandez un calcul
**Vous** : "Calcule 145 * 28 + 12"

1. Python envoie à Ollama : *"L'utilisateur demande : Calcule 145 * 28 + 12. Tu peux utiliser des outils."*
2. Ollama réfléchit : *"C'est un calcul. Je ne suis pas sûr de mon résultat. Je vais utiliser la calculatrice."*
3. Ollama envoie une commande technique :
   ```json
   {"name": "calculer", "arguments": {"expression": "145 * 28 + 12"}}
   ```
   Il dit au serveur : *"Utilise la calculatrice avec le texte '145 * 28 + 12'."*
4. Python exécute `calculer("145 * 28 + 12")` → obtient `4072`
5. Python renvoie à Ollama : *"Le résultat est 4072."*
6. Ollama répond : *"145 × 28 + 12 = 4072."*
7. Python affiche la réponse.

---

## 📜 Explication ligne par ligne : `agent_terminal.py`

```python
import ollama
import re
from datetime import datetime
```

- `import ollama` : On "ouvre" la boîte qui permet de parler à Ollama. C'est comme brancher le téléphone entre le serveur (Python) et la cuisine (Ollama).
- `import re` : On importe un outil pour vérifier du texte. **Re** = **R**egular **E**xpressions (expressions régulières). C'est comme une loupe qui inspecte chaque caractère d'un texte pour s'assurer qu'il ne contient que des chiffres et des symboles mathématiques.
- `from datetime import datetime` : On importe l'horloge du système. C'est comme accrocher une vraie montre au mur du restaurant.

---

```python
MODEL = "qwen2.5:3b"
```

C'est **le nom du livre de recettes** que le chef va utiliser. `qwen2.5:3b` signifie :
- **Qwen** : le nom de l'IA (créée par Alibaba)
- **2.5** : la version du livre
- **3b** : la taille du cerveau (3 milliards de paramètres). Un petit livre = rapide à lire, tient dans une petite cuisine (6 Go de VRAM).

---

```python
def calculer(expression: str) -> str:
    if not re.match(r'^[0-9+\-*/.() ]+$', expression):
        return "Erreur : caractères non autorisés..."
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Erreur de calcul : {e}"
```

**Création de la calculatrice.**
- `expression: str` : La machine attend un **texte** (ex: "15 + 3")
- `-> str` : La machine rend un **texte** en retour (ex: "18")
- `re.match(...)` : La loupe inspecte le texte. Si elle trouve une lettre ou un symbole bizarre (ex: `abc` ou `rm -rf`), elle refuse. C'est une **sécurité** : on ne veut pas que quelqu'un écrive du code malveillant dans la calculatrice.
- `eval(expression)` : C'est le bouton "=" de la calculatrice. Il calcule le résultat.
- `try / except` : C'est une **bouée de sauvetage**. Si le calcul échoue (ex: division par zéro), le programme ne plante pas. Il attrape l'erreur et affiche un message gentil.

---

```python
def heure_actuelle() -> str:
    return datetime.now().strftime("%A %d %B %Y, %H:%M:%S")
```

**Création de la montre.**
- `datetime.now()` : Regarde l'horloge interne du PC et lit la date/heure exacte de maintenant.
- `.strftime(...)` : Formate la lecture brute en texte lisible. `%A` = jour de la semaine, `%d` = numéro du jour, `%B` = mois, `%Y` = année, `%H:%M:%S` = heure:minute:seconde.

---

```python
AVAILABLE_FUNCTIONS = {
    "calculer": calculer,
    "heure_actuelle": heure_actuelle,
}
```

**L'établi.** C'est un dictionnaire (une liste avec des noms). Quand l'IA dit "calculer", Python cherche ici et trouve la machine correspondante.

---

```python
TOOLS = [ ... ]
```

**Le menu présenté à l'IA.** C'est très long car c'est du JSON structuré. On y décrit chaque outil :
- Son nom (`calculer`)
- Sa description (pour que l'IA comprenne quand l'utiliser)
- Ses paramètres (quel texte il faut donner à la machine)

L'IA lit ce menu avant de répondre. Si elle pense qu'un outil est utile, elle demande à l'utiliser.

---

```python
def run_agent(user_msg: str) -> str:
```

**La fonction principale.** C'est le "maître d'hôtel" qui orchestre toute la conversation.
- Il prend le message de l'utilisateur
- Il gère la danse avec Ollama
- Il retourne la réponse finale

---

```python
    messages = [{"role": "user", "content": user_msg}]
```

**L'historique de la conversation.** C'est une liste de messages. Chaque message a :
- un `role` : qui parle (`user` = vous, `assistant` = l'IA, `tool` = le résultat d'un outil)
- un `content` : le texte dit

On commence avec seulement votre message.

---

```python
    response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
```

**L'appel au chef.** Python dit à Ollama :
- "Utilise le modèle Qwen 2.5"
- "Voici l'historique de la conversation"
- "Voici le menu des outils disponibles"

Ollama réfléchit et répond.

---

```python
    while response.message.tool_calls:
```

**La boucle magique.**
`while` = "Tant que...". Tant que la réponse d'Ollama contient une **demande d'outil** (`tool_calls`), on répète les étapes suivantes.

C'est une boucle car il peut y avoir plusieurs outils demandés d'un coup, ou plusieurs tours si l'IA a besoin de plusieurs résultats.

---

```python
        assistant_msg = {
            "role": "assistant",
            "content": response.message.content or "",
            "tool_calls": [ ... ]
        }
        messages.append(assistant_msg)
```

On ajoute à l'historique ce que l'IA a dit. Mais attention : si l'IA demande un outil, son "contenu" (`content`) est souvent vide. C'est normal. L'important est dans `tool_calls` : c'est sa commande technique.

On ajoute ce message à l'historique pour que la conversation reste cohérente.

---

```python
        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments or {}
            func = AVAILABLE_FUNCTIONS.get(func_name)
```

On lit la commande de l'IA :
- `func_name` = le nom de l'outil demandé (ex: `"calculer"`)
- `func_args` = les arguments (ex: `{"expression": "15+3"}`)
- `func = AVAILABLE_FUNCTIONS.get(...)` = on va chercher la machine dans l'établi

---

```python
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
```

On exécute la machine :
- Si la machine n'existe pas → erreur
- Si la machine existe :
  - `func(**func_args)` = on lance la machine avec les arguments. Les `**` signifient "décompose le dictionnaire". Si `func_args` est `{"expression": "15+3"}`, alors `func(**func_args)` devient `func(expression="15+3")`.
  - Si la machine n'a pas besoin d'arguments (comme `heure_actuelle`) → on lance simplement `func()`.
  - `try / except` = bouée de sauvetage si la machine tombe en panne.

---

```python
            print(f"  [Outil: {func_name}({func_args}) -> {result}]")
            messages.append({
                "role": "tool",
                "name": func_name,
                "content": str(result)
            })
```

- On affiche dans le terminal ce qui se passe (pour que vous voyiez l'outil travailler)
- On ajoute le résultat à l'historique avec le rôle `tool` (c'est comme dire : "Le résultat de la calculatrice est 18")

---

```python
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
```

**On re-parle au chef !** Maintenant l'historique contient :
1. Votre question
2. La demande d'outil de l'IA
3. Le résultat de l'outil

Le chef relit tout et répond avec la phrase finale.

Si la phrase finale contient encore une demande d'outil, la boucle `while` recommence. Sinon, on sort.

---

```python
    return response.message.content or "(L'agent n'a pas généré de réponse)"
```

On retourne le texte final de l'IA. Le `or` est une sécurité : si l'IA n'a rien dit, on affiche un message par défaut.

---

```python
def main():
    print("=" * 60)
    print("  Agent IA local - Mode Terminal")
    ...
```

**Le hall d'accueil.** C'est ce qui s'affiche quand vous lancez le programme : le titre et les instructions.

---

```python
    while True:
        try:
            user = input("\nVous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break
```

**Boucle infinie.**
- `while True` : Répète éternellement jusqu'à ce qu'on dise d'arrêter.
- `input("Vous > ")` : Le programme s'arrête et attend que vous tapiez quelque chose au clavier.
- `.strip()` : Enlève les espaces inutiles au début et à la fin de votre texte.
- `except (EOFError, KeyboardInterrupt)` : Si vous appuyez sur `Ctrl+C` ou que vous fermez le programme, il ne plante pas. Il dit "Au revoir !" et s'arrête proprement.

---

```python
        if user.lower() in ("quit", "exit", "q", "bye"):
            print("Au revoir !")
            break
```

Si vous écrivez "quit", "exit", "q" ou "bye", le programme dit au revoir et sort de la boucle (`break`).

---

```python
        print("Agent > ", end="", flush=True)
        try:
            answer = run_agent(user)
        except Exception as e:
            answer = f"[ERREUR] {e}"
        print(answer)
```

- On affiche "Agent > " pour que vous sachiez que l'IA répond.
- `end=""` et `flush=True` : Affiche le texte immédiatement sans attendre la fin de ligne.
- On appelle notre fonction `run_agent(user)` pour obtenir la réponse.
- `try / except` : Si quelque chose explose pendant la conversation, le programme attrape l'erreur et affiche `[ERREUR]` au lieu de planter.
- On affiche la réponse.

---

```python
if __name__ == "__main__":
    main()
```

C'est une **convention Python**. Cela signifie : "Si vous exécutez ce fichier directement, lancez `main()`. Si vous importez ce fichier depuis un autre fichier, ne lancez rien automatiquement."

---

## 🌐 Explication : `app_web.py` (la version web)

Ce fichier fait **exactement la même chose** que `agent_terminal.py`, mais avec une interface graphique. Analysons les différences.

### Qu'est-ce que Streamlit ?

Streamlit est un **constructeur de sites web rapide**. Imaginez que vous voulez ouvrir un café. Au lieu de :
- Construire les murs (HTML)
- Peindre (CSS)
- Installer l'électricité (JavaScript)
- Vous louez un **local déjà meublé** où vous n'avez qu'à poser vos affiches (textes) et vos machines (fonctions Python).

Streamlit s'occupe de tout le design. Vous écrivez du Python, et il génère automatiquement une belle page web.

---

### Les nouveautés

```python
import streamlit as st
```

On importe Streamlit. `as st` est un surnom : au lieu d'écrire `streamlit.truc`, on écrit `st.truc` (plus rapide).

---

```python
st.set_page_config(page_title="Agent IA Local", page_icon="🤖", layout="centered")
```

Configure la fenêtre du navigateur : le titre de l'onglet, l'icône, et le centrage de la page.

---

```python
st.title("🤖 Agent IA Local")
st.caption(f"Modèle : `{MODEL}` | Inférence 100% locale via Ollama | GPU NVIDIA")
```

- `st.title` : Affiche le gros titre en haut de la page.
- `st.caption` : Affiche un petit texte gris sous le titre (infos techniques).

---

```python
with st.sidebar:
    st.header("⚙️ Configuration")
    ...
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.internal_history = []
        st.rerun()
```

**La barre latérale.** C'est le menu sur le côté de la page web.
- `st.sidebar` : Crée une colonne sur la gauche.
- `st.button` : Crée un bouton cliquable.
- Quand on clique le bouton "Nouvelle conversation", on vide la mémoire (`= []`) et on recharge la page (`st.rerun()`).

---

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
if "internal_history" not in st.session_state:
    st.session_state.internal_history = []
```

**La mémoire du chat.**
Quand vous rafraîchissez une page web, tout est effacé. Streamlit a inventé `session_state` : c'est une **boîte à souvenirs** qui reste ouverte tant que vous ne fermez pas l'onglet.

- `messages` : Ce que vous voyez à l'écran (les bulles de discussion). Format simple.
- `internal_history` : Ce qui est envoyé à Ollama (avec les tool calls et résultats). Format complet.

**Pourquoi deux listes ?** Parce que vous n'avez pas besoin de voir les commandes techniques (tool calls) dans la discussion. Vous voyez uniquement les messages jolis. Mais Ollama, lui, a besoin de tout l'historique technique pour répondre correctement.

---

```python
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
```

**Afficher les bulles.**
- On parcourt la liste des messages visibles.
- `st.chat_message("user")` : Crée une bulle grise à droite (comme WhatsApp).
- `st.chat_message("assistant")` : Crée une bulle blanche à gauche.
- `st.markdown` : Affiche le texte avec la mise en forme (gras, italique, etc.).

---

```python
if user_input := st.chat_input("Posez votre question..."):
```

**La barre de saisie.**
- `st.chat_input` : Crée une barre de texte en bas de l'écran (style Messenger).
- `:=` : C'est une astuce Python qui dit : "Crée la variable `user_input` ET vérifie si elle n'est pas vide en même temps."
- Si l'utilisateur a écrit quelque chose et appuyé sur Entrée, on continue.

---

```python
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
```

On affiche immédiatement la bulle de l'utilisateur et on la sauvegarde dans la mémoire visible.

---

```python
    st.session_state.internal_history.append({"role": "user", "content": user_input})
```

On ajoute aussi le message dans l'historique technique (celui envoyé à Ollama).

---

```python
    with st.chat_message("assistant"):
        with st.spinner("L'agent réfléchit..."):
            try:
                reply = run_agent_turn(st.session_state.internal_history)
            except Exception as e:
                reply = f"❌ Erreur : {e}"
        st.markdown(reply)
```

- On ouvre une bulle "assistant".
- `st.spinner` : Affiche une petite roue qui tourne avec le texte "L'agent réfléchit..." pendant que l'ordinateur calcule.
- On appelle `run_agent_turn` (la même logique que `run_agent` dans le terminal, mais adaptée à Streamlit).
- On affiche la réponse.

---

```python
    st.session_state.messages.append({"role": "assistant", "content": reply})
```

On sauvegarde la réponse dans la mémoire visible pour qu'elle reste affichée si vous posez une nouvelle question.

---

## 🗺️ Récapitulatif du voyage d'une question

```
┌─────────────────┐
│   VOUS (web)    │  "Quelle heure est-il ?"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit (UI) │  Affiche votre bulle + sauvegarde
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python (agent) │  run_agent_turn() prépare l'historique
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ollama (API)   │  "L'utilisateur demande l'heure"
│  GPU NVIDIA     │  Le modèle Qwen 2.5 réfléchit
└────────┬────────┘
         │  Demande l'outil "heure_actuelle"
         ▼
┌─────────────────┐
│  Python (agent) │  Exécute heure_actuelle() → "18 juin 2026, 14:30"
│  PC (horloge)   │  Ajoute le résultat à l'historique
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ollama (API)   │  "Le résultat est 18 juin 2026, 14:30"
│  GPU NVIDIA     │  Le modèle formule une phrase agréable
└────────┬────────┘
         │  "Il est 18 juin 2026, 14:30."
         ▼
┌─────────────────┐
│  Streamlit (UI) │  Affiche la bulle de réponse
└─────────────────┘
```

---

## ❓ Glossaire des mots compliqués rencontrés

| Mot technique | Explication simple |
|---|---|
| **API** | Un **portier** à l'entrée d'un hôtel. Vous ne parlez pas directement au chef, vous parlez au portier (API) qui transmet. |
| **GPU** | Le **cerveau visuel** de l'ordinateur. Très rapide pour les calculs en parallèle (comme l'IA). |
| **VRAM** | La **mémoire de travail** du GPU. Comme le plan de travail d'une cuisine. Si c'est trop petit, on ne peut pas préparer de gros plats. |
| **Modèle** | Le **livre de recettes** de l'IA. Un fichier énorme (plusieurs milliards de règles) appris sur Internet. |
| **Inference** | Le **acte de réfléchir** de l'IA. Quand le modèle lit votre question et prédit la réponse. |
| **Tool Calling** | Le droit pour l'IA de **demander une calculatrice** ou une **montre** quand elle est coincée. |
| **JSON** | Un **langage d'emballage** pour les données. Comme une boîte avec des étiquettes : `{"nom": "Jean", "age": 30}`. |
| **Dictionnaire** | En Python, une **boîte avec des étiquettes**. On cherche par nom, pas par numéro. |
| **Boucle** | Une **répétition**. `while` = "tant que la condition est vraie, recommence". |
| **Fonction** | Une **machine** qu'on construit une fois et qu'on peut relancer autant de fois qu'on veut. |
| **Argument / Paramètre** | Les **ingrédients** qu'on donne à une machine pour qu'elle travaille. |
| **Variable** | Une **boîte** avec un nom, dans laquelle on range une valeur. |
| **Session** | Une **séance de discussion**. Tant que vous ne fermez pas l'onglet, la session conserve la mémoire. |
| **State** | L'**état** actuel. Par exemple : "à quelle étape de la conversation on est". |

---

**Vous avez survécu au cours !** 🎉

Si vous relisez les codes avec ce document à côté, tout devient plus clair. N'hésitez pas à me demander si un passage reste obscur.
