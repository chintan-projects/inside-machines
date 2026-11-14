from explainer_studio.scene_kit import *
from shared.series import card,TEAL,GOLD,text


class Cover(CoverScene):
    title = "One choice leads\nto the next"
    def get_visual(self) -> VGroup:
        inputs=card('The / sky / is',width=4).move_to([-1.2,0.7,0])
        chosen=card('blue',GOLD).move_to([2.1,-0.8,0])
        route=get_curved_arrow(chosen.get_left(),inputs.get_bottom(),angle=-PI/2,color=TEAL,stroke_width=4)
        return VGroup(inputs,chosen,route,text('chosen → input → processed',28,TEAL).move_to([0,-2,0]))
