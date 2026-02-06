import arcade
from config import (cell_size, SCREEN_WIDTH, SCREEN_HEIGHT, density, number_colors, time_to_lose,
                    gravity_drag, SPARK_TEX, smoke_mutator, SMOKE_TEX)
import random
from arcade.particles import FadeParticle, Emitter, EmitBurst


class Big_map(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        self.rows = (SCREEN_HEIGHT * 2) // cell_size
        self.cols = (SCREEN_WIDTH * 2) // cell_size

        self.world_width = SCREEN_WIDTH * 2
        self.world_height = SCREEN_HEIGHT * 2

        self.time = 0
        self.keys_pressed = set()
        self.speed = 300

        self.boom = arcade.load_sound("sounds/BOOM.wav")

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.mine_sprites = arcade.SpriteList()
        self.flag_sprites = arcade.SpriteList()
        self.camera_list = arcade.SpriteList()
        self.emitters = []

        self.camera = arcade.Sprite("images/flag.png")
        self.camera.scale = cell_size / self.camera.width
        self.camera.center_x = self.cols * cell_size // 2
        self.camera.center_y = self.rows * cell_size // 2
        self.camera.visible = False
        self.camera_list.append(self.camera)

        self.game_over = False
        self.game_win = False

        self.mines_count = 0
        self.cells_open = 0
        self.cells = self.rows * self.cols

        self.grid = self.create_grid()
        self.create_sprites()
        self.world_camera.position = (self.camera.center_x - SCREEN_WIDTH // 2,
                                      self.camera.center_y - SCREEN_HEIGHT // 2)

    def create_sprites(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * cell_size + cell_size // 2
                y = row * cell_size + cell_size // 2

                if self.grid[row][col][0] == "b":
                    mine = arcade.Sprite("images/bomb.png")
                    mine.scale = cell_size / mine.width
                    mine.center_y = y
                    mine.center_x = x
                    mine.visible = False
                    self.mine_sprites.append(mine)

                flag = arcade.Sprite("images/flag.png")
                flag.center_x = x
                flag.center_y = y
                flag.visible = False
                flag.scale = (cell_size - 5) / flag.width
                self.flag_sprites.append(flag)

    def create_grid(self):
        grid = [[[0, 0] for _ in range(self.cols)] for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                grid[i][j] = ["b", 0] if random.random() < density else [0, 0]
                if grid[i][j][0] == "b":
                    self.mines_count += 1

        for r in range(self.rows // 2 - 3, self.rows // 2 + 2):
            for c in range(self.cols // 2 - 3, self.cols // 2):
                if grid[r][c][0] == "b":
                    self.mines_count -= 1
                grid[r][c][1] = 1
                grid[r][c][0] = 0
                self.cells_open += 1

        for i in range(self.rows):
            for j in range(self.cols):
                if grid[i][j][0] != "b":
                    bombs = 0
                    for row in range(max(0, i - 1), min(self.rows, i + 2)):
                        for col in range(max(0, j - 1), min(self.cols, j + 2)):
                            if grid[row][col][0] == "b":
                                bombs += 1
                    grid[i][j][0] = bombs
        return grid

    def mine_boom(self, x, y, count=80):
        self.boom.play()

        self.emitters.append(Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(SPARK_TEX),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.1),
                start_alpha=255, end_alpha=0,
                scale=random.uniform(0.35, 0.6),
                mutation_callback=gravity_drag,
            ),
        ))

        self.emitters.append(Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(12),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=SMOKE_TEX,
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 0.6),
                lifetime=random.uniform(1.5, 2.5),
                start_alpha=200, end_alpha=0,
                scale=random.uniform(0.6, 0.9),
                mutation_callback=smoke_mutator,
            ),
        ))

    def on_draw(self):
        self.clear()

        # Используем мировую камеру
        self.world_camera.use()

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * cell_size + cell_size // 2
                y = row * cell_size + cell_size // 2

                if self.grid[row][col][1] == 0:
                    arcade.draw_rect_filled(arcade.rect.XYWH(x, y,
                                                             cell_size - 2,
                                                             cell_size - 2),
                                            arcade.color.WHITE)
                else:
                    arcade.draw_rect_filled(arcade.rect.XYWH(x, y,
                                                             cell_size - 2,
                                                             cell_size - 2),
                                            arcade.color.DARK_GRAY)
                    if self.grid[row][col][0] != "b":
                        color = number_colors[self.grid[row][col][0]]
                        arcade.draw_text(str(self.grid[row][col][0]), x - 10, y - 10, color, cell_size // 2)

                arcade.draw_rect_outline(arcade.rect.XYWH(x, y,
                                                          cell_size - 2,
                                                          cell_size - 2),
                                         arcade.color.BLACK, 1)

        self.mine_sprites.draw()
        self.flag_sprites.draw()
        self.camera_list.draw()

        for e in self.emitters:
            e.draw()

        self.gui_camera.use()

        arcade.draw_text(f'''Управление: WASD/Стрелки - движение\n
                            Всего бомб - {self.mines_count}''',
                         10, SCREEN_HEIGHT - 30,
                         arcade.color.BLACK, 14)

    def on_update(self, delta_time):
        if self.game_over:
            from gui import LoseGame
            self.time += delta_time
            if self.time >= time_to_lose:
                self.window.show_view(LoseGame())
                return

        if (self.cells - self.cells_open) == self.mines_count:
            from gui import WinGame
            self.window.show_view(WinGame())
            return

        for emitter in self.emitters[:]:
            emitter.update()
            if emitter.can_reap():
                self.emitters.remove(emitter)

        move_speed = self.speed * delta_time

        new_x = self.camera.center_x
        new_y = self.camera.center_y

        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            new_x -= move_speed
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            new_x += move_speed
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            new_y += move_speed
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            new_y -= self.speed * delta_time

        if new_x < 0:
            new_x = 0
        elif new_x > SCREEN_WIDTH * 2:
            new_x = SCREEN_WIDTH * 2

        if new_y < 0:
            new_y = 0
        elif new_y > SCREEN_HEIGHT * 2:
            new_y = SCREEN_HEIGHT * 2

        self.camera.center_x = new_x
        self.camera.center_y = new_y

        self.camera.update()

        cam_x, cam_y = self.world_camera.position

        target_x = self.camera.center_x
        target_y = self.camera.center_y

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(self.world_width - half_w, target_x))
        target_y = max(half_h, min(self.world_height - half_h, target_y))

        # Плавно к цели, аналог arcade.math.lerp_2d, но руками
        smooth_x = (1 - 0.1) * cam_x + 0.1 * target_x
        smooth_y = (1 - 0.1) * cam_y + 0.1 * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

    def on_mouse_press(self, x, y, button, modifiers):
        world_x = x + (self.world_camera.position[0] - SCREEN_WIDTH // 2)
        world_y = y + (self.world_camera.position[1] - SCREEN_HEIGHT // 2)

        col = int(world_x // cell_size)
        row = int(world_y // cell_size)

        x = col * cell_size + cell_size // 2
        y = row * cell_size + cell_size // 2

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.grid[row][col][0] == "b":
                mines = arcade.get_sprites_at_point((x, y), self.mine_sprites)
                for mine in mines:
                    mine.visible = True
                    self.mine_boom(mine.center_x, mine.center_y)
                self.game_over = True

            if self.grid[row][col][1] == 0 and self.grid[row][col][0] != "b":
                self.grid[row][col][1] = 1
                self.cells_open += 1

        if button == arcade.MOUSE_BUTTON_RIGHT:
            flags = arcade.get_sprites_at_point((x, y), self.flag_sprites)
            for flag in flags:
                if flag.visible:
                    flag.visible = False
                elif not flag.visible and self.grid[row][col][1] == 0:
                    flag.visible = True

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)