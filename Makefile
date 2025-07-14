SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = build

clean:
	find . -name '*egg-info' | xargs rm -rf
	find . -name '.benchmarks' | xargs rm -rf
	find . -name '.coverage' | xargs rm -rf
	find . -name '.mypy_cache' | xargs rm -rf
	find . -name '.pyre' | xargs rm -rf
	find . -name '.pytest_cache' | xargs rm -rf
	find . -name '.tox' | xargs rm -rf
	find . -name '__pycache__' | xargs rm -rf
	find . -name 'reports' | xargs rm -rf
	find . -name '.ruff_cache' | xargs rm -rf
	find . -name 'htmlcov' | xargs rm -rf
	find . -name 'dist' | xargs rm -rf
	find . -name 'build' | xargs rm -rf
	find . -name '*.pyc' -delete 2>/dev/null || true
	find . -name '*.pyo' -delete 2>/dev/null || true

prerequisites:
	python3 -m pip install -U pip setuptools wheel setuptools_scm[toml]

install: prerequisites
	python3 -m pip install -U --upgrade-strategy eager '.[all]'

develop: prerequisites
	python3 -m pip install -U --upgrade-strategy eager -e '.[dev]'
	python3 -m pip install pre-commit
	pre-commit install


lint:
	pre-commit run --all-files --hook-stage manual

package: prerequisites
	python3 -m pip install setuptools>=40.8.0 wheel setuptools_scm[toml]>=6.0
	python3 -m pip install -U --upgrade-strategy eager build
	python3 -m build --no-isolation


test: install
	python3 -m pip install pytest coverage pytest-cov pytest-html pytest-xdist pytest-mock fastapi httpx uvicorn requests
	pytest tests/ -v --tb=short --cov=sfai --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=pytest_report.xml

tox:
	python3 -m pip install tox
	python3 -m tox
