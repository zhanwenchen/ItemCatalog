import sys
sys.path.insert(0, "/var/www/ItemCatalog")
sys.path.insert(0, "/home/ubuntu/.virtualenvs/catalog/lib/python2.7/site-packages")
print(sys.path)

from project import app
application = app
