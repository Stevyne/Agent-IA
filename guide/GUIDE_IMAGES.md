# 🖼️ Guide : Donner des yeux à votre Agent IA (Analyse d'images)

> **Date** : 18 juin 2026  
> **Public** : PC avec GPU NVIDIA GTX 10xx (6-11 Go VRAM)  
> **Objectif** : Décrire, analyser, extraire du texte (OCR) et interpréter des images locales.

---

## 🧠 Concept : Le modèle "aveugle" vs "voyant"

Jusqu'ici, votre agent (Qwen 2.5) est **aveugle**. Il lit du texte, mais il ne peut pas voir une photo, un graphique, une capture d'écran ou un document scanné.

Un **modèle multimodal** (ou modèle de vision-langage) est un cerveau qui possède **deux entrées** :
1. Un œil : il regarde l'image (pixels)
2. Une oreille : il lit votre question (texte)

Il répond en combinant les deux : *"Je vois un chat roux sur un canapé bleu."*

---

## 🏗️ Comment ça marche techniquement

```
Votre image (photo.png)
       ↓
  [Encodage Base64]
       ↓
  Texte long et bizarre : "iVBORw0KGgoAAAANSUhEUgAA..."
       ↓
  Ollama (API) envoie à l'IA :
    {
      "role": "user",
      "content": "Décris cette image",
      "images": ["iVBORw0KGgo..."]
    }
       ↓
  Modèle multimodal (ex: LLaVA) analyse pixels + texte
       ↓
  Réponse texte : "C'est une photo d'un chat roux."
```

> **Base64** : C'est un alphabet de 64 caractères (A-Z, a-z, 0-9, +, /) qui permet de transformer n'importe quel fichier (image, vidéo, zip) en **texte pur**. L'IA ne comprend que le texte, donc on "traduit" l'image en texte pour elle.

---

## ⚠️ Contraintes matérielles honnêtes (GTX 10xx)

Les modèles multimodaux sont **plus gourmands** que les modèles texte seuls. La "partie vision" du cerveau ajoute des millions de paramètres et consomme de la VRAM.

| Modèle Ollama | Taille | VRAM requise (estimé) | Qualité vision | GTX 1060 6 Go |
|---|---|---|---|---|
| **moondream** | ~1,6B | **~2 Go** | ⭐ Basique (suffisant pour OCR et description simple) | ✅ Parfait |
| **llava-phi3** | ~3,8B | **~4-5 Go** | ⭐⭐ Bonne (détail, objets, texte) | ✅ OK |
| **llava:7b** | ~7B | **~6-8 Go** | ⭐⭐⭐ Très bonne | ⚠️ Juste (GTX 1060) / ✅ OK (1070+) |
| **qwen2.5-vl** | Variable | **~8-12 Go** | ⭐⭐⭐⭐ Excellente | ❌ Trop lourd |

> **Conseil** : commencez par `moondream` ou `llava-phi3` pour tester. Si vous avez un GTX 1070/1080, montez à `llava:7b`.

> **Limite** : un modèle vision ne remplace pas un modèle de texte expert. `llava` est moins bon en tool calling (calculatrice, appel d'outils) que Qwen 2.5. Pour un "super agent" qui fait les deux, il faut un pipeline (voir section 5).

---

## 📦 Modèles à télécharger (Ollama)

```bash
# Très léger, rapide, qualité modeste
ollama pull moondream

# Bon équilibre taille/qualité (recommandé pour 6-8 Go)
ollama pull llava-phi3

# Plus lourd, meilleur détail (si vous avez 8+ Go VRAM)
ollama pull llava
```

---

## 🚀 Ce que peut faire `agent_images.py`

1. **Décrire une image** : *"Décris ce que tu vois"*
2. **OCR (Lire le texte)** : *"Extrais tout le texte visible sur cette image"* (très utile pour les PDF scannés !)
3. **Analyse technique** : *"Quels sont les éléments en rouge sur ce schéma ?"*, *"De quelle couleur est cette voiture ?"*
4. **Conversation sur l'image** : posez une question, puis une question de suivi sans recharger l'image (*"Et à droite de cet objet ?"*)
5. **Multi-images** : comparez deux images (*"Quelle est la différence entre photo1.jpg et photo2.jpg ?"*)

---

## 🛠️ Installation supplémentaire

L'agent utilise la bibliothèque Python standard (`base64`), mais `Pillow` (PIL) est utile pour vérifier les images :

```bash
pip install pillow
```

> **Facultatif** : Pillow permet aussi de redimensionner une image trop grande avant de l'envoyer (utile pour accélérer l'analyse avec `moondream`).

---

## 📋 Comparaison : Modèle vision vs Pipeline hybride

| Approche | Comment ça marche ? | Avantage | Inconvénient |
|---|---|---|---|
| **Modèle vision seul** | Un seul modèle (LLaVA) lit l'image + répond | Simple, une seule étape | Moins bon en texte/tool calling. Consomme VRAM. |
| **Pipeline hybride** | 1. LLaVA regarde l'image et écrit une description. 2. Qwen 2.5 lit cette description + fait les calculs/outils. | Le meilleur des deux mondes | Deux modèles à charger (sauf si on les charge à la volée) |

> Pour votre GTX 10xx, je recommande d'utiliser **deux agents séparés** :
> - `agent_images.py` pour analyser les images et documents scannés (OCR)
> - `agent_documents.py` pour les questions complexes avec outils (calcul, documents texte)
>
> Vous pouvez copier-coller la description d'une image dans l'autre agent si besoin.

---

## 🎯 Idées d'utilisation concrètes

- **Numériser un document papier** : photographiez-le, demandez à l'agent : *"Extrais tout le texte de cette image."* → vous obtenez un texte copiable.
- **Analyser un graphique** : envoyez une capture d'écran de courbe boursière, demandez *"Quelle est la tendance générale ?"*
- **Décrire une photo pour un malvoyant** : *"Décris cette scène en détail."*
- **Vérifier un schéma électrique** : *"Quelle est la valeur de cette résistance sur le schéma ?"*
- **Traduction visuelle** : photographiez un panneau en étranger, demandez *"Traduis le texte de ce panneau."*

---

## ⚠️ Limites à connaître

1. **Qualité des modèles locaux** : `moondream` et `llava` sont bons, mais moins précis que GPT-4V ou Claude Vision (qui sont des modèles cloud géants). Ils peuvent parfois halluciner (voir un objet qui n'est pas là).
2. **OCR limité** : l'OCR local est pratique pour du texte clair, mais un texte manuscrit ou très stylisé peut être mal lu. Pour un OCR professionnel, utilisez `Tesseract` (mais c'est un autre outil).
3. **Taille des images** : une image 4K pèse lourd en base64 et ralentit l'analyse. L'agent resize automatiquement si nécessaire.
4. **Mémoire contextuelle** : les images en base64 dans l'historique consomment beaucoup de tokens (place dans le cerveau). L'agent limite l'historique pour éviter la saturation.
