"""Erzeugt SolidCraft-Skripte für das Y-Stück (R60 / R85 / R110).

Koordinaten: Wandflansch auf XY bei Z=0, Rohrachse der waagerechten Leitung
liegt bei Z = H = t + riser + R (wie bei den 90°-Adaptern), Strömung in +X.
"""
import json, math, sys

out_dir = sys.argv[1]
c45 = math.cos(math.radians(45))


def script(R):
    t, riser, rohr_d, bohrung = 4, 6, 75, 69
    muffe_l, muffe_d, muffe_kern = 25, 81, 73
    links, mix, konus_l, aus_l = 40, -35, 100, 30
    H = t + riser + R
    L45 = R * (1 - c45) / c45
    xj = R * (1 - c45) + L45 * c45
    xL = -links - muffe_l
    xc = xj + mix

    cmds = []
    def add(cmd, **p):
        cmds.append({"command": cmd, "params": p})
    def par(name, expr):
        add("parameters.add", name=name, expression=expr, unit="mm")

    par("t", "4 mm"); par("riser", "6 mm"); par("R", f"{R} mm")
    par("flansch", "104 mm"); par("lochkreis", "88.9 mm")
    par("rohr_d", "75 mm"); par("bohrung", "69 mm")
    par("einlauf", "(76.2 mm - bohrung) / 2")
    par("H", "t + riser + R")
    par("L45", "R * (1 - sin(45 deg)) / cos(45 deg)")
    par("xj", "R * (1 - cos(45 deg)) + L45 * sin(45 deg)")
    par("mix", f"{mix} mm"); par("xc", "xj + mix")
    par("links", f"{links} mm")
    par("muffe_l", f"{muffe_l} mm"); par("muffe_d", f"{muffe_d} mm"); par("muffe_kern", f"{muffe_kern} mm")
    par("xL", "-links - muffe_l")
    par("konus_l", f"{konus_l} mm"); par("aus_d", "100 mm"); par("aus_wand", "3 mm"); par("aus_l", f"{aus_l} mm")
    par("aus_innen", "aus_d - 2 * aus_wand")
    par("haupt_d", "rohr_d + 1 mm"); par("haupt_bohrung", "bohrung + 1 mm")

    X = [1, 0, 0]

    # --- Muffe als eigener Ring mit Innengewinde M75x2, zuerst gebaut und eigener Körper wie der GewindeStutzen der Adapter; ragt 1 mm in Y hinein ---
    add("solid.cylinder", name="MuffeRing", body_name="Muffe", diameter="muffe_d", height="muffe_l + 1",
        base=["xL", 0, "H"], axis=X, operation="new")
    add("solid.cylinder", name="MuffeRingBohrung", diameter="muffe_kern", height="muffe_l + 3",
        base=["xL - 1", 0, "H"], axis=X, operation="cut", targets=["Muffe"])
    add("solid.thread", name="MuffeGewinde", face=[xL + muffe_l / 2, -muffe_kern / 2, H],
        designation="M75x2", modeled=True)

    # --- Außenkontur ---
    add("solid.cylinder", name="Flansch", body_name="Y", diameter="flansch", height="t",
        base=[0, 0, 0], operation="new")
    # Wandzulauf: gerade hoch, 45°-Bogen R, gerade bis zur Rohrachse – ein Sweep ohne Nahtstellen
    add("sketch.create", plane={"origin": [0, 0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="ZulaufPfadSk")
    add("sketch.line", points=[[0, "t - 1"], [0, "t + riser"]])
    add("sketch.arc.center_point", center=["R", "t + riser"], start=[0, "t + riser"], sweep=-45)
    add("sketch.line", points=["a1.end", ["xj", "H"]])
    add("sketch.finish")
    add("sketch.create", plane="XY", offset="t - 1", name="ZulaufProfilSk")
    add("sketch.circle.center", center=[0, 0], diameter="rohr_d")
    add("sketch.finish")
    add("solid.sweep", name="Zulauf", sketch="ZulaufProfilSk", path_sketch="ZulaufPfadSk", path=["l1", "a1", "l2"],
        operation="join", targets=["Y"])

    # Hauptleitung als ein Drehprofil (Schulter hinter der Muffe, Rohr, Konus, Auslass), dreht um die Rohrachse
    add("sketch.create", plane={"origin": [0, 0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="HauptSk")
    add("sketch.line", points=[["xL - 5", "H"], ["xc + konus_l + aus_l + 5", "H"]], construction=True)
    add("sketch.line", closed=True, points=[
        ["xL + muffe_l", "H"], ["xL + muffe_l", "H + muffe_d / 2"],
        ["xL + muffe_l + (muffe_d - haupt_d) / 2", "H + haupt_d / 2"],
        ["xc", "H + haupt_d / 2"], ["xc + konus_l", "H + aus_d / 2"],
        ["xc + konus_l + aus_l", "H + aus_d / 2"], ["xc + konus_l + aus_l", "H"]])
    add("sketch.finish")
    add("solid.revolve", name="Hauptleitung", sketch="HauptSk", axis="l1", angle="360 deg",
        operation="join", targets=["Y"])

    # --- Innenkontur ---
    # Wandzulauf: gerade hoch, 45°-Bogen R, gerade bis zur Rohrachse – ein Sweep ohne Nahtstellen
    add("sketch.create", plane={"origin": [0, 0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="ZulaufBohrungPfadSk")
    add("sketch.line", points=[[0, "-1"], [0, "t + riser"]])
    add("sketch.arc.center_point", center=["R", "t + riser"], start=[0, "t + riser"], sweep=-45)
    add("sketch.line", points=["a1.end", ["xj", "H"]])
    add("sketch.finish")
    add("sketch.create", plane="XY", offset="-1", name="ZulaufBohrungProfilSk")
    add("sketch.circle.center", center=[0, 0], diameter="bohrung")
    add("sketch.finish")
    add("solid.sweep", name="ZulaufBohrung", sketch="ZulaufBohrungProfilSk", path_sketch="ZulaufBohrungPfadSk", path=["l1", "a1", "l2"],
        operation="cut", targets=["Y"])
    add("sketch.create", plane={"origin": [0, 0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="HauptBohrSk")
    add("sketch.line", points=[["xL - 5", "H"], ["xc + konus_l + aus_l + 5", "H"]], construction=True)
    add("sketch.line", closed=True, points=[
        ["xL + muffe_l - 1", "H"], ["xL + muffe_l - 1", "H + haupt_bohrung / 2"],
        ["xc", "H + haupt_bohrung / 2"], ["xc + konus_l", "H + aus_innen / 2"],
        ["xc + konus_l + aus_l + 1", "H + aus_innen / 2"], ["xc + konus_l + aus_l + 1", "H"]])
    add("sketch.finish")
    add("solid.revolve", name="HauptBohrung", sketch="HauptBohrSk", axis="l1", angle="360 deg",
        operation="cut", targets=["Y"])

    # --- Flansch-Details wie am 90°-Adapter ---
    add("solid.cylinder", name="Schraubloch", diameter="4.5 mm", height="t + 2",
        base=["lochkreis / 2", 0, -1], operation="cut", targets=["Y"])
    add("solid.pattern.circular", name="Schraubloecher", features=["Schraubloch"], axis="Z", count=4)
    add("solid.chamfer", name="FlanschFase", edges=[[0, -52, t]], distance="1 mm")
    add("solid.chamfer", name="RiserFase", edges=[[0, -rohr_d / 2, t]], distance="2 mm")
    add("solid.chamfer", name="EinlaufFase", edges=[[0, -bohrung / 2, 0]], distance="einlauf")

    info = dict(R=R, H=H, xj=round(xj, 1), xc=round(xc, 1), x_from=xL,
                x_to=round(xc + konus_l + aus_l, 1))
    return {"commands": cmds}, info


for R in (60, 85, 110):
    s, info = script(R)
    json.dump(s, open(f"{out_dir}/y_R{R}.json", "w"), indent=1)
    print(info)
