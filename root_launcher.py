#!/usr/bin/env python
import os
import subprocess

# * The default os set to 'LOCAL' values
rlary = {
    "/tmp/_rl_restart_mysql": "/usr/bin/systemctl restart mariadb.service",
    "/tmp/_rl_stop_mysql": "systemctl stop mariadb.service",
    "/tmp/_rl_start_mysql": "systemctl start mariadb.service"
}

issue = "LOCAL"
with open('/home/jw/src/jmcap/v2bot/issue', 'r') as f:
    issue = f.readline().strip()

if issue == "REMOTE":
    rlary = {
        "/tmp/_rl_restart_mysql": "/bin/systemctl restart mysql",
        "/tmp/_rl_stop_mysql": "/bin/systemctl stop mysql",
        "/tmp/_rl_start_mysql": "/bin/systemctl start mysql"
    }


for key in rlary:
    if os.path.isfile(key):
        print(f"deleting {key}")
        os.remove(key)
        args = rlary[key].split()
        print(key,type(args),args)
        process = subprocess.run(args)
        print(process)

