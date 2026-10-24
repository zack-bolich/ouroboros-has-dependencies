import importlib.util,sys,contextlib
from pathlib import Path
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fish',root.parent/'upstream-fish.py')
fish=importlib.util.module_from_spec(spec);spec.loader.exec_module(fish)
with (root/'seven.mur').open('w') as output,contextlib.redirect_stdout(output):
    interpreter=fish.Interpreter((root/'seven.fish').read_text())
    try:
        for _ in range(3000000):interpreter.move()
        raise RuntimeError('Fish step limit')
    except fish.StopExecution as exc:
        assert not exc.message,exc.message
assert (root/'seven.mur').read_bytes()==(root/'seven.expected.mur').read_bytes(), 'Fish output differs from independently constructed Muriel source'
print('Published Fish emitted', (root/'seven.mur').stat().st_size,'Muriel bytes')
