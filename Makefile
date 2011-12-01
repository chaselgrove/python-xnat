test:
	nosetests -w xnat

clean:
	find . -name "*.pyc" -exec rm -v {} \;

# eof
