clean-build:
	rm -rf build/
	rm -rf dist/
	rm -r *.pyo
	rm -r *.pyc
	rm -rf TheAlchemist.spec

spec:
	 pyi-makespec TheAlchemist.py  --noconsole --onefile --icon=./assets/sprites/icon.icns --add-data './assets:./assets'

build:
	pyinstaller TheAlchemist.spec --noconfirm