#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: utils.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Shared utility helpers: caching, formatting, JSON responses.
===========================================================================
"""
from __future__ import annotations
from functools import lru_cache
from typing import Any, Dict

import pandas as pd


def to_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def fmt_int(n: int | float | None) -> str:
    if n is None:
        return "0"
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)


@lru_cache(maxsize=8)
def top_n(df: pd.DataFrame, col: str, n: int = 10) -> pd.DataFrame:
    return df.sort_values(col, ascending=False).head(n).copy()