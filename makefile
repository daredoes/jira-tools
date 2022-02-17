install-venv:
	python3 -m venv venv
	venv/bin/python3 -m pip install -r requirements.txt

activate:
	source venv/bin/activate