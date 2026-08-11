# Node.js Debugging Deep Dive (from node-inspect-debugger skill)

## Programmatic CDP (scripting from terminal)

When you want to automate — set many breakpoints, capture scope state, script a repro — use `chrome-remote-interface`:

```bash
npm i -g chrome-remote-interface
node --inspect-brk=9229 target.js &
```

Driver script (save as `/tmp/cdp-debug.js`):

```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames, reason }) => {
    const top = callFrames[0];
    console.log(`PAUSED: ${reason} @ ${top.url}:${top.location.lineNumber + 1}`);

    // Walk scopes for locals
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId, ownProperties: true,
        });
        for (const p of result) {
          console.log(`  ${scope.type}.${p.name} =`, p.value?.value ?? p.value?.description);
        }
      }
    }

    // Evaluate expression in paused frame
    const { result } = await Debugger.evaluateOnCallFrame({
      callFrameId: top.callFrameId,
      expression: 'typeof state !== "undefined" ? JSON.stringify(state) : "n/a"',
    });
    console.log('state =', result.value ?? result.description);

    await Debugger.resume();
  });

  await Runtime.enable();
  await Debugger.enable();

  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$', lineNumber: 119, columnNumber: 0,
  });

  await Runtime.runIfWaitingForDebugger();
})();
```

```bash
node /tmp/cdp-debug.js
```

## Debugging Hermes ui-tui

### Single Ink component under dev
```bash
cd /home/bb/hermes-agent/ui-tui
npm run build
node --inspect-brk dist/entry.js
# In another terminal:
node inspect -p <node pid>
```

### Running `hermes --tui`
```bash
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
kill -SIGUSR1 "$TUI_PID"
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'
node inspect ws://127.0.0.1:9229/<uuid>
```

## Vitest Tests Under Debugger

```bash
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism src/app/foo.test.tsx
# In another terminal: node inspect -p <pid>
```

Use `--no-file-parallelism` (vitest) or `--runInBand` (jest) so only one worker exists.

## Heap Snapshots & CPU Profiles

```javascript
// CPU profile for 5 seconds
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));

// Heap snapshot
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot({ reportProgress: false });
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```

## Common Pitfalls

1. **Wrong line numbers in TS.** Break in `dist/*.js` or use `--enable-source-maps`.
2. **`--inspect` vs `--inspect-brk`.** Use `--inspect-brk` to set breakpoints before code runs.
3. **Port collisions.** Default 9229. Use `--inspect=0` for random port.
4. **Child processes.** Use `NODE_OPTIONS='--inspect-brk'` to propagate.
5. **Background kills.** `Ctrl+C` out of `node inspect` leaves target paused. `cont` first or `kill` explicitly.
6. **Security.** `--inspect=0.0.0.0:9229` exposes arbitrary code execution. Always bind to 127.0.0.1.

## One-Shot Recipes

**"Why is this variable undefined?"**
```bash
node --inspect-brk script.js &
node inspect -p $!
sb('script.js', X)
cont
repl
> myVariable
```

**"What's the call path into this function?"**
```
sb('suspectFn')
cont
bt
```

**"This async chain hangs — where?"**
```
# Start with --inspect (no -brk), let it run to hang, then:
pause
bt
```
