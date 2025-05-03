import pygame
import random
import os
import sys
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GAME_TITLE = "Snake Game 🐍"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)

# Speed settings
INITIAL_SPEED = 10
MAX_SPEED = 25
SPEED_INCREMENT = 0.5

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Create game directory structure
def create_directories():
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

# Snake class
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        self.last_move_time = time.time()
        self.move_delay = 0.1  # seconds between moves

    def get_head_position(self):
        return self.positions[0]

    def update_direction(self, direction):
        if self.length > 1 and (direction[0] * -1, direction[1] * -1) == self.direction:
            # Prevent moving directly opposite current direction
            return
        self.direction = direction

    def move(self):
        current = time.time()
        if current - self.last_move_time < self.move_delay:
            return
            
        self.last_move_time = current
        
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + (x * GRID_SIZE)) % SCREEN_WIDTH
        new_y = (head[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT
        new_position = (new_x, new_y)
        
        # Check for collision with self
        if new_position in self.positions[1:]:
            return False  # Game over
            
        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.positions.pop()
            
        return True  # Still alive

    def reset(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.move_delay = 0.1

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            # Draw snake head in darker green
            if i == 0:
                pygame.draw.rect(surface, DARK_GREEN, pygame.Rect(p[0], p[1], GRID_SIZE, GRID_SIZE))
                # Add eyes to the snake head
                self.draw_eyes(surface, p)
            else:
                pygame.draw.rect(surface, self.color, pygame.Rect(p[0], p[1], GRID_SIZE, GRID_SIZE))
                
            # Add some detail to the snake body segments
            if i > 0:
                inner_rect = pygame.Rect(
                    p[0] + 2, p[1] + 2, 
                    GRID_SIZE - 4, GRID_SIZE - 4
                )
                pygame.draw.rect(surface, DARK_GREEN, inner_rect)
                
    def draw_eyes(self, surface, head_pos):
        # Determine eye positions based on direction
        x, y = head_pos
        
        if self.direction == UP:
            left_eye = (x + GRID_SIZE // 4, y + GRID_SIZE // 4)
            right_eye = (x + 3 * GRID_SIZE // 4, y + GRID_SIZE // 4)
        elif self.direction == DOWN:
            left_eye = (x + GRID_SIZE // 4, y + 3 * GRID_SIZE // 4)
            right_eye = (x + 3 * GRID_SIZE // 4, y + 3 * GRID_SIZE // 4)
        elif self.direction == LEFT:
            left_eye = (x + GRID_SIZE // 4, y + GRID_SIZE // 4)
            right_eye = (x + GRID_SIZE // 4, y + 3 * GRID_SIZE // 4)
        else:  # RIGHT
            left_eye = (x + 3 * GRID_SIZE // 4, y + GRID_SIZE // 4)
            right_eye = (x + 3 * GRID_SIZE // 4, y + 3 * GRID_SIZE // 4)
            
        # Draw the eyes
        pygame.draw.circle(surface, WHITE, left_eye, GRID_SIZE // 5)
        pygame.draw.circle(surface, WHITE, right_eye, GRID_SIZE // 5)
        
        # Draw pupils
        pygame.draw.circle(surface, BLACK, left_eye, GRID_SIZE // 10)
        pygame.draw.circle(surface, BLACK, right_eye, GRID_SIZE // 10)

# Food class
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
        self.last_spawn_time = time.time()

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self, surface):
        r = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.color, r)
        # Add a highlight to make the food look more appealing
        pygame.draw.rect(
            surface, 
            (255, 150, 150), 
            pygame.Rect(
                self.position[0] + GRID_SIZE // 3,
                self.position[1] + GRID_SIZE // 3,
                GRID_SIZE // 4,
                GRID_SIZE // 4
            )
        )

# Game class
class Game:
    def __init__(self):
        create_directories()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.large_font = pygame.font.SysFont("arial", 48)
        self.speed = INITIAL_SPEED
        self.load_sounds()
        self.reset()

    def load_sounds(self):
        # Initialize sound effects
        try:
            pygame.mixer.init()
            if not os.path.exists("assets/eat.wav"):
                # Create a simple sound placeholder if the file doesn't exist
                print("Sound files not found. The game will run without sound effects.")
                self.eat_sound = None
                self.crash_sound = None
            else:
                self.eat_sound = pygame.mixer.Sound("assets/eat.wav")
                self.crash_sound = pygame.mixer.Sound("assets/crash.wav")
        except:
            print("Sound system initialization failed. The game will run without sound effects.")
            self.eat_sound = None
            self.crash_sound = None

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.paused = False

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_RETURN:
                        self.reset()
                    if event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if event.key == pygame.K_UP:
                        self.snake.update_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.update_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.update_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.update_direction(RIGHT)
                    elif event.key == pygame.K_ESCAPE:
                        return False
        return True

    def run_logic(self):
        if not self.game_over and not self.paused:
            # Move the snake
            if not self.snake.move():
                self.game_over = True
                if self.crash_sound:
                    self.crash_sound.play()
                return
                
            # Check if the snake has eaten the food
            if self.snake.get_head_position() == self.food.position:
                self.snake.length += 1
                self.snake.score += 10
                if self.eat_sound:
                    self.eat_sound.play()
                
                # Increase game speed
                if self.speed < MAX_SPEED:
                    self.speed += SPEED_INCREMENT
                    # Also adjust snake's move delay to make it faster
                    self.snake.move_delay = max(0.04, self.snake.move_delay * 0.95)
                    
                # Spawn new food
                self.food.randomize_position()
                # Make sure food doesn't spawn on the snake
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

    def display_text(self, text, size, color, x, y):
        font = pygame.font.SysFont("arial", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def display_score(self):
        score_text = f"Score: {self.snake.score}"
        score_font = self.font.render(score_text, True, WHITE)
        self.screen.blit(score_font, (10, 10))

    def display_game_over(self):
        game_over_font = self.large_font.render("GAME OVER", True, RED)
        retry_font = self.font.render("Press ENTER to play again or ESC to quit", True, WHITE)
        final_score_font = self.font.render(f"Final Score: {self.snake.score}", True, WHITE)
        
        self.screen.blit(game_over_font, (SCREEN_WIDTH//2 - game_over_font.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(retry_font, (SCREEN_WIDTH//2 - retry_font.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(final_score_font, (SCREEN_WIDTH//2 - final_score_font.get_width()//2, SCREEN_HEIGHT//2 - 30))

    def display_pause(self):
        pause_font = self.large_font.render("PAUSED", True, BLUE)
        continue_font = self.font.render("Press P to continue", True, WHITE)
        
        self.screen.blit(pause_font, (SCREEN_WIDTH//2 - pause_font.get_width()//2, SCREEN_HEIGHT//2 - 45))
        self.screen.blit(continue_font, (SCREEN_WIDTH//2 - continue_font.get_width()//2, SCREEN_HEIGHT//2 + 15))

    def draw_frame(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        self.display_score()
        
        if self.game_over:
            self.display_game_over()
        elif self.paused:
            self.display_pause()
            
        pygame.display.flip()

    def run(self):
        # Main game loop
        running = True
        while running:
            # Process events
            running = self.process_events()
            
            # Run game logic
            self.run_logic()
            
            # Draw the current frame
            self.draw_frame()
            
            # Control game speed
            self.clock.tick(self.speed)

# Main function
def main():
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
