import pygame
import random
import time
import os, sys
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW = (800, 800)
BLOCK = 40
START_SPEED = 1
HARD_MODE_SPEED = 2
SPEED_INCREASE = 0.5
HARD_MODE_SPEED_INCREASE = 1
FPS = 30
LEVEL_UP_SCORE = 10
LEVEL_29_SPEED = 15 #Symbolic NES level
HARD_LEVEL_29_SPEED = 30 #Double the speed for hard mode level 29
VICTORY_POEM = '''TETRIS
The game of falling blocks, a test of skill and reflexes
With each piece that falls, a new challenge arises
The player must think quickly, plan ahead, and adapt to the ever-changing board
Lines are cleared, points are scored, and the game speeds up
You are a hero. A master of Tetris. You have conquered the 29th level, the legendary final stage
But the game is never truly over. The challenge continues, as you strive for higher scores and new records
Congratulations, for the love of the Legend of Zelda II, you have beaten Tetris
Yet the game may never truly end; for endless mode is coming soon.
[TO BE CONTINUED...]
The second last line is to be removed when endless mode is released, and the last line is just a teaser for it. 
Endless mode will be a free update that adds an infinite level after level 29, with the speed increasing every 10 levels. 
The music will also change every 10 levels, with some new tracks and some old ones from the main game.
The goal of endless mode is to get the highest score possible before inevitably losing'''

# Colors
BGCOLOR = (0, 0, 0)
BOXESCOLOR = (255, 255, 255)
I_COLOR = (0, 255, 255)
J_COLOR = (0, 0, 255)
L_COLOR = (255, 165, 0)
O_COLOR = (255, 255, 0)
S_COLOR = (0, 255, 0)
T_COLOR = (128, 0, 128)
Z_COLOR = (255, 0, 0)

# Global Variables
blocks = []
block_colors = []
prev_music_file = None

class GameState(Enum):
    TITLE = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    WARNING = 4 #Warning screen telling the player that the game is started in hard mode

class Tetrimino():
    class Rotation(Enum):
        UP = 0
        RIGHT = 1
        DOWN = 2
        LEFT = 3

    def __init__(self, type):
        self.type = type
        self.rotation = Tetrimino.Rotation.UP
        self.block_locations = self.get_initial_block_locations(type)
        self.color = self.get_color(type)
        self.last_move_time = time.time()

    def get_initial_block_locations(self, type):
        if type == 'I':
            return [[3, 19], [4, 19], [5, 19], [6, 19]]
        elif type == 'J':
            return [[5, 19], [5, 18], [5, 17], [4, 17]]
        elif type == 'L':
            return [[4, 19], [4, 18], [4, 17], [5, 17]]
        elif type == 'O':
            return [[4, 19], [5, 19], [4, 18], [5, 18]]
        elif type == 'S':
            return [[5, 19], [6, 19], [4, 18], [5, 18]]
        elif type == 'T':
            return [[4, 19], [5, 19], [6, 19], [5, 18]]
        elif type == 'Z':
            return [[4, 19], [5, 19], [5, 18], [6, 18]]
        else:
            raise ValueError("Invalid Tetrimino type")

    def get_color(self, type):
        if type == 'I':
            return I_COLOR
        elif type == 'J':
            return J_COLOR
        elif type == 'L':
            return L_COLOR
        elif type == 'O':
            return O_COLOR
        elif type == 'S':
            return S_COLOR
        elif type == 'T':
            return T_COLOR
        elif type == 'Z':
            return Z_COLOR
        else:
            raise ValueError("Invalid Tetrimino type")
        
    def move(self, direction):
        current_time = time.time()
        if current_time - self.last_move_time >= 0.1:
            if direction == 'left' and not self.check_collision('left'):
                for block in self.block_locations:
                    block[0] -= 1
            elif direction == 'right' and not self.check_collision('right'):
                for block in self.block_locations:
                    block[0] += 1
            elif direction == 'down' and not self.check_collision('down'):
                for block in self.block_locations:
                    block[1] -= 1  
            self.last_move_time = current_time
    
    def hard_drop(self):
        while True:
            # Check if moving down would cause collision
            can_move = True
            for block in self.block_locations:
                if block[1] - 1 < 0:
                    can_move = False
                    break
                for blk in blocks:
                    if [block[0], block[1] - 1] == blk[0]:
                        can_move = False
                        break
                if not can_move:
                    break
            
            if not can_move:
                break
            
            # Move down
            for block in self.block_locations:
                block[1] -= 1 

    def rotate(self, direction):
        if direction == 'clockwise':
            new_rotation = Tetrimino.Rotation((self.rotation.value + 1) % 4)
            px, py = self.block_locations[1]
            new = []
            for x, y in self.block_locations:
                dx = x - px
                dy = y - py
                nx = px - dy
                ny = py + dx
                new.append([int(nx), int(ny)])
            for block in new:
                if block[0] < 0 or block[0] >= 10 or block[1] < 0 or block[1] >= 20:
                    return
            for block in blocks:
                if block in new:
                    return
            self.block_locations = new
        else:
            new_rotation = Tetrimino.Rotation((self.rotation.value - 1) % 4)
            px, py = self.block_locations[1]
            new = []
            for x, y in self.block_locations:
                dx = x - px
                dy = y - py
                nx = px + dy
                ny = py - dx
                new.append([int(nx), int(ny)])
            for block in new:
                if block[0] < 0 or block[0] >= 10 or block[1] < 0 or block[1] >= 20:
                    return
            for block in blocks:
                if block in new:
                    return 
            self.block_locations = new
        self.rotation = new_rotation

    def check_collision(self, direction):
        if direction == 'left':
            for block in self.block_locations:
                if block[0] - 1 < 0:
                    return True
                for blk in blocks:
                    if [block[0] - 1, block[1]] == blk[0]:
                        return True
        elif direction == 'right':
            for block in self.block_locations:
                if block[0] + 1 >= 10:
                    return True
                for blk in blocks:
                    if [block[0] + 1, block[1]] == blk[0]:
                        return True
        elif direction == 'down':
            for block in self.block_locations:
                if block[1] - 1 < 0:
                    return True
                for blk in blocks:
                    if [block[0], block[1] - 1] == blk[0]:
                        return True
        return False

    def break_into_blocks(self):
        if self.check_collision('down'):
            for block in self.block_locations:
                blocks.append([block, self.color])
            return True
        return False

class TetrisGame:
    def __init__(self):
        self.state = GameState.TITLE
        self.score = 0
        self.level = 1
        self.speed = START_SPEED
        self.current_tetrimino = None
        self.next_tetrimino = None
        self.tetrises = 0
        self.triples = 0
        self.doubles = 0
        self.last_move_time = time.time()
        self.hard_mode = False
        self.endless_mode = False
        global blocks
        blocks.clear()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.state == GameState.TITLE:
                        if self.hard_mode:
                            self.state = GameState.WARNING
                        else:
                            self.state = GameState.PLAYING
                    elif self.state == GameState.WARNING:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.GAME_OVER:
                        self.__init__()
                if event.key == pygame.K_LSHIFT and self.state == GameState.TITLE:
                    self.endless_mode = not self.endless_mode
                    if self.endless_mode and self.hard_mode:
                        self.hard_mode = False #Endless mode is designed to allow players to clear levels more easily
                    if self.endless_mode:
                        pygame.display.set_caption("Tetris - ENDLESS MODE")
                if self.current_tetrimino: # Cannot call methods on NoneType
                    if event.key == pygame.K_UP:
                        if self.state == GameState.PLAYING:
                            self.current_tetrimino.rotate('clockwise')
                    if event.key == pygame.K_DOWN:
                        if self.state == GameState.PLAYING:
                            self.current_tetrimino.move('down')
                    if event.key == pygame.K_LEFT:
                        if self.state == GameState.PLAYING:
                            self.current_tetrimino.move('left')
                    if event.key == pygame.K_RIGHT:
                        if self.state == GameState.PLAYING:
                            self.current_tetrimino.move('right')
                    if event.key == pygame.K_x:
                        if self.state == GameState.PLAYING:
                            self.current_tetrimino.hard_drop()
                    if event.key == pygame.K_z:
                        if self.state == GameState.PLAYING:
                            self.current_tetrimino.rotate('counterclockwise')
                else: 
                    if event.key == pygame.K_x:
                        if self.state == GameState.WARNING:
                            self.state = GameState.PLAYING
                    if event.key == pygame.K_z:
                        if self.state == GameState.TITLE:
                            self.hard_mode = not self.hard_mode
                            if self.hard_mode:
                                pygame.display.set_caption("Tetris - HARD MODE")
                                self.speed = HARD_MODE_SPEED
                            else:
                                pygame.display.set_caption("Tetris")
                                self.speed = START_SPEED
                        if self.state == GameState.WARNING:
                            self.state = GameState.TITLE

    def spawn_tetrimino(self):
        types = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
        self.current_tetrimino = Tetrimino(self.next_tetrimino if self.next_tetrimino else random.choice(types))
        self.next_tetrimino = random.choice(types)
        self.last_move_time = time.time()
        for block in self.current_tetrimino.block_locations:
            for block_info in blocks:
                if block == block_info[0]: 
                    self.state = GameState.GAME_OVER

    def play_bgm(self):
        music_folder = 'sounds'
        global prev_music_file
        if self.state == GameState.TITLE:
            music_file = '01 Title.mp3'
        elif self.state == GameState.PLAYING and not self.hard_mode:
            if self.state == GameState.PLAYING and self.level <= 10:
                music_file = '19.mp3'
            elif self.state == GameState.PLAYING and 11 <= self.level <= 20:
                music_file = '4 - Deeper In the Cave....mp3' #Ominous music from Zelda II
            else:
                music_file = '4 - Deeper In the Cave....mp3' # Continue with level 20 music for levels 21-28
        elif self.state == GameState.PLAYING and self.hard_mode:
            music_file = 'hard_mode.mp3' #Pokemon FR/LG VS Rival music, because it's intense and fitting for hard mode
        elif self.state == GameState.PLAYING and self.endless_mode:
            if not self.level % 30:
                music_file = '19.mp3' #Return to the original music every 30 levels for nostalgia
            elif not (self.level - 10) % 30:
                music_file = '4 - Deeper In the Cave....mp3' #Return to the ominous music every 30 levels for variety
            elif not (self.level - 20) % 30:
                music_file = 'hard_mode.mp3' #Return to the intense hard mode music every 30 levels for hype
        elif self.state == GameState.PLAYING and self.level == 29:
            music_file = '15 - The Palace Boss.mp3' #Epic boss music from Zelda II
        elif self.state == GameState.GAME_OVER:
            music_file = 'game_over.mp3'
        elif self.state == GameState.WARNING:
            music_file = 'warning.mp3' #Beeping noise to warn the player that hard mode is enabled
        else:
            return  # For PAUSED state, don't change music
        if prev_music_file == music_file:
            return
        music_file_path = os.path.join(music_folder, music_file)
        pygame.mixer.music.load(music_file_path)
        pygame.mixer.music.play(-1)
        prev_music_file = music_file

    def level_up(self):
        self.level += 1
        self.score = 0
        self.speed += SPEED_INCREASE if not self.hard_mode else HARD_MODE_SPEED_INCREASE
        if self.level == 21 and not self.endless_mode:
            self.level = 29
            self.speed = HARD_LEVEL_29_SPEED if self.hard_mode else LEVEL_29_SPEED #Teleport to the legendary 29th level
        if self.level == 30 and not self.endless_mode:
            self.state = GameState.GAME_OVER
        if not self.hard_mode:
            blocks.clear()

    def calculate_score(self):
        score = 0
        score += (self.level - 1) * LEVEL_UP_SCORE
        if self.level == 29:
            score += 500 #Bonus for reaching level 29
        if self.level == 30:
            score += 1000 #Bonus for beating level 29
        if self.level > 30:
            score += (self.level - 30) * 100 #Bonus for each level cleared after 30 in endless mode
        score += self.tetrises * 50
        score += self.triples * 20
        score += self.doubles * 5
        #Bonus for clearing multiple lines at once
        return score

    def clear_lines(self):
        global blocks
        lines_cleared = 0
        for y in range(20):
            line_blocks = [block for block in blocks if block[0][1] == y]
            if len(line_blocks) >= 10:
                lines_cleared += 1
                blocks = [block for block in blocks if block[0][1] != y]
                # Drop all blocks above the cleared line
                for block in blocks:
                    if block[0][1] > y:
                        block[0][1] -= 1
        
        if lines_cleared == 4:
            self.tetrises += 1
            self.score += 10
        elif lines_cleared == 3:
            self.triples += 1
            self.score += 5
        elif lines_cleared == 2:
            self.doubles += 1
            self.score += 3
        elif lines_cleared == 1:
            self.score += 1
        if lines_cleared > 0:
            return True #See if to check again for cascading line clears
        return False
    
    def update(self):
        self.handle_input()
        self.play_bgm()
        if self.state == GameState.PLAYING:
            if self.current_tetrimino is None:
                self.spawn_tetrimino()
            elif self.current_tetrimino.check_collision('down'):
                self.current_tetrimino.break_into_blocks()
                self.current_tetrimino = None
                while self.clear_lines():
                    pass
                if self.score >= LEVEL_UP_SCORE:
                    self.level_up()
            if time.time() - self.last_move_time >= 1 / self.speed:
                if self.current_tetrimino is not None:
                    for block in self.current_tetrimino.block_locations:
                        block[1] -= 1
                    self.last_move_time = time.time() 
        if self.state == GameState.GAME_OVER:
            self.score = self.calculate_score()
        if self.state == GameState.PAUSED:
            self.last_move_time = time.time() # Prevents piece from falling while paused

class View:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode(WINDOW)
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.poem = {}
        for i, line in enumerate(VICTORY_POEM.split('\n')):
            self.poem[line] = WINDOW[1] + i * 40

    def load_font(self, font_name, size):
        font_folder = 'fonts'
        font_path = os.path.join(font_folder, font_name)
        return pygame.font.Font(font_path, size)

    def title_screen(self):
        self.screen.fill(BGCOLOR)
        if self.game.hard_mode:
            title_font = self.load_font('HyliaSerifBeta-Regular.otf', 48)
        else:
            title_font = self.load_font('TetrisNew.ttf', 48)
        start_font = self.load_font('PressStart2P.ttf', 24)
        title_surface = title_font.render("TETRIS", True, BOXESCOLOR)
        start_surface = start_font.render("PUSH START", True, BOXESCOLOR)
        self.screen.blit(title_surface, (WINDOW[0] // 2 - title_surface.get_width() // 2, WINDOW[1] // 3))
        self.screen.blit(start_surface, (WINDOW[0] // 2 - start_surface.get_width() // 2, WINDOW[1] // 2))
        pygame.display.flip()

    def warning_screen(self):
        self.screen.fill(BGCOLOR)
        warning_font = self.load_font('PressStart2P.ttf', 24)
        warning_surface = warning_font.render("WARNING: HARD MODE ENABLED", True, BOXESCOLOR)
        start_surface = warning_font.render("PRESS X TO START, Z TO GO BACK", True, BOXESCOLOR)
        self.screen.blit(start_surface, (WINDOW[0] // 2 - start_surface.get_width() // 2, WINDOW[1] // 2 + 40))
        self.screen.blit(warning_surface, (WINDOW[0] // 2 - warning_surface.get_width() // 2, WINDOW[1] // 2))
        pygame.display.flip()

    def base_game_screen(self):
        self.screen.fill(BGCOLOR)
        pygame.draw.line(self.screen, BOXESCOLOR, (400, 0), (400, 800), 4)
        pygame.draw.rect(self.screen, BOXESCOLOR, (500, 600, 250, 150), 2)
        score_font = self.load_font('PressStart2P.ttf', 18)
        score_surface = score_font.render(f"SCORE: {self.game.score}", True, BOXESCOLOR)
        level_surface = score_font.render(f"LEVEL: {self.game.level}", True, BOXESCOLOR)
        self.screen.blit(score_surface, (510, 50))
        self.screen.blit(level_surface, (510, 100))

    def draw_blocks(self):
        for i, block in enumerate(blocks):
            pygame.draw.rect(self.screen, block[1], (block[0][0] * BLOCK, (19 - block[0][1]) * BLOCK, BLOCK, BLOCK))
        if self.game.current_tetrimino:
            for block in self.game.current_tetrimino.block_locations:
                pygame.draw.rect(self.screen, self.game.current_tetrimino.color, (block[0] * BLOCK, (19 - block[1]) * BLOCK, BLOCK, BLOCK))
        
    def paused(self):
        pause_font = self.load_font('PressStart2P.ttf', 40)
        pause_surface = pause_font.render("PAUSED", True, BOXESCOLOR)
        self.screen.blit(pause_surface, (WINDOW[0] // 2 - pause_surface.get_width() // 2, WINDOW[1] // 2 - pause_surface.get_height() // 2))

    def game_over(self):
        self.screen.fill(BGCOLOR)
        if self.game.level > 29:
            self.draw_win()
        over_font = self.load_font('PressStart2P.ttf', 40)
        over_surface = over_font.render("GAME OVER", True, BOXESCOLOR)
        self.screen.blit(over_surface, (WINDOW[0] // 2 - over_surface.get_width() // 2, WINDOW[1] // 2 - over_surface.get_height() // 2))
        score_font = self.load_font('PressStart2P.ttf', 24)
        score_surface = score_font.render(f"FINAL SCORE: {self.game.score}", True, BOXESCOLOR)
        self.screen.blit(score_surface, (WINDOW[0] // 2 - score_surface.get_width() // 2, WINDOW[1] // 2 + over_surface.get_height() // 2))
        pygame.display.flip()

    def draw_win(self):
        win_font = self.load_font('HyliaSerifBeta-Regular.otf', 16)
        for line in self.poem:
            line_surface = win_font.render(line, True, BOXESCOLOR)
            self.screen.blit(line_surface, (WINDOW[0] // 2 - line_surface.get_width() // 2, self.poem[line]))
            #Negative lines will not display, so the poem will scroll
            self.poem[line] -= 1 #Already displayed line does not move on screen, but readies up for the next frame 


    def draw_next_tetrimino(self):
        if self.game.next_tetrimino:
            next_font = self.load_font('PressStart2P.ttf', 18)
            next_surface = next_font.render("NEXT:", True, BOXESCOLOR)
            self.screen.blit(next_surface, (510, 610))
            type = self.game.next_tetrimino
            color = Tetrimino(type).get_color(type)
            positions = Tetrimino(type).get_initial_block_locations(type)
            offset_x = 510
            offset_y = 640
            for pos in positions:
                x = pos[0] - 4
                y = 19 - pos[1]
                pygame.draw.rect(self.screen, color, (offset_x + x * BLOCK, offset_y + y * BLOCK, BLOCK, BLOCK))
    
    def render(self):
        if self.game.state == GameState.TITLE:
            self.title_screen()
        elif self.game.state == GameState.WARNING:
            self.warning_screen()
        elif self.game.state in [GameState.PLAYING, GameState.PAUSED]:
            self.base_game_screen()
            self.draw_blocks()
            self.draw_next_tetrimino()
            if self.game.state == GameState.PAUSED:
                self.paused()
            pygame.display.flip()
        elif self.game.state == GameState.GAME_OVER:
            self.game_over()
        self.clock.tick(FPS)

def main():
    game = TetrisGame()
    window = View(game)
    while True:
        game.update()
        window.render()

if __name__ == "__main__":
    main()
