test:
	nosetests -w xnat --nologcapture

clean:
	find . -name "*.pyc" -exec rm -v {} \;

# eof
