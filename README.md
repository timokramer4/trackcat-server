# Trackcat webserver

This application is a web application developed under Python and Flask, designed for the [Trackcat android app](https://github.com/timokramer4/trackcat-android). On the one hand, it contains possible server interfaces for the communication of the applications running on Android and iOS with the database and, on the other hand, a coresponding web-based application for computer use. The data is stored in a MySQL database and is the central core of this application - without a database, this application will not work.

## Requirements

There are certain system environment requirements for running this application:

- Running Python with Flask extension
- Working MySQL database
- Port forwarding (only if external use desired)

## Preparation

### MySQL database

Before the web server can be started, the basic structure of the database must first exist, this can be done using the SQL script `DatabaseCreationScript.sql` located in the `Database` folder. Alternatively, the MySQL Workbench schema (`DatabaseScheme.mwb`) can be called to create the database instances. 

After completing the database preparation, the structure of the database with its entities should now look as follows:

 - TrackCatDB
   - liveRecords
   - locations
   - records
   - users
   - users_has_users

If an external database or the access data for the database differ from the normal ones, then the following lines in `main.py` must be edited at the beginning:

```python
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'TrackCatDB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
```

In order for server redirects to work, the use of a custom domain under which the page can be reached must be specified below. This information is mandatory, otherwise redirects will not work correctly:

```python
app.config['BASE_URL'] = "http://HERE_YOUR_ADDRESS:5000"
```

### Webserver

Once Python and Flask are installed, you can proceed with the installation of the necessary Flask extensions. To do this, the following commands must be executed:

```console
$ pip3 install flask
$ pip3 install simplejson
$ pip3 install flask-mysql
$ pip3 install flask-login
$ pip3 install passlib
$ pip3 install python-dateutil
```

### Mail settings

For the mail transfer of the server to work, the settings of the mail server to be used must be changed in `mailSend.py`. This is done in the following lines:

```python
SMTP_SERVER = "YOUR_SMTP_SERVER_ADDRESS"
SMTP_FROM = "YOUR_EMAIL_ADDRESS"
SMTP_PASSWORD = "YOUR_EMAIL_PASSWORD"
SMTP_PORT = 587
```

## Launching

After installing the database and all necessary Flask extensions to run this script, the web server can be started with the following command. It should be noted that this must be done from the folder where the `main.py` script is located so that references to static data will still work:

```console
$ py main.py
```

