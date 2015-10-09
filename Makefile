all: check flake8

flake8:
	flake8 . test

check:
	./test

loc:
	@wc $(shell find . -name "*.py")
