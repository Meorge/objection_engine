from .beans.img import AnimImg
from .beans.scene import AnimScene

def add_objection_scene(default_character, bg, bench, current_character_name, current_frame, scenes, sound_effects):
    objection = AnimImg("assets/objection.gif")
    # Add the "Objection!" bubble on top of the current background and character
    objection.shake_effect = True
    character = default_character
    scene_objs = list(
        filter(lambda x: x is not None, [bg, character, bench, objection])
    )
    scenes.append(AnimScene(scene_objs, 11, start_frame=current_frame))

    # For a short period of time after the bubble disappears, continue to display
    # the background and character(?)
    bg.shake_effect = False
    if bench is not None:
        bench.shake_effect = False
    character.shake_effect = False
    scene_objs = list(
        filter(lambda x: x is not None, [bg, character, bench])
    )
    scenes.append(AnimScene(scene_objs, 11, start_frame=current_frame))
    sound_effects.append(
        {
            "_type": "objection",
            "character": current_character_name.lower(),
            "length": 22,
        }
    )