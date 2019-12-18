from app import *

with app.app_context():
	db.create_all()

	# create baic info for 3 tables (privileges, languages, and citysides)
	# These tables have no access from the web program, ther rows are only set from here

	#filling the privilege table
	admin = Privilege(privilege="Admin")
	user = Privilege(privilege="User")
	db.session.add(admin)
	db.session.add(user)

	#filling the language table
	english = Language(language="English")
	arabic = Language(language="Arabic")
	db.session.add(english)
	db.session.add(arabic)

	#filling the city side table
	left = Cityside(cityside="Left")	
	right = Cityside(cityside="Right")
	db.session.add(left)
	db.session.add(right)

	#adding admin user
	admin_account = Uploader(name="Admin", userId="admin", password="admin", privilege_id=1, 
		cityside_id=1, language_id=1)
	user_account = Uploader(name="User", userId="user", password="user", privilege_id=2, 
		cityside_id=2, language_id=2)
	db.session.add(admin_account)
	db.session.add(user_account)

	db.session.commit()