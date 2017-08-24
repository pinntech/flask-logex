"""Runner for testing app and blueprint logging individually"""

import subprocess
from tests.samples import app

if __name__ == '__main__':
    app.run()
    subprocess.call(['rm', '-rf', 'logs'])
