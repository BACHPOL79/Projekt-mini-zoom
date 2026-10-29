"""
Laboratorium/Projekt 4 - Algebra Boole'a na obiektach technicznych.
Skrypt odtwarza w Blenderze wspornik z blueprintu (rzut izometryczny),
krok po kroku wg zadań 4.1-4.5. Jednostki jak u prowadzącego: metry,
1 mm z rysunku = 0.01 m (podstawa 0.6 x 0.7 x 0.2 m, środek podstawy w World Origin).

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
# LAB4_SMOOTH=1 -> wersja gładka (więcej segmentów + Shade Smooth by Angle),
# inaczej wersja "z paskami" (płaskie cieniowanie, widoczne ścianki)
SMOOTH = os.environ.get("LAB4_SMOOTH") == "1"
VARIANT = "gladki" if SMOOTH else "paski"
CYL_VERTS = 128 if SMOOTH else 64
if SMOOTH:
    SEG = 32

# ---------------------------------------------------------------------------
# Wymiary z rysunku [mm]
# ---------------------------------------------------------------------------
BASE_W, BASE_D, BASE_H = 60, 70, 20        # podstawa 60 x 70 x 20
TAB_W, TAB_T = 40, 20                      # dolna część: szer. 2xR20, grubość 20
TAB_HOLE_Z = BASE_H - 60                   # środek otworu fi15: 60 pod GÓRĄ podstawy (Z = -40)
TAB_R, FILLET_R = 20, 10                   # R20 na dole, R10 przy podstawie
TAB_HOLE_D = 15
CYL_D, CYL_L = 50, 40                      # cylinder fi50 x 40
CYL_Z = 20 + 60                            # oś cylindra 60 nad GÓRĄ podstawy (Z = 80)
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


def cylinder_y(name, r, y0, y1, x=0.0, z=0.0, verts=None):
    """Cylinder o osi równoległej do Y (od y0 do y1)."""
    verts = verts or CYL_VERTS
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


K = 0.01          # 1 mm z rysunku = 0.01 m w Blenderze (jak w instrukcji)
ZO = -BASE_H / 2  # podstawa wyśrodkowana w Z (kostka nieprzesuwana w osi Z)


def to_scene(ob):
    """Siatka zbudowana w mm -> skala sceny (m), środek podstawy w Z = 0."""
    for v in ob.data.vertices:
        v.co = Vector((v.co.x * K, v.co.y * K, (v.co.z + ZO) * K))
    ob.data.update()


def prim_cylinder(coll, r, y0, y1, z, verts=None):
    """Shift+A > Cylinder (r=1, depth=2), Rotation X 90, Scale jak w instrukcji."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts or CYL_VERTS, radius=1, depth=2,
        location=(0, K * (y0 + y1) / 2, K * (z + ZO)), rotation=(math.radians(90), 0, 0))
    ob = bpy.context.active_object
    ob.scale = (K * r, K * r, K * (y1 - y0) / 2)
    link(ob, coll)
    return ob


# pętle krawędzi tylko na granicach bloków (jak Ctrl+R w zad. 4.2.2 / 4.3.1):
# X: podpórka 5, część dolna 20, tylna ścianka 25; Y: tył części dolnej 20,
# przód cylindra 35, przód ścianki 60; Z: koniec R10 (-10), środek otworu fi15
BLOCK_X = [RIB_T / 2, TAB_W / 2, CYL_D / 2]


def natural_planes(xs):
    return ([((x, 0, 0), (1, 0, 0)) for x in xs] +
            [((0, y, 0), (0, 1, 0)) for y in (TAB_T, CYL_Y0, CYL_Y0 + 25)] +
            [((0, 0, z), (0, 0, 1)) for z in (-FILLET_R, TAB_HOLE_Z)])


def on_cylinder(f):
    """ściana należąca do cylindra (płaszcz, denka, otwory) - bez dodatkowych cięć"""
    ax_z = K * (CYL_Z + ZO)
    for v in f.verts:
        r = math.hypot(v.co.x, v.co.z - ax_z) / K
        y = v.co.y / K
        if not (CYL_Y0 - 1e-3 <= y <= CYL_Y0 + CYL_L + 1e-3 and r <= CYL_D / 2 + 1e-3):
            return False
        if not (abs(r - CYL_D / 2) < 0.05 or r <= CB_D / 2 + 1e-3 or
                abs(y - CYL_Y0) < 1e-3 or abs(y - CYL_Y0 - CYL_L) < 1e-3):
            return False
    return True


def bisect(ob, planes, skip=None):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for co, no in planes:
        faces = [f for f in bm.faces if not (skip and skip(f))]
        geom = list({v for f in faces for v in f.verts}) + \
            list({e for f in faces for e in f.edges}) + faces
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-6)
    bm.to_mesh(ob.data)
    bm.free()


def lc(name, parent=None):
    """layer collection (oko w Outlinerze)"""
    root = parent or bpy.context.view_layer.layer_collection
    for ch in root.children:
        if ch.name == name:
            return ch
        found = lc(name, ch)
        if found:
            return found
    return None


# ---------------------------------------------------------------------------
# Zadanie 4.1 - przygotowanie sceny i blueprintu
# ---------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

blueprint = bpy.data.images.load(os.path.join(HERE, "blueprint.png"))
blueprint.pack()                            # obraz zapisany wewnątrz .blend

# kolekcje jak w instrukcji: obiekt_mods > model, wycinanie
col_mods = bpy.data.collections.new("obiekt_mods")
col_model = bpy.data.collections.new("model")
col_cuts = bpy.data.collections.new("wycinanie")
scene.collection.children.link(col_mods)
col_mods.children.link(col_model)
col_mods.children.link(col_cuts)

# ---------------------------------------------------------------------------
# Zadanie 4.2 / 4.3 - obiekt bazowy "Cube" (połowa + Mirror X)
# Przód podstawy styczny z płaszczyzną XZ (Y = 0), origin w World Origin.
# ---------------------------------------------------------------------------
hw = BASE_W / 2
parts = []

# 4.2.1 podstawa 20 x 60 x 70 (połowa: X 0..30)
parts.append(prism_from_profile(
    "p_base", [(0, 0), (hw, 0), (hw, BASE_H), (0, BASE_H)], 'Y', 0, BASE_D))

# 4.3.1-4.3.2 dolna część wyciągnięta z podstawy, zaokrąglenia R10 i R20
tab = [(0, 5), (hw, 5), (hw, 0)]
tab += arc(hw, -FILLET_R, FILLET_R, 90, 180)[1:]                 # R10
tab += [(TAB_W / 2, TAB_HOLE_Z)]
tab += arc(0, TAB_HOLE_Z, TAB_R, 0, -90)[1:]                     # R20
parts.append(prism_from_profile("p_tab", tab, 'Y', 0, TAB_T))

# 4.3.3 (1) tylna ścianka gr. 10, zwężona do stycznej z cylindrem
plate_y0 = CYL_Y0 + 25                                           # = 60
parts.append(prism_from_profile(
    "p_plate", [(0, BASE_H - 5), (hw, BASE_H - 5), (hw, BASE_H), (CYL_D / 2, CYL_Z), (0, CYL_Z)],
    'Y', plate_y0, plate_y0 + PLATE_T))

# 4.3.3 (3)-(5) podpórka: pełna ścianka gr. 10 pod skosem, od przedniej krawędzi
# podstawy do dołu cylindra i dalej do tylnej ścianki
RIB_TOP = CYL_Z - CYL_D / 2 + 1
rib = [(0, BASE_H - 5), (0, BASE_H), (CYL_Y0, RIB_TOP), (plate_y0 + 5, RIB_TOP),
       (plate_y0 + 5, BASE_H - 5)]
parts.append(prism_from_profile("p_rib", rib, 'X', 0, RIB_T / 2))

for p in parts:
    col_model.objects.link(p)

base = parts[0]
for p in parts[1:]:
    boolean(base, 'UNION', operand_object=p)
apply_all_modifiers(base)
for p in parts[1:]:
    bpy.data.objects.remove(p)
cleanup(base)
if not SMOOTH:
    # 4.2.2 / 4.3.1 pętle krawędzi - każda ściana osobno do zaznaczenia
    bisect(base, natural_planes(BLOCK_X))
# otwarta połowa: bez ścian w płaszczyźnie symetrii X = 0
bm = bmesh.new()
bm.from_mesh(base.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces
                           if all(abs(v.co.x) < 1e-4 for v in f.verts)], context='FACES')
bm.to_mesh(base.data)
bm.free()
to_scene(base)
base.name = "Cube"
base.data.name = "Cube"

mir = base.modifiers.new("Mirror", 'MIRROR')
mir.use_axis = (True, False, False)
mir.use_clip = True
mir.use_mirror_merge = True
mir.merge_threshold = 0.01                   # Merge 0.01 m (wg instrukcji)

# 4.3.3 (2) cylinder fi50 x 40 -> Dimensions 0.5 x 0.5 x 0.4 m, Z = 0.7 m
cyl = prim_cylinder(col_model, CYL_D / 2, CYL_Y0, CYL_Y0 + CYL_L, CYL_Z)    # "Cylinder"

# ---------------------------------------------------------------------------
# Zadanie 4.4 - otwory i wgłębienia: kolekcja "wycinanie" (niewidoczna)
# ---------------------------------------------------------------------------
c_hole = prim_cylinder(col_cuts, HOLE_D / 2, CYL_Y0 - 5, CYL_Y0 + CYL_L + 5, CYL_Z)   # .001 fi20
c_tab = prim_cylinder(col_cuts, TAB_HOLE_D / 2, -5, TAB_T + 5, TAB_HOLE_Z)            # .002 fi15
c_cb = prim_cylinder(col_cuts, CB_D / 2, CYL_Y0 - 1, CYL_Y0 + CB_DEPTH, CYL_Z)        # .003 fi30x6
# pogłębienie obustronne: Mirror względem środka cylindra (oś lokalna Z cylindra = Y świata)
m = c_cb.modifiers.new("Mirror", 'MIRROR')
m.use_axis = (False, False, True)
m.mirror_object = cyl

# 4.4.1 Boolean Difference, operand: kolekcja "wycinanie"
for ob in (cyl, base):
    b = ob.modifiers.new("Boolean", 'BOOLEAN')
    b.operation = 'DIFFERENCE'
    b.operand_type = 'COLLECTION'
    b.collection = col_cuts
    b.solver = 'EXACT'

# ---------------------------------------------------------------------------
# Zadanie 4.5 - Duplicate Collection "obiekt_mods" -> "obiekt_final"
# ---------------------------------------------------------------------------
col_final = bpy.data.collections.new("obiekt_final")
scene.collection.children.link(col_final)
col_f_model = bpy.data.collections.new("model")          # -> "model.001"
col_f_cuts = bpy.data.collections.new("wycinanie")       # -> "wycinanie.001"
col_final.children.link(col_f_model)
col_final.children.link(col_f_cuts)

dup = {}
for src, dst in ((col_model, col_f_model), (col_cuts, col_f_cuts)):
    for ob in src.objects:
        c = ob.copy()                                    # Cube.001, Cylinder.004 ...
        c.data = ob.data.copy()
        dst.objects.link(c)
        dup[ob] = c
dup[c_cb].modifiers["Mirror"].mirror_object = dup[cyl]
for k in (cyl, base):
    dup[k].modifiers["Boolean"].collection = col_f_cuts

# 4.5.3 apply: najpierw obiekty "wycinanie", potem cylinder, potem obiekt bazowy
for k in (c_hole, c_tab, c_cb):
    apply_all_modifiers(dup[k])
apply_all_modifiers(dup[cyl])
apply_all_modifiers(dup[base])

# Boolean > Union obiektu bazowego i cylindra -> apply
final = dup[base]
u = final.modifiers.new("Boolean", 'BOOLEAN')
u.operation = 'UNION'
u.object = dup[cyl]
u.solver = 'EXACT'
apply_all_modifiers(final)
cleanup(final, dist=1e-6)
if not SMOOTH:
    # te same pętle na granicach bloków po obu stronach; cylinder nie jest cięty
    bisect(final, [((K * co[0], K * co[1], K * (co[2] + ZO)), no)
                   for co, no in natural_planes([-x for x in BLOCK_X] + [0] + BLOCK_X)],
           skip=on_cylinder)
    # usunięcie ukośnych krawędzi "mostków" po Booleanie (np. otwór -> brzeg ściany)
    bm = bmesh.new()
    bm.from_mesh(final.data)
    def axial(e):
        d = (e.verts[1].co - e.verts[0].co).normalized()
        return max(abs(d.x), abs(d.y), abs(d.z)) > 0.9999
    bridges = [e for e in bm.edges if len(e.link_faces) == 2 and not axial(e)
               and e.link_faces[0] is not e.link_faces[1]
               and e.link_faces[0].normal.angle(e.link_faces[1].normal, 1) < math.radians(0.5)]
    bmesh.ops.dissolve_edges(bm, edges=bridges, use_verts=True)
    bm.to_mesh(final.data)
    bm.free()
for p in final.data.polygons:
    p.use_smooth = False
if SMOOTH:
    # wygładzenie: krzywizny gładkie, ostre krawędzie (> 30 st.) zostają ostre
    for ob in (final, base, cyl):
        for o in bpy.context.view_layer.objects:
            o.select_set(o == ob)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))

# materiał
mat = bpy.data.materials.new("stal")
mat.diffuse_color = (0.55, 0.6, 0.68, 1)
for ob in (final, base, cyl, dup[cyl]):
    ob.data.materials.append(mat)

# widoczność (oczka w Outlinerze): wycinanie ukryte, obiekt_mods ukryty,
# pracujemy na obiekt_final; cylinder użyty w Union ukryty
lc("wycinanie").hide_viewport = True
lc("wycinanie.001").hide_viewport = True
col_cuts.hide_render = True
col_f_cuts.hide_render = True
lc("obiekt_mods").hide_viewport = True
col_mods.hide_render = True
dup[cyl].hide_set(True)
dup[cyl].hide_render = True

# ---------------------------------------------------------------------------
# Kamera, światło, widok: 3D Viewport + Image Editor z blueprintem (zad. 4.1)
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.5
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (2.6, -2.6, 2.3)
cam.rotation_euler = (Vector((0, 0.35, 0.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam)
scene.camera = cam
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(30))
scene.collection.objects.link(sun)

deps = bpy.context.evaluated_depsgraph_get()
bm = bmesh.new()
bm.from_mesh(final.data)
print(f"[lab4] {final.name}: {len(bm.verts)} v, {len(bm.faces)} f, "
      f"non-manifold edges: {sum(1 for e in bm.edges if not e.is_manifold)}, "
      f"volume: {bm.calc_volume() / K ** 3:.1f} mm3")
bm.free()

for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = blueprint
        if area.type == 'VIEW_3D':
            ov = area.spaces.active.overlay
            ov.show_wireframes = not SMOOTH
            ov.wireframe_threshold = 1.0
            ov.show_extra_edge_length = not SMOOTH

out_dir = os.path.join(HERE, "output")
os.makedirs(out_dir, exist_ok=True)
for o in bpy.context.view_layer.objects:
    o.select_set(o == final)
bpy.context.view_layer.objects.active = final
bpy.ops.wm.obj_export(filepath=os.path.join(out_dir, f"wspornik_final_{VARIANT}.obj"),
                      export_selected_objects=True, export_materials=False)
bpy.ops.wm.stl_export(filepath=os.path.join(out_dir, f"wspornik_final_{VARIANT}.stl"),
                      export_selected_objects=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, f"projekt4_wspornik_{VARIANT}.blend"),
                            compress=True)
print("[lab4] zapisano", out_dir)
