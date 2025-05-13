import pygame
import random
import heapq
from collections import deque
import time

class Game:
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Font for displaying resources
        self.font = pygame.font.Font(None, 30)
        
        # Grid settings
        self.cell_size = 60
        self.grid_width = self.width // self.cell_size
        self.grid_height = self.height // self.cell_size
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Game objects
        self.plants = []
        self.zombies = []
        self.projectiles = []
        self.resources = 90  # Increased starting resources
        self.plant_cost = 30  # Increased plant cost
        self.wave_count = 0
        
        # Game timing
        self.last_shoot_time = {}
        self.shoot_delay = 1000
        self.last_wave_time = pygame.time.get_ticks()
        self.wave_delay = 10000  # 10 seconds between waves
        
        # A* pathfinding variables
        self.directions = [(-1,0)]  # Only allow moving left
        
        self.mode = None  # 'user_vs_ai' or 'ai_vs_ai'
        self.last_ai_plant_time = time.time()
        self.ai_plant_interval = 2.0  # seconds between AI plant placements
        
    def get_grid_pos(self, x, y):
        return (x // self.cell_size, y // self.cell_size)
        
    def is_valid_cell(self, x, y):
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height
        
    def manhattan_distance(self, start, goal):
        return abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        
    def plant_penalty(self, cell):
        # Returns a penalty if the cell or its neighbors have a plant
        x, y = cell
        penalty = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if self.is_valid_cell(nx, ny) and self.grid[ny][nx] == 'plant':
                    penalty += 5  # Penalty for being near a plant
        return penalty
        
    def a_star(self, start, goal):
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for dx, dy in self.directions:
                next_cell = (current[0] + dx, current[1] + dy)
                
                if not self.is_valid_cell(next_cell[0], next_cell[1]):
                    continue
                
                # Add plant penalty to the cost
                penalty = self.plant_penalty(next_cell)
                new_cost = cost_so_far[current] + 1 + penalty
                
                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    priority = new_cost + self.manhattan_distance(next_cell, goal)
                    heapq.heappush(frontier, (priority, next_cell))
                    came_from[next_cell] = current
        
        return came_from, cost_so_far

    def spawn_zombie(self):
        current_time = pygame.time.get_ticks()
        
        if random.random() < 0.01:   
            y = random.randint(0, self.grid_height-1)
            self.zombies.append({ # regular zombie
                'x': self.width - self.cell_size,
                'y': y * self.cell_size,
                'health': 100,
                'speed': 0.8,  
                'damage': 0.5,
                'is_boss': False
            })
        
        if current_time - self.last_wave_time >= self.wave_delay:
            self.wave_count += 1
            y = random.randint(0, self.grid_height-1)
            self.zombies.append({ # boss zombie
                'x': self.width - self.cell_size,
                'y': y * self.cell_size,
                'health': 400,
                'speed': 0.5,   
                'damage': 3,
                'is_boss': True
            })
            self.last_wave_time = current_time

    def update(self):
        if self.resources <= -100:
            print(f"Game Over! You survived {self.wave_count} waves!")
            pygame.quit()
            return False
            
        print(f"[DEBUG] Resources: {self.resources}")
        
        current_time = pygame.time.get_ticks()
        
        for plant in self.plants: # shooting mech 
            plant_id = id(plant)
            if plant_id not in self.last_shoot_time or \
               current_time - self.last_shoot_time[plant_id] >= self.shoot_delay:
                
                plant_row = plant['y'] // self.cell_size
                zombies_in_row = [z for z in self.zombies 
                                if z['y'] // self.cell_size == plant_row and 
                                z['x'] > plant['x']]
                
                if zombies_in_row:
                    self.projectiles.append({
                        'x': plant['x'] + self.cell_size//2,
                        'y': plant['y'] + self.cell_size//2,
                        'speed': 8,
                        'damage': 30
                    })
                    self.last_shoot_time[plant_id] = current_time

        zombies_to_remove = []
        for zombie in self.zombies:
            # Only move left, no up or down
            zombie['x'] -= zombie['speed']

            if zombie['x'] <= 0: # if zombies reach the wall
                self.resources -= (30 if zombie['is_boss'] else 10)
                zombies_to_remove.append(zombie)

        for zombie in zombies_to_remove: # remove zombies if reaches the wall
            if zombie in self.zombies:
                self.zombies.remove(zombie)

        projectiles_to_remove = [] # remove projectiles after a hit 
        for proj in self.projectiles:
            proj['x'] += proj['speed']
            
            if proj['x'] > self.width: # Remove projectiles that go off screen
                projectiles_to_remove.append(proj)
                continue
            
            for zombie in self.zombies: # Check collisions with zombies for damage
                if (abs(proj['x'] - (zombie['x'] + self.cell_size//2)) < self.cell_size//3 and 
                    abs(proj['y'] - (zombie['y'] + self.cell_size//2)) < self.cell_size//3):
                    zombie['health'] -= proj['damage']
                    projectiles_to_remove.append(proj)
                    
                    if zombie['health'] <= 0 and zombie in self.zombies: # Remove dead zombies and award resources
                        self.zombies.remove(zombie)
                        self.resources += 10  
                    break

        # Remove used projectiles
        for proj in projectiles_to_remove:
            if proj in self.projectiles:
                self.projectiles.remove(proj)
                
        return True

    def draw(self):
        self.screen.fill((0, 150, 0))  # Green background 
        
        # Draw grid
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, (0,0,0), (x,0), (x,self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, (0,0,0), (0,y), (self.width,y))
            
        # Draw plants
        for plant in self.plants:
            pygame.draw.circle(self.screen, (0,255,0), 
                             (plant['x'] + self.cell_size//2, 
                              plant['y'] + self.cell_size//2), 
                             self.cell_size//3)
            
        # Draw zombies
        for zombie in self.zombies:

            color = (150,0,150) if zombie['is_boss'] else (150,0,0)
            size = self.cell_size//2 if zombie['is_boss'] else self.cell_size//3
            
            pygame.draw.circle(self.screen, color, 
                             (int(zombie['x']) + self.cell_size//2, 
                              int(zombie['y']) + self.cell_size//2), 
                             size)
            
            # Draw zombie health bar
            health_width = (zombie['health'] / (300 if zombie['is_boss'] else 100)) * self.cell_size
            health_color = (255,0,255) if zombie['is_boss'] else (255,0,0)
            pygame.draw.rect(self.screen, health_color,
                           (int(zombie['x']), int(zombie['y'] - 10),
                            health_width, 5))
            
        # Draw projectiles
        for proj in self.projectiles:
            pygame.draw.circle(self.screen, (255,255,0), 
                             (int(proj['x']), int(proj['y'])), 5)
            
        # Draw resources and wave count
        resources_text = self.font.render(f'Resources: {self.resources}', True, (255, 255, 255))
        wave_text = self.font.render(f'Wave: {self.wave_count}', True, (255, 255, 255))
        plant_cost_text = self.font.render(f'Plant Cost: {self.plant_cost}', True, (255, 255, 255))
        self.screen.blit(resources_text, (10, 10))
        self.screen.blit(wave_text, (10, 50))
        self.screen.blit(plant_cost_text, (10, 90))
            
        pygame.display.flip()

    def ai_place_plant(self):
        # Place a plant in front of the zombie closest to the left wall
        if self.resources < self.plant_cost:
            print(f"[AI] Not enough resources to place plant. Resources: {self.resources}")
            return
        if not self.zombies:
            print("[AI] No zombies to defend against.")
            return
        # Find the zombie closest to the left wall
        closest_zombie = min(self.zombies, key=lambda z: z['x'])
        grid_x, grid_y = self.get_grid_pos(closest_zombie['x'], closest_zombie['y'])
        # Try to place a plant in the same row, as close to the zombie as possible
        for x in range(grid_x-1, -1, -1):
            if self.is_valid_cell(x, grid_y) and not self.grid[grid_y][x]:
                self.plants.append({
                    'x': x * self.cell_size,
                    'y': grid_y * self.cell_size,
                    'health': 100
                })
                self.grid[grid_y][x] = 'plant'
                self.resources -= self.plant_cost
                print(f"[AI] Placed plant at ({x}, {grid_y}). Resources left: {self.resources}")
                return
        print(f"[AI] No valid cell to place plant in row {grid_y}.")

    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        # Mode selection screen
        selecting_mode = True
        while selecting_mode:
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            text1 = font.render('Press U for User vs AI', True, (255, 255, 255))
            text2 = font.render('Press A for AI vs AI', True, (255, 255, 255))
            self.screen.blit(text1, (60, 200))
            self.screen.blit(text2, (60, 300))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.mode = 'user_vs_ai'
                        selecting_mode = False
                    elif event.key == pygame.K_a:
                        self.mode = 'ai_vs_ai'
                        selecting_mode = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mode == 'user_vs_ai':
                        if self.resources >= self.plant_cost: # Place plant at mouse click
                            x, y = event.pos
                            grid_x, grid_y = self.get_grid_pos(x, y)
                            if self.is_valid_cell(grid_x, grid_y) and not self.grid[grid_y][grid_x]:
                                self.plants.append({
                                    'x': grid_x * self.cell_size,
                                    'y': grid_y * self.cell_size,
                                    'health': 100
                                })
                                self.grid[grid_y][grid_x] = 'plant'
                                self.resources -= self.plant_cost

            # AI plant placement if in AI vs AI mode
            if self.mode == 'ai_vs_ai':
                now = time.time()
                if now - self.last_ai_plant_time > self.ai_plant_interval:
                    self.ai_place_plant()
                    self.last_ai_plant_time = now

            self.spawn_zombie()
            if not self.update():  # Game over check
                break
            self.draw()
            # Display mode on screen
            font = pygame.font.Font(None, 30)
            mode_text = font.render(f'Mode: {"User vs AI" if self.mode == "user_vs_ai" else "AI vs AI"}', True, (255, 255, 0))
            self.screen.blit(mode_text, (400, 10))
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()