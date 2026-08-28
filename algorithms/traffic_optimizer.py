from dataclasses import dataclass

DIRECTIONS = ("NORTH", "EAST", "SOUTH", "WEST")

@dataclass
class OptimizerConfig:
    waiting_weight: float = 3.4
    total_weight: float = 1.1
    wait_time_weight: float = 0.24
    density_weight: float = 19.0
    queue_weight: float = 2.2
    starvation_weight: float = 0.42
    min_green: float = 8.0
    max_green: float = 26.0
    yellow_time: float = 2.5
    starvation_seconds: float = 32.0

@dataclass
class Decision:
    direction: str
    green_time: float
    scores: dict[str, float]
    reason: str

class SmartFlowOptimizer:
    """Deterministic adaptive signal selector based on measured simulation data."""
    def __init__(self, config: OptimizerConfig | None = None):
        self.config = config or OptimizerConfig()

    def choose(self, road_stats: dict, time_since_green: dict[str, float], current_green: str | None,
               emergency_direction: str | None = None) -> Decision:
        scores: dict[str, float] = {}
        for direction in DIRECTIONS:
            stats = road_stats[direction]
            starvation_bonus = min(time_since_green.get(direction, 0), 65) * self.config.starvation_weight
            if time_since_green.get(direction, 0) >= self.config.starvation_seconds:
                starvation_bonus += 18.0
            score = (
                stats["waiting"] * self.config.waiting_weight
                + stats["total"] * self.config.total_weight
                + stats.get("queue", 0) * self.config.queue_weight
                + stats["avg_wait"] * self.config.wait_time_weight
                + stats["density"] * self.config.density_weight
                + starvation_bonus
            )
            if direction == current_green:
                score *= 0.78
            if emergency_direction == direction:
                score += 1000.0
            scores[direction] = round(score, 2)

        direction = max(DIRECTIONS, key=lambda d: (scores[d], time_since_green.get(d, 0), road_stats[d]["waiting"]))
        stats = road_stats[direction]
        if emergency_direction == direction:
            green_time = 18.0
            reason = "Emergency vehicle detected on this route; temporary highest priority"
        else:
            pressure = stats["waiting"] + stats.get("queue", 0) * 0.8 + stats["density"] * 9 + min(stats["avg_wait"] / 4, 8)
            green_time = max(self.config.min_green, min(self.config.max_green, self.config.min_green + pressure * 0.85))
            reason_bits = []
            if stats["waiting"] >= max(1, max(road_stats[d]["waiting"] for d in DIRECTIONS)):
                reason_bits.append("highest waiting vehicles")
            if stats["avg_wait"] >= max(road_stats[d]["avg_wait"] for d in DIRECTIONS):
                reason_bits.append("longest waiting time")
            if stats["density"] >= max(road_stats[d]["density"] for d in DIRECTIONS):
                reason_bits.append("highest traffic density")
            if time_since_green.get(direction, 0) >= self.config.starvation_seconds:
                reason_bits.append("fairness boost")
            reason = " + ".join(reason_bits[:3]) or "best combined demand score"
        return Decision(direction, round(green_time, 1), scores, reason)

class TraditionalScheduler:
    def __init__(self, fixed_green: float = 12.0):
        self.fixed_green = fixed_green
        self.index = -1

    def next(self) -> Decision:
        self.index = (self.index + 1) % len(DIRECTIONS)
        direction = DIRECTIONS[self.index]
        return Decision(direction, self.fixed_green, {}, "Fixed-time rotation ignores live density")
