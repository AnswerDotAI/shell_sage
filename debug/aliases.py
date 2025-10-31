from subprocess import check_output as co 
print(co("uv run python debug/probe_tty.py".split(),  text=True ))
aliases = co(["zsh", '-ic', 'alias'], text=True).strip()
print ("Found ", len(aliases.split()), "aliases")
