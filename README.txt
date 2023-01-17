Run following commands on the terminal:
	- docker-compose build
	- docker-compose up -d
	- docker-compose run --rm python_service python /code/app.py


Current issue: Cannot run python file on a docker container (module is not imported because the container is not running (assumption))
Successfully runs when running the python file on a terminal directly

when run using docker-compose up without "-d" there is a log telling that so this is either the the command passed to CMD has been run or it did not run indefinitely and container stopped after the command but with the debug purpose print statements in app.py it is likely it has not been run