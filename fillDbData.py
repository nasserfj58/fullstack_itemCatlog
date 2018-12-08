from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storedb_setup import Base, Product, ProductType, User
import bcrypt

engine = create_engine('sqlite:///nasserzon.db?check_same_thread=false')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
dbsession = DBsession()

#create categories
ptype = ProductType(name='Smartphone')
dbsession.add(ptype)
dbsession.commit()

ptype = ProductType(name='Laptop')
dbsession.add(ptype)
dbsession.commit()

ptype = ProductType(name='Desktop')
dbsession.add(ptype)
dbsession.commit()

#create AdminUser
email = 'nasserfj58@gmail.com'
password = bcrypt.hashpw('123456789', bcrypt.gensalt())
username = 'nasser'

user = User(username=username,password=password,email=email)
dbsession.add(user)
dbsession.commit()

adminuser = dbsession.query(User).filter_by(email=email).first()

#Create Products
product = Product(name='Iphone X',typeId=1,userId=adminuser.id,price=3000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()


product = Product(name='Samsung Galaxy S9',typeId=1,userId=adminuser.id,price=4000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

product = Product(name='Samsung Galaxy S9 Note',typeId=1,userId=adminuser.id,price=5000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

product = Product(name='One Plus 6p',typeId=1,userId=adminuser.id,price=3000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()


product = Product(name='Dell Laptop',typeId=2,userId=adminuser.id,price=3000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

product = Product(name='Lenovo Laptop',typeId=2,userId=adminuser.id,price=4000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

product = Product(name='Macbook Laptop',typeId=2,userId=adminuser.id,price=5000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()


product = Product(name='Dell Desktop',typeId=3,userId=adminuser.id,price=3000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

product = Product(name='Lenovo Desktop',typeId=3,userId=adminuser.id,price=4000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

product = Product(name='IMAC Desktop',typeId=3,userId=adminuser.id,price=8000,desc="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec erat lorem, varius vel ullamcorper sed, auctor eget nisi. Ut semper tellus nec lacus eleifend convallis. In hendrerit, purus ultricies elementum consectetur, ligula ipsum vestibulum nunc, nec rutrum diam metus """)
dbsession.add(product)
dbsession.commit()

