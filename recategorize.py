import sys
from getpass import getpass

sys.argv.append("inciclopedia")
sys.argv.append(input("Introduzca el nombre de usuario del bot:"))
sys.argv.append(getpass("Introduzca la contraseña del bot: "))

import scripts.recategorize.recategorize
