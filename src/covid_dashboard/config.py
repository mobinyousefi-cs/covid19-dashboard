#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: config.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Centralized configuration. Load secrets from environment variables.

Notes:
- Default config is safe for local development.
- Set FLASK_ENV=production for production.
===========================================================================
"""
from __future__ import annotations
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = ENV != "production"
    TESTING = False
    DATA_DIR = os.environ.get("DATA_DIR", str(DATA_DIR))
    DATASET_URL = (
        os.environ.get(
            "DATASET_URL",
            "https://data-flair.training/blogs/download-covid-19-dataset/",
        )
    )

class TestConfig(Config):
    TESTING = True
    DEBUG = True