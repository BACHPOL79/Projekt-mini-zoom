"""
Laboratorium/Projekt 4 - Algebra Boole'a na obiektach technicznych.
Skrypt odtwarza w Blenderze wspornik z blueprintu (rzut izometryczny),
krok po kroku wg zadań 4.1-4.5. Jednostki: 1 BU = 1 mm.

Uruchomienie:
  blender --background --python build_model.py
  (lub w Blenderze: zakładka Scripting > Open > Run Script)
"""
import math
import os
import bpy
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = 16  # liczba segmentów zaokrągleń (wg instrukcji)

# ---------------------------------------------------------------------------
# Wymiary z rysunku [mm]
# ---------------------------------------------------------------------------
BASE_W, BASE_D, BASE_H = 60, 70, 20        # podstawa 60 x 70 x 20
TAB_W, TAB_T = 40, 20                      # dolna część: szer. 2xR20, grubość 20
TAB_HOLE_Z = -60                           # środek otworu fi15: 60 pod podstawą
TAB_R, FILLET_R = 20, 10                   # R20 na dole, R10 przy podstawie
TAB_HOLE_D = 15
CYL_D, CYL_L = 50, 40                      # cylinder fi50 x 40
CYL_Z = 60                                 # oś cylindra 60 nad spodem podstawy
CYL_Y0 = 35                                # przód cylindra 35 od przodu podstawy
PLATE_T = 10                               # tylna ścianka gr. 10 (25 od cylindra)
HOLE_D, CB_D, CB_DEPTH = 20, 30, 6         # fi20, pogłębienie fi30 x 6 obustronnie
RIB_T = 10                                 # żebro ukośne gr. 10


# ---------------------------------------------------------------------------
# Pomocnicze
# ---------------------------------------------------------------------------
def arc(cx, cz, r, a0, a1, n=SEG):
    """Punkty łuku (x, z) od kąta a0 do a1 [stopnie], n segmentów."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def prism_from_profile(name, profile, axis, d0, d1):
    """Tworzy bryłę przez wyciągnięcie (extrude) wielokąta 2D wzdłuż osi.
    axis='Y': profil (x, z); axis='X': profil (y, z)."""
    bm = bmesh.new()
    def v3(p, d):
        return (p[0], d, p[1]) if axis == 'Y' else (d, p[0], p[1])
    bottom = [bm.verts.new(v3(p, d0)) for p in profile]
    face = bm.faces.new(bottom)
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    off = Vector(v3((0, 0), d1 - d0)) if axis == 'Y' else Vector((d1 - d0, 0, 0))
    bmesh.ops.translate(bm, verts=top, vec=off)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)


def cylinder_y(name, r, y0, y1, x=0.0, z=0.0, verts=64):
    """Cylinder o osi równoległej do Y (od y0 do y1)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts,
                          radius1=r, radius2=r, depth=y1 - y0)
    # create_cone daje oś Z -> obrót na oś Y
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                     matrix=__import__("mathutils").Matrix.Rotation(math.radians(-90), 3, 'X'))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = (x, (y0 + y1) / 2, z)
    return ob


def apply_all_modifiers(ob):
    bpy.context.view_layer.objects.active = ob
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def boolean(ob, operation, operand_object=None, operand_collection=None):
    m = ob.modifiers.new(f"Boolean_{operation.title()}", 'BOOLEAN')
    m.operation = operation
    m.solver = 'EXACT'
    if operand_collection is not None:
        m.operand_type = 'COLLECTION'
        m.collection = operand_collection
    else:
        m.object = operand_object
    return m


def cleanup(ob, dist=1e-4):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dist)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5),
                             verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def link(ob, coll):
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)


# ---------------------------------------------------------------------------
# Zadanie 4.1 - przygotowanie sceny i blueprintu
# ---------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001   # 1 BU = 1 mm
scene.unit_settings.length_unit = 'MILLIMETERS'

blueprint = bpy.data.images.load(os.path.join(HERE, "blueprint.png"))
blueprint.pack()                            # obraz zapisany wewnątrz .blend

col_model = bpy.data.collections.new("model")
col_cuts = bpy.data.collections.new("wycięcia")
col_mods = bpy.data.collections.new("obiekt_mods")
scene.collection.children.link(col_mods)
col_mods.children.link(col_model)
col_mods.children.link(col_cuts)

# ---------------------------------------------------------------------------
# Zadanie 4.2 / 4.3 - obiekt bazowy (połowa + Mirror X)
# Przód podstawy styczny z płaszczyzną XZ (Y = 0), origin w World Origin.
# ---------------------------------------------------------------------------
hw = BASE_W / 2
parts = []

# 4.2.1 podstawa 20 x 60 x 70 (połowa: X 0..30)
parts.append(prism_from_profile(
    "p_base", [(0, 0), (hw, 0), (hw, BASE_H), (0, BASE_H)], 'Y', 0, BASE_D))

# 4.3.1-4.3.2 dolna część wyciągnięta z podstawy, zaokrąglenia R10 i R20 (16 segm.)
tab = [(0, 5), (hw, 5), (hw, 0)]
tab += arc(hw, -FILLET_R, FILLET_R, 90, 180)[1:]                 # R10
tab += [(TAB_W / 2, TAB_HOLE_Z)]
tab += arc(0, TAB_HOLE_Z, TAB_R, 0, -90)[1:]                     # R20
parts.append(prism_from_profile("p_tab", tab, 'Y', 0, TAB_T))

# 4.3.3 tylna ścianka (kątownik) styczna do cylindra, gr. 10
plate_y0 = CYL_Y0 + 25                                           # = 60
parts.append(prism_from_profile(
    "p_plate", [(0, BASE_H - 5), (hw, BASE_H - 5), (hw, BASE_H), (CYL_D / 2, CYL_Z), (0, CYL_Z)],
    'Y', plate_y0, plate_y0 + PLATE_T))

# 4.3.3 (5) żebro ukośne gr. 10 od przedniej krawędzi podstawy do cylindra
p0 = Vector((0, BASE_H))                    # (y, z)
p1 = Vector((CYL_Y0, 42))                   # poniżej pogłębienia fi30
d = (p1 - p0).normalized()
n = Vector((d.y, -d.x))
q0 = p0 + n * RIB_T
y_in = CYL_Y0 + 13
rib = [(p0.x, q0.y), tuple(p0), tuple(p1), (y_in, p1.y),
       (y_in, q0.y + (y_in - q0.x) * d.y / d.x), tuple(q0)]
parts.append(prism_from_profile("p_rib", rib, 'X', 0, RIB_T / 2))

for p in parts:
    col_model.objects.link(p)

# scalenie składowych połowy w jeden obiekt "podstawa"
base = parts[0]
base.name = "podstawa"
base.data.name = "podstawa"
for p in parts[1:]:
    boolean(base, 'UNION', operand_object=p)
apply_all_modifiers(base)
for p in parts[1:]:
    bpy.data.objects.remove(p)
cleanup(base)

# usunięcie ścian leżących w płaszczyźnie symetrii X = 0 (otwarta połowa)
bm = bmesh.new()
bm.from_mesh(base.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces
                           if all(abs(v.co.x) < 1e-4 for v in f.verts)], context='FACES')
bm.to_mesh(base.data)
bm.free()

mir = base.modifiers.new("Mirror", 'MIRROR')
mir.use_axis = (True, False, False)
mir.use_clip = True
mir.use_mirror_merge = True
mir.merge_threshold = 0.01

# 4.3.3 (2) cylinder fi50 x 40
cyl = cylinder_y("cylinder", CYL_D / 2, CYL_Y0, CYL_Y0 + CYL_L, z=CYL_Z)
col_model.objects.link(cyl)

# ---------------------------------------------------------------------------
# Zadanie 4.4 - otwory i wgłębienia (kolekcja "wycięcia", niewidoczna)
# ---------------------------------------------------------------------------
cyl_mid = CYL_Y0 + CYL_L / 2
cuts = [
    cylinder_y("otwor_fi20", HOLE_D / 2, CYL_Y0 - 5, CYL_Y0 + CYL_L + 5, z=CYL_Z),
    cylinder_y("poglebienie_fi30x6", CB_D / 2, CYL_Y0 - 1, CYL_Y0 + CB_DEPTH, z=CYL_Z),
    cylinder_y("otwor_fi15", TAB_HOLE_D / 2, -5, TAB_T + 5, z=TAB_HOLE_Z),
]
for c in cuts:
    col_cuts.objects.link(c)
    c.display_type = 'WIRE'

# pogłębienie obustronne -> Mirror Y względem środka cylindra (empty)
mid = bpy.data.objects.new("srodek_cylindra", None)
mid.location = (0, cyl_mid, CYL_Z)
mid.empty_display_size = 10
col_mods.objects.link(mid)   # poza kolekcją wycięć (Boolean wymaga samych siatek)
m = cuts[1].modifiers.new("Mirror", 'MIRROR')
m.use_axis = (False, True, False)
m.mirror_object = mid

col_cuts.hide_viewport = True
col_cuts.hide_render = True

# 4.4.1 Boolean Difference z kolekcją "wycięcia"
for ob in (cyl, base):
    boolean(ob, 'DIFFERENCE', operand_collection=col_cuts)

# ---------------------------------------------------------------------------
# Zadanie 4.5 - kopia kolekcji i oczyszczenie modelu
# ---------------------------------------------------------------------------
col_final = bpy.data.collections.new("obiekt_final")
scene.collection.children.link(col_final)
col_f_model = bpy.data.collections.new("model_final")
col_f_cuts = bpy.data.collections.new("wycięcia_final")
col_final.children.link(col_f_model)
col_final.children.link(col_f_cuts)

dup = {}
for ob in list(col_model.objects) + list(col_cuts.objects) + list(col_mods.objects):
    c = ob.copy()
    if ob.data:
        c.data = ob.data.copy()
    c.name = ob.name + "_final"
    if ob.name in col_cuts.objects:
        col_f_cuts.objects.link(c)
    elif ob.name in col_model.objects:
        col_f_model.objects.link(c)
    else:
        col_final.objects.link(c)
    dup[ob.name] = c
# odwołania w kopiach -> kopie
dup["poglebienie_fi30x6"].modifiers["Mirror"].mirror_object = dup["srodek_cylindra"]
for k in ("cylinder", "podstawa"):
    dup[k].modifiers["Boolean_Difference"].collection = col_f_cuts

# 4.5.3 apply: najpierw wycięcia, potem cylinder, potem podstawa
col_mods.hide_viewport = True               # oryginał ukryty
col_mods.hide_render = True
for k in ("otwor_fi20", "poglebienie_fi30x6", "otwor_fi15"):
    apply_all_modifiers(dup[k])
apply_all_modifiers(dup["cylinder"])
apply_all_modifiers(dup["podstawa"])

final = dup["podstawa"]
boolean(final, 'UNION', operand_object=dup["cylinder"])
apply_all_modifiers(final)
cleanup(final)
final.name = "wspornik_final"
final.data.name = "wspornik_final"
bpy.data.objects.remove(dup["cylinder"])
col_f_cuts.hide_viewport = True
col_f_cuts.hide_render = True
for p in final.data.polygons:
    p.use_smooth = False

# materiał
mat = bpy.data.materials.new("stal")
mat.diffuse_color = (0.55, 0.6, 0.68, 1)
for ob in (final, base, cyl):
    ob.data.materials.append(mat)

# ---------------------------------------------------------------------------
# Widok: 3D Viewport + Image Editor z blueprintem (zad. 4.1), kamera, światło
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 230
cam_data.clip_end = 5000
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (260, -260, 240)
direction = Vector((0, 35, 5)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam)
scene.camera = cam
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(30))
scene.collection.objects.link(sun)

# statystyki kontrolne
deps = bpy.context.evaluated_depsgraph_get()
me = final.evaluated_get(deps).to_mesh()
bm = bmesh.new()
bm.from_mesh(me)
nonman = [e for e in bm.edges if not e.is_manifold]
print(f"[lab4] wspornik_final: {len(bm.verts)} v, {len(bm.faces)} f, "
      f"non-manifold edges: {len(nonman)}, volume: {bm.calc_volume():.1f} mm3")
bm.free()
final.evaluated_get(deps).to_mesh_clear()

# Zad. 4.1: obszar roboczy z Viewport 3D obok Image Editor (blueprint)
ws = bpy.data.workspaces.get("UV Editing")
if ws:
    ws.name = "Blueprint"
    for area in ws.screens[0].areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = blueprint
        if area.type == 'VIEW_3D':
            area.spaces.active.clip_end = 5000
    bpy.context.window.workspace = ws
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.clip_end = 5000

out_dir = os.path.join(HERE, "output") if not os.environ.get("LAB4_OUT") else os.environ["LAB4_OUT"]
os.makedirs(out_dir, exist_ok=True)
# eksport bryły końcowej (dla starszych wersji Blendera / druku 3D)
for o in bpy.context.view_layer.objects:
    o.select_set(o == final)
bpy.context.view_layer.objects.active = final
bpy.ops.wm.obj_export(filepath=os.path.join(out_dir, "wspornik_final.obj"),
                      export_selected_objects=True, export_materials=False)
bpy.ops.wm.stl_export(filepath=os.path.join(out_dir, "wspornik_final.stl"),
                      export_selected_objects=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "projekt4_wspornik.blend"),
                            compress=True)
print("[lab4] zapisano", out_dir)
