# Projekt 4 – Algebra Boole'a na obiektach technicznych (Blender)

Osobny projekt laboratoryjny (nie jest częścią aplikacji *mini-zoom*, leży na osobnej gałęzi `blender-lab4`).

## Pliki do pobrania

| Plik | Co to jest |
|---|---|
| `output/projekt4_wspornik_gladki.blend` | **Wersja końcowa GŁADKA** – bez pasków: 128 segmentów cylindra, 32 segmenty zaokrągleń, *Shade Smooth by Angle* 30° |
| `output/projekt4_wspornik_paski.blend` | **Wersja końcowa Z PASKAMI** – widoczne wszystkie linie siatki: bryła przecięta pętlami krawędzi (X ±5/±20/±25, Y 10…70, Z −60…80), bevele 16 segm., w Viewport włączone *Overlays → Wireframe* i *Edge Length*. Linie można wyłączyć/włączyć: *Overlays* (ikona dwóch kółek nad widokiem) → *Wireframe*. Oba pliki: kolekcje `obiekt_mods` (model + wycięcia z modyfikatorami) i `obiekt_final` (bryła po apply i Union), blueprint spakowany w pliku |
| `output/wspornik_final_gladki.*`, `output/wspornik_final_paski.*` (`.obj`, `.stl`) | Sama bryła końcowa (do importu w starszym Blenderze / druku 3D) |
| `output/projekt4_polowa.blend` | **Wersja zrobiona do połowy** (stan w trakcie pracy – patrz niżej) |
| `build_half.py` | Skrypt budujący wersję do połowy |
| `podglad_polowa.png` | Podgląd wersji do połowy (z siatką) |
| `build_model.py` | Skrypt, który buduje cały model od zera (te same kroki co niżej) |
| `blueprint.png` | Rysunek referencyjny |
| `podglad.png` | Rendery modelu z 4 stron |

**Jak pobrać z GitHuba:** wejdź w repozytorium → przełącz gałąź na `blender-lab4` → `output/projekt4_wspornik_gladki.blend` (lub `_paski`) → przycisk *Download raw file*.
Plik zapisany w Blenderze 5.2 – otworzy się w Blenderze 4.5 LTS i nowszych. W starszej wersji: uruchom `build_model.py` (zakładka *Scripting* → *Open* → *Run Script*, `blueprint.png` musi leżeć obok skryptu) albo zaimportuj `.obj`.

Po otwarciu `.blend` kliknij u góry zakładkę **Blueprint** – po lewej Image Editor z rysunkiem, po prawej Viewport 3D (zad. 4.1).

![podgląd](podglad.png)

## Wersja zrobiona do połowy – `projekt4_polowa.blend`

Zrobione: 4.1, 4.2, 4.3.1 i 4.3.2, czyli podstawa z Mirror, wszystkie pętle cięć, część dolna wyciągnięta o 80 i zaokrąglenia R10/R20. Cylinder ⌀50×40 jest dodany, ale **jeszcze nieosadzony** (wisi nad modelem).
Niezrobione: tylna ścianka, podpórka, osadzenie cylindra (4.3.3), otwory i Boolean (4.4), oczyszczanie (4.5).
Po czym widać, że to praca w toku:
* obiekt nadal nazywa się `Cube`, plik otwiera się w **Edit Mode** z zaznaczonymi ścianami, z których będą wyciągane tylna ścianka i podpórka (następny krok),
* Mirror jest niezatwierdzony (edytowana tylko połowa), widać wszystkie pętle cięć i bevele 16 segmentów,
* 3D kursor stoi już w miejscu otworu ⌀15 (0, 10, −60),
* brak kolekcji `wycięcia`, `obiekt_mods`, `obiekt_final`,
* lista postępu w tekście `POSTEP_PRACY.txt`.

**Jakie zakładki otworzyć (u góry okna Blendera):**
1. **Layout** – widok startowy: Viewport 3D w Edit Mode, w Outlinerze kolekcja `model` z `Cube` i `Cylinder`; po prawej *Properties* → ikona klucza 🔧 (*Modifiers*) pokazuje niezatwierdzony Mirror.
2. **UV Editing** – po lewej Image Editor z blueprintem, po prawej Viewport 3D (to jest układ z zad. 4.1).
3. **Modeling** – wygodna praca na siatce (Edit Mode).
4. **Scripting** – w edytorze tekstu `POSTEP_PRACY.txt` z odhaczonymi i pozostałymi krokami.

W Viewport włączone są nakładki *Wireframe* i *Edge Length*. Przy zaznaczonych krawędziach wyświetlają się ich długości.

## Wymiary odczytane z rysunku [mm]

Jednostki sceny: *Metric*, *Unit Scale* 0.001, *Length* = mm (1 jednostka = 1 mm). Przód podstawy leży na płaszczyźnie XZ (Y = 0), model rośnie w stronę +Y, oś symetrii to płaszczyzna YZ (X = 0).

| Element | Wymiary / położenie |
|---|---|
| Podstawa | 60 (X) × 70 (Y) × 20 (Z); X −30…30, Y 0…70, Z 0…20 |
| Część dolna | szer. 40 (2×R20), grub. 20 (Y 0…20), środek otworu 60 pod spodem podstawy (Z = −60), dół R20, przejście do podstawy R10 |
| Otwór dolny | ⌀15 przelotowy |
| Cylinder | ⌀50 × 40, oś równoległa do Y na wysokości Z = 80 (**60 nad górą podstawy**), Y 35…75 (35 od przodu podstawy) |
| Otwór cylindra | ⌀20 przelotowy, pogłębienie ⌀30 × 6 z obu stron |
| Tylna ścianka | pełna (bez wycięcia), od góry podstawy do osi cylindra Z = 80, grub. 10 (Y 60…70, czyli 25 za przodem cylindra), u dołu szer. 60 (cała podstawa), zwęża się do 50 – styczna do cylindra |
| Podpórka | **pełna ścianka** grub. 10 (środek, X −5…5): skos od przedniej krawędzi podstawy do **dolnej krawędzi** przodu cylindra, pod skosem wypełniona aż do podstawy, cylindra i tylnej ścianki – bez pustej przestrzeni |

## Wykonanie krok po kroku (ręcznie w Blenderze)

### Zadanie 4.1 – przygotowanie Blendera
1. *File → New → General*, zaznacz kostkę, kamerę i światło → `X` → *Delete*.
2. *Scene Properties → Units*: Unit System *Metric*, Unit Scale `0.001`, Length *Millimeters*. W Viewport → `N` → *View* ustaw *Clip End* np. 5000.
3. Przeciągnij lewą krawędź okna (lub wejdź w zakładkę *UV Editing*), by mieć **Viewport 3D** i **Image Editor** obok siebie.
4. W Image Editor: *Image → Open* → `blueprint.png`.

### Zadanie 4.2 – kształt podstawowy
1. W Outlinerze: PPM → *New Collection* → nazwij `model`.
2. **Kostka 20×60×70 (Z.4.2.1)**: `Shift+A` → *Mesh → Cube*. Domyślna kostka ma 2×2×2 i środek w (0,0,0). Skalujemy ją w **Edit Mode**, żeby Object Origin został w World Origin, a skala obiektu = 1:
   * `Tab` (Edit Mode) → `A` (zaznacz wszystko),
   * wpisz z klawiatury: `S` `X` `0.3` `Enter` (szer. 60), `S` `Y` `0.35` `Enter` (głęb. 70), `S` `Z` `0.1` `Enter` (wys. 20). Przy domyślnych jednostkach (metrach) wyjdzie 0.6 × 0.7 × 0.2 m, tak jak u prowadzącego (0.1 m = 10 mm),
   * przód styczny z płaszczyzną XZ: `G` `Y` `0.35` `Enter`. Siatka zajmuje wtedy Y 0…0.7, a przód (strona widoczna w `Numpad 1`) leży na Y = 0. Opcjonalnie `G` `Z` `0.1`, żeby spód leżał na Z = 0.
   * kontrola: `N` → *Item*. Zaznacz ścianę przednią, *Median Y* = 0. W Object Mode *Dimensions* = 0.6 / 0.7 / 0.2, *Scale* = 1, *Location* = 0.
   * jeśli wolisz milimetry (jak w moim pliku): *Scene Properties → Units* → Unit Scale `0.001`, Length *Millimeters*. Wtedy `S X 30`, `S Y 35`, `S Z 10`, `G Y 35`.
3. `M` → przenieś do kolekcji `model`.
4. Edit Mode → `Ctrl+R` → pętla krawędzi w połowie (płaszczyzna YZ, X = 0). Zaznacz wierzchołki z X < 0 → `X` → *Vertices*.
5. *Modifiers → Add → Generate → Mirror*: Axis **X**, *Bisect* wył., *Clipping* **wł.**, *Merge* **wł.**, 0.01.
6. **Z.4.2.2** – dodaj pętle krawędzi (`Ctrl+R`, potem wpisz wartość przesunięcia) w miejscach wypustek: X = 20 (bok części dolnej), X = 25 (bok tylnej ścianki), X = 5 (żebro), Y = 20 (tył części dolnej), Y = 60 (przód tylnej ścianki).

### Zadanie 4.3 – rozbudowa obiektu bazowego
**4.3.1 Część dolna**
1. Zaznacz na spodzie ścianę X 0…20, Y 0…20 → `E` → wyciągnij w dół o **80** (`E`, `Z`, `-80`).
2. `Ctrl+R` dodaj pętle wyznaczające początek i koniec zaokrągleń (Z = −10 przy podstawie, Z = −60 na środku otworu). Zbędne cięcia usuń: zaznacz → `X` → *Dissolve Edges/Vertices*.

**4.3.2 Zaokrąglenia**
1. Krawędź dolna zewnętrzna (X = 20, Z = −80) → `Ctrl+B` (Bevel), *Width* **20**, *Segments* **16** → po odbiciu daje półokrąg R20.
2. Krawędź wewnętrzna między spodem podstawy a bokiem części dolnej (X = 20, Z = 0) → `Ctrl+B`, *Width* **10**, *Segments* **16** → R10.

**4.3.3 Część górna**
1. (1) Na górze podstawy zaznacz ścianę X 0…25, Y 60…70 → `E` → wyciągnij do Z = 80 (o 60); zewnętrzne górne werteksy przesuń z X = 30 na X = 25 (zwężenie do stycznej z cylindrem) – to tylna ścianka gr. 10.
2. (2) `Shift+A` → *Cylinder*: Vertices 64, Radius 25, Depth 40. Obróć `R X 90`. Ustaw Location: X 0, Y 55, Z 80 (przód na Y = 35). Przenieś do kolekcji `model`. Można też użyć *Snap → Vertex → Closest*.
3. (3) Podpórka: dodaj pętlę Y = 35. Zaznacz na górze podstawy pas ścian X 0…5 od Y = 0 do tylnej ścianki i wyciągnij go razem z tylną ścianką (jeden extrude o 60).
4. (4) Ustaw górne werteksy pasa na skos: Y = 0 → Z = 20 (scal z krawędzią podstawy, `M` → *By Distance*), Y = 10 → Z = 32, Y = 20 → Z = 44, Y = 35 → Z = 56 (dół przodu cylindra). Pod skosem zostaje **pełna ścianka** – nic nie wycinamy. Brakujące ściany uzupełnij `F` (Fill).
5. (5) Powtórz dla pozostałych kątowników (tylna ścianka styczna do cylindra).

### Zadanie 4.4 – otwory
1. Nowa kolekcja `wycięcia`.
2. Ustaw kursor w środku otworu (`Shift+S` → *Cursor to Selected* na zaznaczonych wierzchołkach albo `N` → *View → 3D Cursor*), potem `Shift+A` → *Cylinder* – pojawi się w miejscu kursora:
   * `otwor_fi20`: R 10, dł. 50, oś Y, środek (0, 55, 80),
   * `poglebienie_fi30x6`: R 15, Y 34…41 (6 mm w głąb cylindra + 1 mm zapasu). Dodaj **Mirror** oś **Y** z *Mirror Object* = Empty w środku cylindra (0, 55, 80) → pogłębienie po obu stronach,
   * `otwor_fi15`: R 7.5, dł. 30, oś Y, środek (0, 10, −60).
3. W Outlinerze wyłącz widoczność kolekcji `wycięcia` (ikonka oka / ekranu).
4. Na **podstawie** i **cylindrze**: *Add Modifier → Generate → Boolean*, **Difference**, *Operand Type* **Collection** → `wycięcia`. (W kolekcji muszą być same siatki – Empty trzymaj poza nią.)

### Zadanie 4.5 – oczyszczenie modelu
1. Utwórz kolekcję `obiekt_mods` i przeciągnij do niej `model` i `wycięcia`.
2. PPM na `obiekt_mods` → *Duplicate Collection* → nazwij `obiekt_final`; ukryj `obiekt_mods`. Dalej pracuj tylko na kopii (w kopii Boolean musi wskazywać na **kopię** kolekcji wycięć).
3. Sprawdź model pod kątem nakładających się ścian (*Edit Mode → Select → Select All by Trait → Non Manifold*, `M` → *Merge by Distance*).
4. *Apply* (`Ctrl+A` → *Apply All Modifiers* / menu modyfikatora → *Apply*): najpierw na obiektach wycięć, potem na cylindrze, potem na podstawie (Mirror, potem Boolean).
5. Na podstawie dodaj **Boolean → Union** z obiektem cylinder → *Apply*. Usuń cylinder (jest już częścią bryły).

Wynik: obiekt `wspornik_final` – jedna zamknięta bryła (0 krawędzi non-manifold, objętość ≈ 242 389 mm³).

## Uruchomienie skryptu
```
blender --background --python build_model.py                    # wersja z paskami
LAB4_SMOOTH=1 blender --background --python build_model.py      # wersja gładka
```
Wynik trafi do `output/`.
