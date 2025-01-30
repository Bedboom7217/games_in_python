import pygame
import random
import time
import sqlite3
import os, sys
from enum import Enum
import yaml

# Read the YAML configuration file
with open('snake.config', 'r') as file:
    config = yaml.safe_load(file)

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = config['settings']['window_size']
GRID_SIZE = config['settings']['grid_size']
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
SOUND_EFFECT_FINISHED = pygame.USEREVENT + 1  # Define a custom event

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = tuple(config['colors']['color1'])
GREEN = tuple(config['colors']['snake_color'])
CYAN = tuple(config['colors']['color2'])
YELLOW = tuple(config['colors']['color3'])

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
        self.draw_level_up = False
        self.frames_to_blit_level_up = 10
        self.reset_game()

    def reset_game(self):
        self.total_remaining_time = 0
        self.timer_duration = 120*1000
        self.food_count = 10
        self.level = 1
        self.direction = Direction.RIGHT
        self.snake = [(GRID_COUNT // 4, GRID_COUNT // 2)]
        self.foods = []
        self.generate_foods()
        self.level_start_time = pygame.time.get_ticks()
        self.score = 0
        self.game_over = False
        self.play_bgm('bgm.mp3', -1)
        self.initials = ''
        self.enter_initials = False

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

    def level_up(self):
        if self.score >= 10: 
            if self.level == 10:
                self.you_win()
            else:
                self.draw_level_up = True
                self.food_count -= 1
                self.level += 1
                self.score = 0
                self.frames_to_blit_level_up = 10
                if len(self.foods) > self.food_count:
                    self.foods.pop()
                self._stop_sound_effect()
                self.play_sound('level_up.mp3')
                level_elapsed_time = pygame.time.get_ticks() - self.level_start_time
                remaining_time = self.timer_duration - level_elapsed_time 
                self.total_remaining_time += remaining_time
                self.timer_duration -= 10*1000
                self.level_start_time = pygame.time.get_ticks()

    def add_high_score(self, player_initials, score):
        connection = sqlite3.connect('snake.db')
        cursor = connection.cursor()
        cursor.execute('''
        INSERT INTO HighScores (player_initials, score) VALUES (?, ?)
        ''', (player_initials, score))
        connection.commit()

    def get_high_scores(self, limit=10):
        connection = sqlite3.connect('snake.db')
        cursor = connection.cursor()
        cursor.execute('''
        SELECT player_initials, score, date_played FROM HighScores
        ORDER BY score DESC LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

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

    def _get_final_score(self):
        end_game_score = (self.level - 1)*10
        end_game_score += self.score
        end_game_score += self.total_remaining_time // 1000
        end_game_score -= len(self.snake)
        if self._you_win():
            end_game_score *= 2
        if end_game_score < 0:
            end_game_score = 0
        return end_game_score    

    def stop_game(self):
        self.play_sound('game_over.mp3')

    def _you_win(self):
        return self.level == 10 and self.score == 10

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
                elif event.key == pygame.K_r and self.game_over and not self.enter_initials:
                    self.reset_game()
                elif event.key == pygame.K_BACKSPACE and self.enter_initials:
                    self.initials = self.initials[:-1]
                elif event.key == pygame.K_RETURN and self.enter_initials:
                    self.enter_initials = False
                    self.add_high_score(self.initials, self._get_final_score())
                elif event.unicode.isalpha() and len(self.initials) < 3:
                    self.initials += event.unicode.upper()  # Add uppercase letter
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
            self.enter_initials = True
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

        # Check if time is up
        level_elapsed_time = pygame.time.get_ticks() - self.level_start_time
        if level_elapsed_time > self.timer_duration:
            self.game_over = True
            self.enter_initials = True

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

        # Draw level up
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

        # Draw game over message
        if self.game_over and not self.enter_initials:
            game_over_text = font.render(f'Game Over! Press R to Restart!'
                    f'Score: {self._get_final_score()}', False, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2,
                100))
            self.screen.blit(game_over_text, text_rect)

        # Draw time left
        # Convert remaining time into minutes and seconds
        level_elapsed_time = pygame.time.get_ticks() - self.level_start_time
        remaining_time = self.timer_duration - level_elapsed_time 
        minutes = remaining_time // 1000 // 60
        seconds = remaining_time // 1000 % 60
        time_text = f"{minutes}:{seconds}"

        # Render the timer text
        font = pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 28)
        timer_text = font.render(f"Time left: {time_text}", True, WHITE)
        # Get the text's rectangle
        text_rect = timer_text.get_rect(topright=(WINDOW_SIZE - 10, 10))
        # Draw the timer
        if not self.game_over:
            self.screen.blit(timer_text, text_rect)

        # Draw you win
        if self._you_win():
            win_font = pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 32)
            win_text = win_font.render(f'You win! Push R to replay. Score: '
                    f'{self._get_final_score()}', False, WHITE)
            text_rect = win_text.get_rect(center=(WINDOW_SIZE/2, 100))
            self.screen.blit(win_text, text_rect)
            
        # Input initials
        if self.enter_initials:
            initials_font = \
            pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 40)
            initials_text = initials_font.render(f'Enter Initials: {self.initials}', False, WHITE)
            text_rect = initials_text.get_rect(center=(WINDOW_SIZE/2,
                WINDOW_SIZE/2))
            self.screen.blit(initials_text, text_rect)

        # Draw high scores
        score_number = 1
        draw_y = 200
        scores_font = pygame.font.Font(self.load_font('Mojang-Regular.ttf'), 16)
        if self.game_over and not self.enter_initials:
            for score in self.get_high_scores(): 
                scores_text = scores_font.render(f'{score_number}.  Player Initials: {score[0]} Score: {score[1]} Time Played(UTC): {score[2]}', False, WHITE)
                text_rect = scores_text.get_rect(center=(WINDOW_SIZE/2, draw_y))
                self.screen.blit(scores_text, text_rect)
                score_number += 1
                draw_y += 25

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
