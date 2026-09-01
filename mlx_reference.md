# Référence des fonctions MLX (mlx_CLXV)

Fiche de référence des fonctions exposées par le module Python `mlx` (classe `Mlx`).

## Conventions d'appel

Le wrapper Python **calque les prototypes C à l'identique** :

- Le **pointeur d'instance MLX** retourné par `mlx_init()` doit être passé en **1er argument** de presque toutes les fonctions.
- Les **hooks** prennent un argument `param` supplémentaire (le `void *` du C), passé tel quel au callback.
- Les fonctions qui, en C, retournent des valeurs via des **pointeurs** (`int *`) retournent en Python un **tuple**.
- Les couleurs sont des entiers au format `0xRRGGBB`.

Références qui font autorité chez toi : `man man/man3/mlx.3` et l'en-tête `mlx.h`.
⚠️ Les signatures marquées *(à vérifier)* sont propres à cette version vulkan/`mlx_CLXV` — confirme-les dans le man si tu les utilises.

---

## Initialisation & instance

**`mlx_init()`** → `mlx_ptr`
`void *mlx_init(void)`
Ouvre la connexion au système graphique et retourne le pointeur d'instance MLX. À appeler en tout premier ; ce pointeur est requis par la quasi-totalité des autres fonctions.

**`mlx_release(mlx_ptr)`**
`int mlx_release(void *mlx_ptr)`
Libère l'instance MLX et ses ressources en fin de programme (équivalent moderne de la destruction de l'affichage). Spécifique à `mlx_CLXV`.

---

## Fenêtres

**`mlx_new_window(mlx_ptr, size_x, size_y, title)`** → `win_ptr`
`void *mlx_new_window(void *mlx_ptr, int size_x, int size_y, char *title)`
Crée une fenêtre de la taille donnée avec un titre, et retourne son pointeur.

**`mlx_clear_window(mlx_ptr, win_ptr)`**
`int mlx_clear_window(void *mlx_ptr, void *win_ptr)`
Efface tout le contenu de la fenêtre (la remplit de noir).

**`mlx_destroy_window(mlx_ptr, win_ptr)`**
`int mlx_destroy_window(void *mlx_ptr, void *win_ptr)`
Détruit la fenêtre et libère ses ressources.

---

## Dessin direct

**`mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)`**
`int mlx_pixel_put(void *mlx_ptr, void *win_ptr, int x, int y, int color)`
Dessine un seul pixel directement dans la fenêtre. Simple mais **lent** pour du rendu massif → préférer le workflow image ci-dessous.

**`mlx_string_put(mlx_ptr, win_ptr, x, y, color, string)`**
`int mlx_string_put(void *mlx_ptr, void *win_ptr, int x, int y, int color, char *string)`
Écrit une chaîne de texte à la position donnée (utile pour le HUD, les menus rapides, le debug).

---

## Images (rendu recommandé)

Principe : on dessine tout dans une **image en mémoire** (hors écran), puis on la pousse d'un coup dans la fenêtre. Bien plus rapide que `mlx_pixel_put`.

**`mlx_new_image(mlx_ptr, width, height)`** → `img_ptr`
`void *mlx_new_image(void *mlx_ptr, int width, int height)`
Crée une image (buffer de pixels) sur laquelle dessiner hors écran.

**`mlx_get_data_addr(img_ptr, ...)`** → `(addr, bits_per_pixel, size_line, endian)`
`char *mlx_get_data_addr(void *img_ptr, int *bits_per_pixel, int *size_line, int *endian)`
Retourne l'adresse du buffer de l'image et ses infos de format. Les paramètres passés par référence en C sont retournés en **tuple** en Python. C'est ce qui permet d'écrire les pixels directement en mémoire, très vite.

**`mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)`**
`int mlx_put_image_to_window(void *mlx_ptr, void *win_ptr, void *img_ptr, int x, int y)`
Affiche (blit) une image dans la fenêtre à la position donnée. **La méthode de rendu à privilégier** pour le jeu.

**`mlx_destroy_image(mlx_ptr, img_ptr)`**
`int mlx_destroy_image(void *mlx_ptr, void *img_ptr)`
Libère une image.

---

## Chargement d'images (fichiers)

**`mlx_xpm_file_to_image(mlx_ptr, filename, ...)`** → `(img_ptr, width, height)`
`void *mlx_xpm_file_to_image(void *mlx_ptr, char *filename, int *width, int *height)`
Charge un fichier XPM en image ; retourne le pointeur d'image et ses dimensions (tuple en Python).

**`mlx_png_file_to_image(mlx_ptr, filename, ...)`** → `(img_ptr, width, height)`
`void *mlx_png_file_to_image(void *mlx_ptr, char *filename, int *width, int *height)`
Idem pour un fichier PNG (ajout `mlx_CLXV`). Pratique pour charger tes sprites Pac-Man/fantômes.

---

## Boucle & hooks

**`mlx_loop(mlx_ptr)`**
`int mlx_loop(void *mlx_ptr)`
Démarre la boucle d'événements. **Bloque** jusqu'à l'arrêt : c'est le cœur runtime du programme.

**`mlx_loop_exit(mlx_ptr)`**
`int mlx_loop_exit(void *mlx_ptr)`
Demande l'arrêt propre de la boucle. À appeler depuis un hook (ex. Échap, ou fermeture de fenêtre).

**`mlx_loop_hook(mlx_ptr, funct, param)`**
`int mlx_loop_hook(void *mlx_ptr, int (*funct)(), void *param)`
Enregistre une fonction appelée à **chaque itération** de la boucle, quand aucun événement n'est en attente. C'est ici que va la mise à jour du jeu + le rendu par frame.

**`mlx_key_hook(win_ptr, funct, param)`**
`int mlx_key_hook(void *win_ptr, int (*funct)(), void *param)`
Callback appelé sur **appui de touche**. Le callback reçoit le `keycode` (+ `param`). ⚠️ 1er argument = `win_ptr`, pas `mlx_ptr`.

**`mlx_mouse_hook(win_ptr, funct, param)`**
`int mlx_mouse_hook(void *win_ptr, int (*funct)(), void *param)`
Callback sur **clic souris** (bouton + position).

**`mlx_expose_hook(win_ptr, funct, param)`**
`int mlx_expose_hook(void *win_ptr, int (*funct)(), void *param)`
Callback quand la fenêtre doit être **redessinée** (exposée).

**`mlx_hook(win_ptr, x_event, x_mask, funct, param)`**
`int mlx_hook(void *win_ptr, int x_event, int x_mask, int (*funct)(), void *param)`
Hook **générique** bas niveau pour n'importe quel événement X (appui/relâchement de touche, souris, fermeture de fenêtre…). Plus flexible que les hooks dédiés — indispensable pour gérer la croix de fermeture et le relâchement de touche.

### Codes d'événements X courants (pour `mlx_hook`)

| Événement | Code | Usage typique |
|---|---|---|
| KeyPress | 2 | appui touche |
| KeyRelease | 3 | relâchement touche |
| ButtonPress | 4 | clic souris enfoncé |
| ButtonRelease | 5 | clic souris relâché |
| MotionNotify | 6 | mouvement souris |
| DestroyNotify | 17 | fermeture de la fenêtre (croix) |

---

## Souris

**`mlx_mouse_get_pos(mlx_ptr, win_ptr, ...)`** → `(x, y)` *(à vérifier)*
`int mlx_mouse_get_pos(void *mlx_ptr, void *win_ptr, int *x, int *y)`
Retourne la position courante du curseur (tuple en Python). Selon la version, le 1er argument peut être seulement `win_ptr`.

**`mlx_mouse_move(mlx_ptr, win_ptr, x, y)`** *(à vérifier)*
`int mlx_mouse_move(void *mlx_ptr, void *win_ptr, int x, int y)`
Déplace le curseur à la position donnée.

**`mlx_mouse_hide(mlx_ptr, win_ptr)`** *(à vérifier)*
`int mlx_mouse_hide(void *mlx_ptr, void *win_ptr)`
Cache le curseur.

**`mlx_mouse_show(mlx_ptr, win_ptr)`** *(à vérifier)*
`int mlx_mouse_show(void *mlx_ptr, void *win_ptr)`
Affiche le curseur.

---

## Clavier (répétition automatique)

**`mlx_do_key_autorepeatoff(mlx_ptr)`**
`int mlx_do_key_autorepeatoff(void *mlx_ptr)`
Désactive la répétition automatique des touches maintenues. **Recommandé en jeu** pour un contrôle net (sinon une touche maintenue génère des rafales d'événements).

**`mlx_do_key_autorepeaton(mlx_ptr)`**
`int mlx_do_key_autorepeaton(void *mlx_ptr)`
Réactive la répétition automatique.

---

## Écran & synchronisation (spécifique vulkan / mlx_CLXV)

**`mlx_get_screen_size(mlx_ptr, ...)`** → `(x, y)`
`int mlx_get_screen_size(void *mlx_ptr, int *x, int *y)`
Retourne la taille de l'écran (tuple en Python).

**`mlx_do_sync(mlx_ptr)`** *(spécifique vulkan)*
`int mlx_do_sync(void *mlx_ptr)`
Force une synchronisation/flush du rendu. Utile si un dessin n'apparaît pas immédiatement sur cette version.

**`mlx_sync(mode, ptr)`** *(à vérifier)*
`int mlx_sync(int mode, void *ptr)`
Synchronise selon un mode donné (voir constantes ci-dessous) sur une image ou une fenêtre. Signature exacte à confirmer dans `mlx.h`.

### Constantes de synchronisation

| Constante | Rôle (à confirmer dans le man) |
|---|---|
| `Mlx.SYNC_IMAGE_WRITABLE` | attendre qu'une image soit de nouveau modifiable en sécurité avant d'y réécrire |
| `Mlx.SYNC_WIN_COMPLETED` | attendre que le rendu de la fenêtre soit terminé |
| `Mlx.SYNC_WIN_FLUSH` | forcer l'envoi (flush) des dessins en attente vers la fenêtre |

---

## Flux typique d'un programme

```python
from mlx import Mlx

m = Mlx()
ptr = m.mlx_init()                              # 1. instance
win = m.mlx_new_window(ptr, 800, 600, "Jeu")    # 2. fenêtre
img = m.mlx_new_image(ptr, 800, 600)            # 3. image (buffer)
# ... écrire les pixels dans l'image via mlx_get_data_addr ...
m.mlx_put_image_to_window(ptr, win, img, 0, 0)  # 4. afficher
m.mlx_key_hook(win, on_key, 0)                  # 5. entrées
m.mlx_loop_hook(ptr, update, 0)                 # 6. update/rendu par frame
m.mlx_loop(ptr)                                 # 7. boucle (bloquante)
m.mlx_release(ptr)                              # 8. nettoyage
```
