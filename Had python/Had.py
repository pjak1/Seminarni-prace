import pyglet
import random
from pathlib import Path
from win32api import GetSystemMetrics
VELIKOST_CTVERCE = 64
# Načtení obrázků
cesta_casti = Path("casti_hada")
casti_hada = {}
for cesta in cesta_casti.glob("*.png"):
    casti_hada[cesta.stem] = pyglet.image.load(cesta)


class Stav:
    def __init__(self):
        self.vyska = 15
        self.sirka = 15
        self.had_zije = True


stav = Stav()
window = pyglet.window.Window(GetSystemMetrics(0), GetSystemMetrics(1), fullscreen=True)
stav.sirka = window.width // VELIKOST_CTVERCE
stav.vyska = window.height // VELIKOST_CTVERCE


class Had:
    def __init__(self):
        self.had = [(6, 7), (7, 7)]
        self.smer_pohybu = 1, 0
        self.odkud = ""
        self.kam = ""
        self.smery_ve_fronte = []
        self.cast_hada = 0

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
        # Pohyb - nová pozice = stará pozice + nový směr zadaný hráčem
        stara_x, stara_y = self.had[-1]
        smer_x, smer_y = self.smer_pohybu
        nova_x = stara_x + smer_x
        nova_y = stara_y + smer_y
        # Kontrola vylezení z hrací plochy
        if nova_x < 0 or nova_x >= stav.sirka:
            stav.had_zije = False
        if nova_y > stav.vyska or nova_y < 0:
            stav.had_zije = False
        # Když had narazí sam do sebe
        nova_hlava = nova_x, nova_y
        if nova_hlava in self.had:
            stav.had_zije = False

        # Jezení jídla
        self.had.append(nova_hlava)
        if nova_hlava in jabko.pozice_jidla:
            jabko.pozice_jidla.remove(nova_hlava)
            jabko.Pridat_jidlo()
        elif nova_hlava in pomeranc.pozice_jidla:
            pomeranc.pozice_jidla.remove(nova_hlava)
            pomeranc.Pridat_jidlo()
        else:
            del self.had[0]

    def Smery(self):
        delkaHada = len(self.had)
        delkaHada -= 1
        # Určuje směr předchozí části
        if self.had[self.cast_hada - 1][0] < self.had[self.cast_hada][0]:
            self.odkud = "left"
        if self.had[self.cast_hada - 1][0] > self.had[self.cast_hada][0]:
            self.odkud = "right"
        if self.had[self.cast_hada - 1][1] < self.had[self.cast_hada][1]:
            self.odkud = "bottom"
        if self.had[self.cast_hada - 1][1] > self.had[self.cast_hada][1]:
            self.odkud = "top"
        if self.cast_hada == 0 or (self.cast_hada - 1) < 0:
            self.odkud = "end"
        # Určuje kam má směřovat část hada
        if self.cast_hada == delkaHada or (self.cast_hada + 1) > delkaHada:
            self.kam = "tongue"
            self.cast_hada = 0
            return
        if self.had[self.cast_hada][0] < self.had[self.cast_hada + 1][0]:
            self.kam = "right"
        if self.had[self.cast_hada][0] > self.had[self.cast_hada + 1][0]:
            self.kam = "left"
        if self.had[self.cast_hada][1] < self.had[self.cast_hada + 1][1]:
            self.kam = "top"
        if self.had[self.cast_hada][1] > self.had[self.cast_hada + 1][1]:
            self.kam = "bottom"
        self.cast_hada += 1


had = Had()


class Jidlo:
    def __init__(self):
        self.pozice_jidla = []

    def Pridat_jidlo(self):
        for pridej_jidlo in range(50):
            x = random.randrange(stav.sirka)
            y = random.randrange(stav.vyska)
            pozice = x, y
            if (pozice not in self.pozice_jidla) and (pozice not in had.had) and (pozice not in jidlo.pozice_jidla):
                self.pozice_jidla.append(pozice)
                jidlo.pozice_jidla.append(pozice)
                return


jidlo = Jidlo()


class Jabko(Jidlo):
    def __init__(self):
        super().__init__()
        self.pozice_jidla = []
        self.Pridat_jidlo()


jabko = Jabko()


class Pomeranc(Jidlo):
    def __init__(self):
        super().__init__()
        self.pozice_jidla = []
        self.Pridat_jidlo()


pomeranc = Pomeranc()


# Vykreslování
@window.event
def on_draw():
    window.clear()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    for x, y in had.had:
        had.Smery()
        odkud = had.odkud
        kam = had.kam
        if not stav.had_zije:
            kam = "dead"
            odkud = "end"
        casti_hada[odkud + "-" + kam].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
    for x, y in jabko.pozice_jidla:
        casti_hada["apple"].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
    for x, y in pomeranc.pozice_jidla:
        casti_hada["orange"].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)


# Ovládání pohybu
@window.event
def on_key_press(kod_znaku, pomocna_klavesa):  # povinné 2 parametry
    if kod_znaku == pyglet.window.key.LEFT:
        novy_smer = -1, 0
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.RIGHT:
        novy_smer = 1, 0
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.UP:
        novy_smer = 0, 1
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.DOWN:
        novy_smer = 0, -1
        had.smery_ve_fronte.append(novy_smer)


def Pohyb(prodleva):
    had.Pohyb()


pyglet.clock.schedule_interval(Pohyb, 1 / 6)

pyglet.app.run()
