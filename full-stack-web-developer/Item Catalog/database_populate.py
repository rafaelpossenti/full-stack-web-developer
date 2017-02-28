from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Item

engine = create_engine('sqlite:///heroes.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = User(name="Carlito",
             email="chaplin@gmail.com",
             picture="http://cp91279.biography.com/1000509261001/1000509261001"
             "_1824351571001_BIO-Biography-23-Hollywood-Directors"
             "-Charlie-Chaplin-115950-SF.jpg")
session.add(User1)
session.commit()

User2 = User(name="Nietzsche",
             email="nietzsche@gmail.com",
             picture="https://upload.wikimedia.org/wikipedia/commons/thumb/1/"
             "1b/Nietzsche187a.jpg/220px-Nietzsche187a.jpg")
session.add(User2)
session.commit()

User3 = User(name="Neruda",
             email="neruda@gmail.com",
             picture="https://s-media-cache-ak0.pinimg.com/originals/"
             "28/0b/fa/280bfae7964aed33226b341df39465fe.jpg")
session.add(User3)
session.commit()

# Create all categories
category1 = Category(name="aquatic")
session.add(category1)
session.commit()

category2 = Category(name="flying")
session.add(category2)
session.commit()

category3 = Category(name="earthly")
session.add(category3)
session.commit()

category4 = Category(name="fire")
session.add(category4)
session.commit()

category5 = Category(name="shock")
session.add(category5)
session.commit()

category6 = Category(name="wind")
session.add(category6)
session.commit()

category7 = Category(name="strong")
session.add(category7)
session.commit()

category8 = Category(name="mystic")
session.add(category8)
session.commit()

category9 = Category(name="invisible")
session.add(category9)
session.commit()

category10 = Category(name="speed")
session.add(category10)
session.commit()

category11 = Category(name="size")
session.add(category11)
session.commit()

category12 = Category(name="armor")
session.add(category12)
session.commit()

# Create sample items
item1 = Item(name="Iron man",
             description="Iron Man (Anthony Edward Tony Stark) is a"
             " fictional superhero appearing in American comic books published"
             " by Marvel Comics, as well as its associated media.",
             picture_url="https://upload.wikimedia.org/wikipedia/"
             "en/e/e0/Iron_Man_bleeding_edge.jpg",
             user_id=1, category_id=12)
session.add(item1)
session.commit()

item2 = Item(name="Batman",
             description="Batman is a fictional superhero appearing in "
             "American comic books published by DC Comics. The character"
             " was created by artist Bob Kane and writer Bill Finger.",
             picture_url="https://upload.wikimedia.org/wikipedia/en"
             "/2/22/Batman-DC-Comics.jpg",
             user_id=3, category_id=3)
session.add(item2)
session.commit()

item3 = Item(name="Human Torch",
             description="The Human Torch is a fictional superhero "
             "appearing in American comic books published "
             "by Marvel Comics. The character is a founding member of"
             " the Fantastic Four. He is writer Stan Lee.",
             picture_url="https://upload.wikimedia.org/wikipedia/"
             "en/c/c7/Human_Torch_%28Johnny_Storm%29.png",
             user_id=2, category_id=4)
session.add(item3)
session.commit()

item8 = Item(name="Superman",
             description="Superman is a fictional superhero appearing in "
             "American comic books published by DC Comics. The character "
             "was created by writer Jerry Siegel and artist Joe Shuster.",
             picture_url="https://upload.wikimedia.org/wikipedia/en/"
             "e/eb/SupermanRoss.png",
             user_id=1, category_id=2)
session.add(item8)
session.commit()

print "The Heroes are UP!"
