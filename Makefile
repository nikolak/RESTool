.PHONY: clean-pyc docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "build-ui - compile design.ui file to restoolgui.py using pyuic4"
	@echo "strip-osx - remove unecessary files bundeled by py2app"
	@echo "build-osx - build os x distributable using py2app"

clean: clean-pyc

strip-osx:
	rm -rf dist/RESTool.app/Contents/Frameworks/QtDeclarative.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtDesigner.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtHelp.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtMultimedia.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtNetwork.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtOpenGL.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtScript.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtScriptTools.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtSql.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtSvg.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtTest.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtWebKit.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtXml.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/QtXmlPatterns.framework
	rm -rf dist/RESTool.app/Contents/Frameworks/phonon.framework
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/phonon.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtDeclarative.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtDesigner.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtHelp.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtMultimedia.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtNetwork.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtOpenGL.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtScript.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtScriptTools.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtSql.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtSvg.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtTest.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtWebKit.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtXml.so
	rm -f dist/RESTool.app/Contents/Resources/lib/python2.7/lib-dynload/PyQt4/QtXmlPatterns.so

build-osx:
	python setup.py py2app -O2 -S --qt-plugins QtCore,QtGui

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

lint:
	flake8 RESTool tests

docs:
	rm -f docs/RESTool.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ RESTool
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

build-ui:
	pyuic4 RESTool/ui/design_v2.ui -o RESTool/restoolgui.py
