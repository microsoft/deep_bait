import glob
import os
import shutil
import subprocess


def rename_env_file():
    shutil.move("example.env", ".env")


def main():
    create_env()
    rename_env_file()


class EnvException(Exception):
    pass


def create_env():
    print(os.getcwd())
    print(glob.glob("*"))
    make_process = subprocess.Popen(['make', 'create-env'], stderr=subprocess.STDOUT)
    if make_process.wait() != 0:
        raise EnvException('Environment creation failed!! WHY oh WHY')


if __name__ == "__main__":
    main()
