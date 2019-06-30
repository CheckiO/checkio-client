import platform
import getpass
import os
import sys
import stat
import json
import logging

from checkio_client.settings import conf

IS_ROOT = getpass.getuser() == 'root'

CONFIG_X = '''{
  "name": "com.checkio.client",
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

EXEC_SCRIPT_NAME = 'checkio_chrome_plugin.py'

FILENAME = 'com.checkio.client.json'

FOLDER_DARWIN_ROOT = "/Library/Google/Chrome/NativeMessagingHosts"
FOLDER_DARWIN_USER = "~/Library/Application Support/Google/Chrome/NativeMessagingHosts"
FOLDER_DARWIN_USER = os.path.expanduser(FOLDER_DARWIN_USER)

FOLDER_LINUX_ROOT = "/etc/opt/chrome/native-messaging-hosts"
FOLDER_LINUX_USER = "~/.config/google-chrome/NativeMessagingHosts"
FOLDER_LINUX_USER = os.path.expanduser(FOLDER_LINUX_USER)

FOLDER_WINDOW = os.path.join(conf.foldername, 'chrome')
WIN_REG_KEY = r'Software\Google\Chrome\NativeMessagingHosts\com.checkio.client'
WIN_BAT_FILE = 'chrome_plugin.bat'

BAT_FILE_SCRIPT = '''@echo off
"{executable}" {py_script}
'''

INSTALL_STEPS = []
INSTALL_STEPS_FILE = os.path.join(conf.foldername, 'install_steps_chrome.json')

INS_NEW_FILE = 'new_file'
INS_NEW_REG = 'new_reg_cur_user'

INSTALL_URL = 'http://www.checkio.org/local-editor/chrome/extension/'

def update_global_ff():
    global CONFIG_X
    CONFIG_X = '''{
  "name": "com.checkio.client",
  "description": "Example host for native messaging",
  "path": "HOST",
  "type": "stdio",
  "allowed_extensions": [ "{c7e3ccfd-0398-411b-8607-fa4ae25b4cd3}" ]
}'''

    global EXEC_SCRIPT_NAME
    EXEC_SCRIPT_NAME = 'checkio_ff_plugin.py'

    global FOLDER_DARWIN_ROOT
    FOLDER_DARWIN_ROOT = '/Library/Application Support/Mozilla/NativeMessagingHosts/'
    global FOLDER_DARWIN_USER
    FOLDER_DARWIN_USER = '~/Library/Application Support/Mozilla/NativeMessagingHosts/'
    FOLDER_DARWIN_USER = os.path.expanduser(FOLDER_DARWIN_USER)

    global FOLDER_LINUX_ROOT
    FOLDER_LINUX_ROOT = '/usr/lib/mozilla/native-messaging-hosts/'
    global FOLDER_LINUX_USER
    FOLDER_LINUX_USER = '~/.mozilla/native-messaging-hosts/'
    FOLDER_LINUX_USER = os.path.expanduser(FOLDER_LINUX_USER)

    global WIN_REG_KEY
    WIN_REG_KEY = r'Software\Mozilla\NativeMessagingHosts\com.checkio.client'
    global WIN_BAT_FILE
    WIN_BAT_FILE = 'ff_plugin.bat'

    global INSTALL_STEPS_FILE
    INSTALL_STEPS_FILE = os.path.join(conf.foldername, 'install_steps_ff.json')

    global FOLDER_WINDOW
    FOLDER_WINDOW = os.path.join(conf.foldername, 'ff')

    global INSTALL_URL
    INSTALL_URL = 'http://www.checkio.org/local-editor/firefox/extension/'


def update_global_chromium():

    global EXEC_SCRIPT_NAME
    EXEC_SCRIPT_NAME = 'checkio_chromium_plugin.py'

    global FOLDER_DARWIN_ROOT
    global FOLDER_DARWIN_USER
    FOLDER_DARWIN_ROOT = "/Library/Application Support/Chromium/NativeMessagingHosts"
    FOLDER_DARWIN_USER = "~/Library/Application Support/Chromium/NativeMessagingHosts"
    FOLDER_DARWIN_USER = os.path.expanduser(FOLDER_DARWIN_USER)

    global FOLDER_LINUX_ROOT
    global FOLDER_LINUX_USER
    FOLDER_LINUX_ROOT = '/etc/chromium/native-messaging-hosts/'
    FOLDER_LINUX_USER = '~/.config/chromium/NativeMessagingHosts/'
    FOLDER_LINUX_USER = os.path.expanduser(FOLDER_LINUX_USER)

    global WIN_BAT_FILE
    WIN_BAT_FILE = 'chromium_plugin.bat'

    global INSTALL_STEPS_FILE
    INSTALL_STEPS_FILE = os.path.join(conf.foldername, 'install_steps_chromium.json')

    global FOLDER_WINDOW
    FOLDER_WINDOW = os.path.join(conf.foldername, 'chromium')


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
    if args.ff:
        update_global_ff()

    if args.chromium:
        update_global_chromium()

    if is_installed():
        print('Plugin was installed before. Uninstallation...')
        uninstall(args)

    globals()['install_' + platform.system().lower()]()
    save_install_steps()
    configure_editor()
    print('Installation Complete!')
    print()
    print('You can now install browser extension ' + INSTALL_URL)
    print()

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
    script_filename = os.path.join(conf.foldername, EXEC_SCRIPT_NAME)

    logging.info('Init Script File ' + script_filename)
    os.makedirs(os.path.dirname(script_filename), exist_ok=True)
    with open(script_filename, 'w') as fh:
        fh.write(EXEC_SCRIPT.replace('EXEC', sys.executable))
    add_install_step(INS_NEW_FILE, script_filename)

    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | stat.S_IEXEC)

    logging.info('Init Config File ' + conf_filename)
    os.makedirs(os.path.dirname(conf_filename), exist_ok=True)
    with open(conf_filename, 'w') as fh:
        fh.write(CONFIG_X.replace('HOST', win_bat or script_filename))
    add_install_step(INS_NEW_FILE, conf_filename)

    st = os.stat(conf_filename)
    os.chmod(conf_filename, st.st_mode | stat.S_IRUSR)
    return (conf_filename, script_filename)

def install_windows():
    (conf_filename, script_filename) = install_x(FOLDER_WINDOW, WIN_BAT_FILE)

    bat_file = os.path.join(FOLDER_WINDOW, WIN_BAT_FILE)
    logging.info('Init Bat File ' + bat_file)

    with open(bat_file, 'w') as fh:
        fh.write(BAT_FILE_SCRIPT.format(
            executable=sys.executable,
            py_script=script_filename
        ))
    add_install_step(INS_NEW_FILE, bat_file)

    logging.info('Init Registry Key')

    import winreg
    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, WIN_REG_KEY)
    winreg.SetValueEx(reg_key, None, 0, winreg.REG_SZ, conf_filename)
    add_install_step(INS_NEW_REG, WIN_REG_KEY)

def uninstall(args=None):
    if args.ff:
        update_global_ff()
    if args.chromium:
        update_global_chromium()

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
        logging.info('Unable to remove file {}: {}'.format(filename, e))
    else:
        logging.info('Remove file ' + filename)

def uninstall_new_reg_cur_user(reg_key):
    import winreg
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_key)
    except Exception as e:
        logging.info('Unable to remove Registry Key {}: {}'.format(reg_key, e))
    else:
        logging.info('Remove Registry Key ' + reg_key)

def configure_editor():
    if not platform.system() == 'Windows':
        return
    default_data = conf.default_domain_data
    editor = default_data['editor']
    editor = input('Command that will be used for editing files [{}]:'.format(editor)) or editor
    conf.default_domain_section['editor'] = editor.strip()
    conf.save()

