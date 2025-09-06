PYTHON ?= python3

.PHONY: venv deps run build-mac build-win clean

venv:
	$(PYTHON) -m venv .venv

deps: venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

run: deps
	. .venv/bin/activate && $(PYTHON) gui_new.py

build-mac: deps
	. .venv/bin/activate && pyinstaller --noconsole --name IrkPUMP gui_new.py

build-win: deps
	. .venv/bin/activate && pyinstaller --noconsole --name IrkPUMP gui_new.py

clean:
	rm -rf build dist *.spec .venv


