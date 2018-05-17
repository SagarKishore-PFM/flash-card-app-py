"""
Created on Saturday, May 7th, 2018
@author: sagar


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
from kivy.uix.label import Label
from kivy.clock import Clock

from random import randrange

from testdatabase import generate_test_stack_database
from helperfuncs import word_description

selected_stack = generate_test_stack_database()[0]

# PRE BETA

# TODO:

# >> Color or add an image to the Yes, No, FrontFace Word Name, Audio Buttons
# >> Change font size for FF Word Name Button
# >> New function needed for word description in BF 2nd row
# >> Remove new words progress bar and label once you are done
# >> Add a button to go back to the stack list screen which also saves state
# >> This means saving the rank_dict and in turn making rank_dict an instance
#     var for Stack class
# >> Maybe add a slide animation??
# >> Figure out how to pass the selected stack across screens
# >> Then use this selected stack in RootFloatLayout
# >> Make the kivy file uniform in terms of linting
# >> Remove the prints and make them to log instead


class RootFloatLayout(FloatLayout):
    rank_dict = {0: set(),
                 1: set(),
                 2: set(),
                 3: set(),
                 4: set(),
                 5: set(),
                 6: set(),
                 -1: set(selected_stack.words), }
    selected_stack = selected_stack
    val = ObjectProperty(rank_dict)
    max_value = NumericProperty(-1)

    def __init__(self, *args, **kwargs):
        super(RootFloatLayout, self).__init__(*args, **kwargs)
        self.max_value = len(selected_stack.words)
        self.AL = AnimatedLayout()
        self.next_word()
        self.add_widget(self.AL)

    def next_word(self, word_rank=None):
        old_word = None
        if(word_rank is not None):
            old_word, new_rank = word_rank
            print(f'old word is {old_word.name} and will be added to rank {new_rank}')
            self.rank_dict[new_rank].add(old_word)
            self.update_progressbars()
        # bottom1 = 'Not yet used1'
        # bottom2 = 'Not yet used2'
        if(len(self.rank_dict[-1]) == 0):
            bottom1, bottom2 = self.updatebottom()

        if(len(self.rank_dict[0]) > 10):
            new_flag = False
            if(len(self.rank_dict[0] < 16)):
                new_flag = True
                bottom1, bottom2 = self.updatebottom(new_flag)

        if(len(self.rank_dict[0]) < 11 and self.rank_dict[-1]):
            bottom1 = -1
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
        self.AL.rank, self.AL.word = (rank, word)

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
            return (self.rank_dict[bottom1].pop(), bottom1)
        else:
            return (self.rank_dict[bottom2].pop(), bottom2)

    def updatebottom(self, new_flag=False):
        rd = self.rank_dict
        if(new_flag):
            lenlist = [len(rd[x]) for x in rd]
        else:
            lenlist = [0] + [len(rd[x]) for x in rd if x != -1]
        print('lenlist is -->', lenlist)
        non_zero_list = []
        for i, x in enumerate(lenlist):
            if(x > 0):
                non_zero_list.append(i-1)
        try:
            bottom1, bottom2 = non_zero_list[:2]
        except ValueError:
            bottom1 = non_zero_list[0]
            bottom2 = None
        print(f'returning --> {bottom1}, {bottom2}')
        return (bottom1, bottom2)

    def update_progressbars(self):
        reviewing_set = self.rank_dict[1].union(self.rank_dict[2],
                                                self.rank_dict[3],
                                                self.rank_dict[4],
                                                self.rank_dict[5])

        self.ids.NewProgressBar.value = len(self.rank_dict[-1])
        self.ids.MasteredProgressBar.value = len(self.rank_dict[6])
        self.ids.ReviewingProgressBar.value = len(reviewing_set)
        self.ids.LearningProgressBar.value = len(self.rank_dict[0])

        self.ids.NewLabel.text = f'New words left {len(self.rank_dict[-1])} / {self.max_value}'
        self.ids.MasteredLabel.text = f'Mastered {len(self.rank_dict[6])} / {self.max_value} words'
        self.ids.ReviewingLabel.text = f'Reviewing {len(reviewing_set)} / {self.max_value} words'
        self.ids.LearningLabel.text = f'Learning {len(self.rank_dict[0])} / {self.max_value} words'


class AnimatedLayout(BoxLayout):
    angle = NumericProperty(0)
    word = ObjectProperty(None)
    rank = NumericProperty(-2)

    def on_word(self, animated_layout, new_word):
        self.draw_front_face()

    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0

    def flip_animation(self):
        anim = Animation(angle=360, duration=0.4, s=1/60, t='in_expo')
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

        bf = BackFace()
        bf.ids.WordNameLabel.text = self.word.name
        bf.ids.WordDescriptionLabel.text = word_description(self.word)
        self.add_widget(bf)

    def yes(self):
        if(self.rank < 0 or self.rank == 6):
            self.parent.next_word((self.word, 6))
        else:
            self.parent.next_word((self.word, self.rank + 1))
        self.slide_animation()

    def no(self):
        self.parent.next_word((self.word, 0))
        self.slide_animation()


class FrontFace(BoxLayout):
    pass


class BackFace(BoxLayout):
    pass


class ProgressLabel(Label):
    occupancy = NumericProperty(0)


class GameScreen(Screen):
    pass


class GameScreenApp(App):

    def build(self):
        return GameScreen()


def rank_text(rank):
    if(rank < 0):
        return ('New Word', [1, 1, 1, 1])
    if(rank == 0):
        return ('Learning', [1, 0, 0, 1])
    if(0 < rank < 6):
        return ('Reviewing', [1, 1, 0, 1])
    if(rank == 6):
        return ('Mastered', [0, 1, 0, 1])


def main():
    GameScreenApp().run()


if __name__ == '__main__':
    main()
