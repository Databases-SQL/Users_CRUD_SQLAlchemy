from sqlite3 import Cursor
from flask import request, Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import marshmallow as ma
from sqlalchemy import create_engine
from sqlalchemy import text

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "crm"

engine = create_engine(f'postgresql://{database_host}/{database_name}')



db = SQLAlchemy(app)
ma  = Marshmallow(app)





class AppUsers(db.Model):
   __tablename__= "users"
   user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
   first_name = db.Column(db.String(), nullable = False)
   last_name = db.Column(db.String(), nullable = False)
   email = db.Column(db.String(), nullable = False, unique = True)
   password = db.Column(db.String(), nullable = False)
   city = db.Column(db.String())
   state = db.Column(db.String())
   active = db.Column(db.Boolean(), nullable=False, default=False)
   created_date = db.Column(db.DateTime, default=datetime.utcnow)
   role = db.Column(db.String(), default='user', nullable=False)
   
   def __init__(self, first_name, last_name, email, password, city, state, role):
      self.first_name = first_name
      self.last_name = last_name
      self.email = email
      self.password = password
      self.city = city
      self.state = state
      self.active = True
      self.role = role
   
   
class AppUsersSchema(ma.Schema):
   class Meta:
      fields = ['user_id','first_name', 'last_name', 'email', 'password', 'phone', 'created_date', 'role', 'active']
    
user_schema = AppUsersSchema()
users_schema = AppUsersSchema(many=True)



def create_all():
   print("Querying for Super Admin user...")
   user_data = db.session.query(AppUsers).filter(AppUsers.email == 'admin@devpipeline.com').first()
   if user_data == None:
      print("Super Admin not found! Creating foundation-admin@devpipeline user...")
      password = ''
      while password == '' or password is None:
         password = input(' Enter a password for Super Admin:')

      record = AppUsers('Super', 'Admin', "admin@devpipeline.com", password, "super-admin", "Orem", "Utah")

      db.session.add(record)
      db.session.commit()
   else:
      print("Super Admin user found!")




# add user using SQLAlchemy
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


# activate an user

@app.route('/user/activate/<user_id>', methods=['PUT'])
def activate_user(user_id):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
   if not user_record:
      return ('User not found'), 404
   user_record.active = True
   db.session.commit()




# deactivate an user

@app.route('/user/deactivate/<user_id>', methods=['PUT'])
def deactivate_user(user_id):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
   if not user_record:
      return ('User not found'), 404
   user_record.active = False
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

   return jsonify('User Updated'), 201




# get all users
@app.route('/user/list', methods=['GET'])
def get_all_users():
    output_json ={}

    list_of_users = []

    with engine.connect() as connection:
        result = connection.execute(text('''SELECT 
                          user_id, first_name, last_name, email, password, city, state, active
                          FROM Users  
                      '''))


    for user in result:
      new_record = {
      'user_id' : user[0],
      'first_name' : user[1],
      'last_name' : user[2],
      'email': user[3],
      'password': user[4],
      'city' : user[5],
      'state' : user[6],
      'active' : user[7]
      }

      list_of_users.append(new_record)

      output_json = {"results": list_of_users}

    return jsonify(output_json), 200




# get user by id
@app.route('/user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
  with engine.connect() as connection:
        result = connection.execute(text('SELECT user_id, first_name, last_name, email, password, city, state, active FROM Users WHERE user_id = %s', (user_id,)))


  if result:
    result_dictionary = {
      'user_id' : result[0],
      'first_name' : result[1],
      'last_name' : result[2],
      'email': result[3],
      'password': result[4],
      'city' : result[5],
      'state' : result[6],
      'active' : result[7]
    }

    return jsonify(result_dictionary), 200
  return('User not found'), 404




# # Delete an user
@app.route('/user/delete/<user_id>', methods=['DELETE'])
def user_delete(user_id):
  with engine.connect() as connection:
        result = connection.execute(text('SELECT user_id,first_name, last_name, email, password, city, state, active FROM Users WHERE user_id = %s', (user_id,)))

  if result:
    with engine.connect() as connection:
        result = connection.execute(text('DELETE FROM Users WHERE user_id = %s',(user_id,)))
    connection.commit()
    return jsonify('User Deleted'), 200
  return jsonify('User not found'), 404
  


# # Search for a key word in user's data
@app.route('/user/search/<search_term>', methods=['GET'])
def user_search(search_term):
  search_term = search_term.lower()
  with engine.connect() as connection:
    result = connection.execute(text('''SELECT first_name, last_name, city, state, email 
                     FROM Users 
                     WHERE LOWER(first_name) LIKE %s
                     OR LOWER(last_name) LIKE %s
                     OR LOWER(city) LIKE %s
                     OR LOWER(state) LIKE %s
                     OR LOWER(email) LIKE %s
                     ''',
                     (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%')
                     ))
  # results = cursor.fetchall()

  if result:
    list_of_search_results = []

    for result in result:
          list_of_search_results.append( {
         'first_name' : result[0],
         'last_name' : result[1],
         'city' : result[2],
         'state' : result[3],
         'email' : result[4],
      } )

    output_dictionary = {
      "results" : list_of_search_results
   }
    return jsonify(output_dictionary), 200

  return jsonify('Search term not found'), 404


if __name__ == '__main__':
    create_all()
    app.run()