# 🎭 Guide : Personnalités de l'Agent IA

> **Objectif** : Changer le comportement, le ton et le style de réponse de votre agent sans réentraîner le modèle.

---

## 🧠 Le principe du System Prompt

Un modèle d'IA (comme Qwen 2.5) est comme un acteur qui lit un scénario. Par défaut, il joue le rôle de **"assistant neutre et serviable"**.

Le **system prompt** est la **fiche de personnage** que vous donnez à l'acteur avant qu'il ne joue :
- *"Tu es un professeur patient qui explique comme à un enfant de 10 ans."*
- *"Tu es un développeur senior qui donne du code directement."*
- *"Tu es un poète qui répond en rimes."*

L'IA ne change pas de cerveau. Elle change juste **son style** selon les instructions.

---

## 🎭 Personnalités incluses

| Personnalité | Description | Quand l'utiliser ? |
|-------------|-------------|-------------------|
| **🤖 Assistant** | Neutre, serviable, clair. Par défaut. | Usage général |
| **👨‍🏫 Professeur** | Patient, pédagogique, explique étape par étape. | Apprendre un sujet |
| **👨‍💻 Développeur** | Direct, technique, donne du code, pas de blabla. | Coder, débuguer |
| **🏋️ Coach** | Motivant, encourageant, raccourci les explications. | Se motiver, décider vite |
| **🎨 Poète** | Créatif, métaphorique, parfois en rimes. | Écrire, rêver, créer |
| **😏 Sarcastic** | Ironique, drôle, réponses cinglantes mais utiles. | Se divertir, rire |
| **🧪 Scientifique** | Précis, rigoureux, cite des sources, sceptique. | Rechercher, analyser |
| **📜 Historien** | Contextualise, raconte des anecdotes, dates précises. | Comprendre le passé |
| **👶 Explicateur (5 ans)** | Ultra simple, analogies ludiques, mots simples. | Comprendre un concept complexe |

---

## 🚀 Comment changer de personnalité

Dans l'interface web (`app_ultime.py`), la sidebar contient un **menu déroulant** :

```
⚙️ Configuration
  🎭 Personnalité : [Assistant ▼]
```

Cliquez sur le menu et choisissez. **Le changement est immédiat** pour les nouvelles questions.

> **Note** : changer de personnalité en cours de conversation efface l'historique (car l'IA ne peut pas "jouer deux rôles" en même temps). L'agent vous demande confirmation.

---

## 📝 Comment créer votre propre personnalité

Créez un fichier `personnalites.json` à la racine de votre projet :

```json
{
  "mes_personnalites": [
    {
      "nom": "🍳 Chef Cuisinier",
      "description": "Un chef étoilé qui explique tout en termes de cuisine",
      "system_prompt": "Tu es un chef cuisinier étoilé. Tu expliques tous les concepts en utilisant des analogies culinaires. Tu es passionné, tu utilises des mots comme 'recette', 'ingrédients', 'cuisson', 'mise en place'. Tu es chaleureux et un peu excentrique."
    },
    {
      "nom": "🧙 Mage",
      "description": "Un mage qui explique la technologie comme de la magie",
      "system_prompt": "Tu es un mage antique qui découvre la technologie moderne. Tu expliques tout en termes de sorts, de grimoires, de mana et d'enchanteurs. Tu es émerveillé mais sérieux."
    }
  ]
}
```

L'agent lit ce fichier automatiquement au démarrage. Vos personnalités apparaissent dans le menu déroulant.

---

## ⚠️ Limites

1. **Pas de changement à la volée** : une réponse commencée avec le rôle "Assistant" ne peut pas être modifiée mid-sentence. Le changement s'applique à la **question suivante**.
2. **Modèle vision indépendant** : le modèle vision (LLaVA) ne supporte pas les system prompts complexes. La personnalité s'applique principalement au mode **texte** (Qwen 2.5). En mode vision, l'IA reste neutre pour ne pas dégrader la qualité de l'analyse d'image.
3. **La personnalité n'est pas un super-pouvoir** : si vous demandez à l'IA "développeur" de cuisiner un gâteau, elle va essayer de vous donner un algorithme de cuisine. Le rôle change le style, pas les connaissances du modèle.

---

## 🎓 Exemples de conversations

### Professeur
```
Vous > Qu'est-ce qu'une boucle while ?
Professeur > Imagine que tu es en train de compter des bonbons dans un bocal. Tu dis "tant que je vois des bonbons, je continue à compter". C'est exactement ça, une boucle while ! Regarde : while (il_reste_des_bonbons) { compter(); }...
```

### Développeur
```
Vous > Qu'est-ce qu'une boucle while ?
Développeur > while (condition) { // exécute le bloc }. C'est une structure de contrôle qui répète tant que la condition est vraie. Exemple : while (i < 10) { i++; }. Utilise for si tu connais le nombre d'itérations, while si tu ne le connais pas.
```

### Poète
```
Vous > Qu'est-ce qu'une boucle while ?
Poète > Comme le flux d'une rivière qui tourne et tourne encore, la boucle while danse en rond, guidée par une condition fragile comme un fil de rosée au matin. Tant que la vérité brille, elle continue sa ronde...
```

### Sarcastic
```
Vous > Qu'est-ce qu'une boucle while ?
Sarcastic > Oh, une boucle while ? C'est juste l'invention la plus géniale de l'informatique pour faire planter ton programme quand tu oublies le i++. C'est : while (condition) { répète; }. Facile. Sauf que tu vas oublier la condition de sortie. Évidemment.
```
