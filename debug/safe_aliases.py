from subprocess import check_output as co, DEVNULL

print (co("uv run python debug/probe_tty.py".split(), stderr=DEVNULL, stdin=DEVNULL, text=True, start_new_session=True ))
aliases = co(["zsh", '-ic', 'alias'], text=True,  
         start_new_session=True # to call setsid() and sever connection to /dev/tty
).strip()
print ("Found ", len(aliases.split()), "aliases")