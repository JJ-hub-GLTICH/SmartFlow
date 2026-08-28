from __future__ import annotations
import random
import pygame
from algorithms.traffic_optimizer import DIRECTIONS, SmartFlowOptimizer, TraditionalScheduler, Decision
from simulation.signal import TrafficSignal, GREEN, YELLOW, RED
from simulation.vehicle import Vehicle
from simulation.traffic import Metrics

BASE_SPAWN_RATES = {"NORTH": 0.78, "EAST": 0.38, "SOUTH": 0.62, "WEST": 0.34}
RUSH_MULTIPLIERS = {"NORTH": 1.75, "EAST": 1.25, "SOUTH": 2.05, "WEST": 1.45}
LANE_OFFSET = 24
SAFE_GAP = 15

class IntersectionSimulation:
    def __init__(self, mode: str, seed: int = 7):
        self.mode = mode
        self.seed = seed
        self.rng = random.Random(seed)
        self.vehicles: list[Vehicle] = []
        self.signals = {d: TrafficSignal(d) for d in DIRECTIONS}
        self.optimizer = SmartFlowOptimizer()
        self.traditional = TraditionalScheduler()
        self.metrics = Metrics()
        self.time = 0.0
        self.speed = 1.0
        self.intensity = 1.0
        self.rush_hour = False
        self.rush_factor = 0.0
        self.paused = False
        self.phase = "YELLOW"
        self.phase_remaining = 0.5
        self.current: str | None = None
        self.last_green = {d: 0.0 for d in DIRECTIONS}
        self.spawn_timers = {d: self.rng.uniform(0.15, 1.0) for d in DIRECTIONS}
        self.decision = Decision("NORTH", 0, {}, "Initializing signals")
        self.emergency_direction: str | None = None
        self.emergency_active = False
        self._seed_initial_traffic()

    def _seed_initial_traffic(self):
        for d, count in {"NORTH": 5, "SOUTH": 4, "EAST": 2, "WEST": 3}.items():
            for i in range(count):
                self.vehicles.append(Vehicle(d, 0, 0, self.time - i * .4, vehicle_type=self._vehicle_type()))

    def reset(self):
        mode, speed, intensity = self.mode, self.speed, self.intensity
        self.__init__(mode, self.seed)
        self.speed, self.intensity = speed, intensity

    def toggle_rush_hour(self):
        self.rush_hour = not self.rush_hour

    def activate_emergency(self, direction: str = "SOUTH"):
        if self.emergency_active:
            return
        self.emergency_direction = direction
        self.emergency_active = True

    def stop_lines(self, rect: pygame.Rect) -> dict[str, float]:
        return {"NORTH": rect.centery - 82, "SOUTH": rect.centery + 82, "EAST": rect.centerx + 82, "WEST": rect.centerx - 82}

    def spawn_pos(self, d: str, rect: pygame.Rect, index: int = 0):
        gap = 48 * index
        return {
            "NORTH": (rect.centerx - LANE_OFFSET, rect.y - 45 - gap),
            "SOUTH": (rect.centerx + LANE_OFFSET, rect.bottom + 45 + gap),
            "EAST": (rect.right + 45 + gap, rect.centery - LANE_OFFSET),
            "WEST": (rect.x - 45 - gap, rect.centery + LANE_OFFSET),
        }[d]

    def update(self, dt: float, rect: pygame.Rect):
        if self.paused: return
        dt *= self.speed; self.time += dt
        self.rush_factor = min(1.0, self.rush_factor + dt / 30.0) if self.rush_hour else max(0.0, self.rush_factor - dt / 12.0)
        self.last_rect = rect.copy()
        self._align_seeded(rect)
        for d in DIRECTIONS: self.last_green[d] += dt
        self._spawn(dt, rect)
        self._signals(dt)
        self._vehicles(dt, rect)
        self._check_emergency_clear(rect)
        for s in self.signals.values(): s.update(dt)

    def _align_seeded(self, rect):
        for d in DIRECTIONS:
            unplaced = [v for v in self.vehicles if v.direction == d and v.x == 0 and v.y == 0]
            for i, v in enumerate(unplaced):
                v.x, v.y = self.spawn_pos(d, rect, i + 1)

    def _vehicle_type(self):
        roll = self.rng.random()
        return "bus" if roll > .93 else "truck" if roll > .80 else "car"

    def _spawn(self, dt, rect):
        if self.emergency_active and not any(v.emergency for v in self.vehicles):
            x, y = self.spawn_pos(self.emergency_direction or "SOUTH", rect)
            self.vehicles.append(Vehicle(self.emergency_direction or "SOUTH", x, y, self.time, emergency=True))
        for d, base in BASE_SPAWN_RATES.items():
            rate = base * self.intensity * (1 + self.rush_factor * (RUSH_MULTIPLIERS[d] - 1))
            self.spawn_timers[d] -= dt * rate
            if self.spawn_timers[d] <= 0:
                x, y = self.spawn_pos(d, rect)
                if self._spawn_clear(d, x, y):
                    self.vehicles.append(Vehicle(d, x, y, self.time, vehicle_type=self._vehicle_type()))
                self.spawn_timers[d] = self.rng.uniform(0.75, 1.85)

    def _spawn_clear(self, d, x, y):
        return all(not (v.direction == d and abs(v.x - x) < 58 and abs(v.y - y) < 58) for v in self.vehicles)

    def _signals(self, dt):
        self.phase_remaining -= dt
        if self.phase_remaining > 0: return
        if self.phase == "GREEN":
            self.phase = "YELLOW"; self.phase_remaining = self.optimizer.config.yellow_time
            for d, s in self.signals.items(): s.set_state(YELLOW if d == self.current else RED)
        else:
            stats = self.road_stats()
            emergency = self.emergency_direction if self.emergency_active and self.mode == "SMARTFLOW" else None
            self.decision = self.optimizer.choose(stats, self.last_green, self.current, emergency) if self.mode == "SMARTFLOW" else self.traditional.next()
            self.current = self.decision.direction
            self.last_green[self.current] = 0.0
            self.phase = "GREEN"; self.phase_remaining = self.decision.green_time
            self.metrics.signal_changes += 1
            for d, s in self.signals.items(): s.set_state(GREEN if d == self.current else RED)

    def _vehicles(self, dt, rect):
        stops = self.stop_lines(rect)
        for d in DIRECTIONS:
            cars = sorted([v for v in self.vehicles if v.direction == d], key=lambda v: v.progress(), reverse=True)
            leader = None
            for v in cars:
                dist = v.distance_to_stop(stops)
                after_line = dist < -8
                red_stop = self.signals[d].state != GREEN and not after_line
                desired = v.target_speed or 75.0
                if red_stop and dist < 95:
                    desired = min(desired, max(0.0, (dist - 2) * 1.15))
                if leader:
                    gap = abs(leader.progress() - v.progress()) - leader.half_length - v.half_length
                    if gap < SAFE_GAP + 36:
                        desired = min(desired, max(0.0, (gap - SAFE_GAP) * 1.6))
                v.stopped = desired < 3.0 and (red_stop or leader is not None)
                if v.stopped: v.waiting_time += dt
                v.move(dt, desired)
                leader = v
        survivors = []
        for v in self.vehicles:
            if v.offscreen(rect.right, rect.bottom): self.metrics.record_clear(v.waiting_time)
            else: survivors.append(v)
        self.vehicles = survivors

    def _check_emergency_clear(self, rect):
        if self.emergency_active and not any(v.emergency for v in self.vehicles):
            self.emergency_active = False
            self.emergency_direction = None

    def road_stats(self) -> dict:
        stats = {}
        stops = self.stop_lines(getattr(self, "last_rect", pygame.Rect(300,80,660,565)))
        for d in DIRECTIONS:
            cars = [v for v in self.vehicles if v.direction == d]
            waiting = [v for v in cars if v.stopped or v.waiting_time > 0.1]
            queue = sum(1 for v in cars if v.distance_to_stop(stops) > -10 and (v.stopped or self.signals[d].state != GREEN))
            density = min(1.0, len(cars) / 16)
            stats[d] = {"total": len(cars), "waiting": len(waiting), "queue": queue, "density": density,
                        "avg_wait": sum(v.waiting_time for v in cars) / len(cars) if cars else 0.0,
                        "signal": self.signals[d].state, "green_time": self.signals[d].green_elapsed}
        return stats
