import psutil
import argparse
import pathlib
from colorama import init, Fore, Style


class PSArgs():

    def __init__(self, procname, printcmd=False, printmods=False, cmdline=''):
        self.procname = procname
        self.printmods = printmods
        self.printcmd = printcmd
        self.cmdline = cmdline
        self.run()

    def run(self):
        print('[*] ---------------------------------------------')
        print(f'[*] Processes, filter string [{Fore.CYAN}{self.procname}{Fore.RESET}]')
        print('[*] ---------------------------------------------')
        for p in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                pid = p.info['pid']
                name = p.info['name']
                cmdline = p.info['cmdline']
                rss = p.info['memory_info'].rss // 1024
            except:
                continue
            if self.procname and self.procname.lower() not in name.lower():
                continue
            if self.cmdline and \
                    self.cmdline.lower() not in ' '.join(cmdline).lower():
                continue

            print(f'[+] {Style.BRIGHT}{name[:25]:<25s} '
                + f'{Fore.RED}PID:{pid:6d}{Fore.RESET} '
                + f'{Fore.GREEN}{rss:12,} MBytes{Fore.RESET}'
                + f'{Style.RESET_ALL}')

            try:
                if self.printcmd:
                    self.print_cmdline_args(p)
                if self.printmods:
                    self.print_loaded_modules(p)
            except Exception:
                continue

    def print_cmdline_args(self, p):
        cmdline = p.info['cmdline']
        if cmdline is None:
            return
        print(f'[+] Command Line Args:')
        line = ''
        for a in cmdline:
            if len(line) > 50:
                print(f'    {Fore.CYAN}{line}{Fore.RESET}')
                line = ''
            line += f'{a} '
        if line:
            print(f'    {Fore.CYAN}{line}{Fore.RESET}')
        print('')

    def print_loaded_modules(self, p):
        mmaps = p.memory_maps()
        print(f'[+] loaded modules:')
        for mod in sorted(mmaps, key=lambda x: x.rss, reverse=True):
            m = pathlib.Path(mod.path)
            if m.suffix != '.dll':
                continue
            rss = mod.rss / 1024
            name = m.name.lower()
            if len(name) > 40:
                name = f'... {name[len(name) - 36:]}'
            print(f'    {Fore.MAGENTA}{name:<40s} {rss:8,.0f} MB{Fore.RESET}')
        print('')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--procname', default='',
        help='match a specific process name')
    parser.add_argument(
        '-lm', default=False, action='store_true',
        help='list loaded modules')
    parser.add_argument(
        '-lc', default=False, action='store_true',
        help='list command line params')
    parser.add_argument(
        '-cmdline', default='', help='command line filter')
    args = parser.parse_args()
    PSArgs(
        args.procname, printmods=args.lm,
        printcmd=args.lc, cmdline=args.cmdline)
