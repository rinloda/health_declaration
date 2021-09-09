from app import User, Symptoms, Vaccine, Get_Vaccine, db

import os

# if os.path.exists('myDB.db'):
#   os.remove('myDB.db')
  
db.create_all()

u1 = User(id=1,user_firstname='Tan',user_lastname='Nguyen',phone_number=123456789,email_user='tn@gmail.com')
db.session.add(u1)

#############
s1 = Symptoms(id=1,current_symptom='Fever, hard breath',user_id=u1.id)
db.session.add(s1)


#############
v1 = Vaccine(id=1,
name_vaccine='Pfizer',
company_name='Pfizer Inc',
information="Pfizer develops and produces medicines and vaccines for immunology, oncology, cardiology, endocrinology, and neurology. The company has several blockbuster drugs or products that each generate more than US$1 billion in annual revenues. In 2020, 50% of the company's revenues came from the United States, 8% came from each of China and Japan, and 36% came from other countries.",
side_effect="Tiredness, Headache, Muscle pain, Chills, Fever, Nausea.")

db.session.add(v1)

############
g1 = Get_Vaccine(id=1, get_vaccine='Yes',user_id=u1.id,vaccine_id=v1.id) 



try:
  db.session.commit()
except Exception:
  db.session.rollback()

db.session.close()

#print("My user:", u1.user_firstname, u1.user_lastname)
#print("User phone:", u1.phone_number)
# print(len(u1.email_user))

# ######
# print("##############")
# print(s1)
# print(s1.current_symptom)
# print(s1.user_id)


# print("##############")
# print(v1)
# print(v1.name_vaccine)
# print(v1.user_id)