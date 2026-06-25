# 📡 Guide : API REST — Accéder à l'Agent depuis n'importe quel appareil

> **Objectif** : Transformer votre agent en **serveur API local** accessible depuis votre téléphone, tablette, ou un autre PC sur votre réseau Wi-Fi.

---

## 🏰 Analogie : le Téléphone de l'Agent

Jusqu'ici, votre agent était un **serveur dans un restaurant** qui ne parlait qu'à vous, assis à la table (Streamlit sur votre PC).  
Avec l'API REST, il devient un **restaurant avec un service de livraison**. Vous pouvez commander depuis :
- Votre téléphone (dans le canapé)
- Votre tablette (dans la cuisine)
- Un autre PC (dans le bureau)
- Même un script Python automatique (une sonnette qui sonne toute seule)

Le **serveur API** reste sur votre PC principal (celui avec le GPU NVIDIA). Les autres appareils envoient des **requêtes** (commandes) par le réseau Wi-Fi.

---

## 🔧 Architecture

```
Votre téléphone (192.168.1.42)
    ↓ POST http://192.168.1.10:8000/chat
    { "message": "Quelle heure est-il ?" }

Réseau Wi-Fi local (pas Internet)
    ↓

Votre PC avec GPU (192.168.1.10)
    ↓
Serveur FastAPI (api_server.py)
    ↓
Ollama (GPU NVIDIA) → Qwen 2.5 / LLaVA
    ↓
Réponse JSON : { "reply": "Il est 14h30..." }
    ↑
Retour au téléphone
```

> ⚠️ **Important** : L'API est accessible uniquement sur votre **réseau local** (Wi-Fi domestique). Elle n'est pas exposée sur Internet sans configuration supplémentaire (ce qui serait dangereux).

---

## 📦 Installation

```bash
pip install fastapi uvicorn python-multipart
```

> `fastapi` = le framework API (rapide, moderne)  
> `uvicorn` = le serveur web qui fait tourner l'API  
> `python-multipart` = pour recevoir des fichiers (images uploadées)

---

## 🚀 Lancer le serveur API

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

- `--host 0.0.0.0` : accepte les connexions depuis n'importe quelle IP du réseau local
- `--port 8000` : le numéro de port (vous pouvez changer)

**Vous verrez :**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Votre serveur est en ligne !

---

## 🔍 Trouver l'adresse IP de votre PC

**Windows** : ouvrez l'invite de commandes, tapez :
```cmd
ipconfig
```
Cherchez la ligne `Adresse IPv4` (ex: `192.168.1.10`).

**Linux** : ouvrez un terminal, tapez :
```bash
ip addr show
# ou simplement
hostname -I
```

---

## 🎯 Utiliser l'API depuis un autre appareil

### 1. Test rapide (depuis votre navigateur)
Ouvrez sur le même PC :
```
http://localhost:8000/docs
```

Vous voyez une **interface interactive Swagger** où vous pouvez tester l'API directement. C'est le mode "démo".

### 2. Depuis un autre PC
```bash
curl -X POST http://192.168.1.10:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quelle heure est-il ?"}'
```

### 3. Depuis un téléphone (Python)
```python
import requests

response = requests.post(
    "http://192.168.1.10:8000/chat",
    json={"message": "Calcule 15 * 4"}
)
print(response.json()["reply"])
# "15 × 4 = 60"
```

### 4. Avec une image
```python
import requests
import base64

with open("photo.png", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://192.168.1.10:8000/chat",
    json={
        "message": "Décris cette image",
        "image_b64": image_b64
    }
)
print(response.json()["reply"])
```

---

## 📡 Endpoints de l'API

| Endpoint | Méthode | Description | Exemple de requête |
|----------|---------|-------------|-------------------|
| `/` | GET | Vérifier que le serveur est en ligne | `curl http://192.168.1.10:8000/` |
| `/chat` | POST | Envoyer un message à l'agent | `{"message": "...", "image_b64": "..."}` |
| `/docs` | GET | Interface interactive Swagger (test) | Navigateur |

### Requête POST `/chat`

```json
{
  "message": "Quelle heure est-il ?",
  "image_b64": "iVBORw0KGgo..."  // optionnel
}
```

### Réponse

```json
{
  "reply": "Il est lundi 20 juin 2026, 14 heures 30.",
  "tools_used": ["heure_actuelle"],
  "model_used": "qwen2.5:3b"
}
```

---

## ⚠️ Limites et sécurité

| Point | Explication |
|-------|-------------|
| **Réseau local uniquement** | Par défaut, l'API n'est accessible que sur votre Wi-Fi. Ne la forward pas sur Internet sans authentification ! |
| **Un seul utilisateur à la fois** | Ollama utilise votre GPU. Si l'interface web (`app_ultime.py`) et l'API sont utilisées simultanément, elles se partagent le GPU et peuvent être lentes. |
| **Pas de mémoire persistante** | Chaque requête `/chat` est indépendante. L'API ne conserve pas l'historique entre deux appels (contrairement à l'interface web). Si vous voulez une conversation continue, vous devez envoyer l'historique complet à chaque fois. |
| **Pas de voix** | L'API retourne du texte uniquement. Le TTS (voix) doit être géré par le client (l'appareil qui appelle l'API). |
| **Pas de Streamlit** | L'API n'a pas d'interface graphique. C'est un serveur "invisible" qui attend des requêtes. |

---

## 🔒 Pour aller plus loin (avancé)

Si vous voulez sécuriser l'accès (même sur le réseau local) :
- Ajoutez une **clé API** dans les headers : `Authorization: Bearer votrecle123`
- Limitez les IPs autorisées : `--host 127.0.0.1` (uniquement le PC local) et utilisez un reverse proxy
- Ajoutez du **rate limiting** (limite de requêtes/minute) pour protéger votre GPU

Ces améliorations ne sont pas incluses par défaut pour garder le code simple, mais sont faciles à ajouter avec FastAPI.
