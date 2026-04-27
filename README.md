# Stress Test

Stress Test is a 2D train logistics game built with Python and Pygame. The project simulates railway construction, train movement, and transport flow on a node-and-edge network, with early multiplayer networking components and supporting tools under active development.

## Team

- Hugo
- Ella
- Spencer
- Aryan

## Project Overview

The game loop is centered around building track, managing train routes, and visualizing movement in a large scrolling world. Core systems are designed around graph-based pathing and simulation-friendly entities.

Current gameplay foundation includes:

- Interactive home, pause, and quit screens.
- Camera movement and zoom controls.
- Track placement via node and edge creation.
- Depot placement and train spawning foundations.
- Train and car movement over connected graph edges.
- Render stack composition for world objects.
- Standalone websocket server/client prototypes in the networking module.

## Current State

This is an active in-progress project. Some modules, tools, and test files are placeholders or partially implemented. The current focus appears to be core gameplay systems and architecture scaffolding for future expansion.

## Tech Stack

- Python
- pygame-ce (rendering, input, game loop)
- websockets (multiplayer/network prototypes)
- Supporting scientific and utility packages listed in requirements.txt

## Repository Layout

- main.py: Application entry point.
- app/game.py: Main game controller and frame loop.
- app/core/: Shared simulation systems (graph, constants, events, state/time scaffolding).
- app/entities/: Gameplay domain entities (train, cars, stations, lines, depot, passengers/cargo).
- app/avatars/: Render avatars/sprites for trains, track, stations, and cars.
- app/view/: Camera and menu/screen UI code.
- app/networking/: Websocket server/client and a multiplayer test window.
- tests/: Test and experimental validation scripts.
- tools/: Project utility scripts (currently scaffolded).
- assets/: Audio, maps, shaders, fonts, and sprite resources.
- save/: Runtime and config persistence artifacts.

## Setup

### 1. Clone and enter the project

```powershell
git clone <your-repo-url>
cd Stress-Test
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

## Running the Game

```powershell
python main.py
```

The game opens a Pygame window and starts at the home screen.

## Controls

- W, A, S, D: Move camera.
- 1: Zoom in.
- 2: Zoom out.
- Top toolbar buttons:
	- Pause (||)
	- Quit (X)
	- Place Track (toggle track placement mode)

## Multiplayer Prototype

The networking package includes a websocket prototype that is separate from the main game loop integration.

Server:

```powershell
python -m app.networking.server
```

Client:

```powershell
python -m app.networking.client
```

What it currently does:

- Assigns each connecting client a unique ID.
- Broadcasts position updates between clients.
- Renders connected players as colored dots in a test window.

## Testing

Test files exist under tests, but coverage is currently mixed between placeholders and script-based validation.

Run available tests/scripts with:

```powershell
python -m pytest tests
```

If pytest is not installed in your environment, install it first:

```powershell
pip install pytest
```

You can also run selected visual scripts directly, for example:

```powershell
python tests/test_train_render.py
```

## Development Notes

- The project includes strong type-hint and docstring intent across many modules.
- Several files are intentionally scaffolded for future implementation.
- requirements.txt is encoded in UTF-16 in this repository state; keep that in mind if editing dependency files with external tooling.

## Contributing

1. Create a feature branch.
2. Keep changes focused and documented.
3. Add or update tests where practical.
4. Open a pull request with a short summary of gameplay and technical impact.

## License

This project is released under the MIT License.
See LICENSE for full terms.
