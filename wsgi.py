import sys
sys.path.insert(0, "/var/www/ItemCatalog")
sys.path.insert(0, "/home/ubuntu/.virtualenvs/catalog")

from project import app
application = app
