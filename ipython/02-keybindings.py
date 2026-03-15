# ~/.ipython/profile_default/startup/02-keybindings.py
from subprocess import run
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import HasFocus
from prompt_toolkit.enums import DEFAULT_BUFFER

def _ssage(event):
    buf = event.app.current_buffer
    res = run(["ssage_extract", "--do_print", buf.text or "0"], capture_output=True, text=True)
    buf.text = res.stdout.rstrip('\n')
    buf.cursor_position = len(buf.text)

ip = get_ipython()
if ip.pt_app: ip.pt_app.key_bindings.add(Keys.ControlJ, filter=HasFocus(DEFAULT_BUFFER))(_ssage)
