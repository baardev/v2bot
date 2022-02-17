#!/usr/bin/env python
import os
import subprocess
import toml
import lib_v2_globals as g

os.chdir("/home/jw/src/jmcap/v2bot")

g.cvars = toml.load(g.cfgfile)

# * The default os set to 'LOCAL' values
rlary = {
    "/tmp/_rl_restart_mysql": "/usr/bin/systemctl restart mariadb.service",
    "/tmp/_rl_stop_mysql": "systemctl stop mariadb.service",
    "/tmp/_rl_start_mysql": "systemctl start mariadb.service"
}

issue = "LOCAL"
with open(f"{g.cvars['cwd']}/issue", 'r') as f:
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
        if os.path.isfile(key):
            print(f"{key} NOT DELETED")
        else:
            print(f"{key} DELETED")
        args = rlary[key].split()
        print(key,type(args),args)
        process = subprocess.run(args)
        print(process)

