# SmartFlow — Adaptive Traffic Management Simulation

SmartFlow is a Python/Pygame Computer Science Expo prototype demonstrating algorithmic adaptive traffic management at a simplified four-way city intersection. It compares predictable fixed-time traffic lights with an adaptive controller that reacts to measured queues, waiting time, and density.

> SmartFlow is an educational simulation/prototype. It is not a real-world traffic-control system and does not use real cameras, live sensor feeds, or machine learning.

## Features

- Four-way intersection with North, South, East, and West traffic.
- Continuous, moderately busy city traffic with smooth acceleration and deceleration.
- Lane-centered vehicles that queue behind red lights and behind other vehicles.
- Vehicle variety: cars, trucks, buses, and a distinct emergency vehicle.
- Traditional fixed-time signal mode for comparison.
- SmartFlow adaptive signal mode using live simulation data.
- Rush Hour Mode with gradually increasing, uneven traffic demand.
- Emergency Vehicle Mode that gives temporary priority to the emergency route.
- Live traffic dashboard with LOW / MEDIUM / HIGH density, signal state, and flow status.
- Performance comparison using actual simulated metrics.

## Traditional Traffic Control

Traditional mode rotates through North, East, South, and West with the same fixed green duration. It deliberately ignores live vehicle counts, queue length, density, and waiting time so students can compare it with adaptive control.

## SmartFlow Adaptive Control

SmartFlow observes the current simulation before every phase decision. It computes a priority score for each road and selects the eligible direction with the strongest need. Each green phase is followed by a yellow transition before another road receives green, preventing unsafe direct switching.

## Traffic Priority Algorithm

For each road, SmartFlow uses measured simulation data:

```text
score = waiting_vehicles * 3.4
      + total_vehicles * 1.1
      + queued_vehicles * 2.2
      + average_wait_seconds * 0.24
      + density * 19.0
      + fairness_bonus
```

Fairness grows while a road has not received green and receives an additional boost after extended starvation. Green times are clamped between sensible minimum and maximum values, while emergency priority temporarily overrides normal scoring for the emergency route.

## Realistic Traffic Simulation

Vehicles enter from all four directions at controlled, varied rates. They stay centered in their assigned lanes, maintain safe following gaps, slow smoothly for red/yellow phases, queue naturally at stop lines, and accelerate progressively when signals turn green. Rush hour increases arrival pressure gradually instead of instantly filling the road.

## Rush Hour Mode

Press `H` to toggle Rush Hour Mode. Traffic demand ramps up over roughly 30 seconds, with different multipliers by road so congestion develops unevenly. This makes queues and density indicators visibly change while keeping the simulation stable for a classroom demonstration.

## Emergency Vehicle Mode

Press `E` to activate an emergency demonstration in SmartFlow mode. A distinct emergency vehicle enters from the South route. SmartFlow detects the emergency route, safely transitions signals, gives that route temporary highest priority, lets the vehicle pass through the intersection, and then returns to normal adaptive behavior.

## Performance Comparison

The right-side panel compares Traditional and SmartFlow using live simulation data:

- Average waiting time
- Current waiting vehicles
- Vehicles cleared
- Maximum waiting time
- Signal changes
- Total vehicles processed

The comparison is intentionally honest: SmartFlow is expected to reduce unnecessary waiting under uneven traffic, but results can vary with the current traffic pattern.

## Architecture

```text
main.py                         Application loop and controls
simulation/vehicle.py           Vehicle movement, spacing, types, and drawing
simulation/signal.py            Signal states and green timing
simulation/traffic.py           Metrics data classes
simulation/intersection.py      Spawning, queues, signals, rush hour, emergency logic
algorithms/traffic_optimizer.py SmartFlow priority algorithm and fixed scheduler
ui/dashboard.py                 Dashboard, panels, metrics, and intersection rendering
```

## Requirements

- Python 3.13
- Pygame 2.6.1

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

- `SPACE` — start/pause the simulation
- `M` — switch displayed mode between Traditional and SmartFlow
- `R` — reset both simulations
- `UP/DOWN` — adjust simulation speed
- `LEFT/RIGHT` — adjust traffic intensity
- `H` — toggle Rush Hour Mode
- `E` — activate Emergency Vehicle Mode in SmartFlow
- `1/2/3/4` — manually inject North/East/South/West vehicles into the displayed simulation

## Suggested Expo Demonstration

1. Start the app and point out live traffic already moving through the intersection.
2. Show Traditional mode and explain fixed timing.
3. Let uneven queues develop naturally.
4. Switch to SmartFlow and show the priority score and reason panel.
5. Toggle Rush Hour Mode and watch density levels and queue lengths increase.
6. Trigger Emergency Vehicle Mode and show temporary emergency priority.
7. Watch SmartFlow return to normal adaptive decisions after the emergency clears.

## Limitations

- Straight-through movement only; turning lanes are not modeled.
- Synthetic traffic arrivals rather than real sensors or camera detection.
- Simplified vehicle physics and simplified road geometry.
- Single intersection only; no city-wide coordination.
- The adaptive controller is deterministic scoring, not machine learning.

## Future Improvements

- Turning lanes and pedestrian crossings.
- Multiple coordinated intersections.
- More detailed vehicle behavior and route choices.
- Exportable metrics for science-fair charts.
- Optional sensor/camera integration for advanced demonstrations.
