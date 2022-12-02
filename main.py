# Copyright 2022 Sciforce Ukraine. All rights reserved.
import cProfile
import pathlib
import pstats
import sys
from utils.logger import jacka_logger

PROFILING = False


def _main():
    from rest_client import client
    import subprocess
    from time import sleep

    # If filename is provided, start the server & client
    if len(sys.argv) > 1:
        server = subprocess.Popen(
                ['python3', 'rest_server/server.py'],
                stdout=subprocess.PIPE,
                cwd=pathlib.Path().absolute())
        while True:
            stdout_line = server.stdout.readline().decode('utf-8')
            if stdout_line.startswith('SERVER ONLINE'):
                break
            # We use print instead of logging: it is raw Flask output
            print(stdout_line, end='')
        sleep(1)

        try:
            client.main(pathlib.Path(sys.argv[1]).absolute())
        finally:
            server.kill()
    else:
        # Otherwise start the server only and respond to requests
        import rest_server.server
        rest_server.server.main()


if __name__ == '__main__':
    ROUTINE = _main
    jacka_logger.info(f"Starting Jackalope, profiling: {PROFILING}")
    if PROFILING:
        with cProfile.Profile(builtins=False) as prof:
            ROUTINE()
        stats = pstats.Stats(prof)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats('stats.prof')
    else:
        ROUTINE()

    jacka_logger.info("Jackalope finished.")
