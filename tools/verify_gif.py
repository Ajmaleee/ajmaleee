from PIL import Image
import numpy as np, importlib.util
spec=importlib.util.spec_from_file_location("mp","tools/matrix_portrait.py")
mp=importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
font=mp.load_font(); portrait=mp.load_portrait(); cells=mp.build_cells(portrait,font); background=mp.build_background()
import random
rng=random.Random(1337); sm={}
for col in range(mp.COLS):
    sm[col]=[(rng.randrange(mp.N_FRAMES), rng.choice((1,2,2,3)), rng.randint(9,17)) for _ in range(1 if rng.random()<0.55 else 2)]
g=Image.open("assets/matrix-portrait.gif")
for idx in (0,1,20,55):
    ref=np.asarray(mp.draw_frame(idx,cells,sm,font,background)).astype(np.int16)
    g.seek(idx); got=np.asarray(g.convert("RGB")).astype(np.int16)
    d=np.abs(ref-got)
    print(idx,"maxdiff",int(d.max()),"mean",round(float(d.mean()),4),"pct>8",round(float((d.max(axis=2)>8).mean()*100),3))
