# 🌐 Guide : Recherche Web en temps réel (DuckDuckGo)

> **Objectif** : Votre agent peut chercher des informations fraîches sur Internet quand vous le demandez. Il vérifie d'abord que vous êtes connecté.

---

## 🧠 Pourquoi la recherche web change tout

Votre modèle local (Qwen 2.5) est comme un étudiant qui a passé son examen en **2024**. Il ne connaît rien après cette date :
- ❌ Le résultat du match d'hier
- ❌ La météo d'aujourd'hui
- ❌ La dernière version de Python sortie la semaine dernière
- ❌ L'actualité politique ou économique

La **recherche web** est comme lui donner un **téléphone portable** : il peut appeler l'extérieur et vous donner des infos à jour.

> ⚠️ **Votre conversation reste privée** : seule la **requête de recherche** (ex: "météo Paris") part sur Internet. Votre conversation complète, vos documents, vos images restent 100% sur votre PC.

---

## 🔧 Comment ça marche

```
Vous > "Quel temps fait-il à Paris aujourd'hui ?"
    ↓
L'agent réfléchit : "C'est une question sur le présent. Je dois chercher sur le web."
    ↓
[Outil : rechercher_web("météo Paris aujourd'hui")]
    ↓
DuckDuckGo (Internet) retourne 3 résultats frais
    ↓
L'agent lit les résultats et répond :
"D'après la recherche web, il fait 24°C à Paris aujourd'hui avec un ciel partiellement nuageux..."
```

---

## 📦 Installation

```bash
pip install duckduckgo-search
```

C'est **tout**. Pas de clé API. Pas de compte. Gratuit.

---

## 🛡️ Vérification de connexion Internet

Avant de chercher, l'agent teste silencieusement si votre PC est connecté :
- Il essaie de joindre `duckduckgo.com` pendant 2 secondes
- Si échec → il vous dit gentiment : *"Je ne peux pas chercher sur le web, vous semblez hors ligne."*
- Il continue quand même de répondre avec ses connaissances locales (mode 2024)

---

## 🎯 Exemples de requêtes qui activent la recherche web

```markdown
Vous > "Quel temps fait-il à Paris ?"
Agent > [recherche web : météo Paris] → réponse à jour

Vous > "Quelle est la dernière version de Python ?"
Agent > [recherche web : dernière version Python] → Python 3.12.x sorti le...

Vous > "Qui a gagné la finale de la Coupe du Monde 2026 ?"
Agent > [recherche web : Coupe du Monde 2026 final résultat] → réponse à jour

Vous > "Quel est le cours du Bitcoin aujourd'hui ?"
Agent > [recherche web : cours Bitcoin aujourd'hui] → réponse à jour
```

---

## ⚠️ Limites

- **DuckDuckGo** est gratuit mais peut limiter le nombre de requêtes si vous abusez (plusieurs dizaines par minute). Pour un usage personnel, c'est illimité.
- **La qualité dépend des résultats** : si la recherche retourne des sites peu fiables, l'agent peut être induit en erreur (comme n'importe quel humain qui ferait une recherche Google).
- **Pas de lecture de page complète** : l'agent ne lit que le **titre et le résumé** des résultats DuckDuckGo (snippet), pas l'article entier. C'est suffisant pour 90% des questions factuelles.

---

## 🔴 Alternative : SerpAPI (Google)

Si DuckDuckGo ne suffit pas, vous pouvez utiliser **SerpAPI** qui fait des recherches Google réelles. Mais c'est payant après 100 requêtes gratuites/mois, et nécessite une clé API (stockée dans un fichier `.env` sécurisé).

Pour l'instant, **DuckDuckGo suffit amplement** pour un usage personnel.
