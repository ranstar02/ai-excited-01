# Moonward

A tiny fox with a flowing red scarf rides a gigantic luminous koi out of a dark teal ocean toward a golden moon. Crisp vector-style shapes, suspended droplets, and an indigo star field capture the leap.

Run with Python 3.13 (standard library only):

```sh
python3 main.py
```

The deterministic 1024×1024 RGB PNG is written to `/output/entry.png`. To choose another directory:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

All drawing primitives, supersampling, and PNG encoding are implemented in `main.py`.
