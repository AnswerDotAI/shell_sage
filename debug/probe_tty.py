import os, sys
print("stdin isatty:", sys.stdin.isatty())
print("stdout isatty:", sys.stdout.isatty())
print("stderr isatty:", sys.stderr.isatty())
for fd in (0,1,2):
    try:
        print(fd, "ttyname:", os.ttyname(fd))
    except OSError:
        print(fd, "ttyname:", None)
try:
    fd = os.open("/dev/tty", os.O_RDWR)
    print("can open /dev/tty: YES")
    os.close(fd)
except OSError as e:
    print("can open /dev/tty: NO ->", e)