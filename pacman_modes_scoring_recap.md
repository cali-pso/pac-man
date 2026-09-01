# Récap projet Pacman — modes & scoring

**Principe d'archi de base :** un mode = un `Ruleset` (paquet de paramètres + hooks). Les modes se *fusionnent* en un ruleset actif. On a dégagé **trois axes orthogonaux** plutôt qu'une liste plate :

- **Horloge** : temps réel *ou* tactics (tour par tour) — on en choisit exactement une
- **Difficulté** : standard *ou* hardcore — on en choisit exactement une
- **Flavor modes** (empilables) : shadow, roguelite, 2 joueurs…

## Tableau des modes

| Mode | Axe | Effet principal | Empilable ? | Notes / à trancher |
|---|---|---|---|---|
| **Standard** | Difficulté | Jeu de base : 3 vies, super-pacgums, temps plein | base | Doit rester conforme au sujet |
| **Hardcore** | Difficulté | 0 vie, pas de super-pacgums, temps ÷2 | exclut les autres *flavors*, mais compatible tactics | Barème le plus haut |
| **Temps réel** | Horloge | Budget = secondes | — | Horloge par défaut |
| **Tactics** | Horloge | Tour par tour, budget = nombre de coups | compatible 2J + flavors + hardcore | Lift structurel (change la boucle) |
| **Shadow** | Flavor | Couloirs sombres, zone lumineuse autour de Pac-Man (↑ en mangeant, ↓ avec le temps) ; super-pacgum spécial « shine bright » (illumine X sec/coups) | oui | Doit lire l'horloge abstraite, pas des secondes en dur |
| **Roguelite** | Flavor | Couche méta / progression entre niveaux | oui | Le plus lourd → priorité basse |
| **2 joueurs** | Flavor | 1–2 joueurs, clavier et/ou manette | oui | ⚠️ manette : vérifier équivalent MLX avant de promettre |

## Barèmes de score (A/B/C/D)

La lettre = **nombre de flavor modes actifs**. Hardcore = barème séparé (car exclusif des flavors).

| Barème | Flavors actifs | Pacgum | Super | Fantôme |
|---|---|---|---|---|
| A | 0 (base) | 5 | 25 | 100 |
| B | 1 | 6 | 30 | 120 |
| C | 2 | 7 | 35 | 140 |
| D | 3 | 8 | 40 | 160 |
| Hardcore | exclusif | 12 | — | — |

*(valeurs indicatives à ajuster — envisager une montée non linéaire 5→7→10→14 pour mieux récompenser l'empilement)*

## Bonus de fin de niveau

Déclenché quand **tous les pacgums** sont mangés (= anti-abus intégré : « vite » veut dire « tout nettoyer vite », jamais rusher).

| | Clear bonus | Bonus budget restant | Cap |
|---|---|---|---|
| Standard (temps) | 100 | 1 pt/seconde | — |
| Hardcore (temps) | 250 | 15 pts/seconde | 450 |
| Tactics standard | 100 | 2 pts/coup économisé | 200 |
| Tactics hardcore | 250 | 25 pts/coup économisé | 500 |

Le budget (secondes ou coups) passe par une **horloge abstraite** : même code de bonus, seule l'unité change.

## Points ouverts à décider ensemble

1. **Ordre des tours en 2J tactics** : alterné (simple, lisible) ou simultané (tendu, mais résolution des collisions à gérer) ? Et « un tour » = un round complet, pas un coup individuel.
2. **Courbe des barèmes** : linéaire (+1) ou accélérée pour vraiment récompenser le risque ?
3. **Réglage `per_second`/`cap` hardcore** : à caler après un playtest chronométré.
4. **Priorités de dev** : base solide → shadow → hardcore → 2J → tactics → roguelite (roguelite en dernier, scope le plus large).
