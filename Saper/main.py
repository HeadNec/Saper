import arcade
from gui import MenuView
from database import create_database
from config import SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_TITLE


class SaperMainWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        create_database()
        self.show_view(MenuView())

def main():
    window = SaperMainWindow()
    arcade.run()

if __name__ == "__main__":
    main()