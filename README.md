# Stress Test

Stress Test is a 2D train logistics game built with Python and Pygame. The current repository focuses on the single-player gameplay loop, track-building, route navigation, train movement, and the UI scaffolding around those systems.

## Team

- Hugo
- Ella
- Spencer
- Aryan

## Overview

The game is organized around a node-and-edge world graph. Players track, make lines, assign trains to lines, and watch trains move across the network while passengers and cargo are handled by the entity layer.

Current gameplay features include:

- Home, pause, quit, and depot screens.
- Camera movement and zoom.
- Track placement on a graph of nodes and edges.
- Line creation and train assignment
- Passenger spawning, boarding, and paying.
- Train, car, and station entity modeling.
- Render stack composition for world objects.

## Current State

This codebase is still in active development. Some modules are fully functional, while others remain scaffolded or partially implemented.

The strongest areas right now are:

- Core graph and pathfinding logic in `app/core/`.
- Train, car, station, city, line, and cargo entities in `app/entities/`.
- Sprite and avatar classes in `app/avatars/`.
- Basic UI and camera systems in `app/view/`.

Some parts are still intentionally unfinished:

- A few files under `tools/` are placeholders.
- Several files under `tests/` are empty or script-style validation helpers rather than full automated tests.
- A handful of type-check warnings still exist in the codebase and are unrelated to the docstring cleanup.

## Tech Stack

- Python
- pygame-ce for rendering, input, and the main loop
- Pygame-based sprite composition and surface rotation
- Utility and test tooling listed in `requirements.txt`

## Repository Layout

- `main.py`: Application entry point.
- `app/game.py`: Main game controller and frame loop.
- `app/core/`: Graph and pathfinding primitives.
- `app/entities/`: Gameplay entities such as trains, cars, stations, cities, lines, passengers, and cargo.
- `app/avatars/`: Sprite and avatar classes for world objects.
- `app/view/`: Camera and menu/screen UI helpers.
- `tests/`: Smoke tests, validation scripts, and placeholder test files.
- `tools/`: Utility entry points for build and editor workflows.
- `assets/`: Sprite and other art resources.
- `save/`: Runtime configuration and persistence data.

## Setup

### 1. Clone and enter the project

```powershell
git clone https://github.com/Hugo14156/Stress-Test.git
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

- `W`, `A`, `S`, `D`: Move camera.
- `1`: Zoom in.
- `2`: Zoom out.
- Top toolbar buttons:
  - Pause (`||`)
  - Quit (`X`)
  - Place Track
  - Make Line

## Experimental Multiplayer

The separate networking branch contains an experimental multiplayer mode. It is not part of this repository's default single-player loop, but it exists as a prototype for client/server-style play and networked position updates. To use it,
follow the instructions below. 

### Switching to networking branch

```powershell
git switch networking
```

### Pulling latest version

```powershell
git pull
```
From there, a server should run `server.py`.

### Starting server

```powershell
python -m app.networking.server
```

Then, all clients should run `client.py`

### Starting client

```powershell
python -m app.networking.client
```
On startup, clients will attempt to automatically connect to a server. If this process fails, you will be prompted to
enter an address. The address will be found printed in the terminal running the server. 

If you would like to be both the server and the client, run the server in one terminal, then make a new terminal and run
client in there.

## Testing

The `tests/` folder currently mixes placeholder files, small smoke tests, and a few visual scripts.

Run available tests/scripts with:

```powershell
python -m pytest tests
```

If `pytest` is not installed in your environment, install it first:

```powershell
pip install pytest
```

You can also run selected visual scripts directly, for example:

```powershell
python tests/test_train_render.py
```

## Development Notes

- Many modules already have class and method docstrings.
- Several files are intentionally scaffolded for future implementation.
- `requirements.txt` is encoded in UTF-16 in this repository state, so keep that in mind if editing dependency files with external tooling.

## Contributing

1. Create a feature branch.
2. Keep changes focused and documented.
3. Add or update tests where practical.
4. Open a pull request with a short summary of gameplay and technical impact.

## License

This project is released under the MIT License.
See `LICENSE` for full terms.
