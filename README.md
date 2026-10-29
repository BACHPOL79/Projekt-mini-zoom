# Projekt 4 – Algebra Boole'a na obiektach technicznych (Blender)

Osobny projekt laboratoryjny (nie jest częścią aplikacji *mini-zoom*, leży na osobnej gałęzi `blender-lab4`).

## Pliki do pobrania

| Plik | Co to jest |
|---|---|
| `output/projekt4_wspornik_paski.blend` | **Wersja końcowa z paskami**: widoczne wszystkie linie siatki (Overlays → Wireframe, Edge Length), po `Tab` każdą ścianę można zaznaczyć osobno |
| `output/projekt4_wspornik_gladki.blend` | **Wersja końcowa gładka**: 128 segmentów cylindra, Shade Smooth by Angle 30°, bez pasków |
| `output/projekt4_polowa.blend` | **Wersja zrobiona do połowy** (stan po zadaniu 4.3.2) |
| `output/wspornik_final_*.obj`, `.stl` | Sama bryła końcowa (import w starszym Blenderze / druk 3D) |
| `build_model.py`, `build_half.py` | Skrypty, które budują pliki od zera (`LAB4_SMOOTH=1` → wersja gładka) |
| `blueprint.png`, `instrukcja-Lab-proj-4.pdf` | Rysunek referencyjny i instrukcja |
| `podglad*.png` | Podglądy |

**Jak pobrać z GitHuba:** wejdź w repozytorium → przełącz gałąź na `blender-lab4` → `output/…blend` → *Download raw file*.
Pliki są zapisane w Blenderze 5.2 i otwierają się w wersji 4.5 LTS lub nowszej.

## Konwencja jak u prowadzącego

Jednostki domyślne (metry), **1 mm z rysunku = 0.01 m**:
* podstawa 60 × 70 × 20 → **0.6 × 0.7 × 0.2 m**; przód na płaszczyźnie XZ (Y = 0), kostka wyśrodkowana w Z (Z −0.1…0.1), origin w World Origin,
* cylinder ⌀50 × 40 → `Shift+A` *Cylinder*, **Location (0, 0.55, 0.7)**, **Rotation X 90°**, **Scale 0.25 / 0.25 / 0.2** → Dimensions 0.5 × 0.5 × 0.4 m (oś 60 mm nad górą podstawy).

## Scene Collection w pliku końcowym (zad. 4.4–4.5)

```
obiekt_mods                [oko wył.]  ← stan z modyfikatorami
  model
    Cube           Mirror (X, Clipping, Merge 0.01 m) + Boolean (Difference, Collection: wycinanie, Exact)
    Cylinder       Boolean (Difference, Collection: wycinanie, Exact)
  wycinanie                [oko wył.]
    Cylinder.001   otwór ⌀20 przelotowy
    Cylinder.002   otwór ⌀15 przelotowy
    Cylinder.003   pogłębienie ⌀30 × 6 + Mirror (Mirror Object: Cylinder) → obie strony
obiekt_final                            ← Duplicate Collection, modyfikatory zatwierdzone
  model.001
    Cube.001       gotowa bryła (Mirror → Boolean → Union z cylindrem, apply)
    Cylinder.004   [ukryty] cylinder użyty w Union
  wycinanie.001            [oko wył.]
    Cylinder.005 / .006 / .007
```
Żeby zobaczyć wersję z działającymi modyfikatorami: w Outlinerze włącz oko przy `obiekt_mods`, a wyłącz przy `obiekt_final`.

## Wymiary [mm z rysunku → m w Blenderze]

| Element | Wymiary |
|---|---|
| Podstawa | 60 × 70 × 20 → 0.6 × 0.7 × 0.2 |
| Część dolna | szer. 40 (2×R20), grub. 20 (Y 0…0.2), środek otworu 60 pod spodem podstawy (Z = −0.7), dół R20, przejście R10 |
| Otwór dolny | ⌀15 przelotowy |
| Cylinder | ⌀50 × 40, oś 60 nad górą podstawy (Z = 0.7), Y 0.35…0.75 |
| Otwór cylindra | ⌀20 przelotowy, pogłębienie ⌀30 × 6 z obu stron |
| Tylna ścianka | pełna, gr. 10 (Y 0.6…0.7), od podstawy do osi cylindra, u dołu szer. 60, zwęża się do 50 (styczna do cylindra) |
| Podpórka | pełna ścianka gr. 10 (X −0.05…0.05): skos od przedniej krawędzi podstawy do dołu przodu cylindra, pod skosem wypełniona do podstawy, cylindra i tylnej ścianki |

## Wersja zrobiona do połowy – `projekt4_polowa.blend`

Zrobione: 4.1, 4.2, 4.3.1 i 4.3.2, czyli podstawa z Mirror, pętle cięć, część dolna i zaokrąglenia R10/R20. Cylinder jest dodany ze skalą 0.25/0.25/0.2, ale **jeszcze nieosadzony** (Z = 1.3 zamiast 0.7).
Niezrobione: tylna ścianka, podpórka, osadzenie cylindra, `wycinanie`, Boolean, `obiekt_mods`/`obiekt_final`.
Plik otwiera się w Edit Mode z zaznaczonymi ścianami do następnego extrude. Kursor 3D stoi w miejscu otworu ⌀15, a lista postępu jest w `POSTEP_PRACY.txt` (zakładka Scripting).

**Zakładki:** **Layout** (start), **UV Editing** (blueprint obok widoku 3D – zad. 4.1), **Modeling**, **Scripting** (lista postępu).

## Wykonanie krok po kroku (ręcznie)

### 4.1
1. *File → New → General*, usuń kostkę, kamerę i światło (`X`).
2. Zakładka *UV Editing* (albo podziel okno): Viewport 3D obok Image Editor, *Image → Open* → `blueprint.png`.

### 4.2 Kostka 20×60×70
1. Outliner: PPM → *New Collection* → `model`.
2. `Shift+A` → *Cube*. `Tab`, `A`, potem kolejno: `S X 0.3 Enter`, `S Y 0.35 Enter`, `S Z 0.1 Enter` (domyślna kostka ma 2 m, więc wychodzi 0.6 × 0.7 × 0.2). Następnie `G Y 0.35 Enter`, żeby przód leżał na XZ. Origin zostaje w (0,0,0).
   Kontrola: Object Mode → `N` → Dimensions 0.6 / 0.7 / 0.2, Scale 1.
3. `Ctrl+R` pętla na środku (X = 0) → zaznacz lewą połowę → `X` → *Vertices*.
4. *Add Modifier → Mirror*: Axis X, Clipping wł., Merge 0.01 m.
5. Z.4.2.2: `Ctrl+R` dodaj pętle w miejscach wypustek: X = 0.05 / 0.2 / 0.25, Y = 0.1 / 0.2 / 0.35 / 0.6.

### 4.3
1. Spód X 0…0.2, Y 0…0.2 → `E` → `Z -0.8`. Pętla na Z = −0.7 (środek otworu).
2. Bevel `Ctrl+B`, Segments 16: dolna krawędź Width 0.2 (R20), krawędź przy podstawie Width 0.1 (R10).
3. Na górze podstawy zaznacz pas X 0…0.05 (podpórka) i Y 0.6…0.7 (tylna ścianka) → `E` → `Z 0.6`. Zewnętrzne górne werteksy ścianki przesuń z X = 0.3 na 0.25. Górne werteksy podpórki ustaw na skos od przedniej krawędzi podstawy (Z = 0.1) do dołu cylindra (Y = 0.35, Z ≈ 0.46). Pod skosem zostaje pełna ścianka.
4. `Shift+A` → *Cylinder*: Location (0, 0.55, 0.7), Rotation X 90, Scale 0.25 / 0.25 / 0.2 → kolekcja `model`.

### 4.4
1. Nowa kolekcja `wycinanie`. Kursor w środek otworu (`Shift+S` → *Cursor to Selected*) → `Shift+A` *Cylinder*:
   * `Cylinder.001`: Location (0, 0.55, 0.7), Rot X 90, Scale 0.1 / 0.1 / 0.25 (⌀20),
   * `Cylinder.002`: Location (0, 0.1, −0.7), Rot X 90, Scale 0.075 / 0.075 / 0.15 (⌀15),
   * `Cylinder.003`: Location (0, 0.375, 0.7), Rot X 90, Scale 0.15 / 0.15 / 0.035 (⌀30 × 6) + *Mirror* (Axis Z, Mirror Object: `Cylinder`) → pogłębienie z obu stron.
2. Wyłącz oko przy kolekcji `wycinanie`.
3. Na `Cube` i `Cylinder`: *Add Modifier → Boolean*, Difference, Operand Type **Collection** → `wycinanie`, Solver **Exact**.

### 4.5
1. Kolekcja `obiekt_mods` → przeciągnij do niej `model` i `wycinanie`.
2. PPM na `obiekt_mods` → *Duplicate Collection* → nazwij `obiekt_final`; wyłącz oko przy `obiekt_mods`.
3. W `obiekt_final` *Apply* modyfikatory: najpierw obiekty z `wycinanie.001`, potem `Cylinder.004`, potem `Cube.001`.
4. Na `Cube.001`: *Boolean → Union*, Object `Cylinder.004` → *Apply*. Ukryj `Cylinder.004`.

Wynik: `Cube.001` – jedna zamknięta bryła (0 krawędzi non-manifold, objętość ≈ 241 339 mm³ z rysunku).

## Uruchomienie skryptów
```
blender --background --python build_model.py                  # wersja z paskami
LAB4_SMOOTH=1 blender --background --python build_model.py    # wersja gładka
blender --background --python build_half.py                    # wersja do połowy
```
