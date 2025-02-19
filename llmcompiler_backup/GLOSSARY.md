# LLMCompiler Syntax Glossary

Ce document décrit le format exact attendu par le LLMCompiler pour les prompts et les réponses.

## Format Principal (LLMCompiler)

Le format principal attendu est :
```
Question: <question de l'utilisateur>

Thought: <raisonnement>
1. <action_name>[<args>]
Observation: <résultat>

Thought: <raisonnement suivant>
2. <action_name>[<args>]
Observation: <résultat>

...

Thought: <raisonnement final>
<N>. join()
<END_OF_PLAN>
```

### Références aux Résultats

Pour utiliser le résultat d'une action précédente dans les arguments, on utilise `$N` :
```
1. Search["population de Paris"]
2. Calculator[$1 * 2]  # Utilise le résultat de Search
3. Table[["Ville", "Population"], [["Paris", $2]]]  # Utilise le résultat de Calculator
```

Les deux formats sont valides :
- `$1`, `$2`, `$3` : format court
- `${1}`, `${2}`, `${3}` : format avec accolades

## Exemple concret :
```
Question: Show temperatures for the last 3 days

Thought: I need to check if Node-RED is operational first
1. NodeStatus[]
Observation: Node-RED is operational

Thought: Now I can get the temperature data
2. TemperatureRange[2024-02-15, 2024-02-17]
Observation: {"2024-02-15": 22.5, "2024-02-16": 23.1, "2024-02-17": 21.8}

Thought: I have all the information needed
3. join()
<END_OF_PLAN>
```

## Format ReAct (Benchmarks)

Le format ReAct, utilisé uniquement pour les benchmarks, est différent :
```
Thought: I need to find the height of Mount Everest
Action: Search[Mount Everest]
Observation: Mount Everest height is 8,848.86 meters
Thought: I need to halve the height
Action: Calculate[8848.86/2]
Observation: 4424.43
Thought: I have the answer
Action: Finish[4424.43]
```

### Comparaison des Formats

| Caractéristique | LLMCompiler | ReAct |
|-----------------|-------------|--------|
| Préfixe action | `N.` | `Action:` |
| Arguments | `tool[args]` | `tool[args]` |
| Action finale | `join()` | `Finish[answer]` |
| Fin de plan | `<END_OF_PLAN>` | Non requis |
| Structure | Plan complet | Itératif |

## Exemples Complets

### Exemple Simple
```
Question: Quelle est la température ?

Thought: Je dois d'abord vérifier si Node-RED fonctionne
1. NodeStatus[]
Observation: Node-RED is operational

Thought: Je peux maintenant obtenir la température
2. Temperature[2024-02-18]
Observation: 22.5

Thought: J'ai la réponse
3. join()
<END_OF_PLAN>
```

### Exemple avec Table
```
Question: Montre les températures des 3 derniers jours

Thought: Je dois d'abord vérifier Node-RED
1. NodeStatus[]
Observation: Node-RED is operational

Thought: Je peux obtenir les données
2. TemperatureRange[2024-02-15, 2024-02-17]
Observation: {"2024-02-15": 22.5, "2024-02-16": 23.1, "2024-02-17": 21.8}

Thought: Je vais formater les données en tableau
3. Table[["Date", "Temperature (°C)"], [["2024-02-15", "22.5"], ["2024-02-16", "23.1"], ["2024-02-17", "21.8"]]]
Observation: Table: headers=Date,Temperature (°C)|2024-02-15,22.5|2024-02-16,23.1|2024-02-17,21.8

Thought: Les données sont prêtes
4. join()
<END_OF_PLAN>
```

## Workflows et Syntaxes

LLMCompiler supporte deux workflows différents avec leurs syntaxes spécifiques :

### 1. Workflow LLMCompiler (Principal)

C'est le workflow par défaut utilisé dans l'application principale. Il utilise une architecture à deux niveaux avec un planner et un agent.

**Syntaxe des actions** :
```
Thought: raisonnement pour choisir l'action
1. tool_name[args]
Observation: résultat
Thought: nouveau raisonnement
2. another_tool[arg1, arg2]  
<END_OF_PLAN>
```

**Exemple avec dépendances** :
```
Thought: I need to check if Node-RED is operational first
1. NodeStatus[]
Observation: Node-RED is operational

Thought: Now I can get the temperature data
2. TemperatureRange[2024-02-15, 2024-02-17]
Observation: {"2024-02-15": 22.5, "2024-02-16": 23.1, "2024-02-17": 21.8}

Thought: I will format this data as a table
3. Table[["Date", "Temperature (°C)"], [["2024-02-15", "22.5"], ["2024-02-16", "23.1"], ["2024-02-17", "21.8"]]]
```

### 2. Workflow ReAct (Benchmarks)

Utilisé uniquement pour les benchmarks et comparaisons. Utilise une architecture simple avec un seul agent qui planifie et exécute de manière itérative.

**Syntaxe des actions** :
```
Thought: I need to find the height of Mount Everest
Action: Search[Mount Everest]
Observation: Mount Everest height is 8,848.86 meters
Thought: I need to halve the height
Action: Calculate[8848.86/2]
Observation: 4424.43
Thought: I have the answer
Action: Finish[4424.43]
```

**Note** : Le workflow ReAct utilise `Finish[answer]` comme action finale au lieu de `join()` dans LLMCompiler.

### Comparaison

| Caractéristique | LLMCompiler | ReAct |
|-----------------|-------------|--------|
| Architecture | Deux niveaux (planner + agent) | Un seul agent |
| Planification | Plan complet avant exécution | Itératif (action par action) |
| Format actions | `N. tool_name[args]` | `Action: tool[args]` |
| Action finale | `join()` | `Finish[answer]` |
| Utilisation | Application principale | Benchmarks uniquement |

## Gestion des Dépendances dans les Prompts

Les dépendances entre outils sont gérées différemment selon le workflow :

#### 1. LLMCompiler (ITTPC)

Les dépendances sont définies dans le PREFIX du prompt avec des guidelines explicites :

```
Guidelines:
  - Each action MUST be in the format: <action_id>. <action_name>[<args>]
  - Action IDs MUST start at 1 and increment by 1
  - Always check Node-RED status before accessing data
  - Never search for the same query twice
```

Exemple de prompt avec dépendances :
```
Action can be one of these types:
  (1) NodeStatus[]: Check Node-RED server status
  (2) Temperature[date]: Get temperature for a specific date
  (3) TemperatureRange[start_date, end_date]: Get temperature range
  (4) join(): Return the answer and finish

Guidelines:
  - Always check NodeStatus before any Temperature actions
  - Format dates as YYYY-MM-DD
  - Use join() as the last action
```

#### 2. ReAct (Benchmarks)

Les dépendances sont gérées via les guidelines du prompt :

```
Guidelines:
  - Final answer should always be in the format of Finish[answer]
  - Final answer MUST NOT contain any description
  - Never search for the same entity twice
  - When using Calculate, you cannot calculate multiple expressions in one call
  - Once you have numbers, make comparisons on your own
```

Exemple de prompt avec dépendances :
```
Action can be one of three types:
  (1) Search[entity]: search on Wikipedia
  (2) Calculate[expression]: calculate expression
  (3) Finish[answer]: return answer and finish

Guidelines:
  - Search before Calculate if you need entity information
  - Split multiple calculations into separate Calculate actions
  - Use Finish[answer] only when you have all required data
```

#### Bonnes Pratiques

1. **Dépendances Explicites** :
   - Définir clairement l'ordre des actions requises
   - Spécifier les prérequis pour chaque type d'action

2. **Gestion des Erreurs** :
   - Indiquer comment gérer les échecs d'actions
   - Définir les alternatives en cas d'erreur

3. **Format des Données** :
   - Spécifier le format attendu pour chaque type de donnée
   - Définir comment transformer les données entre les actions

4. **Limitations** :
   - Documenter les restrictions sur les combinaisons d'actions
   - Préciser les limites de chaque outil

## Erreurs Communes à Éviter

1. Format d'Action Incorrect ❌
   ```
   Action: NodeStatus()
   Action ID: 1
   ```
   Format Correct ✅
   ```
   1. NodeStatus[]
   ```

2. Oubli de Thought ❌
   ```
   1. NodeStatus[]
   2. Temperature[2024-02-18]
   ```
   Format Correct ✅
   ```
   Thought: Vérifions Node-RED
   1. NodeStatus[]
   Thought: Obtenons la température
   2. Temperature[2024-02-18]
   ```

3. Mauvaise Action de Fin ❌
   ```
   Action: Finish[réponse]
   ```
   Format Correct ✅
   ```
   4. join()
   <END_OF_PLAN>
   ```
