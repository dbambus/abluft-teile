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

Jedes Teil liegt als `.sc` (SolidCraft, parametrisch) und `.stl` vor, die Bauskripte in `skripte/`.

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
