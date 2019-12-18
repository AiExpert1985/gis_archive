import os, random, string
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from models import *

UPLOAD_FOLDER = '/Feeders_archive/upload'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

# ADDING SECRET KEY USED BY session object
app.config['SECRET_KEY'] = '8xXzNqveder4b_YdD6Z3Yw'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

#--------------------------------- Messages dictionary  --------------------------------------------------

messagesDic = {
	"add": {"Arabic":"تم الاضافة", "English":"Data has been added"},
	"update": {"Arabic":"تم التحديث", "English":"Data has been edited"},
	"search": {"Arabic":"نتائج البحث", "English":"Search Result"},
	"delete": {"Arabic":"تم الحذف", "English":"Data has been deleted"}
}

errorsDic = {
	"commitErr": {"Arabic":"حدث خطأ في قاعدة البيانات", "English":"Errors during database submit"},
	"authorityErr": {"Arabic":"ليس لديك الصلاحيات لتنفيذ الايعاز", "English": "You have no authority for executing the command"},
	"fileDownloadErr": {"Arabic":"لم يتم العثور على الملف المطلوبين", "English": "File does not found"},
	"updateErr": {"Arabic":"لم يتم تحديث المعلومات", "English": "data was not updated"},
	"fileTypeErr": {"Arabic":"لا يمكن تحميل هذا النوع من الملفات", "English": "File type is not supported"}
}

#--------------------------------- Support functions for file upload  ----------------------------------------

# check if extension of upload file is within the allowed extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# avoid file name duplication
def getUniquePath(folder, filename):    
    path = os.path.join(folder, filename)
    while os.path.exists(path):
         path = path.split('.')[0] + ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + '.' + path.split('.')[1]
    return path

# to give random file names
def random_file_name(filename):
	extension = filename.rsplit('.', 1)[1].lower()
	name = ''
	for i in range(10):
		name += random.choice(string.ascii_lowercase)
	return name+"."+extension

# process the file in request and return file name if the file is ok
def processFile(request, language, page_name):
	if 'file' not in request.files:
		message ='No file part'
		return redirect(url_for('indexes', page_name=page_name, message=message))
	file = request.files['file']
	# if user does not select file, browser also
	# submit an empty part without filename
	if file.filename == '':
		message = 'No selected file'
		return redirect(url_for('indexes', page_name=page_name, message=message))
	if file and allowed_file(file.filename):
		# I replaced the standard secure_file() with my random_file_name to save unique random file names
		# filename = secure_filename(file.filename)
		filename = random_file_name(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	else:
		message = errorsDic["fileTypeErr"][language]
		return redirect(url_for('indexes', page_name=page_name, message=message))
	return filename

#--------------------------- Support functions for page acess (authorization)  -----------------------------

# check if the user has properly logged in to able able to access web pages
def registered():
    return (session.get("USER_NAME", None) is not None and session.get("PASSWORD", None) is not None)

# recieve person db object, and return one of two options, admin or user
def has_privilege():
	uploader = Uploader.query.filter(and_(Uploader.userId == session["USER_NAME"], Uploader.password == session["PASSWORD"])).first()
	return uploader.privilege.privilege == "Admin"
  
# ---------------------------------- Login / Logout / Session initiation -----------------------------------

@app.route("/")
def login():
	return render_template("login.html")

@app.route("/initiate_session/", methods=["POST"])
def initiate_seesion():
	userId = request.form.get("userId")
	password = request.form.get("password")
	if not Uploader.query.filter(and_(Uploader.userId == userId, Uploader.password == password)).all():
		return redirect(url_for("login"))
	session["USER_NAME"] = userId
	session["PASSWORD"] = password
	uploader = Uploader.query.filter(and_(Uploader.userId == userId, Uploader.password == password)).first()
	session["LANGUAGE"] = uploader.language.language;
	session["ID_NUMBER"] = uploader.id
	return redirect(url_for("indexes", page_name="upload"))

@app.route("/logout")
def logout():
	session.pop("USER_NAME")
	session.pop("PASSWORD")
	return redirect(url_for("login"))

# ------------------------------------------------- Index -----------------------------------------------

indexDic = {
	# In upload page, only display files uploaded by current uploader
	"upload": {	"stations":"Station.query.all()", 
				"feeders":"Feeder.query.all()", 
				"files":"File.query.filter_by(uploader_id=session['ID_NUMBER']).order_by(File.id.asc()).all()", 
				"has_privilege":"has_privilege()"},
	"admin_users": {"citysides":"Cityside.query.all()", 
					"privileges":"Privilege.query.all()", 
					"languages":"Language.query.all()", 
					"uploaders":"Uploader.query.order_by(Uploader.id.asc()).all()"},
	"admin_feeders": {"stations":"Station.query.all()", 
					 "feeders":"Feeder.query.order_by(Feeder.id.asc()).all()"},
	"admin_stations": {"citysides":"Cityside.query.all()", 
						"stations":"Station.query.order_by(Station.id.asc()).all()"},
	"admin_files": {"stations":"Station.query.all()", 
					"feeders":"Feeder.query.all()", 
					"uploaders":"Uploader.query.all()", 
					"files":"File.query.order_by(File.id.asc()).all()", 
					"toDate":"(datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d')"}
}

@app.route("/index/<string:page_name>")
@app.route("/index/<string:page_name>/<string:message>")
def indexes(page_name, message="none"):
	# user can access only the upload page
	if page_name != "upload" and (not registered() or not has_privilege()):
		return redirect(url_for("login"))
	pageArgs = indexDic[page_name]
	passedArgs = {}
	for key, value in pageArgs.items():
		passedArgs[key] = eval(value)
	return render_template(f"{page_name}.html", message=message, language=session["LANGUAGE"], **passedArgs)

# ------------------------------------------------- Add -----------------------------------------------

addDic = {
	"admin_users": {
			"experssions": {
					"name": 'request.form.get("user_name")',
					"userId": 'request.form.get("user_id")',
					"cityside_id": 'request.form.get("city_side")',
					"password": 'request.form.get("password")',
					"privilege_id": 'request.form.get("privilege")',
					"language_id": 'request.form.get("language")',},
			"db_query": 'Uploader(**kwQuery)'},
	"admin_stations": {
			"experssions": {
					'station': 'request.form.get("station_name")',
					'cityside_id': 'request.form.get("city_side")'},
			"db_query": 'Station(**kwQuery)'},
	"admin_feeders": {
			"experssions": {
					'feeder': 'request.form.get("feeder_name")',
					'station_id': 'request.form.get("station_id")'},
			"db_query": 'Feeder(**kwQuery)'},
	"upload": {
			"experssions": {
					'name': 'filename',
					'station_id': 'request.form.get("station_id")',
					'feeder_id': 'request.form.get("feeder_id")',
					'uploader_id': '(Uploader.query.filter(and_(Uploader.userId == session["USER_NAME"], Uploader.password == session["PASSWORD"])).first()).id',
					'updator': 'request.form.get("editor")',
					'updatingDate': 'request.form.get("e_date")',
					'note': 'request.form.get("note")'},
			"db_query": 'File(**kwQuery)'}
}

@app.route("/add", methods=["POST"])
def adds():
	if not registered() or not has_privilege():
		return redirect(url_for("login"))
	page_name = request.form.get("page_name")
	language=session["LANGUAGE"]
	# some checks for the upload page
	if page_name == "upload":
		filename = processFile(request, language, page_name)
	kwQuery = {}
	for key,value in (addDic[page_name]["experssions"]).items():
		kwQuery[key] = eval(value)
	db_object = eval(addDic[page_name]["db_query"])
	try:
		db.session.add(db_object)
		db.session.commit()
	except:
		message = errorsDic["commitErr"][language]
		return redirect(url_for('indexes', page_name=page_name, message=message))		
	message = messagesDic["add"][language]
	return redirect(url_for('indexes', page_name=page_name, message=message))

# ------------------------------------------------- Update -----------------------------------------------

updateDic = {
	"admin_users": {
		"condition":"Uploader.query.get(databaseId)",
		"experssions": ['uploader = Uploader.query.get(databaseId)',
						'uploader.userId = request.form.get("user_id")', 
						'uploader.name = request.form.get("user_name")', 
						'uploader.cityside_id = request.form.get("city_side")', 
						'uploader.password = request.form.get("password")', 
						'uploader.privilege_id = request.form.get("privilege")', 	
						'uploader.language_id = request.form.get("language")']
				},
	"admin_stations": {
		"condition": "Station.query.get(databaseId)",
		"experssions": ['station = Station.query.get(databaseId)',
						'station.station = request.form.get("station_name")',
						'station.cityside_id = request.form.get("city_side")']
				},
	"admin_feeders": {
		"condition": "Feeder.query.get(databaseId)",
		"experssions": ['feeder = Feeder.query.get(databaseId)',
						'feeder.feeder = request.form.get("feeder_name")',
						'feeder.station_id = request.form.get("station_id")']
				},
	"admin_files": {
		"condition": "File.query.get(databaseId)",
		"experssions": ['file = File.query.get(databaseId)',
						'file.station_id = request.form.get("station_id")',
						'file.feeder_id = request.form.get("feeder_id")',
						'file.updatingDate = request.form.get("e_from_date")',
						'file.updator = request.form.get("e_name")',
						'file.note = request.form.get("note")']
				}
}

@app.route("/update", methods=["POST"])
def updates():
	if not registered() or not has_privilege():
		return redirect(url_for("login"))
	databaseId = request.form.get("databaseId")
	page_name = request.form.get("page_name")
	language = session["LANGUAGE"]
	if eval(updateDic[page_name]["condition"]) == None:
		message = errorsDic["updateErr"][language]
		return redirect(url_for("indexes", page_name=page_name, message=message))		
	for line in updateDic[page_name]["experssions"]:
		exec(line)
	try:
		db.session.commit()
	except:
		message = errorsDic["commitErr"][language]
		return redirect(url_for('indexes', page_name=page_name, message=message))		
	message = messagesDic["update"][language]	
	return redirect(url_for('indexes', page_name=page_name, message=message))

# ------------------------------------------------- Delete -----------------------------------------------

deleteDic = {
	"admin_users": "Uploader.query.get(db_id)",
	"admin_feeders": "Feeder.query.get(db_id)",
	"admin_stations": "Station.query.get(db_id)",
	"admin_files": "File.query.get(db_id)"
}

@app.route("/delete/<string:page_name>/<int:db_id>")
def deletes(page_name, db_id):
	if not registered() or not has_privilege():
		return redirect(url_for("login"))
	# you can't delete accounts of primary users: first (Admin) and second (User) because they are Built in accounts
	language = session["LANGUAGE"]
	if(page_name=="admin_users" and (db_id == 1 or db_id == 2)):
		message = errorsDic["authorityErr"][language]
		return redirect(url_for('indexes', page_name=page_name, message=message))
	# execute command from string
	item = eval(deleteDic[page_name])
	try:
		db.session.delete(item)
		db.session.commit()
	except:
		message = errorsDic["commitErr"][language]
		return redirect(url_for('indexes', page_name=page_name, message=message))
	message = messagesDic["delete"][language]
	return redirect(url_for('indexes', page_name=page_name, message=message))

# ---------------------------------------- Search / Admin Files ---------------------

@app.route("/admin/files/search", methods=["POST"])
def admin_files_search():
	if not registered() or not has_privilege():
		return redirect(url_for("login"))
	language = session["LANGUAGE"]
	message = messagesDic["search"][language]
	# below would be used for the options of the form of html page
	stations = Station.query.all()
	feeders = Feeder.query.all()
	uploaders = Uploader.query.all()
	# Sending the current tomorrow date to the html to be used by date selector
	toDate = (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d')
	# initialized an empty tuple for dynamically storing the search arguments
	filters = ()
	# add to the tuple the from/to date for updating
	e_from_date = request.form.get("e_from_date")
	e_to_date = request.form.get("e_to_date")
	filters += (File.updatingDate <= e_to_date, File.updatingDate >= e_from_date)
	#if an updator is selected, add it to the filters tuple
	e_name = request.form.get("e_name")
	if e_name != "all":
		filters += (File.updator==e_name,)
	# add to the tuple the from/to dates for uploading
	u_from_date = request.form.get("u_from_date")
	u_to_date = request.form.get("u_to_date")
	filters += (File.creationDate <= u_to_date, File.creationDate >= u_from_date)
	# if an uploader is selected, add it to the filters tuple
	u_name_id = request.form.get("u_name_id")
	if u_name_id != "all":
		filters += (File.uploader_id==u_name_id,)
	# if station id is selected, then add it to the tuple
	station_id = request.form.get("station_id")
	if station_id != "all":
		filters += (File.station_id == station_id,)
	# if feeder id is selected by user, then add it to the tuple
	feeder_id = request.form.get("feeder_id")
	if feeder_id != "all":
		filters += (File.feeder_id == feeder_id,)
	# here I used the *filters as a dynamic way to add expressions to the filter 
	files = File.query.filter(and_(*filters)).all()
	return render_template("admin_files.html", files=files, stations=stations, feeders=feeders, uploaders=uploaders, 
		toDate=toDate, message=message, has_privilege=has_privilege(), language=language)

# ------------------------------------------------- Download file -----------------------------------------------

@app.route('/download/<string:page_name>/<string:filename>')
def download(page_name, filename):
	if not registered():
		return redirect(url_for("login"))
	try:
		return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
	except:
		message = errorsDic["fileDownloadErr"][language]
		return redirect(url_for('indexes', page_name=page_name, message=message))


if __name__ == "__main__":
	app.run(debug=True)