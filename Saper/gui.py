import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from database import get_wins, get_loses, clear_database, add_lose, add_win
from config import SCREEN_HEIGHT, SCREEN_WIDTH
from pyglet.graphics import Batch


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        self.manager = UIManager()

        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)


    def setup_widgets(self):
        label = UILabel(text="Cапер",
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        from default import Default
        flat_button1 = UIFlatButton(text="Стандартный режим", width=200, height=50, color=arcade.color.BLUE)
        flat_button1.on_click = lambda event: self.window.show_view(Default())
        self.box_layout.add(flat_button1)

        from on_time import On_time
        flat_button2 = UIFlatButton(text="На время", width=200, height=50, color=arcade.color.BLUE)
        flat_button2.on_click = lambda event: self.window.show_view(On_time())
        self.box_layout.add(flat_button2)

        from big import Big_map
        flat_button3 = UIFlatButton(text="Большая сетка", width=200, height=50, color=arcade.color.BLUE)
        flat_button3.on_click = lambda event: self.window.show_view(Big_map())
        self.box_layout.add(flat_button3)

        label = UILabel(text=f'''Победы - {get_wins()[0]}\n
                             Поражения - {get_loses()[0]}''',
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        flat_button4 = UIFlatButton(text="Отчистить победы и поражения", width=200, height=50, color=arcade.color.BLUE)
        flat_button4.on_click = lambda event: clear_database()
        self.box_layout.add(flat_button4)


    def on_draw(self):
        self.clear()
        self.manager.draw()


    def on_hide_view(self):
        self.manager.disable()


    def on_show_view(self):
        self.manager.enable()

    def on_update(self, delta_time):
        self.manager.on_update(delta_time)


class WinGame(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_GREEN)
        add_win()

        self.batch = Batch()
        self.main_text = arcade.Text("Вы выйграли", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                                     arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)

        self.space_text = arcade.Text("Нажми SPACE, чтобы вернуться в главное меню", SCREEN_WIDTH / 2,
                                      SCREEN_HEIGHT / 2 - 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.window.show_view(MenuView())

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_update(self, delta_time):
        pass


class LoseGame(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_RED)
        add_lose()

        self.batch = Batch()
        self.main_text = arcade.Text("Вы проиграли", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                                     arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)

        self.space_text = arcade.Text("Нажми SPACE, чтобы вернуться в главное меню", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.window.show_view(MenuView())

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_update(self, delta_time):
        pass