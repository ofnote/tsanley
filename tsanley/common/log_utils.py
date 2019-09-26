
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

colmap = {
    'green': bcolors.OKGREEN,
    'blue': bcolors.OKBLUE,
    'red': bcolors.FAIL
}
def debug_log (*s, level=0):
    if level >=2: log (*s, style=bcolors.BOLD)

def log (*s, style=bcolors.OKBLUE):
    if style in colmap: style = colmap[style] 
    print(style, bcolors.BOLD, *s, bcolors.ENDC)
