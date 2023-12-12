#!/usr/bin/python3
""" module doc
"""
from fabric.api import task, local, env, put, run
from datetime import datetime
import os

env.hosts = ['54.165.75.147','54.196.28.207']


@task
def do_pack():
    """ method doc
        sudo fab -f 1-pack_web_static.py do_pack
    """
    formatted_dt = datetime.now().strftime('%Y%m%d%H%M%S')
    mkdir = "mkdir -p versions"
    path = f"versions/web_static_{formatted_dt}.tgz"
    print(f"Packing web_static to versions/web_static_{formatted_dt}.tgz")
    if local(f"{mkdir}&& tar -cvzf {path} web_static").succeeded:
        return path
    return None


@task
def do_deploy(archive_path):
    """ method doc
        fab -f 2-do_deploy_web_static.py do_deploy:
        archive_path=versions/web_static_20231004201306.tgz
        -i ~/.ssh/id_rsa -u ubuntu
    """
    try:
        if os.path.exists(archive_path) is False:
            return False
        fn_with_ext = os.path.basename(archive_path)
        fn_no_ext, ext = os.path.splitext(fn_with_ext)
        dpath = "/data/web_static/releases/"
        put(archive_path, "/tmp/")

        # Use sudo for commands requiring elevated privileges
        run(f"sudo rm -rf {dpath}{fn_no_ext}/")
        run(f"sudo mkdir -p {dpath}{fn_no_ext}/")
        run(f"sudo tar -xzf /tmp/{fn_with_ext} -C {dpath}{fn_no_ext}/")
        run(f"sudo rm /tmp/{fn_with_ext}")
        run(f"sudo mv {dpath}{fn_no_ext}/web_static/* {dpath}{fn_no_ext}/")
        run(f"sudo rm -rf {dpath}{fn_no_ext}/web_static")
        run(f"sudo rm -rf /data/web_static/current")
        run(f"sudo ln -s {dpath}{fn_no_ext}/ /data/web_static/current")

        print("New version deployed!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

