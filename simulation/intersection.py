from __future__ import annotations
import random
import pygame
from algorithms.traffic_optimizer import DIRECTIONS, SmartFlowOptimizer, TraditionalScheduler, Decision
from simulation.signal import TrafficSignal, GREEN, YELLOW, RED
from simulation.vehicle import Vehicle
from simulation.traffic import Metrics

SPAWN_RATES = {"NORTH": 0.95, "EAST": 0.28, "SOUTH": 0.55, "WEST": 0.25}

class IntersectionSimulation:
    def __init__(self, mode: str, seed: int = 7):
        self.mode = mode
        self.rng = random.Random(seed)
        self.vehicles: list[Vehicle] = []
        self.signals = {d: TrafficSignal(d) for d in DIRECTIONS}
        self.optimizer = SmartFlowOptimizer()
        self.traditional = TraditionalScheduler()
        self.metrics = Metrics()
        self.time = 0.0
        self.speed = 1.0
        self.intensity = 1.0
        self.paused = False
        self.phase = "YELLOW"
        self.phase_remaining = 0.5
        self.current: str | None = None
        self.next_decision: Decision | None = None
        self.last_green = {d: 0.0 for d in DIRECTIONS}
        self.spawn_timers = {d: self.rng.uniform(0.1, 1.2) for d in DIRECTIONS}
        self.decision = Decision("NORTH", 0, {}, "Initializing signals")

    def toggle_mode(self):
        self.mode = "SMARTFLOW" if self.mode == "TRADITIONAL" else "TRADITIONAL"
        self.force_cycle()

    def force_cycle(self):
        self.phase = "YELLOW"; self.phase_remaining = self.optimizer.config.yellow_time
        for s in self.signals.values(): s.set_state(YELLOW if s.state == GREEN else RED)

    def reset(self):
        mode = self.mode
        self.__init__(mode)

    def stop_lines(self, rect: pygame.Rect) -> dict[str, float]:
        return {"NORTH": rect.centery - 76, "SOUTH": rect.centery + 76, "EAST": rect.centerx + 76, "WEST": rect.centerx - 76}

    def spawn_pos(self, d: str, rect: pygame.Rect):
        lane = 23
        return {
            "NORTH": (rect.centerx - lane, -35), "SOUTH": (rect.centerx + lane, rect.h + 35),
            "EAST": (rect.w + 35, rect.centery - lane), "WEST": (-35, rect.centery + lane),
        }[d]

    def update(self, dt: float, rect: pygame.Rect):
        if self.paused: return
        dt *= self.speed; self.time += dt
        for d in DIRECTIONS: self.last_green[d] += dt
        self._spawn(dt, rect)
        self._signals(dt)
        self._vehicles(dt, rect)
        for s in self.signals.values(): s.update(dt)

    def _spawn(self, dt, rect):
        for d, base in SPAWN_RATES.items():
            self.spawn_timers[d] -= dt * base * self.intensity
            if self.spawn_timers[d] <= 0:
                x, y = self.spawn_pos(d, rect)
                same = [v for v in self.vehicles if v.direction == d and abs(v.x - x) < 70 and abs(v.y - y) < 70]
                if not same: self.vehicles.append(Vehicle(d, x, y, self.time))
                self.spawn_timers[d] = self.rng.uniform(0.6, 1.7)

    def _signals(self, dt):
        self.phase_remaining -= dt
        if self.phase_remaining > 0: return
        if self.phase == "GREEN":
            self.phase = "YELLOW"; self.phase_remaining = self.optimizer.config.yellow_time
            for d, s in self.signals.items(): s.set_state(YELLOW if d == self.current else RED)
        else:
            stats = self.road_stats()
            self.decision = self.optimizer.choose(stats, self.last_green, self.current) if self.mode == "SMARTFLOW" else self.traditional.next()
            self.current = self.decision.direction
            self.last_green[self.current] = 0.0
            self.phase = "GREEN"; self.phase_remaining = self.decision.green_time
            self.metrics.signal_changes += 1
            for d, s in self.signals.items(): s.set_state(GREEN if d == self.current else RED)

    def _vehicles(self, dt, rect):
        stops = self.stop_lines(rect)
        by_dir = {d: sorted([v for v in self.vehicles if v.direction == d], key=lambda v: v.distance_to_stop(stops)) for d in DIRECTIONS}
        for d, cars in by_dir.items():
            for i, v in enumerate(cars):
                can_go = self.signals[d].state == GREEN or v.distance_to_stop(stops) < -10
                gap_block = i > 0 and 0 < cars[i-1].distance_to_stop(stops) - v.distance_to_stop(stops) < 38
                at_line = 0 < v.distance_to_stop(stops) < 18
                v.stopped = (not can_go and at_line) or gap_block
                if v.stopped: v.waiting_time += dt
                else: v.move(dt)
        survivors = []
        for v in self.vehicles:
            if v.offscreen(rect.w, rect.h): self.metrics.record_clear(v.waiting_time)
            else: survivors.append(v)
        self.vehicles = survivors

    def road_stats(self) -> dict:
        stats = {}
        for d in DIRECTIONS:
            cars = [v for v in self.vehicles if v.direction == d]
            waiting = [v for v in cars if v.stopped or v.waiting_time > 0.1]
            density = min(1.0, len(cars) / 18)
            stats[d] = {"total": len(cars), "waiting": len(waiting), "density": density,
                        "avg_wait": sum(v.waiting_time for v in cars) / len(cars) if cars else 0.0,
                        "signal": self.signals[d].state, "green_time": self.signals[d].green_elapsed}
        return stats
