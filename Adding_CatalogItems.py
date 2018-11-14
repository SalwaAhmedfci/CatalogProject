import sqlalchemy
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User

# opening connection with database

engine = sqlalchemy.create_engine('sqlite:///CategoryItems.db')
Base.metadata.bind = engine
# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user1 = User(name="Ahmed",
             picture='https://pbs.twimg.com/profile_images/2671170543/'
                     '18debd694829ed78203a5a36dd364160_400x400.png',
             email="salwa@gmail.com")
session.add(user1)
session.commit()
# adding Category

Category1 = Category(name="Soccer", user_id=1)
session.add(Category1)
session.commit()

Category2 = Category(name="Baseball", user_id=1)
session.add(Category2)
session.commit()

Category3 = Category(name="Frisbee", user_id=1)
session.add(Category3)
session.commit()

Category4 = Category(name="Snowboarding", user_id=1)
session.add(Category4)
session.commit()

Category5 = Category(name="Rock Climbing", user_id=1)
session.add(Category5)
session.commit()

Category6 = Category(name="Foosball", user_id=1)
session.add(Category6)
session.commit()

Category7 = Category(name="Skating", user_id=1)
session.add(Category7)
session.commit()

Category9 = Category(name="Hockey", user_id=1)
session.add(Category9)
session.commit()

Category10 = Category(name="Tennis", user_id=1)
session.add(Category10)
session.commit()

Category11 = Category(name="Swimming", user_id=1)
session.add(Category11)
session.commit()

Category12 = Category(name='Snorkeling', user_id=1)
session.add(Category12)
session.commit()

# adding items for each category

Stick = Items(name="Stick", user_id=1,
              description="A piece of sport equipment"
                          " used by the players in all the "
                          "forms of hockey to move the ball "
                          "or puck "
                          "either to push, pull, hit, strike, "
                          "flick, steer, launch or stop "
                          "the "
                          "ball/puck during play with the objective "
                          "being to move the "
                          "ball/puck around "
                          "the playing area and between team members "
                          "using the stick, and to "
                          "ultimately "
                          "score a goal with it against an opposing team.",
              category=Category1)
session.add(Stick)
session.commit()

Goggles = Items(name="Goggles", user_id=1,
                description="Ski and snowboard "
                            "goggles are one of "
                            "the essentials of your"
                            " winter equipment, "
                            "and should be picked with a "
                            "lot of care. There"
                            " is probably nothing worse, "
                            "after badly "
                            "fitted boots, than not being "
                            "able to see "
                            "anything while skiing or "
                            "snowboarding.",
                category=Category4)
session.add(Goggles)
session.commit()

Two_Shinguards = Items(name="Two Shinguards", user_id=1,
                       description="A shin guard or shin "
                                   "pad is a piece "
                                   "of equipment worn on the "
                                   "front of a player's "
                                   "shin to protect "
                                   "them from injury. These "
                                   "are commonly "
                                   "used in sports including"
                                   " association "
                                   "football, "
                                   "baseball, ice hockey, field "
                                   "hockey, lacrosse, cricket, "
                                   "mountain bike trials, "
                                   "and other sports..",
                       category=Category1)
session.add(Two_Shinguards)
session.commit()

Snowboard = Items(name="Snowboard", user_id=1,
                  description="Snowboards are"
                              " boards where both feet "
                              "are secured to the same board,"
                              "which are wider than"
                              " skis, with the "
                              "ability to glide on snow."
                              "Snowboards widths are "
                              "between 6 and 12 "
                              "inches or 15 to 30 centimeters."
                              "Snowboards are differentiated "
                              "from monoskis "
                              "by the stance of the user.",
                  category=Category4)
session.add(Snowboard)
session.commit()

Shinguard = Items(name="Shinguard", user_id=1,
                  description="A shin guard or shin pad "
                              "is a piece of "
                              "equipment worn on the front "
                              "of a player's shin "
                              "to protect them from injury. "
                              "These are commonly"
                              " used in sports including "
                              "association "
                              "football, baseball, ice "
                              "hockey, field hockey, lacrosse,"
                              " cricket, mountain "
                              "bike trials, "
                              "and other sports.",
                  category=Category1)
session.add(Shinguard)
session.commit()

Frisbee = Items(name="Frisbee", user_id=1,
                description="A frisbee (also c"
                            "alled a flying disc or simply "
                            "a disc)[1] is a gliding toy or sporting "
                            "item "
                            "that is generally plastic "
                            "and roughly 20 to 25 "
                            "centimetres (8 to 10 in) "
                            "in diameter with "
                            "a pronounced lip. "
                            "It is used recreationally"
                            " and competitively for "
                            "throwing and catching, "
                            "as in flying disc "
                            "games.",
                category=Category3)
session.add(Frisbee)
session.commit()

Bat = Items(name="Bat", user_id=1,
            description="smooth wooden or metal"
                        " club used in the"
                        " sport of baseball"
                        " to hit the ball after "
                        "it is thrown "
                        "by the pitcher. "
                        "By regulation it may be"
                        " no more than 2.75 inches (70 mm) "
                        "in diameter at the thickest "
                        "part and no more than 42 "
                        "inches (1,100 mm) long. Although "
                        "historically bats approaching "
                        "3 pounds (1.4 kg) were swung,"
                        "today bats of 33 "
                        "ounces (0.94 kg) are common, "
                        "topping out "
                        "at 34 ounces (0.96 kg) to 36 "
                        "ounces (1.0 kg).",
            category=Category2)
session.add(Bat)
session.commit()

Jersey = Items(name="Jersey", user_id=1,
               description="A jersey is an item "
                           "of knitted clothing, traditionally "
                           "in wool or cotton, with sleeves,"
                           "worn as a pullover, "
                           "as it does not open"
                           " at the front, unlike"
                           " a cardigan. It is usually "
                           "close- "
                           "fitting and machine "
                           "knitted in contrast to"
                           " a guernsey that is more "
                           "often hand knit with a "
                           "thicker yarn. The word "
                           "is usually used"
                           " interchangeably with sweater.",
               category=Category1)
session.add(Jersey)
session.commit()

Cleats = Items(name="Cleats", user_id=1,
               description="Cleats or studs "
                           "are protrusions on the sole "
                           "of a shoe, or on an "
                           "external attachment to a "
                           "shoe, that provide additional "
                           "traction on a soft"
                           " or slippery surface. "
                           "They can be conical "
                           "or blade-like in shape, "
                           "and made of plastic, rubber or metal. "
                           "In American English the term "
                           "cleats is used synecdochically "
                           "to refer to shoes featuring "
                           "such "
                           "protrusions.",
               category=Category1)
session.add(Cleats)
session.commit()

# printing Category

items = session.query(Category).all()

for item in items:
    print(item.name)
# printing Items of Category
items = session.query(Items).all()

for item in items:
    print(item.name + " ( " + item.category.name + " ) ")
