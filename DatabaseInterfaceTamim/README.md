Here are the packages I am using : 
	virutualenv (install it via powershell, for this you will need to write: pip install virtualenv)
	WTForms 3.0.1
	Werkzeug 1.0.1
	SQLAlchemy 1.4.29
	Python-dotenv 0.19.
	psycopg2-binary 2.9.3
	Flask 1.1.4
	Flask-WTF 1.0.0
	Flask-SQLAlchemy 2.5.1
	Flask-Migrate 2.6.0
	Flask-Bootstrap 3.3.7.1
	Flask-Script 2.0.6
	Flask-CLI: 0.4.0


How to execute: 
	1. You will need a small pre setup:
		1.1: install Postgres 14.1 (https://www.postgresql.org/download/)
		1.2: You will need to setup a password for Postgres: I suggest using this: HuServerlessProject , otherwise you will need to change line 13 in the app.py
		1.3: Open PGAdmin on your pc
		1.4: Create a new Database with the name JobTool, otherwise you will need to change line 13 in the app.py 
		1.5 activate the virtual enviroment in the powershell -->write this inside the powershell: virtualenv env  (make sure you are doing that inside the project directory)

	2. on the Terminal inside your IDE you will have to execute the following commands one after another: 
		2.1: python manage.py db init
			--> This should create a new folder inside the Project directory called "Migrations" 
		2.2: python manage.py db migrate
		2.3: python manage.py db upgrade
			--> After executing the update command, go to pgAdmin, inside our created database, expand schemes and check the tables.
				 if there is no tables or only 1 table (Alembic Versions) then right click on "Tables" and hit refresh.
					now you should see the new tables (Job, Queue and HistoricalData, Simulationstabelle) and a table called: Alembic versions
						if you dont see them then sth went wrong obviously xD 

	3. Now that the database is all set, you just need to execute this command inside the Terminal of your IDE: 
		3.1 python manage.py runserver 
			if everything works as its supposed to be, the terminal will reply with sth like this: 
					*Running on http://127.0.0.1:5000/

	Now You are all set

IMPORTANT: If you want to change on the STRUCTURE (for example changing the datatyp of an attribut) of ANY TABLE you will have to do all the following: 
					- Delete ALL the tables created on PGAdmin
					- Delete The Migrations File
					- Add your changes (AND CHECK FOR COMPATIBILITY OF THE HTML PAGES)
					- Execute the previous python commands in the IDE Terminal 
					

URLs if Using the UI (Assuming you are running on the standard port for flask (port: 5000 ) if you specify it with an anotherport you will need to change the number 5000 below): 
127.0.0.1:5000    ---> Should take you to the main page and from there you can navigate through the Navigation Bar 

Thank you in advance
Tamim
