from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    subtitle: str
    seed: int
    # The demo runs for 9 real seconds while simulating 18 seconds of traffic.
    # This keeps the expo fast without starving the adaptive algorithm of enough events to react.
    duration: float = 18.0
    real_seconds_per_test: float = 9.0
    initial_counts: dict[str, int] = field(default_factory=dict)
    base_rates: dict[str, float] = field(default_factory=dict)
    changing_rates: tuple[float, dict[str, float]] | None = None
    rush: bool = False
    emergency_direction: str | None = None
    emergency_at: float | None = None
    explanation: str = ""

    @property
    def sim_speed(self) -> float:
        return self.duration / self.real_seconds_per_test

SCENARIOS: dict[str, Scenario] = {
    "rush": Scenario(
        key="rush", title="RUSH HOUR", subtitle="Heavy traffic during peak time", seed=48291,
        # Deliberately realistic imbalance: SOUTH is the busiest approach, so an adaptive
        # controller has a clear decision to make instead of following the fixed rotation.
        initial_counts={"NORTH": 5, "EAST": 4, "SOUTH": 10, "WEST": 3},
        base_rates={"NORTH": .45, "EAST": .25, "SOUTH": .85, "WEST": .20}, rush=True,
        explanation="Traffic became heavy on several roads. SmartFlow responded to the growing queues and gave priority where more vehicles were waiting.",
    ),
    "emergency": Scenario(
        key="emergency", title="EMERGENCY", subtitle="An ambulance needs priority", seed=91364,
        initial_counts={"NORTH": 4, "EAST": 5, "SOUTH": 5, "WEST": 4},
        base_rates={"NORTH": .55, "EAST": .58, "SOUTH": .70, "WEST": .50}, emergency_direction="SOUTH", emergency_at=3.5,
        explanation="Traditional continued its normal signal cycle. SmartFlow detected the emergency and temporarily prioritized the ambulance route.",
    ),
    "uneven": Scenario(
        key="uneven", title="UNEVEN TRAFFIC", subtitle="One road becomes much busier", seed=27440,
        initial_counts={"NORTH": 2, "EAST": 10, "SOUTH": 3, "WEST": 6},
        base_rates={"NORTH": .25, "EAST": .90, "SOUTH": .25, "WEST": .45},
        explanation="One road had much more traffic than the others. SmartFlow recognized the imbalance and gave that road priority.",
    ),
    "changing": Scenario(
        key="changing", title="CHANGING TRAFFIC", subtitle="Traffic demand shifts between roads", seed=76108,
        initial_counts={"NORTH": 4, "EAST": 8, "SOUTH": 3, "WEST": 4},
        base_rates={"NORTH": .38, "EAST": .80, "SOUTH": .30, "WEST": .35},
        # The busiest approach changes halfway through the simulated test.
        changing_rates=(9.0, {"NORTH": .32, "EAST": .30, "SOUTH": .34, "WEST": 1.00}),
        explanation="The busiest road changed during the test. SmartFlow changed its priority as the traffic situation changed.",
    ),
}

@dataclass
class ScenarioResult:
    mode: str
    avg_wait: float
    vehicles_cleared: int
    vehicles_waiting: int
    max_wait: float
    signal_changes: int
    emergency_wait: float | None = None
    emergency_clear_time: float | None = None
    priority_changes: int = 0
    smart_steps: list[str] = field(default_factory=list)

class ScenarioRunner:
    def __init__(self):
        self.state = "idle"
        self.scenario: Scenario | None = None
        self.elapsed_real = 0.0
        self.message_timer = 0.0
        self.results: dict[str, ScenarioResult] = {}
        self.active_sim = None

    def open_lab(self):
        self.state = "menu"
        self.scenario = None
        self.results = {}
        self.active_sim = None

    def start(self, scenario: Scenario, traditional, smart, rect):
        self.scenario = scenario
        self.results = {}
        self._prepare(traditional, "TRADITIONAL", rect)
        self._prepare(smart, "SMARTFLOW", rect)
        self.active_sim = traditional
        self.state = "intro"
        self.elapsed_real = 0.0
        self.message_timer = 1.7

    def _prepare(self, sim, mode: str, rect):
        sim.configure_scenario(self.scenario, mode)
        sim.speed = self.scenario.sim_speed
        sim.paused = True
        sim.update(0, rect)

    def update(self, dt, traditional, smart, rect):
        if self.state not in {"intro", "traditional", "resetting", "smartflow"} or not self.scenario:
            return None
        if self.state == "intro":
            self.message_timer -= dt
            if self.message_timer <= 0:
                traditional.paused = False
                self.active_sim = traditional
                self.state = "traditional"
                self.elapsed_real = 0.0
        elif self.state == "traditional":
            self.elapsed_real += dt
            if traditional.time >= self.scenario.duration:
                traditional.paused = True
                self.results["TRADITIONAL"] = traditional.scenario_result()
                self._prepare(smart, "SMARTFLOW", rect)
                self.active_sim = smart
                self.state = "resetting"
                self.message_timer = 0.7
        elif self.state == "resetting":
            self.message_timer -= dt
            if self.message_timer <= 0:
                smart.paused = False
                self.state = "smartflow"
                self.elapsed_real = 0.0
        elif self.state == "smartflow":
            self.elapsed_real += dt
            if smart.time >= self.scenario.duration:
                smart.paused = True
                self.results["SMARTFLOW"] = smart.scenario_result()
                self.state = "results"
        return self.active_sim

    def return_live(self, traditional, smart):
        self.state = "idle"
        self.active_sim = None
        traditional.reset()
        smart.reset()
        traditional.paused = smart.paused = False
