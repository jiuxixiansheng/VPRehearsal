"""Build the calibrated YuYan stage in the open level using Unreal Editor Python.

Run phases with run_phase(name); no unrelated actors or assets are removed.
All geometry is in centimetres. Pixel coordinates trace the supplied floor plan.
Explicit drawing dimensions override pixel measurements for the work tables.
"""
import json
import math
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((Path(__file__).with_name('layout.json')).read_text(encoding='utf-8'))
CAL = CONFIG['calibration']
S = CAL['longitudinal_depth_mm'] / 10.0 / (CAL['front_wall_y_px'] - CAL['back_wall_y_px'])
CX = CAL['center_x_px']
CY = (CAL['front_wall_y_px'] + CAL['back_wall_y_px']) / 2.0
H = CONFIG['approved_assumptions']['clear_height_cm']
ASSET_ROOT = CONFIG['asset_root']
TAG = 'YY_VP_STAGE_V1'

PALETTE = {
    'Floor': ([0.115, 0.135, 0.15], 0.72, 0.05),
    'Wall': ([0.58, 0.60, 0.60], 0.86, 0.0),
    'Concrete': ([0.30, 0.33, 0.35], 0.89, 0.0),
    'Acoustic': ([0.045, 0.058, 0.073], 0.96, 0.0),
    'Metal': ([0.07, 0.085, 0.10], 0.38, 0.7),
    'Door': ([0.12, 0.25, 0.28], 0.55, 0.35),
    'Trim': ([0.27, 0.40, 0.43], 0.5, 0.35),
    'Furniture': ([0.36, 0.30, 0.23], 0.62, 0.0),
    'RoomFloor': ([0.20, 0.23, 0.25], 0.8, 0.0),
    'Tape': ([0.18, 0.52, 0.40], 0.9, 0.0),
    'Grid': ([0.17, 0.19, 0.21], 0.85, 0.0),
    'Light': ([1.0, 0.91, 0.74], 0.4, 0.0),
}


def xy(px, py):
    return ((px - CX) * S, (py - CY) * S)


def make_specs():
    groups = {name: [] for name in ('shell', 'annex', 'architecture', 'furniture', 'measurements', 'lighting')}

    def box(group, key, center, size, material='Wall', yaw=0, collision=True):
        groups[group].append(dict(kind='box', key=key, center=list(center), size=list(size), material=material, yaw=yaw, collision=collision))

    def rect(group, key, a, b, height, bottom=0, material='Wall'):
        x, y = xy((a[0]+b[0])/2, (a[1]+b[1])/2)
        box(group, key, (x, y, bottom+height/2), (abs(b[0]-a[0])*S, abs(b[1]-a[1])*S, height), material)

    def line(group, key, a, b, thickness, height, bottom=0, material='Wall', collision=True):
        ax, ay = xy(*a); bx, by = xy(*b)
        box(group, key, ((ax+bx)/2, (ay+by)/2, bottom+height/2), (math.hypot(bx-ax, by-ay), thickness, height), material, math.degrees(math.atan2(by-ay,bx-ax)), collision)

    def opening(group, key, a, b, double=True, swing=1):
        clear_h = CONFIG['approved_assumptions']['door_clear_height_cm']
        line(group, key+'_Lintel', a, b, 25, H-clear_h, clear_h, 'Wall')
        ax, ay = xy(*a); bx, by = xy(*b)
        length = math.hypot(bx-ax, by-ay)
        phi = math.atan2(by-ay, bx-ax)
        for n, (x,y) in enumerate(((ax,ay),(bx,by))):
            box(group, key+'_Jamb_'+str(n), (x,y,clear_h/2), (12,25,clear_h), 'Metal')
        leaves = [(ax,ay,phi,swing)]
        if double: leaves.append((bx,by,phi+math.pi,-swing))
        leaf_length = length/(2 if double else 1)-7
        for n,(hx,hy,angle,direction) in enumerate(leaves):
            angle += math.radians(68*direction)
            box(group, key+'_Leaf_'+str(n), (hx+math.cos(angle)*leaf_length/2,hy+math.sin(angle)*leaf_length/2,(clear_h-5)/2), (leaf_length,5,clear_h-5), 'Door', math.degrees(angle))
            box(group, key+'_Handle_'+str(n), (hx+math.cos(angle)*(leaf_length-14),hy+math.sin(angle)*(leaf_length-14),105), (5,7,22), 'Metal', math.degrees(angle), False)

    def label(key, text, px, py, size=30, z=0.5):
        x,y=xy(px,py)
        groups['measurements'].append(dict(kind='text',key=key,text=text,center=[x,y,z],text_size=size))

    # Ground floor: trace the stepped main-room outline instead of a bounding box.
    rect('shell','Foundation',(39,174),(853,1067),22,-42,'Concrete')
    rect('shell','MainFloor',(68,204),(820,977),20,-20,'Floor')
    rect('shell','BackLeftRecessFloor',(50,204),(68,347),20,-20,'Floor')
    rect('shell','BackRightRecessFloor',(820,204),(839,347),20,-20,'Floor')
    rect('shell','RightEntryFloor',(839,214),(897,322),20,-20,'RoomFloor')
    for n,(a,b) in enumerate([
        ((50,199),(839,199)),
        ((47,199),(47,220)),((47,260),(47,284)),((47,331),(47,347)),
        ((50,347),(68,347)),((65,347),(65,977)),
        ((839,347),(820,347)),((823,347),(823,924)),
        ((844,199),(844,218)),((844,269),(844,347)),
    ]): line('shell','PerimeterWall_%02d'%n,a,b,24,H)
    opening('shell','BackLeftDoorA',(47,220),(47,260),False,-1)
    opening('shell','BackLeftDoorB',(47,284),(47,331),False,-1)
    opening('shell','RightMainEntry',(844,218),(844,269),False,-1)
    for n,(a,b) in enumerate([((844,214),(897,214)),((897,214),(897,322)),((844,322),(897,322))]):
        line('shell','EntryVestibuleWall_%d'%n,a,b,20,H)

    # Foreground: power room, left sound lock, furniture store, right sound lock,
    # and the right-hand circulation/stair enclosure, traced from the drawing.
    rect('annex','ServiceAnnexFloor',(50,977),(838,1058),20,-20,'RoomFloor')
    rect('annex','StairLandingFloor',(820,924),(838,977),20,-20,'RoomFloor')
    walls=[
        ((48,977),(48,1056)),((123,982),(123,1056)),((243,982),(243,1056)),
        ((523,982),(523,1056)),((746,990),(746,1056)),
        ((68,979),(176,979)),((227,979),(285,979)),
        ((407,979),(525,979)),((584,983),(741,983)),
        ((50,1058),(73,1058)),((114,1058),(176,1058)),
        ((227,1058),(640,1058)),((640,1058),(640,1047)),((640,1047),(746,1047)),
        ((643,989),(643,1008)),((643,1036),(643,1047)),
        ((741,982),(741,990)),((741,1039),(741,1058)),
        ((746,1058),(838,1058)),((846,924),(846,1058)),((823,924),(846,924)),
    ]
    for n,(a,b) in enumerate(walls): line('annex','Partition_%02d'%n,a,b,22,H)
    opening('annex','PowerExternalDoor',(73,1058),(114,1058),True,1)
    opening('annex','SoundlockA_InnerDoor',(176,979),(227,979),True,1)
    opening('annex','SoundlockA_OuterDoor',(176,1058),(227,1058),True,1)
    opening('annex','StoreSlidingOpening',(285,979),(407,979),True,1)
    opening('annex','SoundlockB_InnerDoor',(525,983),(584,983),True,1)
    opening('annex','SoundlockB_LobbyDoor',(643,1008),(643,1036),False,-1)
    opening('annex','Lobby_StairDoor',(741,990),(741,1039),False,-1)
    # Stair flight is a vertical placeholder; only its footprint is measured.
    for n in range(8):
        rect('annex','StairTread_%02d'%n,(812,1004-(n+1)*5),(837,1004-n*5),17.5*(n+1),0,'Concrete')

    # Concrete perimeter piers and long wall panels follow plan spacing.
    for n,px in enumerate([47,247,447,645,845]):
        rect('architecture','RearPier_%02d'%n,(px-6,174),(px+6,199),H,0,'Concrete')
    for side,px in [('Left',55),('Right',834)]:
        for n,py in enumerate([355,553,752,953,1054]):
            rect('architecture',side+'Pier_%02d'%n,(px-11,py-6),(px+11,py+6),H,0,'Concrete')
    for n,px in enumerate([246,445,642]):
        rect('architecture','FrontPier_%02d'%n,(px-5,1048),(px+5,1066),H,0,'Concrete')
    # Lower acoustic panels and upper neutral wall bands: elevations are assumed.
    for side,px in [('L',69),('R',819)]:
        for n,py in enumerate(range(374,925,58)):
            rect('architecture','Acoustic_'+side+'_%02d'%n,(px-0.7,py),(px+0.7,py+40),260,60,'Acoustic')
            rect('architecture','UpperPanel_'+side+'_%02d'%n,(px-0.8,py),(px+0.8,py+40),95,390,'Concrete')
    for n,px in enumerate(range(74,811,60)):
        rect('architecture','RearAcoustic_%02d'%n,(px,204),(px+43,205.3),260,60,'Acoustic')
        rect('architecture','RearUpperPanel_%02d'%n,(px,204),(px+43,205.4),95,390,'Concrete')
    # 6 m perimeter datum; no ceiling obscures the overhead layout.
    for n,(a,b) in enumerate([((50,199),(839,199)),((65,347),(65,977)),((823,347),(823,977)),((68,979),(741,979))]):
        line('architecture','RoofEdge_%d'%n,a,b,38,24,H-24,'Metal')
    # 5 m surveying grid is a very subtle surface marking, not geometry variation.
    half_width=(820-68)*S/2
    half_depth=CAL['longitudinal_depth_mm']/20
    for n,x in enumerate(range(-1000,1001,500)):
        box('architecture','SurveyGridX_%d'%n,(x,0,0.04),(0.65,half_depth*2,0.06),'Grid',collision=False)
    for n,y in enumerate(range(-1000,1001,500)):
        box('architecture','SurveyGridY_%d'%n,(0,y,0.045),(half_width*2,0.65,0.06),'Grid',collision=False)

    # Two dimensioned 3000 x 800 mm tables, seven chairs as shown.
    tx,ty=xy(444,272)
    table_h=CONFIG['approved_assumptions']['table_height_cm']
    for n,dx in enumerate([-150,150]):
        box('furniture','Worktable_%d_Top'%n,(tx+dx,ty,table_h-2),(300,80,4),'Furniture')
        for k,(ox,oy) in enumerate([(-132,-28),(-132,28),(132,-28),(132,28)]):
            box('furniture','Worktable_%d_Leg_%d'%(n,k),(tx+dx+ox,ty+oy,(table_h-4)/2),(5,5,table_h-4),'Metal')
        box('furniture','Worktable_%d_Rail'%n,(tx+dx,ty,20),(269,4,5),'Metal')
    for n,dx in enumerate([-255,-170,-85,0,85,170,255]):
        cx=tx+dx; cy=ty-76
        box('furniture','Chair_%d_Seat'%n,(cx,cy,45),(44,44,6),'Acoustic')
        box('furniture','Chair_%d_Back'%n,(cx,cy-20,69),(44,5,44),'Acoustic')
        for k,(ox,oy) in enumerate([(-17,-17),(-17,17),(17,-17),(17,17)]):
            box('furniture','Chair_%d_Leg_%d'%(n,k),(cx+ox,cy+oy,21),(2.8,2.8,42),'Metal')

    # Editor-only measurement aids, positioned from explicit dimension strings.
    anchor_x=half_width-CAL['dimensioned_side_clearance_mm']/10.0
    split_y=-half_depth+CAL['depth_segments_mm'][0]/10.0
    for side,x in [('L',-anchor_x),('R',anchor_x)]:
        for k,(ya,yb) in enumerate([(-half_depth,split_y),(split_y,half_depth)]):
            box('measurements','Longitudinal_'+side+'_%d'%k,(x,(ya+yb)/2,0.12),(1.0,yb-ya,0.12),'Tape',collision=False)
        for k,y in enumerate([-half_depth,split_y,half_depth]):
            box('measurements','Tick_'+side+'_%d'%k,(x,y,0.15),(38,1.5,0.14),'Tape',collision=False)
        for k,(ya,yb,txt) in enumerate([(-half_depth,split_y,'19495 mm'),(split_y,half_depth,'10600 mm')]):
            groups['measurements'].append(dict(kind='text',key='Dimension_'+side+'_%d'%k,text=txt,center=[x+40,(ya+yb)/2,0.5],text_size=25))
    for side,sign in [('L',-1),('R',1)]:
        box('measurements','SideClearance_'+side,(sign*(half_width-168.4),split_y,0.18),(336.8,1.2,0.12),'Tape',collision=False)
        groups['measurements'].append(dict(kind='text',key='ClearanceLabel_'+side,text='3368 mm',center=[sign*(half_width-168.4),split_y+35,0.5],text_size=22))
    label('RoomDepth','CLEAR DEPTH 30.095 m',444,875,34)
    label('RoomWidth','BODY WIDTH %.3f m (PLAN RATIO)'%(2*half_width/100),444,895,25)
    label('TableDimensions','3000 x 800 mm  |  3000 x 800 mm',444,303,25)
    for key,txt,px,py in [('PowerLabel','POWER',85,1015),('SoundA_Label','SOUND LOCK A',181,1018),('StoreLabel','FURNITURE STORE',384,1018),('SoundB_Label','SOUND LOCK B',580,1020),('LobbyLabel','ENTRY',694,1020),('StairLabel','STAIR',792,1034)]:
        label(key,txt,px,py,22)

    # Neutral, practical previs lighting; fixtures are assumed, not CAD dimensions.
    for ix,x in enumerate([-950,0,950]):
        for iy,y in enumerate([-1020,-40,940]):
            key='HouseLight_%d_%d'%(ix,iy)
            box('lighting',key+'_Housing',(x,y,H-34),(180,95,10),'Metal',collision=False)
            box('lighting',key+'_Diffuser',(x,y,H-40),(170,85,2),'Light',collision=False)
            groups['lighting'].append(dict(kind='light',key=key,center=[x,y,H-48],intensity=55000,source_width=170,source_height=85,radius=1800))
    for n,(px,py) in enumerate([(88,1013),(180,1013),(380,1013),(583,1013),(696,1013),(791,1020)]):
        x,y=xy(px,py)
        groups['lighting'].append(dict(kind='light',key='ServiceLight_%d'%n,center=[x,y,H-50],intensity=6500,source_width=70,source_height=40,radius=650))
    groups['lighting'].append(dict(kind='postprocess',key='StageExposure',center=[0,0,300]))
    groups['lighting'].append(dict(kind='start',key='EntryPlayerStart',center=[0,1100,100]))
    # Snap finished wall faces to the calibrated floor extents. Pixel tracing
    # supplies wall topology; the explicit 30095 mm dimension controls clearance.
    for spec in groups['shell']:
        if spec['key']=='PerimeterWall_00':
            spec['center'][1]=-half_depth-12
        elif spec['key']=='PerimeterWall_05':
            spec['center'][0]=-half_width-12
        elif spec['key']=='PerimeterWall_07':
            spec['center'][0]=half_width+12
    front_shift=(half_depth+11)-xy(444,979)[1]
    for spec in groups['annex']:
        if spec['key'] in ('Partition_05','Partition_06','Partition_07') or spec['key'].startswith(('SoundlockA_InnerDoor','StoreSlidingOpening')):
            spec['center'][1]+=front_shift
    return groups


def prepare_materials():
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    out=[]
    for key,(color,roughness,metallic) in PALETTE.items():
        path=ASSET_ROOT+'/Materials/M_YY_'+key
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            out.append(path)
            continue
        material=tools.create_asset('M_YY_'+key,ASSET_ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        assert material, path
        c=mel.create_material_expression(material,unreal.MaterialExpressionConstant3Vector,-420,0)
        c.set_editor_property('constant',unreal.LinearColor(*color,1.0))
        assert mel.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
        for value,prop,y in [(roughness,unreal.MaterialProperty.MP_ROUGHNESS,160),(metallic,unreal.MaterialProperty.MP_METALLIC,300)]:
            e=mel.create_material_expression(material,unreal.MaterialExpressionConstant,-420,y)
            e.set_editor_property('r',value)
            assert mel.connect_material_property(e,'',prop)
        if key=='Light':
            ec=mel.create_material_expression(material,unreal.MaterialExpressionConstant3Vector,-420,450)
            ec.set_editor_property('constant',unreal.LinearColor(4.0,3.7,3.2,1.0))
            assert mel.connect_material_property(ec,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        errors=mel.recompile_material(material)
        assert not errors, list(errors)
        assert unreal.EditorAssetLibrary.save_asset(path)
        out.append(path)
    return out


def run_phase(phase,start=0,count=1000):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert world and world.get_path_name()==CONFIG['target_level'], 'Wrong target level'
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    existing={str(t)[6:]:a for a in actors.get_all_level_actors() for t in a.tags if str(t).startswith('YYKey:')}
    specs=make_specs()[phase]
    cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
    materials={k:unreal.load_asset(ASSET_ROOT+'/Materials/M_YY_'+k) for k in PALETTE}
    done=[]
    for spec in specs[start:start+count]:
        key=spec['key']; kind=spec['kind']; actor=existing.get(key)
        cls={'box':unreal.StaticMeshActor,'text':unreal.TextRenderActor,'light':unreal.RectLight,'postprocess':unreal.PostProcessVolume,'start':unreal.PlayerStart}[kind]
        loc=unreal.Vector(*spec['center'])
        rot=unreal.Rotator(roll=0,pitch=90 if kind=='text' else (-90 if kind=='light' else 0),yaw=90 if kind=='text' else (-90 if kind=='start' else spec.get('yaw',0)))
        if actor is None:
            actor=actors.spawn_actor_from_class(cls,loc,rot)
            assert actor, key
            actor.tags=[TAG,'YYKey:'+key,'YYPhase:'+phase]
        else:
            actor.set_actor_location(loc,False,False)
            actor.set_actor_rotation(rot,False)
        actor.set_actor_label('YY_'+key)
        actor.set_folder_path('YY_Stage/'+{'shell':'01_Shell','annex':'02_ServiceRooms','architecture':'03_Architecture','furniture':'04_Worktables','measurements':'90_Measurements','lighting':'05_Lighting'}[phase])
        if kind=='box':
            comp=actor.static_mesh_component
            comp.set_mobility(unreal.ComponentMobility.STATIC)
            if comp.get_editor_property('static_mesh')!=cube:
                assert comp.set_static_mesh(cube),key
            comp.set_material(0,materials[spec['material']])
            actor.set_actor_scale3d(unreal.Vector(*(v/100.0 for v in spec['size'])))
            actor.set_actor_enable_collision(spec.get('collision',True))
        elif kind=='text':
            comp=actor.get_editor_property('text_render')
            comp.set_text(spec['text'])
            comp.set_world_size(spec['text_size'])
            comp.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            comp.set_text_render_color(unreal.Color(r=130,g=224,b=193,a=255))
            actor.set_actor_enable_collision(False)
        elif kind=='light':
            comp=actor.light_component
            comp.set_mobility(unreal.ComponentMobility.MOVABLE)
            comp.set_intensity_units(unreal.LightUnits.LUMENS)
            comp.set_intensity(spec['intensity'])
            comp.set_source_width(spec['source_width'])
            comp.set_source_height(spec['source_height'])
            comp.set_attenuation_radius(spec['radius'])
            comp.set_light_color(unreal.LinearColor(1.0,0.96,0.89,1.0))
        elif kind=='postprocess':
            actor.set_editor_property('unbound',True)
            settings=actor.get_editor_property('settings')
            for p,v in [('override_auto_exposure_method',True),('auto_exposure_method',unreal.AutoExposureMethod.AEM_HISTOGRAM),('override_auto_exposure_min_brightness',True),('auto_exposure_min_brightness',7.5),('override_auto_exposure_max_brightness',True),('auto_exposure_max_brightness',7.5),('override_auto_exposure_bias',True),('auto_exposure_bias',0.0)]:
                settings.set_editor_property(p,v)
            actor.set_editor_property('settings',settings)
        if phase=='measurements':
            actor.set_editor_property('is_editor_only_actor',True)
            actor.set_actor_hidden_in_game(True)
        done.append(key)
    actors.select_nothing()
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return {'phase':phase,'processed':len(done),'total':len(specs),'next':start+len(done),'complete':start+len(done)>=len(specs)}


def validate():
    subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors={str(t)[6:]:a for a in subsystem.get_all_level_actors() for t in a.tags if str(t).startswith('YYKey:')}
    mismatches=[]; total=0
    for phase,specs in make_specs().items():
        for spec in specs:
            total+=1; actor=actors.get(spec['key'])
            if not actor: mismatches.append('missing:'+spec['key']);continue
            loc=actor.get_actor_location()
            if max(abs(a-b) for a,b in zip((loc.x,loc.y,loc.z),spec['center']))>0.05:
                mismatches.append('location:'+spec['key'])
            if spec['kind']=='box':
                scale=actor.get_actor_scale3d()
                if max(abs(a*100-b) for a,b in zip((scale.x,scale.y,scale.z),spec['size']))>0.05:
                    mismatches.append('size:'+spec['key'])
                assert actor.static_mesh_component.get_material(0),spec['key']
    result={'expected_actors':total,'actual_stage_actors':len(actors),'mismatches':mismatches,
        'main_depth_mm':CAL['longitudinal_depth_mm'],'main_body_width_mm':(820-68)*S*10,
        'back_recess_width_mm':(839-50)*S*10,'clear_height_mm':H*10,
        'table_size_mm':[3000,800],'scale_cm_per_pixel':S,
        'curved_screen_created':False,'level':CONFIG['target_level'],
        'notes':CONFIG['approved_assumptions']}
    out=ROOT/'Saved/VPStage/validation.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
