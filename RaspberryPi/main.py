import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.AccessController import AccessController

if __name__ == "__main__":
    app = AccessController()
    app.run()