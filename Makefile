default:

test:
	nosetests -w xnat --nologcapture

docs: doc/doc.html

doc/doc.html: doc/doc.rst
	rst2html.py doc/doc.rst doc/doc.html

clean:
	find . -name "*.pyc" -exec rm -v {} \;
	rm -f doc/doc.html

# eof
