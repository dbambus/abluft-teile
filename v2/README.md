# Abluft-Teile v2: Steckmuffe mit TPU-Dichtring

Alles im FDM-Druck. Statt Gewinde haben die Teile eine Steckmuffe mit Nut, in die ein
gedruckter TPU-Dichtring (5 mm hoch) kommt. Die Wände sind für eine 0,6-mm-Düse mit 3 Wandlinien
ausgelegt (3 × 0,62 = 1,86 mm).

| Ordner | Teil | Muffe | Spitzende |
|---|---|---|---|
| `bogen/` | 90°-Bogen R60 / R85 / R110, Tischflansch Ø104 (4×M4 auf 88,9) | – | Ø75 |
| `rohr/` | Rohr 250 mm Ø75 und Ø100 (Muffe unten, zum Drucken aufs Bett) | Ø75 / Ø100 | Ø75 / Ø100 |
| `y-stueck/` | Y-Abzweig R60 / R85 / R110, 45°-Einmündung, Konus Ø75 → Ø100 | Ø75 (links) | Ø100 (rechts) |
| `dichtring/` | Dichtring Ø75 und Ø100, **TPU** | | |
| `strang-R60/` | Assembly Bogen R60 → 2 × Rohr Ø75 (Muffe 40 tief) → Y-Stück R60, Öffnungen 590 mm auseinander | Ø75 | Ø75 |

Jedes Teil liegt als `.sc` (SolidCraft, parametrisch) und `.stl` vor, die Bauskripte in `skripte/`.

## Strang R60 (Bogen → Rohr → Rohr → Y)

`strang-R60/Strang_R60.sc` setzt Bogen R60 und Y-Stück R60 (beide schon gedruckt, verlinkt aus `bogen/` und
`y-stueck/`) mit 590 mm zwischen den Flanschmitten auf die Maschine, dazwischen zwei gleiche Rohre
`Rohr_250_D75_E40` (250 mm, **Muffe 40 statt 30 mm tief**) und die drei Dichtringe.

Der Abstand wird an den drei Steckstellen ausgeglichen (Einstecktiefe mindestens 15 mm, damit das Spitzende
den Dichtring sicher überdeckt):

| Steckstelle | max. Einstecktiefe | bei 575 / 590 / 605 mm |
|---|---|---|
| Bogen → Rohr 1 | 33 (Bogen-Spitzende 35 lang) | 30 / 25 / 20 |
| Rohr 1 → Rohr 2 | 40 | 30 / 25 / 20 |
| Rohr 2 → Y-Stück | 30 (Y-Muffe) | 30 / 25 / 20 |

Summe der Einstecktiefen = 665 mm − Abstand, also gehen **562 bis 620 mm**. In SolidCraft den Parameter
`abstand` ändern (die Rohre und Ringe folgen, `e3` zeigt die Tiefe im Y-Stück), oder neu bauen:
`python3 strang-R60/gen_strang.py --abstand 575`.

## Toleranzen

Neu erzeugen mit eigenen Werten (dauert für alle Teile gut 15 min, Rohre und Ringe wenige Sekunden):

```sh
python3 gen_v2.py --spiel 0.15 --verpressung 0.4 --nut-spiel 0.2
python3 gen_v2.py --nur rohr_75 dichtring_75 --spiel 0.2   # nur einzelne Teile
python3 gen_v2.py --help                                   # alle Optionen
```

| Option | Standard | Bedeutung |
|---|---|---|
| `--spiel` | 0,15 | radiales Spiel zwischen Spitzende und Muffenbohrung |
| `--verpressung` | 0,4 | wie weit der Dichtring radial zusammengedrückt wird |
| `--nut-spiel` | 0,2 | axiales Spiel des Rings in der Nut |
| `--ring-h` / `--ring-s` | 5 / 2,5 | Höhe und radiale Dicke des Dichtrings |
| `--linienbreite` / `--wandlinien` | 0,62 / 3 | Wanddicke = Linienbreite × Wandlinien |
| `--einsteck` | 30 | Einstecktiefe der Muffe |
| `--rohr-l` | 250 | Rohrlänge |

Dieselben Werte stehen als Parameter in jeder `.sc`-Datei und lassen sich auch in SolidCraft ändern.

Maße mit den Standardwerten:

| | Ø75 | Ø100 |
|---|---|---|
| Muffenbohrung | 75,30 | 100,30 |
| Nutgrund | 79,20 | 104,20 |
| Muffe außen | 82,92 | 107,92 |
| Rohr innen | 71,28 | 96,28 |
| Dichtring innen / außen × Höhe | 74,20 / 79,20 × 5 | 99,20 / 104,20 × 5 |

## Druckhinweise

- Rohre stehend drucken, Muffe unten. Die Oberseite der Nut ist ein 2,5 mm breiter Überhang innen; mit 0,6er-Düse ohne Stütze machbar.
- Bögen und Y-Stücke auf dem Flansch drucken; die waagerechte Leitung braucht Stützen wie in v1.
- Den Dichtring vor dem Zusammenstecken in die Nut drücken, das Spitzende leicht mit Silikonfett einstreichen.
