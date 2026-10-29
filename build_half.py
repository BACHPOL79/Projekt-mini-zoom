"""
Projekt 4 - wersja zrobiona DO POŁOWY (stan pracy po zadaniu 4.3.2).
Model budowany "ręcznymi" operacjami Edit Mode: kostka -> cięcia -> usunięcie
połowy -> Mirror -> pętle krawędzi -> extrude -> bevel. Brak żebra, otworów,
Booleanów i oczyszczania (zadania 4.3.3 (3)-(5), 4.4, 4.5 do zrobienia).
"""
import math
import os
import bpy
import bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)


def cut(bm, co, no):
    """Odpowiednik pętli krawędzi Ctrl+R: przecięcie siatki płaszczyzną."""
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-5)


def face_at(bm, center, normal, tol=1e-3):
    for f in bm.faces:
        if (f.calc_center_median() - Vector(center)).length < tol and \
                f.normal.dot(Vector(normal)) > 0.99:
            return f
    raise RuntimeError(f"brak ściany w {center}")


def edges_where(bm, pred):
    return [e for e in bm.edges if all(pred(v.co) for v in e.verts)]


def near(a, b):
    return abs(a - b) < 1e-3


# --- 4.1 scena, jednostki, blueprint ---------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'   # jak u prowadzącego: 1 mm = 0.01 m
img = bpy.data.images.load(os.path.join(HERE, "blueprint.png"))
img.pack()

col_model = bpy.data.collections.new("model")
scene.collection.children.link(col_model)

# --- 4.2.1 kostka 60 x 70 x 20, przód na płaszczyźnie XZ ----------------------
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.scale(bm, vec=(60, 70, 20), verts=bm.verts)
bmesh.ops.translate(bm, vec=(0, 35, 10), verts=bm.verts)

# podział w płaszczyźnie YZ i usunięcie lewej połowy
cut(bm, (0, 0, 0), (1, 0, 0))
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x < -1e-3], context='VERTS')

# --- 4.2.2 dodatkowe linie cięć (miejsca wypustek) ---------------------------
for x in (5, 20, 25):
    cut(bm, (x, 0, 0), (1, 0, 0))
for y in (10, 20, 35, 60):
    cut(bm, (0, y, 0), (0, 1, 0))

# --- 4.3.1 część dolna: extrude ściany spodu w dół o 60 ----------------------
bottom = [f for f in bm.faces if f.normal.z < -0.99 and
          all(v.co.x <= 20 + 1e-3 and v.co.y <= 20 + 1e-3 for v in f.verts)]
ext = bmesh.ops.extrude_face_region(bm, geom=bottom)
bmesh.ops.delete(bm, geom=bottom, context='FACES')
verts = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
bmesh.ops.translate(bm, verts=verts, vec=(0, 0, -60))
# pętla na wysokości środka otworu (koniec zaokrąglenia R20)
cut(bm, (0, 0, -40), (0, 0, 1))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)

# --- 4.3.2 zaokrąglenia Bevel, 16 segmentów ----------------------------------
# R10 - przejście podstawa / część dolna
e10 = edges_where(bm, lambda c: near(c.x, 20) and near(c.z, 0) and c.y <= 20 + 1e-3)
bmesh.ops.bevel(bm, geom=e10 + list({v for e in e10 for v in e.verts}),
                offset=10, offset_type='OFFSET', segments=16, profile=0.5,
                affect='EDGES', clamp_overlap=False)
# R20 - dół części dolnej (bevel prawie na całą szerokość połówki)
e20 = edges_where(bm, lambda c: near(c.x, 20) and near(c.z, -60))
bmesh.ops.bevel(bm, geom=e20 + list({v for e in e20 for v in e.verts}),
                offset=19.98, offset_type='OFFSET', segments=16, profile=0.5,
                affect='EDGES', clamp_overlap=False)

# ściany na płaszczyźnie symetrii nie są potrzebne (Mirror + Clipping)
bmesh.ops.delete(bm, geom=[f for f in bm.faces
                           if all(abs(v.co.x) < 1e-3 for v in f.verts)], context='FACES')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

me = bpy.data.meshes.new("Cube")
# skala instrukcji: 1 mm = 0.01 m, podstawa wyśrodkowana w Z (Z -0.1..0.1)
for v in bm.verts:
    v.co = Vector((v.co.x * 0.01, v.co.y * 0.01, (v.co.z - 10) * 0.01))
bm.to_mesh(me)
bm.free()
base = bpy.data.objects.new("Cube", me)
col_model.objects.link(base)
mir = base.modifiers.new("Mirror", 'MIRROR')
mir.use_axis = (True, False, False)
mir.use_clip = True
mir.use_mirror_merge = True
mir.merge_threshold = 0.01

# --- 4.3.3 (2) cylinder fi50 x 40 dodany, jeszcze NIE osadzony (wisi nad modelem) ----------------
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1, depth=2,
                                    location=(0, 0.55, 1.3), rotation=(math.radians(90), 0, 0))
cyl = bpy.context.active_object
cyl.scale = (0.25, 0.25, 0.2)                     # 0.5 x 0.5 x 0.4 m
for c in cyl.users_collection:
    c.objects.unlink(cyl)
col_model.objects.link(cyl)

mat = bpy.data.materials.new("stal")
mat.diffuse_color = (0.55, 0.6, 0.68, 1)
for ob in (base, cyl):
    ob.data.materials.append(mat)

# 3D kursor w miejscu przyszłego otworu fi15 (przygotowanie do 4.4)
scene.cursor.location = (0, 0.1, -0.5)

# --- notatki postępu (zakładka Scripting) ------------------------------------
txt = bpy.data.texts.new("POSTEP_PRACY.txt")
txt.write("""PROJEKT 4 - STAN PRACY
[x] 4.1   scena (metry, 1 mm = 0.01 m), blueprint w Image Editor (zakładka UV Editing)
[x] 4.2.1 kostka 60x70x20, podział YZ, połowa usunięta, Mirror X + Clipping
[x] 4.2.2 pętle krawędzi: X=5, 20, 25 / Y=10, 20, 35, 60
[x] 4.3.1 część dolna wyciągnięta o 60, cięcie Z=-40 (środek otworu, 60 pod górą podstawy)
[x] 4.3.2 Bevel R10 i R20, 16 segmentów
[~] 4.3.3 (2) cylinder fi50x40 dodany - TRZEBA go osadzić: Location (0, 0.55, 0.7)
[ ] 4.3.3 (1) tylna ścianka gr.10 do Z=80, zwężona do stycznej (zaznaczone ściany)
[ ] 4.3.3 (3)-(5) podpórka - pełna ścianka gr.10 pod skosem do cylindra
[ ] 4.4   kolekcja "wycinanie": fi20, pogłębienie fi30x6 (Mirror), fi15 (kursor już ustawiony w (0, 0.1, -0.5))
[ ] 4.4   Boolean Difference -> kolekcja "wycinanie"
[ ] 4.5   obiekt_mods (model + wycinanie) -> Duplicate Collection -> obiekt_final, apply, Union
""")

# --- widoki: blueprint obok viewportu ----------------------------------------
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = img
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            sp.overlay.show_wireframes = True
            sp.overlay.show_extra_edge_length = True
            r = sp.region_3d
            r.view_location = (0, 0.35, 0.2)
            r.view_distance = 3.4
            r.view_rotation = Vector((0, 0, -1)).rotation_difference(Vector((0, 0, -1)))
            r.view_rotation = (Matrix.Rotation(math.radians(-45), 3, 'Z') @
                               Matrix.Rotation(math.radians(60), 3, 'X')).to_quaternion()
        if area.type == 'TEXT_EDITOR':
            area.spaces.active.text = txt

# --- zapis w Edit Mode z zaznaczoną ścianą pod żebro (następny krok) ---------
for o in bpy.context.view_layer.objects:
    o.select_set(o == base)
bpy.context.view_layer.objects.active = base
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='FACE')
bmE = bmesh.from_edit_mesh(base.data)
for f in bmE.faces:
    c = f.calc_center_median()
    f.select_set(f.normal.z > 0.99 and near(c.z, 20) and (c.y > 60 or c.x < 5))
bmesh.update_edit_mesh(base.data)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "projekt4_polowa.blend"), compress=True)
print("[polowa] zapisano")
