# Guide d'installation : Agent IA interactif local (GPU NVIDIA GTX 10xx)

> **Date** : 18 juin 2026  
> **Public** : PC avec GPU NVIDIA Pascal (GTX 1060, 1070, 1080, 1080 Ti)  
> **Objectif** : Créer un agent IA conversationnel capable d'utiliser des outils (calcul, heure, etc.) qui tourne 100% en local.

---

## 1. Vérifier votre configuration

Avant de commencer, identifiez votre VRAM (mémoire vidéo) pour choisir le bon modèle :

| Votre carte | VRAM | Modèle recommandé | Commande Ollama |
|-------------|------|-------------------|-----------------|
| GTX 1060 | 6 Go | **Qwen 2.5 3B** (excellent tool use) | `ollama pull qwen2.5:3b` |
| GTX 1070 / 1080 | 8 Go | **Qwen 2.5 7B** (Q4 = ~4,5 Go VRAM) | `ollama pull qwen2.5:7b` |
| GTX 1080 Ti | 11 Go | **Qwen 2.5 7B** (Q5, meilleure qualité) | `ollama pull qwen2.5:7b` |

> **Pourquoi Qwen 2.5 ?** C'est actuellement l'un des meilleurs modèles open-source pour l'appel d'outils (function calling), même en petit format (3B).

---

## 2. Étape 1 : Mettre à jour les pilotes NVIDIA

Ollama embarque son propre moteur CUDA, mais il faut des drivers récents.

1. Allez sur : https://www.nvidia.fr/drivers/
2. Téléchargez et installez le dernier driver pour votre GTX 10xx.
3. **Redémarrez** votre PC.

---

## 3. Étape 2 : Installer Ollama

Ollama est le moteur qui va télécharger, charger et faire tourner le modèle sur votre GPU.

### Windows
1. Téléchargez : https://ollama.com/download/windows
2. Exécutez le `.exe` et suivez l'installation.
3. Ollama se lance automatiquement en arrière-plan (icône dans la barre des tâches).

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Vérifier que Ollama fonctionne
Ouvrez un terminal / invite de commandes et tapez :
```bash
ollama --version
```
Vous devez voir un numéro de version (ex: `0.5.x`).

---

## 4. Étape 3 : Vérifier que le GPU est détecté

Ollama doit utiliser votre NVIDIA, pas le CPU.

```bash
ollama ps
```

Puis téléchargez un modèle test (ex: si vous avez 6 Go) :
```bash
ollama pull qwen2.5:3b
```

Lancez une conversation rapide :
```bash
ollama run qwen2.5:3b
```
> Dites `Bonjour` puis `/bye` pour quitter.

**Vérifiez la charge GPU** : pendant que le modèle répond, ouvrez le `Gestionnaire des tâches` (Windows) ou `nvidia-smi` (Linux). Votre GPU NVIDIA doit monter en charge (mémoire et calcul). Si ce n'est pas le cas, Ollama tourne sur CPU (voir section Débogage en fin de guide).

---

## 5. Étape 4 : Installer Python et préparer l'environnement

### Si vous n'avez pas Python :
Téléchargez **Python 3.11** (recommandé pour la stabilité) : https://www.python.org/downloads/release/python-3119/

**Important** : lors de l'installation sur Windows, cochez **"Add Python to PATH"**.

### Créer le projet
Ouvrez un terminal dans le dossier où vous voulez créer votre agent :

```bash
# Créer le dossier
mkdir mon_agent_ia
cd mon_agent_ia

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux / Mac :
source venv/bin/activate

# Installer les dépendances
pip install ollama streamlit
```

> **Note** : Le paquet `ollama` en Python est juste un client HTTP. Il n'a pas besoin de PyTorch ni de CUDA toolkit. C'est Ollama (le logiciel installé à l'étape 2) qui gère tout le calcul GPU.

---

## 6. Étape 5 : Copier les fichiers de code

Dans votre dossier `mon_agent_ia`, copiez les deux fichiers fournis avec ce guide :

- `agent_terminal.py` → Agent conversationnel dans le terminal (simple)
- `app_web.py` → Interface web interactive avec Streamlit

Vous pouvez les renommer si vous voulez.

**Ouvrez `agent_terminal.py` et/ou `app_web.py` et modifiez la ligne suivante selon votre VRAM :**

```python
MODEL = "qwen2.5:3b"   # Pour GTX 1060 6 Go
# MODEL = "qwen2.5:7b" # Pour GTX 1070/1080/1080 Ti 8-11 Go
```

---

## 7. Étape 6 : Lancer l'agent en mode terminal

Assurez-vous que votre `venv` est activé, puis :

```bash
python agent_terminal.py
```

L'agent démarre. Vous pouvez lui poser des questions comme :
- `"Quelle heure est-il ?"` → l'agent appelle l'outil `heure_actuelle`
- `"Calcule 145 * 28 + 12"` → l'agent appelle l'outil `calculer`
- `"Raconte-moi une blague"` → l'agent répond directement sans outil

---

## 8. Étape 7 : Lancer l'interface web (Streamlit)

Pour une expérience plus sympa avec une vraie interface de chat :

```bash
streamlit run app_web.py
```

Votre navigateur s'ouvre automatiquement sur `http://localhost:8501`.

**Fonctionnalités de l'interface web :**
- Historique de conversation conservé
- Affichage spécial quand l'agent utilise un outil
- Réponses en temps réel

---

## 9. Débogage courant (si ça ne marche pas)

### Problème : "Ollama ne trouve pas le modèle"
```bash
ollama pull qwen2.5:3b
```

### Problème : "La réponse est très lente" (CPU au lieu du GPU)
- Vérifiez que les drivers NVIDIA sont bien installés.
- Sur Windows, vérifiez dans le Gestionnaire des tâches > Performance > GPU que le calcul monte.
- Sur Linux, tapez `nvidia-smi` pendant une génération. Si le processus `ollama` n'apparaît pas sur la GPU, il y a un souci de driver.

### Problème : "Out of memory" / crash VRAM
- Votre modèle est trop gros pour votre carte. Baissez vers un modèle plus petit (3B au lieu de 7B).
- Fermez les jeux, navigateurs lourds et applications qui utilisent le GPU avant de lancer l'agent.
- Redémarrez Ollama : `ollama ps` puis tuez les processus si besoin.

### Problème : "L'agent n'utilise jamais les outils"
- Le modèle Qwen 2.5 est très bon à ça, mais si vous utilisez un autre modèle moins adapté, l'agent peut ignorer les outils.
- Vérifiez que le modèle supporte le `tool calling` (Qwen 2.5, Llama 3.2/3.1, Mistral 7B v0.3).

---

## 10. Pour aller plus loin

Vous pouvez enrichir votre agent en ajoutant vos propres outils dans les fichiers Python. Quelques idées :
- **Lire/écrire des fichiers** (texte, notes)
- **Rechercher sur le web** (nécessite une API comme SerpAPI, ou un scraper local)
- **Exécuter du code Python** (avec un bac à sable sécurisé)
- **Générer des images** (si vous avez assez de VRAM, ou via une API locale comme Stable Diffusion)
- **Interagir avec votre calendrier / emails** (via API)

---

**Bonne création !** Votre agent tourne 100% localement, vos données ne quittent jamais votre PC.
