import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
from simulation.intersection import IntersectionSimulation
from ui.dashboard import Dashboard

WIDTH, HEIGHT = 1280, 760

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('SmartFlow — Adaptive Traffic Management System')
    clock = pygame.time.Clock()
    dashboard = Dashboard()
    traditional = IntersectionSimulation('TRADITIONAL', seed=22)
    smart = IntersectionSimulation('SMARTFLOW', seed=22)
    active = smart
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    traditional.paused = not traditional.paused; smart.paused = traditional.paused
                elif event.key == pygame.K_m:
                    active = traditional if active is smart else smart
                elif event.key == pygame.K_r:
                    traditional.reset(); smart.reset(); active = smart if active.mode == 'SMARTFLOW' else traditional
                elif event.key == pygame.K_UP:
                    traditional.speed = smart.speed = min(3.0, smart.speed + 0.25)
                elif event.key == pygame.K_DOWN:
                    traditional.speed = smart.speed = max(0.25, smart.speed - 0.25)
                elif event.key == pygame.K_RIGHT:
                    traditional.intensity = smart.intensity = min(2.2, smart.intensity + 0.1)
                elif event.key == pygame.K_LEFT:
                    traditional.intensity = smart.intensity = max(0.5, smart.intensity - 0.1)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    from simulation.vehicle import Vehicle
                    dirs = ['NORTH','EAST','SOUTH','WEST']; d = dirs[event.key - pygame.K_1]
                    rect = pygame.Rect(300,80,screen.get_width()-620,screen.get_height()-115)
                    x,y = active.spawn_pos(d, rect); active.vehicles.append(Vehicle(d,x,y,active.time))
        sim_rect = pygame.Rect(300,80,screen.get_width()-620,screen.get_height()-115)
        traditional.update(dt, sim_rect); smart.update(dt, sim_rect)
        dashboard.draw(screen, active, traditional, smart)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
