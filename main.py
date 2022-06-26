from flask import request, Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import marshmallow as ma
# import psycopg2

from models.app_user import AppUsers



app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "crm"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_host}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma  = Marshmallow(app)

"""Initializes the global database object used by the app."""
# if isinstance(app, Flask) and isinstance(db, SQLAlchemy):
#    load_models()
#    db.init_app(app)
# else:
#    raise ValueError('Cannot init DB without db and app objects.')

app = Flask(__name__)




# conn = psycopg2.connect("dbname='crm' user='silvanakoharian' host='localhost'")
# cursor = conn.cursor()

def create_all():
   print("Querying for Super Admin user...")
   user_data = db.session.query(AppUsers).filter(AppUsers.email == 'admin@devpipeline.com').first()
   if user_data == None:
      print("Super Admin not found! Creating foundation-admin@devpipeline user...")
      password = ''
      while password == '' or password is None:
         password = input(' Enter a password for Super Admin:')
      
      # hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
      record = AppUsers('Super', 'Admin', "admin@devpipeline.com", password, "super-admin", "Orem", "Utah")

      db.session.add(record)
      db.session.commit()
   else:
      print("Super Admin user found!")

   # cursor.execute("""
   #    CREATE TABLE IF NOT EXISTS Users (
   #       user_id SERIAL PRIMARY KEY,
   #       first_name VARCHAR NOT NULL,
   #       last_name VARCHAR,
   #       email VARCHAR NOT NULL UNIQUE,
   #       phone VARCHAR,
   #       city VARCHAR,
   #       state VARCHAR,
   #       org_id INT,
   #       active SMALLINT
   #    );
   # """)
   # cursor.execute("""
   #    CREATE TABLE IF NOT EXISTS Organizations (
   #       org_id SERIAL PRIMARY KEY,
   #       name VARCHAR NOT NULL,
   #       phone VARCHAR,
   #       city VARCHAR,
   #       state VARCHAR,
   #       active SMALLINT
   #    );
   # """)
   # conn.commit()
   # cursor.execute("SELECT org_id FROM Organizations WHERE name='DevPipeline';")
   # results = cursor.fetchone()
   # org_id = -999
   # if not results:
   #    print("Organization DevPipeline not found...Creating")
   #    cursor.execute("""
   #       INSERT INTO Organizations
   #       (name, phone, city, state, active)
   #       VALUES('DevPipeline', '3853090807', 'Orem', 'UT', 1)
   #       RETURNING org_id;
   #    """)
   #    org_id = cursor.fetchone()[0]
   #    conn.commit()
   # else:
   #    org_id = results[0]

   # cursor.execute("SELECT * FROM Users WHERE email='admin@devpipeline.com'")
   # results = cursor.fetchone()
   # if not results:
   #    print("Admin user not found....Creating admin user 'admin@devpipeline.com'")
   #    cursor.execute("""
   #       INSERT INTO Users
   #       (first_name, last_name, email, phone, city, state, org_id, active)
   #       VALUES('Admin', 'Admin', 'admin@devpipeline.com', '8088088088', 'SLC', 'UT', %s, 1);
   #    """, [org_id,])
   #    conn.commit()

@app.route('/user/add', methods=['POST'])
def add_user():
   form = request.form

   fields = ["first_name", "last_name", "email", "password", "city", "state", "role"]
   req_fields = ["first_name", "email"]
   values = []
   
   for field in fields:
      form_value = form.get(field)
      if form_value in req_fields and form_value == " ":
         return jsonify (f'{field} is required field'), 400

      values.append(form_value)
   
   first_name = form.get('first_name')
   last_name = form.get('last_name')
   email = form.get('email')
   password = form.get('password')
   city = form.get('city')
   state = form.get('state')
   role = form.get('role')

   new_user_record = AppUsers(first_name, last_name, email, password, city, state, role)

   db.session.add(new_user_record)
   db.session.commit()
   
   return jsonify('User Added'), 200

@app.route('/user/activate/<user_id>', methods=['PUT'])
def activate_user(user_id):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
   if not user_record:
      return ('User not found'), 404
   user_record.active = True
   db.session.commit()

# update user's information
@app.route('/user/edit/<user_id>', methods=['PUT'])
def edit_user(user_id, first_name = None, last_name = None, email = None, password = None, city= None, state = None, active = None):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
   if not user_record:
      return ('User not found'), 404
   if request:
      form = request.form
      first_name = form.get('first_name')
      last_name = form.get('last_name')
      email = form.get('email')
      password = form.get('password')
      city = form.get('city')
      state = form.get('state')
      role = form.get('role')
      active = form.get('active')
   
   if first_name:
      user_record.first_name = first_name
   if last_name:
      user_record.last_name = last_name
   if email:
      user_record.email = email
   if password:
      user_record.password = password
   if city:
      user_record.city = city
   if state:
      user_record.state = state
   if role:
      user_record.role = role
   if active:
      user_record.active = active
   
   db.session.commit()

   # cursor.execute('SELECT user_id,first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE user_id = %s', (user_id,))
   # result = cursor.fetchone()
   # print(result)
   # set_clauses = []        
   # update_values = []

   # fields = ["first_name", "last_name", "email", "phone", "city", "state", "org_id", "active"]

   # if result:
   #    form = request.form
   #    for field in fields:
   #       form_value = form.get(field)
   #       if form_value !=None:
   #          set_clauses.append(f'{field} = %s')
   #          update_values.append(form_value)

   #    set_clause_string = ' , '.join(set_clauses)
   #    update_values.append(str(user_id))
   #    query_str = f'UPDATE Users SET {set_clause_string} WHERE user_id = %s'
   #    cursor.execute(query_str, update_values)
   #    conn.commit()
   return jsonify('User Updated'), 201
   # return ('User not found'), 404

if __name__ == '__main__':
   create_all()
   app.run()