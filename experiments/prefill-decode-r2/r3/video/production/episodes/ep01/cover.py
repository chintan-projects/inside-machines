from explainer_studio.scene_kit import *
from shared.series import chip, TEAL, GOLD, words


class Cover(CoverScene):
    title = "One choice leads\nto the next."

    def get_visual(self) -> VGroup:
        prompt = chip("The / sky / is", width=4).move_to([-2.8,0,0])
        blue = chip("blue", GOLD).move_to([1.5,0,0])
        route = get_curved_arrow(blue.get_bottom(),prompt.get_bottom(),angle=-PI/1.7,color=TEAL,stroke_width=5)
        label = words("chosen → back in → processed",30,TEAL).move_to([0,-1.8,0])
        return VGroup(prompt,blue,route,label)
