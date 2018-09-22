import platform
import getpass
import os
import sys
import stat

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

def install(args=None):
    globals()['install_' + platform.system().lower()]()

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

def install_x(folder):
    conf_filename = os.path.join(folder, FILENAME)
    script_filename = os.path.join(conf.foldername, 'checkio_web_plugin.py')

    print('Init Script File ' + script_filename)
    with open(script_filename, 'w') as fh:
        fh.write(EXEC_SCRIPT.replace('EXEC', sys.executable))

    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | stat.S_IEXEC)

    print('Init Config File ' + conf_filename)

    with open(conf_filename, 'w') as fh:
        fh.write(CONFIG_X.replace('HOST', script_filename))

    st = os.stat(conf_filename)
    os.chmod(conf_filename, st.st_mode | stat.S_IRUSR)
    return conf_filename

def install_windows():
    conf_filename = install_x(FOLDER_WINDOW)
    import winreg
    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, WIN_REG_KEY)
    winreg.SetValueEx(reg_key, None, 0, winreg.REG_SZ, conf_filename)
    print('Init Registry Key')

def uninstall(args=None):
    globals()['uninstall_' + platform.system().lower()]()

