---
name: 12-bases-de-donnees
description: Synthèse cours Bases de données M1 Statistique Strasbourg (E. Claeys, 6 PDFs) — Modélisation MCD/MLD/Merise, clés primaires/étrangères, SELECT/WHERE, jointures, sous-requêtes, dépendances fonctionnelles et normalisation
metadata:
  type: reference
---

# Bases de données — synthèse unifiée (E. Claeys, M1 Statistique 2018-2020)

> Cours **bases de données relationnelles** (méthode Merise, SQL) — 6 PDFs au total. Synthèse consolidée.

## 1. Modélisation des données (méthode Merise) — `Cours Modélisation v3.pdf`

### 1.1 Trois niveaux d'abstraction

| Niveau | Sigle | Contenu |
|---|---|---|
| **Conceptuel** | **MCD** | Entités, associations, cardinalités. Indépendant du SGBD. Pour échanger entre informaticiens et non-informaticiens. |
| **Logique** | **MLD** (= MLDR, MRD, MLRD) | Tables, clés primaires, clés étrangères. Adapté à un SGBD relationnel. |
| **Physique** | (MPD) | Index, partitionnement, optimisation. |

### 1.2 MCD — Modèle Conceptuel des Données (Entity/Relationship)

**Notations** (méthode Merise) :
- **Entité** = rectangle, nommée au pluriel, contient des **propriétés atomiques**
- Une propriété unique = **identifiant** (= future clé primaire)
- **Association** = ovale, nommée par un verbe, **cardinalités** sur chaque côté

### 1.3 Cardinalités

| Notation | Sens |
|---|---|
| `0,1` | 0 ou 1 (optionnel, unique) |
| `1,1` | exactement 1 (obligatoire, unique) |
| `0,N` | 0 à plusieurs (optionnel, multiple) |
| `1,N` | 1 à plusieurs (obligatoire, multiple) |

**Exemple** : une usine est implantée dans **1,1** pays ; un pays peut avoir **0,N** usines.

### 1.4 Méthode Merise
- Créée années 70 sur commande de l'État français
- Auteur principal : **Hubert Tardieu**
- Basée sur le modèle relationnel de **Edgar F. Codd** (1970, IBM San José)

---

## 2. Passage du MCD au MLD (3 règles)

### Règle 1 : Toute entité du MCD devient une table du MLD
- L'identifiant devient la **clé primaire**
- Les propriétés deviennent les attributs (colonnes)

**Exemple** : `CLIENT(numClient, nom, prenom, adresse)` (numClient = clé primaire, soulignée).

### Règle 2 : Association 1:N → clé étrangère
Une association de type 1:N (un côté à 1, l'autre à n) se traduit par la **création d'une clé étrangère** côté **N**, référençant la clé primaire côté **1**.

**Exemple** : CLIENT (0,N) ─ passe ─ (1,1) COMMANDE
→ `CLIENT(numClient, nom, …)`
→ `COMMANDE(numCommande, dateCommande, #numClient)` (# = clé étrangère)

### Règle 3 : Association N:N → table de jonction
Une association N:N se traduit par la **création d'une nouvelle table** dont la clé primaire est composée des clés étrangères des entités liées + éventuelles propriétés de l'association.

**Exemple** : COMMANDE (1,N) ─ concerne (quantité) ─ (1,N) PRODUIT
→ `COMMANDE(numCommande, dateCommande)`
→ `PRODUIT(refProduit, libelleProduit)`
→ `CONCERNE(#numCommande, #refProduit, quantité)` (clé composite)

⚠️ **Bon usage** : renommer la table de jonction avec un nom métier significatif (ex: `LIGNE_DE_COMMANDE` plutôt que `CONCERNE`).

### Cas particulier — cardinalité (0,1)
Plutôt que de mettre une clé étrangère avec NULL possible (mauvaise pratique car ambigu), **créer une table de jonction** comme pour le N:N.

---

## 3. Clés primaires et étrangères — `Cours clef_primaire_etrangere.pdf`

### 3.1 Clé primaire
> **Définition** : contrainte d'unicité, composée d'une ou plusieurs colonnes, identifiant chaque tuple de manière unique.

Propriétés :
- ✅ Valeurs uniques (jamais de doublons)
- ✅ Valeurs **non nulles** obligatoires
- ✅ Création automatique d'un **index** (pour rechercher rapidement)

### 3.2 Choix de la clé primaire
Trois critères à respecter :
1. La valeur ne sera **jamais nulle**
2. L'utilisateur saisit-il la valeur ou faut-il la générer ?
3. Pas de doublons

**Bonne pratique recommandée** :
- Utiliser une **colonne `id` auto-incrémentée** de type `INT UNSIGNED`
- Avantages : pas d'erreur de saisie, recherches plus rapides sur entiers que sur textes

```sql
CREATE TABLE Animal (
    id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    espece VARCHAR(40) NOT NULL,
    nom VARCHAR(30),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
```

⚠️ Une seule clé primaire par table. Une seule colonne peut être auto-incrémentée (généralement la clé primaire).

### 3.3 Clé étrangère
> Une clé étrangère identifie une colonne référençant la clé primaire d'une autre table. C'est le **principe fondamental des BDD relationnelles**.

**Fonction principale** : assurer l'**intégrité référentielle** de la base.

**Exemple** : si la colonne `Commande.numClient` est définie comme clé étrangère vers `Client.numClient`, MySQL **refusera** d'insérer une commande avec un numéro de client inexistant.

### 3.4 Notes techniques
- La colonne référencée doit avoir un **index** (généralement parce qu'elle est clé primaire)
- Les types doivent être **strictement identiques** des deux côtés
- Tous les moteurs ne supportent pas les clés étrangères : ✅ **InnoDB** oui, ❌ MyISAM non

---

## 4. Sélection — SELECT / WHERE (`Cours Selection.pdf`)

### 4.1 Syntaxe de base
```sql
SELECT [DISTINCT] colonnes
FROM table
[WHERE conditions]
[GROUP BY colonnes]
[HAVING conditions_agrégat]
[ORDER BY colonnes]
[LIMIT n]
```

### 4.2 Clauses obligatoires
- `SELECT` : liste des attributs à extraire
- `FROM` : table(s) à interroger

### 4.3 Clause WHERE — conditions
Évaluée ligne par ligne, retourne VRAI/FAUX.

**Opérateurs logiques** : `AND`, `OR`, `NOT`

⚠️ **Précédence** : AND s'évalue **avant** OR. Toujours utiliser des **parenthèses** pour clarifier !
```sql
SELECT * FROM Produit
WHERE color='rouge' AND color='vert' OR color='blue';
-- équivaut à : (rouge ET vert) OU bleu
-- Pour le sens « rouge ET (vert OU bleu) », il faut parenthéser
```

### 4.4 Opérateurs de comparaison
| Opérateur | Sens |
|---|---|
| `=`, `!=`, `<>` | égal, différent |
| `<`, `>`, `<=`, `>=` | inégalités |
| `[NOT] BETWEEN expr1 AND expr2` | dans l'intervalle |
| `[NOT] IN (expr1, expr2, …)` | dans la liste |
| `[NOT] LIKE 'chaîne'` | correspond au motif (% = joker) |
| `IS [NOT] NULL` | est nul / n'est pas nul |

### 4.5 Création / suppression
```sql
CREATE DATABASE nom_base CHARACTER SET 'utf8';
CREATE TABLE nom_table (...);
DROP DATABASE nom_base;
DROP TABLE nom_table;
```

---

## 5. Jointures — `Cours Jointures.pdf`

> Les jointures permettent d'**associer plusieurs tables** dans une même requête, exploitant la puissance des BDD relationnelles.

### 5.1 Types de jointures (avec diagrammes de Venn)

| Type | Résultat |
|---|---|
| `INNER JOIN` | **Intersection** A∩B : lignes où la condition est vraie dans les 2 tables. **La plus courante.** |
| `LEFT [OUTER] JOIN` | Toutes les lignes de A + correspondances dans B (NULL sinon) |
| `RIGHT [OUTER] JOIN` | Toutes les lignes de B + correspondances dans A (NULL sinon) |
| `FULL [OUTER] JOIN` | Toutes les lignes des deux tables |
| `NATURAL JOIN` | Jointure naturelle quand les colonnes portent le même nom |
| `UNION` | Union des résultats (concaténation verticale) |

### 5.2 Syntaxe
```sql
SELECT *
FROM A
INNER JOIN B ON A.key = B.key;
```

### 5.3 Patterns utiles
- **Lignes orphelines** (dans A mais pas dans B) :
```sql
SELECT * FROM A
LEFT JOIN B ON A.key = B.key
WHERE B.key IS NULL;
```

---

## 6. Sous-requêtes (concepts standards)

Une sous-requête est un `SELECT` imbriqué dans une autre requête.

### 6.1 Emplacements
- Dans **WHERE** : pour filtrer sur un résultat
- Dans **FROM** : pour créer une "table temporaire"
- Dans **SELECT** : pour calculer une valeur dérivée

### 6.2 Opérateurs spécifiques
| Opérateur | Sens |
|---|---|
| `IN (SELECT …)` | l'expression est dans le résultat |
| `EXISTS (SELECT …)` | la sous-requête retourne au moins une ligne |
| `ANY` / `SOME` | comparaison avec au moins un résultat |
| `ALL` | comparaison avec tous les résultats |

### 6.3 Exemple
```sql
-- Clients ayant commandé au moins une fois en 2025
SELECT nom FROM Client
WHERE numClient IN (
    SELECT numClient FROM Commande
    WHERE YEAR(dateCommande) = 2025
);
```

---

## 7. Dépendances fonctionnelles & Normalisation — `Cours DP FN v3.pdf`

### 7.1 Pourquoi normaliser ?

**3 problèmes inhérents à une mauvaise conception** :
1. **Anomalies de mise à jour** : données redondantes → incohérences si oubli (ex: changer un prénom à 2 endroits)
2. **Valeurs nulles** : si on garde tout dans une table, il faut souvent des NULL pour conserver les voitures sans propriétaire ou personnes sans voiture
3. **Anomalies d'insertion / suppression** : impossible de saisir une personne sans voiture, etc.

### 7.2 Conception par abstractions successives (5 étapes)
1. Perception du monde réel et des besoins
2. Élaboration du schéma conceptuel (MCD)
3. Conception du schéma logique (MLD)
4. **Affinement du schéma logique = normalisation**
5. Élaboration du schéma physique (index, partitionnement)

### 7.3 Décomposition sans perte
Décomposer R en R₁, R₂, …, Rₙ tels que **R = JOIN(R₁, R₂, …, Rₙ)** — sinon **perte d'information**.

### 7.4 Dépendances Fonctionnelles (DF) ⭐

**Origine** : Delobel & Rissanen, IBM Research San José, 1971.

**Définition formelle** : Soit R(A₁, …, Aₙ) un schéma de relation. On dit que X → Y (X **détermine** Y) si :
$$ \forall t_1, t_2 \in R, \quad \text{Proj}_X(t_1) = \text{Proj}_X(t_2) \implies \text{Proj}_Y(t_1) = \text{Proj}_Y(t_2) $$

**Interprétation** : à chaque valeur de X correspond **une seule** valeur de Y.

**Exemple** dans une relation VOITURE :
- `NV → COULEUR` (le numéro détermine la couleur)
- `TYPE → MARQUE`
- `TYPE → PUISSANCE`

### 7.5 Axiomes d'Armstrong ⭐
| Axiome | Énoncé |
|---|---|
| **Réflexivité** | Y ⊆ X ⟹ X → Y |
| **Augmentation** | X → Y ⟹ XZ → YZ |
| **Transitivité** | X → Y et Y → Z ⟹ X → Z |

Règles déduites :
- **Union** : X → Y et X → Z ⟹ X → YZ
- **Pseudo-transitivité** : X → Y et WY → Z ⟹ WX → Z
- **Décomposition** : X → Y et Z ⊆ Y ⟹ X → Z

### 7.6 Concepts dérivés
- **Fermeture transitive F⁺** : ensemble de TOUTES les DF déductibles de F
- **Équivalence** : deux ensembles ont même fermeture transitive
- **Couverture minimale** : sous-ensemble minimal de F générant la même fermeture transitive (DF non redondantes)

### 7.7 Formes normales (non détaillé dans le PDF lu mais standard du cours)
| Forme | Critère |
|---|---|
| **1NF** | Attributs atomiques (pas de listes/tableaux dans une cellule) |
| **2NF** | 1NF + tout attribut non-clé dépend de TOUTE la clé (pas d'une partie) |
| **3NF** | 2NF + pas de DF entre attributs non-clés (X → Y où ni X ni Y n'est clé) |
| **BCNF** (Boyce-Codd) | Forme normale de Boyce-Codd : toute DF X → Y a X comme superclé |

Objectif : **éliminer la redondance** sans perdre d'information ⇒ aboutir à un schéma optimal (typiquement 3NF ou BCNF).

---

## 🎯 Applications au projet TradingMonitor

### Lien direct avec ce qui existe déjà
Le projet utilise **SQLite** (`results.db`, `snapshots.db`) — qui est une BDD relationnelle. Tous les concepts vus s'appliquent.

### MCD/MLD pour le Bloc 2 (events normalisés) — angle de rapport ⭐

Le **Bloc 2** (events government contracts + Congress trades) est un cas d'école pour la modélisation :

#### MCD proposé
```
GOUVERNEMENT (cik, nom_société, secteur, …)
  │ 1,N
  │ obtient
  │ 1,1
CONTRAT (id_contrat, date_signature, montant, durée, type)
  │ 1,N
  │ référence
  │ 1,1
NAICS (code_naics, intitulé, secteur_associé)

POLITICIEN (cik_politicien, nom, parti, chambre)
  │ 1,N
  │ trade
  │ 1,1
TRADE_INSIDER (id_trade, date, montant, sens, ticker, #cik_politicien)
```

#### MLD résultant
```
GOUVERNEMENT(cik, nom_société, secteur)
CONTRAT(id_contrat, date_signature, montant, #cik_société, #code_naics)
NAICS(code_naics, intitulé, secteur_associé)
POLITICIEN(cik_politicien, nom, parti, chambre)
TRADE_INSIDER(id_trade, date, montant, sens, ticker, #cik_politicien)
```

➡️ **Démontre la compétence BDD du cours dans le rapport**, au-delà du simple "j'ai stocké en SQLite".

### Normalisation = anti-redondance
**Erreur fréquente** dans des projets data science amateurs : tout mettre dans un seul DataFrame plat. La normalisation montre qu'on a réfléchi à la structure.

**Exemple concret pour le projet** : les `trades.csv` du Bloc 1 (38 035 lignes). Si on a des colonnes `ticker_secteur`, `ticker_industrie` répétées 1000 fois pour le même ticker, c'est une violation de la 2NF. Solution : table séparée `TICKER(ticker, secteur, industrie)`.

### Jointures SQL pour le rapport
Au lieu de gros joins en Python, montrer qu'on peut faire :
```sql
SELECT t.ticker, t.return_net, c.contract_amount
FROM Trades t
LEFT JOIN Contracts c ON t.ticker = c.ticker
                     AND c.date_signature BETWEEN t.entry_date - INTERVAL '30 DAYS' 
                                              AND t.entry_date;
```
⇒ Plus performant et plus lisible.

### Clés étrangères = intégrité référentielle
Pour éviter d'avoir des trades qui référencent des tickers inexistants : déclarer la clé étrangère avec contrainte ⇒ le SGBD garantit l'intégrité.

### Auto-incrément vs IDs métier
Pour le Bloc 1, chaque trade pourrait avoir :
- `id INTEGER PRIMARY KEY AUTOINCREMENT` (clé technique)
- `(ticker, entry_date, exit_date)` (clé métier composite — contrainte UNIQUE)

⇒ Le cours recommande la clé auto-incrémentée pour les performances.

---

## ✅ Méthodes / concepts acquis
- Méthode **Merise** (MCD, MLD, MPD)
- Entités, propriétés, associations, cardinalités
- 3 règles de passage MCD → MLD
- Clé primaire, clé étrangère, intégrité référentielle
- Auto-incrément, `InnoDB`
- **SELECT, WHERE** (opérateurs comparaison, logiques)
- BETWEEN, IN, LIKE, IS NULL
- **5 types de JOIN** (INNER, LEFT, RIGHT, FULL, NATURAL)
- UNION
- Sous-requêtes (IN, EXISTS, ANY, ALL)
- **Dépendances fonctionnelles X → Y**
- **Axiomes d'Armstrong** (réflexivité, augmentation, transitivité)
- Fermeture transitive F⁺
- Couverture minimale
- Formes normales (1NF, 2NF, 3NF, BCNF — concepts)
- Décomposition sans perte

## 🆕 À étudier (PAS dans ces cours mais utile pour le projet)
- **GROUP BY**, **HAVING**, fonctions d'agrégation (SUM, AVG, COUNT)
- **Window functions** (LAG, LEAD, ROW_NUMBER, RANK) — très utile pour séries temporelles
- **CTE** (Common Table Expressions, WITH ...) — pour requêtes complexes lisibles
- **Index** (création, types : B-tree, hash, full-text)
- **Vues** (CREATE VIEW)
- **Transactions** (BEGIN, COMMIT, ROLLBACK, isolation levels)
- **Triggers** et **stored procedures**
- **EXPLAIN** pour optimisation
- Différences entre SGBD : MySQL / PostgreSQL / SQLite / SQL Server
- NoSQL (MongoDB, Redis) — alternative pour gros volumes non structurés
