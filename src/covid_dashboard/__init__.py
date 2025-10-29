#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: __init__.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Package initializer and application factory for the Flask dashboard.

Usage:
from covid_dashboard import create_app
app = create_app()

Notes:
- Uses app factory pattern with blueprints for clean extensibility.
- Configuration via `config.py` and environment variables.
===========================================================================
"""
from __future__ import annotations
from .app import create_app  # re-export factory for convenience