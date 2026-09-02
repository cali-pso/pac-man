"""Test decisif du workflow image. Lancer :  uv run python3 diag_img.py
Regarde la fenetre (carre VERT ?), appuie ESC, puis colle toute la sortie.
"""
import struct
from mlx import Mlx

m = Mlx()
p = m.mlx_init()
w = m.mlx_new_window(p, 400, 400, "img test")

img = m.mlx_new_image(p, 200, 200)
data, bpp, size_line, endian = m.mlx_get_data_addr(img)
print("bpp:", bpp, "| size_line:", size_line, "| endian:", endian)
print("data type:", type(data).__name__)

try:
    mvb = data.cast("B")
    print("cast('B') OK | len:", len(mvb),
          "| attendu:", size_line * 200,
          "| readonly:", mvb.readonly)
except Exception as e:
    print("cast FAIL:", e)
    mvb = data

# Remplit toute l'image en vert
fmt = "<I" if endian == 0 else ">I"
green = struct.pack(fmt, 0x00FF00)
try:
    mvb[:] = green * (len(mvb) // 4)
    print("remplissage OK")
except Exception as e:
    print("remplissage FAIL:", e)

# Essaie un sync d'image (au cas ou le buffer doit etre valide)
for name in ("SYNC_IMAGE_WRITABLE",):
    val = getattr(m, name, None)
    if val is not None:
        try:
            m.mlx_sync(val, img)
            print(f"mlx_sync({name}, img) OK")
        except Exception as e:
            print(f"mlx_sync({name}, img) FAIL:", e)

m.mlx_put_image_to_window(p, w, img, 100, 100)
try:
    m.mlx_do_sync(p)
    print("mlx_do_sync(p) OK")
except Exception as e:
    print("mlx_do_sync FAIL:", e)

# IMPORTANT : on ne detruit PAS l'image
m.mlx_string_put(p, w, 20, 20, 0xFFFFFF, "Carre VERT visible ?")

def key(kc, *a):
    if kc == 65307:
        m.mlx_loop_exit(p)
    return 0

m.mlx_key_hook(w, key, 0)
m.mlx_loop(p)
