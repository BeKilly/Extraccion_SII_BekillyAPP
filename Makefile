.PHONY: install upgrade run run-headless venta compra ambos clean

SHELL := /bin/bash

# Carga variables desde .env si existe (ignora si no está)
-include .env
export

# Valores por defecto (pueden sobreescribirse en .env o por CLI)
CONFIG ?= config/sample_config.yaml
TIPOS ?= VENTA COMPRA
HEADLESS ?= true
RUT ?=

# Rutas del entorno virtual y CLI
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
CLI := $(VENV)/bin/bekilly-sii

# Flags dinámicos
HEADLESS_FLAG := $(if $(filter false,$(HEADLESS)),--no-headless,)
TIPOS_FLAGS := $(if $(TIPOS),--tipos $(TIPOS),)
RUT_FLAG := $(if $(RUT),--rut $(RUT),)

install:
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install .

upgrade:
	$(PIP) install -U .

run:
	$(CLI) --config $(CONFIG) $(HEADLESS_FLAG)

run-headless:
	$(CLI) --config $(CONFIG)

# VENTA
venta:
	$(CLI) --config $(CONFIG) --tipos VENTA $(HEADLESS_FLAG) $(RUT_FLAG)

# COMPRA
compra:
	$(CLI) --config $(CONFIG) --tipos COMPRA $(HEADLESS_FLAG) $(RUT_FLAG)

# Ambos tipos (usa TIPOS del .env o los defaults)
ambos:
	$(CLI) --config $(CONFIG) $(TIPOS_FLAGS) $(HEADLESS_FLAG) $(RUT_FLAG)

clean:
	rm -rf $(VENV) build dist *.egg-info
