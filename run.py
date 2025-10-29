#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: run.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Entry point for running the Flask development server.
===========================================================================
"""
from covid_dashboard import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))