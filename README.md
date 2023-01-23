# COMP0022
COMP0022 Database and Information Management Systems group 2 project

To run the simple system, go to COMP0022 folder on terminal and run the following: - docker-compose build
                                                                                   - docker-compose up 
Then on the browser type in: -localhost
                             -localhost:80
Press the "view data" button to see first 10 movies in the list (this will take some time to load the page)

To quit after running docker-compose up: press ctrl + c

To access just the mysql after running the system: 1. If you have ran with docker-compose up, open another terminal, if you have ran with     docker-compose up -d, then you should be able to use the same terminal
                                                   2. run the command "docker exec -it [container id] mysql -uroot -p 
                                                   3. You will be asked to enter password which is '123'
                                                   4. mysql bash should open

The system currently creates a mysql image and a nginx image, then creates a movie database and adds all data from movies.csv file(this is from the file we were given for this project) and shopws 10 records on the web server
