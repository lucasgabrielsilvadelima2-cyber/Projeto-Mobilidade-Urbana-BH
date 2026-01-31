# Makefile para facilitar comandos comuns

.PHONY: help install test run clean format lint docs

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    - Instala dependências"
	@echo "  make test       - Executa testes"
	@echo "  make run        - Executa pipeline completo"
	@echo "  make clean      - Remove arquivos temporários"
	@echo "  make format     - Formata código com black"
	@echo "  make lint       - Verifica qualidade do código"
	@echo "  make docs       - Gera documentação"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --cov=src --cov-report=html

run:
	python src/pipeline.py

run-bronze:
	python src/pipeline.py --layers bronze

run-silver:
	python src/pipeline.py --layers silver

run-gold:
	python src/pipeline.py --layers gold

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

format:
	black src/ tests/
	isort src/ tests/

lint:
	flake8 src/ tests/
	mypy src/

docs:
	@echo "Documentação disponível em:"
	@echo "  - README.md"
	@echo "  - docs/ARCHITECTURE.md"
