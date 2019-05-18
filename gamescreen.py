"""
Created on Saturday, May 7th, 2018
@author: Sagar Kishore

The game screen which implements the flash card algorithm and provides the
feature to continue where you left off.
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from random import randrange

from helperfuncs import word_description, play


class GameScreen(Screen):
    Builder.load_string("""
<GameScreen>:
    name: 'game screen'
    id: RootFL

    Button:
        text: 'Go back to Stack List'
        pos_hint: {'x': 0.025, 'y': 0.85}
        size_hint: 0.15, 0.1
        on_release: root.save_changes()

    BoxLayout:
        orientation: 'vertical'
        pos_hint: {'center_x': 0.5, 'y': 0.025}
        size_hint: 0.5, 0.3
        padding: 10, 10
        spacing: 5

        canvas.before:
            Color:
                rgba: 1, 1, 1, 0.1
            Rectangle:
                pos: self.pos
                size: self.size

        GamePFL:
            id: NewPFL

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.1
                Rectangle:
                    pos: self.pos
                    size: self.size
        GamePFL:
            id: MasteredPFL

            canvas.before:
                Color:
                    rgba: 0, 1, 0, 0.1
                Rectangle:
                    pos: self.pos
                    size: self.size

        GamePFL:
            id: ReviewingPFL

            canvas.before:
                Color:
                    rgba: 1, 1, 0, 0.1
                Rectangle:
                    pos: self.pos
                    size: self.size

        GamePFL:
            id: LearningPFL

            canvas.before:
                Color:
                    rgba: 1, 0, 0, 0.1
                Rectangle:
                    pos: self.pos
                    size: self.size

<GamePFL@ProgressFloatLayout>:
    ProgressBar:
        id: PB
        pos_hint: {'center_x': 0.5, 'y': 0.3}
        size_hint: 0.8, 0.05
        # max: root.max_value

    Label:
        id: Lbl
        pos_hint: {'center_x': 0.5, 'y': 0.15}
        font_size: 24
""")
    game_stack = ObjectProperty(None)

    def on_enter(self, *args, **kwargs):
        super(GameScreen, self).__init__(*args, **kwargs)
        self.rank_dict = self.game_stack.rank_dict
        self.max_value = self.game_stack.size
        self.ids.NewPFL.ids.PB.max = self.max_value
        self.ids.MasteredPFL.ids.PB.max = self.max_value
        self.ids.ReviewingPFL.ids.PB.max = self.max_value
        self.ids.LearningPFL.ids.PB.max = self.max_value

        self.AL = AnimatedLayout()
        self.next_word()
        self.add_widget(self.AL)
        self.update_progressbars()

    def on_leave(self):
        self.clear_widgets()

    def next_word(self, word_rank=None):
        old_word = None
        if(word_rank is not None):
            old_word, new_rank = word_rank
            print(f'{old_word.name} will be added to rank {new_rank}')
            self.rank_dict[new_rank].add(old_word)
            self.update_progressbars()

        if(len(self.rank_dict['-1']) == 0):
            bottom1, bottom2 = self.updatebottom()

        if(len(self.rank_dict['0']) > 10):
            new_flag = False
            if(len(self.rank_dict['0']) < 16):
                new_flag = True
            bottom1, bottom2 = self.updatebottom(new_flag)

        if(len(self.rank_dict['0']) < 11 and len(self.rank_dict['-1']) > 0):
            bottom1 = '-1'
            bottom2 = None
        # print('bottom1 is -->', bottom1)
        # print('bottom2 is -->', bottom2)
        word, rank = self.choosefrombottom2(bottom1, bottom2)
        while(old_word == word):
            try:
                new_word, new_rank = self.choosefrombottom2(bottom1, bottom2)
                self.rank_dict[rank].add(word)
                word, rank = new_word, new_rank
            except KeyError:
                pass
        # print(f"sending word {word.name} to AL of rank {rank}")
        self.AL.rank, self.AL.word = (str(rank), word)

        print(f'selected word {word.name} from rank {rank}')
        print('-------------------------------------------------------')
        print('-------------------------------------------------------')
        print('-------------------------------------------------------')
        print('-------------------------------------------------------')

    def choosefrombottom2(self, bottom1, bottom2):
        p = randrange(1, 11)
        print('probability is -->', p)
        print('bottom1 is -->', bottom1)
        print('bottom2 is -->', bottom2)
        if(p < 8 or bottom2 is None):
            return (self.rank_dict[str(bottom1)].pop(), str(bottom1))
        else:
            return (self.rank_dict[str(bottom2)].pop(), str(bottom2))

    def updatebottom(self, new_flag=False):
        rd = self.rank_dict
        if(new_flag):
            lenlist = [len(rd[x]) for x in rd]
        else:
            lenlist = [0] + [len(rd[x]) for x in rd if x != '-1']
        print('lenlist is -->', lenlist)
        non_zero_list = []
        for i, x in enumerate(lenlist):
            if(x > 0):
                non_zero_list.append(str(i - 1))
        try:
            bottom1, bottom2 = non_zero_list[:2]
        except ValueError:
            bottom1 = non_zero_list[0]
            bottom2 = None
        print(f'returning --> {bottom1}, {bottom2}')
        return (bottom1, bottom2)

    def update_progressbars(self):

        reviewing_set = self.rank_dict['1'].union(self.rank_dict['2'],
                                                  self.rank_dict['3'],
                                                  self.rank_dict['4'],
                                                  self.rank_dict['5'])

        self.ids.NewPFL.ids.PB.value = len(self.rank_dict['-1'])
        self.ids.MasteredPFL.ids.PB.value = len(self.rank_dict['6'])
        self.ids.ReviewingPFL.ids.PB.value = len(reviewing_set)
        self.ids.LearningPFL.ids.PB.value = len(self.rank_dict['0'])

        self.ids.NewPFL.ids.Lbl.text = \
            f"New words left {len(self.rank_dict['-1'])} / {self.max_value}"
        self.ids.MasteredPFL.ids.Lbl.text = \
            f"Mastered {len(self.rank_dict['6'])} / {self.max_value} words"
        self.ids.ReviewingPFL.ids.Lbl.text = \
            f"Reviewing {len(reviewing_set)} / {self.max_value} words"
        self.ids.LearningPFL.ids.Lbl.text = \
            f"Learning {len(self.rank_dict['0'])} / {self.max_value} words"

    def save_changes(self):
        self.rank_dict[self.AL.rank].add(self.AL.word)
        self.game_stack.rank_dict = self.rank_dict
        self.manager.current = 'stack screen'


class ProgressFloatLayout(FloatLayout):
    max_value = NumericProperty(-1)


class AnimatedLayout(BoxLayout):
    Builder.load_string("""
<AnimatedLayout>:
    id: AL
    cols: 1
    rows: 1
    canvas.before:
        PushMatrix
        Rectangle:
            pos: self.pos
            size: self.size
        Rotate:
            angle: self.angle
            axis: 0, 1, 0
            origin: self.center
    canvas.after:
        PopMatrix
    pos_hint: {'center_x': 0.5, 'y': 0.7}
    size_hint_x: 0.5
    size_hint_y: 0.3

<FrontFace>:
    cols: 1
    rows: 1
    size_hint: 1, 1
    canvas.before:
        Rectangle:
            pos: root.pos
            size: root.size
    FloatLayout:
        pos: root.pos
        Button:
            id: word_btn
            text: ''
            size_hint: 1, 1
            pos: root.pos
            font_size: 45

        Label:
            id: rank_label
            pos_hint: {'x': 0.35, 'y': 0.2}
            font_size: 28

<BackFace>:
    rows: 3
    cols: 1
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.3, 0.3, 0.3, 1
        Rectangle:
            pos: root.pos
            size: root.size
    RelativeLayout:
        canvas.before:
            Color:
                rgba: 0, 0.51, 0.8, 0.4
            Rectangle:
                pos: FirstBox.pos
                size: FirstBox.size
        orientation: 'horizontal'
        id: FirstBox
        size_hint: 1, 0.2

        Label:
            id: WordNameLabel
            font_size: 48

        Label:
            id: rank_label
            pos_hint: {'x': 0.35, 'y': 0.2}
            font_size: 28

        Button:
            text: 'Audio'
            size_hint: 0.1, 0.2
            pos_hint: {'x': 0.6, 'y': 0.6}
            on_release: root.parent.pronunciation(self)

    BoxLayout:
        canvas.before:
            Color:
                rgba: 0.3, 0.1, 0.8, 0.4
            Rectangle:
                pos: SecondBox.pos
                size: SecondBox.size
        orientation: 'horizontal'
        id: SecondBox
        size_hint: 1, 0.7

        ScrollView:
            id: SV
            height: root.height * 0.9
            Label:
                id: WordDescriptionLabel
                text: 'word desc goes here'
                height: self.texture_size[1]
                size_hint_y: None
                size: SecondBox.size[0] * 0.85, SecondBox.size[1] * 0.85
                text_size: self.width, None
                halign: 'left'
                valign: 'middle'
                markup: True
                padding: 100, 100

    BoxLayout:
        orientation: 'horizontal'
        id: ThirdBox
        size_hint: 1, 0.1
        Button:
            id: YesButton
            text:'Yes'
            on_release: root.parent.yes()
        Button:
            id: NoButton
            text:'No'
            on_release: root.parent.no()
""")

    angle = NumericProperty(0)
    word = ObjectProperty(None)
    rank = StringProperty()

    def on_word(self, animated_layout, new_word):
        self.draw_front_face()

    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0

    def flip_animation(self):
        anim = Animation(angle=360, duration=0.4, s=1 / 60, t='in_expo')
        anim.start(self)
        Clock.schedule_once(self.draw_back_face, anim.duration)  # + 0.1)

    def slide_animation(self):
        pass

    def draw_front_face(self):
        self.pos_hint = {'center_x': 0.5, 'y': 0.75}
        self.size_hint_y = 0.2
        self.clear_widgets()

        self.front_face = FrontFace()
        self.front_face.ids.word_btn.text = self.word.name
        self.front_face.ids.word_btn.on_release = self.flip_animation

        label_text, label_color = rank_text(self.rank)
        self.front_face.ids.rank_label.text = label_text
        self.front_face.ids.rank_label.color = label_color
        self.add_widget(self.front_face, index=0)

    def draw_back_face(self, dt):
        self.size_hint_y = 0.6
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.65}
        self.clear_widgets()

        back_face = BackFace()
        back_face.ids.WordNameLabel.text = self.word.name
        back_face.ids.WordDescriptionLabel.text = word_description(self.word)
        label_text, label_color = rank_text(self.rank)
        back_face.ids.rank_label.text = label_text
        back_face.ids.rank_label.color = label_color
        self.add_widget(back_face)

    def yes(self):
        if(self.rank < '0' or self.rank == '6'):
            self.parent.next_word((self.word, '6'))
        else:
            self.parent.next_word((self.word, str(int(self.rank) + 1)))
        self.slide_animation()
        print(self.parent.rank_dict)

    def no(self):
        self.parent.next_word((self.word, '0'))
        self.slide_animation()
        print(self.parent.rank_dict)

    def pronunciation(self, instance):
        ret = play(self.word)
        if(ret < 0):
            instance.disabled = True


class FrontFace(BoxLayout):
    pass


class BackFace(BoxLayout):
    pass


class ProgressLabel(Label):
    occupancy = NumericProperty(0)


class GameScreenApp(App):

    def build(self):
        return GameScreen()


def rank_text(rank):
    if(rank < '0'):
        return ('New Word', [1, 1, 1, 1])
    if(rank == '0'):
        return ('Learning', [1, 0, 0, 1])
    if('0' < rank < '6'):
        return ('Reviewing', [1, 1, 0, 1])
    if(rank == '6'):
        return ('Mastered', [0, 1, 0, 1])


def main():
    GameScreenApp().run()


if __name__ == '__main__':
    main()
