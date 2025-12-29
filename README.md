# OpenGL Game (CSE423 Project)

An interactive game built with Python and OpenGL/GLUT, developed for BRACU CSE423. This repository contains the game entry point and a bundled OpenGL Python package used for rendering and input handling.

## **Overview**
- **Goal:** Real-time 2D/3D rendering with responsive controls and a simple game loop suitable for coursework and demos.
- **Entry Point:** See [project.py](project.py) — starts the window, initializes OpenGL, and runs the main loop.
- **Rendering:** Uses GLUT/freeglut for windowing + input callbacks; OpenGL fixed-function or shader-based rendering depending on configuration.
- **Input:** Keyboard and special keys handled via GLUT callbacks for movement, actions, and pausing.

## **Features**
- **Real-time loop:** Deterministic update-render cycle with frame timing.
- **Modular structure:** Clear separation of initialization, update, and draw stages.
- **Cross-platform OpenGL:** Works on Windows; can adapt to macOS/Linux with compatible GLUT.
- **Bundled OpenGL package:** Local [OpenGL](OpenGL) module included for convenience.

## **Tech Stack**
- **Language:** Python 3.12 (compatible with Python 3.10+)
- **Graphics:** OpenGL via GLUT/freeglut
- **Libraries:** Local [OpenGL](OpenGL) package (PyOpenGL-style modules); optional `PyOpenGL`/`PyOpenGL_accelerate` if you choose to install via pip

## **Getting Started**

### **Prerequisites**
- **Windows 10/11**
- **Python 3.12** (or 3.10+) available in PATH

### **Setup (recommended virtual environment)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If you prefer pip packages instead of the bundled OpenGL, install these:
pip install PyOpenGL PyOpenGL_accelerate
```

### **Run the game**
```powershell
python project.py
```

If you encounter issues related to GLUT DLLs, consult the bundled docs in [OpenGL/DLLS/freeglut_README.txt](OpenGL/DLLS/freeglut_README.txt) and ensure required DLLs are accessible via PATH or the working directory.

## **Controls**
- Typical defaults with GLUT:
	- **Arrow/WASD keys:** Movement or camera control.
	- **Space/Enter:** Action (jump/interact).
	- **Esc:** Quit.

Note: Exact bindings depend on the handlers defined in [project.py](project.py). Input is implemented using GLUT callbacks (`keyboard`, `special`, etc.).

## **Project Structure**
- **[project.py](project.py):** Main entry; sets up window, initializes OpenGL state, registers input callbacks, and runs the game loop.
- **[OpenGL](OpenGL):** Bundled Python modules resembling PyOpenGL, including subpackages for GL/GLU/GLUT and various extensions.
	- **[OpenGL/GLUT/freeglut.py](OpenGL/GLUT/freeglut.py):** GLUT/freeglut bindings (platform dependent).
	- **[OpenGL/DLLS](OpenGL/DLLS):** Documentation and notices for GLUT/freeglut and GLE.
- **[README.md](README.md):** Project documentation (this file).

## **Architecture**
- **Initialization:**
	- Create window and OpenGL context via GLUT.
	- Configure viewport, clear color, depth test, blending as needed.
- **Game Loop:**
	- Update: advance state based on elapsed time and inputs.
	- Render: draw the current frame using OpenGL calls.
	- Timing: target a stable framerate; adjust step using measured `Δt`.
- **Input Handling:**
	- Register keyboard/special callbacks to update player state and trigger actions.
- **Rendering Path:**
	- Fixed-function pipeline (glBegin/glEnd) or shader-based draw calls depending on the code path used.

## **Development**
- **Live run:** Use `python project.py` during development.
- **Assets/config:** If you add assets, keep paths relative to the repository root and load them at init time.
- **Performance tips:** Prefer batched draw calls and avoid per-frame allocations in tight loops.

## **Troubleshooting**
- **GLUT DLL not found:**
	- Ensure `freeglut.dll` is in PATH or alongside the executable.
	- See [OpenGL/DLLS/freeglut_README.txt](OpenGL/DLLS/freeglut_README.txt).
- **Black screen / no render:**
	- Verify context creation succeeded and viewport is set.
	- Confirm your GPU/driver supports the requested profile.
- **Input unresponsive:**
	- Check that GLUT callbacks are registered before entering the main loop.
	- Ensure your window is focused when testing inputs.

## **Extending the Game**
- **Add scenes/states:** Create simple state classes with `update()` and `draw()` methods.
- **Introduce physics:** Use a fixed update step (e.g., 60 Hz) and interpolate rendering.
- **Shaders:** Add GLSL programs and switch to VBOs for modern pipeline rendering.

## **FAQ**
- **Do I need to install PyOpenGL?**
	- The repository bundles an `OpenGL` package. Installing `PyOpenGL` is optional; it may improve performance when paired with `PyOpenGL_accelerate`.
- **Can I run on macOS/Linux?**
	- Yes, with platform-appropriate GLUT libraries and Python. Paths/DLLs will differ.

## **Credits**
- BRACU CSE423 course project. GLUT/freeglut and GLE notices in [OpenGL/DLLS](OpenGL/DLLS).
