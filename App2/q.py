from sqlalchemy import create_engine, MetaData, Column, String, Integer
from sqlalchemy.testing.schema import Table

engine = create_engine('sqlite:///shop.db',echo=True)
metadata = MetaData(bind=engine)

users_table = Table('basket', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('idUser', Integer),
                    Column('idItem', Integer),
                    Column('count', Integer),
                    )


# create tables in database
metadata.create_all()
