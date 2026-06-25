# 🎙️ Guide : Donner une voix à votre Agent IA

> **Date** : 18 juin 2026  
> **Public** : PC avec GPU NVIDIA GTX 10xx (6-11 Go VRAM)  
> **Objectif** : Parler avec votre agent (voix), et/ou l'entendre répondre.

---

## 🏠 L'analogie du téléphone

Jusqu'ici, vous discutiez avec votre agent par **SMS** (texte dans le terminal).  
Maintenant, vous voulez passer à **l'appel téléphonique** :

| Élément | Équivalent technique | Rôle |
|---|---|---|
| **Votre bouche** | Micro + **STT** (Speech-to-Text) | Transforme votre voix en texte pour l'IA |
| **Le cerveau de l'IA** | Ollama + Qwen 2.5 | Réfléchit et écrit une réponse |
| **La bouche de l'IA** | **TTS** (Text-to-Speech) | Transforme la réponse texte en voix qui sort des haut-parleurs |

---

## 🧱 Les 3 briques d'un agent vocal

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  VOUS PARLEZ │ → │   L'IA      │ → │ L'IA RÉPOND │
│  (micro)     │    │  réfléchit  │    │  (voix)     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
   ┌───┴───┐         ┌────┴────┐        ┌───┴───┐
   │  STT  │         │ Ollama  │        │  TTS  │
   │ recon │         │  GPU    │        │ synthè│
   │naissance│        │         │        │ se voc│
   └───────┘         └─────────┘        └───────┘
```

---

## 🎙️ Partie 1 : TTS (Text-to-Speech) — La voix de l'IA

### Option A : `pyttsx3` (recommandé débutant) ✅
- **Avantage** : 100% offline, ultra-léger, aucun GPU nécessaire, installation instantanée (`pip install pyttsx3`)
- **Inconvénient** : Voix robotique (type GPS de 2010). Sur Windows, la voix française n'est pas installée par défaut.
- **Usage** : Parfait pour commencer et tester.

### Option B : `edge-tts` (recommandé qualité) 🌟
- **Avantage** : Voix **ultra-naturelle** (même moteur que Microsoft Edge/Cortana). Gratuit.
- **Inconvénient** : Nécessite **Internet** (les voix sont en ligne). Génère un fichier `.mp3` qu'il faut lire.
- **Usage** : Si vous voulez une voix humaine réaliste et que vous avez Internet.

### Option C : `piper-tts` (expert, 100% offline naturel)
- **Avantage** : Voix naturelle, 100% offline, très rapide sur CPU.
- **Inconvénient** : Nécessite d'installer un binaire + télécharger un modèle de voix (~50-100 Mo). Plus technique.
- **Usage** : Si vous voulez le meilleur des deux mondes (offline + naturel) et que vous êtes à l'aise.

> **Mon conseil** : Commencez par `pyttsx3` pour tester. Si la voix robotique vous agace, passez à `edge-tts` (1 ligne de code de plus, mais online).

---

## 🎤 Partie 2 : STT (Speech-to-Text) — Vous parlez à l'IA

### Option A : `SpeechRecognition` + Google API (recommandé débutant) ✅
- **Avantage** : Très précis, gratuit, simple à installer (`pip install SpeechRecognition pyaudio`)
- **Inconvénient** : Nécessite **Internet** (envoie un bout de votre voix à Google pendant 2 secondes). Pas 100% privé.
- **Usage** : Parfait pour commencer.

### Option B : `faster-whisper` (offline, 100% local) 🌟
- **Avantage** : 100% offline, modèle de transcription local, très précis. Le modèle `tiny` fait seulement 39 Mo et tourne sur CPU ou votre GTX 10xx.
- **Inconvénient** : Nécessite un peu plus de RAM (modèle `tiny` = 39 Mo, `base` = 74 Mo, `small` = 244 Mo). Un peu plus lent que Google.
- **Usage** : Si vous voulez une totale confidentialité (rien ne quitte votre PC).

> **Mon conseil** : Commencez par Google SpeechRecognition. Si vous aimez le concept et voulez du offline, on installera `faster-whisper` plus tard.

---

## 📋 Tableau récapitulatif

| Vous voulez... | TTS | STT | Installation |
|---|---|---|---|
| **Tester rapidement** | `pyttsx3` (robotique) | Clavier seulement (pas de micro) | `pip install pyttsx3` |
| **Bonne qualité + Internet OK** | `edge-tts` (naturelle) | `SpeechRecognition` (Google) | `pip install pyttsx3 edge-tts speechrecognition pyaudio` |
| **100% offline + qualité** | `piper-tts` | `faster-whisper` (tiny) | Plus complexe (voir plus tard) |

---

## 🛠️ Installation (Windows)

### 1. TTS basique (pyttsx3)
```bash
pip install pyttsx3
```

### 2. TTS premium (edge-tts) — optionnel
```bash
pip install edge-tts
```

### 3. STT (micro + Google)
```bash
pip install SpeechRecognition pyaudio
```

> **Problème fréquent sous Windows** : `pyaudio` peut refuser de s'installer.  
> Si `pip install pyaudio` échoue, téléchargez le fichier `.whl` correspondant à votre Python ici : https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio  
> Exemple : `pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl` (pour Python 3.11)

---

## ⚠️ Limites à connaître

| Limite | Explication | Solution |
|---|---|---|
| **Voix française Windows** | `pyttsx3` utilise la voix de votre système. Windows n'a souvent que la voix anglaise `David`/`Zira`. | Installez une voix FR dans Windows : Paramètres > Heure et langue > Langue > Ajouter une langue > Français (France). Ou utilisez `edge-tts`. |
| **Latence** | L'IA doit d'abord générer le texte (Ollama, 1-5 secondes), puis le lire (TTS, 0-2 secondes). | Utilisez le modèle `qwen2.5:3b` pour la vitesse. |
| **Bruit ambiant** | Le micro capte les bruits de la pièce. | Parlez près du micro, dans un endroit calme. |
| **Mots techniques** | `pyttsx3` lit mal les codes (`python`, `json`, `qwen2.5`). | L'IA est censée répondre en langage naturel. Si elle répond en code, c'est moche à l'oreille. |

---

## 🚀 Comment lancer l'agent vocal

Le script `agent_vocal.py` propose **deux modes** :

### Mode 1 : Vous tapez, l'IA parle (le plus simple)
```
Vous tapez : "Quelle heure est-il ?"
L'IA (voix) : "Il est 18 juin 2026, 14 heures 30."
```

### Mode 2 : Vous parlez, l'IA parle (vrai conversation vocale)
```
Vous (micro) : "Quelle heure est-il ?"
L'IA (voix) : "Il est 18 juin 2026, 14 heures 30."
```

> Le mode 2 nécessite un micro fonctionnel et `SpeechRecognition` installé. Si le micro ne marche pas, le script bascule automatiquement sur le mode clavier.

---

## 🎓 Prochaines étapes

Si vous aimez le concept, vous pouvez monter en gamme :
1. **Voix plus naturelle** : Passer à `edge-tts` (voix humaine) ou `piper-tts` (offline naturelle)
2. **Confidentialité totale** : Passer à `faster-whisper` (STT offline) + `piper-tts` (TTS offline)
3. **Interface web vocale** : Adapter `app_web.py` avec Streamlit + bouton micro + lecteur audio

Dites-moi quel niveau vous intéresse et je vous prépare la version !
