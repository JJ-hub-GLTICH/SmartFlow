import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
from simulation.intersection import IntersectionSimulation
from ui.dashboard import Dashboard
from simulation.scenario import SCENARIOS, ScenarioRunner

WIDTH, HEIGHT = 1280, 760


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('SmartFlow — Adaptive Traffic Management System')
    clock = pygame.time.Clock()
    dashboard = Dashboard()
    runner = ScenarioRunner()
    traditional = IntersectionSimulation('TRADITIONAL', seed=22)
    smart = IntersectionSimulation('SMARTFLOW', seed=22)
    active = smart
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if runner.state == "menu":
                    for rect, key in dashboard.lab_buttons:
                        if rect.collidepoint(event.pos):
                            sim_rect = pygame.Rect(300,80,screen.get_width()-620,screen.get_height()-115)
                            runner.start(SCENARIOS[key], traditional, smart, sim_rect)
                            active = traditional
                            break
                elif runner.state == "results":
                    for rect, action in dashboard.result_buttons:
                        if rect.collidepoint(event.pos):
                            sim_rect = pygame.Rect(300,80,screen.get_width()-620,screen.get_height()-115)
                            if action == "again" and runner.scenario:
                                runner.start(runner.scenario, traditional, smart, sim_rect); active = traditional
                            elif action == "choose":
                                runner.open_lab()
                            elif action == "live":
                                runner.return_live(traditional, smart); active = smart
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    runner.open_lab()
                    traditional.paused = smart.paused = True
                elif runner.state != "idle":
                    continue
                elif event.key == pygame.K_SPACE:
                    traditional.paused = not traditional.paused; smart.paused = traditional.paused
                elif event.key == pygame.K_m and runner.state == "idle":
                    active = traditional if active is smart else smart
                elif event.key == pygame.K_r and runner.state == "idle":
                    traditional.reset(); smart.reset(); active = smart if active.mode == 'SMARTFLOW' else traditional
                elif event.key == pygame.K_UP:
                    traditional.speed = smart.speed = min(3.0, smart.speed + 0.25)
                elif event.key == pygame.K_DOWN:
                    traditional.speed = smart.speed = max(0.25, smart.speed - 0.25)
                elif event.key == pygame.K_RIGHT:
                    traditional.intensity = smart.intensity = min(2.2, smart.intensity + 0.1)
                elif event.key == pygame.K_LEFT:
                    traditional.intensity = smart.intensity = max(0.5, smart.intensity - 0.1)
                elif event.key == pygame.K_h:
                    traditional.toggle_rush_hour(); smart.toggle_rush_hour()
                elif event.key == pygame.K_e:
                    smart.activate_emergency('SOUTH')
                    active = smart
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    from simulation.vehicle import Vehicle
                    dirs = ['NORTH','EAST','SOUTH','WEST']; d = dirs[event.key - pygame.K_1]
                    rect = pygame.Rect(300,80,screen.get_width()-620,screen.get_height()-115)
                    x,y = active.spawn_pos(d, rect); active.vehicles.append(Vehicle(d,x,y,active.time))
        sim_rect = pygame.Rect(300,80,screen.get_width()-620,screen.get_height()-115)
        traditional.update(dt, sim_rect); smart.update(dt, sim_rect)
        scenario_active = runner.update(dt, traditional, smart, sim_rect)
        if scenario_active is not None:
            active = scenario_active
        dashboard.draw(screen, active, traditional, smart)
        dashboard.draw_scenario_overlay(screen, runner)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
