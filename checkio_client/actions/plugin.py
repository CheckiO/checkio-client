import platform
import getpass
import os
import sys
import stat
import json

from checkio_client.settings import conf

IS_ROOT = getpass.getuser() == 'root'

CONFIG_X = '''{
  "name": "com.google.chrome.checkio.client",
  "description": "Chrome Native Messaging API for CheckiO Client",
  "path": "HOST",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://mlglngjgefkbflbmelghfeijmojocnbi/"
  ]
}'''

EXEC_SCRIPT = '''#!EXEC
from checkio_client.web_plugin import main
main()
'''

FILENAME = 'com.google.chrome.checkio.client.json'

FOLDER_DARWIN_ROOT = "/Library/Google/Chrome/NativeMessagingHosts"
FOLDER_DARWIN_USER = "~/Library/Application Support/Google/Chrome/NativeMessagingHosts"
FOLDER_DARWIN_USER = os.path.expanduser(FOLDER_DARWIN_USER)

FOLDER_LINUX_ROOT = "/etc/opt/chrome/native-messaging-hosts"
FOLDER_LINUX_USER = "~/.config/google-chrome/NativeMessagingHosts"
FOLDER_LINUX_USER = os.path.expanduser(FOLDER_LINUX_USER)

FOLDER_WINDOW = conf.foldername
WIN_REG_KEY = r'Software\Google\Chrome\NativeMessagingHosts\com.google.chrome.checkio.client'
WIN_BAT_FILE = 'web_plugin.bat'

BAT_FILE_SCRIPT = '''@echo off
{executable} {py_script}
'''

INSTALL_STEPS = []
INSTALL_STEPS_FILE = os.path.join(conf.foldername, 'web_plugin_install_steps.json')

INS_NEW_FILE = 'new_file'
INS_NEW_REG = 'new_reg_cur_user'



def add_install_step(name, value):
    INSTALL_STEPS.append([name, value])

def save_install_steps():
    with open(INSTALL_STEPS_FILE, 'w', encoding='utf-8') as fh:
        json.dump(
            INSTALL_STEPS,
            fh
        )

def read_install_steps():
    with open(INSTALL_STEPS_FILE, 'r', encoding='utf-8') as fh:
        return json.load(
            fh
        )

def is_installed():
    return os.path.exists(INSTALL_STEPS_FILE)


def install(args=None):
    if is_installed():
        print('Plugin was installed before. Uninstallation...')
        uninstall()
        
    globals()['install_' + platform.system().lower()]()
    save_install_steps()
    print('Installation Complete!')

def install_darwin():
    if IS_ROOT:
        folder = FOLDER_DARWIN_ROOT
    else:
        folder = FOLDER_DARWIN_USER

    install_x(folder)

def install_linux():
    if IS_ROOT:
        folder = FOLDER_LINUX_ROOT
    else:
        folder = FOLDER_LINUX_USER

    install_x(folder)

def install_x(folder, win_bat=None):
    conf_filename = os.path.join(folder, FILENAME)
    script_filename = os.path.join(conf.foldername, 'checkio_web_plugin.py')

    print('Init Script File ' + script_filename)
    with open(script_filename, 'w') as fh:
        fh.write(EXEC_SCRIPT.replace('EXEC', sys.executable))
    add_install_step(INS_NEW_FILE, script_filename)

    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | stat.S_IEXEC)

    print('Init Config File ' + conf_filename)

    with open(conf_filename, 'w') as fh:
        fh.write(CONFIG_X.replace('HOST', win_bat or script_filename))
    add_install_step(INS_NEW_FILE, conf_filename)

    st = os.stat(conf_filename)
    os.chmod(conf_filename, st.st_mode | stat.S_IRUSR)
    return (conf_filename, script_filename)

def install_windows():
    (conf_filename, script_filename) = install_x(FOLDER_WINDOW, WIN_BAT_FILE)

    bat_file = os.path.join(FOLDER_WINDOW, WIN_BAT_FILE)
    print('Init Bat File ' + bat_file)

    with open(bat_file, 'w') as fh:
        fh.write(BAT_FILE_SCRIPT.format(
            executable=sys.executable,
            py_script=script_filename
        ))
    add_install_step(INS_NEW_FILE, bat_file)

    print('Init Registry Key')

    import winreg
    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, WIN_REG_KEY)
    winreg.SetValueEx(reg_key, None, 0, winreg.REG_SZ, conf_filename)
    add_install_step(INS_NEW_REG, WIN_REG_KEY)

def uninstall(args=None):
    try:
        steps = read_install_steps()
    except FileNotFoundError:
        print('Plugin was not installed')
        return

    for step in steps:
        globals()['uninstall_' + step[0]](step[1])

    os.remove(INSTALL_STEPS_FILE)

    print('Uninstall Complete')

def uninstall_new_file(filename):
    try:
        os.remove(filename)
    except Exception as e:
        print('Unable to remove file {}: {}'.format(filename, e))
    else:
        print('Remove file ' + filename)

def uninstall_new_reg_cur_user(reg_key):
    import winreg
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_key)
    except Exception as e:
        print('Unable to remove Registry Key {}: {}'.format(reg_key, e))
    else:
        print('Remove Registry Key ' + reg_key)


