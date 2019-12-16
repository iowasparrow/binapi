#!/var/www/html/binweb/binapi/.venv/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/html/binweb/binapi/")

#from flaskapp import app as application
from api import app as application
application.secret_key = '123'
