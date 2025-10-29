#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: tests/test_app_factory.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================
"""
from covid_dashboard import create_app


def test_app_creation():
    app = create_app()
    assert app is not None
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200