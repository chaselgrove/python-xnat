test:
	nosetests -w xnat -s

clean:
	find . -name "*.pyc" -exec rm -v {} \;

# eof
