# 🎙️ Guide : Agent vocal 100% offline (Piper-TTS + Faster-Whisper)

> **Objectif** : Parler à votre IA et l'entendre répondre, **sans jamais envoyer quoi que ce soit sur Internet** (ni voix, ni texte, ni audio).

---

## 🧱 Architecture offline complète

```
Vous (micro) ──► Faster-Whisper (local) ──► Texte ──► Ollama (GPU) ──► Texte ──► Piper-TTS (local) ──► Haut-parleur
```

| Brique | Rôle | Taille | Où ça tourne |
|--------|------|--------|-------------|
| **Faster-Whisper** | Reconnaissance vocale (STT) | Modèle `tiny` = 39 Mo / `base` = 74 Mo | **CPU** (très rapide) |
| **Ollama** | Cerveau IA | Modèle `qwen2.5:3b` = 2-4 Go VRAM | **GPU NVIDIA** (GTX 10xx) |
| **Piper-TTS** | Synthèse vocale naturelle | Modèle voix = ~50-100 Mo | **CPU** (instantané) |

> **Avantage clé** : tout tourne localement. Même si vous coupez Internet, l'agent fonctionne.

---

## ⚠️ Prérequis importants

Avant de commencer, assurez-vous d'avoir déjà installé et testé :
- Python 3.11+ avec `venv` fonctionnel
- Ollama + Qwen 2.5 qui fonctionne (`ollama run qwen2.5:3b` répond)
- `pip install pyaudio` qui fonctionne (déjà vu dans le guide vocal précédent)

---

## 📦 Étape 1 : Installer les bibliothèques Python

Dans votre environnement virtuel activé :

```bash
pip install faster-whisper
pip install SpeechRecognition  # on le garde pour la capture micro
pip install pyaudio            # déjà installé normalement
```

> **Note** : `faster-whisper` utilise `ctranslate2` en backend. Il télécharge automatiquement le modèle Whisper au premier lancement dans `~/.cache/huggingface` (ou `C:\Users\Vous\.cache\huggingface` sur Windows).

---

## 🎙️ Étape 2 : Installer Piper-TTS (la voix)

Piper-TTS n'est **pas** une bibliothèque Python classique. C'est un **programme externe** (binaire) que Python appelle. Voici comment l'installer.

### 2.1 Créer le dossier des modèles

```bash
# Dans le dossier de votre projet
mkdir models
mkdir models\piper        # Windows
mkdir models/piper         # Linux
```

### 2.2 Télécharger le binaire Piper

Allez sur la page des releases Piper :  
👉 https://github.com/rhasspy/piper/releases

Téléchargez la dernière version pour votre système :

| OS | Fichier à télécharger | Où le mettre |
|---|---|---|
| **Windows** | `piper_windows_amd64.zip` | Dézippez dans `models\piper\` |
| **Linux** | `piper_linux_x86_64.tar.gz` | Dézippez dans `models/piper/` |
| **macOS** | `piper_macos_x64.tar.gz` | Dézippez dans `models/piper/` |

**Après dézippage**, vous devez avoir dans `models/piper/` (ou `models\piper\`) :
- `piper.exe` (Windows) ou `piper` (Linux/Mac) — **le programme**
- Des fichiers `.dll` (Windows) ou `.so` (Linux) — les bibliothèques liées

> **Vérifiez** : essayez de lancer `models\piper\piper.exe -h` (Windows) ou `./models/piper/piper -h` (Linux) dans un terminal. Vous devez voir l'aide s'afficher.

### 2.3 Télécharger une voix française

Piper utilise des modèles `.onnx` (le cerveau vocal) + un `.json` (la configuration).

Voix recommandées (français) :

| Voix | Fichier | Qualité | Taille | Lien |
|---|---|---|---|---|
| **Siwis (féminine)** | `fr_FR-siwis-medium` | ⭐⭐⭐ Bonne | ~60 Mo | [Télécharger](https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx) |
| | + config | | | [Config](https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json) |
| **Gilles (masculine)** | `fr_FR-gilles-low` | ⭐⭐ Correcte | ~30 Mo | [Télécharger](https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx) |
| | + config | | | [Config](https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json) |

**Méthode simple** : téléchargez les deux fichiers (`.onnx` et `.onnx.json`) et placez-les dans `models/piper/`.

**Méthode rapide avec `wget` (Linux)** :
```bash
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

**Méthode rapide avec PowerShell (Windows)** :
```powershell
cd models\piper
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx" -OutFile "fr_FR-siwis-medium.onnx"
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json" -OutFile "fr_FR-siwis-medium.onnx.json"
```

> **Alternative** : allez sur https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/fr , choisissez une voix, cliquez sur les fichiers `.onnx` et `.json`, puis sur le bouton ⬇️ **Download**.

### 2.4 Tester Piper en ligne de commande

**Windows** :
```cmd
echo "Bonjour, je suis votre agent vocal." | models\piper\piper.exe --model models\piper\fr_FR-siwis-medium.onnx --output_file test.wav
```

**Linux/Mac** :
```bash
echo "Bonjour, je suis votre agent vocal." | ./models/piper/piper --model ./models/piper/fr_FR-siwis-medium.onnx --output_file test.wav
```

Si vous entendez (ou voyez) un fichier `test.wav` créé, c'est que Piper fonctionne ! 🎉

---

## 🧠 Étape 3 : Vérifier Faster-Whisper (téléchargement automatique)

La première fois que vous lancerez `agent_vocal_offline.py`, Faster-Whisper téléchargera automatiquement le modèle Whisper dans le cache de votre ordinateur. C'est normal et c'est gratuit.

- Modèle `tiny` : **39 Mo** (très rapide, qualité OK pour un micro proche)
- Modèle `base` : **74 Mo** (meilleure qualité, toujours très rapide)
- Modèle `small` : **244 Mo** (meilleure qualité, un peu plus lent)

> **Conseil** : commencez avec `tiny`. Si l'IA ne vous comprend pas assez bien, passez à `base` en changeant une ligne dans le code.

---

## 📁 Structure finale attendue

```
votre-projet/
├── venv/                       # (ignoré par Git)
├── models/
│   └── piper/
│       ├── piper.exe           # (Windows) ou 'piper' (Linux)
│       ├── ... .dll / .so      # bibliothèques
│       ├── fr_FR-siwis-medium.onnx      # voix
│       └── fr_FR-siwis-medium.onnx.json # config
├── documents/                  # (ignoré par Git)
├── agent_vocal_offline.py     # ✅ Le nouveau script
├── ... autres fichiers .py
└── README.md
```

---

## 🚀 Étape 4 : Lancer l'agent

```bash
python agent_vocal_offline.py
```

**Au premier lancement** :
1. Piper se lance → vérifie que le binaire et le modèle sont trouvés
2. Faster-Whisper télécharge le modèle `tiny` (39 Mo) → patientez 30-60 secondes
3. Ollama se connecte → c'est instantané si vous l'avez déjà
4. L'agent dit : **"Bonjour. Je suis prêt. Vous pouvez parler ou taper."**

---

## 🎮 Commandes pendant la conversation

| Commande | Action |
|----------|--------|
| `.m` | Activer le **mode micro** (vous parlez) |
| `.c` | Activer le **mode clavier** (vous tapez) |
| `.s` | **Arrêter** la voix en cours (si l'IA est en train de parler) |
| `quit` / `exit` | Quitter |

---

## 🔧 Dépannage

### "Piper non trouvé"
- Vérifiez que `models/piper/piper.exe` (Windows) existe bien.
- Le script cherche automatiquement dans `models/piper/` puis dans le `PATH`.

### "Faster-Whisper ne trouve pas le modèle"
- C'est normal au premier lancement : il télécharge automatiquement.
- Si vous n'avez pas Internet **même une seule fois**, téléchargez le modèle manuellement depuis https://huggingface.co/Systran/faster-whisper-tiny et placez-le dans `~/.cache/huggingface/hub/`.

### "Le micro ne marche pas"
- Vérifiez que `pyaudio` est bien installé.
- Vérifiez que votre micro est bien celui par défaut dans Windows.

### "L'IA parle trop lentement / trop vite"
- Modifiez la variable `PIPER_SPEED` dans `agent_vocal_offline.py` (1.0 = normal, 1.2 = rapide, 0.8 = lent).

### "Je ne comprends rien à ce que dit l'IA"
- La voix `siwis-medium` est de bonne qualité. Si vous préférez une autre voix, téléchargez-en une autre depuis le repo Piper et modifiez `PIPER_MODEL` dans le script.

---

## 🎓 Pourquoi c'est plus complexe que `pyttsx3` ?

| | `pyttsx3` | `Piper-TTS` + `Faster-Whisper` |
|---|---|---|
| Installation | `pip install` | Binaire + modèle à télécharger manuellement |
| Voix | Robotique GPS | **Humaine naturelle** |
| STT | Google (online) | **Faster-Whisper (offline)** |
| Confidentialité | Voix envoyée à Google | **100% offline** |
| Taille | Quelques Mo | ~100 Mo (Piper) + ~40 Mo (Whisper) |
| Qualité | Basse | **Très bonne** |

Le jeu en vaut la chandelle si vous voulez une **expérience conversationnelle fluide et privée**.

---

**Bon courage pour l'installation !** Si vous bloquez sur une étape, dites-moi à quel message d'erreur vous arrivez.
