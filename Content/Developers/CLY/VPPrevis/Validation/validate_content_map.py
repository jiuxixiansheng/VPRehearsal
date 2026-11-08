import json
import pathlib
import unreal

target = '/Game/Developers/CLY/Levels/VP_TestContent'
subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world or world.get_path_name().split('.')[0] != target:
    world = None
    assert subsystem.load_level(target), 'Could not independently open content map'
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
levels = [level.get_outer().get_path_name() for level in unreal.EditorLevelUtils.get_levels(world)]
assert len(levels) == 1, levels
assert all('/VP_TestContent.' in actor.get_path_name() for actor in actors)
by_label = {actor.get_actor_label(): actor for actor in actors}
environment = ['DirectionalLight', 'SkyAtmosphere', 'SkyLight',
               'ExponentialHeightFog', 'VolumetricCloud', 'SM_SkySphere']
assert all(label in by_label for label in environment)
assert 'VP_Content_EditView' in by_label
assert not any(label.startswith('VP_Studio_') for label in by_label)
sun = by_label['DirectionalLight'].light_component
assert sun.lighting_channels.channel1 and not sun.lighting_channels.channel0
report = {
    'success': True,
    'world': world.get_path_name(),
    'loaded_levels': levels,
    'environment_actors': environment,
    'sun_intensity': sun.intensity,
    'sky_intensity': by_label['SkyLight'].light_component.intensity,
    'sun_channel': 1,
    'editor_camera': 'VP_Content_EditView',
    'actor_count': len(actors),
    'studio_actors_loaded': False,
}
output = pathlib.Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())) / 'Content/Developers/CLY/VPPrevis/Validation/standalone-content-result.json'
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
unreal.log('VP_STANDALONE_CONTENT_PASS ' + json.dumps(report))
