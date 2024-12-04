# Ambient Assisted Living for Long-term Monitoring and Interaction (ALMI)

This repository provides a modular framework for simulating and analyzing cooperative tasks between a signle agent and a signle human in a graph-based environment. Developed within the scope of the [ALMI](https://www.york.ac.uk/assuring-autonomy/about/aaip/demonstrators/safe-robots-assisted-living/) project, it leverages [PRISM model checker](https://www.prismmodelchecker.org/) for path validation and probability modeling, enabling robust testing of mission execution under various conditions. The framework includes tools for environment setup, mission planning, simulation execution, and result analysis.

---

## Overview

### Top-Level Files

#### [`Coop_Task.py`](./Coop_Task.py)
- **Purpose**: Coordinates cooperative task simulations involving a single agent and a single human. Defines simulation parameters and runs tasks iteratively across multiple episodes.
- **Interactions**: Uses utility modules from the [`Utilities`](./Utilities/) folder to set up environments, manage missions, and execute simulations.

#### [`Coop_Task_Single.py`](./Coop_Task_Single.py)
- **Purpose**: Simplified version of [`Coop_Task.py`](./Coop_Task.py) for running single, predefined simulations.
- **Interactions**: Similar to [`Coop_Task.py`](./Coop_Task.py) but focuses on testing specific scenarios.

#### [`Data_Analysis.py`](./Data_Analysis.py)
- **Purpose**: Provides tools to analyze simulation results and individual episodes interactively.
- **Interactions**: Reads simulation data stored in directories and interacts with result files generated during simulations.

---

### Top-Level Directories
- **[PRISM](./PRISM)**: Contains models, state definitions, and transition data for simulations. These files are used with [PRISM](https://www.prismmodelchecker.org/) to validate paths, analyze state transitions, and support decision-making processes.
- **[Utilities](./Utilities)**: Contains core modules for environment setup, mission creation, simulation, and [PRISM](https://www.prismmodelchecker.org/) integration.

---

### Utilities Folder

#### [`Environment.py`](./Utilities/Environment.py)
- **Purpose**: Defines the `Graph` class to create and manage environments.
- **Features**: Constructs maps, defines connections, and implements pathfinding algorithms.
- **Used By**: [`Coop_Task.py`](./Coop_Task.py), [`Coop_Task_Single.py`](./Coop_Task_Single.py).

#### [`Maps.py`](./Utilities/Maps.py)
- **Purpose**: Provides predefined environments and risk matrices.
- **Features**: Defines connection details and safe zones for agent and human.
- **Used By**: [`Environment.py`](./Utilities/Environment.py).

#### [`Mission.py`](./Utilities/Mission.py)
- **Purpose**: Manages mission creation, breakdown, and optimization.
- **Features**: Creates sub-missions and applies pathfinding for task execution.
- **Used By**: [`Coop_Task.py`](./Coop_Task.py).

#### [`Prism.py`](./Utilities/Prism.py)
- **Purpose**: Interfaces with [PRISM](https://www.prismmodelchecker.org/) for model checking and path validation.
- **Features**: Generates [PRISM](https://www.prismmodelchecker.org/) models and validates paths.
- **Used By**: [`Coop_Task.py`](./Coop_Task.py), [`Simulate.py`](./Utilities/Simulate.py).

#### [`Simulate.py`](./Utilities/Simulate.py)
- **Purpose**: Executes simulation logic for agent and human.
- **Features**: Handles decision-making, path updates, and logging.
- **Used By**: [`Coop_Task.py`](./Coop_Task.py).

---

## Workflow and Interaction

1. **Environment Setup**:
   - [`Utilities/Maps.py`](./Utilities/Maps.py) provides predefined environments.
   - [`Utilities/Environment.py`](./Utilities/Environment.py) uses these maps to construct a graph-based environment.

2. **Mission Definition**:
   - [`Utilities/Mission.py`](./Utilities/Mission.py) creates and optimizes tasks for agents.

3. **Simulation Execution**:
   - [`Coop_Task.py`](Coop_Task.py) or [`Coop_Task_Single.py`](Coop_Task_Single.py) orchestrates simulations.
   - [`Utilities/Simulate.py`](./Utilities/Simulate.py) handles step-by-step agent and human interactions.

4. **Path Validation**:
   - [`Utilities/Prism.py`](./Utilities/Prism.py) validates paths and actions via [PRISM](https://www.prismmodelchecker.org/).

5. **Data Analysis**:
   - [`Data_Analysis.py`](Data_Analysis.py) processes simulation results to extract insights.

6. **PRISM Integration**:
   - Files in the [PRISM](./PRISM) folder are utilized for advanced path validation and state analysis.

---
