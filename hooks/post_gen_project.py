import glob
import os
import subprocess
# from getpass import getpass

# from dotenv import set_key
#
# DOTENV_PATH='.env'
#
# env_key_dict={
#     "SELECTED_SUBSCRIPTION":"{{cookiecutter.selected_subscription}}",
#     "GROUP_NAME":"{{cookiecutter.group_name}}",
#     "STORAGE_ACCOUNT_NAME":"{{cookiecutter.storage_account_name}}",
#     "LOCATION":"{{cookiecutter.location}}",
#     "FILESHARE_NAME":"{{cookiecutter.fileshare_name}}",
#     "SERVICE_PRINCIPAL_APP_NAME":"{{cookiecutter.service_principal_app_name}}"
# }
#
# def set_service_principal_password():
#     pwd=getpass('Please enter the password to use for your service principal')
#     set_key(DOTENV_PATH, 'SERVICE_PRINCIPAL_PASSWORD', pwd)


def main():
    # for key, value in env_key_dict.items():
    #     set_key(DOTENV_PATH, key, value)
    # set_service_principal_password()
    create_env()

class EnvException(Exception):
    pass

def create_env():
    print(os.getcwd())
    print(glob.glob("*"))
    make_process = subprocess.Popen("ls", stderr=subprocess.STDOUT)
    make_process.wait()
    # if make_process.wait() != 0:
    raise EnvException('Environment creation failed!! WHY oh WHY')

if __name__ == "__main__":
    main()