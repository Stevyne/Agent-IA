"""
🛡️ Agent GitHub — Assistant interactif pour publier votre projet en toute sécurité.

Ce script vous guide pas à pas pour :
- Vérifier que vos documents privés ne sont pas publiés
- Faire les commits et les pushes
- Connecter votre projet à GitHub

USAGE :
    python agent_git.py
"""

import subprocess
import os
import sys

# ============================
# OUTILS DE BASE (couleurs + exécution)
# ============================

def run(cmd, capture=True, check=False):
    """
    Exécute une commande shell et retourne le résultat.
    C'est le 'couteau suisse' de notre agent : il lance toutes les commandes git.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            check=check
        )
        return result
    except Exception as e:
        return type("obj", (object,), {
            "returncode": 1,
            "stdout": "",
            "stderr": str(e)
        })()


def header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def ok(msg):
    print(f"  ✅ {msg}")


def warn(msg):
    print(f"  ⚠️  {msg}")


def err(msg):
    print(f"  ❌ {msg}")


def info(msg):
    print(f"  ℹ️  {msg}")


def prompt(text):
    return input(f"\n  ➤️  {text}").strip()


# ============================
# VÉRIFICATIONS DE SÉCURITÉ (les plus importantes)
# ============================

def check_git_installed():
    """Vérifie que Git est installé sur l'ordinateur."""
    result = run("git --version")
    if result.returncode == 0:
        ok(f"Git détecté : {result.stdout.strip()}")
        return True
    else:
        err("Git n'est pas installé ou n'est pas dans le PATH.")
        info("Téléchargez Git ici : https://git-scm.com/downloads")
        return False


def check_git_repo():
    """Vérifie si on est dans un dossier Git (si git init a été fait)."""
    if os.path.exists(".git"):
        ok("Dossier Git initialisé (.git trouvé)")
        return True
    warn("Aucun dossier .git trouvé ici.")
    return False


def check_gitignore_exists():
    """Vérifie que le fichier .gitignore existe."""
    if os.path.exists(".gitignore"):
        ok("Fichier .gitignore présent")
        return True
    warn("Fichier .gitignore MANQUANT !")
    info("Créez-en un IMMÉDIATEMENT pour protéger vos documents privés.")
    return False


def check_gitignore_content():
    """
    Vérifie que .gitignore contient les règles critiques pour notre projet.
    C'est le GARDE DU CORPS de votre agent IA.
    """
    if not os.path.exists(".gitignore"):
        return False

    with open(".gitignore", "r", encoding="utf-8") as f:
        content = f.read()

    required = {
        "documents/": False,
        "memory.json": False,
        "chroma_db": False,
        "venv/": False,
        "__pycache__/": False,
    }

    for line in content.splitlines():
        line = line.strip()
        for key in required:
            if key in line and not line.startswith("#"):
                required[key] = True

    missing = [k for k, v in required.items() if not v]

    if missing:
        warn("Votre .gitignore manque de règles critiques :")
        for m in missing:
            print(f"     - {m}")
        info("Ajoutez ces lignes dans votre .gitignore avant de continuer.")
        return False
    else:
        ok("Toutes les règles de sécurité sont présentes dans .gitignore")
        return True


def check_sensitive_tracked():
    """
    VÉRIFICATION CRUCIALE : regarde si Git suit déjà des fichiers sensibles.
    Si 'documents/' ou 'memory.json' sont dans l'index Git, c'est une FUITE.
    """
    result = run("git ls-files")
    if result.returncode != 0:
        warn("Impossible de vérifier les fichiers suivis par Git.")
        return False

    tracked = result.stdout.splitlines()
    dangerous = []

    for f in tracked:
        if f.startswith("documents/") or f == "memory.json" or f.startswith("chroma_db"):
            dangerous.append(f)

    if dangerous:
        err("🚨 ALERTE SÉCURITÉ : des fichiers sensibles sont suivis par Git !")
        for f in dangerous:
            print(f"     ❌ {f}")
        info("Ces fichiers risquent d'être publiés sur GitHub.")
        info("Solution : utilisez l'option 'Retirer les fichiers sensibles de Git' dans le menu.")
        return False
    else:
        ok("Aucun fichier sensible ne suit Git (sécurité OK)")
        return True


def show_git_status():
    """Affiche le statut Git actuel (fichiers modifiés, nouveaux, etc.)."""
    result = run("git status")
    if result.returncode == 0:
        print(result.stdout)
    else:
        err(result.stderr)


# ============================
# ACTIONS GIT
# ============================

def do_git_init():
    """Initialise Git dans le dossier actuel."""
    if check_git_repo():
        info("Git est déjà initialisé ici.")
        return

    answer = prompt("Initialiser Git ici ? (o/n) : ").lower()
    if answer in ("o", "oui", "y", "yes"):
        result = run("git init", check=False)
        if result.returncode == 0:
            ok("Git initialisé avec succès !")
        else:
            err(result.stderr)
    else:
        info("Annulé.")


def do_add_gitignore():
    """Ajoute le .gitignore à l'index Git."""
    if not os.path.exists(".gitignore"):
        err("Aucun fichier .gitignore trouvé.")
        return

    result = run("git add .gitignore")
    if result.returncode == 0:
        ok(".gitignore ajouté à l'index Git.")
    else:
        err(result.stderr)


def do_add_files():
    """
    Affiche les fichiers non suivis et permet d'ajouter ceux que vous voulez.
    C'est un 'git add' interactif et sécurisé.
    """
    header("AJOUTER DES FICHIERS AU COMMIT")

    result = run("git status --short")
    if result.returncode != 0:
        err("Impossible de lire le statut Git.")
        return

    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
    if not lines:
        info("Aucun fichier à ajouter. Tout est propre (ou rien n'a changé).")
        return

    print("  Fichiers détectés par Git :")
    for i, line in enumerate(lines, 1):
        print(f"    {i:2}. {line}")

    print("\n  Tapez :")
    print("    - 'a' pour tout ajouter (⚠️ vérifiez d'abord qu'il n'y a pas de fichiers sensibles)")
    print("    - 'n' pour ne rien ajouter")
    print("    - '1 2 5' pour ajouter seulement les fichiers 1, 2 et 5")
    print("    - 'p' pour ajouter fichier par fichier avec confirmation")

    choice = prompt("Votre choix : ").lower()

    if choice == "a":
        # Vérification de sécurité avant d'ajouter tout
        sec = check_sensitive_tracked()
        if sec:
            r = run("git add .")
            if r.returncode == 0:
                ok("Tous les fichiers ont été ajoutés.")
            else:
                err(r.stderr)
        else:
            warn("Ajout global annulé pour protéger vos fichiers sensibles.")
            info("Utilisez 'p' pour ajouter fichier par fichier.")

    elif choice == "n":
        info("Aucun fichier ajouté.")

    elif choice == "p":
        # Ajout progressif
        for i, line in enumerate(lines, 1):
            # le statut short a le format : XY filename
            # on extrait le nom après les 2 premiers caractères + espace
            filename = line[3:] if len(line) > 3 else line
            ans = prompt(f"Ajouter '{filename}' ? (o/n) : ").lower()
            if ans in ("o", "oui", "y", "yes"):
                r = run(f'git add "{filename}"')
                if r.returncode == 0:
                    ok(f"Ajouté : {filename}")
                else:
                    err(r.stderr)
            else:
                print(f"     Ignoré : {filename}")

    else:
        # Essayer de parser des numéros
        try:
            nums = [int(x) for x in choice.split() if x.strip().isdigit()]
            for n in nums:
                if 1 <= n <= len(lines):
                    filename = lines[n-1][3:] if len(lines[n-1]) > 3 else lines[n-1]
                    r = run(f'git add "{filename}"')
                    if r.returncode == 0:
                        ok(f"Ajouté : {filename}")
                    else:
                        err(r.stderr)
                else:
                    warn(f"Numéro {n} invalide.")
        except Exception as e:
            err(f"Choix non reconnu : {e}")


def do_remove_sensitive():
    """
    Retire les fichiers sensibles de l'index Git SANS les supprimer de votre PC.
    C'est l'antidote si vous avez fait 'git add documents/' par accident.
    """
    header("RETIRER LES FICHIERS SENSIBLES DE GIT")

    result = run("git ls-files")
    if result.returncode != 0:
        err("Impossible de lister les fichiers suivis.")
        return

    tracked = result.stdout.splitlines()
    to_remove = [f for f in tracked if f.startswith("documents/") or f == "memory.json" or f.startswith("chroma_db")]

    if not to_remove:
        info("Aucun fichier sensible trouvé dans l'index Git. Parfait.")
        return

    print("  Fichiers sensibles détectés dans l'index :")
    for f in to_remove:
        print(f"    ❌ {f}")

    ans = prompt("Les retirer de l'index Git (les fichiers restent sur votre PC) ? (o/n) : ").lower()
    if ans in ("o", "oui", "y", "yes"):
        for f in to_remove:
            # --cached = retire de l'index mais garde le fichier sur le disque
            r = run(f'git rm -r --cached "{f}"')
            if r.returncode == 0:
                ok(f"Retiré de l'index : {f}")
            else:
                err(r.stderr)

        # Committer ce nettoyage
        msg = prompt("Message du commit de nettoyage (ex: 'Retrait fichiers sensibles') : ")
        if not msg:
            msg = "Retrait des fichiers sensibles de l'index Git"
        r = run(f'git commit -m "{msg}"')
        if r.returncode == 0:
            ok("Commit de nettoyage effectué.")
        else:
            err(r.stderr)
    else:
        info("Annulé. Les fichiers sensibles restent dans l'index.")


def do_commit():
    """Crée un commit avec un message."""
    header("CRÉER UN COMMIT")

    # Vérifier s'il y a quelque chose à committer
    r = run("git diff --cached --name-only")
    if r.returncode != 0 or not r.stdout.strip():
        info("Rien à committer (pas de fichiers en 'staging').")
        info("Utilisez l'option 'Ajouter des fichiers' d'abord.")
        return

    print("  Fichiers prêts à être commités :")
    for f in r.stdout.strip().splitlines():
        print(f"    📄 {f}")

    msg = prompt("Message du commit (ex: 'Ajout agent lecteur PDF') : ")
    if not msg:
        warn("Message vide. Commit annulé.")
        return

    result = run(f'git commit -m "{msg}"')
    if result.returncode == 0:
        ok(f"Commit créé avec succès : '{msg}'")
    else:
        err(result.stderr)


def do_connect_github():
    """Guide pour connecter le dépôt local à GitHub."""
    header("CONNECTER À GITHUB")

    if not check_git_repo():
        err("Vous devez d'abord initialiser Git (option 1 du menu).")
        return

    # Vérifier si un remote existe déjà
    r = run("git remote -v")
    if r.returncode == 0 and r.stdout.strip():
        info("Remote déjà configuré :")
        print(r.stdout)
        ans = prompt("Voulez-vous le remplacer ? (o/n) : ").lower()
        if ans not in ("o", "oui", "y", "yes"):
            info("Conservation du remote actuel.")
            return

    print("\n  1. Allez sur https://github.com/new")
    print("  2. Créez un dépôt VIDE (sans README, sans .gitignore)")
    print("  3. Copiez le lien HTTPS (ex: https://github.com/VotreNom/mon-agent-ia.git)")

    url = prompt("Collez l'URL du dépôt GitHub : ")
    if not url.startswith("https://github.com/"):
        warn("L'URL ne ressemble pas à un dépôt GitHub. Vérifiez.")
        confirm = prompt("Continuer quand même ? (o/n) : ").lower()
        if confirm not in ("o", "oui", "y", "yes"):
            return

    r = run(f'git remote add origin "{url}"')
    if r.returncode == 0:
        ok(f"Remote 'origin' ajouté : {url}")
    else:
        # Peut-être que origin existe déjà, essayer de le changer
        r2 = run(f'git remote set-url origin "{url}"')
        if r2.returncode == 0:
            ok(f"Remote 'origin' mis à jour : {url}")
        else:
            err(r.stderr)
            err(r2.stderr)


def do_push():
    """Pousse les commits sur GitHub avec toutes les vérifications de sécurité."""
    header("POUSSER SUR GITHUB")

    # Vérifications de sécurité (obligatoires)
    if not check_git_repo():
        return

    if not check_gitignore_exists():
        warn("PUSH ANNULÉ — Pas de .gitignore !")
        return

    if not check_gitignore_content():
        warn("PUSH ANNULÉ — .gitignore incomplet !")
        return

    if not check_sensitive_tracked():
        warn("PUSH ANNULÉ — Fichiers sensibles détectés dans l'index Git !")
        info("Utilisez l'option 'Retirer les fichiers sensibles' dans le menu.")
        return

    # Vérifier s'il y a des commits à pousser
    r = run("git log origin/main..main")
    if r.returncode == 0 and not r.stdout.strip():
        # Peut-être que la branche s'appelle master ou autre
        r2 = run("git log origin/master..master")
        if r2.returncode == 0 and not r2.stdout.strip():
            info("Aucun nouveau commit à pousser (ou remote non configuré).")

    # Demander confirmation
    ans = prompt("Toutes les vérifications de sécurité sont OK. Pousser sur GitHub ? (o/n) : ").lower()
    if ans not in ("o", "oui", "y", "yes"):
        info("Push annulé.")
        return

    # Détecter la branche actuelle
    r_branch = run("git branch --show-current")
    branch = r_branch.stdout.strip() if r_branch.returncode == 0 else "main"

    result = run(f"git push -u origin {branch}")
    if result.returncode == 0:
        ok(f"🎉 Push réussi sur la branche '{branch}' !")
        info("Vérifiez sur GitHub que tout est en ordre.")
    else:
        err(result.stderr)
        info("Astuce : si c'est votre premier push, assurez-vous d'avoir créé le dépôt sur GitHub.")


# ============================
# MENU PRINCIPAL
# ============================

def menu():
    print("\n" + "=" * 60)
    print("  🛡️  AGENT GITHUB — Assistant de publication sécurisée")
    print("=" * 60)
    print("  Ce guide vous aide à pousser votre code sur GitHub")
    print("  SANS jamais publier vos documents privés.")
    print("-" * 60)
    print("  1. 🔧 Initialiser Git (git init)")
    print("  2. 📝 Ajouter .gitignore au suivi")
    print("  3. 📦 Ajouter les fichiers source au commit")
    print("  4. 🔍 Vérifier le statut Git")
    print("  5. 💾 Créer un commit")
    print("  6. 🔗 Connecter à GitHub (remote)")
    print("  7. 🚨 Retirer les fichiers sensibles de l'index")
    print("  8. 🚀 Pousser sur GitHub (avec vérifications de sécurité)")
    print("  9. 🧪 Audit complet de sécurité")
    print("  0. ❌ Quitter")
    print("-" * 60)


def audit_complet():
    """Fait toutes les vérifications de sécurité d'un coup."""
    header("AUDIT COMPLET DE SÉCURITÉ")
    all_ok = True

    if not check_git_installed():
        all_ok = False
    if not check_git_repo():
        all_ok = False
    if not check_gitignore_exists():
        all_ok = False
    if not check_gitignore_content():
        all_ok = False
    if not check_sensitive_tracked():
        all_ok = False

    if all_ok:
        ok("🎉 TOUT EST VERT ! Vous pouvez pousser sur GitHub en toute sécurité.")
    else:
        warn("🔴 Des problèmes ont été détectés. Corrigez-les avant de publier.")


def main():
    if not check_git_installed():
        prompt("Appuyez sur Entrée pour quitter...")
        sys.exit(1)

    while True:
        menu()
        choice = prompt("Votre choix : ")

        if choice == "1":
            do_git_init()
        elif choice == "2":
            do_add_gitignore()
        elif choice == "3":
            do_add_files()
        elif choice == "4":
            show_git_status()
        elif choice == "5":
            do_commit()
        elif choice == "6":
            do_connect_github()
        elif choice == "7":
            do_remove_sensitive()
        elif choice == "8":
            do_push()
        elif choice == "9":
            audit_complet()
        elif choice == "0":
            print("\n  👋 Au revoir ! Poussez bien.\n")
            break
        else:
            warn("Choix non reconnu. Tapez un chiffre entre 0 et 9.")


if __name__ == "__main__":
    main()
