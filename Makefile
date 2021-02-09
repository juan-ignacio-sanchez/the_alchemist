clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.pyo
	rm -rf *.pyc

build-mac:
	./mac-builder.sh

build-linux:
	./linux-builder.sh

build-windows:
	./windows-builder.sh

build-all: build-linux build-mac build-windows

install:
	pip3 install --user pipenv
	python3 -m pipenv install

play:
	python3 -m pipenv run python ./TheAlchemist.pyc