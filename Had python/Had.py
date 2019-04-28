import pyglet
import random
from pathlib import Path
VELIKOST_CTVERCE = 64
# Načtení obrázků
cesta_casti = Path("casti_hada")
casti_hada = {}
for cesta in cesta_casti.glob("*.png"):
    casti_hada[cesta.stem] = pyglet.image.load(cesta)

n = 0  # číslování částí pro Smery


class Stav:
    def __init__(self):
        self.vyska = 15
        self.sirka = 15
        self.had_zije = True


stav = Stav()


class Had:
    def __init__(self):
        self.had = [(6, 7), (7, 7)]
        self.smer_pohybu = 1, 0
        self.krmeni = []
        self.odkud = ""
        self.kam = ""
        self.smery_ve_fronte = []
        self.Pridat_jidlo()
        self.Pridat_jidlo()

    def Pridat_jidlo(self):
        for pridej_jidlo in range(50):
            x = random.randrange(stav.sirka)
            y = random.randrange(stav.vyska)
            pozice = x, y
            if (pozice not in self.krmeni) and (pozice not in self.had):
                self.krmeni.append(pozice)
                return

    def Pohyb(self):
        if self.smery_ve_fronte:
            # Fronta směru pohybu po rychlém stisknutí kláves
            novy_smer = self.smery_ve_fronte[0]
            del self.smery_ve_fronte[0]
            stary_smer_x, stary_smer_y = self.smer_pohybu
            novy_smer_x, novy_smer_y = novy_smer
            if(stary_smer_x, stary_smer_y) != (-novy_smer_x, -novy_smer_y):
                self.smer_pohybu = novy_smer
        if not stav.had_zije:
            return
            # Pohyb
        stara_x, stara_y = self.had[-1]
        smer_x, smer_y = self.smer_pohybu
        nova_x = stara_x + smer_x
        nova_y = stara_y + smer_y
        # Kontrola vylezení z hrací plochy
        if nova_x < 0 or nova_x > stav.sirka:
            stav.had_zije = False
        if nova_y > stav.vyska or nova_y < 0:
            stav.had_zije = False
        # Když had narazí sam do sebe
        nova_hlava = nova_x, nova_y
        if nova_hlava in self.had:
            stav.had_zije = False

        # Jezení jídla
        self.had.append(nova_hlava)
        if nova_hlava in self.krmeni:
            self.krmeni.remove(nova_hlava)
            self.Pridat_jidlo()
        else:
            del self.had[0]


window = pyglet.window.Window(1500, 950)
h = Had()
stav.sirka = window.width // VELIKOST_CTVERCE
stav.vyska = window.height // VELIKOST_CTVERCE


# Vykreslování
@window.event
def on_draw():
    window.clear()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    for x, y in h.had:
        odkud = "end"
        kam = "end"
        if kam == "end" and not stav.had_zije:
            kam = "dead"
        casti_hada[odkud + "-" + kam].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
    for x, y in h.krmeni:
        casti_hada["jidlo"].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)

# Ovládání pohybu


@window.event
def on_key_press(kod_znaku, pomocna_klavesa):  # povinné 2 parametry
    if kod_znaku == pyglet.window.key.LEFT:
        novy_smer = -1, 0
    if kod_znaku == pyglet.window.key.RIGHT:
        novy_smer = 1, 0
    if kod_znaku == pyglet.window.key.UP:
        novy_smer = 0, 1
    if kod_znaku == pyglet.window.key.DOWN:
        novy_smer = 0, -1
    h.smery_ve_fronte.append(novy_smer)


def Pohyb(prodleva):
    h.Pohyb()


pyglet.clock.schedule_interval(Pohyb, 1 / 6)

pyglet.app.run()
