from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



# Items under 'Soccer'
category1 = Category(name = "Soccer")
session.add(category1)
session.commit()

item1 = Item(name = "Soccer Ball", description = "with good bounce", category = category1)
session.add(item1)
session.commit()

item2 = Item(name = "Soccer Shoes", description = "with good grip",
    category = category1)
session.add(item2)
session.commit()


# Items under 'Basketball'
category2 = Category(name = "Basketball")

session.add(category2)
session.commit()

item1 = Item(name = "Js", description = "every young dude's dream",
    category = category2)

session.add(item1)
session.commit()


# Items under 'Baseball'
category3 = Category(name = "Baseball")

session.add(category3)
session.commit()


item1 = Item(name = "Baseball bat", description = "A bat", category = category3)

session.add(item1)
session.commit()

# Items under 'Frisbee'
category4 = Category(name = "Frisbee")

session.add(category4)
session.commit()

item1 = Item(name = "Frisbee", description =
    "The most fun disk you can own",
    category = category4)

session.add(item1)
session.commit()

# Items under 'Snowboarding'
category5 = Category(name = "Snowboarding")
session.add(category5)
session.commit()

item1 = Item(name = "Goggles", description = "", category = category5)
session.add(item1)
session.commit()

item2 = Item(name = "Snowboard", description = "", category = category5)
session.add(item2)
session.commit()

# Items under 'Rock Climbing'
category6= Category(name = "Rock Climbing")

session.add(category6)
session.commit()

item1 = Item(name = "Hooks", description = "Save your life", category = category6)

session.add(item1)
session.commit()

#Menu for Auntie Ann's
category7 = Category(name = "Foosball")

session.add(category7)
session.commit()

item1 = Item(name = "Foosball Table", description = "Make your startup hot",
    category = category7)

session.add(item1)
session.commit()

#Menu for Cocina Y Amor
category8 = Category(name = "Skating")

session.add(category8)
session.commit()


item1 = Item(name = "Skating Shoes", description = "Feel better than flying", category = category8)

session.add(item1)
session.commit()

#Menu for Auntie Ann's
category9 = Category(name = "Hockey")

session.add(category9)
session.commit()

item1 = Item(name = "Hockey Stick", description = "Your ultimate weapon", category = category9)

session.add(item1)
session.commit()

print "added items!"
