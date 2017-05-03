from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

import json

engine = create_engine('postgresql://catalog:items@localhost:5432/items')
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



# # Items under 'Soccer'
# category1 = Category(name = "Soccer")
# session.add(category1)
# session.commit()
#
# item1 = Item(name = "Soccer Ball", description = "with good bounce", category = category1, creator="phil.zhanwen.chen@gmail.com")
# session.add(item1)
# session.commit()
#
# item2 = Item(name = "Soccer Shoes", description = "with good grip", category = category1, creator="phil.zhanwen.chen@gmail.com")
# session.add(item2)
# session.commit()


# # Items under 'Basketball'
# category2 = Category(name = "Basketball")
#
# session.add(category2)
# session.commit()
#
# item1 = Item(name = "Js", description = "every young dude's dream", category = category2, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()

#
# # Items under 'Baseball'
# category3 = Category(name = "Baseball")
#
# session.add(category3)
# session.commit()
#
#
# item1 = Item(name = "Baseball bat", description = "A bat", category = category3, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()
#
# # Items under 'Frisbee'
# category4 = Category(name = "Frisbee")
#
# session.add(category4)
# session.commit()
#
# item1 = Item(name = "Frisbee", description = "The most fun disk you can own", category = category4, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()
#
# # Items under 'Snowboarding'
# category5 = Category(name = "Snowboarding")
# session.add(category5)
# session.commit()
#
# item1 = Item(name = "Goggles", description = "", category = category5, creator="phil.zhanwen.chen@gmail.com")
# session.add(item1)
# session.commit()
#
# item2 = Item(name = "Snowboard", description = "", category = category5, creator="phil.zhanwen.chen@gmail.com")
# session.add(item2)
# session.commit()
#
# # Items under 'Rock Climbing'
# category6= Category(name = "Rock Climbing")
#
# session.add(category6)
# session.commit()
#
# item1 = Item(name = "Hooks", description = "Save your life", category = category6, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()
#
#
# category7 = Category(name = "Foosball")
#
# session.add(category7)
# session.commit()
#
# item1 = Item(name = "Foosball Table", description = "Make your startup hot", category = category7, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()
#
# category8 = Category(name = "Skating")
#
# session.add(category8)
# session.commit()
#
#
# item1 = Item(name = "Skating Shoes", description = "Feel better than flying", category = category8, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()
#
# category9 = Category(name = "Hockey")
#
# session.add(category9)
# session.commit()
#
# item1 = Item(name = "Hockey Stick", description = "Your ultimate weapon", category = category9, creator="phil.zhanwen.chen@gmail.com")
#
# session.add(item1)
# session.commit()


category_json = json.loads("""{
  "all_categories": [
    {
      "name": "Laptops",
      "items": [
        {
            "name": "Apple MacBook Pro 15",
            "description": "Colorful, powerful workstations suitable for \
                            moderate gaming",
            "creator": "phil.zhanwen.chen@gmail.com"
        } ,
        {
            "name": "The New Razer Blade",
            "description": "The portable gaming laptop with GTX 1060 inside",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "The New Razer Blade",
            "description": "The portable gaming laptop with GTX 1060 inside",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "Asus ROG Strix GL502",
            "description": "The best all-around gaming laptop that's \
                            surprisingly cheap",
            "creator": "phil.zhanwen.chen@gmail.com"
        }
      ]
    },
    {
      "name": "IoT",
      "items": [
        {
            "name": "Intel Joule",
            "description": "The best and brightest, if you have \
                            40 hours to spend on setting it up",
            "creator": "phil.zhanwen.chen@gmail.com"
        } ,
        {
            "name": "Intel Edison",
            "description": "Cheap yet powerful IoT module, with plenty of \
                            3rd party expansions",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "NVidia Jetson TX2",
            "description": "The Joule-wannabe, with pre-2000 IO options.",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "Arduino UNO R3",
            "description": "THE basic IoT board. Grab a dozen when you come \
                            across them. Needs upgrades tho.",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "Raspberry Pi 3",
            "description": "Similar to Arduino, recently updated.",
            "creator": "phil.zhanwen.chen@gmail.com"
        }
      ]
    },
    {
      "name": "GPUs",
      "items": [
        {
            "name": "NVidia GTX 1080 Ti",
            "description": "The destroyer of Pascal Titan sales",
            "creator": "phil.zhanwen.chen@gmail.com"
        } ,
        {
            "name": "NVidia GTX Titan X (Pascal)",
            "description": "Sales have been cannibalized by the 1080 Ti",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "AMD Radeon RX 480",
            "description": "Value QHD.",
            "creator": "phil.zhanwen.chen@gmail.com"
        },
        {
            "name": "Nvidia GeForce GTX 1070",
            "description": "Can do 4K",
            "creator": "phil.zhanwen.chen@gmail.com"
        }
      ]
    },
    {
      "name": "Drones",
      "items": [
        {
            "name": "Parrot AR Drone 2.0",
            "description": "For roboticists too lazy to DIY",
            "creator": "phil.zhanwen.chen@gmail.com"
        } ,
        {
            "name": "DJI Phantom 3",
            "description": "On sale for $330 at Newegg",
            "creator": "phil.zhanwen.chen@gmail.com"
        }
      ]
    }
  ]
}""")

for category in category_json['all_categories']:
    category_input = Category(
        name = str(category['name'])
    )

    for item in category['items']:
        item_input = Item(
            name = str(item['name']),
            description = str(item['description']),
            creator = str(item['creator']),
            category_id = category_input.id
        )
        category_input.items.append(item_input)
        session.add(item_input)
        session.commit()
    session.add(category_input)
    session.commit()

print "added items!"
