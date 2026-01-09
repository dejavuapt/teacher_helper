def is_port_connectable(host: str, port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        return soc.connect_ex((host, port)) == 0


# specific platfrom. sure that lsof installled
def kill_process_linux(port: int) -> None:
    import signal
    import subprocess
    import os

    try:
        com = f"lsof -t -i:{port}"
        pids = (
            subprocess.check_output(com, shell=True, stderr=subprocess.STDOUT)
            .decode()
            .strip()
            .split("\n")
        )
        for _ in pids:
            if _:
                os.kill(int(_), signal.SIGKILL)
    except Exception:
        pass
