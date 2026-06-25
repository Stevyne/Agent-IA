# 📄 Agent lecteur de documents (PDF, Word, TXT)

## Qu'est-ce qu'on va construire ?

Votre agent deviendra une **bibliothécaire intelligente** :

1. **Vous déposez** des fichiers dans un dossier `documents/` (PDF, Word, TXT)
2. **L'agent les lit** automatiquement au démarrage
3. **L'agent les indexe** dans une base de données "intelligente" (ChromaDB)
4. **Vous posez des questions** comme :
   - *"Résume le contrat de location"*
   - *"Extrais tous les passages qui parlent de la clause de non-concurrence"*
   - *"Quel est le chiffre d'affaires mentionné dans le rapport PDF ?"*
   - *"Compare les deux documents sur le thème de l'environnement"*
5. **L'agent utilise un outil** pour fouiller dans les documents et vous répond avec **citations précises** (fichier + page + texte exact)

---

## 📚 Les nouvelles bibliothèques Python nécessaires

Avant, on avait installé `ollama` et `streamlit`. Maintenant, on ajoute 3 outils pour lire les documents :

| Bibliothèque | À quoi ça sert ? | Analogie |
|---|---|---|
| **`pypdf`** | Ouvrir un PDF et extraire le texte page par page | Un **scanner** qui lit chaque page |
| **`python-docx`** | Ouvrir un Word (.docx) et extraire les paragraphes | Un **défroisseur** qui lit les paragraphes |
| **`chromadb`** | Base de données vectorielle (déjà vu) | La **carte GPS** des idées |

### Installation
```bash
pip install pypdf python-docx chromadb ollama
```

> **Note** : `chromadb` va télécharger automatiquement un petit modèle (~80 Mo) pour transformer les textes en "coordonnées GPS" (embeddings). C'est fait une seule fois.

---

## 🏗️ Architecture du nouveau système

### Le problème de l'ancienne version
Avant, dans `agent_avec_rag.py`, le programme injectait **automatiquement** les documents dans chaque conversation. C'était comme si le serveur vous suivait partout avec **toute la bibliothèque sur le dos**, même quand vous demandiez juste l'heure. C'est lent et inutile.

### La solution : l'outil `rechercher_documents`
On transforme la recherche documentaire en **outil optionnel** (comme la calculatrice ou la montre). L'IA décide **elle-même** quand l'utiliser.

**Le déroulement :**
1. Vous demandez : *"Quelle est la clause de résiliation dans mon contrat PDF ?"*
2. L'IA réfléchit : *"C'est une question sur les documents. J'ai un outil pour ça."*
3. L'IA appelle l'outil `rechercher_documents` avec votre question comme requête.
4. L'outil fouille dans ChromaDB et retourne 5 passages pertinents avec leurs sources (fichier, page).
5. L'IA reçoit ces passages et répond : *"Dans le fichier `contrat.pdf` page 3, il est écrit : 'La résiliation peut être effectuée avec un préavis de 3 mois...'"*

---

## 📖 Comment on lit les formats

### PDF (`.pdf`)
```python
from pypdf import PdfReader

reader = PdfReader("fichier.pdf")
for i, page in enumerate(reader.pages):
    texte = page.extract_text()
    # texte = contenu de la page i
```
On lit **page par page**. On garde le numéro de page dans les métadonnées.

### Word (`.docx`)
```python
from docx import Document

doc = Document("fichier.docx")
for i, paragraphe in enumerate(doc.paragraphs):
    texte = paragraphe.text
    # texte = contenu du paragraphe i
```
On lit **paragraphe par paragraphe**. On garde le numéro de paragraphe.

### TXT (`.txt`)
```python
with open("fichier.txt", "r", encoding="utf-8") as f:
    texte = f.read()
```
On lit tout le fichier, puis on le découpe en morceaux (chunks).

---

## 🔍 Le découpage et l'indexation (RAG)

### Métadonnées : les étiquettes sur chaque morceau
Chaque "morceau" de texte stocké dans ChromaDB porte une **étiquette** (métadonnée) :
```json
{
  "source": "contrat.pdf",
  "type": "pdf",
  "page": 3
}
```

Ainsi, quand l'agent trouve un passage, il sait **d'où il vient** exactement et peut vous le citer.

### Détail du découpage

- **PDF** : on garde chaque page comme un chunk (ou on découpe les pages trop longues en 2)
- **Word** : on regroupe les paragraphes par blocs de 500 caractères
- **TXT** : on découpe tous les 500 caractères avec chevauchement de 100 caractères

---

## 🤖 Le Tool Calling pour la recherche

On ajoute un nouvel outil dans le menu de l'IA :

```json
{
  "type": "function",
  "function": {
    "name": "rechercher_documents",
    "description": "Recherche des passages pertinents dans les documents PDF, Word et TXT de la bibliothèque. À utiliser dès que l'utilisateur pose une question sur les documents.",
    "parameters": {
      "type": "object",
      "properties": {
        "requete": {"type": "string", "description": "La question ou le sujet à chercher dans les documents"},
        "n_resultats": {"type": "integer", "description": "Nombre de passages à retourner (défaut: 5)"}
      },
      "required": ["requete"]
    }
  }
}
```

L'IA peut maintenant **décider** d'utiliser cet outil quand elle veut. Vous n'avez pas besoin de dire "cherche dans mes documents", elle devine... mais vous pouvez aussi le dire explicitement pour être sûr.

---

## 🎯 Exemples de conversation possibles

```
Vous > Résume le document rapport_annuel.pdf
Agent > [Utilise l'outil rechercher_documents avec "résumé rapport annuel"]
Agent > Le document `rapport_annuel.pdf` présente une entreprise...

Vous > Extrais tous les passages qui parlent de la clause de confidentialité
Agent > [Utilise l'outil rechercher_documents avec "clause confidentialité"]
Agent > J'ai trouvé 3 passages :
1. Dans `contrat.docx` (paragraphe 12) : "Le salarié s'engage à garder confidentiel..."
2. Dans `contrat.docx` (paragraphe 45) : "Cette clause s'applique pendant 2 ans..."
3. Dans `annexe.pdf` (page 8) : "La confidentialité couvre aussi les données clients..."

Vous > Quel est le montant de la facture 104 ?
Agent > [Utilise l'outil rechercher_documents avec "facture 104 montant"]
Agent > Dans le document `factures.pdf` page 22, la facture 104 est au montant de 1 240 €.
```

---

## ⚠️ Limites à connaître

1. **PDF scannés / images** : `pypdf` ne lit que le texte "digital". Si votre PDF est une **image scannée** (photo d'un papier), il ne verra rien. Il faudrait un OCR (reconnaissance optique de caractères) comme `pytesseract`, mais c'est plus lourd.
2. **Tableaux complexes** : `pypdf` et `python-docx` lisent le texte brut. Les tableaux complexes peuvent perdre leur mise en forme (les cases deviennent des lignes de texte mélangées).
3. **Mémoire du modèle** : l'IA ne peut pas "tenir" un document de 500 pages en mémoire d'un coup. Elle le consulte par morceaux de 5 passages à la fois. Si vous voulez une vue d'ensemble, demandez-lui d'abord un résumé, puis des questions précises.
4. **Non, elle n'écrit pas dans vos fichiers** : l'IA lit seulement. Elle ne peut pas modifier votre PDF ou Word (ce serait un autre projet).

---

## 🚀 Prochaines étapes suggérées

- **Mémoire + Documents** : combinez ce fichier avec `agent_avec_memoire.py` pour qu'elle se souvienne de VOUS en plus de vos documents.
- **Interface web** : adaptez ce script avec Streamlit (remplacez `input()` par `st.chat_input()` comme dans `app_web.py`).
