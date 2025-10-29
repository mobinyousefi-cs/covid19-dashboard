#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: data_pipeline.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Data acquisition & preprocessing.
- Downloads the dataset archive from the official source (config.DATASET_URL).
- Extracts CSV files into ./data/ and normalizes columns.
- Exposes accessor functions for dashboards and APIs.

Usage:
from covid_dashboard.data_pipeline import ensure_data, load_summary
ensure_data(app.config)
summary = load_summary(app.config)

Notes:
- Keeps a lightweight cache in memory.
- Designed to work offline after first download.
===========================================================================
"""
from __future__ import annotations
import io
import os
import re
import zipfile
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import requests

from .utils import top_n

CSV_EXPECT = {
    "covid_19_data.csv": [
        "ObservationDate",
        "Province/State",
        "Country/Region",
        "Last Update",
        "Confirmed",
        "Deaths",
        "Recovered",
    ],
    # Additional city-level CSVs may exist in the archive; we will load flexibly.
}


# ------------------------------ IO HELPERS ------------------------------ #

def _download_dataset(url: str) -> bytes:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content


def _extract_if_zip(raw: bytes, data_dir: Path) -> None:
    is_zip = False
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            is_zip = True
            zf.extractall(data_dir)
    except zipfile.BadZipFile:
        pass

    if not is_zip:
        # If not a zip, try saving as a single CSV (some mirrors return direct CSV)
        (data_dir / "covid_19_data.csv").write_bytes(raw)


# ------------------------------ PUBLIC API ------------------------------ #

_memory_cache: Dict[str, pd.DataFrame] = {}


def ensure_data(config: Dict) -> Path:
    data_dir = Path(config["DATA_DIR"]) if isinstance(config, dict) else Path(config.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    # If we already have expected CSV, skip download
    any_csv = list(data_dir.glob("*.csv"))
    if not any_csv:
        raw = _download_dataset(config["DATASET_URL"] if isinstance(config, dict) else config.DATASET_URL)
        _extract_if_zip(raw, data_dir)

    return data_dir


def _read_any_csv(data_dir: Path) -> pd.DataFrame:
    # Best-effort: read the main CSV or concatenate all CSVs found.
    csvs = list(data_dir.glob("*.csv"))
    frames = []
    for p in csvs:
        try:
            df = pd.read_csv(p)
            frames.append(df)
        except Exception:
            continue
    if not frames:
        raise FileNotFoundError("No readable CSV files found in data directory.")
    df = pd.concat(frames, ignore_index=True, sort=False)
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c: c.strip() for c in df.columns}
    df = df.rename(columns=cols)
    # Standardize column names commonly seen in DataFlair/JHU style datasets
    rename_map = {
        "Province/State": "province_state",
        "Country/Region": "country",
        "ObservationDate": "date",
        "Last Update": "last_update",
        "Confirmed": "confirmed",
        "Deaths": "deaths",
        "Recovered": "recovered",
        "Latitude": "lat",
        "Longitude": "lon",
    }
    df = df.rename(columns=rename_map)

    # Parse dates
    for dc in ["date", "last_update"]:
        if dc in df.columns:
            df[dc] = pd.to_datetime(df[dc], errors="coerce")

    # Fill missing numeric columns
    for nc in ["confirmed", "deaths", "recovered"]:
        if nc in df.columns:
            df[nc] = pd.to_numeric(df[nc], errors="coerce").fillna(0).astype(int)
        else:
            df[nc] = 0

    # Country normalization
    if "country" in df.columns:
        df["country"] = (
            df["country"].astype(str).str.strip().str.replace("\s+", " ", regex=True)
        )

    # Province normalization
    if "province_state" in df.columns:
        df["province_state"] = df["province_state"].fillna("").astype(str)

    # Lat/Lon cleanup
    for geo in ["lat", "lon"]:
        if geo in df.columns:
            df[geo] = pd.to_numeric(df[geo], errors="coerce")

    return df


def load_raw(config: Dict) -> pd.DataFrame:
    if "raw" in _memory_cache:
        return _memory_cache["raw"]
    data_dir = ensure_data(config)
    df = _read_any_csv(data_dir)
    df = _normalize_columns(df)
    _memory_cache["raw"] = df
    return df


def load_summary(config: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return (by_country, by_date) aggregated views."""
    if "by_country" in _memory_cache and "by_date" in _memory_cache:
        return _memory_cache["by_country"], _memory_cache["by_date"]

    df = load_raw(config)

    # Aggregate by country (latest available date per country)
    if "date" in df.columns:
        latest_date = df["date"].max()
        latest = df[df["date"] == latest_date].copy()
    else:
        latest = df.copy()

    group_cols = [c for c in ["country"] if c in latest.columns]
    by_country = (
        latest.groupby(group_cols)[["confirmed", "deaths", "recovered"]]
        .sum()
        .reset_index()
        .sort_values("confirmed", ascending=False)
    )

    # Aggregate time series (global)
    if "date" in df.columns:
        by_date = (
            df.groupby("date")["confirmed", "deaths", "recovered"].sum().reset_index()
        )
    else:
        by_date = pd.DataFrame(columns=["date", "confirmed", "deaths", "recovered"])

    _memory_cache["by_country"] = by_country
    _memory_cache["by_date"] = by_date
    return by_country, by_date


def load_country_detail(config: Dict, country: str) -> pd.DataFrame:
    df = load_raw(config)
    sub = df[df["country"].str.lower() == country.lower()].copy()
    if "date" in sub.columns:
        sub = (
            sub.groupby(["date", "province_state"])[["confirmed", "deaths", "recovered"]]
            .sum()
            .reset_index()
            .sort_values(["date", "confirmed"], ascending=[True, False])
        )
    return sub


def top10_countries(config: Dict) -> pd.DataFrame:
    by_country, _ = load_summary(config)
    return top_n(by_country, "confirmed", 10)