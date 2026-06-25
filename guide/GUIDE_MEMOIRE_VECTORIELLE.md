# 🧠 Guide : Mémoire Vectorielle à Long Terme (Souvenirs)

> **Objectif** : L'agent se souvient de faits précis sur vous (prénom, préférences, projets, dates) dans une base de données "intelligente" et les retrouve instantanément, même après 1000 conversations.

---

## 🏠 Analogie : le Carnet de l'Enquêteur

Imaginez un **détective privé** qui travaille sur votre dossier :
- **Mémoire classique** : il prend des notes sur un bloc de papier. Au bout de 20 pages, il doit tout résumer sur une seule page. Il oublie les détails.
- **Mémoire vectorielle** : il a un **classeur géant** avec des milliers de fiches. Chaque fiche porte une **étiquette sémantique** (le sens des mots). Quand vous demandez : *"Comment s'appelle mon chat ?"*, il ne lit pas toutes les fiches. Il pense à "chat", "animal", "nom" et va **directement** à la bonne fiche.

C'est une **carte géante des idées** où chaque souvenir a ses coordonnées GPS. Deux idées proches ("chat" et " Rouxy") sont stockées à côté.

---

## 🔧 Comment ça marche

```
Conversation :
Vous > "Mon chat s'appelle Rouxy et il a 3 ans"
Agent > "Quel joli nom ! Rouxy est un chat de 3 ans."
    ↓
[Extraction automatique]
"Le chat de l'utilisateur s'appelle Rouxy"
"Le chat de l'utilisateur a 3 ans"
    ↓
[Stockage vectoriel]
Chaque phrase est transformée en coordonnées (768 nombres)
    ↓
[Mémoire long terme]
Stocké dans une base ChromaDB dédiée (chroma_souvenirs/)

--- 3 mois plus tard ---

Vous > "Comment s'appelle mon chat ?"
    ↓
[Recherche vectorielle]
La question est transformée en coordonnées. On cherche les voisins.
    ↓
[Retour]
Trouvé : "Le chat de l'utilisateur s'appelle Rouxy" (similarité 0.94)
    ↓
Agent > Votre chat s'appelle Rouxy ! 🐱
```

---

## 📦 Installation

```bash
pip install sentence-transformers
```

Un modèle d'embedding (`all-MiniLM-L6-v2`, ~80 Mo) se télécharge **une seule fois** au premier lancement.

---

## 🎯 Ce que ça change concrètement

### Avant (mémoire classique)
```
Vous > Mon chat s'appelle Rouxy
... (50 conversations plus tard) ...
Vous > Comment s'appelle mon chat ?
Agent > Je suis désolé, je ne me souviens pas. Vous ne m'avez pas dit...
```

### Après (mémoire vectorielle)
```
Vous > Mon chat s'appelle Rouxy
... (50 conversations plus tard, l'agent a résumé l'historique 3 fois) ...
Vous > Comment s'appelle mon chat ?
Agent > [cherche dans ses souvenirs] Votre chat s'appelle Rouxy ! 🐱
```

### Autres exemples
```markdown
Vous > Je travaille sur un projet de jardinage automatisé avec Arduino
... (200 conversations plus tard) ...
Vous > Quel projet je fais en ce moment ?
Agent > Vous travaillez sur votre jardinage automatisé avec Arduino.

Vous > Ma couleur préférée est le bleu marine
... (1000 conversations plus tard) ...
Vous > Quelle est ma couleur préférée ?
Agent > Votre couleur préférée est le bleu marine.

Vous > Je suis allergique aux cacahuètes
... (urgence, 6 mois plus tard) ...
Vous > Peux-tu vérifier si cette recette est sûre pour moi ?
Agent > [cherche] Attention, vous êtes allergique aux cacahuètes !
```

---

## ⚙️ Technique simplifiée

| Étape | Explication | Analogie |
|---|---|---|
| **Extraction** | Après chaque réponse, le modèle résume les faits clés en 1-3 phrases courtes. | Le secrétaire écrit une fiche récapitulative. |
| **Embedding** | Chaque phrase est transformée en 768 nombres (un vecteur) par un modèle `all-MiniLM-L6-v2`. | Le classeur range la fiche à une coordonnée précise selon son sens. |
| **Stockage** | Les vecteurs sont stockés dans une base ChromaDB (`chroma_souvenirs/`). | La fiche est rangée dans le tiroir correspondant. |
| **Recherche** | Votre question est aussi transformée en vecteur. On cherche les 3 fiches les plus proches. | Le secrétaire pense à la question et va directement au bon tiroir. |
| **Injection** | Les souvenirs trouvés sont glissés discrètement dans le contexte de l'IA avant qu'elle réponde. | Le détective lit les fiches pertinentes avant de répondre au téléphone. |

---

## ⚠️ Limites

1. **Extraction automatique** : le modèle extrait les faits tout seul. Il peut parfois rater un détail ou en inventer un. La qualité dépend du modèle (Qwen 2.5 est très bon à ça).
2. **Pas de dates complexes** : la mémoire ne sait pas *"Quand est-ce que j'ai dit ça ?"* de manière précise. Elle sait juste que c'est "dans le passé".
3. **Faits, pas émotions** : elle stocke des faits concrets, pas l'ambiance émotionnelle d'une conversation.
4. **Téléchargement initial** : le modèle `all-MiniLM-L6-v2` (~80 Mo) se télécharge au premier lancement. C'est une fois.

---

## 🔒 Sécurité

- Le dossier `chroma_souvenirs/` est dans `.gitignore` : vos souvenirs ne partent jamais sur GitHub.
- Aucun souvenir ne quitte votre PC. Les embeddings sont calculés localement.
