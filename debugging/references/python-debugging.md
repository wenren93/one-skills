# Python Debugging Deep Dive (from python-debugpy skill)

## Recipe: Debug a pytest test

```bash
# Drop to pdb on failure:
pytest tests/path/test_file.py::test_name --pdb

# Drop to pdb at START of test:
pytest tests/path/test_file.py::test_name --trace

# Show locals without pdb:
pytest tests/path/test_file.py --showlocals --tb=long
```

pdb does NOT work under xdist. Add `-p no:xdist` or run single test with `-n 0`.

## Recipe: Post-mortem with wrapper

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

Or set global hook:
```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

## Recipe: Remote debug — attach to running process

### Pattern A: Source-edit — wait at launch
```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```

### Pattern B: Launch with `-m debugpy`
```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py
```

### Pattern C: Attach to already-running process
```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
```
Some kernels block ptrace: `echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope`

### Client Options

**Option 1: remote-pdb (cleanest for terminal agents)**
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
# Then: nc 127.0.0.1 4444
```

**Option 2: VS Code launch.json**
```json
{
  "name": "Attach to Hermes",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "127.0.0.1", "port": 5678 },
  "justMyCode": false
}
```

## Debugging Hermes-specific Processes

### Tests
Always add `-p no:xdist` or run single tests.

### `run_agent.py` / CLI
Add `breakpoint()` near the suspect line, run `hermes` normally.

### `tui_gateway` subprocess
Source-edit with `debugpy.listen` + `wait_for_client`, or use `remote-pdb` at a specific handler.

### `_SlashWorker` subprocess
Use `remote-pdb` with `set_trace()` inside the worker's exec path.

## Common Pitfalls

1. **pdb under pytest-xdist silently does nothing.** Always `-p no:xdist`.
2. **`breakpoint()` in CI hangs.** Never commit it.
3. **`PYTHONBREAKPOINT=0`** disables all breakpoints.
4. **debugpy.listen blocks only with `wait_for_client()`.**
5. **Attach to PID fails on hardened kernels.** Fix ptrace_scope or launch under debugpy.
6. **Threads.** pdb only debugs current thread. Use debugpy for multithreaded.
7. **asyncio.** pdb works in coroutines but `await` inside pdb needs Python 3.13+.
8. **Forking/multiprocessing.** pdb does not follow forks.

## Verification

- After `pip install debugpy`: `python -c "import debugpy; print(debugpy.__version__)"`
- For remote debug: `ss -tlnp | grep 5678`
- Post-debug cleanup: `rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py`
