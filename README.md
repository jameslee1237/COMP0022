# COMP0022
COMP0022 Database and Information Management Systems group 2 project

To run the simple system, go to COMP0022 folder on terminal and run the following: - docker-compose build
                                                                                   - docker-compose up -d
Then on the browser type in: -localhost
                             -localhost:80
Press the "view data" button to see first 10 movies in the list (this will take some time to load the page)

To quit after running docker-compose up -d: type in docker-compose down

To access just the mysql after running the system: 1. If you have ran with docker-compose up, open another terminal, if you have ran with     docker-compose up -d, then you should be able to use the same terminal
                                                   2. run the command "docker exec -it [container id] mysql -uroot -p 
                                                   3. You will be asked to enter password which is '123'
                                                   4. mysql bash should open

To create a database dump for back up: docker-compose exec -t mysql /usr/bin/mysqldump -uroot --password=123 movies > dump.sql
This creates a dump.sql file but if run on windows, the file encoding may be utf-16 which will cause error when starting the system. If this is the case, copy all contents of the .sql file and paste into notepad and save file as utf-8 encoding.
Also if db_volume has not been created in mysql folder when running the system (most likely when running the system for the first time) and if the following code does not exist in the .sql file: "CREATE DATABASE IF NOT EXISTS movies;
                                                        use movies;"

The system currently creates a mysql image and a nginx image, then creates a movie database and adds all data from movies.csv file(this is from the file we were given for this project) and shopws 10 records on the web server

Please let me know if you find any other errors or difficulties running the system
