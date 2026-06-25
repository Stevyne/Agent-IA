# 🛡️ Explication de `agent_git.py` — L'agent qui vous aide à publier sur GitHub

> Ce document explique chaque partie du code comme si vous n'aviez jamais programmé.

---

## 🎭 Quel est le rôle de cet agent ?

Jusqu'ici, vos agents (`agent_documents.py`, etc.) parlaient à **Ollama** (l'IA sur votre GPU).

`agent_git.py` est différent : il est **gardien du château** et **chef d'orchestre**. Il ne parle pas à une IA. Il **donne des ordres à votre ordinateur** (via le terminal) et **vérifie que vous ne faites pas d'erreur** avant de publier.

---

## 🏰 Analogie : le Maître d'ouvrage d'un chantier

Imaginez que vous voulez construire une maison et l'ouvrir au public (GitHub). Vous avez :
- Des **plans publics** (votre code Python) que tout le monde peut voir
- Des **photos privées** (votre dossier `documents/`, vos conversations `memory.json`) que vous ne voulez JAMAIS montrer

`agent_git.py` est le **maître d'ouvrage** qui :
1. Vérifie que vous avez les bonnes portes et murs (`.gitignore`)
2. Compte les pièces avant d'ouvrir (vérification des fichiers sensibles)
3. Donne les ordres aux ouvriers (`git init`, `git add`, `git commit`, `git push`)
4. **Bloque l'ouverture au public** si une photo privée traîne encore dans le salon

---

## 🔧 Partie 1 : Les outils de base (les couleurs et le couteau suisse)

```python
import subprocess
import os
import sys
```

- **`subprocess`** : La boîte qui permet de **donner des ordres au terminal** de votre ordinateur. C'est comme un interphone entre Python et le système.
- **`os`** : La boîte qui sait **où vous êtes** sur l'ordinateur (dans quel dossier), et si un fichier existe.
- **`sys`** : La boîte qui permet de **quitter proprement** le programme.

---

## 🎨 Les fonctions `header()`, `ok()`, `warn()`, `err()`, `info()`

Ce sont des **raccourcis d'affichage**. C'est comme avoir des étiquettes colorées pour vos dossiers :

```python
def ok(msg):
    print(f"  ✅ {msg}")
```

Quand on écrit `ok("Git détecté")`, ça affiche : `✅ Git détecté`

| Fonction | Emoji | Rôle | Analogie |
|---|---|---|---|
| `ok()` | ✅ | Tout va bien | Tampon vert sur un dossier |
| `warn()` | ⚠️ | Attention, vérifiez | Tampon orange |
| `err()` | ❌ | Problème bloquant | Tampon rouge, STOP |
| `info()` | ℹ️ | Information utile | Post-it jaune |
| `header()` | = | Titre de section | Pancarte de chantier |

---

## 🔧 Partie 2 : `run()` — Le couteau suisse

```python
def run(cmd, capture=True, check=False):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture,
        text=True,
        check=check
    )
    return result
```

C'est la **fonction la plus importante**. Elle exécute une commande du terminal.

### Détail ligne par ligne

**`subprocess.run(...)`** : C'est l'interphone. On dit à l'ordinateur : *"Exécute cette commande pour moi."*

**`cmd`** : Le texte de la commande. Par exemple `"git --version"` ou `"git status"`.

**`shell=True`** : On dit à l'ordinateur d'utiliser le **terminal** (l'interprète de commandes) pour comprendre la phrase. Sans ça, Python ne comprendrait pas `git`.

**`capture_output=True`** : Au lieu d'afficher le résultat n'importe où dans le terminal, on le **capture** dans une boîte (la variable `result`).

**`text=True`** : On veut du texte lisible, pas des 0 et 1 binaires.

**`check=False`** : Si la commande échoue (ex: `git` n'est pas installé), on ne veut pas que le programme **explose**. On veut juste savoir que ça a raté.

### Ce que retourne `result`

`result` est un objet avec 3 choses dedans :
- `result.returncode` : Le code de retour. `0` = succès. `1` (ou autre) = échec.
- `result.stdout` : Le texte normal retourné par la commande (ex: `git version 2.45.0`).
- `result.stderr` : Le texte d'erreur (ex: `git: commande introuvable`).

> **Analogie** : C'est comme envoyer un courrier recommandé. `returncode` = le récépissé (0 = livré, 1 = refusé). `stdout` = la réponse du destinataire. `stderr` = le message du facteur disant "adresse inconnue".

---

## 🔍 Partie 3 : `check_git_installed()` — Le vigile à l'entrée

```python
def check_git_installed():
    result = run("git --version")
    if result.returncode == 0:
        ok(f"Git détecté : {result.stdout.strip()}")
        return True
    else:
        err("Git n'est pas installé...")
        return False
```

**Ce qu'il fait** : Il envoie un petit message à l'ordinateur : *"Quelle est la version de Git ?"*

- Si Git répond (`returncode == 0`), c'est que le logiciel est installé. On affiche la version et on dit "OK".
- Si Git ne répond pas (`returncode != 0`), c'est que Git n'est pas sur l'ordinateur. On affiche une erreur et on arrête.

> **Analogie** : C'est comme appeler le concierge pour savoir si le gardien est en poste. S'il répond au téléphone, tout va bien. S'il ne répond pas, la sécurité ne peut pas fonctionner.

---

## 🏠 Partie 4 : `check_git_repo()` — Le plan de la maison existe-t-il ?

```python
def check_git_repo():
    if os.path.exists(".git"):
        ok("Dossier Git initialisé")
        return True
    warn("Aucun dossier .git trouvé")
    return False
```

**`.git`** est un dossier caché que Git crée quand on fait `git init`. C'est le **plan d'architecte** de votre maison. S'il n'existe pas, vous ne pouvez pas construire.

**`os.path.exists(".git")`** : C'est comme demander : *"Le plan d'architecte est-il sur le bureau ?"*

---

## 📝 Partie 5 : `check_gitignore_exists()` — La porte de la chambre privée existe-t-elle ?

```python
def check_gitignore_exists():
    if os.path.exists(".gitignore"):
        ok("Fichier .gitignore présent")
        return True
    warn("Fichier .gitignore MANQUANT !")
    return False
```

Le fichier `.gitignore` est la **liste des pièces interdites au public**. Si cette liste n'existe pas, n'importe qui peut entrer dans la chambre privée.

---

## 🔐 Partie 6 : `check_gitignore_content()` — Le vigile lit la liste des pièces interdites

```python
def check_gitignore_content():
    with open(".gitignore", "r") as f:
        content = f.read()

    required = {
        "documents/": False,
        "memory.json": False,
        "chroma_db": False,
        "venv/": False,
        "__pycache__/": False,
    }
```

### Le dictionnaire `required`

C'est une **liste de courses** avec des cases à cocher. Au début, toutes les cases sont décochées (`False`).

```python
    for line in content.splitlines():
        line = line.strip()
        for key in required:
            if key in line and not line.startswith("#"):
                required[key] = True
```

On lit le fichier `.gitignore` **ligne par ligne** :
1. `content.splitlines()` : Coupe le texte à chaque ligne. C'est comme prendre une feuille et la découper en bandelettes.
2. `line.strip()` : Enlève les espaces au début et à la fin. C'est comme épousseter.
3. `line.startswith("#")` : Si la ligne commence par `#`, c'est un **commentaire** (ex: `# Ceci est privé`). On ignore les commentaires.
4. `if key in line` : Si la ligne contient `documents/`, on coche la case `documents/`

```python
    missing = [k for k, v in required.items() if not v]
```

C'est une **liste de toutes les cases restées décochées**. Si `documents/` n'a pas été trouvé dans le fichier, il est dans `missing`.

> **Analogie** : C'est comme le vigile qui vérifie que la liste des pièces interdites contient bien : "Salle des documents", "Coffre memory.json", "Cave chroma_db", "Remise venv", "Garage __pycache__". Si un élément manque, il sonne l'alarme.

---

## 🚨 Partie 7 : `check_sensitive_tracked()` — Le vigile ouvre TOUTES les portes pour vérifier

```python
def check_sensitive_tracked():
    result = run("git ls-files")
    if result.returncode != 0:
        return False

    tracked = result.stdout.splitlines()
```

**`git ls-files`** : C'est une commande magique de Git qui dit : *"Liste-moi TOUS les fichiers que tu suis actuellement."* C'est comme demander au gardien : *"Montre-moi la liste des pièces que tu as ouvertes au public."*

```python
    dangerous = []
    for f in tracked:
        if f.startswith("documents/") or f == "memory.json" or f.startswith("chroma_db"):
            dangerous.append(f)
```

On inspecte chaque fichier de la liste :
- `f.startswith("documents/")` : Le fichier est dans le dossier `documents/` ?
- `f == "memory.json"` : Le fichier est exactement `memory.json` ?
- `f.startswith("chroma_db")` : Le fichier commence par `chroma_db` (donc `chroma_db/` ou `chroma_db_docs/`) ?

Si **un seul** de ces cas est vrai, le fichier est **dangereux** et on l'ajoute à la liste `dangerous`.

```python
    if dangerous:
        err("🚨 ALERTE SÉCURITÉ : des fichiers sensibles sont suivis par Git !")
        for f in dangerous:
            print(f"     ❌ {f}")
```

Si la liste `dangerous` n'est pas vide, on affiche un **message rouge** avec chaque fichier dangereux.

> **Analogie** : Le vigile fait le tour de toutes les pières. S'il trouve une photo privée encore affichée dans le salon, il crie : "🚨 ALERTE ! On voit encore `contrat.pdf` dans la vitrine !"

---

## 🧹 Partie 8 : `do_remove_sensitive()` — Le vigile retire les photos privées du salon

```python
def do_remove_sensitive():
    result = run("git ls-files")
    tracked = result.stdout.splitlines()
    to_remove = [f for f in tracked if f.startswith("documents/") or ...]
```

On refait la liste des fichiers dangereux.

```python
        for f in to_remove:
            r = run(f'git rm -r --cached "{f}"')
```

**`git rm -r --cached "fichier"`** : C'est la commande magique qui dit à Git : *"Oublie ce fichier. Ne le publie pas. Mais laisse-le sur le disque dur de l'ordinateur."*

- `rm` = remove (retirer)
- `-r` = récursif (pour les dossiers entiers)
- `--cached` = **retirer de l'index Git seulement**, pas de l'ordinateur

> **Analogie** : Le vigile enlève la photo du mur du salon (`--cached`), mais la remet dans le tiroir de la chambre (votre disque dur). La photo existe toujours chez vous, mais les visiteurs ne la verront plus.

```python
        r = run(f'git commit -m "{msg}"')
```

On crée un **commit** (une photo de l'état actuel) pour dire : *"J'ai nettoyé le salon. Voici le nouveau état."*

---

## 📦 Partie 9 : `do_add_files()` — Le tri sélectif des cartons

```python
def do_add_files():
    result = run("git status --short")
    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
```

**`git status --short`** : Affiche la liste des fichiers qui ont changé, en format court. C'est comme le gardien qui dit : *"Voici les nouveaux objets qui traînent dans l'entrée."*

```python
    print("  - 'a' pour tout ajouter")
    print("  - 'n' pour ne rien ajouter")
    print("  - '1 2 5' pour ajouter seulement certains fichiers")
    print("  - 'p' pour ajouter un par un avec confirmation")
```

L'agent vous propose **4 modes** :

| Mode | Analogie | Quand l'utiliser ? |
|---|---|---|
| **`a`** (all) | Mettre tous les cartons dans le camion | Seulement si vous êtes sûr qu'il n'y a pas de fichiers sensibles |
| **`n`** (none) | Ne rien emporter | Si vous hésitez |
| **`1 2 5`** | Choisir les cartons 1, 2 et 5 | Si vous voulez un contrôle précis |
| **`p`** (progressif) | Ouvrir chaque carton un par un et demander "celui-là ?" | Le plus sûr, surtout au début |

```python
        for i, line in enumerate(lines, 1):
            filename = line[3:] if len(line) > 3 else line
            ans = prompt(f"Ajouter '{filename}' ? (o/n) : ")
```

`line[3:]` : En mode court, `git status` affiche `?? fichier.py`. On enlève les 3 premiers caractères (`?? `) pour obtenir le vrai nom du fichier.

> **Analogie** : C'est comme trier vos affaires avant un déménagement. Le vigile ouvre chaque carton et demande : "On emporte celui-ci ?" Si vous dites non, il reste chez vous.

---

## 💾 Partie 10 : `do_commit()` — Le sceau sur les cartons

```python
def do_commit():
    r = run("git diff --cached --name-only")
    if r.returncode != 0 or not r.stdout.strip():
        info("Rien à committer")
        return
```

**`git diff --cached --name-only`** : Liste les fichiers qui sont dans le **camion** (l'index Git) mais pas encore scellés. C'est le vigile qui dit : *"Voici ce qui est prêt à partir."*

```python
    msg = prompt("Message du commit : ")
    result = run(f'git commit -m "{msg}"')
```

**`git commit -m "message"`** : C'est le **sceau officiel**. On prend une photo de l'état actuel du camion et on écrit sur la photo : *"Ajout de l'agent PDF"*. Cette photo reste dans l'historique pour toujours.

---

## 🔗 Partie 11 : `do_connect_github()` — Connecter le camion à la route publique

```python
    r = run("git remote -v")
    if r.returncode == 0 and r.stdout.strip():
        info("Remote déjà configuré")
```

**`git remote -v`** : Vérifie si le camion est déjà connecté à une route (GitHub). Le "remote" c'est l'adresse de destination.

```python
    url = prompt("Collez l'URL du dépôt GitHub : ")
    r = run(f'git remote add origin "{url}"')
```

On ajoute l'adresse GitHub comme destination. `origin` est le nom standard de la route principale.

```python
        r2 = run(f'git remote set-url origin "{url}"')
```

Si la route `origin` existe déjà, on la **remplace** par la nouvelle adresse (`set-url`).

> **Analogie** : C'est comme programmer le GPS du camion. On dit : "La destination principale s'appelle `origin` et elle est à l'adresse `https://github.com/...`"

---

## 🚀 Partie 12 : `do_push()` — Le départ du camion

```python
def do_push():
    if not check_git_repo(): return
    if not check_gitignore_exists(): return
    if not check_gitignore_content(): return
    if not check_sensitive_tracked(): return
```

**Les 4 barrières de sécurité** (une après l'autre) :
1. La maison a-t-elle un plan ? (`.git` existe)
2. La liste des pièces interdites existe-t-elle ? (`.gitignore` présent)
3. La liste est-elle complète ? (`.gitignore` contient les bonnes règles)
4. Y a-t-il encore des photos privées dans le salon ? (aucun fichier sensible suivi)

**Si UNE SEULE barrière tombe**, la fonction s'arrête immédiatement (`return`). Le camion ne part pas.

```python
    ans = prompt("Toutes les vérifications OK. Pousser ? (o/n) : ")
    if ans not in ("o", "oui", "y", "yes"):
        info("Push annulé.")
        return
```

Même après les 4 vérifications, l'agent demande encore une **confirmation humaine**.

```python
    r_branch = run("git branch --show-current")
    branch = r_branch.stdout.strip()
    result = run(f"git push -u origin {branch}")
```

**`git branch --show-current`** : Demande "Sur quelle voie (branche) sommes-nous ?" (généralement `main` ou `master`).

**`git push -u origin {branch}`** : Envoie le camion sur la route `origin`, voie `{branch}`. Le `-u` dit au GPS de se souvenir de cette route pour la prochaine fois.

---

## 🎮 Partie 13 : `menu()` et `main()` — Le tableau de bord

```python
def menu():
    print("\n" + "=" * 60)
    print("  🛡️  AGENT GITHUB")
    print("=" * 60)
    print("  1. 🔧 Initialiser Git")
    print("  2. 📝 Ajouter .gitignore")
    ...
```

C'est simplement le **tableau de bord** qui s'affiche à l'écran avec les numéros des options.

```python
def main():
    if not check_git_installed():
        prompt("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
```

Au démarrage, on vérifie que Git est installé. Sinon, on arrête immédiatement (`sys.exit(1)`). Le `1` signifie "erreur" (le `0` signifierait "succès").

```python
    while True:
        menu()
        choice = prompt("Votre choix : ")

        if choice == "1":
            do_git_init()
        elif choice == "2":
            do_add_gitignore()
        ...
        elif choice == "0":
            break
```

C'est la **boucle infinie** du menu. Tant que vous ne tapez pas `0`, le programme reste ouvert et vous propose les options. C'est comme le menu d'un distributeur automatique.

```python
        else:
            warn("Choix non reconnu")
```

Si vous tapez `42` ou `abc`, le distributeur dit : *"Je ne connais pas ce bouton."*

---

## 🧪 Partie 14 : `audit_complet()` — L'inspection générale

```python
def audit_complet():
    header("AUDIT COMPLET")
    all_ok = True

    if not check_git_installed(): all_ok = False
    if not check_git_repo(): all_ok = False
    if not check_gitignore_exists(): all_ok = False
    if not check_gitignore_content(): all_ok = False
    if not check_sensitive_tracked(): all_ok = False

    if all_ok:
        ok("🎉 TOUT EST VERT !")
    else:
        warn("🔴 Des problèmes ont été détectés")
```

C'est le **bilan de santé complet**. On passe toutes les vérifications d'affilée. Si toutes réussissent, on affiche le feu vert. Sinon, le feu rouge avec les détails.

> **Analogie** : C'est le contrôle technique complet du camion avant le départ. On vérifie les pneus, les freins, le chargement, la destination. Si tout est vert, on peut rouler.

---

## 🗺️ Récapitulatif du voyage d'une commande dans `agent_git.py`

```
Vous tapez "8" (Pousser sur GitHub)
    ↓
main() lit votre choix et appelle do_push()
    ↓
do_push() appelle 4 vérifications (barrières de sécurité)
    ↓
Chaque vérification utilise run("git ...") pour interroger le système
    ↓
subprocess.run() exécute la commande dans le terminal réel
    ↓
Le résultat revient (returncode, stdout, stderr)
    ↓
L'agent analyse et affiche ✅, ⚠️ ou ❌
    ↓
Si tout est vert → confirmation humaine → git push
    ↓
Le code est sur GitHub, vos documents restent chez vous
```

---

## 🎓 Pourquoi cet agent est différent des autres

| Agent | Il parle à... | Il utilise... | Son rôle |
|---|---|---|---|
| `agent_terminal.py` | Ollama (GPU) | `ollama.chat()` | Répondre à vos questions |
| `agent_documents.py` | Ollama (GPU) | `ollama.chat()` + ChromaDB | Lire vos documents |
| `agent_git.py` | Votre ordinateur | `subprocess.run()` | Vérifier, protéger, publier |

`agent_git.py` n'a **pas besoin d'IA**. C'est un agent "classique" : il suit des règles strictes (si le fichier est sensible → bloquer). Il est **intelligent par sa logique**, pas par un modèle de langage.

---

**Vous avez maintenant toutes les clés pour comprendre votre arsenal d'agents !** 🎉
