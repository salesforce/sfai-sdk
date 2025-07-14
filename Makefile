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
	find . -name 'site' | xargs rm -rf
	find . -name '*.pyc' -delete 2>/dev/null || true
	find . -name '*.pyo' -delete 2>/dev/null || true

prerequisites:
	uv pip install -U pip setuptools wheel setuptools_scm[toml]

install: prerequisites
	uv pip install -U '.[all]'

develop: prerequisites
	uv pip install -U -e '.[dev]'
	uv pip install pre-commit
	pre-commit install

docs-install: prerequisites
	uv pip install -U -e '.[docs]'

docs-serve: docs-install
	mkdocs serve --dev-addr 127.0.0.1:8000

docs-build: docs-install
	mkdocs build

docs-deploy: docs-install
	mkdocs gh-deploy

docs-clean:
	rm -rf site/


lint:
	pre-commit run --all-files --hook-stage manual

package: prerequisites
	uv pip install setuptools>=40.8.0 wheel setuptools_scm[toml]>=6.0
	uv pip install -U build
	python3 -m build --no-isolation


test: install
	uv pip install pytest coverage pytest-cov pytest-html pytest-xdist pytest-mock fastapi httpx uvicorn requests
	pytest tests/ -v --tb=short --cov=sfai --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=pytest_report.xml

tox:
	uv pip install tox
	python3 -m tox
