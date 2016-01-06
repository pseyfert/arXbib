test:
	python setup.py test

install:
	pip install . --user --upgrade

.PHONY: test install
