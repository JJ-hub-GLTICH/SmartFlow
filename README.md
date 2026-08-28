# SmartFlow — Adaptive Traffic Management Simulation

SmartFlow is a Python/Pygame Computer Science Expo prototype that compares traditional fixed-time traffic lights with an adaptive signal controller at a four-way intersection.

## Problem Statement

Fixed-time signals follow a preset cycle even when traffic is uneven. That can make a congested road wait while an empty road receives green time.

## Traditional Traffic System

Traditional mode rotates North, East, South, and West using the same fixed green duration. It does not inspect vehicle counts, waiting time, or density.

## SmartFlow Solution

SmartFlow mode measures each road's queue and calculates a deterministic priority score. The highest scoring road receives the next green light, and the green duration expands or shrinks within safe limits.

## Algorithm

For every signal cycle, SmartFlow computes:

```text
score = waiting_vehicles * 3.0
      + total_vehicles * 1.2
      + average_wait_seconds * 0.18
      + density * 18.0
      + fairness_bonus
```

Fairness grows as a road waits and receives an extra boost after 34 seconds without green. Green time is clamped between 7 and 24 seconds. Every change passes through a 2.5 second yellow phase, so lights never jump directly from one green road to another.

## Architecture

```text
main.py                         Application loop and controls
simulation/vehicle.py           Vehicle movement and drawing
simulation/signal.py            Signal states
simulation/traffic.py           Metrics data classes
simulation/intersection.py      Spawning, vehicle rules, signal cycle
algorithms/traffic_optimizer.py SmartFlow priority algorithm and fixed scheduler
ui/dashboard.py                 Dashboard and intersection rendering
```

## Technologies

- Python 3
- Pygame
- Standard Python libraries only

## Install

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

- `SPACE` start/pause
- `M` switch displayed mode between Traditional and SmartFlow
- `R` reset both simulations
- `UP/DOWN` adjust simulation speed
- `LEFT/RIGHT` adjust traffic intensity
- `1/2/3/4` manually inject North/East/South/West vehicles into the displayed simulation

## Traditional vs SmartFlow

Both simulations run from the same reproducible demo traffic pattern: North heavy, South medium, East and West low. The performance panel is calculated from actual simulated vehicles cleared, waiting cars, average wait, maximum wait, and signal changes.

## Limitations

This is an educational simulation, not real traffic infrastructure. It uses simplified straight-through vehicle movement, synthetic arrivals, and deterministic scoring rather than physical sensors or machine learning.

## Future Improvements

- Real traffic sensors
- Camera-based vehicle detection
- Real-time traffic data
- Machine-learning-based prediction
- Multi-intersection coordination

## Expo Demonstration

1. Run `python main.py`.
2. Watch Traditional mode continue fixed rotations even when North becomes congested.
3. Press `M` to display SmartFlow.
4. Explain that SmartFlow reads traffic density, waiting cars, and waiting duration, then chooses the highest priority road while fairness prevents starvation.
5. Use the performance panel to compare measured outcomes from the running scenario.
