.PHONY: clean-pyc docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "build-ui - compile design.ui file to restoolgui.py using pyuic4"


clean: clean-pyc

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