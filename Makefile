clean:
	rm -rf build/
	rm -rf dist/
	rm -r *.pyo
	rm -r *.pyc
	rm -rf TheAlchemist.spec

spec:
	 pyi-makespec TheAlchemist.py  --noconsole --onefile --icon=./assets/sprites/icon.icns --add-data './assets:./assets'

build:
	pyinstaller TheAlchemist.spec --noconfirm

install:
	pip3 install --user pipenv
	python3 -m pipenv install

play:
	python3 -m pipenv run python ./TheAlchemist.py