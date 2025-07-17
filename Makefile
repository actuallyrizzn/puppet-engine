test:
	pytest

coverage:
	pytest --cov=src --cov-report=html 