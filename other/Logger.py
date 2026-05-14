
verbose = 0
info = 1
warning = 2
error = 3
fatal = 4

def log(*args, type:int=info):
    print(*args)