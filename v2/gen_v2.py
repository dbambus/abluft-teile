"""Abluft-Teile v2: Steckmuffe mit TPU-Dichtring statt Gewinde.

Erzeugt SolidCraft-Skripte und baut daraus mit solidcraft-cli .sc + .stl:
  bogen/      90°-Bogen Tischflansch -> Ø75-Spitzende (R60 / R85 / R110)
  rohr/       Rohr Ø75 und Ø100, Muffe unten, Spitzende oben
  y-stueck/   Y-Abzweig: Muffe Ø75 links, Wandzulauf 45°, Konus auf Ø100-Spitzende (R60 / R85 / R110)
  dichtring/  Dichtring Ø75 und Ø100 (TPU)

Toleranzen kommen als Optionen und landen als Parameter im Modell, sodass sie
auch in SolidCraft noch geändert werden können:
  python3 gen_v2.py --spiel 0.15 --verpressung 0.4 --nut-spiel 0.2

Muffe (von der Öffnung aus): 1 mm Einführfase, 'nut_a' Steg, Nut für den Dichtring
(Breite ring_h + nut_spiel), Bohrung bis 'einsteck', dann 45°-Anschlag auf den
Rohr-Innendurchmesser. Der Dichtring sitzt satt im Nutgrund und steht um
spiel + verpressung in die Bohrung; das Spitzende drückt ihn um 'verpressung' zusammen.
"""
import argparse, json, math, os, subprocess, sys

CLI = "/Applications/SolidCraft.app/Contents/MacOS/solidcraft-cli"
HERE = os.path.dirname(os.path.abspath(__file__))
c45 = math.cos(math.radians(45))

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--spiel", type=float, default=0.15, help="radiales Spiel Spitzende/Muffenbohrung, mm (Standard 0.15)")
ap.add_argument("--verpressung", type=float, default=0.4, help="radiale Verpressung des Dichtrings, mm (Standard 0.4)")
ap.add_argument("--nut-spiel", type=float, default=0.2, help="axiales Spiel des Dichtrings in der Nut, mm (Standard 0.2)")
ap.add_argument("--ring-h", type=float, default=5, help="Höhe des Dichtrings, mm (Standard 5)")
ap.add_argument("--ring-s", type=float, default=2.5, help="radiale Dicke des Dichtrings, mm (Standard 2.5)")
ap.add_argument("--linienbreite", type=float, default=0.62, help="Linienbreite, mm (Standard 0.62 für 0.6-Düse)")
ap.add_argument("--wandlinien", type=int, default=3, help="Wandlinien (Standard 3)")
ap.add_argument("--einsteck", type=float, default=30, help="Einstecktiefe der Muffe, mm (Standard 30)")
ap.add_argument("--rohr-l", type=float, default=250, help="Gesamtlänge der Rohre, mm (Standard 250)")
ap.add_argument("--nur", nargs="*", help="nur diese Teile bauen, z.B. rohr_75 bogen_R60")
ap.add_argument("--nur-skripte", action="store_true", help="nur die JSON-Skripte schreiben, nicht bauen")
a = ap.parse_args()

wand = a.linienbreite * a.wandlinien


class Script:
    def __init__(self):
        self.cmds = []

    def add(self, cmd, **p):
        self.cmds.append({"command": cmd, "params": p})

    def par(self, name, expr, unit="mm"):
        self.add("parameters.add", name=name, expression=expr, unit=unit)

    def steck(self):
        """Gemeinsame Parameter der Steckverbindung."""
        self.par("linienbreite", f"{a.linienbreite} mm")
        self.par("wandlinien", f"{a.wandlinien}", unit="")
        self.par("wand", "linienbreite * wandlinien")
        self.par("spiel", f"{a.spiel} mm")
        self.par("verpressung", f"{a.verpressung} mm")
        self.par("nut_spiel", f"{a.nut_spiel} mm")
        self.par("ring_h", f"{a.ring_h} mm")
        self.par("ring_s", f"{a.ring_s} mm")
        self.par("einsteck", f"{a.einsteck} mm")
        self.par("nut_a", "4 mm")
        self.par("nut_b", "ring_h + nut_spiel")
        self.par("fase_m", "1 mm")
        self.par("fase_s", "1 mm")

    def muffe(self, d):
        """Parameter der Muffe für das Spitzende 'd' (Name eines Parameters)."""
        self.par("muffe_bohrung", f"{d} + 2 * spiel")
        self.par("nut_d", f"{d} - 2 * verpressung + 2 * ring_s")
        self.par("muffe_d", "nut_d + 2 * wand")

    def json(self):
        return {"commands": self.cmds}


def muffe_innen(s0, r_innen):
    """Innenkontur der Muffe als (s, r)-Ausdrücke, von der Öffnung (s0) bis zum Anschlag auf r_innen."""
    return [
        (f"{s0} - 1", "muffe_bohrung / 2 + fase_m + 1"),
        (f"{s0} + fase_m", "muffe_bohrung / 2"),
        (f"{s0} + nut_a", "muffe_bohrung / 2"),
        (f"{s0} + nut_a", "nut_d / 2"),
        (f"{s0} + nut_a + nut_b", "nut_d / 2"),
        (f"{s0} + nut_a + nut_b", "muffe_bohrung / 2"),
        (f"{s0} + einsteck", "muffe_bohrung / 2"),
        (f"{s0} + einsteck + muffe_bohrung / 2 - {r_innen}", r_innen),
    ]


# --- Rohr: Wandquerschnitt als ein Drehprofil um Z, Muffe unten (Druckbett), Spitzende oben ---
def rohr(D):
    s = Script()
    s.par("rohr_l", f"{a.rohr_l} mm")
    s.par("rohr_d", f"{D} mm")
    s.steck()
    s.par("bohrung", "rohr_d - 2 * wand")
    s.muffe("rohr_d")
    # Skizze: x = Welt-Z (Rohrachse), y = Welt-X (Radius)
    s.add("sketch.create", plane={"origin": [0, 0, 0], "x_dir": [0, 0, 1], "y_dir": [1, 0, 0]}, name="WandSk")
    s.add("sketch.line", points=[[-5, 0], ["rohr_l + 5", 0]], construction=True)
    innen = muffe_innen("0", "bohrung / 2")[1:]  # ohne Verlängerung vor der Öffnung
    pts = [
        ["0", "muffe_bohrung / 2 + fase_m"],
        ["0", "muffe_d / 2 - 0.5 mm"],          # kleine Fase gegen Elefantenfuß
        ["0.5 mm", "muffe_d / 2"],
        ["einsteck", "muffe_d / 2"],
        ["einsteck + muffe_d / 2 - rohr_d / 2", "rohr_d / 2"],
        ["rohr_l - fase_s", "rohr_d / 2"],
        ["rohr_l", "rohr_d / 2 - fase_s"],
        ["rohr_l", "bohrung / 2"],
    ] + [list(p) for p in reversed(innen)]
    s.add("sketch.line", closed=True, points=pts)
    s.add("sketch.finish")
    s.add("solid.revolve", name="Rohr", body_name="Rohr", sketch="WandSk", axis="l1", angle="360 deg", operation="new")
    return s


# --- Dichtring (TPU): satt im Nutgrund, innen um 'verpressung' kleiner als das Spitzende ---
def dichtring(D):
    s = Script()
    s.par("rohr_d", f"{D} mm")
    s.steck()
    s.muffe("rohr_d")
    s.add("solid.cylinder", name="Ring", body_name="Dichtring", diameter="nut_d", height="ring_h", operation="new")
    s.add("solid.cylinder", name="RingBohrung", diameter="rohr_d - 2 * verpressung", height="ring_h + 2",
          base=[0, 0, -1], operation="cut", targets=["Dichtring"])
    return s


def flansch_params(s, R):
    s.par("t", "4 mm"); s.par("riser", "6 mm"); s.par("R", f"{R} mm")
    s.par("flansch", "104 mm"); s.par("lochkreis", "88.9 mm")
    s.par("rohr_d", "75 mm")
    s.steck()
    s.par("bohrung", "rohr_d - 2 * wand")
    s.par("einlauf", "(76.2 mm - bohrung) / 2")
    s.par("H", "t + riser + R")


def flansch_details(s, body, bohrung):
    t = 4
    s.add("solid.cylinder", name="Schraubloch", diameter="4.5 mm", height="t + 2",
          base=["lochkreis / 2", 0, -1], operation="cut", targets=[body])
    s.add("solid.pattern.circular", name="Schraubloecher", features=["Schraubloch"], axis="Z", count=4)
    s.add("solid.chamfer", name="FlanschFase", edges=[[0, -52, t]], distance="1 mm")
    s.add("solid.chamfer", name="RiserFase", edges=[[0, -37.5, t]], distance="2 mm")
    s.add("solid.chamfer", name="EinlaufFase", edges=[[0, -bohrung / 2, 0]], distance="einlauf")


XZ = {"origin": [0, 0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}


def zulauf(s, sweep, ende, pfad_name, profil_name, feature, d, z0, op, targets):
    """Wandzulauf: gerade hoch, Bogen R um 'sweep' Grad, gerade bis 'ende' (x, z) – ein Sweep."""
    s.add("sketch.create", plane=XZ, name=pfad_name)
    s.add("sketch.line", points=[[0, z0], [0, "t + riser"]])
    s.add("sketch.arc.center_point", center=["R", "t + riser"], start=[0, "t + riser"], sweep=sweep)
    s.add("sketch.line", points=["a1.end", ende])
    s.add("sketch.finish")
    s.add("sketch.create", plane="XY", offset=z0, name=profil_name)
    s.add("sketch.circle.center", center=[0, 0], diameter=d)
    s.add("sketch.finish")
    s.add("solid.sweep", name=feature, sketch=profil_name, path_sketch=pfad_name, path=["l1", "a1", "l2"],
          operation=op, targets=targets)


# --- 90°-Bogen: Tischflansch, Bogen R, gerades Ø75-Spitzende ---
def bogen(R):
    s = Script()
    flansch_params(s, R)
    s.par("stutzen", "einsteck + 5 mm")
    s.add("solid.cylinder", name="Flansch", body_name="Bogen", diameter="flansch", height="t", operation="new")
    zulauf(s, -90, ["R + stutzen", "H"], "BogenPfadSk", "BogenProfilSk", "BogenRohr", "rohr_d", "t - 1", "join", ["Bogen"])
    zulauf(s, -90, ["R + stutzen + 1", "H"], "BogenBohrungPfadSk", "BogenBohrungProfilSk", "BogenBohrung", "bohrung", "-1", "cut", ["Bogen"])
    # Einführfase am Spitzende
    s.add("sketch.create", plane=XZ, name="SpitzFaseSk")
    s.add("sketch.line", points=[["R", "H"], ["R + stutzen + 5", "H"]], construction=True)
    s.add("sketch.line", closed=True, points=[
        ["R + stutzen - fase_s - 1", "H + rohr_d / 2 + 1"],
        ["R + stutzen + 1", "H + rohr_d / 2 - fase_s - 1"],
        ["R + stutzen + 1", "H + rohr_d / 2 + 1"]])
    s.add("sketch.finish")
    s.add("solid.revolve", name="SpitzFase", sketch="SpitzFaseSk", axis="l1", angle="360 deg",
          operation="cut", targets=["Bogen"])
    flansch_details(s, "Bogen", 75 - 2 * wand)
    return s


# --- Y-Stück: Muffe Ø75 links, Wandzulauf 45°, Konus ab der Einmündung, Ø100-Spitzende rechts ---
def y_stueck(R):
    s = Script()
    flansch_params(s, R)
    L45 = R * (1 - c45) / c45
    s.par("L45", "R * (1 - sin(45 deg)) / cos(45 deg)")
    s.par("xj", "R * (1 - cos(45 deg)) + L45 * sin(45 deg)")
    s.par("mix", "-35 mm"); s.par("xc", "xj + mix")
    s.par("links", "40 mm")
    s.par("xL", "-links - einsteck")
    s.par("konus_l", "100 mm"); s.par("aus_d", "100 mm"); s.par("aus_l", "einsteck + 5 mm")
    s.par("aus_innen", "aus_d - 2 * wand")
    s.par("xe", "xc + konus_l + aus_l")
    s.par("haupt_d", "rohr_d + 1 mm"); s.par("haupt_bohrung", "bohrung + 1 mm")
    s.muffe("rohr_d")

    s.add("solid.cylinder", name="Flansch", body_name="Y", diameter="flansch", height="t", operation="new")
    zulauf(s, -45, ["xj", "H"], "ZulaufPfadSk", "ZulaufProfilSk", "Zulauf", "rohr_d", "t - 1", "join", ["Y"])

    def yp(sx, r):  # (s, r) relativ zur Muffenöffnung -> Skizzenpunkt
        return [f"xL + ({sx})", f"H + ({r})"]

    # Hauptleitung außen: Muffe, 45°-Schulter, Rohr, Konus, Spitzende mit Fase
    s.add("sketch.create", plane=XZ, name="HauptSk")
    s.add("sketch.line", points=[["xL - 5", "H"], ["xe + 5", "H"]], construction=True)
    s.add("sketch.line", closed=True, points=[
        ["xL", "H"], ["xL", "H + muffe_d / 2"],
        yp("einsteck", "muffe_d / 2"),
        yp("einsteck + muffe_d / 2 - haupt_d / 2", "haupt_d / 2"),
        ["xc", "H + haupt_d / 2"], ["xc + konus_l", "H + aus_d / 2"],
        ["xe - fase_s", "H + aus_d / 2"], ["xe", "H + aus_d / 2 - fase_s"],
        ["xe", "H"]])
    s.add("sketch.finish")
    s.add("solid.revolve", name="Hauptleitung", sketch="HauptSk", axis="l1", angle="360 deg",
          operation="join", targets=["Y"])

    zulauf(s, -45, ["xj", "H"], "ZulaufBohrungPfadSk", "ZulaufBohrungProfilSk", "ZulaufBohrung", "bohrung", "-1", "cut", ["Y"])

    # Hauptleitung innen: Muffe mit Nut, Anschlag, Rohr, Konus, Spitzende
    s.add("sketch.create", plane=XZ, name="HauptBohrSk")
    s.add("sketch.line", points=[["xL - 5", "H"], ["xe + 5", "H"]], construction=True)
    innen = [yp(*p) for p in muffe_innen("0", "haupt_bohrung / 2")]
    s.add("sketch.line", closed=True, points=[["xL - 1", "H"]] + innen + [
        ["xc", "H + haupt_bohrung / 2"], ["xc + konus_l", "H + aus_innen / 2"],
        ["xe + 1", "H + aus_innen / 2"], ["xe + 1", "H"]])
    s.add("sketch.finish")
    s.add("solid.revolve", name="HauptBohrung", sketch="HauptBohrSk", axis="l1", angle="360 deg",
          operation="cut", targets=["Y"])

    flansch_details(s, "Y", 75 - 2 * wand)
    return s


TEILE = {
    "rohr_75": ("rohr", "Rohr_250_D75", lambda: rohr(75)),
    "rohr_100": ("rohr", "Rohr_250_D100", lambda: rohr(100)),
    "dichtring_75": ("dichtring", "Dichtring_D75_TPU", lambda: dichtring(75)),
    "dichtring_100": ("dichtring", "Dichtring_D100_TPU", lambda: dichtring(100)),
}
for R in (60, 85, 110):
    TEILE[f"bogen_R{R}"] = ("bogen", f"Bogen_75_R{R}", lambda R=R: bogen(R))
    TEILE[f"y_R{R}"] = ("y-stueck", f"Y_Stueck_R{R}", lambda R=R: y_stueck(R))

fehler = 0
for key, (ordner, name, bau) in TEILE.items():
    if a.nur and key not in a.nur:
        continue
    d = os.path.join(HERE, ordner)
    os.makedirs(os.path.join(d, "skripte"), exist_ok=True)
    pfad = os.path.join(d, "skripte", f"{name}.json")
    json.dump(bau().json(), open(pfad, "w"), indent=1)
    if a.nur_skripte:
        print(pfad)
        continue
    r = subprocess.run([CLI, "run", pfad, "--save", os.path.join(d, f"{name}.sc"),
                        "--out", os.path.join(d, f"{name}.stl"), "--quiet"], capture_output=True, text=True)
    print(f"{name}: {'ok' if r.returncode == 0 else 'FEHLER ' + (r.stderr or r.stdout).strip()[-300:]}")
    fehler += r.returncode != 0
sys.exit(1 if fehler else 0)
