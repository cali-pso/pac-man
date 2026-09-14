# Récap projet Pacman — modes, scoring, roguelite & son (v4)

**Principe d'archi :** un mode = un `Ruleset` (paramètres + hooks) ; les modes se *fusionnent* en un ruleset actif. **Deux axes** (tactics abandonné) :

- **Difficulté** : standard *ou* hardcore — exactement une
- **Flavor modes** empilables : shadow, roguelite, 2 joueurs

## Tableau des modes

| Mode | Axe | Effet principal | Empilable ? | Notes |
|---|---|---|---|---|
| **Standard** | Difficulté | Reproduction **exacte du Pac-Man du sujet**, timer inclus (le chrono peut mettre fin à la partie) | base | Timer **fonctionnel**, mais **pas de bonus de score** lié au temps |
| **Hardcore** | Difficulté | 0 vie, pas de super-pacgums, temps ÷2 ; **débloqué après avoir fini le mode normal** | **exclusif** (désactive tous les flavors) | Barème le plus haut ; déblocage persistant |
| **Shadow** | Flavor | Couloirs sombres, zone lumineuse autour de Pac-Man (↑ en mangeant, ↓ avec le temps) ; super-pacgum « shine bright ». **Design figé.** | oui | — |
| **Roguelite** | Flavor | Choix d'un bonus/malus après chaque niveau (section dédiée) | oui | Le plus lourd → priorité basse |
| **2 joueurs** | Flavor | 3 sous-modes : versus / coop / random. **Clavier uniquement, pas de manette.** | oui | Voir détail ci-dessous |

## Mode 2 joueurs — 3 sous-modes

| Sous-mode | Contrôles | Condition de victoire / note |
|---|---|---|
| **Versus** | J1 = Pac-Man ; J2 = un fantôme (lequel **change selon le niveau**), les 3 autres = IA | **J2 (fantôme) gagne quand les vies de Pac-Man = 0** |
| **Coop** | Même Pac-Man partagé : J1 = haut/bas, J2 = gauche/droite | Simple et chaotique |
| **Random** | Même Pac-Man partagé, alternance : l'écran indique qui joue, bascule **aléatoire** en cours de niveau | Bascule aléatoire bornée **[3 s, 15 s]** (ajustable en cours de dev) |

## Scoring

- **Standard (aucun mode)** = Pac-Man du sujet : pacgum **10**, super-pacgum **50**, fantômes **200 → 400 → 800 → 1600**. Timer fonctionnel, **sans bonus de temps**.
- **Modes (≥ 1 flavor actif)** = **un seul barème modifié**, identique quel que soit le nombre de modes actifs (les scores sont affichés séparément au menu → pas besoin de moduler par mode).
- **Hardcore** = barème séparé (exclusif).

| Barème | Quand | Pacgum | Super | Fantôme |
|---|---|---|---|---|
| Standard | aucun mode | 10 | 50 | 200→400→800→1600 |
| Modes | ≥ 1 flavor actif | *à définir* | *à définir* | *à définir* |
| Hardcore | exclusif | le plus élevé | — | le plus élevé |

*Option : valeurs absolues, OU multiplicateur sur les valeurs réelles (arrondi entier).*
*Les lettres (S, R…) au menu ne servent qu'à **étiqueter** quels modes étaient actifs — elles n'affectent pas le barème.*

**Cumul des multiplicateurs = additif.** Chaque multiplicateur apporte son surplus au-dessus de 1, sommé : `total = 1 + Σ(surplus)`. Ex. roguelite ×2 (+1,0) + mega ×1,5 (+0,5) → **×2,5**. Si le barème est exprimé en multiplicateur, il entre dans la même somme.

### Bonus de fin de niveau (modes actifs uniquement)

Déclenché quand **tous les pacgums** sont mangés.

| | Clear bonus | Bonus temps restant | Cap |
|---|---|---|---|
| Modes actifs | 100 | 1 pt/seconde | — |
| Hardcore | 250 | 15 pts/seconde | 450 |

## Cheat mode (Konami code)

- Débloqué **en cours de partie** via le Konami code (↑ ↑ ↓ ↓ ← → ← → B A) → ouvre un menu.
- **Le run n'est PAS enregistré au classement** si le cheat mode a été activé.
- **La séquence + toutes les infos doivent figurer dans le README** (le sujet exige que le cheat aide l'évaluateur à tester).
- Options : **Météore** (tue tous les fantômes instantanément, sans résurrection), **Aimant** (attire tous les pacgums), + celles du sujet (invincibilité, saut de niveau, gel des fantômes, vies bonus, vitesse accrue…).

## Roguelite — système bonus/malus

**Acquisition :** après chaque niveau, choix entre **3 options** — au départ **2 affichées + 1 cachée** (ce ratio fluctue, voir item #8) — tirées aléatoirement dans le pool débloqué **et éligible**. La cachée peut être bonus ou malus (risque/récompense).

**Pool & déblocage :**
- **10 paires** (1 bonus + son malus inverse) = **20 items**.
- Départ (avant la 1re partie) : **3 paires** débloquées — **+1/−1 vie**, **+1/−1 bouclier**, **vitesse Pac-Man ↑/↓**.
- Débloquer un bonus débloque **automatiquement son malus affilié** (items par paires).
- Déblocage via un **événement sur un niveau aléatoire, 1 max par partie** ; message en début de niveau expliquant le défi (ex. « Chaque fantôme détient un fragment d'artefact, obtenez-les tous… »).
- **Persistant** entre parties (→ sauvegarde de progression).

### Probabilité bonus/malus du tirage (anti-série)

Les 3 slots sont tirés **en séquence**, chacun bonus ou malus selon une proba qui s'auto-ajuste :
- 1er slot : **50 % bonus / 50 % malus**.
- Après chaque slot, décalage de **10 %** : un **bonus** tiré → −10 % de bonus au suivant ; un **malus** tiré → +10 % de bonus au suivant.
- Ex. 1er = bonus → 2e à **40/60** ; 1er = malus → 2e à **60/40** ; le 3e continue le décalage cumulé.
- Sur 3 tirages, reste borné dans **[30 %, 70 %]** (pas de clamp nécessaire) ; **remis à 50 %** à chaque nouveau niveau.
- La proba fixe le **type** de chaque slot ; l'éligibilité choisit ensuite l'**item concret** ; la case cachée est simplement masquée à l'écran (son type est déjà fixé par la chaîne).

### Règle d'éligibilité (garde-fous unifiés)

Chaque item porte un prédicat `est_éligible(état)`. **Le tirage ne pioche que parmi les items éligibles**, ce qui unifie tous les garde-fous :
- `−1 bouclier` : éligible seulement si bouclier ≥ 1.
- `−1 case aimant` : éligible seulement si rayon aimant > 0 (plancher à 0).
- Vitesse (Pac-Man ou fantômes) : **jamais 0** — plancher strictement positif (seul le blocage met à 0).
- `Révéler une option cachée` : éligible seulement s'il reste une option cachée.
- `+1 découvert` (révélation) : impossible si tout est déjà découvert.
- **Plancher de 3 items garanti** : pas de repli nécessaire. Les items étant débloqués par paires et les bonus quasi toujours éligibles/réobtenables, il reste toujours ≥ 3 items piochables (au pire, il ne reste que des bonus à obtenir).

### Liste des bonus / malus (paires inverses)

| # | Bonus | Malus (inverse) |
|---|---|---|
| 1 | Vitesse ↑ Pac-Man | Vitesse ↓ Pac-Man (plancher > 0) |
| 2 | +1 vie | −1 vie |
| 3 | Vitesse ↓ fantômes | Vitesse ↑ fantômes |
| 4 | Aimant +1 case | Aimant −1 case (si rayon > 0) |
| 5 | +1 bouclier (1 hit) | −1 bouclier (si bouclier ≥ 1) |
| 6 | Durée super-pacgum ↑ | Durée super-pacgum ↓ |
| 7 | Temps de départ ↑ | Temps de départ ↓ |
| 8 | Révèle 1 option cachée du choix | Cache 1 option supplémentaire |
| 9 | Fantômes bloqués X s (début niveau) | Pac-Man bloqué X s (début niveau) |
| 10 | Score ×2 | Score ÷2 |

*Ratio découvert/caché du choix (item #8) : départ 2/1, borné (min. 1 option affichée à définir).*

### Super-pacgums en roguelite

En mode roguelite, manger un super-pacgum **conserve son effet de base** (fantômes comestibles) **et y ajoute** un bonus ou malus aléatoire **tiré des 10 paires**, valable pour une **durée limitée sur le niveau actuel**.

### Mega pacgum (global, tous modes)

**1 % de chance d'apparition par niveau.** Effets cumulés **jusqu'à la fin du niveau en cours** :
- Vitesse de Pac-Man **fortement augmentée**
- **Timer gelé**
- **Tout le niveau éclairé** (pertinent en mode shadow)
- **Fantômes comestibles**
- **Score ×1,5**

Cumul : le ×1,5 s'**ajoute additivement** aux autres multiplicateurs (voir règle ci-dessous). Le timer gelé gonfle le bonus de temps de fin de niveau → **jackpot assumé** (le mega est très rare), pas à corriger.

## Persistance (2 fichiers, robustes aux erreurs)

1. **Highscores** (prévu par le sujet).
2. **Progression** : paires bonus/malus débloquées + flag « hardcore débloqué ».

## Leaderboards au menu principal

Switch entre **4 tableaux** :
- **Standard**
- **Hardcore**
- **Modes actifs** — chaque score porte les **lettres** des modes effectifs (`S` shadow, `R` roguelite…, ex. `SR`). Tous les runs à modes partageant le même barème, ils sont **directement comparables** ; les lettres sont informatives. *(coop/random y figurent avec leur lettre ; versus a sa propre table.)*
- **Versus** (table dédiée) — colonnes : **nom du gagnant**, **nom du perdant**, **qui a joué quoi** (défini en début de partie), **lettres des modes**.

## Son

Musique d'ambiance au menu, musiques en niveau, déplacement de Pac-Man, navigation menus, son spécifique du Konami code, etc.

- **Le sujet n'interdit pas une lib non graphique pour l'audio** (la contrainte MLX porte sur le graphique) → **on utilise une lib audio dédiée.**
- **Assets libres de droits ou originaux** (pas de musique sous copyright).

## Points encore à trancher

1. **Valeurs du barème Modes** (unique) et du barème Hardcore : absolues ou multiplicateur ?
2. **Borne du ratio découvert/caché** (min. d'options affichées).

## Décidé

- **Barème unique pour tous les modes** (affichage séparé au menu) ; lettres = simples étiquettes.
- **Versus** : table de leaderboard dédiée (gagnant / perdant / rôles / lettres).
- **Roguelite** : 3 paires de départ (vie, bouclier, vitesse) ; tirage anti-série 50 %±10 % ; règle d'éligibilité ; plancher de 3 garanti.
- **Random** : bascule aléatoire bornée [3 s, 15 s].
- **Hardcore** : exclusif (confirmé pour l'instant).
- **Lib graphique** : `mlx_CLXV` (MLX officielle 42, module Python inclus, même écosystème que le maze package).
- **Priorités de dev** : loader MazeGenerator → shadow → hardcore → 2 joueurs → roguelite.
