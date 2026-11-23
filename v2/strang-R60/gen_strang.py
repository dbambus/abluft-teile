"""Strang R60: 90°-Bogen R60 -> Rohr -> Rohr -> Y-Stück R60, als SolidCraft-Assembly.

Bogen und Y-Stück stehen mit ihren Flanschen auf der Maschine, die beiden Lüftungsöffnungen
(Flanschmitten) liegen 'abstand' auseinander (Standard 590 mm). Dazwischen zwei gleiche Rohre
Ø75 mit 40 mm tiefer Muffe (statt 30), damit der Abstand an drei Steckstellen ausgeglichen werden kann:

  Steckstelle  Spitzende -> Muffe       Einstecktiefe min / max
  e1           Bogen     -> Rohr 1      15 / 33   (Bogen-Spitzende ist 35 lang)
  e2           Rohr 1    -> Rohr 2      15 / 40
  e3           Rohr 2    -> Y-Stück     15 / 30   (Y-Muffe ist 30 tief)

  15 mm Mindesteinstecktiefe: Dichtring sitzt 4…9,2 mm hinter der Muffenöffnung, + 1 mm Fase
  am Spitzende + ~5 mm Überdeckung.

  Summe e1+e2+e3 = 2*rohr_l + bogen_spitz + y_muffe - abstand = 665 - abstand (bei rohr_l 250)
  -> abstand von 665-103 = 562 bis 665-45 = 620 mm möglich; 575 / 590 / 605 -> je 30 / 25 / 20 mm.

Erzeugt Strang_R60.json und baut daraus Strang_R60.sc (Bauteile verlinkt, relativ) und Strang_R60.stl.
  python3 gen_strang.py                 # abstand 590
  python3 gen_strang.py --abstand 575
"""
import argparse, json, os, subprocess, sys

CLI = "/Applications/SolidCraft.app/Contents/MacOS/solidcraft-cli"
HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--abstand", type=float, default=590, help="Abstand der Lüftungsöffnungen, mm (Standard 590)")
ap.add_argument("--rohr-l", type=float, default=250, help="Rohrlänge, mm (Standard 250)")
a = ap.parse_args()

cmds = []


def add(cmd, **p):
    cmds.append({"command": cmd, "params": p})


def par(name, expr):
    add("parameters.add", name=name, expression=expr, unit="mm")


# Achse der waagerechten Leitung: Y = 0, Z = H; Bogen-Flanschmitte bei X = 0, Y-Flanschmitte bei X = abstand.
par("abstand", f"{a.abstand} mm")
par("H", "70 mm")              # t + riser + R bei R60
par("rohr_l", f"{a.rohr_l} mm")
par("bogen_spitz", "95 mm")    # Spitze des Bogen-Spitzendes: R + einsteck + 5
par("y_muffe", "70 mm")        # Muffenöffnung des Y-Stücks links der Flanschmitte: links + einsteck
par("ring_s0", "4.1 mm")       # Dichtring ab Muffenöffnung: nut_a + nut_spiel / 2
par("e_mittel", "(2 * rohr_l + bogen_spitz + y_muffe - abstand) / 3")
par("e1", "e_mittel")
par("e2", "e_mittel")
par("x_r1", "bogen_spitz - e1")
par("x_r2", "x_r1 + rohr_l - e2")
par("e3", "x_r2 + rohr_l - (abstand - y_muffe)")


def liegend(x):
    """Bauteil-Z (Rohrachse) auf Welt-X legen, Ursprung nach (x, 0, H)."""
    return [0, 0, 1, x, 0, 1, 0, 0, -1, 0, 0, "H"]


add("component.insert_design", path="../bogen/Bogen_75_R60.sc", name="Bogen_R60")
add("component.insert_design", path="../y-stueck/Y_Stueck_R60.sc", name="Y_R60",
    matrix=[1, 0, 0, "abstand", 0, 1, 0, 0, 0, 0, 1, 0])
add("component.insert_design", path="Rohr_250_D75_E40.sc", name="Rohr_1", matrix=liegend("x_r1"))
add("component.insert_design", path="Rohr_250_D75_E40.sc", name="Rohr_2", matrix=liegend("x_r2"), reuse=True)
ring = "../dichtring/Dichtring_D75_TPU.sc"
add("component.insert_design", path=ring, name="Dichtring", matrix=liegend("x_r1 + ring_s0"))
add("component.insert_design", path=ring, matrix=liegend("x_r2 + ring_s0"), reuse=True)
add("component.insert_design", path=ring, matrix=liegend("abstand - y_muffe + ring_s0"), reuse=True)

pfad = os.path.join(HERE, "Strang_R60.json")
json.dump({"commands": cmds}, open(pfad, "w"), indent=1)
r = subprocess.run([CLI, "run", pfad, "--script-relative", "--save", os.path.join(HERE, "Strang_R60.sc"),
                    "--out", os.path.join(HERE, "Strang_R60.stl"), "--quiet"], capture_output=True, text=True)
print("Strang_R60:", "ok" if r.returncode == 0 else "FEHLER " + (r.stderr or r.stdout).strip()[-600:])
sys.exit(r.returncode)
