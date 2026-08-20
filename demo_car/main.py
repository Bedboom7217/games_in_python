import pygame
import sys, os
import random, time
import sprites
import math

pygame.init()
WINDOW = (960, 720)
VISIBLE_LENGTH = 32 # how many blocks ahead of the car are sprites spawned at
FPS = 60
scaled_sprites = {}
INSTRUCTIONS = '''I Thought I Could Drive
But maybe not???
This is a game about driving a car on the highway and avoiding obstacles.
It is to demonstrate the illusion of 3D using only 2D sprites
Controls:
Left and Right Arrow Keys to Move
X = A button on a Nintendo Controller, Accelerate
Z = B button on a Nintendo Controller, Brake
Enter = Start Game / Restart Game'''
LEVEL_UP = pygame.event.Event(pygame.USEREVENT + 1)

# Helpers
def parse_bytearray_to_sprite(ba):
    index = 0
    for sprite in ["traffic_cone", "roadblock", "gas", "motel_sprite"]:
        for size in range(1, 33):
            if sprite != "motel_sprite":
                grid = []
                for i in range(size):
                    grid.append([])
                    for j in range(size):
                        if ba[index+3] == 1:
                            grid[-1].append(-1)
                        else:
                            grid[-1].append((chr(ba[index]), chr(ba[index+1]), chr(ba[index+2])))
                        index += 4
                scaled_sprites[(sprite, size)] = grid
            else:
                grid = []
                for i in range(15*size):
                    row = []
                    for j in range(30*size):
                        if ba[index+3] == 1:
                            row.append(-1)
                        else:
                            row.append((chr(ba[index]), chr(ba[index+1]), chr(ba[index+2])))
                        index += 4
                    grid.append(row)
                scaled_sprites[("motel", size)] = grid

class Game:
    def __init__(self):
        self.car_location = WINDOW[0]//2
        self.obstacles = []
        self.score = 0
        self.speed = 5
        self.gas_remain = 100
        self.game_state = "title"
        self.current_bgm = None
        self.movement_direction = None
        self.accelerating = False
        self.braking = False
        self.prev_accelerating = False  # Track previous state to avoid repeating engine sound
        self.distance_traveled = 0  # Track continuous distance for obstacle movement
        self.game_over_played = False  # Track if game over sound was played
        pygame.mixer.init()
        self.sound_path = os.path.join("D:/ethan/games_in_python/demo_car/sounds")
        self.sfx_channel_1 = pygame.mixer.Channel(0)
        self.sfx_channel_2 = pygame.mixer.Channel(1)
        self.bgm_channel = pygame.mixer.Channel(2)
        self.prev_bgm = None
        self.level_start_time = time.time()
        self.level = 1
        self.play_sfx("title.mp3") # Intro from Contra for the Nintendo Entertainment System. Nostalgic way to add tension
        self.remaining_time = 100
        self.time_limit = 100
        self.remaining_distance = 700 # Increases each level
        self.level_distance = 700
        self.obstacle_increment_position = 0 # 0-3, obstacles are moved forward every 2 distance units but spawned only every 8
        self.last_increment = 0
        self.last_spawn = 0
        self.spawn_chance = 0.1
        self.time_bonus = 0
        self.final_score = 0
        self.obstacle_list = ["gas", "traffic_cone", "roadblock"]
        self.hard_mode = False
        self.endless_mode = False
        self.selection = None
        self.level_up_state = False
        self.fps = FPS # Used to track frame lagging
        self.prev_frame_time = time.time()
    
    def check_collisions(self):
        for obstacle in self.obstacles:
            if (self.car_location < obstacle[1]*32 < self.car_location+28 or self.car_location < obstacle[1]*32+32 < self.car_location+28) and obstacle[2] in [0, 1]:
                if obstacle[0] == "gas":
                    self.gas_remain = min(100, self.gas_remain + 20)
                    self.obstacles.remove(obstacle)
                    self.play_sfx("gas_collect.mp3")
                elif obstacle[0] == "motel":
                    break
                else:
                    self.game_state = "game_over"
                    self.play_sfx("explosion.mp3")
                    break
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_state == "title":
                        self.game_state = "selection"
                        self.selection = 0
                    elif self.game_state == "selection":
                        self.game_state = "playing"
                        self.selection = None
                    elif self.game_state == "game_over":
                        self.__init__() # reset game
                elif event.key == pygame.K_LEFT:
                    if self.game_state == "playing":
                        self.movement_direction = "left"
                    elif self.game_state == "selection":
                        if self.selection == 0:
                            self.hard_mode = not self.hard_mode
                        else:
                            self.endless_mode = not self.endless_mode
                elif event.key == pygame.K_RIGHT:
                    if self.game_state == "playing":
                        self.movement_direction = "right"
                    elif self.game_state == "selection":
                        if self.selection == 0:
                            self.hard_mode = not self.hard_mode
                        else:
                            self.endless_mode = not self.endless_mode
                elif event.key == pygame.K_x:
                    if self.game_state == "playing":
                        self.accelerating = True
                    elif self.game_state == "selection":
                        self.selection = (self.selection + 1) % 2
                elif event.key == pygame.K_z:
                    if self.game_state == "playing":
                        self.braking = True
                    elif self.game_state == "selection":
                        self.selection = (self.selection - 1) % 2
            elif event.type == pygame.KEYUP:
                # On key release, consult current keyboard state to avoid
                # leaving `movement_direction` stuck when multiple keys
                # were pressed or events arrive out-of-order.
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                        self.movement_direction = "left"
                    elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                        self.movement_direction = "right"
                    else:
                        self.movement_direction = None
                elif event.key == pygame.K_x:
                    self.accelerating = False
                elif event.key == pygame.K_z:
                    self.braking = False
    
    def handle_movement(self):
        if self.movement_direction == "left":
            self.car_location = max(0, self.car_location - (8*FPS//self.fps))
        elif self.movement_direction == "right":
            self.car_location = min(WINDOW[0] - 24, self.car_location + (8*FPS//self.fps))
        if self.accelerating:
            self.speed = min(20, self.speed + (0.1*FPS/self.fps))
            # Only play engine sound when acceleration starts, not every frame
            if not self.prev_accelerating:
                self.play_sfx("engine.mp3")
        elif self.braking:
            self.speed = max(0, self.speed - (0.1*FPS/self.fps))
        else:
            self.speed = max(5, self.speed - (0.02*FPS/self.fps))
        self.prev_accelerating = self.accelerating
    
    def spawn_obstacles(self):
        if not self.endless_mode and int(self.remaining_distance) == 128: # Motel
            # Format: [type, lane, spawn_distance]
            self.obstacles.append(["motel", 1, 31])
        else:
            availible_lanes = list(range(1, 31))
            while random.random() < self.spawn_chance:
                try:
                    lane = random.choice(availible_lanes)
                    availible_lanes.remove(lane)
                except IndexError:
                    break
                t = random.choice(self.obstacle_list)
                # Obstacles spawn at the current level_distance milestone
                self.obstacles.append([t, lane, 31])
                if len(self.obstacles) > 200:
                    break
    
    def play_bgm(self):
        if self.game_state == "title" or self.game_state == "selection":
            bgm = None
        elif self.game_state == "playing" and self.gas_remain > 25 and (self.endless_mode or time.time() - self.level_start_time < 70 and self.level < 17):
            bgm = "game_music.mp3"
        elif self.game_state == "playing" and not self.endless_mode and self.level == 17:
            bgm = "last_level.mp3"
        elif self.game_state == "playing": # Low gas or less than 40 seconds left
            bgm = "tension.mp3"
        elif self.game_state == "game_over" and not self.endless_mode and self.level > 17:
            bgm = "ending.mp3"
        else:
            bgm = None
        if bgm != self.prev_bgm and bgm is not None:
            self.bgm_channel.play(pygame.mixer.Sound(os.path.join(self.sound_path, bgm)), loops=-1)
            self.prev_bgm = bgm
        elif bgm == None:
            self.bgm_channel.stop()
            self.prev_bgm = None
        
    def play_sfx(self, sfx):
        # Cache Sound objects to avoid repeated disk I/O and construction stalls
        if not hasattr(self, 'sfx_cache'):
            self.sfx_cache = {}
        if sfx not in self.sfx_cache:
            path = os.path.join(self.sound_path, sfx)
            try:
                self.sfx_cache[sfx] = pygame.mixer.Sound(path)
            except Exception:
                return
        if sfx == "engine.mp3":
            self.sfx_channel_2.play(self.sfx_cache[sfx])
        else:
            self.sfx_channel_1.play(self.sfx_cache[sfx])
    
    def level_up(self):
        self.level += 1
        self.level_up_state = True
        if self.level == 18:
            self.game_state = "game_over"
        self.level_distance += 100
        self.remaining_distance = self.level_distance
        self.level_start_time = time.time()
        self.obstacles = []
        self.prev_accelerating = False
        self.distance_traveled = 0
        self.game_over_played = False
        if not self.hard_mode:
            self.spawn_chance = min(0.8, self.spawn_chance + 0.05)
        else:
            self.spawn_chance = min(0.975, self.spawn_chance + 0.1)
        if self.level == 17:
            self.obstacle_list.remove("gas") # Last level! No more gas to stop people that keep holding the accelerate button

    def calculate_final_score(self):
        if not self.endless_mode:
            score = (self.level-1) * 200
        else:
            score = 0
        score += int(self.gas_remain) * 2
        if not self.endless_mode:
            score += (int(self.remaining_distance) - int(self.level_distance)) * 3
            score += self.time_bonus * 5
        else:
            score += int(self.distance_traveled) * 3
        return score

    def update(self):
        self.handle_input()
        self.play_bgm()
        if self.game_state == "title" or self.game_state == "selection":
            self.level_start_time = time.time() # Reset level timer so it doesn't start until the player starts playing
        if self.game_state == "selection":
            if self.hard_mode and not self.endless_mode:
                self.spawn_chance = 0.3
            elif self.hard_mode and self.endless_mode:
                self.spawn_chance = 0.6
            if self.endless_mode:
                self.remaining_distance = None
                self.level_distance = None
                self.level = None
                self.level_start_time = None
            elif not self.endless_mode:
                self.remaining_distance = 700
                self.level_distance = 700
                self.level = 1
                self.level_start_time = time.time()
            if not self.hard_mode:
                self.spawn_chance = 0.1
        elif self.game_state == "game_over":
            if not self.game_over_played:
                self.game_over_played = True
                self.final_score = self.calculate_final_score()
        elif self.game_state == "playing":
            self.handle_movement()
            self.check_collisions()
            if not self.endless_mode and not int(self.remaining_distance) % 4:
                self.spawn_obstacles()
            elif self.endless_mode and not int(self.distance_traveled) % 4:
                self.spawn_obstacles()
            if not self.endless_mode:
                if not int(self.remaining_distance) % 2 and int(self.remaining_distance) != self.last_increment:
                    self.obstacle_increment_position = (self.obstacle_increment_position + 1) % 4
                    self.last_increment = int(self.remaining_distance)
                self.remaining_distance -= self.speed / self.fps
                if self.remaining_distance <= 0:
                    self.level_up()
                    self.play_sfx("level_clear.mp3") # Sound from the Legend of Zelda II
                else:
                    self.level_up_state = False
                if self.gas_remain == 0 or time.time() - self.level_start_time > self.time_limit:
                    self.game_state = "game_over"
                    self.game_over_played = False
                    self.play_sfx("game_over.mp3")
            else:
                if not int(self.distance_traveled) % 2 and int(self.distance_traveled) != self.last_increment:
                    self.obstacle_increment_position = (self.obstacle_increment_position + 1) % 4
                    self.last_increment = int(self.distance_traveled)
                self.distance_traveled += self.speed / self.fps
                if self.gas_remain == 0:
                    self.game_state = "game_over"
                    self.game_over_played = False
                    self.play_sfx("game_over.mp3")
            # Remove obstacles that have passed the player
            if not self.endless_mode:
                # Move all obstacles forward once when we cross an 8-unit boundary.
                # Previously this decremented only the first obstacle because
                # `last_spawn` was updated inside the loop; that made many
                # obstacles appear to never move.
                if not int(self.remaining_distance) % 4 and int(self.remaining_distance) != self.last_spawn:
                    for obstacle in self.obstacles:
                        obstacle[2] -= 1
                    self.last_spawn = int(self.remaining_distance)

                # Remove obstacles that have passed the player
                for obstacle in self.obstacles[:]:
                    if obstacle[2] < 0:
                        self.obstacles.remove(obstacle)
                self.remaining_time = max(0, self.time_limit - (time.time() - self.level_start_time))
            else:
                if not int(self.distance_traveled) % 4 and int(self.distance_traveled) != self.last_spawn:
                    for obstacle in self.obstacles:
                        obstacle[2] -= 1
                    self.last_spawn = int(self.distance_traveled)

                # Remove obstacles that have passed the player
                for obstacle in self.obstacles[:]:
                    if obstacle[2] < 0:
                        self.obstacles.remove(obstacle)
            if self.accelerating:
                self.gas_remain = max(0, self.gas_remain - (0.035*FPS/self.fps))
            else:
                self.gas_remain = max(0, self.gas_remain - (0.015*FPS/self.fps))
            self.fps = 1 / (time.time() - self.prev_frame_time)
            self.prev_frame_time = time.time()

class View:
    def __init__(self, game):
        self.game = game # type = Game
        self.clock = pygame.time.Clock()
        pygame.display.init()
        pygame.display.set_caption("Car Game")
        self.screen = pygame.display.set_mode(WINDOW)
        self.road = ((0, WINDOW[1]), (WINDOW[0], WINDOW[1]), (495, 162), (464, 162)) # A trapezoid to show one-point perspective. 
        #Pygame uses an inverted Cartesian plane where down = more y but left and right are preserved
        self.font = os.path.join("D:/ethan/games_in_python/demo_car/fonts/PressStart2P.ttf")
        pygame.font.init()
        self.scanlines = self.generate_scanlines() # Lines where sprites will be drawn. Precompute to save processing power since they don't change
        self.level_up_time = None
    
    def render_sprite(self, sprite, position):
        surf = pygame.Surface((len(sprite[0]), len(sprite)), pygame.SRCALPHA)
        for y, row in enumerate(sprite):
            for x, pixel in enumerate(row):
                if pixel != -1:
                    try:
                        surf.set_at((x, y), (ord(pixel[0]), ord(pixel[1]), ord(pixel[2])))
                    except TypeError:
                        surf.set_at((x, y), (pixel[0], pixel[1], pixel[2]))
        self.screen.blit(surf, position)

    def generate_scanlines(self):
        scanlines = {}
        prev_distance = 32
        for spawn_distance in range(VISIBLE_LENGTH):
            for increment in range(4):
                y = prev_distance
                if not spawn_distance % 4:
                    prev_distance += (32-spawn_distance) // 4
                elif increment in [1, 2, 3] and increment % 4 == 3:
                    prev_distance += (32-spawn_distance) // 4 + 1
                elif increment in [0, 1]:
                    prev_distance += (32-spawn_distance) // 4
                elif increment in [2, 3] and not increment % 2:
                    prev_distance += (32-spawn_distance) // 4 + 1
                for lane in range(1, 31):
                    if lane < 16:
                        x = 480 - (16-lane)*(32-spawn_distance)
                    elif lane >= 16:
                        x = 480 + (32-spawn_distance)*(lane-16)
                    scanlines[(spawn_distance, increment, lane)] = (x, y)
        return scanlines
    
    def render_title(self):
        self.screen.fill((0, 0, 0))
        title_font = pygame.font.Font(self.font, 48)
        title_text = title_font.render("Highway Havoc", True, (255, 255, 255))
        instruction_font = pygame.font.Font(self.font, 24)
        instruction_text = instruction_font.render("Press Start", True, (255, 255, 255))
        self.screen.blit(title_text, (WINDOW[0]//2 - title_text.get_width()//2, WINDOW[1]//3))
        self.screen.blit(instruction_text, (WINDOW[0]//2 - instruction_text.get_width()//2, WINDOW[1]//2))
    
    def render_selection(self):
        self.screen.fill((0, 0, 0))
        option_font = pygame.font.Font(self.font, 32)
        option_1_text = option_font.render("Difficulty", True, (255, 255, 255))
        difficulty_text = option_font.render("Hard" if self.game.hard_mode else "Normal", True, (255, 255, 255))
        option_2_text = option_font.render("Mode", True, (255, 255, 255))
        mode_text = option_font.render("Endless" if self.game.endless_mode else "Levels", True, (255, 255, 255))
        self.screen.blit(option_1_text, (WINDOW[0]//2 - option_1_text.get_width()//2, WINDOW[1]//3))
        self.screen.blit(difficulty_text, (WINDOW[0]//2 - difficulty_text.get_width()//2, WINDOW[1]//3 + 40))
        self.screen.blit(option_2_text, (WINDOW[0]//2 - option_2_text.get_width()//2, WINDOW[1]//2))
        self.screen.blit(mode_text, (WINDOW[0]//2 - mode_text.get_width()//2, WINDOW[1]//2 + 40))
        if self.game.selection == 0:
            pygame.draw.rect(self.screen, (255, 255, 255), (WINDOW[0]//2 - difficulty_text.get_width()//2 - 10, WINDOW[1]//3 + 40 - 5, difficulty_text.get_width() + 20, difficulty_text.get_height() + 10), 2)
        elif self.game.selection == 1:
            pygame.draw.rect(self.screen, (255, 255, 255), (WINDOW[0]//2 - mode_text.get_width()//2 - 10, WINDOW[1]//2 + 40 - 5, mode_text.get_width() + 20, mode_text.get_height() + 10), 2)
    
    def render_level_up(self):
        level_font = pygame.font.Font(self.font, 48)
        level_text = level_font.render(f"Level {self.game.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (WINDOW[0]//2 - level_text.get_width()//2, WINDOW[1]//3))

    def render_base_layer(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (50, 255, 50), (0, 192, WINDOW[0], 528)) # Grass
        pygame.draw.polygon(self.screen, (100, 100, 100), self.road) # Road
        
    def render_obstacles(self):
        obstacles = self.game.obstacles
        for obstacle in obstacles:
            name = obstacle[0]
            lane = obstacle[1]
            spawn_distance = obstacle[2]
            render_x = self.scanlines[(spawn_distance, self.game.obstacle_increment_position, lane)][0]
            render_distance = 720 - self.scanlines[(spawn_distance, self.game.obstacle_increment_position, lane)][1]
            sprite = scaled_sprites[(name, 32-spawn_distance)]
            self.render_sprite(sprite, (render_x, render_distance))

    def render_car(self):
        l_sprite = sprites.SPRITES.get("car_left", [])
        r_sprite = sprites.SPRITES.get("car_right", [])
        self.render_sprite(l_sprite, (self.game.car_location-28, WINDOW[1]-20))
        self.render_sprite(r_sprite, (self.game.car_location-12, WINDOW[1]-20))

    def render_hud(self):
        font = pygame.font.Font(self.font, 16)
        level_text = font.render(f"Level: {self.game.level}", True, (255, 255, 255))
        gas_text = font.render(f"Gas: {int(self.game.gas_remain)}%", True, (255, 255, 255))
        fps_text = font.render(f"FPS: {int(self.game.fps)}", True, (255, 255, 255))
        if not self.game.endless_mode:
            time_text = font.render(f"Time: {int(self.game.remaining_time)}s", True, (255, 255, 255))
            distance_text = font.render(f"Distance: {int(self.game.remaining_distance)}m", True, (255, 255, 255))
            self.screen.blit(time_text, (10, 50))
            self.screen.blit(distance_text, (10, 70))
        speed_text = font.render(f"Speed: {int(int(self.game.speed))}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(gas_text, (10, 30))
        self.screen.blit(speed_text, (10, 90))
        self.screen.blit(fps_text, (10, 110))
    
    def render_game_over(self):
        title_font = pygame.font.Font(self.font, 48)
        if self.game.remaining_time <= 0:
            title_text = title_font.render("Time's Up!", True, (255, 255, 255))
        elif self.game.gas_remain <= 0:
            title_text = title_font.render("Out of Gas!", True, (255, 255, 255))
        elif not self.game.endless_mode and self.game.level >= 18:
             title_text = title_font.render("You Win!", True, (255, 255, 255))
        else:
            title_text = title_font.render("Game Over. You crashed!", True, (255, 255, 255))
        instruction_font = pygame.font.Font(self.font, 24)
        instruction_text = instruction_font.render("Press START to retry", True, (255, 255, 255))
        score_text = instruction_font.render(f"Final Score: {self.game.final_score}", True, (255, 255, 255))
        self.screen.blit(title_text, (WINDOW[0]//2 - title_text.get_width()//2, WINDOW[1]//3))
        self.screen.blit(instruction_text, (WINDOW[0]//2 - instruction_text.get_width()//2, WINDOW[1]//2))
        self.screen.blit(score_text, (WINDOW[0]//2 - score_text.get_width()//2, WINDOW[1]//2 + 30))

    def render(self):
        if self.game.game_state == "title":
            self.render_title()
        elif self.game.game_state == "selection":
            self.render_selection()
        else:
            self.render_base_layer()
            self.render_car()
            self.render_obstacles()
            self.render_hud()
            if self.game.game_state == "game_over":
                self.render_game_over() # Things are still rendered under the game over screen, but it adds to the effect and doesn't affect readability
            if self.game.level_up_state == True:
                self.render_level_up()
                self.level_up_time = time.time()
            if self.level_up_time and time.time() - self.level_up_time < 1:
                self.render_level_up()
        pygame.display.flip()
        self.clock.tick(FPS)

def main():
    print(INSTRUCTIONS)
    with open("scaled_sprites.txt", "rb") as file:
        data = file.read()
    # Used to parse the sprite maps back into a dictionary. Will use bytearrays to save space and avoid 100% memory errors.
    parse_bytearray_to_sprite(data)
    game = Game()
    view = View(game)
    while True:
        game.update()
        view.render()


if __name__ == "__main__":
    main()