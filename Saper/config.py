import arcade

database = "database.db"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Сапер"

cell_size = 50
density = 0.25
time_to_lose = 1.5
on_time_timer = 60

number_colors = {
            0: arcade.color.WHITE,
            1: arcade.color.BLUE,
            2: arcade.color.GREEN,
            3: arcade.color.RED,
            4: arcade.color.DARK_BLUE,
            5: arcade.color.DARK_RED,
            6: arcade.color.CYAN,
            7: arcade.color.DARK_CORAL,
            8: arcade.color.GREEN_YELLOW
        }

def gravity_drag(p):
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92

def smoke_mutator(p):
    p.scale_x *= 1.02
    p.scale_y *= 1.02
    p.alpha = max(0, p.alpha - 2)

SPARK_TEX = [
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
    arcade.make_soft_circle_texture(8, arcade.color.PEACH),
    arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
    arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
]

SMOKE_TEX = arcade.make_soft_circle_texture(20, arcade.color.LIGHT_GRAY, 255, 80)