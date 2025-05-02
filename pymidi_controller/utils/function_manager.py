import sys
import importlib.util
from types import ModuleType
from pymidi_controller.utils.config_manager import FUNC_DIR

CACHE: dict[str, tuple[ModuleType, float]] = {}  # name → (module, mtime)

def _ensure_path():
    """Ensure FUNC_DIR is on sys.path (for relative imports inside user modules)."""
    if FUNC_DIR.exists() and str(FUNC_DIR) not in sys.path:
        sys.path.insert(0, str(FUNC_DIR))

def _load_module_from_path(name: str, path: str) -> ModuleType:
    """Safely load a module from a specific file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module '{name}' from {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise RuntimeError(f"Error while executing module '{name}': {e}")
    return module

def load_user_function(name: str):
    """Loads and returns the `main()` function from a user-defined module."""
    _ensure_path()

    # Locate the file on disk
    file_py  = FUNC_DIR / f"{name}.py"
    file_pkg = FUNC_DIR / name / "__init__.py"
    file_alt = FUNC_DIR / name / "main.py"

    filepath = None
    for candidate in (file_py, file_pkg, file_alt):
        if candidate.exists():
            filepath = candidate
            break

    if filepath is None:
        raise FileNotFoundError(f"No module '{name}' found in {FUNC_DIR}")

    mtime = filepath.stat().st_mtime

    # Load (or reload) the module from file
    if name in CACHE:
        _, cached_mtime = CACHE[name]
        if mtime > cached_mtime:
            module = _load_module_from_path(name, str(filepath))  # reload if changed
            CACHE[name] = (module, mtime)
        else:
            module = CACHE[name][0]  # reuse cached module
    else:
        module = _load_module_from_path(name, str(filepath))
        CACHE[name] = (module, mtime)

    if not hasattr(module, "main") or not callable(module.main):
        raise RuntimeError(f"User module '{name}' must define a callable main() function")

    return module.main

def list_functions():
    """Prints available function modules in FUNC_DIR."""
    _ensure_path()
    if not FUNC_DIR.exists():
        print(f"Function directory not found: {FUNC_DIR}")
        return

    print("Available functions:")
    for path in FUNC_DIR.iterdir():
        if path.is_dir() and ((path / "__init__.py").exists() or (path / "main.py").exists()):
            print(f"  - {path.name}")
        elif path.suffix == ".py":
            print(f"  - {path.stem}")
