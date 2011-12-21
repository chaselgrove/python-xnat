default:

test:
	nosetests -w xnat --nologcapture

docs: doc/doc.html

doc/doc.html: doc/doc.rst
	rst2html.py doc/doc.rst doc/doc.html

spell-doc:
	-aspell list < doc/doc.rst | sort -u | grep -vx -f doc/words

clean:
	find . -name "*.pyc" -exec rm -v {} \;
	rm -f doc/doc.html

# eof
