dev:
	pip install -r test-requirements.txt

test:
	py.test ./tests

run:
	FLASK_APP=src/mytest/main.py \
	    MYTEST_CONFIGFILE=../mytest.conf \
	    flask run
	#FLASK_APP=src/mytest/main.py flask run


do:
	curl -v $T http://localhost:5000/random
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/Привітне
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/random
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/Randomness
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/Randomness
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/Randomness
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/Randomize
	sleep 1
	curl -v $T http://localhost:5000/wikipedia/qiwieuryt
	curl -v $T http://localhost:5000/stats/2
	sleep 1
	curl -v $T http://localhost:5000/joke/bill/gates
	#curl -v $T http://localhost:5000/reopen
reset:
	curl -v -XPOST http://localhost:5000/stats/reset

tar:
	find . -type f -name '*.py[co]' -delete
	tar -cz -f mytest.tgz Makefile README* requirements.txt setup.py src/ task test-requirements.txt tests/
	tar -tz -f mytest.tgz
