import pygame
import random
import time
import os, sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
SOUND_EFFECT_FINISHED = pygame.USEREVENT + 1  # Define a custom event

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 220, 110)

FOOD_COLORS = (RED, RED, RED, RED, RED, RED, CYAN, CYAN, YELLOW)

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class SnakeFood:
    def __init__(self, x, y, color):
        self._x = x
        self._y = y
        self._color = color
        self.created_time = time.time()
        self.seconds_until_expiry = random.randint(5, 45)

    def __eq__(self, another_food):
        if self._x == another_food._x and self._y == another_food._y:
            return True

        return False

    def __ne__(self, another_food):
        return not self.__eq__(another_food)
         
    @property
    def coordinate(self):
        return (self._x, self._y)

    @property
    def color(self):
        return self._color

    @property
    def score(self):
        if self._color == RED:
            return 1
        elif self._color == CYAN:
            return 2
        else:
            return 5

    @property
    def sound(self):
        if self._color == RED or self._color == CYAN:
            return "food_sound.mp3"
        else:
            return "yellow_food.mp3"

    def timeout(self):
        return time.time() > self.created_time + self.seconds_until_expiry


class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.in_game = False
        self.food_count = 10
        self.level = 1
        self.draw_level_up = False
        self.frames_to_blit_level_up = 10
        self.timer_duration = 120
        self.reset_game()

    def reset_game(self):
        self.direction = Direction.RIGHT
        self.snake = [(GRID_COUNT // 4, GRID_COUNT // 2)]
        self.foods = []
        self.generate_foods()
        self.score = 0
        self.game_over = False
        self.play_bgm('bgm.mp3', -1)

    def play_bgm(self, music_file_name, loops):
        sounds_folder = 'sounds'
        music_file_path = os.path.join(sounds_folder, music_file_name)
        pygame.mixer.init()
        pygame.mixer.music.stop()
        self._stop_sound_effect()
        pygame.mixer.music.load(music_file_path)
        pygame.mixer.music.play(loops)

    def _stop_sound_effect(self):
        for i in range(pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            if channel.get_busy():
                channel.stop()

    '''
    def start_timer(self, timer_duration, x, y):
        """
        Starts and displays a timer.
        :param timer_duration: duration of the timer in seconds
        :param x: x-coordinate for where to display the timer on the screen
        :param y: y-coordinate for where to display the timer on the screen
        :returns: None
        """
        timer_start = pygame.time.get_ticks()  # Get the current time
        timer_duration_ms = timer_duration * 1000  # Convert seconds to milliseconds
        
        def on_timer_end():
            self.game_over = True
        
        # Main loop to display timer until time runs out
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Calculate elapsed time
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - timer_start
            remaining_time = max(0, (timer_duration_ms - elapsed_time) // 1000)  # Remaining time in seconds

            # Check if timer has expired
            if elapsed_time >= timer_duration_ms:
                on_timer_end()  # Trigger function when timer ends
                running = False  # Stop the timer

            # Convert remaining time into minutes and seconds
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            time_text = f"{minutes:02}:{seconds:02}"

            # Render the timer text
            font = pygame.font.Font('Mojang-Regualar', 28)
            timer_text = font.render(f"Time left: {time_text}", True, WHITE)

            # Draw the timer
            screen.blit(timer_text, (x, y))

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            pygame.time.Clock().tick(60)
    '''

    def level_up(self):
        if self.score >= 10: 
            self.draw_level_up = True
            self.food_count -= 1
            self.level += 1
            self.score = 0
            self.frames_to_blit_level_up = 10
            if len(self.foods) > self.food_count:
                self.foods.pop()
            self._stop_sound_effect()
            self.play_sound('level_up.mp3')
            self.timer_duration -= 10

    def load_font(self, font_name):
        font_folder = 'fonts'
        return os.path.join(font_folder, font_name)

    def title_screen(self):
        # Fonts
        title_font = pygame.font.Font(self.load_font('Mojang-Bold.ttf'), 50)
        start_font = pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 20)
        # Title text and start message
        title_text = title_font.render("Ethan's Snake Game", True, WHITE)
        start_text = start_font.render("Click to Start", True, WHITE)
        # Get rectangles for centering text
        title_rect = title_text.get_rect(center=(400, 200))
        start_rect = start_text.get_rect(center=(400, 400))
        self.screen.blit(title_text, title_rect)  # Draw title text
        self.screen.blit(start_text, start_rect)  # Draw "Click to Start" text
        pygame.display.flip()  # Update the screen


    def stop_game(self):
        self.play_bgm('after_game.mp3', -1)
        self.play_sound('game_over.mp3')

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == SOUND_EFFECT_FINISHED:
                # Resume background music when the sound effect finishes
                pygame.mixer.music.unpause()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.in_game = True
        return True

    def generate_foods(self):
        while len(self.foods) < self.food_count:
            x = random.randint(0, GRID_COUNT-1)
            y = random.randint(0, GRID_COUNT-1)
            food_color = random.choice(FOOD_COLORS)
            food = SnakeFood(x, y, food_color)
            if food.coordinate not in self.snake and food not in self.foods: 
                self.foods.append(food)

    def update(self):
        if self.game_over:
            return

        # Get the head position
        head_x, head_y = self.snake[0]

        # Move the snake
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        else:  # Direction.RIGHT
            new_head = (head_x + 1, head_y)

        # Check for collisions
        if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or
            new_head[1] < 0 or new_head[1] >= GRID_COUNT or
            new_head in self.snake):
            self.game_over = True
            self.stop_game()
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check if food is eaten
        foods_coordinates = [food.coordinate for food in self.foods]
        if new_head in foods_coordinates:
            index = foods_coordinates.index(new_head)
            popped_food = self.foods.pop(index)
            self.score += popped_food.score
            self.play_sound(popped_food.sound)
            self.level_up()
            self.generate_foods()
        else:
            self.snake.pop()

    def play_sound(self, sound_file_name):
        sounds_folder = 'sounds'
        sound_file_path = os.path.join(sounds_folder, sound_file_name)
        pygame.mixer.music.pause()
        sound = pygame.mixer.Sound(sound_file_path)
        channel = sound.play()
        channel.set_endevent(SOUND_EFFECT_FINISHED)

    def draw(self):
        self.screen.fill(BLACK)

        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN,
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                            GRID_SIZE - 1, GRID_SIZE - 1))

        # Draw food
        for food in self.foods:
            if food.timeout():
                self.foods.remove(food)
                continue
            x, y = food.coordinate
            pygame.draw.rect(self.screen, food.color,
                            (x * GRID_SIZE, y * GRID_SIZE,
                             GRID_SIZE - 1, GRID_SIZE - 1))
        if len(self.foods) == 0:
            self.generate_foods()

        # Draw score
        font = pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 28)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        level_text = font.render(f'Level: {self.level}', True, WHITE)
        self.screen.blit(level_text, (10, 50))

        if self.draw_level_up:
            if self.frames_to_blit_level_up == 0:
                self.draw_level_up = False
            else:
                level_up_font = \
                    pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 32)
                level_up_text = level_up_font.render('Level Up!', True, WHITE)
                level_up_rect = level_up_text.get_rect(center=(400, 200))
                self.screen.blit(level_up_text, level_up_rect)
                self.frames_to_blit_level_up -= 1
                # start_timer(timer_duration, 10, 100)

        # Draw game over message
        if self.game_over:
            game_over_text = font.render('Game Over! Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            if not self.handle_events():
                break

            if not self.in_game:
                self.title_screen()
            else:
                self.update()
                self.draw()
                self.clock.tick(5)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
