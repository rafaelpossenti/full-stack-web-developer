from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()  # the base mapper from SQLAlchemy


class User(Base):
    '''Creates the database table for users.

    Attibutes:
        __tablename__: string naming the table.
        id: column to store the user's id.
        name: column to store the user's name.
        email: column to store the user's email.
        password: column to store the user password if exist.
        picture: column to store the URL of the user's picture.
        item: relationship.
    '''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(256))
    item = relationship('Item', cascade="save-update, merge, delete")

    @property
    def serialize(self):
        '''Return object data in easy serializeable format.'''
        return {
            'id': self.id,
            'name': self.name,
            'Item': [i.serialize for i in self.item]
        }


class Category(Base):
    '''Creates the database table for category of items.

    Attibutes:
        __tablename__: string naming the table.
        id: column to store the item's id.
        name: column to store the item's name.
        item: relationship.
    '''
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    item = relationship('Item', cascade="save-update, merge, delete")

    @property
    def serialize(self):
        '''Return object data in easy serializeable format.'''
        return {
            'id': self.id,
            'name': self.name,
            'Item': [i.serialize for i in self.item]
        }


class Item(Base):
    '''Creates the database table for items.

    Attibutes:
        __tablename__: string naming the table.
        id: column to store the item's id.
        name: column to store the item's name.
        description: column to store the item's description.
        picture: column to store the URL of the item's picture.
        category_id: column to store the id of the category of the item.
        category: relationship.
        user_id: column to store the id of the author of the item.
        user: relationship.
    '''
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String, nullable=False)
    picture_url = Column(String(250))
    picture_filename = Column(String(250))

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        '''Return object data in easy serializeable format.'''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'user_id': self.user_id
        }


'''Create the database'''
engine = create_engine('sqlite:///heroes.db')
Base.metadata.create_all(engine)
