
import re
import math
import html
import base64
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta
import shutil
import hashlib
import os
import json
import time
import zipfile
import xml.etree.ElementTree as ET

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from scipy import stats


APP_NAME = "TELLUM ULTIMUM™"
if os.environ.get("TELLUM_HEADLESS_SYNC") != "1":
    st.set_page_config(page_title=APP_NAME, layout="wide", initial_sidebar_state="collapsed")
MOTTO = "Veni. Vidi. Perfeci."
ROMAN_GOLD = "#C9A84C"
ROMAN_IVORY = "#E8E0D0"
ROMAN_CRIMSON = "#8B1A1A"
ROMAN_BLACK = "#0a0a0a"
ROMAN_NAVY = "#0D1B2A"
ROMAN_GOLD_BORDER = "rgba(201, 168, 76, 0.35)"
ROMAN_GOOGLE_FONTS = "@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Cinzel+Decorative:wght@400;700&display=swap');"

ROMAN_HELMET_SVG = (
    '<svg class="tu-helmet-icon" width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M12 2C8.1 2 5 5.1 5 9v2h1.1l.9 7.2h10l.9-7.2H19V9c0-3.9-3.1-7-7-7zm0 2c2.8 0 5 2.2 5 5v1H7V9c0-2.8 2.2-5 5-5z"/>'
    '<path fill="currentColor" d="M9 20h6v2H9z" opacity=".85"/></svg>'
)


def roman_emblem_svg(size=40):
    return f"""
<svg class="tu-roman-emblem" width="{size}" height="{size}" viewBox="0 0 64 64" aria-hidden="true">
  <circle cx="32" cy="34" r="26" fill="none" stroke="{ROMAN_GOLD}" stroke-width="1.6" opacity=".85"/>
  <path d="M8 34c6-10 16-16 24-16s18 6 24 16" fill="none" stroke="{ROMAN_GOLD}" stroke-width="1.4" opacity=".7"/>
  <path d="M10 30c5 8 14 12 22 12s17-4 22-12" fill="none" stroke="{ROMAN_GOLD}" stroke-width="1.2" opacity=".55"/>
  <path d="M32 10 L36 18 L44 18 L38 23 L40 31 L32 26 L24 31 L26 23 L20 18 L28 18 Z" fill="{ROMAN_GOLD}" opacity=".92"/>
  <text x="32" y="48" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="8" font-family="Cinzel, Georgia, serif" font-weight="700">SPQR</text>
</svg>
"""


def roman_app_theme_css():
    return f"""
<style>
{ROMAN_GOOGLE_FONTS}
.stApp {{
    background: {ROMAN_BLACK};
    color: {ROMAN_IVORY};
    font-family: Georgia, "Cinzel Decorative", serif;
}}
.block-container,
.stMainBlockContainer,
.main .block-container {{
    padding-top: 0.75rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    max-width: 100% !important;
}}
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main {{
    max-width: 100%;
    width: 100%;
    background: {ROMAN_BLACK};
}}
header[data-testid="stHeader"] {{
    background: rgba(10, 10, 10, 0.96);
    border-bottom: 1px solid {ROMAN_GOLD_BORDER};
}}
section[data-testid="stSidebar"] {{
    background: {ROMAN_NAVY};
    border-right: 1px solid {ROMAN_GOLD_BORDER};
}}
section[data-testid="stSidebar"] * {{
    color: {ROMAN_IVORY};
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {ROMAN_GOLD} !important;
    font-family: Cinzel, Georgia, serif !important;
    text-transform: uppercase;
    letter-spacing: .6px;
    font-size: .78rem !important;
}}
[data-testid="stMetric"] {{
    background: {ROMAN_NAVY};
    border: 1px solid {ROMAN_GOLD_BORDER};
    border-radius: 12px;
    padding: 14px;
    box-shadow: inset 0 0 18px rgba(201, 168, 76, 0.08);
}}
[data-testid="stMetricLabel"] {{
    color: {ROMAN_GOLD} !important;
    font-family: Cinzel, Georgia, serif !important;
    text-transform: uppercase;
    letter-spacing: .5px;
}}
[data-testid="stMetricValue"] {{
    color: {ROMAN_IVORY} !important;
    font-family: Cinzel, Georgia, serif !important;
}}
h1, h2, h3, h4 {{
    color: {ROMAN_GOLD} !important;
    font-family: Cinzel, Georgia, serif !important;
    text-transform: uppercase;
    letter-spacing: .5px;
}}
p, span, label, .stMarkdown {{
    color: {ROMAN_IVORY};
}}
.stTextInput input, .stNumberInput input, .stTextArea textarea, [data-baseweb="select"] > div {{
    background: {ROMAN_NAVY} !important;
    color: {ROMAN_IVORY} !important;
    border-color: {ROMAN_GOLD_BORDER} !important;
}}
.stButton > button {{
    background: linear-gradient(180deg, rgba(201,168,76,.22), rgba(201,168,76,.08)) !important;
    color: {ROMAN_GOLD} !important;
    border: 1px solid {ROMAN_GOLD_BORDER} !important;
    font-family: Cinzel, Georgia, serif !important;
    text-transform: uppercase;
    letter-spacing: .4px;
}}
.stProgress > div > div {{
    background: {ROMAN_NAVY} !important;
    border: 1px solid {ROMAN_GOLD_BORDER};
    border-radius: 999px;
}}
.stProgress > div > div > div {{
    background: linear-gradient(90deg, #8B6914, {ROMAN_GOLD}) !important;
    border-radius: 999px;
    box-shadow: 0 0 12px rgba(201, 168, 76, 0.45);
}}
.tu-app-header {{
    width: 100%;
    padding: 8px 0 14px 0;
    margin: 0 0 12px 0;
    border-bottom: 1px solid {ROMAN_GOLD_BORDER};
    background: linear-gradient(180deg, rgba(13,27,42,.55), rgba(10,10,10,0));
}}
.tu-brand-lockup {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.tu-brand-text {{
    display: flex;
    flex-direction: column;
    gap: 2px;
}}
.tu-logo {{
    height: 42px;
    width: auto;
    display: block;
    filter: drop-shadow(0 0 8px rgba(201,168,76,.35));
}}
.tu-logo-mark {{
    height: 42px;
    width: 42px;
    border-radius: 50%;
    background: {ROMAN_NAVY};
    color: {ROMAN_GOLD};
    border: 1px solid {ROMAN_GOLD_BORDER};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 11px;
    letter-spacing: .5px;
    font-family: Cinzel, Georgia, serif;
    box-shadow: inset 0 0 16px rgba(201, 168, 76, 0.15);
}}
.tu-brand-title {{
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 1.2px;
    color: {ROMAN_GOLD};
    line-height: 1.05;
    font-family: Cinzel, Georgia, serif;
    text-transform: uppercase;
}}
.tu-brand-tagline {{
    font-size: 12px;
    font-weight: 400;
    font-style: italic;
    color: {ROMAN_GOLD};
    line-height: 1.2;
    font-family: "Cinzel Decorative", Georgia, serif;
    opacity: .92;
}}
[data-testid="stTabs"],
[data-testid="stTabContent"],
[data-testid="stMarkdownContainer"] {{
    width: 100%;
}}
div[data-baseweb="tab-list"] {{
    gap: 8px;
    background: {ROMAN_BLACK};
    border-bottom: 1px solid {ROMAN_GOLD_BORDER};
    padding-bottom: 4px;
}}
button[data-baseweb="tab"] {{
    color: {ROMAN_IVORY} !important;
    font-weight: 700 !important;
    font-family: Cinzel, Georgia, serif !important;
    text-transform: uppercase;
    letter-spacing: .45px;
    background: transparent !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {ROMAN_GOLD} !important;
    border-bottom: 2px solid {ROMAN_GOLD} !important;
}}
div[data-testid="stExpander"] {{
    background: {ROMAN_NAVY};
    border: 1px solid {ROMAN_GOLD_BORDER};
    border-radius: 12px;
    box-shadow: inset 0 0 20px rgba(201, 168, 76, 0.06);
}}
div[data-testid="stVerticalBlock"] > div:has(iframe[title="streamlit.components.v1.components.html"]) {{
    width: 100%;
}}
div[data-testid="stVerticalBlock"] > div:has(iframe[title="streamlit.components.v1.components.html"]) iframe {{
    display: block;
    width: 100% !important;
    max-width: 100%;
    border: none;
    background: {ROMAN_BLACK};
}}
</style>
"""


def classic_app_theme_css():
    return """
<style>
.stApp {
    background: #fbf8f2;
    color: #08245c;
}
.block-container,
.stMainBlockContainer,
.main .block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    max-width: 100% !important;
}
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main {
    max-width: 100%;
    width: 100%;
}
header[data-testid="stHeader"] {
    background: rgba(251, 248, 242, 0.92);
}
section[data-testid="stSidebar"] {
    background: #f2f2f7;
    border-right: 1px solid rgba(0,0,0,0.1);
}
section[data-testid="stSidebar"] label {
    color: #6b7280 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .55px !important;
    font-family: system-ui, -apple-system, sans-serif !important;
}
section[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px;
    padding: 8px 10px !important;
    min-width: 0;
    overflow: visible;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
section[data-testid="stSidebar"] [data-testid="stMetricLabel"],
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] > div,
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] > div > div,
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] label {
    font-size: 10px !important;
    line-height: 1.2 !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    color: #6b7280 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricValue"],
section[data-testid="stSidebar"] [data-testid="stMetricValue"] > div,
section[data-testid="stSidebar"] [data-testid="stMetricValue"] > div > div {
    font-size: 14px !important;
    line-height: 1.2 !important;
    overflow: visible !important;
    text-overflow: unset !important;
    white-space: normal !important;
    word-break: break-word !important;
    color: #1c1c1e !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] div[data-testid="column"] {
    min-width: 0 !important;
}
section[data-testid="stSidebar"] div[data-testid="column"] > div {
    min-width: 0 !important;
}
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 0 0 0.5px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] > div > div,
[data-testid="stMetricLabel"] label {
    color: #6b7280 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .55px !important;
    font-family: system-ui, -apple-system, sans-serif !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.3 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] > div > div {
    color: #1c1c1e !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    letter-spacing: -.25px !important;
    font-family: system-ui, -apple-system, sans-serif !important;
    overflow: visible !important;
    text-overflow: unset !important;
    white-space: normal !important;
    word-break: break-word !important;
    line-height: 1.25 !important;
}
[data-testid="stDecoration"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    display: none !important;
}
h1, h2, h3, h4, p, label {
    color: #08245c;
}
.tu-app-header {
    width: 100%;
    padding: 6px 0 14px 0;
    margin: 0 0 12px 0;
    border-bottom: 1px solid rgba(201, 168, 76, 0.35);
    background: transparent !important;
    color: #E8E0D0 !important;
}
.tu-brand-lockup {
    display: flex;
    align-items: center;
    gap: 12px;
}
.tu-logo-wrap {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border-radius: 10px;
    padding: 5px 8px;
    box-shadow: none;
}
.tu-logo {
    height: 36px;
    width: auto;
    display: block;
    opacity: 1 !important;
    filter: brightness(0) saturate(100%) invert(72%) sepia(47%) saturate(497%) hue-rotate(6deg) brightness(95%) contrast(89%)
        drop-shadow(0 0 6px rgba(201, 168, 76, 0.4));
}
.tu-logo-mark {
    height: 36px;
    width: 36px;
    border-radius: 8px;
    background: transparent;
    color: #C9A84C;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 12px;
    letter-spacing: .4px;
    box-shadow: none;
}
.tu-brand-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.tu-brand-title {
    font-size: 20px;
    font-weight: 900;
    letter-spacing: .55px;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    line-height: 1.05;
    opacity: 1 !important;
}
.tu-brand-tagline {
    font-size: 12px;
    font-weight: 600;
    color: #333333 !important;
    -webkit-text-fill-color: #333333 !important;
    line-height: 1.25;
    margin-top: 1px;
    opacity: 1 !important;
}
[data-testid="stMarkdownContainer"] .tu-app-header,
[data-testid="stMarkdownContainer"] .tu-app-header .tu-brand-title,
[data-testid="stMarkdownContainer"] .tu-app-header .tu-brand-tagline {
    opacity: 1 !important;
}
[data-testid="stMarkdownContainer"] .tu-app-header .tu-brand-title {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}
[data-testid="stMarkdownContainer"] .tu-app-header .tu-brand-tagline {
    color: #333333 !important;
    -webkit-text-fill-color: #333333 !important;
}
[data-testid="stTabs"],
[data-testid="stTabContent"],
[data-testid="stMarkdownContainer"] {
    width: 100%;
}
div[data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: 1px solid rgba(0,0,0,0.10);
    padding-bottom: 2px;
}
button[data-baseweb="tab"] {
    color: #6b7280 !important;
    font-weight: 600 !important;
    font-family: system-ui, -apple-system, sans-serif !important;
    font-size: 13.5px !important;
    letter-spacing: .1px !important;
    padding-bottom: 8px !important;
    transition: color 0.15s ease !important;
}
button[data-baseweb="tab"]:hover {
    color: #08245c !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #08245c !important;
    border-bottom: 2.5px solid #C9A84C !important;
    font-weight: 700 !important;
}
div[data-testid="stVerticalBlock"] > div:has(iframe[title="streamlit.components.v1.components.html"]) {
    width: 100%;
}
div[data-testid="stVerticalBlock"] > div:has(iframe[title="streamlit.components.v1.components.html"]) iframe {
    display: block;
    width: 100% !important;
    max-width: 100%;
    border: none;
}
div[data-testid="stExpander"]:has(.ocr-q-status-pending) {
    border: 1px solid #e8c96a !important;
    border-left: 4px solid #d98c00 !important;
    background: #fffaf0 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
div[data-testid="stExpander"]:has(.ocr-q-status-pending) summary,
div[data-testid="stExpander"]:has(.ocr-q-status-pending) summary * {
    color: #7a4b00 !important;
    font-weight: 700 !important;
}
div[data-testid="stExpander"]:has(.ocr-q-status-imported) {
    border: 1px solid #9ed4b6 !important;
    border-left: 4px solid #2d8659 !important;
    background: #eefaf3 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
div[data-testid="stExpander"]:has(.ocr-q-status-imported) summary,
div[data-testid="stExpander"]:has(.ocr-q-status-imported) summary * {
    color: #1f5c3a !important;
    font-weight: 700 !important;
}
div[data-testid="stExpander"]:has(.ocr-q-status-skipped) {
    border: 1px solid #d1d5db !important;
    border-left: 4px solid #9ca3af !important;
    background: #f3f4f6 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
    opacity: 0.88;
}
div[data-testid="stExpander"]:has(.ocr-q-status-skipped) summary,
div[data-testid="stExpander"]:has(.ocr-q-status-skipped) summary * {
    color: #6b7280 !important;
    font-weight: 600 !important;
}
/* ---- Expander base: clean white card ---- */
div[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 6px;
}
/* ---- Radio → iOS pill ---- */
[data-testid="stRadio"] > div {
    gap: 4px !important;
    flex-wrap: wrap !important;
}
[data-testid="stRadio"] label {
    background: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    border-radius: 999px !important;
    padding: 5px 15px !important;
    font-family: system-ui, -apple-system, sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #08245c !important;
    margin: 0 2px 4px 0 !important;
    min-height: 0 !important;
    text-transform: none !important;
    cursor: pointer;
    transition: background 0.12s ease, color 0.12s ease;
}
[data-testid="stRadio"] label[data-checked="true"],
[data-testid="stRadio"] label:has(input:checked) {
    background: #08245c !important;
    border-color: #08245c !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}
[data-testid="stRadio"] label[data-checked="true"] *,
[data-testid="stRadio"] label:has(input:checked) * {
    color: #ffffff !important;
}
/* ---- Buttons ---- */
.stButton > button,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"] {
    background: #08245c !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: system-ui, -apple-system, sans-serif !important;
    letter-spacing: .15px !important;
    padding: 7px 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.18) !important;
    transition: background 0.12s ease !important;
}
.stButton > button *,
[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-secondary"] * {
    color: #ffffff !important;
}
.stButton > button:hover,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-secondary"]:hover {
    background: #0a2f7a !important;
}
/* ---- Progress bars ---- */
.stProgress > div > div {
    background: #e5e5ea !important;
    border-radius: 999px !important;
    border: none !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, #08245c, #3b6fd4) !important;
    border-radius: 999px !important;
    box-shadow: none !important;
}
/* ---- Metric delta — keep Streamlit's semantic green/red ---- */
[data-testid="stMetricDelta"] {
    overflow: visible !important;
    white-space: normal !important;
}
/* ---- Alert / info boxes — ensure text is readable ---- */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] label {
    color: inherit !important;
}
/* ---- Inputs — subtle white card style ---- */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
[data-baseweb="select"] > div {
    background: #ffffff !important;
    border-color: rgba(0,0,0,0.15) !important;
    border-radius: 10px !important;
    color: #1c1c1e !important;
}
</style>
"""


def command_center_tab_css():
    return f"""
<style>
.cc-page-marker {{ display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }}
.stApp:has(.cc-page-marker) .tu-app-header {{
  padding: 2px 0 6px 0 !important;
  margin: 0 0 4px 0 !important;
}}
.stApp:has(.cc-page-marker) .tu-brand-title {{ font-size: 15px !important; letter-spacing: .6px !important; }}
.stApp:has(.cc-page-marker) .tu-brand-tagline {{ display: none !important; }}
.stApp:has(.cc-page-marker) .tu-logo, .stApp:has(.cc-page-marker) .tu-logo-mark {{
  height: 28px !important; width: 28px !important;
}}
.stApp:has(.cc-page-marker) .block-container,
.stApp:has(.cc-page-marker) .stMainBlockContainer {{
  padding-top: 0.15rem !important;
  max-width: 100% !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker),
div[data-baseweb="tab-panel"]:has(.cc-page-marker) {{
  overflow: hidden !important;
  max-height: calc(100vh - 108px) !important;
  padding-top: 0 !important;
  margin-top: 0 !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stVerticalBlock"],
div[data-baseweb="tab-panel"]:has(.cc-page-marker) [data-testid="stVerticalBlock"] {{
  gap: 0 !important;
  margin-top: 0 !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stVerticalBlockBorderWrapper"] {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-bottom: 2px !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stRadio"] {{
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stRadio"] > div {{
  gap: 4px !important;
  flex-wrap: nowrap !important;
  min-height: 0 !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stRadio"] label {{
  background: #ffffff !important;
  border: 1px solid #e5e5ea !important;
  border-radius: 999px !important;
  padding: 4px 11px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  margin: 0 !important;
  min-height: 0 !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stRadio"] label:has(input:checked) {{
  background: #007aff !important;
  border-color: #007aff !important;
  color: #ffffff !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stAlert"],
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stCaptionContainer"],
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stExpander"] {{
  display: none !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) iframe {{
  background: #f2f2f7 !important;
  display: block;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  overflow: hidden !important;
  border-radius: 16px !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker),
div[data-baseweb="tab-panel"]:has(.cc-page-marker) {{
  background: #f2f2f7 !important;
}}
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stMarkdownContainer"]:has(.cc-page-marker),
div[data-testid="stTabPanel"]:has(.cc-page-marker) [data-testid="stMarkdownContainer"]:has(style) {{
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
}}
.cc-coaching-notice {{
  background: linear-gradient(135deg, #fff8e6 0%, #fff3cd 100%);
  border: 1px solid #f0c040;
  border-left: 4px solid #007aff;
  border-radius: 12px;
  padding: 10px 14px;
  margin: 0 0 10px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
}}
.cc-coaching-notice-title {{
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #007aff;
  margin-bottom: 4px;
}}
.cc-coaching-notice-body {{
  font-size: 14px;
  line-height: 1.45;
  color: #1c1c1e;
  margin-bottom: 4px;
}}
.cc-coaching-notice-hint {{
  font-size: 12px;
  color: #636366;
}}
a.cc-coaching-notice-link {{
  text-decoration: none;
  color: inherit;
  display: block;
  cursor: pointer;
  transition: filter 0.15s ease, box-shadow 0.15s ease;
}}
a.cc-coaching-notice-link:hover {{
  filter: brightness(0.98);
  box-shadow: 0 3px 12px rgba(0,0,0,.10);
}}
a.cc-coaching-notice-link:active {{
  filter: brightness(0.96);
}}
</style>
"""


def scrollable_tab_css():
    """Allow long tab content (Import Hub, Auto Inbox, etc.) to scroll normally."""
    return """
<style>
.tu-scroll-tab-marker { display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main {
  overflow-y: auto !important;
  overflow-x: hidden !important;
  max-height: none !important;
}
div[data-testid="stTabPanel"]:has(.tu-scroll-tab-marker),
div[data-baseweb="tab-panel"]:has(.tu-scroll-tab-marker) {
  overflow: visible !important;
  max-height: none !important;
}
</style>
"""
DATA_DIR = Path.home() / "Desktop" / "Programs" / "TellumUltimumData"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "tellum_ultimum.sqlite3"
UPLOAD_DIR = DATA_DIR / "TU Uploads"
EXPORT_DIR = DATA_DIR / "TU Exports"
INBOX_DIR = DATA_DIR / "TU Inbox"

HEALTH_DATA_SYNC_EXTENSIONS = {".png", ".jpg", ".jpeg", ".heic", ".pdf", ".xml", ".csv", ".xlsx", ".xls", ".txt"}
HEALTH_DATA_SOURCE_CANDIDATES = [
    Path("G:/My Drive/Salim Personal/Health Data"),
    Path.home() / "Google Drive" / "My Drive" / "Health Data",
    Path.home() / "Google Drive" / "Health Data",
    Path.home() / "My Drive" / "Health Data",
    Path("G:/My Drive/Health Data"),
    Path("G:/Health Data"),
]


def _folder_is_ready(path):
    try:
        return bool(path) and Path(path).exists() and Path(path).is_dir()
    except OSError:
        return False


def detect_default_health_data_source_folder():
    for candidate in HEALTH_DATA_SOURCE_CANDIDATES:
        if _folder_is_ready(candidate):
            return Path(candidate)
    return HEALTH_DATA_SOURCE_CANDIDATES[0]


def wait_for_health_data_source_folder(timeout_sec=12):
    """Google Drive for Desktop can mount a few seconds after launch — wait briefly."""
    deadline = time.time() + max(0.0, float(timeout_sec))
    last = detect_default_health_data_source_folder()
    while True:
        configured = get_text_setting("health_data_source_folder_path", "")
        candidates = []
        if configured:
            candidates.append(Path(configured).expanduser())
        candidates.extend(HEALTH_DATA_SOURCE_CANDIDATES)
        for candidate in candidates:
            if _folder_is_ready(candidate):
                resolved = Path(candidate)
                if str(resolved) != configured:
                    save_text_setting("health_data_source_folder_path", str(resolved))
                return resolved
        if time.time() >= deadline:
            return last if _folder_is_ready(last) else (Path(configured).expanduser() if configured else last)
        time.sleep(0.6)


for folder in [
    UPLOAD_DIR,
    EXPORT_DIR,
    INBOX_DIR,
    UPLOAD_DIR / "DEXA",
    UPLOAD_DIR / "FatSecret",
    UPLOAD_DIR / "Oura",
    UPLOAD_DIR / "Workouts",
    UPLOAD_DIR / "Other",
    UPLOAD_DIR / "AppleHealth",
    UPLOAD_DIR / "Torso",
]:
    folder.mkdir(parents=True, exist_ok=True)

DAILY_COLS = [
    "log_date", "weight_lbs", "calories", "protein_g", "carbs_g", "fat_g",
    "steps", "active_energy", "resting_energy", "distance_miles",
    "sleep_minutes", "sleep_score", "readiness_score", "oura_burn",
    "workout", "workout_intensity", "subjective_energy", "notes"
]

DEFAULTS = {
    "baseline_maintenance": 2700.0,
    "target_deficit": 500.0,
    "current_weight_lbs": 175.9,
    "current_body_fat_pct": 12.5,
    "goal_body_fat_pct": 10.0,
    "protein_target_g": 190.0,
    "step_calories_per_1000": 45.0,
    "min_trend_days": 14.0,
    "fat_loss_fraction": 0.90,
    "annual_lean_gain_lbs": 5.0,
    "muscle_gain_fraction": 0.55,
    "default_step_goal": 12000.0,
    "default_workout_burn": 350.0,
    "snack_calorie_unit": 150.0,
    "adaptive_maintenance_adjustment": 0.0,
}

FUEL_WORKOUT_DEFAULTS = {
    "None": 0,
    "Workout A": 250,
    "Workout B": 300,
    "Workout C": 450,
    "StairMaster only": 300,
    "Long walk / high step day": 0,
}
FUEL_ROTATION_WORKOUTS = ["Workout A", "Workout B", "Workout C"]
SIMPLE_DAILY_WORKOUTS = ["Workout A", "Workout B", "Workout C", "StairMaster only", "None"]

# Cut target: estimated scale weight at ~10% body fat.
GOAL_WEIGHT_AT_10PCT_BF = 165.0
KCAL_PER_LB_FAT = 3500.0
EXPECTED_WEEKLY_WORKOUTS = (5, 6)
SLEEP_QUALITY_OPTIONS = ["Poor", "Fair", "Good", "Excellent"]
SLEEP_QUALITY_TO_SCORE = {
    "Poor": 45.0,
    "Fair": 62.0,
    "Good": 78.0,
    "Excellent": 90.0,
}

# Minimum net carbs (g) by day type — enforced in Daily Sync.
FUEL_CARB_MINIMUMS = {
    "None": 220,
    "Long walk / high step day": 220,
    "Workout A": 260,
    "Workout B": 350,
    "Workout C": 260,
    "StairMaster only": 260,
}
FUEL_CARB_DEFAULT_MINIMUM = 220
KRISPIES_CARB_FRACTION = 0.87
FRUIT_CARB_GRAMS = 13.0

MISSION_MODE_KEYS = ["fat_loss", "weight_loss", "muscle_gain", "strength_gain"]

MISSION_LABELS = {
    "fat_loss": "Fat loss",
    "weight_loss": "Weight loss",
    "muscle_gain": "Muscle gain",
    "strength_gain": "Strength gain",
}

MISSION_DESCRIPTIONS = {
    "fat_loss": "Original campaign — cut toward goal body fat % with a daily calorie deficit.",
    "weight_loss": "Scale-focused cut — larger deficit, moderate protein, lower carb floors.",
    "muscle_gain": "Lean bulk — calorie surplus, high protein, higher carbs especially on training days.",
    "strength_gain": "Performance fuel — small surplus, high protein, strong carb support on hard days.",
}

# target_deficit: positive = deficit (cut), negative = surplus (bulk)
MISSION_PRESETS = {
    "fat_loss": {"target_deficit": 500.0, "protein_target_g": 190.0},
    "weight_loss": {"target_deficit": 650.0, "protein_target_g": 175.0},
    "muscle_gain": {"target_deficit": -275.0, "protein_target_g": 210.0, "muscle_gain_fraction": 0.60},
    "strength_gain": {"target_deficit": -150.0, "protein_target_g": 200.0, "muscle_gain_fraction": 0.50},
}

STRENGTH_GAIN_TARGET_PCT = 5.0
MUSCLE_GAIN_TARGET_PCT = 8.0

GAIN_ROAD_MILESTONES = [
    (1.0, "Ignite"),
    (2.0, "Drive"),
    (3.0, "Power"),
    (4.0, "Peak"),
    (5.0, "Summit"),
]

WEIGHT_ROAD_CHECKPOINTS = [
    (0.50, "Halfway"),
    (0.75, "Home stretch"),
]

# Intermediate timeline markers only — Start, Today, and Goal are rendered separately.
JOURNEY_ROAD_FRACTIONS = [
    (0.50, "Halfway"),
    (0.75, "Home stretch"),
]

BF_JOURNEY_CHECKPOINTS = JOURNEY_ROAD_FRACTIONS

MISSION_ROAD_META = {
    "fat_loss": {"title": "Body fat journey", "goal_label": "Goal BF", "decreasing": True},
    "weight_loss": {"title": "Weight journey", "goal_label": "Goal weight", "decreasing": True},
    "muscle_gain": {"title": "Lean mass build", "goal_label": "Target lean", "decreasing": False},
    "strength_gain": {"title": "Strength gain", "goal_label": "+5% target", "decreasing": False},
}

MISSION_JOURNEY_THEME = {
    "fat_loss": {
        "accent": "#ff375f",
        "accent_soft": "#ffe8ed",
        "accent_dark": "#c4003a",
        "metric_name": "Body fat",
        "metric_short": "BF",
        "emoji": "🔥",
        "tagline": "DEXA + cumulative deficit",
        "hero_grad": "linear-gradient(125deg, #ff375f 0%, #ff6485 45%, #ffb3c6 100%)",
        "card_bg": "radial-gradient(ellipse 120% 80% at 100% 0%, rgba(255,55,95,.08) 0%, transparent 55%), #ffffff",
    },
    "weight_loss": {
        "accent": "#007aff",
        "accent_soft": "#e8f2ff",
        "accent_dark": "#005ecb",
        "metric_name": "Weight",
        "metric_short": "Wt",
        "emoji": "⚖️",
        "tagline": "Scale moving down",
        "hero_grad": "linear-gradient(125deg, #007aff 0%, #409cff 45%, #99caff 100%)",
        "card_bg": "radial-gradient(ellipse 120% 80% at 100% 0%, rgba(0,122,255,.08) 0%, transparent 55%), #ffffff",
    },
    "muscle_gain": {
        "accent": "#30d158",
        "accent_soft": "#e8fbea",
        "accent_dark": "#1e9e3f",
        "metric_name": "Lean mass",
        "metric_short": "Lean",
        "emoji": "💪",
        "tagline": "Build the engine",
        "hero_grad": "linear-gradient(125deg, #30d158 0%, #5ce07a 45%, #b8f5c8 100%)",
        "card_bg": "radial-gradient(ellipse 120% 80% at 100% 0%, rgba(48,209,88,.08) 0%, transparent 55%), #ffffff",
    },
    "strength_gain": {
        "accent": "#ff9f0a",
        "accent_soft": "#fff4e6",
        "accent_dark": "#cc7a00",
        "metric_name": "Strength",
        "metric_short": "Str",
        "emoji": "⚡",
        "tagline": "Power phase",
        "hero_grad": "linear-gradient(125deg, #ff9f0a 0%, #ffb340 45%, #ffd699 100%)",
        "card_bg": "radial-gradient(ellipse 120% 80% at 100% 0%, rgba(255,159,10,.08) 0%, transparent 55%), #ffffff",
    },
}

MISSION_CARB_MINIMUMS = {
    "fat_loss": dict(FUEL_CARB_MINIMUMS),
    "weight_loss": {
        "None": 180,
        "Long walk / high step day": 180,
        "Workout A": 220,
        "Workout B": 280,
        "Workout C": 220,
        "StairMaster only": 220,
    },
    "muscle_gain": {
        "None": 250,
        "Long walk / high step day": 250,
        "Workout A": 300,
        "Workout B": 400,
        "Workout C": 300,
        "StairMaster only": 280,
    },
    "strength_gain": {
        "None": 230,
        "Long walk / high step day": 230,
        "Workout A": 280,
        "Workout B": 370,
        "Workout C": 280,
        "StairMaster only": 260,
    },
}

WORKOUT_MET_BY_TYPE = {
    "push": 6.0,
    "pull": 6.0,
    "legs": 5.0,
    "shoulders": 4.0,
    "accessory": 4.0,
}
DEFAULT_RESISTANCE_MET = 5.0
STRONG_LEAN_GAIN_TARGET_SESSIONS_MONTH = 12.0
_STRONG_LEAN_CACHE = {"fingerprint": None, "sets": None, "monthly": {}}


def _strong_paths_fingerprint(paths):
    if not paths:
        return None
    parts = []
    for path in paths:
        try:
            stat = path.stat()
            parts.append(f"{path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}")
        except OSError:
            parts.append(str(path.resolve()))
    return "|".join(parts)

IMPORT_SOURCE_FIELDS = {
    "FatSecret": ["calories", "protein_g", "carbs_g", "fat_g"],
    "Oura": ["sleep_minutes", "sleep_score", "readiness_score", "oura_burn", "steps", "active_energy"],
    "Oura Export": ["sleep_minutes", "sleep_score", "readiness_score", "oura_burn", "steps", "active_energy"],
    "Apple Health Sleep": ["sleep_minutes", "steps", "active_energy", "distance_miles"],
    "Apple Health Weight": ["weight_lbs"],
    "Scale": ["weight_lbs"],
    "Workout": ["workout", "workout_intensity", "active_energy", "subjective_energy"],
    "Strong": ["workout", "workout_intensity", "active_energy"],
    "Rebalance": ["calories", "protein_g", "carbs_g", "fat_g", "steps", "workout", "workout_intensity", "active_energy", "subjective_energy", "weight_lbs", "sleep_score", "oura_burn"],
}

IMPORT_PROVENANCE_GROUPS = {
    "FatSecret": "nutrition",
    "Oura": "sleep_activity",
    "Oura Export": "sleep_activity",
    "Apple Health Sleep": "sleep_activity",
    "Apple Health Weight": "weight",
    "Scale": "weight",
    "Workout": "workout",
    "Strong": "workout",
    "Rebalance": "rebalance",
}

FUEL_FOOD_CALORIES = {
    "krispies": {"label": "Rice Krispies", "kcal_per_g": 3.8, "max_g": 120},
    "milk": {"label": "Milk", "kcal_per_g": 0.65, "max_g": 200},
    "yogurt": {"label": "Greek yogurt", "kcal_per_g": 0.97, "max_g": 400},
    "toast": {"label": "Toast", "kcal_each": 80},
    "butter": {"label": "Butter", "kcal_per_g": 7.2, "serving_g": 7},
    "peach": {"label": "Peach", "kcal_each": 50},
    "nectarine": {"label": "Nectarine", "kcal_each": 50},
    "cookie": {"label": "Cookie", "kcal_each": 150},
}

MILK_TO_KRISPIES_RATIO = 1.5
GAP_MAX_FRUIT_PIECES = 3

FREQUENT_SNACK_PRESETS = {
    "krispies_milk": {"label": "Rice Krispies + milk (1.5× milk)"},
    "toast_butter": {"label": "Toast + butter"},
    "peach": {"label": "Peach"},
    "nectarine": {"label": "Nectarine"},
    "cookie": {"label": "Cookie"},
}

# Default daily food plan (from FatSecret diary template — breakfast + lunch + snacks).
# Weights are raw / dry / uncooked unless noted (rice dry, chicken raw, veg fresh).
MEAL_TEMPLATE_WEIGHT_BASIS = "raw / dry / uncooked"
LUNCH_VEG_MACRO_PER_100G = {
    "calories": 31.0,
    "protein_g": 2.4,
    "carbs_g": 7.0,
    "fat_g": 0.2,
    "fiber_g": 2.6,
    "sodium_mg": 3.0,
}
DEFAULT_LUNCH_VEG_G = 225.0
LUNCH_VEG_G_MIN = 150.0
LUNCH_VEG_G_MAX = 300.0

DAILY_MEAL_TEMPLATE_PLAN_TEXT = (
    "Breakfast: Heritage Whole Wheat Sourdough 177g, Optimum Nutrition Casein 1 heaping scoop, "
    "Optimum Nutrition Whey 1 rounded scoop, Tea 750ml, Butter 21g, Sugar 1 tsp. "
    "Lunch: Jasmine Rice 115g dry uncooked, Skinless Chicken Breast 300g raw, "
    "Mixed vegetables 150-300g raw, Mizkan Rice Vinegar 1 tbsp, Argo Corn Starch 1 tbsp, "
    "Sesame Oil 1 tsp, Vegetable Oil 5g. "
    "Snacks: Pre-workout — Rice Krispies 140g dry + Whole Milk 200g. "
    "Post-workout — Chobani Greek Yogurt 400g, Sugar 1.5 tsp, Peach, Nectarine, cookies as needed."
)

# Base macros from FatSecret export (without lunch vegetables).
_MEAL_TEMPLATE_BASE_MACROS = {
    "calories": 2720.0,
    "protein_g": 189.98,
    "carbs_g": 320.18,
    "fat_g": 66.55,
    "fiber_g": 14.0,
    "sodium_mg": 2180.0,
}

DEFAULT_DAILY_MEAL_TEMPLATE = {
    "lunch_veg_g": DEFAULT_LUNCH_VEG_G,
    "base_macros": dict(_MEAL_TEMPLATE_BASE_MACROS),
    "meals": [
        {
            "name": "Breakfast",
            "calories": 694.0,
            "fat_g": 22.63,
            "carbs_g": 57.03,
            "protein_g": 60.60,
            "items": [
                "Heritage Whole Wheat Sourdough 177g (as served)",
                "Optimum Nutrition Casein (Cookie Dough) 1 heaping scoop",
                "Optimum Nutrition Whey (Double Rich Chocolate) 1 rounded scoop",
                "Tea (brewed) 750ml",
                "Butter 21g · Sugar 1 tsp",
            ],
        },
        {
            "name": "Lunch",
            "calories": 867.0,
            "fat_g": 13.90,
            "carbs_g": 97.53,
            "protein_g": 76.66,
            "items": [
                "Jasmine Rice 115g (dry, uncooked)",
                "Skinless Chicken Breast 300g (raw)",
                "Mixed vegetables 150–300g raw (default 225g)",
                "Mizkan Rice Vinegar 1 tbsp",
                "Argo Corn Starch 1 tbsp · Sesame Oil 1 tsp · Vegetable Oil 5g",
            ],
        },
        {
            "name": "Snacks / Other",
            "calories": 1159.0,
            "fat_g": 30.02,
            "carbs_g": 165.62,
            "protein_g": 52.72,
            "items": [
                "Pre-workout: Rice Krispies 140g (dry) + Whole Milk 200g",
                "Post-workout: Chobani Greek Yogurt 400g · Sugar 1.5 tsp · Peach · Nectarine · Cookies as needed",
            ],
        },
    ],
}

MEAL_TEMPLATE_MACRO_KEYS = ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sodium_mg")
MEAL_TEMPLATE_EXTRA_KEYS = ("lunch_veg_g",)


def lunch_veg_macros(grams):
    """Estimated macros for mixed lunch vegetables (raw / fresh weight)."""
    scale = max(0.0, float(grams or 0)) / 100.0
    per = LUNCH_VEG_MACRO_PER_100G
    return {key: per[key] * scale for key in per}


def resolve_meal_template_totals(template, lunch_veg_g=None):
    """Combine base plan macros with lunch vegetable grams."""
    veg_g = float(
        lunch_veg_g
        if lunch_veg_g is not None
        else template.get("lunch_veg_g")
        or DEFAULT_LUNCH_VEG_G
    )
    base = template.get("base_macros") or _MEAL_TEMPLATE_BASE_MACROS
    veg = lunch_veg_macros(veg_g)
    resolved = {"lunch_veg_g": veg_g}
    for key in MEAL_TEMPLATE_MACRO_KEYS:
        resolved[key] = float(base.get(key) or 0) + float(veg.get(key) or 0)
    return resolved


# Editable meal-plan items — amounts scale linearly from template defaults; veg uses raw weight macros.
MEAL_PLAN_ITEM_LAYOUT = [
    ("breakfast_sourdough", "Breakfast", "Heritage Whole Wheat Sourdough", "g", 177.0, 177.0, {}),
    ("breakfast_casein", "Breakfast", "Optimum Nutrition Casein", "scoop", 1.0, 35.0, {}),
    ("breakfast_whey", "Breakfast", "Optimum Nutrition Whey", "scoop", 1.0, 32.0, {}),
    ("breakfast_tea", "Breakfast", "Tea (brewed)", "ml", 750.0, 0.0, {"negligible": True}),
    ("breakfast_butter", "Breakfast", "Butter", "g", 21.0, 21.0, {}),
    ("breakfast_sugar", "Breakfast", "Sugar", "tsp", 1.0, 4.0, {}),
    ("lunch_rice", "Lunch", "Jasmine Rice (dry, uncooked)", "g", 115.0, 115.0, {}),
    ("lunch_chicken", "Lunch", "Skinless Chicken Breast (raw)", "g", 300.0, 300.0, {}),
    ("lunch_vegetables", "Lunch", "Mixed vegetables (raw)", "g", DEFAULT_LUNCH_VEG_G, DEFAULT_LUNCH_VEG_G, {"veg": True}),
    ("lunch_vinegar", "Lunch", "Mizkan Rice Vinegar", "tbsp", 1.0, 15.0, {}),
    ("lunch_corn_starch", "Lunch", "Argo Corn Starch", "tbsp", 1.0, 8.0, {}),
    ("lunch_sesame_oil", "Lunch", "Sesame Oil", "tsp", 1.0, 5.0, {}),
    ("lunch_veg_oil", "Lunch", "Vegetable Oil", "g", 5.0, 5.0, {}),
    ("snack_krispies", "Pre-workout", "Rice Krispies (dry)", "g", 140.0, 140.0, {}),
    ("snack_milk", "Pre-workout", "Whole Milk", "g", 200.0, 200.0, {}),
    ("snack_yogurt", "Post-workout", "Chobani Greek Yogurt Whole Milk Plain", "g", 400.0, 400.0, {}),
    ("snack_sugar", "Post-workout", "Sugar", "tsp", 1.5, 6.0, {}),
    ("snack_peach", "Post-workout", "Peach (medium, raw)", "count", 1.0, 150.0, {}),
    ("snack_nectarine", "Post-workout", "Nectarine (raw)", "g", 100.0, 100.0, {}),
    ("snack_cookie", "Post-workout", "Cookie", "count", 0.0, 0.0, {"optional": True}),
]

SNACK_MEAL_GROUPS = ("Pre-workout", "Post-workout")
SNACK_TEMPLATE_MEAL = "Snacks / Other"

# Swappable food presets — same slot/amount; nutrition scales from reference portion.
MEAL_FOOD_PRESET_OPTIONS = {
    "breakfast_sourdough": [
        {"id": "default", "label": "Standard — Heritage Whole Wheat Sourdough"},
        {
            "id": "oatmeal_dry",
            "label": "Oatmeal (dry, uncooked)",
            "reference_amount": 80.0,
            "macros": {"calories": 303.0, "protein_g": 11.0, "carbs_g": 54.0, "fat_g": 5.5, "fiber_g": 8.0, "sodium_mg": 5.0},
        },
        {
            "id": "ezekiel_bread",
            "label": "Ezekiel bread (as served)",
            "reference_amount": 160.0,
            "macros": {"calories": 320.0, "protein_g": 20.0, "carbs_g": 48.0, "fat_g": 4.0, "fiber_g": 12.0, "sodium_mg": 380.0},
        },
    ],
    "lunch_rice": [
        {"id": "default", "label": "Standard — Jasmine Rice (dry)"},
        {
            "id": "quinoa_dry",
            "label": "Quinoa (dry, uncooked)",
            "reference_amount": 115.0,
            "macros": {"calories": 420.0, "protein_g": 15.0, "carbs_g": 72.0, "fat_g": 7.0, "fiber_g": 8.0, "sodium_mg": 10.0},
        },
        {
            "id": "brown_rice_dry",
            "label": "Brown rice (dry, uncooked)",
            "reference_amount": 115.0,
            "macros": {"calories": 410.0, "protein_g": 9.5, "carbs_g": 86.0, "fat_g": 3.5, "fiber_g": 6.5, "sodium_mg": 8.0},
        },
    ],
    "lunch_chicken": [
        {"id": "default", "label": "Standard — Skinless Chicken Breast (raw)"},
        {
            "id": "turkey_breast",
            "label": "Turkey breast (raw)",
            "reference_amount": 300.0,
            "macros": {"calories": 330.0, "protein_g": 66.0, "carbs_g": 0.0, "fat_g": 4.0, "fiber_g": 0.0, "sodium_mg": 120.0},
        },
        {
            "id": "salmon_raw",
            "label": "Salmon fillet (raw)",
            "reference_amount": 300.0,
            "macros": {"calories": 620.0, "protein_g": 60.0, "carbs_g": 0.0, "fat_g": 38.0, "fiber_g": 0.0, "sodium_mg": 90.0},
        },
    ],
    "snack_krispies": [
        {"id": "default", "label": "Standard — Rice Krispies (dry)"},
        {
            "id": "banana",
            "label": "Banana (medium, raw)",
            "reference_amount": 1.0,
            "unit_label": "count",
            "macros": {"calories": 105.0, "protein_g": 1.3, "carbs_g": 27.0, "fat_g": 0.4, "fiber_g": 3.1, "sodium_mg": 1.0},
        },
        {
            "id": "oatmeal_pre",
            "label": "Oatmeal (dry, uncooked)",
            "reference_amount": 80.0,
            "macros": {"calories": 303.0, "protein_g": 11.0, "carbs_g": 54.0, "fat_g": 5.5, "fiber_g": 8.0, "sodium_mg": 5.0},
        },
    ],
    "snack_yogurt": [
        {"id": "default", "label": "Standard — Chobani Greek Yogurt Whole Milk Plain"},
        {
            "id": "cottage_cheese",
            "label": "Cottage cheese (low fat)",
            "reference_amount": 400.0,
            "macros": {"calories": 320.0, "protein_g": 52.0, "carbs_g": 16.0, "fat_g": 4.0, "fiber_g": 0.0, "sodium_mg": 920.0},
        },
        {
            "id": "skyr",
            "label": "Skyr (plain)",
            "reference_amount": 400.0,
            "macros": {"calories": 260.0, "protein_g": 48.0, "carbs_g": 16.0, "fat_g": 2.0, "fiber_g": 0.0, "sodium_mg": 180.0},
        },
    ],
}


def _meal_food_preset_catalog(item_id, default_label):
    options = list(MEAL_FOOD_PRESET_OPTIONS.get(item_id) or [])
    if not options:
        options = [{"id": "default", "label": f"Standard — {default_label}"}]
    elif not any(opt["id"] == "default" for opt in options):
        options.insert(0, {"id": "default", "label": f"Standard — {default_label}"})
    if not any(opt["id"] == "custom" for opt in options):
        options.append({"id": "custom", "label": "Custom food…"})
    return options


def _apply_food_override_to_spec(spec, override):
    if not override or override.get("preset_id", "default") == "default":
        return spec
    item_id = spec["id"]
    preset_id = override.get("preset_id")
    updated = dict(spec)
    if preset_id == "custom":
        custom_label = str(override.get("custom_label") or "").strip()
        if custom_label:
            updated["label"] = custom_label
        custom_macros = override.get("custom_macros")
        if isinstance(custom_macros, dict) and custom_macros.get("calories"):
            updated["macros_default"] = {key: float(custom_macros.get(key) or 0) for key in MEAL_TEMPLATE_MACRO_KEYS}
            updated["macro_reference_amount"] = float(
                override.get("macro_reference_amount") or spec.get("default") or 1.0
            )
        return updated
    preset = next(
        (opt for opt in _meal_food_preset_catalog(item_id, spec["label"]) if opt["id"] == preset_id),
        None,
    )
    if not preset:
        return spec
    updated["label"] = preset["label"]
    if preset.get("unit_label"):
        updated["unit_label"] = preset["unit_label"]
    if preset.get("macros"):
        updated["macros_default"] = {key: float(preset["macros"].get(key) or 0) for key in MEAL_TEMPLATE_MACRO_KEYS}
        updated["macro_reference_amount"] = float(preset.get("reference_amount") or spec.get("default") or 1.0)
    return updated


def _meal_food_overrides_from_notes(notes):
    notes = str(notes or "")
    match = re.search(r"meal_foods_json=([^\s|]+)", notes)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(1))
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, json.JSONDecodeError, ValueError):
        return {}


def _format_meal_food_overrides_for_notes(overrides):
    if not overrides:
        return ""
    cleaned = {
        item_id: entry
        for item_id, entry in overrides.items()
        if isinstance(entry, dict) and entry.get("preset_id") not in (None, "default")
    }
    if not cleaned:
        return ""
    return "meal_foods_json=" + json.dumps(cleaned, separators=(",", ":"))


def load_meal_food_overrides(daily, log_day, template=None):
    template = template or load_daily_meal_template()
    overrides = dict(template.get("food_overrides") or {})
    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            if not is_fatsecret_intake_row(row.to_dict()):
                continue
            day_overrides = _meal_food_overrides_from_notes(row.get("notes"))
            if day_overrides:
                overrides.update(day_overrides)
            break
    return overrides


def meal_food_session_key(key_prefix):
    return f"{key_prefix}_meal_food_overrides"


def read_meal_food_overrides(key_prefix, template=None, saved_overrides=None):
    session_key = meal_food_session_key(key_prefix)
    if session_key in st.session_state and isinstance(st.session_state[session_key], dict):
        return dict(st.session_state[session_key])
    return dict(saved_overrides or template.get("food_overrides") or {})


def collect_meal_food_overrides(key_prefix, specs, saved_overrides):
    overrides = {}
    for spec in specs:
        item_id = spec["id"]
        if spec["flags"].get("negligible"):
            continue
        preset_key = f"{key_prefix}_food_preset_{item_id}"
        if preset_key not in st.session_state:
            saved = (saved_overrides or {}).get(item_id)
            if saved and saved.get("preset_id") not in (None, "default"):
                overrides[item_id] = dict(saved)
            continue
        chosen = st.session_state.get(preset_key, "default")
        if chosen == "default":
            continue
        entry = {"preset_id": chosen}
        if chosen == "custom":
            entry["custom_label"] = str(st.session_state.get(f"{key_prefix}_food_custom_{item_id}") or "").strip()
            if st.session_state.get(f"{key_prefix}_food_custom_nut_{item_id}"):
                entry["macro_reference_amount"] = float(spec.get("default") or 1.0)
                entry["custom_macros"] = {
                    key: float(st.session_state.get(f"{key_prefix}_food_{key}_{item_id}") or 0)
                    for key in MEAL_TEMPLATE_MACRO_KEYS
                }
        overrides[item_id] = entry
    return overrides


def _build_meal_plan_item_specs(template=None, food_overrides=None):
    """Item catalog with per-item default macros that sum to the template day totals."""
    template = template or DEFAULT_DAILY_MEAL_TEMPLATE
    meals_by_name = {m.get("name"): m for m in template.get("meals") or []}
    day_totals = resolve_meal_template_totals(template)
    specs = []

    for item_id, meal_name, label, unit_label, default_amt, share_weight, flags in MEAL_PLAN_ITEM_LAYOUT:
        default_amt = float(default_amt or 0)
        share_weight = float(share_weight or 0)
        if meal_name in SNACK_MEAL_GROUPS:
            snack_block = meals_by_name.get(SNACK_TEMPLATE_MEAL) or {}
            group_weight = sum(
                float(row[5] or 0)
                for row in MEAL_PLAN_ITEM_LAYOUT
                if row[1] == meal_name and not row[6].get("negligible") and not row[6].get("optional")
            )
            total_snack_weight = sum(
                float(row[5] or 0)
                for row in MEAL_PLAN_ITEM_LAYOUT
                if row[1] in SNACK_MEAL_GROUPS and not row[6].get("negligible") and not row[6].get("optional")
            )
            group_share = group_weight / total_snack_weight if total_snack_weight > 0 else 0.5
            meal_block = {
                key: float(snack_block.get(key) or 0) * group_share
                for key in ("calories", "protein_g", "carbs_g", "fat_g")
            }
        else:
            meal_block = meals_by_name.get(meal_name) or {}
        veg_default = lunch_veg_macros(template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)

        if flags.get("veg"):
            macros_default = dict(veg_default)
        elif flags.get("optional"):
            macros_default = {key: 0.0 for key in MEAL_TEMPLATE_MACRO_KEYS}
        elif flags.get("negligible"):
            macros_default = {key: 0.0 for key in MEAL_TEMPLATE_MACRO_KEYS}
        else:
            meal_peers = [
                row for row in MEAL_PLAN_ITEM_LAYOUT
                if row[1] == meal_name
                and not row[6].get("veg")
                and not row[6].get("negligible")
                and not row[6].get("optional")
            ]
            veg_share = veg_default if meal_name == "Lunch" else {key: 0.0 for key in MEAL_TEMPLATE_MACRO_KEYS}
            meal_pool = {
                key: float(meal_block.get(key) or 0) - float(veg_share.get(key) or 0)
                for key in ("calories", "protein_g", "carbs_g", "fat_g")
            }
            peer_weight = sum(float(row[5] or 0) for row in meal_peers)
            share = share_weight / peer_weight if peer_weight > 0 else 0.0
            macros_default = {key: meal_pool.get(key, 0.0) * share for key in ("calories", "protein_g", "carbs_g", "fat_g")}
            macros_default["fiber_g"] = 0.0
            macros_default["sodium_mg"] = 0.0

        specs.append(
            {
                "id": item_id,
                "meal": meal_name,
                "label": label,
                "unit_label": unit_label,
                "default": default_amt,
                "flags": flags,
                "macros_default": macros_default,
            }
        )

    cal_total = sum(spec["macros_default"]["calories"] for spec in specs)
    for spec in specs:
        if spec["flags"].get("veg"):
            veg = spec["macros_default"]
            spec["macros_default"]["fiber_g"] = veg.get("fiber_g", 0.0)
            spec["macros_default"]["sodium_mg"] = veg.get("sodium_mg", 0.0)
        elif not spec["flags"].get("negligible") and not spec["flags"].get("optional"):
            cal_share = spec["macros_default"]["calories"] / cal_total if cal_total > 0 else 0.0
            spec["macros_default"]["fiber_g"] = float(day_totals.get("fiber_g") or 0) * cal_share
            spec["macros_default"]["sodium_mg"] = float(day_totals.get("sodium_mg") or 0) * cal_share

    if food_overrides:
        specs = [_apply_food_override_to_spec(spec, food_overrides.get(spec["id"])) for spec in specs]

    return specs


def zero_meal_item_amounts(template=None):
    template = template or load_daily_meal_template()
    return {spec["id"]: 0.0 for spec in _build_meal_plan_item_specs(template)}


def default_meal_item_amounts(template=None):
    template = template or load_daily_meal_template()
    amounts = {}
    for spec in _build_meal_plan_item_specs(template):
        if spec["id"] == "lunch_vegetables":
            amounts[spec["id"]] = float(template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
        else:
            amounts[spec["id"]] = float(spec["default"])
    return amounts


def _meal_items_from_notes(notes):
    notes = str(notes or "")
    match = re.search(r"meal_items=([^|]+)", notes)
    if not match:
        return None
    amounts = {}
    for part in match.group(1).split(","):
        if ":" not in part:
            continue
        item_id, raw_val = part.split(":", 1)
        item_id = item_id.strip()
        if not item_id:
            continue
        try:
            amounts[item_id] = float(raw_val.strip())
        except ValueError:
            continue
    return amounts or None


def _format_meal_items_for_notes(amounts):
    if not amounts:
        return ""
    parts = [f"{item_id}:{float(val):g}" for item_id, val in sorted(amounts.items())]
    return "meal_items=" + ",".join(parts)


def _meals_eaten_from_notes(notes):
    notes = str(notes or "")
    match = re.search(r"meals_eaten=([^|]*)", notes)
    if not match:
        return None
    return {part.strip() for part in match.group(1).split(",") if part.strip()}


def _format_meals_eaten_for_notes(meals_eaten):
    if meals_eaten is None:
        return ""
    if not meals_eaten:
        return "meals_eaten="
    return "meals_eaten=" + ",".join(sorted(meals_eaten))


def infer_meals_eaten_from_amounts(amounts, template=None):
    """Infer which meals have logged intake from per-item amounts."""
    template = template or load_daily_meal_template()
    specs = _build_meal_plan_item_specs(template)
    meals = {}
    for spec in specs:
        if spec["flags"].get("negligible"):
            continue
        meal_name = spec["meal"]
        amt = float(amounts.get(spec["id"]) or 0)
        meals.setdefault(meal_name, []).append(amt > 0)
    return {meal for meal, flags in meals.items() if any(flags)}


def load_meals_eaten_for_day(daily, log_day, template=None):
    template = template or load_daily_meal_template()
    explicit_eaten = None
    has_meal_plan = False
    logged_cal = 0.0
    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            rowd = row.to_dict()
            if is_meal_plan_intake_row(rowd):
                has_meal_plan = True
                explicit_eaten = _meals_eaten_from_notes(row.get("notes"))
                logged_cal = float(rowd.get("calories") or 0)
                break
            if is_fatsecret_intake_row(rowd):
                logged_cal = float(rowd.get("calories") or 0)
                explicit_eaten = _meals_eaten_from_notes(row.get("notes"))
                break
    if explicit_eaten is not None:
        return explicit_eaten
    # Template plan rows without explicit meals_eaten= are unlogged — don't infer from display amounts.
    if has_meal_plan:
        return set()
    if logged_cal > 0:
        amounts = load_meal_item_amounts(daily, log_day, template)
        return infer_meals_eaten_from_amounts(amounts, template)
    return set()


def _meals_eaten_session_key(key_prefix):
    return f"{key_prefix}_meals_eaten"


def _pending_meals_eaten_key(key_prefix):
    return f"{key_prefix}_pending_meals_eaten"


def _queue_meals_eaten_update(key_prefix, meal_name, eaten):
    pending = dict(st.session_state.get(_pending_meals_eaten_key(key_prefix)) or {})
    pending[meal_name] = bool(eaten)
    st.session_state[_pending_meals_eaten_key(key_prefix)] = pending


def _apply_pending_meals_eaten(key_prefix, saved_meals_eaten):
    pending = st.session_state.pop(_pending_meals_eaten_key(key_prefix), None)
    meals_eaten = set(saved_meals_eaten or set())
    if pending:
        for meal_name, eaten in pending.items():
            if eaten:
                meals_eaten.add(meal_name)
            else:
                meals_eaten.discard(meal_name)
    st.session_state[_meals_eaten_session_key(key_prefix)] = meals_eaten
    return meals_eaten


def _amounts_are_all_zero(amounts, template=None):
    template = template or load_daily_meal_template()
    for spec in _build_meal_plan_item_specs(template):
        if spec["flags"].get("negligible") or spec["flags"].get("optional"):
            continue
        if float(amounts.get(spec["id"]) or 0) > 0:
            return False
    return True


def load_meal_item_amounts(daily, log_day, template=None):
    template = template or load_daily_meal_template()
    defaults = default_meal_item_amounts(template)
    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            if not is_fatsecret_intake_row(row.to_dict()):
                continue
            saved = _meal_items_from_notes(row.get("notes"))
            if saved:
                if _amounts_are_all_zero(saved, template):
                    return defaults
                merged = dict(defaults)
                merged.update(saved)
                return merged
            break
    return defaults


def meal_item_session_key(key_prefix, item_id):
    return f"{key_prefix}_item_{item_id}"


def read_meal_item_amounts(key_prefix, template=None, saved_amounts=None):
    """Current item amounts from Streamlit session (falls back to saved day values)."""
    template = template or load_daily_meal_template()
    saved_amounts = dict(saved_amounts or default_meal_item_amounts(template))
    amounts = {}
    for spec in _build_meal_plan_item_specs(template):
        item_id = spec["id"]
        session_key = meal_item_session_key(key_prefix, item_id)
        if session_key in st.session_state:
            amounts[item_id] = float(st.session_state[session_key])
        else:
            amounts[item_id] = float(saved_amounts.get(item_id, spec["default"]))
    return amounts


def amounts_for_logged_meals(amounts, meals_eaten, template=None, food_overrides=None):
    """Only item amounts from meals marked eaten count toward intake."""
    template = template or load_daily_meal_template()
    meals_eaten = set(meals_eaten or [])
    specs = _build_meal_plan_item_specs(template, food_overrides)
    logged = {spec["id"]: 0.0 for spec in specs}
    for spec in specs:
        if spec["meal"] in meals_eaten:
            logged[spec["id"]] = max(0.0, float(amounts.get(spec["id"]) or 0))
    return logged


def compute_logged_meal_item_macros(amounts, meals_eaten, template=None, food_overrides=None):
    logged = amounts_for_logged_meals(amounts, meals_eaten, template, food_overrides)
    return compute_meal_item_macros(logged, template, food_overrides)


def compute_meal_item_macros(amounts, template=None, food_overrides=None):
    """Roll up per-item amounts into day macro totals."""
    template = template or load_daily_meal_template()
    totals = {key: 0.0 for key in MEAL_TEMPLATE_MACRO_KEYS}
    totals["lunch_veg_g"] = float(amounts.get("lunch_vegetables") or template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)

    for spec in _build_meal_plan_item_specs(template, food_overrides):
        item_id = spec["id"]
        amount = max(0.0, float(amounts.get(item_id) or 0))
        default_amt = float(spec["default"] or 0)
        reference_amt = float(spec.get("macro_reference_amount") or default_amt or 0)
        if spec["flags"].get("negligible"):
            continue
        if spec["flags"].get("optional") and default_amt <= 0 and amount <= 0:
            continue
        if spec["flags"].get("veg"):
            item_macros = lunch_veg_macros(amount)
        elif spec["id"] == "snack_cookie":
            count = amount
            cookie_kcal = float(FUEL_FOOD_CALORIES["cookie"]["kcal_each"])
            item_macros = {
                "calories": count * cookie_kcal,
                "protein_g": count * 2.0,
                "carbs_g": count * 18.0,
                "fat_g": count * 8.0,
                "fiber_g": 0.0,
                "sodium_mg": count * 90.0,
            }
        elif reference_amt <= 0:
            continue
        else:
            scale = amount / reference_amt
            item_macros = {key: float(spec["macros_default"].get(key) or 0) * scale for key in MEAL_TEMPLATE_MACRO_KEYS}
        for key in MEAL_TEMPLATE_MACRO_KEYS:
            totals[key] += float(item_macros.get(key) or 0)

    return totals


def planned_snacks_from_meal_items(amounts):
    """Snack inventory already counted in today's meal-plan item amounts."""
    amounts = amounts or {}
    return {
        "krispies_g": max(0.0, float(amounts.get("snack_krispies") or 0)),
        "milk_g": max(0.0, float(amounts.get("snack_milk") or 0)),
        "has_peach": float(amounts.get("snack_peach") or 0) >= 0.5,
        "has_nectarine": float(amounts.get("snack_nectarine") or 0) >= 25.0,
        "cookie_count": max(0, int(round(float(amounts.get("snack_cookie") or 0)))),
    }


def _meal_planner_day_track_key(key_prefix):
    return f"{key_prefix}_last_log_day"


def _reset_meal_planner_session_for_day(key_prefix, log_day):
    """Drop stale widget state when switching fuel-plan dates."""
    track_key = _meal_planner_day_track_key(key_prefix)
    if st.session_state.get(track_key) == log_day:
        return
    for key in list(st.session_state.keys()):
        if not key.startswith(f"{key_prefix}_"):
            continue
        if key == track_key:
            continue
        if key.startswith(f"{key_prefix}_item_") or key.startswith(f"{key_prefix}_food_"):
            st.session_state.pop(key, None)
        elif key in (
            f"{key_prefix}_post_snack_pick",
            _meal_food_edit_session_key(key_prefix),
            meal_food_session_key(key_prefix),
            f"{key_prefix}_save_default",
            f"{key_prefix}_planned_macros",
            f"{key_prefix}_eaten_macros",
        ):
            st.session_state.pop(key, None)
    st.session_state.pop(_meals_eaten_session_key(key_prefix), None)
    st.session_state.pop(_pending_meals_eaten_key(key_prefix), None)
    st.session_state.pop(_pending_meal_amounts_key(key_prefix), None)
    st.session_state.pop(_pending_save_day_key(key_prefix), None)
    st.session_state[track_key] = log_day


def _merge_session_eaten_macros_into_fs(fs_data, meal_key_prefix="ds_meal"):
    """Prefer sidebar meal-planner totals when they are ahead of the DB row."""
    eaten = st.session_state.get(f"{meal_key_prefix}_eaten_macros") or {}
    eaten_cal = float(eaten.get("calories") or 0)
    if eaten_cal <= 0:
        return fs_data
    if not fs_data:
        fs_data = {
            "calories": 0.0,
            "protein_g": None,
            "carbs_g": None,
            "fat_g": None,
            "fiber_g": None,
            "sodium_mg": None,
            "origin": "meal_plan",
            "parsed": {},
        }
    if eaten_cal <= float(fs_data.get("calories") or 0):
        return fs_data
    merged = dict(fs_data)
    merged["calories"] = eaten_cal
    for key in MEAL_TEMPLATE_MACRO_KEYS + ("lunch_veg_g",):
        if eaten.get(key) is not None:
            merged[key] = eaten[key]
    parsed = dict(merged.get("parsed") or {})
    parsed.update({key: merged.get(key) for key in MEAL_TEMPLATE_MACRO_KEYS + ("lunch_veg_g",)})
    merged["parsed"] = parsed
    merged["live_meal_items"] = True
    merged["origin"] = merged.get("origin") or "meal_plan"
    return merged


def resolve_saved_meal_intake(daily, log_day, template=None):
    """DB-only meal intake — used when meal-planner widgets are not active."""
    template = template or load_daily_meal_template()
    amounts = load_meal_item_amounts(daily, log_day, template)
    food_overrides = load_meal_food_overrides(daily, log_day, template)
    meals_eaten = load_meals_eaten_for_day(daily, log_day, template)
    macros = compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides)
    macros["meal_items"] = amounts
    macros["meal_food_overrides"] = food_overrides
    macros["meals_eaten"] = sorted(meals_eaten)
    return macros


def _meal_planner_session_active(key_prefix, log_day):
    if st.session_state.get(_meal_planner_day_track_key(key_prefix)) != log_day:
        return False
    return any(str(k).startswith(f"{key_prefix}_item_") for k in st.session_state)


def resolve_live_meal_intake(daily, log_day, key_prefix="ds_meal"):
    """Meal-item rollup for fuel math — uses unsaved widget values when present."""
    template = load_daily_meal_template()
    saved = load_meal_item_amounts(daily, log_day, template)
    saved_food = load_meal_food_overrides(daily, log_day, template)
    base_specs = _build_meal_plan_item_specs(template)
    food_overrides = collect_meal_food_overrides(key_prefix, base_specs, saved_food)
    if not food_overrides:
        food_overrides = read_meal_food_overrides(key_prefix, template, saved_food)
    if _meal_planner_session_active(key_prefix, log_day):
        amounts = read_meal_item_amounts(key_prefix, template, saved)
        meals_eaten = set(
            st.session_state.get(_meals_eaten_session_key(key_prefix))
            or load_meals_eaten_for_day(daily, log_day, template)
        )
    else:
        amounts = saved
        meals_eaten = load_meals_eaten_for_day(daily, log_day, template)
    macros = compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides)
    macros["meal_items"] = amounts
    macros["meal_food_overrides"] = food_overrides
    macros["meals_eaten"] = sorted(meals_eaten)
    return macros


def resolve_meal_plan_day_totals(daily, log_day, key_prefix="ds_meal"):
    """Full-day plan vs logged-so-far — drives projected intake in coaching."""
    template = load_daily_meal_template()
    live = resolve_live_meal_intake(daily, log_day, key_prefix) or resolve_saved_meal_intake(daily, log_day)
    amounts = dict(live.get("meal_items") or load_meal_item_amounts(daily, log_day, template))
    food_overrides = dict(live.get("meal_food_overrides") or load_meal_food_overrides(daily, log_day, template))
    meals_eaten = set(live.get("meals_eaten") or load_meals_eaten_for_day(daily, log_day, template))
    planned = compute_meal_item_macros(amounts, template, food_overrides)
    logged = compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides)
    remaining_kcal = max(0.0, float(planned.get("calories") or 0) - float(logged.get("calories") or 0))
    meals_order = []
    for spec in _build_meal_plan_item_specs(template, food_overrides):
        if spec["meal"] not in meals_order:
            meals_order.append(spec["meal"])
    return {
        "planned_macros": planned,
        "logged_macros": logged,
        "remaining_kcal": remaining_kcal,
        "unlogged_meals": [name for name in meals_order if name not in meals_eaten],
        "meals_eaten": meals_eaten,
    }


def apply_live_meal_intake(fs_data, daily, log_day, key_prefix="ds_meal"):
    """Overlay item-level consumption onto FatSecret intake for recommendations."""
    live = resolve_live_meal_intake(daily, log_day, key_prefix=key_prefix)
    if not live and not fs_data:
        return fs_data
    if not fs_data:
        fs_data = {
            "calories": 0.0,
            "protein_g": None,
            "carbs_g": None,
            "fat_g": None,
            "fiber_g": None,
            "sodium_mg": None,
            "origin": "meal_plan",
            "parsed": {},
        }
    if not live:
        saved_live = resolve_saved_meal_intake(daily, log_day)
        if float(saved_live.get("calories") or 0) > 0:
            live = saved_live
    if not live:
        return fs_data
    merged = dict(fs_data)
    for key in MEAL_TEMPLATE_MACRO_KEYS + ("lunch_veg_g",):
        if live.get(key) is not None:
            merged[key] = live[key]
    merged["calories"] = float(live["calories"])
    parsed = dict(merged.get("parsed") or {})
    parsed.update({key: live.get(key) for key in MEAL_TEMPLATE_MACRO_KEYS + ("lunch_veg_g",)})
    merged["parsed"] = parsed
    merged["live_meal_items"] = True
    return merged


def _apply_standard_meal_item_labels(template):
    """Keep reference item labels aligned with raw/dry weight convention."""
    default_meals = {m.get("name"): m for m in DEFAULT_DAILY_MEAL_TEMPLATE.get("meals") or []}
    meals = template.get("meals") or []
    for meal in meals:
        default = default_meals.get(meal.get("name"))
        if default and default.get("items"):
            meal["items"] = list(default["items"])
    template["meals"] = meals
    return template


def _patch_template_meals(template):
    """Ensure lunch vegetables appear in the reference breakdown."""
    meals = template.get("meals") or []
    for meal in meals:
        if meal.get("name") != "Lunch":
            continue
        items = list(meal.get("items") or [])
        if not any("vegetable" in str(item).lower() for item in items):
            insert_at = 2 if len(items) >= 2 else len(items)
            items.insert(insert_at, "Mixed vegetables 150–300g raw (default 225g)")
            meal["items"] = items
        veg_g = float(template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
        veg = lunch_veg_macros(veg_g)
        meal["calories"] = 867.0 + veg["calories"]
        meal["fat_g"] = 13.90 + veg["fat_g"]
        meal["carbs_g"] = 97.53 + veg["carbs_g"]
        meal["protein_g"] = 76.66 + veg["protein_g"]
        break
    template["meals"] = meals
    return _apply_standard_meal_item_labels(template)


DEFAULT_DAILY_MEAL_TEMPLATE.update(
    resolve_meal_template_totals(DEFAULT_DAILY_MEAL_TEMPLATE, DEFAULT_LUNCH_VEG_G)
)
_patch_template_meals(DEFAULT_DAILY_MEAL_TEMPLATE)

MEAL_PLAN_ITEM_SPECS = _build_meal_plan_item_specs()


def load_daily_meal_template():
    """User-editable default meal plan (persists in settings)."""
    template = json.loads(json.dumps(DEFAULT_DAILY_MEAL_TEMPLATE))
    raw = get_text_setting("daily_meal_template_json", "")
    if raw:
        try:
            saved = json.loads(raw)
            if isinstance(saved.get("base_macros"), dict):
                template["base_macros"] = saved["base_macros"]
            if saved.get("lunch_veg_g") is not None:
                template["lunch_veg_g"] = float(saved["lunch_veg_g"])
            elif any(key in saved for key in MEAL_TEMPLATE_MACRO_KEYS):
                veg_g = float(saved.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
                veg = lunch_veg_macros(veg_g)
                template["base_macros"] = {
                    key: float(saved.get(key) or template.get(key) or 0) - float(veg.get(key) or 0)
                    for key in MEAL_TEMPLATE_MACRO_KEYS
                }
            if isinstance(saved.get("meals"), list) and saved["meals"]:
                template["meals"] = saved["meals"]
            if isinstance(saved.get("food_overrides"), dict):
                template["food_overrides"] = saved["food_overrides"]
        except (TypeError, json.JSONDecodeError, ValueError):
            pass
    template.update(resolve_meal_template_totals(template))
    _patch_template_meals(template)
    return template


def save_daily_meal_template(parsed, food_overrides=None):
    existing = load_daily_meal_template()
    veg_g = float(parsed.get("lunch_veg_g") or existing.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
    veg = lunch_veg_macros(veg_g)
    base = dict(existing.get("base_macros") or _MEAL_TEMPLATE_BASE_MACROS)
    for key in MEAL_TEMPLATE_MACRO_KEYS:
        if parsed.get(key) is not None:
            base[key] = float(parsed[key]) - float(veg.get(key) or 0)
    payload = {
        "base_macros": base,
        "lunch_veg_g": veg_g,
        **resolve_meal_template_totals({"base_macros": base, "lunch_veg_g": veg_g}),
    }
    if food_overrides is not None:
        payload["food_overrides"] = {
            item_id: entry
            for item_id, entry in food_overrides.items()
            if isinstance(entry, dict) and entry.get("preset_id") not in (None, "default")
        }
    save_text_setting("daily_meal_template_json", json.dumps(payload))


def meal_template_notes(parsed):
    base = tag_import_notes("FatSecret", "Daily meal template")
    extras = []
    if parsed.get("fiber_g"):
        extras.append(f"fiber_g={float(parsed['fiber_g']):.1f}")
    if parsed.get("sodium_mg"):
        extras.append(f"sodium_mg={float(parsed['sodium_mg']):.0f}")
    if parsed.get("lunch_veg_g"):
        extras.append(f"lunch_veg_g={float(parsed['lunch_veg_g']):.0f}")
    chunks = [base, DAILY_MEAL_TEMPLATE_PLAN_TEXT]
    items_blob = _format_meal_items_for_notes(parsed.get("meal_items"))
    if items_blob:
        chunks.append(items_blob)
    foods_blob = _format_meal_food_overrides_for_notes(parsed.get("meal_food_overrides"))
    if foods_blob:
        chunks.append(foods_blob)
    if "meals_eaten" in parsed:
        eaten_blob = _format_meals_eaten_for_notes(parsed.get("meals_eaten"))
        if eaten_blob:
            chunks.append(eaten_blob)
    if extras:
        chunks.append(", ".join(extras))
    return " | ".join(chunks)


def save_daily_meal_intake(
    log_day,
    parsed,
    update_default_template=False,
    meal_items=None,
    meal_food_overrides=None,
    meals_eaten=None,
):
    """Write meal-plan macros to daily_log (replaces FatSecret manual entry)."""
    parsed = dict(parsed or {})
    if meal_items:
        parsed["meal_items"] = dict(meal_items)
    if meal_food_overrides is not None:
        parsed["meal_food_overrides"] = dict(meal_food_overrides)
    if meals_eaten is not None:
        parsed["meals_eaten"] = sorted(set(meals_eaten))
    cal = float(parsed.get("calories") or 0)
    if cal <= 0 and not parsed.get("meal_items"):
        return False
    log_day_str = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)
    notes_str = meal_template_notes(parsed)
    row = {
        "log_date": log_day_str,
        "calories": float(parsed["calories"]),
        "protein_g": _float_or_none(parsed.get("protein_g")),
        "carbs_g": _float_or_none(parsed.get("carbs_g")),
        "fat_g": _float_or_none(parsed.get("fat_g")),
        "notes": notes_str,
    }
    upsert_daily(row, source="FatSecret", force=True, data_ts=pd.Timestamp.now())
    # upsert_daily merges only macro fields for FatSecret source — notes are not in the merge list.
    # Write notes separately so meal_items / meals_eaten / food_overrides are never lost.
    _c = conn()
    _c.execute("UPDATE daily_log SET notes=? WHERE log_date=?", (notes_str, log_day_str))
    _c.commit()
    _c.close()
    if update_default_template:
        save_daily_meal_template(parsed, food_overrides=meal_food_overrides)
    return True


def auto_apply_meal_template_if_missing(daily, log_day):
    """Seed today+ with the daily meal template (plan amounts, nothing logged yet)."""
    if log_day < date.today():
        return False
    template = load_daily_meal_template()
    if get_fatsecret_day_data(daily, log_day) is None:
        # Guard: if a template row already exists (even with 0 cal), don't re-seed — breaks
        # the infinite rerun loop that occurs each morning before any food is logged.
        if not daily.empty:
            today_rows = daily[daily["log_date"].dt.date == log_day]
            for _, row in today_rows.iterrows():
                notes = str(row.get("notes") or "")
                if (
                    "daily meal template" in notes.lower()
                    or _meal_items_from_notes(notes) is not None
                ):
                    return False
        amounts = default_meal_item_amounts(template)
        parsed = compute_logged_meal_item_macros(amounts, set(), template)
        return save_daily_meal_intake(log_day, parsed, meal_items=amounts, meals_eaten=set())

    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            if not is_fatsecret_intake_row(row.to_dict()):
                continue
            saved = _meal_items_from_notes(row.get("notes"))
            if saved and _amounts_are_all_zero(saved, template):
                amounts = default_meal_item_amounts(template)
                # Always start a re-seeded day with an empty eaten set so no meal
                # appears pre-checked from a prior day's template save.
                parsed = compute_logged_meal_item_macros(amounts, set(), template)
                return save_daily_meal_intake(
                    log_day,
                    parsed,
                    meal_items=amounts,
                    meals_eaten=set(),
                )
            break
    return False


def _meal_intake_defaults(daily, log_day):
    template = load_daily_meal_template()
    amounts = load_meal_item_amounts(daily, log_day, template)
    food_overrides = load_meal_food_overrides(daily, log_day, template)
    meals_eaten = load_meals_eaten_for_day(daily, log_day, template)
    from_items = compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides)
    active = get_fatsecret_day_data(daily, log_day)
    if active and active.get("parsed"):
        parsed = dict(from_items)
        for key in MEAL_TEMPLATE_MACRO_KEYS:
            if active.get(key) is not None:
                parsed[key] = active[key]
        if not daily.empty:
            rows = daily[daily["log_date"].dt.date == log_day]
            for _, row in rows.iterrows():
                if is_fatsecret_intake_row(row.to_dict()):
                    parsed.update(_fatsecret_extras_from_notes(row.get("notes")))
                    break
        parsed["lunch_veg_g"] = float(amounts.get("lunch_vegetables") or template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
        return parsed, amounts
    out = {key: from_items.get(key, template.get(key)) for key in MEAL_TEMPLATE_MACRO_KEYS}
    out["lunch_veg_g"] = float(amounts.get("lunch_vegetables") or template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
    return out, amounts


def _meal_item_input_step(spec):
    unit = spec.get("unit_label") or ""
    if unit in ("g", "ml"):
        return 5.0 if spec["id"] == "lunch_vegetables" else 1.0
    if unit == "tsp":
        return 0.5
    if unit in ("scoop", "tbsp", "count"):
        return 1.0
    return 1.0


def _meal_item_input_max(spec):
    default_amt = float(spec.get("default") or 0)
    unit = spec.get("unit_label") or ""
    if spec["id"] == "lunch_vegetables":
        return LUNCH_VEG_G_MAX
    if unit in ("scoop", "tbsp", "tsp", "count"):
        return max(default_amt * 3.0, default_amt + 2.0, 6.0)
    return max(default_amt * 2.5, default_amt + 100.0, 500.0)


def _pending_meal_amounts_key(key_prefix):
    return f"{key_prefix}_pending_item_amounts"


def _queue_meal_item_amounts(key_prefix, amounts):
    """Stage item-amount updates — applied before widgets on the next rerun."""
    pending_key = _pending_meal_amounts_key(key_prefix)
    pending = dict(st.session_state.get(pending_key) or {})
    for item_id, val in amounts.items():
        pending[item_id] = float(val)
    st.session_state[pending_key] = pending


def _pending_save_day_key(key_prefix):
    return f"{key_prefix}_pending_save_day"


def _queue_meal_day_save(key_prefix):
    st.session_state[_pending_save_day_key(key_prefix)] = True


def _apply_pending_meal_planner_updates(key_prefix, base_specs, daily=None, log_day=None, template=None):
    """Apply staged meal-plan edits before any meal widgets are created."""
    if st.session_state.pop(f"{key_prefix}_pending_reset_food", False):
        st.session_state.pop(meal_food_session_key(key_prefix), None)
        st.session_state.pop(_meal_food_edit_session_key(key_prefix), None)
        st.session_state.pop(f"{key_prefix}_post_snack_pick", None)
        st.session_state[_meals_eaten_session_key(key_prefix)] = set()
        meal_names = {spec["meal"] for spec in base_specs}
        st.session_state[_pending_meals_eaten_key(key_prefix)] = {name: False for name in meal_names}
        for spec in base_specs:
            item_id = spec["id"]
            st.session_state.pop(f"{key_prefix}_food_preset_{item_id}", None)
            st.session_state.pop(f"{key_prefix}_food_custom_{item_id}", None)
            st.session_state.pop(f"{key_prefix}_food_custom_nut_{item_id}", None)
            for macro_key in MEAL_TEMPLATE_MACRO_KEYS:
                st.session_state.pop(f"{key_prefix}_food_{macro_key}_{item_id}", None)
        st.session_state.pop(f"{key_prefix}_save_default", None)

    pending = st.session_state.pop(_pending_meal_amounts_key(key_prefix), None)
    if pending:
        for item_id, val in pending.items():
            st.session_state[meal_item_session_key(key_prefix, item_id)] = float(val)

    saved_meals = (
        load_meals_eaten_for_day(daily, log_day, template)
        if daily is not None and log_day is not None and template is not None
        else set()
    )
    _apply_pending_meals_eaten(key_prefix, saved_meals)

    if not st.session_state.pop(_pending_save_day_key(key_prefix), False):
        return False
    if daily is None or log_day is None or template is None:
        return False

    db_amounts = load_meal_item_amounts(daily, log_day, template)
    amounts = read_meal_item_amounts(key_prefix, template, db_amounts)
    saved_food = load_meal_food_overrides(daily, log_day, template)
    food_overrides = collect_meal_food_overrides(key_prefix, base_specs, saved_food)
    if not food_overrides:
        food_overrides = read_meal_food_overrides(key_prefix, template, saved_food)
    meals_eaten = set(st.session_state.get(_meals_eaten_session_key(key_prefix)) or saved_meals)
    rolled = compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides)
    save_daily_meal_intake(
        log_day,
        rolled,
        meal_items=amounts,
        meal_food_overrides=food_overrides,
        meals_eaten=meals_eaten,
    )
    return True


def _planned_item_amount(spec, template):
    if spec["id"] == "lunch_vegetables":
        return float(template.get("lunch_veg_g") or DEFAULT_LUNCH_VEG_G)
    if spec["id"] == "snack_cookie":
        return 1.0
    return float(spec["default"])


def _meal_food_edit_session_key(key_prefix):
    return f"{key_prefix}_editing_food_item"


def _toggle_meal_food_edit(key_prefix, item_id):
    edit_key = _meal_food_edit_session_key(key_prefix)
    if st.session_state.get(edit_key) == item_id:
        st.session_state[edit_key] = None
    else:
        st.session_state[edit_key] = item_id


def _render_meal_food_picker(spec, item_id, key_prefix, item_override, preset_options, preset_ids, current_preset):
    chosen = st.selectbox(
        "Replace with",
        preset_ids,
        index=preset_ids.index(current_preset),
        format_func=lambda pid: next(opt["label"] for opt in preset_options if opt["id"] == pid),
        key=f"{key_prefix}_food_preset_{item_id}",
        label_visibility="collapsed",
    )
    if chosen == "custom":
        st.text_input(
            "Food name",
            value=str(item_override.get("custom_label") or ""),
            key=f"{key_prefix}_food_custom_{item_id}",
            placeholder="e.g. Steel-cut oatmeal",
        )
        custom_nut = st.checkbox(
            "Custom nutrition for planned portion",
            value=bool(item_override.get("custom_macros")),
            key=f"{key_prefix}_food_custom_nut_{item_id}",
        )
        if custom_nut:
            ref_macros = item_override.get("custom_macros") or spec.get("macros_default") or {}
            st.caption(
                f"Per planned portion ({spec.get('default', 0):g} {spec.get('unit_label', '')})"
            )
            st.number_input(
                "Calories (kcal)",
                min_value=0.0,
                value=float(ref_macros.get("calories") or 0),
                step=5.0,
                key=f"{key_prefix}_food_calories_{item_id}",
            )
            c1, c2 = st.columns(2)
            with c1:
                st.number_input(
                    "Protein (g)",
                    min_value=0.0,
                    value=float(ref_macros.get("protein_g") or 0),
                    step=0.5,
                    key=f"{key_prefix}_food_protein_g_{item_id}",
                )
                st.number_input(
                    "Net carbs (g)",
                    min_value=0.0,
                    value=float(ref_macros.get("carbs_g") or 0),
                    step=0.5,
                    key=f"{key_prefix}_food_carbs_g_{item_id}",
                )
            with c2:
                st.number_input(
                    "Fat (g)",
                    min_value=0.0,
                    value=float(ref_macros.get("fat_g") or 0),
                    step=0.5,
                    key=f"{key_prefix}_food_fat_g_{item_id}",
                )
                st.number_input(
                    "Fiber (g)",
                    min_value=0.0,
                    value=float(ref_macros.get("fiber_g") or 0),
                    step=0.5,
                    key=f"{key_prefix}_food_fiber_g_{item_id}",
                )
    elif chosen != "default":
        preset = next(opt for opt in preset_options if opt["id"] == chosen)
        if preset.get("macros"):
            st.caption(
                f"~{preset['macros'].get('calories', 0):.0f} kcal per "
                f"{preset.get('reference_amount', spec.get('default')):g} "
                f"{preset.get('unit_label') or spec.get('unit_label')}"
            )


def _render_meal_item_input(spec, saved_amounts, key_prefix, saved_food_overrides=None):
    item_id = spec["id"]
    default_val = float(saved_amounts.get(item_id, 0))
    step = _meal_item_input_step(spec)
    max_val = _meal_item_input_max(spec)
    unit = spec["unit_label"]
    label = spec["label"]
    if spec["flags"].get("negligible"):
        st.caption(f"· {label} — no meaningful calories")
        return

    saved_food_overrides = saved_food_overrides or {}
    item_override = saved_food_overrides.get(item_id) or {}
    preset_options = _meal_food_preset_catalog(item_id, label)
    preset_ids = [opt["id"] for opt in preset_options]
    current_preset = item_override.get("preset_id", "default")
    if current_preset not in preset_ids:
        current_preset = "default"

    is_editing = st.session_state.get(_meal_food_edit_session_key(key_prefix)) == item_id
    swapped = current_preset not in (None, "default")
    food_col, amt_col = st.columns([1.7, 1.0])
    with food_col:
        food_label = label
        if is_editing:
            food_label = f"▾ {label}"
        elif swapped:
            food_label = f"{label} ·"
        if st.button(
            food_label,
            key=f"{key_prefix}_food_pick_{item_id}",
            help="Click food name to change it",
            use_container_width=True,
            type="primary" if is_editing else "secondary",
        ):
            _toggle_meal_food_edit(key_prefix, item_id)
            st.rerun()
        if is_editing:
            _render_meal_food_picker(
                spec, item_id, key_prefix, item_override, preset_options, preset_ids, current_preset
            )
    with amt_col:
        amount_label = f"Amount ({unit})"
        if item_id == "lunch_vegetables":
            st.number_input(
                amount_label,
                min_value=0.0,
                max_value=float(LUNCH_VEG_G_MAX),
                value=min(max(default_val, 0.0), LUNCH_VEG_G_MAX),
                step=25.0,
                key=meal_item_session_key(key_prefix, item_id),
                help="Fresh/raw vegetable weight before cooking — plan 150–300g.",
                on_change=_on_meal_amount_changed,
                args=(key_prefix,),
            )
        elif unit in ("scoop", "tbsp", "tsp", "count"):
            st.number_input(
                amount_label,
                min_value=0.0,
                max_value=float(max_val),
                value=float(default_val),
                step=float(step),
                key=meal_item_session_key(key_prefix, item_id),
                on_change=_on_meal_amount_changed,
                args=(key_prefix,),
            )
        else:
            st.number_input(
                amount_label,
                min_value=0.0,
                max_value=float(max_val),
                value=float(default_val),
                step=float(step),
                key=meal_item_session_key(key_prefix, item_id),
                on_change=_on_meal_amount_changed,
                args=(key_prefix,),
            )


def _on_meal_amount_changed(key_prefix):
    _queue_meal_day_save(key_prefix)


def _mark_meal_items_eaten(key_prefix, specs, template, saved_amounts, item_ids, meal_name):
    current = read_meal_item_amounts(key_prefix, template, saved_amounts)
    spec_by_id = {spec["id"]: spec for spec in specs}
    updates = {}
    for item_id in item_ids:
        spec = spec_by_id.get(item_id)
        if spec and not spec["flags"].get("negligible"):
            amt = float(current.get(item_id) or 0)
            if amt <= 0:
                amt = _planned_item_amount(spec, template)
            updates[item_id] = amt
    _queue_meal_item_amounts(key_prefix, updates)
    _queue_meals_eaten_update(key_prefix, meal_name, True)
    _queue_meal_day_save(key_prefix)


def _clear_meal_items(key_prefix, specs, template, saved_amounts, meal_name):
    _queue_meals_eaten_update(key_prefix, meal_name, False)
    _queue_meal_day_save(key_prefix)


def render_daily_meal_planner(daily, log_day, key_prefix="ds_meal"):
    """Editable daily food plan — per-item amounts drive fuel math & snack suggestions."""
    template = load_daily_meal_template()
    saved_food = load_meal_food_overrides(daily, log_day, template)
    base_specs = _build_meal_plan_item_specs(template)
    if _apply_pending_meal_planner_updates(key_prefix, base_specs, daily, log_day, template):
        st.rerun()
    saved_amounts = read_meal_item_amounts(
        key_prefix, template, load_meal_item_amounts(daily, log_day, template)
    )
    saved_meals_eaten = load_meals_eaten_for_day(daily, log_day, template)
    _reset_meal_planner_session_for_day(key_prefix, log_day)

    if _meals_eaten_session_key(key_prefix) not in st.session_state:
        st.session_state[_meals_eaten_session_key(key_prefix)] = set(saved_meals_eaten)
    meals_eaten = set(st.session_state.get(_meals_eaten_session_key(key_prefix)) or saved_meals_eaten)
    has_saved = get_fatsecret_day_data(daily, log_day) is not None or day_has_meal_plan(daily, log_day)
    is_template_day = False
    if has_saved and not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            if "daily meal template" in str(row.get("notes") or "").lower():
                is_template_day = True
                break

    st.markdown("**Today's food plan**")
    st.caption(
        "Foods are preloaded from your daily template — **click a food name** to swap it. "
        "**Mark eaten** logs that meal for today (amounts stay visible; you can adjust or clear). "
        "Amount edits auto-save. "
        f"Weights are **{MEAL_TEMPLATE_WEIGHT_BASIS}**."
    )

    meals_order = []
    for spec in base_specs:
        if spec["meal"] not in meals_order:
            meals_order.append(spec["meal"])
    first_unlogged = next((name for name in meals_order if name not in meals_eaten), None)

    for meal_name in meals_order:
        meal_specs = [spec for spec in base_specs if spec["meal"] == meal_name]
        meal_item_ids = [spec["id"] for spec in meal_specs if not spec["flags"].get("negligible")]
        current_food = collect_meal_food_overrides(key_prefix, base_specs, saved_food)
        display_specs = _build_meal_plan_item_specs(template, current_food)
        display_by_id = {spec["id"]: spec for spec in display_specs}
        meal_logged = meal_name in meals_eaten
        expander_label = f"{meal_name} ✓" if meal_logged else meal_name
        expanded = not meal_logged and meal_name == first_unlogged
        # Key changes when state flips so Streamlit resets open/closed — guarantees collapse on mark-eaten
        _exp_key = f"mexp_{key_prefix}_{meal_name}_{'e' if meal_logged else 'p'}"
        with st.expander(expander_label, expanded=expanded, key=_exp_key):
            marker_class = "ds-meal-eaten-marker" if meal_logged else "ds-meal-pending-marker"
            st.markdown(f'<div class="{marker_class}"></div>', unsafe_allow_html=True)
            if meal_logged:
                st.caption("Logged for today — adjust amounts anytime, or **Clear** to remove.")
            if meal_name == "Pre-workout":
                st.caption("Rice Krispies + milk by default — swap to banana or oatmeal if you prefer.")
                if not meal_logged:
                    if st.button(
                        "Mark pre-workout eaten",
                        key=f"{key_prefix}_eat_{meal_name}",
                        use_container_width=True,
                    ):
                        _mark_meal_items_eaten(
                            key_prefix, meal_specs, template, saved_amounts, meal_item_ids, meal_name
                        )
                        st.rerun()
                else:
                    if st.button(
                        "Clear pre-workout",
                        key=f"{key_prefix}_clear_{meal_name}",
                        use_container_width=True,
                    ):
                        _clear_meal_items(key_prefix, meal_specs, template, saved_amounts, meal_name)
                        st.rerun()
            elif meal_name == "Post-workout":
                if not meal_logged:
                    st.caption("Yogurt, sugar, fruit, cookies — select what you've had, then mark eaten.")
                    selectable = [
                        spec for spec in meal_specs if not spec["flags"].get("negligible")
                    ]
                    spec_labels = {
                        spec["id"]: display_by_id.get(spec["id"], spec)["label"] for spec in selectable
                    }
                    pick_col, btn_col = st.columns([1.6, 1.0])
                    with pick_col:
                        selected = st.multiselect(
                            "Snacks to mark eaten",
                            options=[spec["id"] for spec in selectable],
                            format_func=lambda item_id: spec_labels.get(item_id, item_id),
                            key=f"{key_prefix}_post_snack_pick",
                            placeholder="Choose snacks…",
                        )
                    with btn_col:
                        st.write("")
                        if st.button(
                            "Mark selected eaten",
                            key=f"{key_prefix}_eat_post_selected",
                            use_container_width=True,
                            disabled=not selected,
                        ):
                            _mark_meal_items_eaten(
                                key_prefix, meal_specs, template, saved_amounts, selected, meal_name
                            )
                            st.rerun()
                else:
                    if st.button(
                        "Clear post-workout",
                        key=f"{key_prefix}_clear_{meal_name}",
                        use_container_width=True,
                    ):
                        _clear_meal_items(key_prefix, meal_specs, template, saved_amounts, meal_name)
                        st.rerun()
            else:
                if not meal_logged:
                    if st.button(
                        "Mark meal eaten",
                        key=f"{key_prefix}_eat_{meal_name}",
                        use_container_width=True,
                    ):
                        _mark_meal_items_eaten(
                            key_prefix, meal_specs, template, saved_amounts, meal_item_ids, meal_name
                        )
                        st.rerun()
                else:
                    if st.button(
                        "Clear meal",
                        key=f"{key_prefix}_clear_{meal_name}",
                        use_container_width=True,
                    ):
                        _clear_meal_items(key_prefix, meal_specs, template, saved_amounts, meal_name)
                        st.rerun()

            for spec in meal_specs:
                display_spec = display_by_id.get(spec["id"], spec)
                _render_meal_item_input(display_spec, saved_amounts, key_prefix, saved_food)

            meal_amounts = read_meal_item_amounts(key_prefix, template, saved_amounts)
            meal_macros = compute_meal_item_macros(
                {item_id: meal_amounts.get(item_id, 0.0) for item_id in meal_item_ids},
                template,
                current_food,
            )
            st.caption(
                f"Meal subtotal: **{meal_macros['calories']:.0f} kcal** · "
                f"**{meal_macros['carbs_g']:.1f}g** net C · "
                f"**{meal_macros['protein_g']:.1f}g** prot · "
                f"**{meal_macros['fat_g']:.1f}g** fat"
            )

    food_overrides = collect_meal_food_overrides(key_prefix, base_specs, saved_food)
    st.session_state[meal_food_session_key(key_prefix)] = food_overrides
    specs = _build_meal_plan_item_specs(template, food_overrides)

    amounts = read_meal_item_amounts(key_prefix, template, saved_amounts)
    # eaten_macros: only meals already marked eaten (solid ring arc)
    eaten_macros = compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides)
    # planned_macros: full day plan regardless of eaten status (ghost ring track)
    planned_macros = compute_meal_item_macros(amounts, template, food_overrides)
    # Expose to the dashboard so it can show ghost arcs + adjusted deficit
    st.session_state[f"{key_prefix}_planned_macros"] = planned_macros
    st.session_state[f"{key_prefix}_eaten_macros"]   = eaten_macros
    st.markdown(
        _meal_eaten_vs_planned_rings_html(eaten_macros, planned_macros),
        unsafe_allow_html=True,
    )
    st.caption(
        f"Fiber **{eaten_macros['fiber_g']:.1f} g** · Fat **{eaten_macros['fat_g']:.1f} g** · "
        f"Sodium **{eaten_macros['sodium_mg']:.0f} mg** · "
        f"Lunch veg **{eaten_macros.get('lunch_veg_g', 0):.0f} g raw**"
    )
    if has_saved:
        st.caption("Logged meals show **✓** — edits auto-save; use **Save intake** only to update your future-day template.")

    save_col, reset_col = st.columns(2)
    also_default = st.checkbox(
        "Also save as my default template for future days",
        value=False,
        key=f"{key_prefix}_save_default",
    )
    if save_col.button("Save intake", key=f"{key_prefix}_save_day", use_container_width=True, type="primary"):
        save_daily_meal_intake(
            log_day,
            compute_logged_meal_item_macros(amounts, meals_eaten, template, food_overrides),
            update_default_template=also_default,
            meal_items=amounts,
            meal_food_overrides=food_overrides,
            meals_eaten=meals_eaten,
        )
        st.success(f"Saved food plan for {log_day.isoformat()}.")
        st.rerun()
    if reset_col.button("Reset to template", key=f"{key_prefix}_reset", use_container_width=True):
        _queue_meal_item_amounts(key_prefix, default_meal_item_amounts(template))
        st.session_state[f"{key_prefix}_pending_reset_food"] = True
        _queue_meal_day_save(key_prefix)
        st.rerun()

    if has_saved:
        tag = "template applied" if is_template_day else "saved"
        st.caption(f"Active intake for {log_day.isoformat()} ({tag}) — fuel math uses these numbers.")
    else:
        st.caption("No intake saved yet for this date — save to persist; live preview still drives recommendations.")

def conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("PRAGMA busy_timeout=30000")
    return connection


def _init_db_schema():
    c = conn()
    cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
    for k, v in DEFAULTS.items():
        cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (k, v))

    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            log_date TEXT PRIMARY KEY,
            weight_lbs REAL, calories REAL, protein_g REAL, carbs_g REAL, fat_g REAL,
            steps REAL, active_energy REAL, resting_energy REAL, distance_miles REAL,
            sleep_minutes REAL, sleep_score REAL, readiness_score REAL, oura_burn REAL,
            workout TEXT, workout_intensity REAL, subjective_energy REAL, notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_day_close (
            log_date TEXT PRIMARY KEY,
            weight_lbs REAL,
            calories REAL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            steps REAL,
            workout TEXT,
            total_burn REAL,
            projected_deficit REAL,
            target_deficit REAL,
            finalized INTEGER DEFAULT 1,
            finalized_at TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dexa_scans (
            scan_date TEXT PRIMARY KEY,
            weight_lbs REAL, body_fat_pct REAL, fat_mass_lbs REAL,
            lean_mass_lbs REAL, vat_mass_g REAL, vat_volume_cm3 REAL,
            vat_area_cm2 REAL, source_file TEXT, notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS screenshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_date TEXT,
            log_date TEXT,
            source TEXT,
            file_path TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS import_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            import_date TEXT,
            import_type TEXT,
            source_name TEXT,
            file_count INTEGER,
            row_count INTEGER,
            status TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_registry (
            file_hash TEXT PRIMARY KEY,
            first_seen TEXT,
            source_path TEXT,
            stored_path TEXT,
            detected_type TEXT,
            status TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocr_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            file_hash TEXT,
            stored_path TEXT,
            detected_type TEXT,
            ocr_text TEXT,
            parsed_json TEXT,
            status TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workout_calibration (
            workout TEXT PRIMARY KEY,
            expected_burn REAL,
            observed_count INTEGER,
            last_updated TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS weekly_calibration (
            week_start TEXT PRIMARY KEY,
            predicted_weight_change REAL,
            actual_weight_change REAL,
            maintenance_adjustment REAL,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS composition_calibration (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            fat_loss_fraction REAL,
            muscle_gain_fraction REAL,
            kcal_per_lb_fat REAL,
            protein_retention_factor REAL,
            training_retention_factor REAL,
            interval_count INTEGER,
            last_scan_date TEXT,
            last_updated TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dexa_calibration_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TEXT NOT NULL,
            prior_scan_date TEXT,
            interval_days INTEGER,
            actual_weight_lbs REAL,
            actual_fat_lbs REAL,
            actual_lean_lbs REAL,
            actual_bf_pct REAL,
            predicted_weight_lbs REAL,
            predicted_fat_lbs REAL,
            predicted_lean_lbs REAL,
            predicted_bf_pct REAL,
            weight_error_lbs REAL,
            fat_error_lbs REAL,
            lean_error_lbs REAL,
            bf_error_pct REAL,
            observed_fat_fraction REAL,
            observed_lean_fraction REAL,
            cumulative_deficit_kcal REAL,
            resistance_days INTEGER,
            protein_adherence_pct REAL,
            kcal_per_lb_fat_observed REAL,
            created_at TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocr_field_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_type TEXT NOT NULL,
            field_key TEXT NOT NULL,
            raw_snippet TEXT,
            ocr_extracted TEXT,
            corrected_value TEXT NOT NULL,
            label_context TEXT,
            use_count INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ocr_field_corr_lookup
        ON ocr_field_corrections (document_type, field_key)
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocr_type_trust (
            document_type TEXT PRIMARY KEY,
            auto_confirm_enabled INTEGER DEFAULT 0,
            clean_confirmations INTEGER DEFAULT 0,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS weight_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measured_at TEXT NOT NULL,
            log_date TEXT NOT NULL,
            weight_lbs REAL NOT NULL,
            source TEXT,
            file_hash TEXT,
            notes TEXT,
            created_at TEXT,
            UNIQUE(measured_at, weight_lbs)
        )
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_weight_measurements_log_date ON weight_measurements (log_date)"
    )

    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_import_provenance (
            log_date TEXT NOT NULL,
            prov_group TEXT NOT NULL,
            data_ts TEXT NOT NULL,
            source TEXT,
            imported_at TEXT NOT NULL,
            file_hash TEXT,
            PRIMARY KEY (log_date, prov_group)
        )
    """)

    dedupe_ocr_queue_rows(cur)
    sync_pending_ocr_with_registry(cur)
    try:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ocr_queue_file_hash ON ocr_queue (file_hash)")
    except (sqlite3.OperationalError, sqlite3.IntegrityError):
        dedupe_ocr_queue_rows(cur)
        try:
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ocr_queue_file_hash ON ocr_queue (file_hash)")
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS text_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cur.execute(
        "INSERT OR IGNORE INTO text_settings VALUES (?, ?)",
        ("inbox_folder_path", str(INBOX_DIR)),
    )
    cur.execute(
        "INSERT OR IGNORE INTO text_settings VALUES (?, ?)",
        ("health_data_source_folder_path", str(detect_default_health_data_source_folder())),
    )
    for key, default in [
        ("current_weight_manual_override", ""),
        ("current_weight_source", ""),
        ("current_weight_import_priority", ""),
        ("current_weight_import_ts", ""),
        ("current_body_fat_manual_override", ""),
        ("current_body_fat_manual_value", ""),
        ("current_body_fat_source", ""),
        ("current_body_fat_import_ts", ""),
        ("fuel_planner_date", ""),
        ("fuel_workout_by_date", "{}"),
        ("fuel_workout_confirmed_date", ""),
        ("mission_mode", "fat_loss"),
        ("goal_weight_lbs", "165"),
        ("morning_weight_prompt_done", ""),
    ]:
        cur.execute("INSERT OR IGNORE INTO text_settings VALUES (?, ?)", (key, default))

    for col, typedef in [("file_name", "TEXT"), ("file_size", "INTEGER"), ("file_mtime", "REAL")]:
        try:
            cur.execute(f"ALTER TABLE file_registry ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass

    for col, typedef in [
        ("burn_source", "TEXT"),
        ("met_used", "REAL"),
        ("duration_min", "REAL"),
    ]:
        try:
            cur.execute(f"ALTER TABLE workout_calibration ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass

    c.commit()
    c.close()
    seed_import_provenance_once()


def init_db():
    last_error = None
    for attempt in range(6):
        try:
            _init_db_schema()
            return
        except sqlite3.OperationalError as exc:
            last_error = exc
            if "locked" not in str(exc).lower():
                raise
            time.sleep(0.2 * (attempt + 1))
    if last_error:
        raise last_error


def text_settings():
    c = conn()
    try:
        df = pd.read_sql("SELECT * FROM text_settings", c)
        result = dict(zip(df.key, df.value))
    except Exception:
        result = {}
    c.close()
    return result


def get_text_setting(key, default=""):
    ts = text_settings()
    return ts.get(key, default) if ts.get(key) else default


def save_text_setting(key, value):
    c = conn()
    c.execute("INSERT OR REPLACE INTO text_settings VALUES (?, ?)", (key, str(value)))
    c.commit()
    c.close()


def get_inbox_folder():
    configured = get_text_setting("inbox_folder_path", str(INBOX_DIR))
    return Path(configured).expanduser()


def get_health_data_source_folder():
    """Prefer the saved path; if Drive is offline or moved, rediscover the Health Data folder."""
    configured = get_text_setting("health_data_source_folder_path", "")
    if configured:
        path = Path(configured).expanduser()
        if _folder_is_ready(path):
            return path
    detected = detect_default_health_data_source_folder()
    if _folder_is_ready(detected):
        save_text_setting("health_data_source_folder_path", str(detected))
        return Path(detected)
    if configured:
        return Path(configured).expanduser()
    return Path(detected)


MANUAL_ONLY_SETTINGS = {
    "baseline_maintenance",
    "target_deficit",
    "goal_body_fat_pct",
    "protein_target_g",
    "step_calories_per_1000",
    "min_trend_days",
    "fat_loss_fraction",
    "annual_lean_gain_lbs",
    "default_step_goal",
    "default_workout_burn",
    "snack_calorie_unit",
    "adaptive_maintenance_adjustment",
}

IMPORT_OVERRIDABLE_SETTINGS = {
    "current_weight_lbs",
    "current_body_fat_pct",
}


def load_persisted_settings():
    """Load numeric sidebar settings from SQLite; fill defaults for missing keys."""
    s = settings()
    for key, default in DEFAULTS.items():
        if key not in s or s[key] is None:
            s[key] = float(default)
        else:
            s[key] = float(s[key])
    return s


def get_mission_mode():
    mode = get_text_setting("mission_mode", "fat_loss")
    return mode if mode in MISSION_MODE_KEYS else "fat_loss"


def get_mission_carb_minimums(mode=None):
    mode = mode or get_mission_mode()
    return MISSION_CARB_MINIMUMS.get(mode, MISSION_CARB_MINIMUMS["fat_loss"])


def mission_calorie_balance_label(mode=None):
    mode = mode or get_mission_mode()
    deficit = float(MISSION_PRESETS.get(mode, MISSION_PRESETS["fat_loss"])["target_deficit"])
    if deficit > 0:
        return f"{deficit:.0f} kcal deficit"
    if deficit < 0:
        return f"{abs(deficit):.0f} kcal surplus"
    return "Maintenance"


def mission_energy_pill_label(mode=None):
    mode = mode or get_mission_mode()
    if mode in ("muscle_gain", "strength_gain"):
        return "Surplus"
    if mode == "weight_loss":
        return "Deficit"
    return "Deficit"


def goal_weight_lbs(settings, fc=None):
    """Scale weight at the goal body-fat % with DEXA lean mass held constant."""
    if fc and fc.get("target_weight"):
        try:
            tw = float(fc["target_weight"])
            if tw > 0:
                return tw
        except (TypeError, ValueError):
            pass
    lean = float((fc or {}).get("current_lean_mass") or 0)
    goal_bf = float((settings or {}).get("goal_body_fat_pct") or 10.0)
    derived = goal_weight_from_lean(lean, goal_bf) if lean > 0 else 0.0
    if derived > 0:
        return derived
    raw = get_text_setting("goal_weight_lbs", "")
    try:
        if raw:
            return float(raw)
    except ValueError:
        pass
    return float(GOAL_WEIGHT_AT_10PCT_BF)


def apply_mission_preset(mode, fc=None, settings=None, daily=None, dexa=None):
    """Apply mission defaults to persisted settings and reset journey start."""
    if mode not in MISSION_MODE_KEYS:
        return False
    preset = MISSION_PRESETS[mode]
    settings = settings or load_persisted_settings()
    save_text_setting("mission_mode", mode)
    save_setting("target_deficit", float(preset["target_deficit"]))
    save_setting("protein_target_g", float(preset["protein_target_g"]))
    if preset.get("muscle_gain_fraction") is not None:
        save_setting("muscle_gain_fraction", float(preset["muscle_gain_fraction"]))
    if mode == "weight_loss":
        gw = goal_weight_lbs(settings, fc)
        save_text_setting("goal_weight_lbs", str(gw))
    reseed_journey_start(mode, fc or {}, settings, daily, dexa)
    return True


def render_composition_calibration_panel(dexa, fc=None):
    """Show DEXA-learned composition coefficients and calibration history."""
    cal = load_composition_calibration()
    events = load_dexa_calibration_events()

    st.markdown("**Composition model (DEXA-calibrated)**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fat-loss fraction", f"{float(cal.get('fat_loss_fraction') or 0) * 100:.0f}%")
    c2.metric("Lean-gain fraction", f"{float(cal.get('muscle_gain_fraction') or 0) * 100:.0f}%")
    c3.metric("kcal / lb fat", f"{float(cal.get('kcal_per_lb_fat') or 3500):.0f}")
    c4.metric("Calibration intervals", int(cal.get("interval_count") or 0))

    if fc:
        method = fc.get("composition_method") or fc.get("estimation_method") or "model"
        anchor = fc.get("composition_anchor") or "—"
        cap = (
            f"Live estimate: **{float(fc.get('current_bf') or 0):.1f}% BF** · "
            f"method **{method}** · anchor **{anchor}**"
        )
        if fc.get("strong_lean_available"):
            cap += " · Strong sessions scale lean projection"
        st.caption(cap)

    if events.empty:
        st.info(
            "Upload a second quarterly DEXA to compare prediction vs reality and personalize the estimator."
        )
    else:
        view = events.copy()
        for col in ["scan_date", "prior_scan_date"]:
            if col in view.columns:
                view[col] = view[col].astype(str).str[:10]
        display_cols = [
            c
            for c in [
                "scan_date",
                "prior_scan_date",
                "interval_days",
                "actual_bf_pct",
                "predicted_bf_pct",
                "bf_error_pct",
                "observed_fat_fraction",
                "cumulative_deficit_kcal",
                "resistance_days",
            ]
            if c in view.columns
        ]
        with st.expander("Calibration history", expanded=False):
            st.dataframe(view[display_cols], use_container_width=True)
            last = events.iloc[-1]
            st.caption(
                f"Last interval: predicted **{float(last.get('predicted_bf_pct') or 0):.1f}%** vs "
                f"DEXA **{float(last.get('actual_bf_pct') or 0):.1f}%** "
                f"({float(last.get('bf_error_pct') or 0):+.1f} pts)."
            )


def render_muscle_gain_insights(daily, dexa, s, compact=False):
    """Show lean-mass estimate from weight, food, and workouts."""
    analysis = compute_muscle_gain_analysis(daily, dexa, s)
    if not analysis:
        return
    if compact:
        prot = analysis.get("protein_adherence_pct")
        st.caption(
            f"Lean **{analysis['current_lean_lbs']:.1f} lb** · "
            f"**{analysis['lean_gain_lbs_week']:+.2f} lb/wk** est. · "
            f"protein **{prot:.0f}%** days" if prot is not None else
            f"Lean **{analysis['current_lean_lbs']:.1f} lb** · "
            f"**{analysis['lean_gain_lbs_week']:+.2f} lb/wk** est."
        )
        st.caption(analysis["summary"])
        return
    st.markdown("**Lean mass intelligence**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lean mass (est.)", f"{analysis['current_lean_lbs']:.1f} lb")
    c2.metric(
        f"Lean Δ ({analysis['lookback_days']}d)",
        f"{analysis['lean_gain_period_lbs']:+.2f} lb",
    )
    c3.metric("Lean rate", f"{analysis['lean_gain_lbs_week']:+.2f} lb/wk")
    prot = analysis.get("protein_adherence_pct")
    c4.metric("Protein days hit", f"{prot:.0f}%" if prot is not None else "—")
    st.caption(analysis["summary"])
    with st.expander("How this is calculated", expanded=False):
        st.markdown(
            f"- **Weight trend** from scale logs (R²={analysis.get('trend_r2') or 0:.2f})\n"
            f"- **Training days** in window: {analysis['training_days']}\n"
            f"- **Surplus adherence**: {analysis.get('surplus_adherence_pct') or '—'}%\n"
            f"- **Lean share of gain**: {analysis['effective_lean_fraction']*100:.0f}% "
            f"(adjusted for protein, surplus, and workouts)\n"
            f"- DEXA anchor: {analysis['anchor_label']}"
        )


def command_center_unified_css():
    return """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", system-ui, sans-serif;
    background: #e8e8ed;
    color: #1c1c1e;
    font-size: 12px;
    height: 100%;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
  }
  .cc-unified {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #f2f2f7;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,.10), 0 1px 0 rgba(255,255,255,.6) inset;
  }
  .cc-hero {
    flex-shrink: 0;
    padding: 12px 14px 14px;
    color: #fff;
    position: relative;
    overflow: hidden;
  }
  .cc-hero::after {
    content: "";
    position: absolute;
    right: -20px; top: -30px;
    width: 140px; height: 140px;
    border-radius: 50%;
    background: rgba(255,255,255,.12);
    pointer-events: none;
  }
  .cc-hero-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
    position: relative;
    z-index: 1;
  }
  .cc-hero-emoji { font-size: 22px; line-height: 1; margin-bottom: 2px; }
  .cc-hero-title {
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -.02em;
    line-height: 1.1;
  }
  .cc-hero-tagline {
    font-size: 11px;
    font-weight: 600;
    opacity: .88;
    margin-top: 2px;
  }
  .cc-hero-motivation {
    font-size: 10px;
    font-weight: 650;
    opacity: .78;
    margin-top: 6px;
    font-style: italic;
  }
  .cc-hero-pills {
    display: flex;
    gap: 5px;
    margin-top: 10px;
    position: relative;
    z-index: 1;
  }
  .cc-hero-pill {
    flex: 1;
    min-width: 0;
    background: rgba(255,255,255,.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,.28);
    border-radius: 10px;
    padding: 5px 3px;
    text-align: center;
  }
  .cc-hero-pill-featured {
    background: rgba(255,255,255,.95);
    border-color: rgba(255,255,255,.95);
    box-shadow: 0 4px 14px rgba(0,0,0,.12);
  }
  .cc-hero-pill-featured .cc-pill-label { color: #8e8e93 !important; }
  .cc-hero-pill-featured .cc-pill-value { color: var(--cc-accent-dark, #1c1c1e) !important; font-size: 17px; }
  .cc-hero-pill-featured .cc-pill-sub { color: #636366 !important; }
  .cc-hero-pill:not(.cc-hero-pill-featured) .cc-pill-label { color: rgba(255,255,255,.75); }
  .cc-hero-pill:not(.cc-hero-pill-featured) .cc-pill-value { color: #fff; }
  .cc-hero-pill:not(.cc-hero-pill-featured) .cc-pill-sub { color: rgba(255,255,255,.7); }
  .cc-hero-pill .cc-pill-label {
    display: block;
    font-size: 8px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
  }
  .cc-hero-pill .cc-pill-value {
    display: block;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: -.02em;
    line-height: 1.05;
  }
  .cc-hero-pill .cc-pill-sub {
    display: block;
    font-size: 8px;
    margin-top: 1px;
  }
  .cc-trend-pill {
    font-size: 10px;
    font-weight: 800;
    padding: 5px 10px;
    border-radius: 999px;
    white-space: nowrap;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
  }
  .cc-trend-good { color: #fff; background: rgba(36,138,61,.92); }
  .cc-trend-warn { color: #fff; background: rgba(201,52,0,.92); }
  .cc-trend-neutral { color: #fff; background: rgba(255,255,255,.22); border: 1px solid rgba(255,255,255,.35); }
  .cc-journey-wrap {
    flex: 1;
    min-height: 0;
    padding: 8px 10px 10px;
    display: flex;
    flex-direction: column;
  }
  .cc-journey {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,.06);
    padding: 10px 12px 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,.05);
    overflow: hidden;
  }
  .cc-journey-mid {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 10px;
    align-items: center;
    flex-shrink: 0;
  }
  .cc-rings {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .cc-ring-wrap {
    position: relative;
    width: 58px;
    height: 58px;
  }
  .cc-ring-wrap svg { width: 100%; height: 100%; display: block; }
  .cc-ring-center {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }
  .cc-ring-pct {
    font-size: 13px;
    font-weight: 900;
    letter-spacing: -.03em;
    color: #1c1c1e;
  }
  .cc-ring-lbl {
    font-size: 7px;
    font-weight: 700;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-top: 1px;
  }
  .cc-countdown {
    text-align: center;
    padding: 0 4px;
  }
  .cc-countdown-num {
    font-size: 36px;
    font-weight: 900;
    letter-spacing: -.04em;
    line-height: .95;
    background: linear-gradient(180deg, #1c1c1e 0%, #48484a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .cc-countdown-lbl {
    font-size: 10px;
    font-weight: 700;
    color: #636366;
    margin-top: 2px;
  }
  .cc-countdown-sub {
    font-size: 9px;
    color: #8e8e93;
    margin-top: 1px;
  }
  .cc-journey-meta {
    text-align: right;
    min-width: 72px;
  }
  .cc-journey-meta-lbl {
    font-size: 8px;
    font-weight: 700;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: .05em;
  }
  .cc-journey-meta-val {
    font-size: 12px;
    font-weight: 800;
    color: #1c1c1e;
    margin-top: 2px;
  }
  .cc-journey-since {
    font-size: 9px;
    color: #8e8e93;
    margin-top: 4px;
  }
  .cc-metric-strip {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10px;
    font-weight: 650;
    color: #636366;
    padding: 4px 8px;
    background: rgba(0,0,0,.03);
    border-radius: 8px;
    flex-shrink: 0;
  }
  .cc-metric-strip strong { color: #1c1c1e; font-weight: 800; }
  .cc-timeline {
    position: relative;
    flex: 1;
    min-height: 68px;
    margin-top: 2px;
  }
  .cc-timeline-rail {
    position: absolute;
    left: 4%;
    right: 4%;
    top: 20px;
    height: 5px;
    background: #e5e5ea;
    border-radius: 999px;
  }
  .cc-timeline-fill {
    position: absolute;
    left: 4%;
    top: 20px;
    height: 5px;
    border-radius: 999px;
    max-width: 92%;
    box-shadow: 0 0 10px var(--cc-accent-soft, rgba(0,122,255,.4));
  }
  .cc-tm {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    text-align: center;
    min-width: 48px;
  }
  .cc-tm-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #fff;
    border: 2px solid #c7c7cc;
    margin: 15px auto 5px;
  }
  .cc-tm-val {
    font-size: 10px;
    font-weight: 800;
    color: #1c1c1e;
    line-height: 1.1;
  }
  .cc-tm-lbl {
    font-size: 7px;
    font-weight: 700;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-top: 1px;
  }
  .cc-tm-start .cc-tm-dot { border-color: #aeaeb2; background: #f2f2f7; }
  .cc-tm-goal .cc-tm-dot { border-width: 2.5px; background: #fff; }
  .cc-tm-today .cc-tm-dot {
    width: 14px;
    height: 14px;
    margin-top: 13px;
    border-width: 3px;
    background: #fff;
    animation: ccPulse 2s ease-in-out infinite;
  }
  @keyframes ccPulse {
    0%, 100% { box-shadow: 0 0 0 3px var(--cc-accent-soft, #e8f2ff); }
    50% { box-shadow: 0 0 0 7px transparent; }
  }
  .cc-tm-today .cc-tm-val { font-size: 11px; color: var(--cc-accent-dark, #007aff); }
  .cc-tm-today.cc-tm-overlap .cc-tm-lbl {
    font-size: 6px;
    letter-spacing: .02em;
    max-width: 72px;
    line-height: 1.25;
    margin-left: auto;
    margin-right: auto;
  }
  .cc-tm-mile .cc-tm-dot {
    width: 6px; height: 6px;
    margin-top: 18px;
    border-width: 1.5px;
    opacity: .9;
  }
  .cc-tm-mile .cc-tm-val { font-size: 9px; font-weight: 700; }
  .cc-victory {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 24px 16px;
    background: linear-gradient(165deg, #e8fbea 0%, #fff 45%);
    gap: 6px;
  }
  .cc-victory-icon { font-size: 42px; line-height: 1; animation: ccBounce 1.2s ease infinite alternate; }
  @keyframes ccBounce { from { transform: translateY(0); } to { transform: translateY(-4px); } }
  .cc-victory-title {
    font-size: 24px;
    font-weight: 900;
    color: #1c1c1e;
    letter-spacing: -.03em;
  }
  .cc-victory-sub { font-size: 13px; color: #636366; font-weight: 500; max-width: 280px; }
  .cc-victory-stats { display: flex; gap: 24px; margin-top: 12px; }
  .cc-victory-stat-val { font-size: 22px; font-weight: 900; color: #248a3d; }
  .cc-victory-stat-lbl {
    font-size: 9px; font-weight: 700; color: #8e8e93;
    text-transform: uppercase; letter-spacing: .04em;
  }
</style>
"""


def _progress_ring_svg(pct, accent, track="#e5e5ea", r=26, sw=7):
    """Compact Activity-ring arc."""
    pct = max(0.0, min(100.0, float(pct)))
    circ = 2 * math.pi * r
    offset = circ * (1.0 - pct / 100.0)
    cx = cy = r + sw
    size = (r + sw) * 2
    return f"""
      <svg viewBox="0 0 {size} {size}" aria-hidden="true">
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{sw}"/>
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{accent}" stroke-width="{sw}"
          stroke-dasharray="{circ:.2f} {circ:.2f}" stroke-dashoffset="{offset:.2f}"
          stroke-linecap="round" transform="rotate(-90 {cx} {cy})"/>
      </svg>"""


def _mission_motivation(momentum, ctx, fc=None):
    direction = momentum.get("direction", "neutral")
    days = ctx.get("days", 0)
    source_hint = ""
    if fc:
        source_hint = forecast_source_label(fc)
    if direction == "improving":
        base = "Ahead of schedule — keep the pressure on."
    elif direction == "worsening":
        base = "Recalibrate this week — one clean day resets momentum."
    elif days <= 14:
        base = "Final stretch. Every day counts now."
    elif ctx.get("metric_progress", 0) >= 0.5:
        base = "Past halfway. The finish line is real."
    else:
        base = "Steady work compounds. Trust the process."
    if source_hint:
        return f"{base} Timeline based on {source_hint.lower()}."
    return base


def _command_center_hero_html(badge, pills, theme, momentum, mom_cls, trend_cls, trend_icon, trend_text, motivation):
    pill_items = []
    for i, (lbl, val, sub) in enumerate(pills):
        cls = "cc-hero-pill cc-hero-pill-featured" if i == 0 else "cc-hero-pill"
        if i == 0:
            pill_items.append(
                f"""<div class="{cls}">
              <span class="cc-pill-label" style="color:#8e8e93!important;">{lbl}</span>
              <span class="cc-pill-value" style="color:{theme['accent_dark']}!important;font-size:17px;">{val}</span>
              <span class="cc-pill-sub" style="color:#636366!important;">{sub}</span>
            </div>"""
            )
        else:
            pill_items.append(
                f"""<div class="{cls}">
              <span class="cc-pill-label">{lbl}</span>
              <span class="cc-pill-value">{val}</span>
              <span class="cc-pill-sub">{sub}</span>
            </div>"""
            )
    return f"""
    <div class="cc-hero" style="background:{theme['hero_grad']}; --cc-accent-dark:{theme['accent_dark']};">
      <div class="cc-hero-row">
        <div>
          <div class="cc-hero-emoji">{theme['emoji']}</div>
          <div class="cc-hero-title">{badge}</div>
          <div class="cc-hero-tagline">{theme['tagline']}</div>
          <div class="cc-hero-motivation">{motivation}</div>
        </div>
        <div class="cc-trend-pill {trend_cls}">{trend_icon} {trend_text}</div>
      </div>
      <div class="cc-hero-pills">{''.join(pill_items)}</div>
    </div>"""


def command_center_pill_data(s, fc, momentum, daily, dexa, mission_key=None):
    mission_key = mission_key or get_mission_mode()
    preset = MISSION_PRESETS.get(mission_key, MISSION_PRESETS["fat_loss"])
    cal_bal = mission_calorie_balance_label(mission_key)
    protein = float(preset["protein_target_g"])
    preview = mission_key != get_mission_mode()
    ctx = mission_journey_context(
        fc, s, daily, dexa, mission_override=mission_key if preview else None
    )
    mom_dir = momentum.get("direction", "neutral")
    mom_cls = "cc-momentum-good" if mom_dir == "improving" else ("cc-momentum-warn" if mom_dir == "worsening" else "")
    mom_text = {"improving": "Accelerating", "worsening": "Recalibrate"}.get(mom_dir, "On track")
    metric_type = ctx["metric_type"]
    if metric_type == "weight_lbs":
        pills = (
            ("Days left", f"{ctx['days']}", "to goal"),
            ("Weight", f"{ctx['current']:.1f}", "lb now"),
            ("Goal", f"{ctx['goal_metric']:.1f}", "lb"),
            ("Deficit", cal_bal.replace(" kcal deficit", "").replace(" kcal", ""), "kcal/day"),
            ("Protein", f"{protein:.0f}", "g/day"),
        )
    elif metric_type == "lean_lbs":
        pills = (
            ("Days left", f"{ctx['days']}", "to summit"),
            ("Lean", f"{ctx['current']:.1f}", "lb est."),
            ("Target", f"{ctx['goal_metric']:.1f}", "lb"),
            ("Surplus", cal_bal.replace(" kcal surplus", "").replace(" kcal", ""), "kcal/day"),
            ("Protein", f"{protein:.0f}", "g/day"),
        )
    elif metric_type == "strength_pct":
        pills = (
            ("Days left", f"{ctx['days']}", "to +5%"),
            ("Strength", f"+{ctx['current']:.1f}", "% gain"),
            ("Target", f"+{ctx['goal_metric']:.0f}", "%"),
            ("Surplus", cal_bal.replace(" kcal surplus", "").replace(" kcal", ""), "kcal/day"),
            ("Protein", f"{protein:.0f}", "g/day"),
        )
    else:
        avg_def = fc.get("avg_daily_deficit")
        cum = fc.get("cumulative_deficit_kcal")
        avg_lbl = f"{avg_def:.0f}" if avg_def is not None else cal_bal.replace(" kcal deficit", "").replace(" kcal", "")
        cum_lbl = f"{cum:,.0f}" if cum is not None else "—"
        pills = (
            ("Days left", f"{ctx['days']}", "to victory"),
            ("Body fat", f"{ctx['current']:.1f}", "% now"),
            ("Goal BF", f"{ctx['goal_metric']:.1f}", "%"),
            ("Cumulative", cum_lbl, "kcal deficit"),
            ("Pace", avg_lbl, "kcal/day"),
        )
    badge = MISSION_LABELS.get(mission_key, mission_key)
    if preview:
        badge = f"{badge} · preview"
    return ctx, pills, badge, mom_cls, mom_text


def command_center_summary_css():
    return command_center_unified_css()


def command_center_summary_html(s, fc, momentum, daily, dexa, mission_key=None):
    ctx, pills, badge, mom_cls, mom_text = command_center_pill_data(
        s, fc, momentum, daily, dexa, mission_key
    )
    pill_html = "".join(
        f"""<div class="cc-pill">
      <span class="cc-pill-label">{lbl}</span>
      <span class="cc-pill-value">{val}</span>
      <span class="cc-pill-sub">{sub}</span>
    </div>"""
        for lbl, val, sub in pills
    )
    return command_center_unified_css() + f"""
<div class="cc-unified">
  <div class="cc-metrics">
    <div class="cc-head">
      <span class="cc-mission-badge">{badge}</span>
      <span class="cc-momentum {mom_cls}">{mom_text}</span>
    </div>
    <div class="cc-pills">{pill_html}</div>
  </div>
</div>
"""


def _dexa_journey_markers(dexa, js, metric_type):
    """DEXA scans after the journey start — shown as milestones on the road."""
    if dexa is None or dexa.empty or metric_type != "bf_pct":
        return []
    journey_start = _coerce_date(js.get("start_date") if js else None)
    markers = []
    for row in dexa.sort_values("scan_date").itertuples():
        scan_day = pd.Timestamp(row.scan_date).date()
        if journey_start and scan_day <= journey_start:
            continue
        bf = float(row.body_fat_pct)
        lbl = pd.Timestamp(row.scan_date).strftime("%b '%y")
        markers.append((bf, lbl))
    return markers


def _journey_milestone_items(mission, start_metric, goal_metric, increasing):
    start = float(start_metric)
    goal = float(goal_metric)
    span = goal - start
    if mission in ("fat_loss", "weight_loss"):
        items = []
        for frac, label in JOURNEY_ROAD_FRACTIONS:
            val = start + span * float(frac)
            if increasing:
                if val <= start + abs(span) * 0.06:
                    continue
                if val >= goal - abs(span) * 0.06:
                    continue
            else:
                if val >= start - abs(span) * 0.06:
                    continue
                if val <= goal + abs(span) * 0.06:
                    continue
            items.append((val, label))
        return items
    if mission == "strength_gain":
        return [(float(frac), label) for frac, label in GAIN_ROAD_MILESTONES if frac <= STRENGTH_GAIN_TARGET_PCT]
    return [
        (start + span * frac, label)
        for frac, label in ((0.50, "Halfway"), (0.75, "Home stretch"))
        if abs(span) > 1e-6
    ]


def _milestone_marker_too_close(pct, avoid_pcts, min_gap=8.0):
    return any(abs(float(pct) - float(other)) < min_gap for other in avoid_pcts)


def _mission_journey_html(ctx, momentum):
    """Apple Health-style journey card: dual progress + milestone timeline."""
    mission = ctx["mission"]
    meta = ctx["meta"]
    theme = MISSION_JOURNEY_THEME.get(mission, MISSION_JOURNEY_THEME["fat_loss"])
    accent = theme["accent"]
    accent_soft = theme["accent_soft"]
    metric_type = ctx["metric_type"]
    start_metric = ctx["start_metric"]
    goal_metric = ctx["goal_metric"]
    current = ctx["current"]
    days = ctx["days"]
    goal_date = ctx["goal_date"]
    goal_date_label = goal_date.strftime("%b %d, %Y").replace(" 0", " ") if goal_date else "Need data"
    time_prog = ctx["time_progress"]
    metric_prog = ctx["metric_progress"]
    increasing = ctx["increasing"]

    time_pct = max(0.0, min(100.0, time_prog * 100.0))
    metric_pct = max(0.0, min(100.0, metric_prog * 100.0))
    start_display = _milestone_value_label(metric_type, start_metric)
    today_display = _milestone_value_label(metric_type, current)
    goal_display = _milestone_value_label(metric_type, goal_metric)
    days_lbl = meta["goal_label"].lower()
    journey_start = ctx.get("journey_start")
    journey_elapsed = int(ctx.get("journey_elapsed_days") or 0)
    journey_total = int(ctx.get("journey_total_days") or 0)
    start_label = (
        journey_start.strftime("%b %d, %Y").replace(" 0", " ")
        if journey_start
        else "—"
    )

    def metric_marker_pct(value):
        frac = metric_progress_frac(value, start_metric, goal_metric, increasing)
        return max(4.0, min(96.0, frac * 92.0 + 4.0))

    start_pct = 4.0
    goal_pct = 96.0
    today_pct = max(4.0, min(96.0, time_prog * 92.0 + 4.0))
    if journey_elapsed > 0 and today_pct < start_pct + 5.0:
        today_pct = min(goal_pct - 4.0, start_pct + 5.0)
    overlap_start_today = (
        journey_elapsed <= 0
        and abs(float(current) - float(start_metric)) < 0.08
    )

    milestone_html = ""
    avoid_pcts = [start_pct, today_pct, goal_pct]
    for val, label in _journey_milestone_items(mission, start_metric, goal_metric, increasing):
        if increasing and val < float(start_metric) - 0.001:
            continue
        if not increasing and val > float(start_metric) + 0.05:
            continue
        pct = metric_marker_pct(val)
        if _milestone_marker_too_close(pct, avoid_pcts):
            continue
        avoid_pcts.append(pct)
        display = _milestone_value_label(metric_type, val)
        milestone_html += f"""
          <div class="cc-tm cc-tm-mile" style="left:{pct:.1f}%; --cc-accent:{accent}; --cc-accent-soft:{accent_soft};">
            <div class="cc-tm-dot" style="border-color:{accent}"></div>
            <div class="cc-tm-val">{display}</div>
            <div class="cc-tm-lbl">{label}</div>
          </div>"""

    for val, label in ctx.get("dexa_markers") or []:
        if not increasing and val > float(start_metric) + 0.05:
            continue
        if increasing and val < float(start_metric) - 0.001:
            continue
        pct = metric_marker_pct(val)
        if _milestone_marker_too_close(pct, avoid_pcts):
            continue
        avoid_pcts.append(pct)
        display = _milestone_value_label(metric_type, val)
        milestone_html += f"""
          <div class="cc-tm cc-tm-mile" style="left:{pct:.1f}%; --cc-accent:{accent}; --cc-accent-soft:{accent_soft};">
            <div class="cc-tm-dot" style="border-color:{accent}"></div>
            <div class="cc-tm-val">{display}</div>
            <div class="cc-tm-lbl">{label}</div>
          </div>"""

    if overlap_start_today:
        start_marker_html = ""
        today_lbl = "Start · Today"
        today_pct = start_pct
    else:
        start_marker_html = f"""
            <div class="cc-tm cc-tm-start" style="left:{start_pct:.1f}%;">
              <div class="cc-tm-dot"></div>
              <div class="cc-tm-val">{start_display}</div>
              <div class="cc-tm-lbl">Start</div>
            </div>"""
        today_lbl = "Today"

    fill_left = start_pct
    fill_width = max(0.0, today_pct - start_pct)

    time_ring = _progress_ring_svg(time_pct, accent)
    metric_ring = _progress_ring_svg(metric_pct, accent)
    return f"""
      <div class="cc-journey-wrap">
        <div class="cc-journey" style="--cc-accent:{accent}; --cc-accent-soft:{accent_soft}; --cc-accent-dark:{theme['accent_dark']}; background:{theme['card_bg']};">
          <div class="cc-journey-mid">
            <div class="cc-rings">
              <div class="cc-ring-wrap">
                {time_ring}
                <div class="cc-ring-center">
                  <span class="cc-ring-pct">{time_pct:.0f}%</span>
                  <span class="cc-ring-lbl">Time</span>
                </div>
              </div>
              <div class="cc-ring-wrap">
                {metric_ring}
                <div class="cc-ring-center">
                  <span class="cc-ring-pct">{metric_pct:.0f}%</span>
                  <span class="cc-ring-lbl">{theme.get('metric_short', 'Go')}</span>
                </div>
              </div>
            </div>
            <div class="cc-countdown">
              <div class="cc-countdown-num">{days}</div>
              <div class="cc-countdown-lbl">days to {days_lbl}</div>
              <div class="cc-countdown-sub">Day {journey_elapsed} of {journey_total}</div>
            </div>
            <div class="cc-journey-meta">
              <div class="cc-journey-meta-lbl">Target</div>
              <div class="cc-journey-meta-val">{goal_date_label}</div>
              <div class="cc-journey-since">Since {start_label}</div>
            </div>
          </div>
          <div class="cc-metric-strip">
            <span>{theme['metric_name']} progress</span>
            <strong>{start_display} → {today_display} → {goal_display}</strong>
          </div>
          <div class="cc-timeline">
            <div class="cc-timeline-rail"></div>
            <div class="cc-timeline-fill" style="width:{fill_width:.1f}%;background:{accent};left:{fill_left:.1f}%;"></div>
            {start_marker_html}
            {milestone_html}
            <div class="cc-tm cc-tm-today{' cc-tm-overlap' if overlap_start_today else ''}" style="left:{today_pct:.1f}%;">
              <div class="cc-tm-dot" style="border-color:{accent}"></div>
              <div class="cc-tm-val">{today_display}</div>
              <div class="cc-tm-lbl">{today_lbl}</div>
            </div>
            <div class="cc-tm cc-tm-goal" style="left:{goal_pct:.1f}%;">
              <div class="cc-tm-dot" style="border-color:{accent}"></div>
              <div class="cc-tm-val">{goal_display}</div>
              <div class="cc-tm-lbl">{meta['goal_label']}</div>
            </div>
          </div>
        </div>
      </div>
    """


def command_center_unified_html(s, fc, momentum, daily, dexa, mission_key=None):
    """Single Apple Health-style card: metrics + mission road."""
    ctx, pills, badge, mom_cls, mom_text = command_center_pill_data(
        s, fc, momentum, daily, dexa, mission_key
    )
    if ctx["victory"]:
        return victoria_dashboard_html(fc, s, ctx["js"], daily)
    mission = ctx["mission"]
    theme = MISSION_JOURNEY_THEME.get(mission, MISSION_JOURNEY_THEME["fat_loss"])
    direction = momentum.get("direction", "neutral")
    if direction == "improving":
        trend_icon, trend_text, trend_cls = "↗", "Accelerating", "cc-trend-good"
    elif direction == "worsening":
        trend_icon, trend_text, trend_cls = "↘", "Recalibrate", "cc-trend-warn"
    else:
        trend_icon, trend_text, trend_cls = "→", "On track", "cc-trend-neutral"
    motivation = _mission_motivation(momentum, ctx, fc)
    hero_html = _command_center_hero_html(
        badge, pills, theme, momentum, mom_cls, trend_cls, trend_icon, trend_text, motivation
    )
    road_html = _mission_journey_html(ctx, momentum)
    return (
        command_center_unified_css()
        + f"""
<div class="cc-unified">
  {hero_html}
  {road_html}
</div>
"""
    )


def render_mission_command_center(s, daily=None, dexa=None, fc=None, momentum=None, coach=None):
    """Compact Apple Health-style mission bar + unified road card."""
    if fc is not None and momentum is not None:
        components.html(
            command_center_unified_html(s, fc, momentum, daily, dexa, get_mission_mode()),
            height=400,
            scrolling=False,
        )


def render_journey_start_controls(s, fc, daily, dexa, embedded=False):
    """Editable journey anchor — defaults to latest DEXA scan."""
    mission = get_mission_mode()
    js = get_or_create_journey_start(fc, s, daily, dexa)
    dexa_anchor = latest_dexa_journey_anchor(dexa, s, fc)

    def _body():
        if dexa_anchor.get("start_date") and not dexa.empty:
            st.caption(
                f"Latest DEXA **{dexa_anchor['start_date'].isoformat()}** — "
                f"{dexa_anchor['start_body_fat_pct']:.1f}% BF · {dexa_anchor['start_weight_lbs']:.1f} lb"
            )
        else:
            st.caption("No DEXA on file yet — set the start manually or import a scan.")

        default_start = _coerce_date(js.get("start_date")) or dexa_anchor["start_date"] or date.today()
        default_bf = float(
            js.get("start_body_fat_pct")
            or dexa_anchor["start_body_fat_pct"]
            or s.get("current_body_fat_pct")
            or 15.0
        )
        default_weight = float(
            js.get("start_weight_lbs")
            or dexa_anchor["start_weight_lbs"]
            or s.get("current_weight_lbs")
            or 175.0
        )
        lean_default = float(js.get("start_lean_lbs") or dexa_anchor["start_lean_lbs"] or 0)
        if lean_default <= 0 and default_weight > 0 and default_bf > 0:
            lean_default = default_weight * (1.0 - default_bf / 100.0)

        start_day = st.date_input("Journey start date", value=default_start, key="journey_start_date_input")
        anchor_hint = {
            "fat_loss": "Timeline **Start** uses the saved date and **Start body fat %** below.",
            "weight_loss": "Timeline **Start** uses the saved date and **Start weight** below.",
            "muscle_gain": "Timeline **Start** uses the saved date and **Start lean mass** below.",
            "strength_gain": "Timeline **Start** uses the saved date and lean baseline below.",
        }.get(mission, "Set the date and metrics you were at when this campaign began.")
        st.caption(anchor_hint)
        c2, c3 = st.columns(2)
        with c2:
            bf_label = "Start body fat % (timeline anchor)" if mission == "fat_loss" else "Start body fat %"
            start_bf = st.number_input(
                bf_label,
                min_value=3.0,
                max_value=50.0,
                value=default_bf,
                step=0.1,
                key="journey_start_bf_input",
            )
        with c3:
            wt_label = "Start weight (lb, timeline anchor)" if mission == "weight_loss" else "Start weight (lb)"
            start_weight = st.number_input(
                wt_label,
                min_value=80.0,
                max_value=400.0,
                value=default_weight,
                step=0.5,
                key="journey_start_weight_input",
            )
        start_lean = st.number_input(
            "Start lean mass (lb)",
            min_value=50.0,
            max_value=300.0,
            value=max(50.0, lean_default),
            step=0.1,
            key="journey_start_lean_input",
        )

        if js.get("start_date"):
            elapsed = journey_elapsed_days(js["start_date"])
            total = int(js.get("start_days") or journey_total_days(js["start_date"], fc.get("goal_date")))
            metric_lbl = format_journey_metric(js["metric_type"], js["start_metric"])
            sw = float(js.get("start_weight_lbs") or 0)
            sl = float(js.get("start_lean_lbs") or 0)
            sb = float(js.get("start_body_fat_pct") or js.get("start_metric") or 0)
            if sw > 0 and sl > 0 and sb > 0:
                implied_bf = 100.0 * (sw - sl) / sw
                if abs(implied_bf - sb) > 2.5:
                    st.warning(
                        f"Start lean ({sl:.1f} lb) doesn't match start BF ({sb:.1f}%) at {sw:.1f} lb "
                        f"(implies {implied_bf:.1f}% BF). Click **Save journey start** to sync lean from weight + BF."
                    )
            st.caption(
                f"Saved: **{js['start_date']}** · day **{elapsed}** of **{total}** · "
                f"start **{metric_lbl}**"
            )

        b1, b2 = st.columns(2)
        if b1.button("Use latest DEXA", use_container_width=True, key="journey_use_dexa"):
            reseed_journey_start(mission, fc, s, daily, dexa)
            st.rerun()
        if b2.button("Save journey start", type="primary", use_container_width=True, key="journey_save_start"):
            start_bf = float(start_bf)
            start_weight = float(start_weight)
            if start_bf > 0 and start_weight > 0:
                start_lean = start_weight * (1.0 - start_bf / 100.0)
            else:
                start_lean = float(start_lean)
            reseed_journey_start(
                mission,
                fc,
                s,
                daily,
                dexa,
                anchor_override={
                    "start_date": start_day,
                    "start_body_fat_pct": start_bf,
                    "start_weight_lbs": start_weight,
                    "start_lean_lbs": start_lean,
                },
            )
            st.rerun()

    if embedded:
        st.divider()
        st.markdown("**Journey start (timeline anchor)**")
        _body()
    else:
        with st.expander("Journey start (timeline anchor)", expanded=False):
            _body()


def body_fat_manual_override_active():
    return get_text_setting("current_body_fat_manual_override") == "1"


def weight_manual_override_active():
    return get_text_setting("current_weight_manual_override") == "1"


def effective_current_body_fat(fc, settings):
    """Today's BF for journey/hero — manual campaign target wins over DEXA estimate."""
    if body_fat_manual_override_active():
        manual = float(settings.get("current_body_fat_pct") or 0)
        if manual > 0:
            return manual
    return float(fc.get("current_bf") or settings.get("current_body_fat_pct") or 0)


def effective_current_weight(fc, settings):
    """Today's weight for journey/hero — latest scale/log, unless a manual override is set."""
    if weight_manual_override_active():
        manual = float(settings.get("current_weight_lbs") or 0)
        if manual > 0:
            return manual
    return float(
        fc.get("scale_weight")
        or fc.get("current_weight")
        or settings.get("current_weight_lbs")
        or 0
    )


def setting_field_source(field_key):
    if field_key == "current_weight_lbs":
        if get_text_setting("current_weight_manual_override") == "1":
            return "Manual Override"
        return get_text_setting("current_weight_source") or "Last saved"
    if field_key == "current_body_fat_pct":
        if body_fat_manual_override_active():
            return "Manual Override"
        return get_text_setting("current_body_fat_source") or "Last saved"
    return "Last saved"


def parse_import_ts(value):
    """Sortable timestamp for import provenance; missing values sort earliest."""
    if value is None or str(value).strip() == "":
        return pd.Timestamp.min
    try:
        ts = pd.Timestamp(value)
    except Exception:
        return pd.Timestamp.min
    if pd.isna(ts):
        return pd.Timestamp.min
    return ts


def live_weight_sane(weight):
    try:
        wt = float(weight)
    except (TypeError, ValueError):
        return False
    return 80.0 <= wt <= 400.0


def import_beats_saved(candidate_priority, candidate_ts, saved_priority, saved_ts):
    if not saved_ts:
        return True
    try:
        cp = int(candidate_priority if candidate_priority is not None else 99)
        sp = int(saved_priority if saved_priority is not None else 99)
    except (TypeError, ValueError):
        cp, sp = 99, 99
    if cp < sp:
        return True
    if cp > sp:
        return False
    return str(candidate_ts or "") > str(saved_ts or "")


def import_weight_beats_saved(candidate_ts, saved_ts, candidate_priority=None, saved_priority=None):
    """Newest weigh-in wins. Source priority is only a same-timestamp tie-breaker."""
    if not saved_ts:
        return True
    ct = parse_import_ts(candidate_ts)
    st = parse_import_ts(saved_ts)
    if ct > st:
        return True
    if ct < st:
        return False
    return import_beats_saved(candidate_priority, candidate_ts, saved_priority, saved_ts)


def import_provenance_group(source):
    return IMPORT_PROVENANCE_GROUPS.get(source, source)


def normalize_data_ts(value):
    if value is None or value == "":
        return None
    try:
        return pd.Timestamp(value)
    except Exception:
        return None


def parse_document_timestamp(path=None, log_date=None):
    """Best estimate of when document/data was captured (filename → mtime → log_date noon)."""
    path = Path(path) if path else None
    if path is not None:
        name = path.name
        patterns = [
            r"(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})",
            r"(\d{4})-(\d{2})-(\d{2})[_T ](\d{2}):(\d{2})(?::(\d{2}))?",
        ]
        for pat in patterns:
            m = re.search(pat, name)
            if not m:
                continue
            try:
                g = m.groups()
                if len(g) >= 6 and g[3] is not None:
                    return pd.Timestamp(
                        datetime(
                            int(g[0]), int(g[1]), int(g[2]),
                            int(g[3]), int(g[4]), int(g[5] or 0),
                        )
                    )
                if len(g) >= 5:
                    return pd.Timestamp(datetime(int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4])))
            except (TypeError, ValueError):
                continue
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", name)
        if m:
            try:
                return pd.Timestamp(date(int(m.group(1)), int(m.group(2)), int(m.group(3)))) + pd.Timedelta(hours=12)
            except ValueError:
                pass
        if path.exists():
            try:
                return pd.Timestamp.fromtimestamp(path.stat().st_mtime)
            except OSError:
                pass
    day = _coerce_date(log_date)
    if day:
        return pd.Timestamp(datetime.combine(day, datetime.min.time())) + pd.Timedelta(hours=12)
    if path is not None and path.exists():
        try:
            return pd.Timestamp.fromtimestamp(path.stat().st_mtime)
        except OSError:
            pass
    return pd.Timestamp.now()


def resolve_import_data_ts(log_date, path=None, measured_at=None, bedtime_end=None, data_ts=None):
    for candidate in (data_ts, measured_at, bedtime_end):
        ts = normalize_data_ts(candidate)
        if ts is not None and not pd.isna(ts):
            return ts
    return parse_document_timestamp(path, log_date)


def get_import_provenance(log_date, source):
    group = import_provenance_group(source)
    day = str(log_date)[:10]
    c = conn()
    row = c.execute(
        "SELECT data_ts, source, imported_at, file_hash FROM daily_import_provenance WHERE log_date = ? AND prov_group = ?",
        (day, group),
    ).fetchone()
    c.close()
    if not row:
        return None
    return {
        "data_ts": row[0],
        "source": row[1],
        "imported_at": row[2],
        "file_hash": row[3],
        "prov_group": group,
    }


def import_data_beats_existing(log_date, source, incoming_data_ts, file_hash=None):
    """True when incoming document is same age or newer than stored data for this day/group."""
    incoming = normalize_data_ts(incoming_data_ts)
    if incoming is None or pd.isna(incoming):
        incoming = parse_document_timestamp(log_date=log_date)
    existing = get_import_provenance(log_date, source)
    if not existing:
        return True
    if file_hash and existing.get("file_hash") == file_hash:
        return False
    stored = normalize_data_ts(existing.get("data_ts"))
    if stored is None or pd.isna(stored):
        return True
    if incoming > stored:
        return True
    if incoming < stored:
        return False
    return True


def record_import_provenance(log_date, source, data_ts, file_hash=None):
    group = import_provenance_group(source)
    day = str(log_date)[:10]
    ts = normalize_data_ts(data_ts) or parse_document_timestamp(log_date=day)
    now = datetime.now().isoformat(timespec="seconds")
    c = conn()
    c.execute(
        """
        INSERT OR REPLACE INTO daily_import_provenance
        (log_date, prov_group, data_ts, source, imported_at, file_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (day, group, ts.isoformat(), str(source), now, file_hash),
    )
    c.commit()
    c.close()


def _row_has_import_source_data(row, source):
    fields = IMPORT_SOURCE_FIELDS.get(source, [])
    if not fields:
        return False
    return any(row.get(field) not in (None, "", 0, 0.0) for field in fields)


def _infer_import_source_from_notes(notes):
    if not notes:
        return None
    for source in IMPORT_SOURCE_FIELDS:
        if f"[{source}]" in str(notes):
            return source
    return None


def seed_import_provenance_once():
    """Backfill provenance from existing OCR imports and daily_log so old re-imports cannot win."""
    if get_text_setting("import_provenance_seeded", "") == "1":
        return
    candidates = {}

    def consider(log_date, source, data_ts, file_hash=None):
        if source not in IMPORT_SOURCE_FIELDS:
            return
        day = str(log_date)[:10]
        ts = normalize_data_ts(data_ts) or parse_document_timestamp(log_date=day)
        key = (day, import_provenance_group(source))
        prior = candidates.get(key)
        if not prior:
            candidates[key] = {"data_ts": ts, "source": source, "file_hash": file_hash}
            return
        prior_ts = normalize_data_ts(prior.get("data_ts"))
        if prior_ts is None or pd.isna(prior_ts) or ts >= prior_ts:
            candidates[key] = {"data_ts": ts, "source": source, "file_hash": file_hash or prior.get("file_hash")}

    c = conn()
    try:
        ocr_rows = c.execute(
            """
            SELECT detected_type, stored_path, parsed_json, created_at, file_hash
            FROM ocr_queue
            WHERE status IN ('imported', 'confirmed')
            """
        ).fetchall()
    except sqlite3.OperationalError:
        ocr_rows = []
    c.close()

    for dtype, stored_path, parsed_json, created_at, file_hash in ocr_rows:
        source = dtype if dtype in IMPORT_SOURCE_FIELDS else None
        if not source:
            continue
        parsed = {}
        if parsed_json:
            try:
                parsed = json.loads(parsed_json)
            except (TypeError, json.JSONDecodeError):
                parsed = {}
        log_date = parsed.get("log_date") or parsed.get("scan_date")
        if not log_date and stored_path:
            log_date = parse_inbox_image_date(stored_path).isoformat()
        if not log_date:
            continue
        ts = resolve_import_data_ts(
            log_date,
            path=stored_path,
            measured_at=parsed.get("measured_at"),
            data_ts=created_at,
        )
        consider(log_date, source, ts, file_hash=file_hash)

    daily_df = load_daily()
    if not daily_df.empty:
        for _, row in daily_df.iterrows():
            notes = row.get("notes") or ""
            source = _infer_import_source_from_notes(notes)
            if not source or not _row_has_import_source_data(row, source):
                continue
            log_date = row["log_date"]
            if hasattr(log_date, "isoformat"):
                log_date = log_date.isoformat()
            ts = parse_document_timestamp(log_date=log_date)
            consider(log_date, source, ts)

    for (log_date, _group), meta in candidates.items():
        record_import_provenance(log_date, meta["source"], meta["data_ts"], file_hash=meta.get("file_hash"))

    save_text_setting("import_provenance_seeded", "1")


def save_weight_from_import(weight, source, priority, ts, clear_manual=True):
    save_setting("current_weight_lbs", float(weight))
    save_text_setting("current_weight_source", str(source))
    save_text_setting("current_weight_import_priority", str(priority))
    save_text_setting("current_weight_import_ts", str(ts))
    if clear_manual:
        save_text_setting("current_weight_manual_override", "")


def save_body_fat_from_dexa(body_fat_pct, scan_date, clear_manual=True, force=False):
    """Write DEXA BF to settings — skipped while manual override is active unless force=True."""
    if body_fat_manual_override_active() and not force:
        return False
    save_setting("current_body_fat_pct", float(body_fat_pct))
    save_text_setting("current_body_fat_source", "DEXA")
    save_text_setting("current_body_fat_import_ts", str(scan_date))
    if clear_manual:
        save_text_setting("current_body_fat_manual_override", "")
        save_text_setting("current_body_fat_manual_value", "")
    return True


def save_manual_body_fat(body_fat_pct):
    """Persist user-entered BF until explicitly reset to DEXA."""
    bf = float(body_fat_pct)
    save_setting("current_body_fat_pct", bf)
    save_text_setting("current_body_fat_manual_value", str(bf))
    save_text_setting("current_body_fat_manual_override", "1")
    save_text_setting("current_body_fat_source", "Manual Override")


def get_manual_body_fat(settings=None):
    raw = get_text_setting("current_body_fat_manual_value", "")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    if settings is not None:
        return float(settings.get("current_body_fat_pct") or 0)
    return float(load_persisted_settings().get("current_body_fat_pct") or 0)


def reset_body_fat_to_dexa(dexa):
    """Clear manual BF lock and restore from latest DEXA scan."""
    repair_corrupt_dexa_scans()
    dexa = load_dexa() if dexa is None or dexa.empty else dexa
    if dexa.empty:
        return None
    summary = apply_latest_dexa_to_live_metrics(dexa)
    if summary.get("ok"):
        return float(summary.get("body_fat_pct") or 0)
    bf, scan_date = latest_trusted_dexa_body_fat(dexa)
    if bf is not None:
        save_body_fat_from_dexa(bf, scan_date, clear_manual=False, force=True)
        return float(bf)
    return None


def ensure_manual_body_fat_restored(settings_dict):
    """On startup, re-apply locked manual BF if DEXA/import sync overwrote settings."""
    if not body_fat_manual_override_active():
        return settings_dict
    s = dict(settings_dict)
    manual_bf = get_manual_body_fat(s)
    if manual_bf > 0:
        stored = float(settings_dict.get("current_body_fat_pct") or 0)
        if abs(stored - manual_bf) > 1e-6:
            save_setting("current_body_fat_pct", manual_bf)
        s["current_body_fat_pct"] = manual_bf
    elif not get_text_setting("current_body_fat_manual_value", ""):
        # Legacy: flag set before dedicated manual_value key existed.
        save_text_setting("current_body_fat_manual_value", str(s.get("current_body_fat_pct") or ""))
    return s


def settings():
    c = conn()
    df = pd.read_sql("SELECT * FROM settings", c)
    c.close()
    return dict(zip(df.key, df.value))


def save_setting(k, v):
    c = conn()
    c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (k, float(v)))
    c.commit()
    c.close()


def get_fuel_planner_date():
    today = date.today()
    saved = get_text_setting("fuel_planner_date", "")
    if saved:
        try:
            saved_day = date.fromisoformat(saved)
            if saved_day < today:
                save_text_setting("fuel_planner_date", today.isoformat())
                return today
            return saved_day
        except ValueError:
            pass
    save_text_setting("fuel_planner_date", today.isoformat())
    return today


def parse_inbox_image_date(path, default=None, log_date=None):
    """Extract screenshot/capture calendar date from inbox or archived filename."""
    name = Path(path).name
    found = []
    for m in re.finditer(r"(\d{4})(\d{2})(\d{2})", name):
        try:
            found.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        except ValueError:
            continue
    for m in re.finditer(r"(\d{4})-(\d{2})-(\d{2})", name):
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if d not in found:
                found.append(d)
        except ValueError:
            continue

    coerced = _coerce_date(log_date)
    if coerced and coerced in found:
        return coerced

    if len(found) >= 2 and re.match(r"^\d{8}_\d{6}_", name):
        return found[1]

    if found:
        return found[0]

    return default or date.today()


def infer_fatsecret_log_date(stored_path, parsed=None, created_at=None):
    """Best calendar date for a FatSecret screenshot import."""
    parsed = parsed or {}
    raw = parsed.get("log_date")
    if raw:
        try:
            return pd.to_datetime(raw).date()
        except Exception:
            pass
    if stored_path:
        return parse_inbox_image_date(stored_path)
    if created_at:
        try:
            return pd.to_datetime(str(created_at)).date()
        except Exception:
            pass
    return date.today()


def load_daily():
    c = conn()
    df = pd.read_sql("SELECT * FROM daily_log ORDER BY log_date", c, parse_dates=["log_date"])
    c.close()
    return df


def load_dexa():
    c = conn()
    df = pd.read_sql("SELECT * FROM dexa_scans ORDER BY scan_date", c, parse_dates=["scan_date"])
    c.close()
    return df


def load_screenshots():
    c = conn()
    df = pd.read_sql("SELECT * FROM screenshots ORDER BY upload_date DESC", c)
    c.close()
    return df


def get_daily_row(log_date):
    if isinstance(log_date, date):
        log_date = log_date.isoformat()
    c = conn()
    row = c.execute("SELECT * FROM daily_log WHERE log_date = ?", (str(log_date),)).fetchone()
    c.close()
    if not row:
        return None
    return dict(zip(DAILY_COLS, row))


def tag_import_notes(source, notes=""):
    base = str(notes or "").strip()
    token = f"[{source}]"
    if token.lower() in base.lower():
        return base
    return f"{token} {base}".strip() if base else token


def upsert_daily(row, source=None, data_ts=None, file_hash=None, force=False, source_path=None):
    log_date = row.get("log_date")
    if hasattr(log_date, "isoformat"):
        log_date = log_date.isoformat()
    extra_data_ts = data_ts or row.get("_data_ts")
    extra_bedtime = row.get("_bedtime_end")
    measured_at = row.get("measured_at")
    row = {col: row.get(col) for col in DAILY_COLS}
    row["log_date"] = str(log_date)
    prior_notes = ""

    if source and source in IMPORT_SOURCE_FIELDS:
        incoming_ts = resolve_import_data_ts(
            row["log_date"],
            path=source_path,
            measured_at=measured_at,
            bedtime_end=extra_bedtime,
            data_ts=extra_data_ts,
        )
        if not force and not import_data_beats_existing(row["log_date"], source, incoming_ts, file_hash=file_hash):
            return False
        existing = get_daily_row(row["log_date"])
        if existing:
            prior_notes = existing.get("notes") or ""
            merged = dict(existing)
            for field in IMPORT_SOURCE_FIELDS[source]:
                if field in row and row.get(field) is not None:
                    merged[field] = row[field]
            row = merged
        if source == "Rebalance":
            row["notes"] = row.get("notes") or prior_notes or "Daily rebalance update"
        else:
            row["notes"] = tag_import_notes(source, row.get("notes") or prior_notes)

    c = conn()
    c.execute("""
        INSERT INTO daily_log VALUES (
            :log_date, :weight_lbs, :calories, :protein_g, :carbs_g, :fat_g,
            :steps, :active_energy, :resting_energy, :distance_miles,
            :sleep_minutes, :sleep_score, :readiness_score, :oura_burn,
            :workout, :workout_intensity, :subjective_energy, :notes
        )
        ON CONFLICT(log_date) DO UPDATE SET
            weight_lbs=excluded.weight_lbs,
            calories=excluded.calories,
            protein_g=excluded.protein_g,
            carbs_g=excluded.carbs_g,
            fat_g=excluded.fat_g,
            steps=excluded.steps,
            active_energy=excluded.active_energy,
            resting_energy=excluded.resting_energy,
            distance_miles=excluded.distance_miles,
            sleep_minutes=excluded.sleep_minutes,
            sleep_score=excluded.sleep_score,
            readiness_score=excluded.readiness_score,
            oura_burn=excluded.oura_burn,
            workout=excluded.workout,
            workout_intensity=excluded.workout_intensity,
            subjective_energy=excluded.subjective_energy,
            notes=excluded.notes
    """, row)
    c.commit()
    c.close()

    if source and source in IMPORT_SOURCE_FIELDS:
        record_import_provenance(
            row["log_date"],
            source,
            resolve_import_data_ts(
                row["log_date"],
                path=source_path,
                measured_at=measured_at,
                bedtime_end=extra_bedtime,
                data_ts=extra_data_ts,
            ),
            file_hash=file_hash,
        )
    return True


def save_dexa(row):
    c = conn()
    c.execute("""
        INSERT OR REPLACE INTO dexa_scans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, row)
    c.commit()
    c.close()


COMPOSITION_CALIB_DEFAULTS = {
    "fat_loss_fraction": 0.90,
    "muscle_gain_fraction": 0.55,
    "kcal_per_lb_fat": 3500.0,
    "protein_retention_factor": 1.0,
    "training_retention_factor": 1.0,
    "interval_count": 0,
}


def ensure_composition_calibration_tables():
    _init_db_schema()


def load_composition_calibration():
    ensure_composition_calibration_tables()
    c = conn()
    row = c.execute(
        """
        SELECT fat_loss_fraction, muscle_gain_fraction, kcal_per_lb_fat,
               protein_retention_factor, training_retention_factor,
               interval_count, last_scan_date, last_updated, notes
        FROM composition_calibration WHERE id = 1
        """
    ).fetchone()
    c.close()
    out = dict(COMPOSITION_CALIB_DEFAULTS)
    if row:
        keys = [
            "fat_loss_fraction", "muscle_gain_fraction", "kcal_per_lb_fat",
            "protein_retention_factor", "training_retention_factor",
            "interval_count", "last_scan_date", "last_updated", "notes",
        ]
        for key, val in zip(keys, row):
            if val is not None and key not in ("last_scan_date", "last_updated", "notes"):
                out[key] = float(val) if key != "interval_count" else int(val)
            elif val is not None:
                out[key] = val
    return out


def save_composition_calibration(data):
    ensure_composition_calibration_tables()
    cal = {**COMPOSITION_CALIB_DEFAULTS, **(data or {})}
    c = conn()
    c.execute(
        """
        INSERT OR REPLACE INTO composition_calibration
        (id, fat_loss_fraction, muscle_gain_fraction, kcal_per_lb_fat,
         protein_retention_factor, training_retention_factor,
         interval_count, last_scan_date, last_updated, notes)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            float(cal["fat_loss_fraction"]),
            float(cal["muscle_gain_fraction"]),
            float(cal["kcal_per_lb_fat"]),
            float(cal["protein_retention_factor"]),
            float(cal["training_retention_factor"]),
            int(cal.get("interval_count") or 0),
            cal.get("last_scan_date"),
            cal.get("last_updated") or datetime.now().isoformat(timespec="seconds"),
            cal.get("notes") or "",
        ),
    )
    c.commit()
    c.close()


def load_dexa_calibration_events():
    ensure_composition_calibration_tables()
    c = conn()
    try:
        df = pd.read_sql(
            "SELECT * FROM dexa_calibration_events ORDER BY scan_date, id",
            c,
            parse_dates=["scan_date", "prior_scan_date", "created_at"],
        )
    except Exception:
        df = pd.DataFrame()
    c.close()
    return df


def save_dexa_calibration_event(event):
    ensure_composition_calibration_tables()
    c = conn()
    c.execute(
        """
        INSERT INTO dexa_calibration_events (
            scan_date, prior_scan_date, interval_days,
            actual_weight_lbs, actual_fat_lbs, actual_lean_lbs, actual_bf_pct,
            predicted_weight_lbs, predicted_fat_lbs, predicted_lean_lbs, predicted_bf_pct,
            weight_error_lbs, fat_error_lbs, lean_error_lbs, bf_error_pct,
            observed_fat_fraction, observed_lean_fraction,
            cumulative_deficit_kcal, resistance_days, protein_adherence_pct,
            kcal_per_lb_fat_observed, created_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.get("scan_date"),
            event.get("prior_scan_date"),
            event.get("interval_days"),
            event.get("actual_weight_lbs"),
            event.get("actual_fat_lbs"),
            event.get("actual_lean_lbs"),
            event.get("actual_bf_pct"),
            event.get("predicted_weight_lbs"),
            event.get("predicted_fat_lbs"),
            event.get("predicted_lean_lbs"),
            event.get("predicted_bf_pct"),
            event.get("weight_error_lbs"),
            event.get("fat_error_lbs"),
            event.get("lean_error_lbs"),
            event.get("bf_error_pct"),
            event.get("observed_fat_fraction"),
            event.get("observed_lean_fraction"),
            event.get("cumulative_deficit_kcal"),
            event.get("resistance_days"),
            event.get("protein_adherence_pct"),
            event.get("kcal_per_lb_fat_observed"),
            event.get("created_at") or datetime.now().isoformat(timespec="seconds"),
            event.get("notes") or "",
        ),
    )
    c.commit()
    c.close()


def dexa_row_to_anchor(row):
    scan_day = row.get("scan_date")
    if hasattr(scan_day, "date"):
        scan_day = scan_day.date()
    elif scan_day is not None:
        scan_day = _coerce_date(scan_day)
    return {
        "date": scan_day,
        "weight": float(row["weight_lbs"]),
        "bf": float(row["body_fat_pct"]),
        "fat_mass": float(row["fat_mass_lbs"]),
        "lean_mass": float(row["lean_mass_lbs"]),
    }


def normalize_workout_label(workout_str):
    w = (str(workout_str or "")).lower()
    if "workout c" in w or "leg day" in w or w.strip() == "c":
        return "Workout C"
    if "workout b" in w or w.strip() == "b":
        return "Workout B"
    if "workout a" in w or w.strip() == "a":
        return "Workout A"
    if "stair" in w:
        return "StairMaster only"
    if "walk" in w or "step" in w:
        return "Long walk / high step day"
    return "None"


def day_expenditure_estimate(row, settings):
    steps = float(row.get("steps") if row.get("steps") not in (None, "") else settings.get("default_step_goal", 12000))
    base = float(settings["baseline_maintenance"]) + float(settings.get("adaptive_maintenance_adjustment", 0))
    step_burn = steps / 1000.0 * float(settings["step_calories_per_1000"])
    workout_type = normalize_workout_label(row.get("workout"))
    workout_burn = float(FUEL_WORKOUT_DEFAULTS.get(workout_type, 0))
    total = base + step_burn + workout_burn
    return total, workout_type


def _estimated_workout_burn_for_row(row, settings):
    workout_type = normalize_workout_label(row.get("workout"))
    if workout_type and workout_type != "None":
        return float(FUEL_WORKOUT_DEFAULTS.get(workout_type, 0))
    return 0.0


def _estimated_activity_burn_floor(row, settings):
    steps = float(row.get("steps") if row.get("steps") not in (None, "") else settings.get("default_step_goal", 12000))
    base = float(settings["baseline_maintenance"]) + float(settings.get("adaptive_maintenance_adjustment", 0))
    step_burn = steps / 1000.0 * float(settings["step_calories_per_1000"])
    return base + step_burn


def detect_oura_workout_undercount(row, settings):
    """Kept for older logs — Oura burn is never adjusted."""
    return None


def resolve_day_calories_burned(row, settings, manual_burn=None, apply_workout_adjustment=False):
    """Calories burned: Oura as reported, else Apple Health, else a last-resort estimate.

    Oura is never adjusted for workouts, remaining steps, or undercount.
    """
    row = row if isinstance(row, dict) else row.to_dict()
    oura = float(row.get("oura_burn") or 0)
    if oura > 0:
        return {
            "calories_burned": oura,
            "burn_source": "oura",
            "oura_burn": oura,
            "undercount": None,
            "suggested_burn": None,
        }

    if manual_burn is not None and float(manual_burn) > 0:
        burn = float(manual_burn)
        return {
            "calories_burned": burn,
            "burn_source": "manual",
            "oura_burn": None,
            "undercount": None,
            "suggested_burn": None,
        }

    active = float(row.get("active_energy") or 0)
    resting = float(row.get("resting_energy") or 0)
    if active > 0 and resting > 0:
        return {
            "calories_burned": active + resting,
            "burn_source": "apple_health",
            "oura_burn": None,
            "undercount": None,
            "suggested_burn": None,
        }

    total, _ = day_expenditure_estimate(row, settings)
    return {
        "calories_burned": float(total),
        "burn_source": "estimated",
        "oura_burn": None,
        "undercount": None,
        "suggested_burn": None,
    }


def burn_source_label(source):
    labels = {
        "oura": "Oura",
        "oura+workout_adjustment": "Oura + workout fix",
        "manual": "Manual",
        "apple_health": "Apple Health",
        "estimated": "Estimated",
        "day_close": "End-of-day log",
        "oura_entered": "Oura (entered)",
    }
    return labels.get(source or "", source or "—")


def _composition_expenditure_for_row(row, settings, manual_burn=None):
    resolved = resolve_day_calories_burned(row, settings, manual_burn=manual_burn)
    return float(resolved["calories_burned"] or 0)


def composition_interval_metrics(daily, settings, start_date, end_date):
    start_date = _coerce_date(start_date)
    end_date = _coerce_date(end_date)
    if start_date is None or end_date is None or daily.empty:
        return {
            "interval_days": 0,
            "days_with_calories": 0,
            "cumulative_deficit_kcal": 0.0,
            "cumulative_surplus_kcal": 0.0,
            "resistance_days": 0,
            "protein_adherence_pct": None,
        }

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    window = daily.copy()
    window = window[(window["log_date"] > start_ts) & (window["log_date"] <= end_ts)]
    interval_days = max((end_date - start_date).days, 1)
    protein_target = float(settings.get("protein_target_g") or 190.0)

    cumulative_deficit = 0.0
    cumulative_surplus = 0.0
    days_with_calories = 0
    resistance_days = 0
    protein_hits = 0
    protein_days = 0

    closes = load_daily_day_closes()
    close_burn_by_day = {}
    if closes is not None and not closes.empty:
        for _, crow in closes.iterrows():
            day = crow["log_date"].date() if hasattr(crow["log_date"], "date") else crow["log_date"]
            if pd.notna(crow.get("total_burn")) and float(crow["total_burn"]) > 0:
                close_burn_by_day[day] = float(crow["total_burn"])

    for _, row in window.iterrows():
        if _daily_row_is_resistance_day(row):
            resistance_days += 1
        calories = float(row.get("calories") or 0)
        if calories <= 0:
            continue
        day = row["log_date"].date() if hasattr(row["log_date"], "date") else row["log_date"]
        oura = float(row.get("oura_burn") or 0)
        manual_burn = None if oura > 0 else close_burn_by_day.get(day)
        resolved = resolve_day_calories_burned(row, settings, manual_burn=manual_burn)
        if resolved.get("burn_source") == "estimated":
            continue
        burn = float(resolved.get("calories_burned") or 0)
        if burn <= 0:
            continue
        days_with_calories += 1
        balance = burn - calories
        if balance > 0:
            cumulative_deficit += balance
        else:
            cumulative_surplus += abs(balance)
        protein = row.get("protein_g")
        if protein is not None and float(protein) > 0:
            protein_days += 1
            if float(protein) >= protein_target * 0.9:
                protein_hits += 1

    protein_adherence_pct = (
        100.0 * protein_hits / protein_days if protein_days > 0 else None
    )
    return {
        "interval_days": interval_days,
        "days_with_calories": days_with_calories,
        "cumulative_deficit_kcal": cumulative_deficit,
        "cumulative_surplus_kcal": cumulative_surplus,
        "resistance_days": resistance_days,
        "protein_adherence_pct": protein_adherence_pct,
    }


def _ema(previous, observed, alpha=0.35):
    if previous is None:
        return observed
    if observed is None:
        return previous
    return (1.0 - alpha) * float(previous) + alpha * float(observed)


def effective_composition_fractions(settings, calibration, weight_delta, metrics=None):
    cal = calibration or load_composition_calibration()
    metrics = metrics or {}
    mode = get_mission_mode()

    if mode in ("muscle_gain", "strength_gain") and weight_delta >= 0:
        base = float(
            cal.get("muscle_gain_fraction")
            or settings.get("muscle_gain_fraction")
            or MUSCLE_GAIN_FRACTION_BY_MISSION.get(mode, 0.55)
        )
        lean_frac = max(0.25, min(0.85, base))
    else:
        fat_frac = float(cal.get("fat_loss_fraction") or settings.get("fat_loss_fraction") or 0.90)
        lean_frac = max(0.0, min(1.0, 1.0 - fat_frac))

    protein_factor = float(cal.get("protein_retention_factor") or 1.0)
    training_factor = float(cal.get("training_retention_factor") or 1.0)
    interval_days = max(int(metrics.get("interval_days") or 1), 1)

    protein_adherence = metrics.get("protein_adherence_pct")
    if protein_adherence is not None:
        lean_frac += (float(protein_adherence) / 100.0 - 0.5) * 0.08 * protein_factor

    resistance_days = int(metrics.get("resistance_days") or 0)
    if resistance_days > 0:
        training_bonus = min(0.08, resistance_days / interval_days * 0.05) * training_factor
        if weight_delta < 0:
            lean_frac += training_bonus
        elif weight_delta > 0:
            lean_frac += training_bonus

    lean_frac = max(0.05, min(0.95, lean_frac))
    return lean_frac, 1.0 - lean_frac


def annual_lean_gain_lbs_setting(settings, mission=None):
    """Planned lean mass gain per year while cutting (recomp projection)."""
    mode = mission or get_mission_mode()
    if mode not in ("fat_loss", "weight_loss"):
        return 0.0
    return max(0.0, float(settings.get("annual_lean_gain_lbs") or 0.0))


def goal_fat_mass_lbs(lean_mass, goal_bf_pct):
    """Fat mass at goal BF% if lean mass stays at the DEXA baseline."""
    lean = float(lean_mass or 0)
    goal_frac = float(goal_bf_pct or 0) / 100.0
    if lean <= 0 or goal_frac <= 0 or goal_frac >= 1.0:
        return 0.0
    return lean * goal_frac / (1.0 - goal_frac)


def goal_weight_from_lean(lean_mass, goal_bf_pct):
    return float(lean_mass or 0) + goal_fat_mass_lbs(lean_mass, goal_bf_pct)


def fat_to_lose_to_goal_bf(lean_mass, fat_mass, goal_bf_pct):
    return max(0.0, float(fat_mass or 0) - goal_fat_mass_lbs(lean_mass, goal_bf_pct))


def net_energy_balance_kcal(metrics):
    """Positive = cumulative deficit (Oura burn − FatSecret intake)."""
    metrics = metrics or {}
    return float(metrics.get("cumulative_deficit_kcal") or 0) - float(
        metrics.get("cumulative_surplus_kcal") or 0
    )


def latest_logged_weight(daily, as_of=None, after_date=None, settings=None):
    """Newest sane scale / daily-log / saved weight in (after_date, as_of]."""

    def as_day(value):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if hasattr(value, "date") and callable(value.date):
            try:
                got = value.date()
                if isinstance(got, datetime):
                    return got.date()
                if isinstance(got, date):
                    return got
            except Exception:
                pass
        try:
            return date.fromisoformat(str(value)[:10])
        except (TypeError, ValueError):
            return None

    as_of = as_day(as_of) or date.today()
    after_date = as_day(after_date)
    best_day = None
    best_wt = None

    def consider(day, wt):
        nonlocal best_day, best_wt
        day = as_day(day)
        if day is None or not live_weight_sane(wt):
            return
        if day > as_of:
            return
        if after_date is not None and day <= after_date:
            return
        wt = float(wt)
        if best_day is None or day > best_day:
            best_day, best_wt = day, wt

    if daily is not None and not getattr(daily, "empty", True) and "weight_lbs" in daily.columns:
        wdf = daily.dropna(subset=["weight_lbs"]).copy()
        if not wdf.empty:
            wdf = wdf.sort_values("log_date")
            for _, row in wdf.iterrows():
                consider(row["log_date"], row["weight_lbs"])

    if settings:
        saved = settings.get("current_weight_lbs")
        saved_ts = get_text_setting("current_weight_import_ts")
        consider(saved_ts or as_of, saved)

    if best_wt is None:
        return None, None
    return float(best_wt), best_day


def estimate_composition_from_anchor(
    anchor, daily, settings, as_of=None, calibration=None, use_live_scale=True
):
    """DEXA lean held constant. Live weight follows the newest scale/log after the scan."""
    as_of = _coerce_date(as_of) or date.today()
    cal = calibration or load_composition_calibration()
    anchor_date = anchor.get("date")
    lean = float(anchor["lean_mass"])
    fat = float(anchor["fat_mass"])
    weight = float(anchor["weight"])
    bf = float(anchor["bf"])
    anchor_label = f"{anchor_date} DEXA" if anchor_date else "settings estimate"

    if anchor_date and as_of <= anchor_date:
        return {
            "current_weight": weight,
            "current_fat_mass": fat,
            "current_lean_mass": lean,
            "current_bf": bf,
            "weight_delta": 0.0,
            "lean_fraction": 0.0,
            "fat_fraction": 1.0,
            "estimation_method": "dexa_anchor",
            "anchor_label": anchor_label,
            "calibration_intervals": int(cal.get("interval_count") or 0),
            "cumulative_deficit_kcal": 0.0,
            "logged_deficit_days": 0,
            "scale_weight": weight,
            "scale_date": anchor_date,
        }

    metrics = (
        composition_interval_metrics(daily, settings, anchor_date, as_of)
        if anchor_date
        else {}
    )
    net_kcal = net_energy_balance_kcal(metrics)
    fat_lost = net_kcal / KCAL_PER_LB_FAT
    current_fat = max(0.0, fat - fat_lost)
    current_lean = max(0.0, lean)
    current_weight = current_fat + current_lean
    method = "dexa_cumulative_deficit"

    scale_weight, scale_day = latest_logged_weight(
        daily, as_of=as_of, after_date=None, settings=settings
    )
    live_weight, live_day = latest_logged_weight(
        daily, as_of=as_of, after_date=anchor_date, settings=settings
    )
    if scale_weight is None:
        scale_weight = live_weight if live_weight is not None else weight
        scale_day = live_day

    if (
        use_live_scale
        and live_weight is not None
        and live_weight > current_lean + 1.0
    ):
        current_weight = live_weight
        current_fat = max(0.0, current_weight - current_lean)
        method = "dexa_lean_plus_scale"
        if live_day:
            scale_weight = live_weight
            scale_day = live_day

    total_mass = current_fat + current_lean
    current_bf = 100.0 * current_fat / total_mass if total_mass > 0 else bf

    return {
        "current_weight": current_weight,
        "current_fat_mass": current_fat,
        "current_lean_mass": current_lean,
        "current_bf": current_bf,
        "weight_delta": current_weight - weight,
        "lean_fraction": 0.0,
        "fat_fraction": 1.0,
        "estimation_method": method,
        "anchor_label": anchor_label,
        "calibration_intervals": int(cal.get("interval_count") or 0),
        "interval_metrics": metrics,
        "projected_lean_gain_lbs": 0.0,
        "annual_lean_gain_lbs": 0.0,
        "cumulative_deficit_kcal": net_kcal,
        "logged_deficit_days": int(metrics.get("days_with_calories") or 0),
        "scale_weight": scale_weight,
        "scale_date": scale_day,
    }


def calibrate_composition_interval(prior_row, current_row, daily, settings, calibration_state=None):
    """Compare model prediction to new DEXA truth and refine composition coefficients."""
    prior_anchor = dexa_row_to_anchor(prior_row)
    current_anchor = dexa_row_to_anchor(current_row)
    scan_day = current_anchor["date"]
    prior_day = prior_anchor["date"]
    if scan_day is None or prior_day is None:
        return calibration_state or load_composition_calibration()

    daily_through = daily.copy() if not daily.empty else pd.DataFrame()
    if not daily_through.empty:
        daily_through = daily_through[daily_through["log_date"] <= pd.Timestamp(scan_day)]

    cal_before = dict(calibration_state or load_composition_calibration())
    pred = estimate_composition_from_anchor(
        prior_anchor,
        daily_through,
        settings,
        as_of=scan_day,
        calibration=cal_before,
        use_live_scale=False,
    )

    actual_weight = current_anchor["weight"]
    actual_fat = current_anchor["fat_mass"]
    actual_lean = current_anchor["lean_mass"]
    actual_bf = current_anchor["bf"]

    weight_delta = actual_weight - prior_anchor["weight"]
    fat_delta = actual_fat - prior_anchor["fat_mass"]
    lean_delta = actual_lean - prior_anchor["lean_mass"]
    metrics = composition_interval_metrics(daily, settings, prior_day, scan_day)

    observed_fat_fraction = None
    observed_lean_fraction = None
    if abs(weight_delta) > 0.1:
        observed_fat_fraction = max(0.0, min(1.0, fat_delta / weight_delta))
        observed_lean_fraction = max(0.0, min(1.0, lean_delta / weight_delta))

    observed_kcal_per_lb = None
    if fat_delta > 0.05 and metrics["cumulative_deficit_kcal"] > 100:
        observed_kcal_per_lb = metrics["cumulative_deficit_kcal"] / fat_delta
    elif fat_delta < -0.05 and metrics["cumulative_surplus_kcal"] > 100:
        observed_kcal_per_lb = metrics["cumulative_surplus_kcal"] / abs(fat_delta)

    alpha = 0.35
    new_cal = dict(cal_before)
    if observed_fat_fraction is not None:
        if weight_delta < -0.05:
            new_cal["fat_loss_fraction"] = _ema(
                cal_before.get("fat_loss_fraction"), observed_fat_fraction, alpha
            )
            new_cal["fat_loss_fraction"] = max(0.55, min(0.98, new_cal["fat_loss_fraction"]))
            save_setting("fat_loss_fraction", new_cal["fat_loss_fraction"])
        elif weight_delta > 0.05 and observed_lean_fraction is not None:
            new_cal["muscle_gain_fraction"] = _ema(
                cal_before.get("muscle_gain_fraction"), observed_lean_fraction, alpha
            )
            new_cal["muscle_gain_fraction"] = max(0.25, min(0.85, new_cal["muscle_gain_fraction"]))
            save_setting("muscle_gain_fraction", new_cal["muscle_gain_fraction"])

    if observed_kcal_per_lb is not None and 2500.0 <= observed_kcal_per_lb <= 4500.0:
        new_cal["kcal_per_lb_fat"] = _ema(
            cal_before.get("kcal_per_lb_fat"), observed_kcal_per_lb, alpha
        )

    if metrics.get("protein_adherence_pct") is not None and weight_delta < -0.05:
        retention_signal = 0.85 + 0.30 * (float(metrics["protein_adherence_pct"]) / 100.0)
        new_cal["protein_retention_factor"] = _ema(
            cal_before.get("protein_retention_factor"), retention_signal, alpha * 0.5
        )

    if metrics.get("resistance_days", 0) > 0:
        training_signal = 0.85 + min(0.30, metrics["resistance_days"] / max(metrics["interval_days"], 1))
        new_cal["training_retention_factor"] = _ema(
            cal_before.get("training_retention_factor"), training_signal, alpha * 0.5
        )

    new_cal["interval_count"] = int(cal_before.get("interval_count") or 0) + 1
    new_cal["last_scan_date"] = scan_day.isoformat() if hasattr(scan_day, "isoformat") else str(scan_day)
    new_cal["last_updated"] = datetime.now().isoformat(timespec="seconds")
    new_cal["notes"] = f"Calibrated from {prior_day} → {scan_day}"

    save_dexa_calibration_event(
        {
            "scan_date": new_cal["last_scan_date"],
            "prior_scan_date": prior_day.isoformat() if hasattr(prior_day, "isoformat") else str(prior_day),
            "interval_days": metrics.get("interval_days"),
            "actual_weight_lbs": actual_weight,
            "actual_fat_lbs": actual_fat,
            "actual_lean_lbs": actual_lean,
            "actual_bf_pct": actual_bf,
            "predicted_weight_lbs": pred["current_weight"],
            "predicted_fat_lbs": pred["current_fat_mass"],
            "predicted_lean_lbs": pred["current_lean_mass"],
            "predicted_bf_pct": pred["current_bf"],
            "weight_error_lbs": actual_weight - pred["current_weight"],
            "fat_error_lbs": actual_fat - pred["current_fat_mass"],
            "lean_error_lbs": actual_lean - pred["current_lean_mass"],
            "bf_error_pct": actual_bf - pred["current_bf"],
            "observed_fat_fraction": observed_fat_fraction,
            "observed_lean_fraction": observed_lean_fraction,
            "cumulative_deficit_kcal": metrics.get("cumulative_deficit_kcal"),
            "resistance_days": metrics.get("resistance_days"),
            "protein_adherence_pct": metrics.get("protein_adherence_pct"),
            "kcal_per_lb_fat_observed": observed_kcal_per_lb,
            "notes": "Quarterly DEXA calibration",
        }
    )
    save_composition_calibration(new_cal)
    return new_cal


def backfill_composition_calibration(dexa, daily, settings):
    """Learn coefficients from all historical DEXA intervals once."""
    events = load_dexa_calibration_events()
    if not events.empty or dexa.empty or len(dexa) < 2:
        return None
    cal = load_composition_calibration()
    for idx in range(1, len(dexa)):
        cal = calibrate_composition_interval(
            dexa.iloc[idx - 1], dexa.iloc[idx], daily, settings, calibration_state=cal
        )
    return cal


def _parse_dexa_fitpal_authoritative(text):
    """Highest-priority FITPAL PDF fields: trend table + lb composition Total row."""
    out = {}
    if not text:
        return out

    trend = re.search(r"Total Body % Fat Results[\s\S]{0,1000}", text, re.I)
    if trend:
        rows = re.findall(r"(\d{2}/\d{2}/\d{4})\s+\d+\s+([\d.]+)", trend.group(0))
        if rows:
            scan_date, bf = rows[-1]
            try:
                out["scan_date"] = pd.to_datetime(scan_date).date().isoformat()
                out["body_fat_pct"] = float(bf)
            except Exception:
                pass

    for line in text.replace("\r", "\n").split("\n"):
        stripped = line.strip()
        if not re.match(r"^Total\s+", stripped, re.I):
            continue
        if re.match(r"^Total\s+(?:Body|Fat|Lean|Mass|BMD)\b", stripped, re.I):
            continue
        nums = _dexa_parse_floats_from_text(re.sub(r"^Total\s+", "", stripped, flags=re.I))
        parsed = _dexa_row_from_four_numbers_lb(nums)
        if parsed and dexa_scan_values_sane(
            parsed.get("body_fat_pct"),
            parsed.get("fat_mass_lbs"),
            parsed.get("lean_mass_lbs"),
            parsed.get("weight_lbs"),
        ):
            out.update(parsed)
            break

    patient_weight = _parse_dexa_patient_weight_lb(text)
    if patient_weight:
        out["weight_lbs"] = patient_weight

    if not out.get("fat_mass_lbs"):
        fat_block = re.search(r"Total Fat Mass Results[\s\S]{0,500}", text, re.I)
        if fat_block:
            rows = re.findall(r"(\d{2}/\d{2}/\d{4})\s+\d+\s+([\d.]+)", fat_block.group(0))
            if rows:
                if not out.get("scan_date"):
                    try:
                        out["scan_date"] = pd.to_datetime(rows[-1][0]).date().isoformat()
                    except Exception:
                        pass
                out["fat_mass_lbs"] = float(rows[-1][1])

    return out


def dexa_scan_values_sane(body_fat_pct, fat_mass_lbs, lean_mass_lbs, weight_lbs):
    try:
        bf = float(body_fat_pct)
        fat = float(fat_mass_lbs)
        lean = float(lean_mass_lbs)
        weight = float(weight_lbs)
    except (TypeError, ValueError):
        return False
    return 8.0 <= bf <= 55.0 and fat >= 5.0 and lean >= 80.0 and 80.0 <= weight <= 400.0


def repair_corrupt_dexa_scans():
    """Re-parse DEXA PDF/HEIC sources when stored values fail sanity checks."""
    dexa = load_dexa()
    if dexa.empty:
        return 0
    repaired = 0
    for _, row in dexa.iterrows():
        if dexa_scan_values_sane(
            row.get("body_fat_pct"),
            row.get("fat_mass_lbs"),
            row.get("lean_mass_lbs"),
            row.get("weight_lbs"),
        ):
            continue
        source = str(row.get("source_file") or "")
        src_path = Path(source)
        if not src_path.exists():
            continue
        text = ""
        if src_path.suffix.lower() == ".pdf":
            text = extract_pdf_text(src_path)
        elif src_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic", ".webp"}:
            ocr_meta = run_ocr(src_path)
            text = ocr_meta.get("text") or ""
        if not text:
            continue
        parsed = parse_dexa_ocr(text, apply_learning=False)
        new_row = dexa_record_from_parsed(
            parsed,
            source_path=source,
            notes=f"Repaired DEXA import ({row.get('notes') or 'auto-fix'})",
        )
        if new_row and dexa_scan_values_sane(new_row[2], new_row[3], new_row[4], new_row[1]):
            save_dexa(new_row)
            repaired += 1
    return repaired


def apply_dexa_scan_record(row, daily=None, settings=None, reseed_journey=True):
    """Save DEXA truth, sync settings, and refine composition model when possible."""
    if not dexa_scan_values_sane(row[2], row[3], row[4], row[1]):
        return {
            "ok": False,
            "message": "DEXA values failed sanity check — scan not applied.",
            "scan_date": str(row[0]),
        }

    save_dexa(row)
    scan_date = row[0]
    scan_weight = float(row[1])
    bf = float(row[2])
    fat_mass = float(row[3])
    lean_mass = float(row[4])

    save_weight_from_import(scan_weight, "DEXA", 4, str(scan_date), clear_manual=True)
    save_body_fat_from_dexa(bf, str(scan_date), clear_manual=True, force=True)
    save_text_setting("last_applied_dexa_scan", str(scan_date)[:10])

    daily_df = daily if daily is not None else load_daily()
    settings_dict = settings if settings is not None else load_persisted_settings()
    dexa_df = load_dexa()
    summary = {"ok": True, "scan_date": str(scan_date), "calibrated": False}
    scan_key = str(scan_date)[:10]
    events = load_dexa_calibration_events()
    already_calibrated = (
        not events.empty
        and "scan_date" in events.columns
        and events["scan_date"].astype(str).str[:10].eq(scan_key).any()
    )

    if len(dexa_df) >= 2 and not already_calibrated:
        cal = calibrate_composition_interval(
            dexa_df.iloc[-2], dexa_df.iloc[-1], daily_df, settings_dict
        )
        summary.update(
            {
                "calibrated": True,
                "interval_count": int(cal.get("interval_count") or 0),
                "fat_loss_fraction": float(cal.get("fat_loss_fraction") or 0),
                "muscle_gain_fraction": float(cal.get("muscle_gain_fraction") or 0),
                "kcal_per_lb_fat": float(cal.get("kcal_per_lb_fat") or 3500),
                "message": (
                    f"DEXA saved — model calibrated ({cal.get('interval_count')} interval(s)). "
                    f"Fat-loss fraction now {float(cal.get('fat_loss_fraction') or 0)*100:.0f}%."
                ),
            }
        )
    else:
        summary["message"] = (
            f"DEXA anchor saved ({scan_date}) — {bf:.1f}% BF · {scan_weight:.1f} lb."
        )

    if reseed_journey:
        mission = get_mission_mode()
        _anchor, fc_seed = forecast_goal(daily_df, dexa_df, settings_dict)
        anchor = {
            "start_date": _coerce_date(scan_date) or date.today(),
            "start_body_fat_pct": bf,
            "start_weight_lbs": scan_weight,
            "start_lean_lbs": lean_mass,
        }
        reseed_journey_start(
            mission, fc_seed, settings_dict, daily_df, dexa_df, anchor_override=anchor
        )
        summary["journey_reseeded"] = True

    return summary


def extract_pdf_text(path):
    """Extract text from a PDF for DEXA / document parsing."""
    path = Path(path)
    if path.suffix.lower() != ".pdf" or not path.exists():
        return ""
    readers = []
    try:
        from pypdf import PdfReader as PypdfReader
        readers.append(("pypdf", PypdfReader))
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader as PyPDF2Reader
        readers.append(("PyPDF2", PyPDF2Reader))
    except ImportError:
        pass
    for _label, reader_cls in readers:
        try:
            pages = reader_cls(path).pages
            return "\n".join(page.extract_text() or "" for page in pages)
        except Exception:
            continue
    return ""


_FATSECRET_PDF_NAME_TOKENS = ("fooddiary", "food_diary", "fatsecret", "fat_secret")
_FATSECRET_PDF_TEXT_MARKERS = (
    "food diary report",
    "foods.fatsecret.com",
    "www.fatsecret.com",
    "fatsecret.com",
)
_WEEKDAY_LONG_DATE_RE = re.compile(
    r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"(\d{1,2}),\s+(\d{4})",
    re.I,
)
_FOODDIARY_YYMMDD_RE = re.compile(r"(?:fooddiary|food_diary)[_-]?(\d{6})", re.I)
_FATSECRET_DIARY_TOTAL_RE = re.compile(
    r"(?im)(?:^|\n)Total\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)"
)


def filename_looks_like_fatsecret_pdf(path):
    name = Path(path).name.lower()
    if Path(path).suffix.lower() != ".pdf":
        return False
    return any(token in name for token in _FATSECRET_PDF_NAME_TOKENS)


def _fatsecret_diary_date_from_filename(filename):
    m = _FOODDIARY_YYMMDD_RE.search(filename or "")
    if not m:
        return None
    yymmdd = m.group(1)
    try:
        return date(2000 + int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6])).isoformat()
    except ValueError:
        return None


def parse_fatsecret_food_diary_pdf(text, filename=""):
    """Parse a FatSecret Food Diary Report PDF (day total is the last Total row)."""
    result = {}
    body = text or ""
    m = _WEEKDAY_LONG_DATE_RE.search(body)
    if m:
        try:
            result["log_date"] = datetime.strptime(
                f"{m.group(2)} {m.group(3)} {m.group(4)}", "%B %d %Y"
            ).date().isoformat()
        except ValueError:
            pass
    if "log_date" not in result:
        named = _fatsecret_diary_date_from_filename(filename)
        if named:
            result["log_date"] = named

    totals = _FATSECRET_DIARY_TOTAL_RE.findall(body)
    if totals:
        cals, fat, _sat, carbs, _fiber, _sugar, prot = totals[-1]
        result["calories"] = float(cals)
        result["fat_g"] = float(fat)
        result["carbs_g"] = float(carbs)
        result["protein_g"] = float(prot)
        result["notes"] = "FatSecret food diary PDF"
    return result


def classify_pdf(path, text=None):
    """Detect DEXA or FatSecret food-diary PDFs by filename and extracted text."""
    path = Path(path)
    name = path.name.lower()
    if any(token in name for token in ("dexa", "hologic", "dexafit", "fitpal", "dxa", "body comp")):
        return "DEXA"
    if filename_looks_like_fatsecret_pdf(path):
        return "FatSecret"
    body = text if text is not None else extract_pdf_text(path)
    if not body:
        return "PDF"
    norm = normalize_ocr_for_classification(body)
    if any(marker in norm for marker in _FATSECRET_PDF_TEXT_MARKERS):
        return "FatSecret"
    dexa_markers = (
        "dxa results",
        "body composition results",
        "fitpal",
        "hologic",
        "horizon wi",
        "total body % fat",
        "lean + bmc",
    )
    if any(marker in norm for marker in dexa_markers):
        parsed = parse_dexa_ocr(body, apply_learning=False)
        if parsed.get("body_fat_pct") and parsed.get("weight_lbs"):
            return "DEXA"
    return "PDF"


def dexa_record_from_parsed(parsed, source_path="", notes=""):
    """Build dexa_scans row tuple from parsed DEXA fields."""
    scan_date = parsed.get("scan_date")
    weight = parsed.get("weight_lbs")
    bf = parsed.get("body_fat_pct")
    fat_mass = parsed.get("fat_mass_lbs")
    lean_mass = parsed.get("lean_mass_lbs")
    if not scan_date or weight is None or bf is None or fat_mass is None or lean_mass is None:
        return None
    if hasattr(scan_date, "isoformat"):
        scan_date = scan_date.isoformat()[:10]
    else:
        scan_date = str(scan_date)[:10]
    return (
        scan_date,
        float(weight),
        float(bf),
        float(fat_mass),
        float(lean_mass),
        parsed.get("vat_mass_g"),
        parsed.get("vat_volume_cm3"),
        parsed.get("vat_area_cm2"),
        str(source_path or ""),
        notes or "DEXA import",
    )


def auto_import_dexa_parsed(parsed, source_path="", notes="DEXA auto-import", daily=None, settings=None):
    """Save a fully parsed DEXA record and sync live metrics when possible."""
    row = dexa_record_from_parsed(parsed, source_path=source_path, notes=notes)
    if not row:
        return None
    return apply_dexa_scan_record(row, daily=daily, settings=settings)


def apply_latest_dexa_to_live_metrics(dexa, daily=None, settings=None):
    """Sync weight and body fat from the newest DEXA scan; clears manual BF override."""
    repair_corrupt_dexa_scans()
    dexa = load_dexa() if dexa is None else dexa
    if dexa is None or dexa.empty:
        return {"ok": False, "message": "No DEXA scans on file."}
    latest = dexa.sort_values("scan_date").iloc[-1]
    scan_date = latest["scan_date"]
    if hasattr(scan_date, "date"):
        scan_date = scan_date.date().isoformat()
    elif hasattr(scan_date, "isoformat"):
        scan_date = scan_date.isoformat()
    else:
        scan_date = str(scan_date)[:10]

    row = (
        scan_date,
        float(latest["weight_lbs"]),
        float(latest["body_fat_pct"]),
        float(latest["fat_mass_lbs"]),
        float(latest["lean_mass_lbs"]),
        latest.get("vat_mass_g"),
        latest.get("vat_volume_cm3"),
        latest.get("vat_area_cm2"),
        latest.get("source_file") or latest.get("source_path") or "",
        "Applied latest DEXA to live metrics",
    )
    summary = apply_dexa_scan_record(row, daily=daily, settings=settings, reseed_journey=True)
    summary["ok"] = bool(summary.get("ok", True))
    summary["scan_date"] = scan_date
    summary["body_fat_pct"] = float(latest["body_fat_pct"])
    summary["weight_lbs"] = float(latest["weight_lbs"])
    summary["message"] = (
        f"Live metrics synced to DEXA ({scan_date}): "
        f"{float(latest['weight_lbs']):.1f} lb · {float(latest['body_fat_pct']):.1f}% BF. "
        "Manual override cleared and journey re-anchored."
    )
    return summary


def sync_live_metrics_to_latest_dexa(dexa, settings, daily=None):
    """On startup: repair bad scans, apply newest DEXA, reseed journey when needed."""
    repair_corrupt_dexa_scans()
    dexa = load_dexa() if dexa is None else dexa
    if dexa is None or dexa.empty:
        return settings
    latest = dexa.sort_values("scan_date").iloc[-1]
    scan_key = str(latest["scan_date"])[:10]
    latest_bf = float(latest["body_fat_pct"])
    live_bf = float(settings.get("current_body_fat_pct") or 0)
    last_applied = get_text_setting("last_applied_dexa_scan", "")

    needs_apply = (
        last_applied != scan_key
        or body_fat_manual_override_active()
        or abs(live_bf - latest_bf) > 0.4
    )
    if needs_apply and dexa_scan_values_sane(
        latest["body_fat_pct"], latest["fat_mass_lbs"], latest["lean_mass_lbs"], latest["weight_lbs"]
    ):
        apply_latest_dexa_to_live_metrics(dexa, daily=daily, settings=settings)
        return load_persisted_settings()
    return settings


TORSO_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def _torso_silhouette_width(row_gray, bg_percentile=75):
    threshold = np.percentile(row_gray, bg_percentile)
    mask = row_gray < threshold - 8
    if not mask.any():
        return len(row_gray) * 0.4
    idx = np.where(mask)[0]
    return float(idx[-1] - idx[0] + 1)


def estimate_body_fat_from_torso_image(image_path, dexa_anchor_bf=None):
    """
    Visual body-fat estimate from a front-torso photo.
    Calibrated against DEXA anchor when provided — heuristic only, not medical grade.
    """
    display, _temp = prepare_ocr_image_path(image_path)
    if not display.exists():
        return None, {"error": "Image not found"}
    try:
        img = Image.open(display).convert("RGB")
    except Exception as exc:
        return None, {"error": str(exc)}
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    if h < 80 or w < 80:
        return None, {"error": "Image too small"}

    x0, x1 = int(w * 0.18), int(w * 0.82)
    y0, y1 = int(h * 0.12), int(h * 0.88)
    torso = arr[y0:y1, x0:x1]
    gray = 0.299 * torso[:, :, 0] + 0.587 * torso[:, :, 1] + 0.114 * torso[:, :, 2]
    th, _tw = gray.shape

    chest_band = gray[int(th * 0.18): int(th * 0.38), :]
    abs_band = gray[int(th * 0.48): int(th * 0.72), :]

    chest_edges = float(np.mean(np.abs(np.diff(chest_band, axis=0)))) if chest_band.size else 0.0
    abs_edges = float(np.mean(np.abs(np.diff(abs_band, axis=0)))) if abs_band.size else 0.0
    abs_std = float(np.std(abs_band)) if abs_band.size else 0.0
    abs_mean = float(np.mean(abs_band)) if abs_band.size else 128.0

    chest_w = _torso_silhouette_width(gray[int(th * 0.28), :])
    waist_w = _torso_silhouette_width(gray[int(th * 0.62), :])
    whr = waist_w / max(chest_w, 1.0)

    definition_score = abs_edges * 0.55 + chest_edges * 0.25 + abs_std * 0.20
    leanness_index = definition_score - whr * 18.0 - abs(abs_mean - 105.0) * 0.04

    estimated_bf = 24.5 - leanness_index * 0.22
    estimated_bf = float(np.clip(estimated_bf, 7.0, 32.0))

    if dexa_anchor_bf is not None:
        delta = estimated_bf - 15.0
        estimated_bf = float(dexa_anchor_bf) + delta * 0.65
        estimated_bf = float(np.clip(estimated_bf, 6.0, 35.0))

    confidence = "moderate"
    if abs_edges > 8 and whr < 0.88:
        confidence = "good"
    if abs_edges < 3:
        confidence = "low"

    metrics = {
        "definition_score": round(definition_score, 2),
        "waist_chest_ratio": round(whr, 3),
        "abdominal_edge_score": round(abs_edges, 2),
        "confidence": confidence,
        "dexa_anchor_bf": dexa_anchor_bf,
        "method": "torso_visual_heuristic",
    }
    return round(estimated_bf, 1), metrics


def _health_data_image_paths(source_dir=None):
    """All image files under the configured Health Data source folder."""
    source_dir = Path(source_dir or get_health_data_source_folder()).expanduser()
    if not source_dir.exists():
        return []
    paths = []
    try:
        for p in source_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in TORSO_IMAGE_EXTENSIONS:
                paths.append(p)
    except OSError:
        pass
    paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return paths


def list_torso_photo_candidates(max_files=200):
    candidates = []
    seen = set()

    def add_path(p, label):
        p = Path(p).expanduser()
        try:
            key = str(p.resolve())
        except OSError:
            key = str(p)
        if key in seen or not p.exists() or not p.is_file():
            return
        if p.suffix.lower() not in TORSO_IMAGE_EXTENSIONS:
            return
        seen.add(key)
        candidates.append({"path": p, "label": label, "name": p.name, "modified": p.stat().st_mtime})

    health_root = Path(get_health_data_source_folder()).expanduser()
    for p in _health_data_image_paths(health_root):
        try:
            rel = p.relative_to(health_root)
            if rel.parent != Path("."):
                label = f"Health Data / {rel.parent.as_posix()}"
            else:
                label = "Health Data"
        except ValueError:
            label = "Health Data"
        add_path(p, label)

    inbox = get_inbox_folder()
    if inbox.exists():
        try:
            inbox_paths = sorted(inbox.rglob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
        except OSError:
            inbox_paths = []
        for p in inbox_paths:
            if p.is_file() and p.suffix.lower() in TORSO_IMAGE_EXTENSIONS:
                add_path(p, "Inbox (synced from Health Data)")

    torso_dir = UPLOAD_DIR / "Torso"
    torso_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(torso_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file():
            add_path(p, "Torso uploads")

    for folder_name in ("Other", "DEXA", ""):
        folder = UPLOAD_DIR / folder_name if folder_name else UPLOAD_DIR
        if not folder.exists():
            continue
        try:
            paths = folder.rglob("*")
        except OSError:
            continue
        for p in paths:
            if not p.is_file():
                continue
            name = p.name.lower()
            if any(tok in name for tok in ("torso", "progress", "body", "bf", "physique", "front")):
                add_path(p, f"Uploads/{folder_name or 'root'}")

    reg = load_file_registry()
    if not reg.empty:
        skip_types = {"FatSecret", "Oura", "Workout", "DEXA", "Scale", "Apple Health Weight"}
        for _, row in reg.iterrows():
            path = row.get("stored_path") or row.get("source_path")
            dtype = str(row.get("detected_type") or "")
            if path and dtype not in skip_types:
                add_path(path, f"Registry ({dtype or 'image'})")

    candidates.sort(key=lambda c: c["modified"], reverse=True)
    return candidates[:max_files]


def save_torso_upload(uploaded_file):
    torso_dir = UPLOAD_DIR / "Torso"
    torso_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", uploaded_file.name)
    dest = torso_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe}"
    with dest.open("wb") as f:
        f.write(uploaded_file.getbuffer())
    if dest.suffix.lower() == ".heic":
        convert_heic_to_png(dest, dest.with_suffix(".png"))
    return dest


def render_torso_body_fat_panel(dexa, settings, fc):
    st.markdown("### Torso photo body-fat estimate")
    health_folder = get_health_data_source_folder()
    st.caption(
        f"Photos are loaded from your Health Data folder (`{health_folder}`) — the same source synced to the inbox. "
        "Select a front-torso shot for a visual estimate calibrated to your latest DEXA. "
        "Heuristic only; DEXA remains ground truth."
    )
    anchor_bf, anchor_date = latest_trusted_dexa_body_fat(dexa)

    uploaded = st.file_uploader(
        "Upload torso photo",
        type=["jpg", "jpeg", "png", "webp", "heic"],
        key="torso_photo_upload",
    )
    if uploaded is not None and st.button("Save uploaded photo to Torso library", key="save_torso_upload"):
        save_torso_upload(uploaded)
        st.success("Saved to Torso library.")
        st.rerun()

    candidates = list_torso_photo_candidates()
    health_count = sum(1 for c in candidates if c["label"].startswith("Health Data"))
    if health_count:
        st.caption(f"**{health_count}** photo(s) found in Health Data folder.")

    if not candidates:
        st.info(
            f"No photos found in `{health_folder}`. Add torso images there (JPG/PNG/HEIC) — "
            "they sync to the inbox automatically on startup."
        )
        return

    options = {f"{c['label']} · {c['name']}": c for c in candidates}
    selected_label = st.selectbox("Select photo", list(options.keys()), key="torso_photo_select")
    selected = options[selected_label]
    display, _temp = prepare_ocr_image_path(selected["path"])
    if display.exists() and display.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
        st.image(str(display), caption=selected["name"], width=420)

    if st.button("Estimate body fat from selected photo", key="estimate_torso_bf", type="primary"):
        est, metrics = estimate_body_fat_from_torso_image(selected["path"], dexa_anchor_bf=anchor_bf)
        if est is None:
            st.error(metrics.get("error", "Could not analyze image."))
        else:
            st.session_state.torso_bf_estimate = est
            st.session_state.torso_bf_metrics = metrics

    if st.session_state.get("torso_bf_estimate") is not None:
        est = st.session_state.torso_bf_estimate
        metrics = st.session_state.get("torso_bf_metrics") or {}
        live_bf = effective_current_body_fat(fc or {}, settings)
        st.metric("Visual estimate", f"{est:.1f}%", delta=f"{est - live_bf:+.1f} vs live" if live_bf else None)
        if anchor_bf is not None:
            st.caption(
                f"DEXA anchor: **{anchor_bf:.1f}%** ({anchor_date}) · "
                f"confidence: **{metrics.get('confidence', '—')}**"
            )
        with st.expander("Analysis details", expanded=False):
            st.json(metrics)
        if st.button("Use this estimate as current body fat % (manual override)", key="apply_torso_bf"):
            save_manual_body_fat(est)
            st.success(f"Set current body fat to {est:.1f}% (manual override).")
            st.rerun()


def save_uploaded_file(file, source, log_date, notes=""):
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", file.name)
    source_folder_map = {
        "DEXA": "DEXA",
        "FatSecret": "FatSecret",
        "Oura": "Oura",
        "Workout": "Workouts",
        "Strong": "Workouts",
    }
    target_folder = UPLOAD_DIR / source_folder_map.get(source, "Other")
    target_folder.mkdir(parents=True, exist_ok=True)
    dest = target_folder / f"{source}_{log_date}_{datetime.now().strftime('%H%M%S')}_{safe}"
    with dest.open("wb") as f:
        f.write(file.getbuffer())
    c = conn()
    c.execute(
        "INSERT INTO screenshots (upload_date, log_date, source, file_path, notes) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), str(log_date), source, str(dest), notes),
    )
    c.commit()
    c.close()
    return dest


def parse_fatsecret_text(text):
    result = {}
    m = re.search(r"(MON|TUE|WED|THU|FRI|SAT|SUN)\s+(\d{1,2})([A-Z]{3})\s+(\d{4})", text, re.I)
    month_map = {"JAN":1, "FEB":2, "MAR":3, "APR":4, "MAY":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12}
    if m:
        result["log_date"] = date(int(m.group(4)), month_map[m.group(3).upper()], int(m.group(2))).isoformat()

    m = re.search(r"My weight:\s*([\d.]+)\s*lb", text, re.I)
    if m:
        result["weight_lbs"] = float(m.group(1))

    # Food diary summary row: Fat Net C Prot Cals
    m = re.search(r"Fat\s+Net C\s+Prot\s+Cals\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text, re.I | re.S)
    if m:
        result["fat_g"] = float(m.group(1))
        result["carbs_g"] = float(m.group(2))
        result["protein_g"] = float(m.group(3))
        result["calories"] = float(m.group(4))
    else:
        # Diet calendar format
        m = re.search(r"(\d+)\s*kcal", text, re.I)
        if m:
            result["calories"] = float(m.group(1))
        for label, field in [("protein", "protein_g"), ("carbs", "carbs_g"), ("fat", "fat_g")]:
            m = re.search(label + r":\s*([\d.]+)g", text, re.I)
            if m:
                result[field] = float(m.group(1))

    result["notes"] = "FatSecret paste"
    return result


def parse_fatsecret_dataframe(df):
    if df is None or df.empty:
        return []
    norm = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in df.columns}

    def pick(*candidates):
        for cand in candidates:
            key = re.sub(r"[^a-z0-9]", "", cand.lower())
            if key in norm:
                return norm[key]
        return None

    date_col = pick("date", "logdate", "log date", "day")
    cal_col = pick("calories", "cals", "kcal", "energy")
    pro_col = pick("protein", "proteing", "protein g")
    carb_col = pick("carbs", "carbohydrates", "net carbs", "net c")
    fat_col = pick("fat", "fat g", "totalfat")
    weight_col = pick("weight", "weight lbs", "weightlb", "my weight")

    rows = []
    for _, r in df.iterrows():
        row = {"notes": "FatSecret spreadsheet auto import"}
        if date_col is not None and pd.notna(r.get(date_col)):
            try:
                row["log_date"] = pd.to_datetime(r[date_col]).date().isoformat()
            except Exception:
                pass
        if cal_col is not None and pd.notna(r.get(cal_col)):
            row["calories"] = float(r[cal_col])
        if pro_col is not None and pd.notna(r.get(pro_col)):
            row["protein_g"] = float(r[pro_col])
        if carb_col is not None and pd.notna(r.get(carb_col)):
            row["carbs_g"] = float(r[carb_col])
        if fat_col is not None and pd.notna(r.get(fat_col)):
            row["fat_g"] = float(r[fat_col])
        if weight_col is not None and pd.notna(r.get(weight_col)):
            row["weight_lbs"] = float(r[weight_col])
        if row.get("calories") or row.get("weight_lbs"):
            if "log_date" not in row:
                row["log_date"] = date.today().isoformat()
            rows.append(row)
    return rows


def parse_fatsecret_csv(path):
    try:
        return parse_fatsecret_dataframe(pd.read_csv(path))
    except Exception:
        return []


def is_strong_csv_dataframe(df):
    if df is None or df.empty:
        return False
    norm = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in df.columns}
    has_workout = "workoutname" in norm
    has_duration = "duration" in norm
    has_exercise = "exercisename" in norm
    return has_workout and has_duration and has_exercise


def csv_looks_like_strong(path):
    try:
        return is_strong_csv_dataframe(pd.read_csv(path, nrows=3))
    except Exception:
        return False


def parse_workout_duration_hours(value):
    """Parse Strong CSV Duration values such as 42m, 1h 29m, or HH:MM."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        if v <= 0:
            return None
        if v >= 300:
            return v / 3600.0
        return v / 60.0

    text = str(value).strip().lower()
    if not text:
        return None

    if re.fullmatch(r"\d+", text):
        return int(text) / 60.0

    m = re.fullmatch(r"(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:ute)?s?)?)?", text)
    if m and (m.group(1) or m.group(2)):
        return int(m.group(1) or 0) + int(m.group(2) or 0) / 60.0

    m = re.match(r"(\d+)\s*m(?:in(?:ute)?s?)?", text)
    if m:
        return int(m.group(1)) / 60.0

    if re.match(r"\d+:\d+", text):
        parts = [int(p) for p in text.split(":")]
        if len(parts) == 2:
            return parts[0] + parts[1] / 60.0
        if len(parts) == 3:
            return parts[0] + parts[1] / 60.0 + parts[2] / 3600.0

    return None


def workout_met_for_name(workout_name):
    """MET by workout type: Push/Pull 6, Legs 5, Shoulders/accessory 4."""
    w = (str(workout_name or "")).lower()
    if any(k in w for k in ("shoulder", "ohp", "overhead press", "lateral", "rear delt", "delt", "upright row")):
        return WORKOUT_MET_BY_TYPE["shoulders"]
    if any(k in w for k in ("accessory", "curl", "extension", "flye", "fly", "abs", "core", "hammer", "triceps", "biceps")):
        return WORKOUT_MET_BY_TYPE["accessory"]
    if any(k in w for k in ("leg", "squat", "lower", "deadlift", "lunge", "hip thrust", "workout c", "leg day", "leg press")):
        return WORKOUT_MET_BY_TYPE["legs"]
    if any(k in w for k in ("push", "chest", "bench", "incline", "press day", "workout a")):
        return WORKOUT_MET_BY_TYPE["push"]
    if any(k in w for k in ("pull", "back", "row", "lat", "chin", "workout b")):
        return WORKOUT_MET_BY_TYPE["pull"]
    return DEFAULT_RESISTANCE_MET


def estimate_met_workout_burn(met, weight_kg, duration_hours):
    return round(float(met) * float(weight_kg) * float(duration_hours), 1)


def parse_strong_dataframe(df, weight_kg):
    if not is_strong_csv_dataframe(df):
        return []

    norm = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in df.columns}
    date_col = norm["date"]
    workout_col = norm["workoutname"]
    duration_col = norm["duration"]

    sessions = {}
    for _, row in df.iterrows():
        workout_name = str(row.get(workout_col) or "").strip()
        if not workout_name:
            continue
        raw_date = row.get(date_col)
        if pd.isna(raw_date):
            continue
        try:
            session_dt = pd.to_datetime(raw_date)
        except Exception:
            continue
        log_date = session_dt.date().isoformat()
        duration_hours = parse_workout_duration_hours(row.get(duration_col))
        session_key = (log_date, workout_name)
        existing = sessions.get(session_key)
        if existing is None or (duration_hours and not existing.get("duration_hours")):
            met = workout_met_for_name(workout_name)
            burn = (
                estimate_met_workout_burn(met, weight_kg, duration_hours)
                if duration_hours and duration_hours > 0
                else None
            )
            sessions[session_key] = {
                "log_date": log_date,
                "workout": workout_name,
                "duration_hours": duration_hours,
                "met": met,
                "estimated_burn": burn,
            }
        elif existing and duration_hours and not existing.get("duration_hours"):
            existing["duration_hours"] = duration_hours
            existing["estimated_burn"] = estimate_met_workout_burn(
                existing["met"], weight_kg, duration_hours
            )

    return [s for s in sessions.values() if s.get("estimated_burn")]


def parse_strong_csv(path, weight_kg):
    try:
        return parse_strong_dataframe(pd.read_csv(path), weight_kg)
    except Exception:
        return []


def is_observed_workout_burn_row(row):
    """True when daily_log already has a workout-specific observed burn (not a Strong MET estimate)."""
    if not row:
        return False
    active_energy = float(row.get("active_energy") or 0)
    if active_energy <= 0:
        return False
    notes = str(row.get("notes") or "").lower()
    if "[strong]" in notes and "met estimate" in notes:
        return False
    if "[oura]" in notes:
        return False
    if any(
        token in notes
        for token in ("apple health", "hr monitor", "heart rate", "workout jpg", "observed burn", "observed workout")
    ):
        return True
    if "[workout]" in notes:
        return True
    return False


def upsert_strong_daily_estimate(session, source_path=None):
    row = {
        "log_date": session["log_date"],
        "workout": session["workout"],
        "active_energy": session["estimated_burn"],
        "notes": (
            f"Strong MET estimate: {session['met']:.0f} MET × "
            f"{session['duration_hours']:.2f} h → {session['estimated_burn']:.0f} kcal"
        ),
    }
    existing = get_daily_row(session["log_date"])
    if is_observed_workout_burn_row(existing):
        row.pop("active_energy", None)
    return upsert_daily(
        row,
        source="Strong",
        source_path=source_path,
        data_ts=parse_document_timestamp(source_path, session["log_date"]),
    )


def import_strong_csv_file(path, settings):
    weight_lbs = float(settings.get("current_weight_lbs") or DEFAULTS["current_weight_lbs"])
    weight_kg = weight_lbs * 0.453592
    sessions = parse_strong_csv(path, weight_kg)
    if not sessions:
        return 0, "Strong CSV stored (no sessions with duration found)"

    calibration_buckets = {}
    for session in sessions:
        calibration_key = session["workout"]
        calibration_buckets.setdefault(calibration_key, []).append(session)

    for workout_name, bucket in calibration_buckets.items():
        avg_burn = sum(s["estimated_burn"] for s in bucket) / len(bucket)
        avg_met = sum(s["met"] for s in bucket) / len(bucket)
        avg_duration_min = sum((s["duration_hours"] or 0) * 60 for s in bucket) / len(bucket)
        save_workout_estimate(workout_name, avg_burn, met=avg_met, duration_min=avg_duration_min)

    daily_by_date = {}
    for session in sessions:
        daily_by_date[session["log_date"]] = session
    csv_path = Path(path)
    applied = 0
    skipped = 0
    for session in daily_by_date.values():
        if upsert_strong_daily_estimate(session, source_path=csv_path):
            applied += 1
        else:
            skipped += 1

    detail = f"{len(sessions)} Strong session(s); {len(calibration_buckets)} workout type(s) calibrated (MET estimate)"
    if skipped:
        detail += f" ({skipped} day(s) skipped — newer data on file)"
    return len(sessions), detail


def discover_strong_csv_paths(source_dir=None):
    """Find Strong export CSV — newest file only (Drive copies like strong_workouts (5).csv)."""
    folder = Path(source_dir or get_health_data_source_folder()).expanduser()
    if not folder.is_dir():
        return []
    candidates = []
    for path in folder.glob("*.csv"):
        if csv_looks_like_strong(path):
            candidates.append(path)
    if not candidates:
        return []
    named = [
        path for path in candidates
        if re.match(r"strong_workouts(?:\s*\(\d+\))?\.csv$", path.name, re.I)
    ]
    pool = named or candidates
    return [max(pool, key=lambda p: (p.stat().st_mtime, p.stat().st_size))]


def load_strong_workout_sets(source_dir=None, force_reload=False):
    """Load Strong set-level export (cached by file fingerprint)."""
    paths = discover_strong_csv_paths(source_dir)
    fingerprint = _strong_paths_fingerprint(paths)
    if (
        not force_reload
        and fingerprint
        and _STRONG_LEAN_CACHE["fingerprint"] == fingerprint
        and _STRONG_LEAN_CACHE["sets"] is not None
    ):
        return _STRONG_LEAN_CACHE["sets"]

    if not paths:
        _STRONG_LEAN_CACHE.update({"fingerprint": None, "sets": pd.DataFrame(), "monthly": {}})
        return pd.DataFrame()

    path = paths[0]
    try:
        merged = pd.read_csv(path)
        if not is_strong_csv_dataframe(merged):
            merged = pd.DataFrame()
    except Exception:
        merged = pd.DataFrame()

    if not merged.empty:
        norm = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in merged.columns}
        date_col = norm["date"]
        workout_col = norm["workoutname"]
        exercise_col = norm["exercisename"]
        set_col = norm.get("setorder")
        weight_col = norm.get("weight")
        reps_col = norm.get("reps")

        merged = merged.copy()
        merged["_source_file"] = path.name
        merged["_session_dt"] = pd.to_datetime(merged[date_col], errors="coerce")
        merged = merged[merged["_session_dt"].notna()]
        dedupe_cols = [date_col, workout_col, exercise_col]
        if set_col:
            dedupe_cols.append(set_col)
        if weight_col:
            dedupe_cols.append(weight_col)
        if reps_col:
            dedupe_cols.append(reps_col)
        merged = merged.drop_duplicates(subset=dedupe_cols, keep="last")
        merged = merged.sort_values("_session_dt")

    _STRONG_LEAN_CACHE["fingerprint"] = fingerprint
    _STRONG_LEAN_CACHE["sets"] = merged
    _STRONG_LEAN_CACHE["monthly"] = {}
    return merged


def _month_window_bounds(period):
    month_start = period.start_time.date()
    month_end = period.end_time.date()
    return month_start, month_end


def _strong_sessions_by_month(sets_raw):
    """Count unique Strong workout days per calendar month."""
    if sets_raw is None or sets_raw.empty:
        return {}

    norm = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in sets_raw.columns}
    workout_col = norm["workoutname"]
    out = sets_raw.copy()
    out["month"] = out["_session_dt"].dt.to_period("M")
    out["session_date"] = out["_session_dt"].dt.date
    sessions_by_month = {}
    for period, chunk in out.groupby("month"):
        sessions_by_month[period] = int(
            chunk.groupby(["session_date", chunk[workout_col].astype(str)]).ngroups
        )
    return sessions_by_month


def compute_strong_monthly_lean_estimates(daily, settings, months_back=18, source_dir=None):
    """
    Simple monthly lean gain: (annual setting ÷ 12) scaled by Strong session frequency.
    Year cumulative resets each calendar year.
    """
    annual_cap = annual_lean_gain_lbs_setting(settings)
    sets_raw = load_strong_workout_sets(source_dir)
    cache_key = (
        _STRONG_LEAN_CACHE.get("fingerprint"),
        months_back,
        round(annual_cap, 2),
    )
    cached = _STRONG_LEAN_CACHE.get("monthly", {}).get(cache_key)
    if cached is not None:
        return cached

    if sets_raw.empty:
        _STRONG_LEAN_CACHE.setdefault("monthly", {})[cache_key] = []
        return []

    monthly_budget = annual_cap / 12.0 if annual_cap > 0 else 0.0
    sessions_by_month = _strong_sessions_by_month(sets_raw)
    month_periods = sorted(sessions_by_month.keys())
    if months_back and len(month_periods) > months_back:
        month_periods = month_periods[-months_back:]

    rows = []
    year_cumulative = {}
    for period in month_periods:
        month_start, month_end = _month_window_bounds(period)
        sessions = sessions_by_month.get(period, 0)
        freq = min(1.0, sessions / STRONG_LEAN_GAIN_TARGET_SESSIONS_MONTH) if sessions else 0.0
        lean_gain = monthly_budget * freq
        year = int(period.year)
        year_cumulative[year] = year_cumulative.get(year, 0.0) + lean_gain
        rows.append(
            {
                "month": str(period),
                "month_start": month_start,
                "month_end": month_end,
                "lean_gain_lb": round(lean_gain, 2),
                "year_cumulative_lb": round(year_cumulative[year], 2),
            }
        )

    _STRONG_LEAN_CACHE.setdefault("monthly", {})[cache_key] = rows
    return rows


def strong_lean_gain_available(source_dir=None):
    paths = discover_strong_csv_paths(source_dir)
    return bool(paths)


def strong_lean_gain_between_dates(daily, settings, start_date, end_date, source_dir=None):
    """Sum Strong-based monthly lean estimates across a date range (partial months prorated)."""
    start_date = _coerce_date(start_date)
    end_date = _coerce_date(end_date)
    if start_date is None or end_date is None or end_date <= start_date:
        return None

    monthly = compute_strong_monthly_lean_estimates(daily, settings, months_back=36, source_dir=source_dir)
    if not monthly:
        return None

    total = 0.0
    for row in monthly:
        month_start = row["month_start"]
        month_end = row["month_end"]
        overlap_start = max(start_date, month_start)
        overlap_end = min(end_date, month_end)
        if overlap_start > overlap_end:
            continue
        month_days = max((month_end - month_start).days + 1, 1)
        overlap_days = (overlap_end - overlap_start).days + 1
        total += float(row["lean_gain_lb"]) * (overlap_days / month_days)
    return total


def projected_lean_gain_lbs(
    settings,
    days,
    mission=None,
    daily=None,
    anchor_date=None,
    as_of=None,
    source_dir=None,
):
    as_of = _coerce_date(as_of) or date.today()
    anchor_date = _coerce_date(anchor_date)
    if daily is not None and anchor_date and as_of > anchor_date:
        strong_gain = strong_lean_gain_between_dates(
            daily, settings, anchor_date, as_of, source_dir=source_dir
        )
        if strong_gain is not None:
            return max(0.0, float(strong_gain))

    annual = annual_lean_gain_lbs_setting(settings, mission=mission)
    if annual <= 0 or days <= 0:
        return 0.0
    return annual * float(days) / 365.0


def render_strong_lean_gain_panel(daily, settings, dexa=None, fc=None):
    """Month-by-month lean gain from Strong session frequency."""
    if not strong_lean_gain_available():
        st.markdown("**Lean gain estimate**")
        st.info("Add **strong_workouts.csv** to your Health Data folder to enable monthly lean estimates.")
        return

    annual_cap = annual_lean_gain_lbs_setting(settings)
    monthly_budget = annual_cap / 12.0 if annual_cap > 0 else 0.0
    st.markdown("**Lean gain estimate**")
    st.caption(
        f"**{monthly_budget:.2f} lb/mo** max ({annual_cap:.0f} lb/yr setting) · "
        f"scaled by Strong sessions vs ~12/mo"
    )

    with st.spinner("Loading Strong sessions…"):
        monthly = compute_strong_monthly_lean_estimates(daily, settings)
    if not monthly:
        st.info("Strong CSV loaded but no workout sessions found.")
        return

    current_year = date.today().year
    ytd = next(
        (row["year_cumulative_lb"] for row in reversed(monthly) if str(row["month"]).startswith(str(current_year))),
        0.0,
    )
    c1, c2 = st.columns(2)
    c1.metric(f"{current_year} YTD lean (est.)", f"{ytd:.2f} lb")
    c2.metric("Annual target", f"{annual_cap:.1f} lb")

    view = pd.DataFrame(monthly).tail(12)
    display = view[["month", "lean_gain_lb", "year_cumulative_lb"]].rename(
        columns={
            "month": "Month",
            "lean_gain_lb": "Est. gain (lb)",
            "year_cumulative_lb": "Year cumulative (lb)",
        }
    )
    st.dataframe(display, use_container_width=True, hide_index=True)


def _oura_json_records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in (
            "data", "sleep", "sessions", "items", "readiness", "activity",
            "daily_sleep", "daily_activity", "daily_readiness", "records",
        ):
            chunk = payload.get(key)
            if isinstance(chunk, list):
                return chunk
        if payload.get("day") or payload.get("score") is not None:
            return [payload]
    return []


def _oura_record_day(record):
    if not isinstance(record, dict):
        return None
    for key in ("day", "date", "summary_date"):
        raw = record.get(key)
        if raw:
            return str(raw)[:10]
    for key in ("bedtime_end", "timestamp", "bedtime_start"):
        raw = record.get(key)
        if raw:
            try:
                return pd.to_datetime(raw).date().isoformat()
            except Exception:
                continue
    return None


def _oura_record_data_ts(record):
    if not isinstance(record, dict):
        return None
    for key in ("bedtime_end", "timestamp", "bedtime_start", "day", "date"):
        raw = record.get(key)
        if raw:
            ts = normalize_data_ts(raw)
            if ts is not None and not pd.isna(ts):
                return ts
    return None


def _oura_sleep_seconds(record):
    if not isinstance(record, dict):
        return 0
    for key in (
        "total_sleep_duration", "total_sleep_time", "duration", "sleep_duration",
        "time_asleep", "asleep_duration", "total_time_asleep",
    ):
        val = record.get(key)
        if val not in (None, "", 0):
            try:
                return max(0, int(float(val)))
            except (TypeError, ValueError):
                continue
    for key in ("deep_sleep_duration", "rem_sleep_duration", "light_sleep_duration"):
        val = record.get(key)
        if val not in (None, "", 0):
            try:
                secs = max(0, int(float(val)))
                if secs > 0:
                    return secs
            except (TypeError, ValueError):
                continue
    nested = record.get("sleep")
    if isinstance(nested, dict):
        nested_secs = _oura_sleep_seconds(nested)
        if nested_secs > 0:
            return nested_secs
    periods = record.get("periods") or record.get("sleep_periods")
    if isinstance(periods, list):
        total = 0
        for period in periods:
            if not isinstance(period, dict):
                continue
            for key in ("total_sleep_duration", "duration", "time_asleep"):
                val = period.get(key)
                if val not in (None, "", 0):
                    try:
                        total += max(0, int(float(val)))
                        break
                    except (TypeError, ValueError):
                        continue
        if total > 0:
            return total
    return 0


def _oura_sleep_score(record):
    if not isinstance(record, dict):
        return None
    for key in ("score", "sleep_score", "total_score"):
        val = record.get(key)
        if val not in (None, ""):
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    scores = record.get("scores")
    if isinstance(scores, dict):
        for key in ("total", "sleep", "score"):
            val = scores.get(key)
            if val not in (None, ""):
                try:
                    return float(val)
                except (TypeError, ValueError):
                    continue
    nested = record.get("sleep")
    if isinstance(nested, dict):
        return _oura_sleep_score(nested)
    return None


def _oura_readiness_score(record):
    if not isinstance(record, dict):
        return None
    score = record.get("score")
    if score in (None, "") and isinstance(record.get("readiness"), dict):
        score = record["readiness"].get("score")
    if score in (None, "") and isinstance(record.get("readiness"), (int, float)):
        score = record.get("readiness")
    if score not in (None, ""):
        try:
            return float(score)
        except (TypeError, ValueError):
            return None
    return None


def _oura_load_json_bytes(raw_bytes):
    try:
        return json.loads(raw_bytes.decode("utf-8"))
    except Exception:
        return None


def _oura_classify_json_name(name):
    lower = str(name or "").lower()
    if "sleep" in lower or "daily_sleep" in lower:
        return "sleep"
    if "readiness" in lower or "daily_readiness" in lower:
        return "readiness"
    if "activity" in lower or "daily_activity" in lower:
        return "activity"
    return "unknown"


def _oura_guess_json_kind(records):
    if not records:
        return "unknown"
    sample = records[0] if isinstance(records[0], dict) else {}
    if _oura_sleep_seconds(sample) > 0 or sample.get("deep_sleep_duration") or sample.get("rem_sleep_duration"):
        return "sleep"
    if _oura_readiness_score(sample) is not None or (
        sample.get("contributors") and sample.get("score") is not None
    ):
        return "readiness"
    if sample.get("steps") is not None or sample.get("active_calories") is not None:
        return "activity"
    return "unknown"


def _oura_merge_export_records(sleep_records, readiness_records, activity_records):
    by_day = {}

    def _ensure(day):
        if day not in by_day:
            by_day[day] = {"log_date": day}
        return by_day[day]

    for rec in sleep_records:
        if not isinstance(rec, dict):
            continue
        day = _oura_record_day(rec)
        if not day:
            continue
        row = _ensure(day)
        score = _oura_sleep_score(rec)
        if score is not None:
            row["sleep_score"] = score
        secs = _oura_sleep_seconds(rec)
        if secs > 0:
            row["sleep_minutes"] = round(secs / 60.0)
        extras = []
        for label, key in (
            ("deep", "deep_sleep_duration"),
            ("rem", "rem_sleep_duration"),
            ("light", "light_sleep_duration"),
        ):
            val = rec.get(key)
            if val not in (None, "", 0):
                try:
                    extras.append(f"{label}={int(float(val) // 60)}m")
                except (TypeError, ValueError):
                    pass
        if rec.get("average_hrv") not in (None, ""):
            try:
                extras.append(f"hrv={float(rec['average_hrv']):.0f}")
            except (TypeError, ValueError):
                pass
        if rec.get("average_heart_rate") not in (None, ""):
            try:
                extras.append(f"rhr={float(rec['average_heart_rate']):.0f}")
            except (TypeError, ValueError):
                pass
        if extras:
            row["_sleep_extra"] = " | ".join(extras)
        ts = _oura_record_data_ts(rec)
        if ts is not None:
            row["_data_ts"] = ts.isoformat()

    for rec in readiness_records:
        if not isinstance(rec, dict):
            continue
        day = _oura_record_day(rec)
        if not day:
            continue
        row = _ensure(day)
        score = _oura_readiness_score(rec)
        if score is not None:
            row["readiness_score"] = score
        ts = _oura_record_data_ts(rec)
        if ts is not None and "_data_ts" not in row:
            row["_data_ts"] = ts.isoformat()

    for rec in activity_records:
        if not isinstance(rec, dict):
            continue
        day = _oura_record_day(rec)
        if not day:
            continue
        row = _ensure(day)
        steps = rec.get("steps")
        if steps not in (None, ""):
            row["steps"] = float(steps)
        active = rec.get("active_calories")
        total = rec.get("total_calories")
        if active not in (None, ""):
            row["active_energy"] = float(active)
            row["oura_burn"] = float(active)
        elif total not in (None, ""):
            row["oura_burn"] = float(total)

    rows = []
    for day in sorted(by_day):
        row = by_day[day]
        extra = row.pop("_sleep_extra", "")
        note = "Oura export"
        if extra:
            note = f"{note} | {extra}"
        row["notes"] = note
        if row.get("sleep_minutes") or row.get("sleep_score") or row.get("readiness_score") or row.get("oura_burn"):
            rows.append(row)
    return rows


def parse_oura_export_path(path):
    """Parse Oura personal export ZIP or JSON (sleep, readiness, activity)."""
    path = Path(path)
    sleep_records = []
    readiness_records = []
    activity_records = []

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if not name.lower().endswith(".json"):
                    continue
                payload = _oura_load_json_bytes(zf.read(name))
                if payload is None:
                    continue
                records = _oura_json_records(payload)
                kind = _oura_classify_json_name(name)
                if kind == "unknown":
                    kind = _oura_guess_json_kind(records)
                if kind == "sleep":
                    sleep_records.extend(records)
                elif kind == "readiness":
                    readiness_records.extend(records)
                elif kind == "activity":
                    activity_records.extend(records)
    elif path.suffix.lower() == ".json":
        payload = _oura_load_json_bytes(path.read_bytes())
        if payload is None:
            return []
        records = _oura_json_records(payload)
        kind = _oura_classify_json_name(path.name)
        if kind == "unknown":
            kind = _oura_guess_json_kind(records)
        if kind == "sleep":
            sleep_records = records
        elif kind == "readiness":
            readiness_records = records
        elif kind == "activity":
            activity_records = records
        else:
            sleep_records = records
    else:
        return []

    return _oura_merge_export_records(sleep_records, readiness_records, activity_records)


def import_oura_export_file(path):
    rows = parse_oura_export_path(path)
    applied = 0
    skipped = 0
    export_path = Path(path)
    export_ts = parse_document_timestamp(export_path) if export_path.exists() else None
    for row in rows:
        row_ts = row.get("_data_ts") or (export_ts.isoformat() if export_ts is not None else None)
        payload = {k: v for k, v in row.items() if not str(k).startswith("_")}
        if row_ts:
            payload["_data_ts"] = row_ts
        if upsert_daily(payload, source="Oura Export", source_path=export_path):
            applied += 1
        else:
            skipped += 1
    if not rows:
        return 0, "Oura export stored (no sleep/readiness/activity rows found)"
    detail = f"{applied} day(s) merged from Oura export"
    if skipped:
        detail += f" ({skipped} skipped — newer data already on file)"
    return applied, detail


def _apple_health_parse_datetime(raw):
    if not raw:
        return None
    try:
        return pd.to_datetime(raw).to_pydatetime()
    except Exception:
        return None


def _apple_health_sleep_bucket(day_map, day_key, value, duration_sec):
    bucket = day_map.setdefault(
        day_key,
        {"asleep": 0.0, "in_bed": 0.0, "deep": 0.0, "rem": 0.0, "core": 0.0},
    )
    val = str(value or "")
    if "InBed" in val:
        bucket["in_bed"] += duration_sec
    elif "Awake" in val:
        return
    elif "Deep" in val:
        bucket["deep"] += duration_sec
        bucket["asleep"] += duration_sec
    elif "REM" in val:
        bucket["rem"] += duration_sec
        bucket["asleep"] += duration_sec
    elif "Core" in val:
        bucket["core"] += duration_sec
        bucket["asleep"] += duration_sec
    elif "Asleep" in val:
        bucket["asleep"] += duration_sec


def parse_apple_health_xml(path, import_sleep=True, import_weight=False, since_date=None, record_limit=None):
    """Stream-parse Apple Health export.xml for sleep (and optional weight)."""
    path = Path(path)
    since_ts = pd.Timestamp(since_date) if since_date else None
    sleep_by_day = {}
    sleep_end_ts = {}
    weight_rows = []
    seen = 0

    for _event, elem in ET.iterparse(str(path), events=("end",)):
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag != "Record":
            elem.clear()
            continue

        seen += 1
        if record_limit and seen > record_limit:
            break

        rtype = elem.get("type") or ""
        start = _apple_health_parse_datetime(elem.get("startDate"))
        end = _apple_health_parse_datetime(elem.get("endDate"))
        if since_ts is not None and end is not None and pd.Timestamp(end) < since_ts:
            elem.clear()
            continue

        if import_sleep and "SleepAnalysis" in rtype and start and end:
            duration = max(0.0, (end - start).total_seconds())
            if duration > 0:
                day_key = end.date().isoformat()
                _apple_health_sleep_bucket(sleep_by_day, day_key, elem.get("value"), duration)
                sleep_end_ts[day_key] = max(pd.Timestamp(sleep_end_ts.get(day_key, end)), pd.Timestamp(end)).to_pydatetime()
        elif import_weight and "BodyMass" in rtype and end:
            try:
                kg = float(elem.get("value") or 0)
            except (TypeError, ValueError):
                kg = 0.0
            if kg > 0:
                weight_rows.append(
                    {
                        "log_date": end.date().isoformat(),
                        "weight_lbs": round(kg * 2.20462, 2),
                        "measured_at": pd.Timestamp(end).isoformat(),
                        "_data_ts": pd.Timestamp(end).isoformat(),
                        "notes": "Apple Health weight export",
                    }
                )

        elem.clear()

    rows = []
    for day_key in sorted(sleep_by_day):
        bucket = sleep_by_day[day_key]
        sleep_sec = bucket["asleep"] or bucket["in_bed"]
        if sleep_sec <= 0:
            continue
        extras = []
        if bucket["deep"] > 0:
            extras.append(f"deep={int(bucket['deep'] // 60)}m")
        if bucket["rem"] > 0:
            extras.append(f"rem={int(bucket['rem'] // 60)}m")
        if bucket["core"] > 0:
            extras.append(f"core={int(bucket['core'] // 60)}m")
        end_dt = sleep_end_ts.get(day_key)
        row = {
            "log_date": day_key,
            "sleep_minutes": round(sleep_sec / 60.0),
            "notes": "Apple Health sleep" + (f" | {' | '.join(extras)}" if extras else ""),
        }
        if end_dt is not None:
            row["_data_ts"] = pd.Timestamp(end_dt).isoformat()
        rows.append(row)

    return {"sleep_rows": rows, "weight_rows": weight_rows, "records_scanned": seen}


def import_apple_health_xml_file(path, import_sleep=True, import_weight=False, since_date=None):
    parsed = parse_apple_health_xml(
        path,
        import_sleep=import_sleep,
        import_weight=import_weight,
        since_date=since_date,
    )
    applied = 0
    skipped = 0
    xml_path = Path(path)
    if import_sleep:
        for row in parsed["sleep_rows"]:
            if upsert_daily(row, source="Apple Health Sleep", source_path=xml_path):
                applied += 1
            else:
                skipped += 1
    if import_weight:
        weight_entries = [
            {
                "weight_lbs": row["weight_lbs"],
                "measured_at": row.get("measured_at") or row.get("log_date"),
                "log_date": row.get("log_date"),
            }
            for row in parsed["weight_rows"]
        ]
        if weight_entries:
            save_weight_measurements(
                weight_entries,
                source="Apple Health XML",
                notes="Apple Health weight export",
            )
            by_date = {}
            for entry in weight_entries:
                log_date = entry.get("log_date") or str(entry.get("measured_at") or "")[:10]
                measured_at = entry.get("measured_at") or log_date
                if not log_date or entry.get("weight_lbs") is None:
                    continue
                prior = by_date.get(log_date)
                if not prior or str(measured_at) > str(prior["measured_at"]):
                    by_date[log_date] = {
                        "weight_lbs": float(entry["weight_lbs"]),
                        "measured_at": measured_at,
                    }
            for log_date, payload in by_date.items():
                if upsert_daily(
                    {
                        "log_date": log_date,
                        "weight_lbs": payload["weight_lbs"],
                        "measured_at": payload["measured_at"],
                        "_data_ts": payload["measured_at"],
                        "notes": "Apple Health weight export",
                    },
                    source="Apple Health Weight",
                    source_path=xml_path,
                ):
                    applied += 1
                else:
                    skipped += 1
    if applied == 0 and skipped == 0:
        return 0, f"Apple Health XML scanned ({parsed['records_scanned']:,} records) — no matching rows"
    parts = []
    if import_sleep:
        parts.append(f"{len(parsed['sleep_rows'])} sleep day(s)")
    if import_weight:
        parts.append(f"{len(parsed['weight_rows'])} weight point(s)")
    detail = f"Imported {applied} row(s) from Apple Health XML ({', '.join(parts)})"
    if skipped:
        detail += f" — {skipped} skipped (newer data already stored)"
    return applied, detail


def discover_apple_health_export_xml_paths():
    """Locate export.xml copies without walking the whole Drive tree."""
    roots = []
    try:
        roots.append(Path(get_health_data_source_folder()))
    except Exception:
        pass
    roots.extend([Path(get_inbox_folder()), UPLOAD_DIR / "AppleHealth", UPLOAD_DIR])
    found = []
    for root in roots:
        if not root.is_dir():
            continue
        for pattern in ("export.xml", "*export*.xml"):
            try:
                found.extend(p for p in root.glob(pattern) if p.is_file())
            except OSError:
                continue
        try:
            found.extend(p for p in root.glob("*/export.xml") if p.is_file())
        except OSError:
            continue
    uniq = {}
    for path in found:
        try:
            uniq[str(path.resolve())] = path
        except OSError:
            uniq[str(path)] = path
    return list(uniq.values())


def latest_stored_weight_timestamp():
    """Newest scale/AH/daily-log timestamp already in the database."""
    stamps = []
    c = conn()
    try:
        row = c.execute("SELECT MAX(measured_at) FROM weight_measurements").fetchone()
        if row and row[0]:
            stamps.append(parse_import_ts(row[0]))
    except Exception:
        pass
    try:
        row = c.execute(
            """
            SELECT MAX(log_date) FROM daily_log
            WHERE weight_lbs IS NOT NULL AND weight_lbs >= 80 AND weight_lbs <= 400
            """
        ).fetchone()
        if row and row[0]:
            stamps.append(parse_import_ts(row[0]))
    except Exception:
        pass
    c.close()
    stamps = [ts for ts in stamps if ts != pd.Timestamp.min]
    if not stamps:
        return None
    return max(stamps)


def refresh_apple_health_xml_weights():
    """Pull BodyMass from a newer Apple Health export without waiting for a hash-new file."""
    paths = discover_apple_health_export_xml_paths()
    if not paths:
        return 0, "no apple health xml"
    path = max(paths, key=lambda p: p.stat().st_mtime)
    last_stored = latest_stored_weight_timestamp()
    xml_mtime = pd.Timestamp(datetime.fromtimestamp(path.stat().st_mtime))
    if last_stored is not None and xml_mtime <= last_stored:
        return 0, "apple health xml weights already current"
    since = None
    if last_stored is not None:
        since = (last_stored - pd.Timedelta(days=1)).date()
    return import_apple_health_xml_file(
        path, import_sleep=False, import_weight=True, since_date=since
    )


def save_structured_upload(uploaded_file, detected_type):
    folder = target_folder_for_type(detected_type)
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", uploaded_file.name)
    dest = folder / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe}"
    dest.write_bytes(uploaded_file.getbuffer())
    return dest


def auto_import_structured_file(path, detected_type):
    """Import structured inbox files into daily_log when parser data is available."""
    ext = path.suffix.lower()
    imported_rows = 0
    detail = ""

    if detected_type == "FatSecret CSV" or (detected_type in {"FatSecret", "Generic CSV"} and ext in {".csv", ".xlsx", ".xls"}):
        rows = parse_fatsecret_csv(path) if ext == ".csv" else []
        if not rows and ext in {".xlsx", ".xls"}:
            try:
                rows = parse_fatsecret_dataframe(pd.read_excel(path))
            except Exception:
                rows = []
        skipped = 0
        csv_path = Path(path)
        for row in rows:
            if upsert_daily(
                row,
                source="FatSecret",
                source_path=csv_path,
                data_ts=parse_document_timestamp(csv_path, row.get("log_date")),
            ):
                imported_rows += 1
            else:
                skipped += 1
        detail = f"{imported_rows} daily row(s) from spreadsheet"
        if skipped:
            detail += f" ({skipped} skipped — newer data on file)"
    elif ext == ".txt":
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            return 0, f"txt read failed: {exc}"
        parsed = parse_fatsecret_text(text)
        if parsed.get("calories") or parsed.get("weight_lbs"):
            if "log_date" not in parsed:
                parsed["log_date"] = date.today().isoformat()
            txt_path = Path(path)
            if upsert_daily(
                parsed,
                source="FatSecret",
                source_path=txt_path,
                data_ts=parse_document_timestamp(txt_path, parsed.get("log_date")),
            ):
                imported_rows = 1
                detail = "FatSecret text export imported"
            else:
                detail = "FatSecret text export skipped — newer data already on file"
        else:
            detail = "txt stored for review"
    elif detected_type == "Oura Export" or (ext == ".json" and "oura" in path.name.lower()):
        imported_rows, detail = import_oura_export_file(path)
    elif detected_type == "Apple Health XML":
        imported_rows, detail = import_apple_health_xml_file(path, import_sleep=True, import_weight=True)
    elif detected_type == "Strong CSV" or (ext == ".csv" and csv_looks_like_strong(path)):
        imported_rows, detail = import_strong_csv_file(path, load_persisted_settings())
    elif detected_type == "DEXA" and ext == ".pdf":
        text = extract_pdf_text(path)
        parsed = parse_dexa_ocr(text)
        summary = auto_import_dexa_parsed(
            parsed,
            source_path=str(path),
            notes="DEXA PDF auto-import",
        )
        if summary:
            imported_rows = 1
            detail = summary.get("message") or f"DEXA scan saved ({parsed.get('scan_date')})"
        else:
            detail = "DEXA PDF stored — could not parse all required fields"
    elif detected_type == "FatSecret" and ext == ".pdf":
        pdf_path = Path(path)
        text = extract_pdf_text(pdf_path)
        parsed = parse_fatsecret_food_diary_pdf(text, pdf_path.name)
        if not parsed.get("calories"):
            parsed = parse_fatsecret_ocr(text)
            diary = parse_fatsecret_food_diary_pdf(text, pdf_path.name)
            for key, val in diary.items():
                if val not in (None, ""):
                    parsed[key] = val
        if parsed.get("calories"):
            if not parsed.get("log_date"):
                parsed["log_date"] = infer_fatsecret_log_date(pdf_path, parsed).isoformat()
            if upsert_daily(
                parsed,
                source="FatSecret",
                source_path=pdf_path,
                data_ts=parse_document_timestamp(pdf_path, parsed.get("log_date")),
            ):
                imported_rows = 1
                detail = (
                    f"FatSecret food diary PDF imported "
                    f"({parsed.get('log_date')}, {int(float(parsed['calories']))} kcal)"
                )
            else:
                detail = "FatSecret food diary PDF skipped — newer data already on file"
        else:
            detail = "FatSecret PDF stored — could not parse daily totals"

    return imported_rows, detail


def add_metrics(df, s, closes=None):
    """Attach calories burned, intake, deficit (burn − eaten), and rolling averages."""
    if df.empty:
        return df
    out = df.copy()
    closes = closes if closes is not None else load_daily_day_closes()
    close_burn_by_day = {}
    if not closes.empty:
        for _, crow in closes.iterrows():
            day = crow["log_date"].date() if hasattr(crow["log_date"], "date") else crow["log_date"]
            if pd.notna(crow.get("total_burn")) and float(crow["total_burn"]) > 0:
                close_burn_by_day[day] = float(crow["total_burn"])

    burns = []
    burn_sources = []
    deficits = []
    suggested_burns = []
    undercount_flags = []
    target = float(s.get("target_deficit") or 500)

    for _, row in out.iterrows():
        day = row["log_date"].date() if hasattr(row["log_date"], "date") else row["log_date"]
        oura = float(row.get("oura_burn") or 0)
        close_burn = close_burn_by_day.get(day)
        # Oura as reported always wins. Day-close / Apple Health fill gaps only.
        manual_burn = None if oura > 0 else close_burn
        resolved = resolve_day_calories_burned(row, s, manual_burn=manual_burn)
        burn = float(resolved["calories_burned"] or 0)
        intake = float(row.get("calories") or 0)
        burns.append(burn if burn > 0 else None)
        source = resolved["burn_source"]
        if oura <= 0 and close_burn and close_burn > 0:
            source = "day_close"
        burn_sources.append(source)
        suggested_burns.append(resolved.get("suggested_burn"))
        undercount_flags.append(bool(resolved.get("undercount")))
        if intake > 0 and burn > 0 and source != "estimated":
            deficits.append(burn - intake)
        else:
            deficits.append(None)

    out["calories_in"] = out["calories"]
    out["calories_burned"] = burns
    out["burn_source"] = burn_sources
    out["estimated_burn"] = burns
    out["actual_deficit"] = deficits
    out["suggested_burn"] = suggested_burns
    out["oura_undercount_flag"] = undercount_flags
    out["deficit_vs_target"] = [
        (d - target) if d is not None else None for d in deficits
    ]
    out["weight_7d_avg"] = out["weight_lbs"].rolling(7, min_periods=3).mean()
    out["weight_14d_avg"] = out["weight_lbs"].rolling(14, min_periods=7).mean()
    out["steps_7d_avg"] = out["steps"].rolling(7, min_periods=3).mean()
    return out


DAILY_CLOSE_COLS = [
    "log_date", "weight_lbs", "calories", "protein_g", "carbs_g", "fat_g",
    "steps", "workout", "total_burn", "projected_deficit", "target_deficit",
    "finalized", "finalized_at", "notes",
]


def ensure_daily_day_close_table():
    c = conn()
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_day_close (
            log_date TEXT PRIMARY KEY,
            weight_lbs REAL,
            calories REAL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            steps REAL,
            workout TEXT,
            total_burn REAL,
            projected_deficit REAL,
            target_deficit REAL,
            finalized INTEGER DEFAULT 1,
            finalized_at TEXT,
            notes TEXT
        )
    """)
    c.commit()
    c.close()


def load_daily_day_closes():
    ensure_daily_day_close_table()
    c = conn()
    try:
        df = pd.read_sql(
            "SELECT * FROM daily_day_close ORDER BY log_date",
            c,
            parse_dates=["log_date"],
        )
    except Exception:
        df = pd.DataFrame(columns=DAILY_CLOSE_COLS)
    c.close()
    return df


def get_daily_day_close(log_day):
    if isinstance(log_day, date):
        log_day = log_day.isoformat()
    ensure_daily_day_close_table()
    c = conn()
    row = c.execute(
        "SELECT * FROM daily_day_close WHERE log_date = ?",
        (str(log_day),),
    ).fetchone()
    c.close()
    if not row:
        return None
    return dict(zip(DAILY_CLOSE_COLS, row))


def save_daily_day_close(close_row):
    ensure_daily_day_close_table()
    row = {col: close_row.get(col) for col in DAILY_CLOSE_COLS}
    row["log_date"] = str(row.get("log_date") or date.today().isoformat())[:10]
    row["finalized"] = int(row.get("finalized") if row.get("finalized") is not None else 1)
    row["finalized_at"] = row.get("finalized_at") or datetime.now().isoformat(timespec="seconds")
    c = conn()
    c.execute(
        """
        INSERT INTO daily_day_close VALUES (
            :log_date, :weight_lbs, :calories, :protein_g, :carbs_g, :fat_g,
            :steps, :workout, :total_burn, :projected_deficit, :target_deficit,
            :finalized, :finalized_at, :notes
        )
        ON CONFLICT(log_date) DO UPDATE SET
            weight_lbs=excluded.weight_lbs,
            calories=excluded.calories,
            protein_g=excluded.protein_g,
            carbs_g=excluded.carbs_g,
            fat_g=excluded.fat_g,
            steps=excluded.steps,
            workout=excluded.workout,
            total_burn=excluded.total_burn,
            projected_deficit=excluded.projected_deficit,
            target_deficit=excluded.target_deficit,
            finalized=excluded.finalized,
            finalized_at=excluded.finalized_at,
            notes=excluded.notes
        """,
        row,
    )
    c.commit()
    c.close()


def build_history_dataframe(daily, settings, closes=None):
    """Daily log enriched with burn/intake/deficit metrics and end-of-day close flags."""
    if daily.empty:
        return pd.DataFrame()
    closes = closes if closes is not None else load_daily_day_closes()
    close_by_day = {}
    if not closes.empty:
        for _, crow in closes.iterrows():
            day = crow["log_date"].date() if hasattr(crow["log_date"], "date") else crow["log_date"]
            close_by_day[day] = crow.to_dict()

    enriched = daily.copy()
    for idx, row in enriched.iterrows():
        day = row["log_date"].date() if hasattr(row["log_date"], "date") else row["log_date"]
        close = close_by_day.get(day) or {}
        if close.get("workout"):
            enriched.at[idx, "workout"] = close.get("workout")
        else:
            workout = row.get("workout")
            if not workout or str(workout).strip() in ("", "None", "nan"):
                scheduled = get_fuel_workout_for_date(day)
                if scheduled:
                    enriched.at[idx, "workout"] = scheduled
    hist = add_metrics(enriched, settings, closes=closes)
    if not closes.empty:
        finalized_by_day = {}
        for _, crow in closes.iterrows():
            day = crow["log_date"].date() if hasattr(crow["log_date"], "date") else crow["log_date"]
            finalized_by_day[day] = bool(crow.get("finalized"))
        hist["day_finalized"] = hist["log_date"].dt.date.map(lambda d: finalized_by_day.get(d, False))
    else:
        hist["day_finalized"] = False
    hist["close_burn"] = hist["calories_burned"]
    return hist


def compute_historical_average_deficit(daily, settings, lookback_days=30, finalized_only=False):
    """Average actual deficit from logged days with intake."""
    if daily.empty:
        return None
    df = build_history_dataframe(daily, settings)
    if finalized_only and "day_finalized" in df.columns:
        df = df[df["day_finalized"]]
    df = df[df["calories"].notna() & (df["calories"] > 0)]
    if df.empty:
        return None
    if lookback_days:
        cutoff = pd.Timestamp(date.today() - timedelta(days=int(lookback_days)))
        df = df[df["log_date"] >= cutoff]
    if df.empty:
        return None
    vals = pd.Series(df["actual_deficit"]).replace([np.inf, -np.inf], np.nan).dropna()
    if vals.empty:
        return None
    return float(vals.mean())


def compute_campaign_average_deficit(daily, settings, js):
    """Display-only average deficit from logged campaign days."""
    start_date = js.get("start_date")
    if daily.empty or not start_date:
        return None
    try:
        start_ts = pd.Timestamp(start_date)
    except Exception:
        return None
    if "log_date" not in daily.columns:
        return None
    campaign = build_history_dataframe(daily, settings)
    campaign = campaign[campaign["log_date"] >= start_ts]
    campaign = campaign[campaign["calories"].notna() & (campaign["calories"] > 0)]
    if campaign.empty:
        return None
    vals = campaign["actual_deficit"].replace([np.inf, -np.inf], np.nan).dropna()
    if vals.empty:
        return None
    return float(vals.mean())


def sleep_quality_from_score(score):
    """Map a 0–100 sleep score (Oura or logged) to Poor/Fair/Good/Excellent."""
    if score is None:
        return "Good"
    try:
        if pd.isna(score):
            return "Good"
        value = float(score)
    except (TypeError, ValueError):
        return "Good"
    if value < 54:
        return "Poor"
    if value < 70:
        return "Fair"
    if value < 85:
        return "Good"
    return "Excellent"


def sleep_score_from_quality(quality):
    return float(SLEEP_QUALITY_TO_SCORE.get(str(quality or "Good"), 78.0))


def is_training_workout(workout):
    label = str(workout or "").strip()
    if not label or label.lower() in ("none", "nan"):
        return False
    return True


def remaining_cut_to_goal(current_weight, goal_weight=None, fat_to_lose=None):
    """Fat/kcal still needed. Prefer fat_to_lose from the DEXA deficit model."""
    if fat_to_lose is not None:
        lbs = max(0.0, float(fat_to_lose))
        goal = float(goal_weight if goal_weight is not None else GOAL_WEIGHT_AT_10PCT_BF)
        current = float(current_weight or 0)
        return {
            "current_weight": current,
            "goal_weight": goal,
            "lbs_remaining": lbs,
            "kcal_remaining": lbs * KCAL_PER_LB_FAT,
        }
    goal = float(goal_weight if goal_weight is not None else GOAL_WEIGHT_AT_10PCT_BF)
    current = float(current_weight or 0)
    lbs = max(0.0, current - goal)
    return {
        "current_weight": current,
        "goal_weight": goal,
        "lbs_remaining": lbs,
        "kcal_remaining": lbs * KCAL_PER_LB_FAT,
    }


def compute_deficit_rollups(hist, today=None):
    """Sum logged calorie deficit for today, last 7 days, last 30 days, and all time."""
    today = today or date.today()
    empty = {
        "daily": None,
        "weekly": None,
        "monthly": None,
        "total": None,
        "daily_days": 0,
        "weekly_days": 0,
        "monthly_days": 0,
        "total_days": 0,
        "avg_daily": None,
    }
    if hist is None or hist.empty or "actual_deficit" not in hist.columns:
        return empty
    df = hist.copy()
    df["day"] = pd.to_datetime(df["log_date"]).dt.date
    vals = pd.to_numeric(df["actual_deficit"], errors="coerce")

    def _sum_for(mask):
        subset = vals[mask].dropna()
        if subset.empty:
            return None, 0
        return float(subset.sum()), int(len(subset))

    daily, n_d = _sum_for(df["day"] == today)
    weekly, n_w = _sum_for(df["day"] >= today - timedelta(days=6))
    monthly, n_m = _sum_for(df["day"] >= today - timedelta(days=29))
    total, n_t = _sum_for(vals.notna())
    avg_daily = (total / n_t) if total is not None and n_t > 0 else None
    return {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "total": total,
        "daily_days": n_d,
        "weekly_days": n_w,
        "monthly_days": n_m,
        "total_days": n_t,
        "avg_daily": avg_daily,
    }


DEFICIT_TARGET_HIT_FRACTION = 0.90


def _monday_on_or_before(day):
    day = _coerce_date(day) or date.today()
    return day - timedelta(days=day.weekday())


def deficit_target_threshold(target):
    """Count a day/week as on-target at 90% of the planned deficit (or surplus)."""
    target = float(target or 0)
    if target >= 0:
        return target * DEFICIT_TARGET_HIT_FRACTION
    return target * DEFICIT_TARGET_HIT_FRACTION


def _day_hits_target(deficit, target):
    if deficit is None or (isinstance(deficit, float) and pd.isna(deficit)):
        return False
    deficit = float(deficit)
    target = float(target or 0)
    threshold = deficit_target_threshold(target)
    if target >= 0:
        return deficit >= threshold
    return deficit <= threshold


def deficit_track_start_date(hist, fc=None, today=None):
    """First day of the cut visual: DEXA date when known, else first logged deficit day."""
    today = today or date.today()
    fc = fc or {}
    dexa_day = _coerce_date(fc.get("dexa_date"))
    if dexa_day:
        return dexa_day
    label = str(fc.get("composition_anchor") or "")
    m = re.match(r"(\d{4}-\d{2}-\d{2})", label)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    if hist is not None and not hist.empty and "log_date" in hist.columns:
        days = pd.to_datetime(hist["log_date"], errors="coerce").dt.date.dropna()
        if not days.empty:
            return min(days)
    return today - timedelta(days=83)


def build_deficit_tracking_frame(hist, settings, fc=None, today=None, start_date=None, live_today_deficit=None):
    """Calendar frame of daily deficit, hit/miss vs target, and running totals."""
    today = today or date.today()
    target = float((settings or {}).get("target_deficit") or 500)
    start_date = _coerce_date(start_date) or deficit_track_start_date(hist, fc, today=today)
    if start_date > today:
        start_date = today

    by_day = {}
    if hist is not None and not hist.empty and "actual_deficit" in hist.columns:
        work = hist.copy()
        work["day"] = pd.to_datetime(work["log_date"], errors="coerce").dt.date
        for _, row in work.iterrows():
            day = row.get("day")
            if day is None or (isinstance(day, float) and pd.isna(day)):
                continue
            val = row.get("actual_deficit")
            if val is None or (isinstance(val, float) and pd.isna(val)):
                continue
            by_day[day] = float(val)

    rows = []
    running = 0.0
    planned = 0.0
    day = start_date
    while day <= today:
        deficit = by_day.get(day)
        if day == today and live_today_deficit is not None:
            try:
                deficit = float(live_today_deficit)
            except (TypeError, ValueError):
                pass
        logged = deficit is not None
        if logged:
            running += deficit
            planned += target
        hit = _day_hits_target(deficit, target)
        rows.append(
            {
                "day": day,
                "day_ts": pd.Timestamp(day),
                "deficit": deficit,
                "target": target,
                "hit": hit,
                "logged": logged,
                "status": "hit" if hit else ("miss" if logged else "empty"),
                "cumulative": running,
                "planned_cumulative": planned,
                "week_start": _monday_on_or_before(day),
            }
        )
        day += timedelta(days=1)
    daily = pd.DataFrame(rows)
    if daily.empty:
        weekly = pd.DataFrame()
        return daily, weekly, target

    weekly_rows = []
    for week_start, group in daily.groupby("week_start", sort=True):
        week_end = min(week_start + timedelta(days=6), today)
        days_in_week = (week_end - week_start).days + 1
        logged_days = int(group["logged"].sum())
        hit_days = int(group["hit"].sum())
        deficit_sum = float(group.loc[group["logged"], "deficit"].sum()) if logged_days else 0.0
        week_target = target * max(logged_days, 1)
        avg_def = (deficit_sum / logged_days) if logged_days else None
        week_hit = _day_hits_target(avg_def, target) if logged_days else False
        weekly_rows.append(
            {
                "week_start": week_start,
                "week_ts": pd.Timestamp(week_start),
                "week_label": f"{week_start.month}/{week_start.day}",
                "deficit": deficit_sum,
                "week_target": week_target,
                "logged_days": logged_days,
                "hit_days": hit_days,
                "days_in_week": days_in_week,
                "hit": week_hit,
                "status": "hit" if week_hit else ("miss" if logged_days else "empty"),
            }
        )
    weekly = pd.DataFrame(weekly_rows)
    return daily, weekly, target


def deficit_hit_stats(daily, weekly, today=None):
    today = today or date.today()
    empty = {
        "days_hit_7": 0,
        "days_logged_7": 0,
        "weeks_hit": 0,
        "weeks_logged": 0,
        "streak": 0,
        "vs_plan": None,
        "cumulative": None,
        "planned": None,
    }
    if daily is None or daily.empty:
        return empty
    last7 = daily[daily["day"] >= today - timedelta(days=6)]
    weeks_logged = weekly[weekly["logged_days"] > 0] if weekly is not None and not weekly.empty else pd.DataFrame()
    vs_plan = None
    cumulative = float(daily.iloc[-1]["cumulative"])
    planned = float(daily.iloc[-1]["planned_cumulative"])
    vs_plan = cumulative - planned
    streak = 0
    for rec in reversed(list(daily.itertuples(index=False))):
        if rec.day > today:
            continue
        if rec.day == today and not rec.logged:
            continue
        if rec.hit:
            streak += 1
            continue
        break
    return {
        "days_hit_7": int(last7["hit"].sum()),
        "days_logged_7": int(last7["logged"].sum()),
        "weeks_hit": int(weeks_logged["hit"].sum()) if not weeks_logged.empty else 0,
        "weeks_logged": int(len(weeks_logged)),
        "streak": streak,
        "vs_plan": vs_plan,
        "cumulative": cumulative,
        "planned": planned,
    }


def deficit_heatmap_html(daily, today=None, weeks=12):
    """GitHub-style week columns × weekday rows: gold = at target, red = short."""
    today = today or date.today()
    start = _monday_on_or_before(today) - timedelta(weeks=max(1, int(weeks)) - 1)
    by_day = {}
    if daily is not None and not daily.empty:
        for _, row in daily.iterrows():
            by_day[row["day"]] = row
    cols = max(1, int(weeks))
    cell_colors = {
        "hit": ("#C9A84C", "#C9A84C"),
        "miss": ("#8B1A1A", "#a32626"),
        "empty": ("#1c1c1c", "rgba(232,224,208,.22)"),
        "future": ("transparent", "transparent"),
    }

    def _cell(status, title, is_today=False):
        fill, border = cell_colors.get(status, cell_colors["empty"])
        outline = "outline:1px solid #E8E0D0;outline-offset:1px;" if is_today else ""
        return (
            f'<span title="{html.escape(title)}" style="'
            f"width:13px;height:13px;border-radius:3px;display:inline-block;"
            f"background:{fill};border:1px solid {border};{outline}"
            f'"></span>'
        )

    grid = (
        f'<div style="display:grid;gap:3px;align-items:center;'
        f'grid-template-columns:16px repeat({cols}, 13px);margin:4px 0 8px 0;">'
    )
    parts = [
        '<div style="margin:8px 0 14px 0;">',
        '<div style="display:flex;gap:12px;flex-wrap:wrap;font-size:11px;color:#cfc6b4;margin:0 0 8px 0;">',
        '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;background:#C9A84C;vertical-align:middle;"></span>At target</span>',
        '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;background:#8B1A1A;vertical-align:middle;"></span>Short</span>',
        '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;background:#1c1c1c;border:1px solid rgba(232,224,208,.3);vertical-align:middle;"></span>No log</span>',
        "</div>",
        grid,
        "<span></span>",
    ]
    for w in range(cols):
        monday = start + timedelta(weeks=w)
        label = f"{monday.month}/{monday.day}" if w % 2 == 0 or w == cols - 1 else ""
        parts.append(
            f'<span style="font-size:9px;color:#9a917f;text-align:center;line-height:1;">{html.escape(label)}</span>'
        )
    weekday_names = ["M", "T", "W", "T", "F", "S", "S"]
    for wd, name in enumerate(weekday_names):
        parts.append(f'<span style="font-size:9px;color:#9a917f;letter-spacing:.4px;">{name}</span>')
        for w in range(cols):
            d = start + timedelta(weeks=w, days=wd)
            rec = by_day.get(d)
            if d > today:
                parts.append(_cell("future", d.isoformat(), False))
            elif rec is None:
                parts.append(_cell("empty", f"{d.isoformat()}: no log", d == today))
            elif rec.get("logged"):
                status = rec.get("status") or "miss"
                title = f"{d.isoformat()}: {float(rec['deficit']):,.0f} kcal"
                parts.append(_cell(status, title, d == today))
            else:
                parts.append(_cell("empty", f"{d.isoformat()}: no log", d == today))
    parts.append("</div></div>")
    return "".join(parts)


def _deficit_chart_theme(chart):
    return (
        chart.configure(background="transparent")
        .configure_view(strokeWidth=0, fill="transparent")
        .configure_axis(
            labelColor="#E8E0D0",
            titleColor="#C9A84C",
            gridColor="rgba(201,168,76,0.12)",
            domainColor="rgba(232,224,208,0.25)",
            tickColor="rgba(232,224,208,0.25)",
            labelFontSize=11,
            titleFontSize=12,
        )
        .configure_legend(
            labelColor="#E8E0D0",
            titleColor="#C9A84C",
            orient="top",
        )
    )


def render_deficit_pace_visuals(hist, settings, fc=None, key_prefix="defvis", live=None):
    """Day grid, daily bars, weekly bars, and cumulative deficit vs the planned target."""
    fc = fc or {}
    live = live or {}
    today = date.today()
    daily, weekly, target = build_deficit_tracking_frame(
        hist,
        settings,
        fc=fc,
        today=today,
        live_today_deficit=live.get("preview_deficit"),
    )
    if daily.empty or not daily["logged"].any():
        st.caption("Log Oura burn and FatSecret intake to chart deficit vs target.")
        return

    stats = deficit_hit_stats(daily, weekly, today=today)
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Days at target (7d)", f"{stats['days_hit_7']}/7")
    weeks_logged = stats["weeks_logged"]
    h2.metric(
        "Weeks at target",
        f"{stats['weeks_hit']}/{weeks_logged}" if weeks_logged else "—",
    )
    h3.metric("Streak", f"{stats['streak']} day" if stats["streak"] == 1 else f"{stats['streak']} days")
    vs_plan = stats["vs_plan"]
    h4.metric(
        "Cumulative vs plan",
        ("+" if vs_plan is not None and vs_plan >= 0 else "") + _fmt_kcal(vs_plan),
        help="Actual running deficit minus planned (target × logged days since DEXA).",
    )
    st.caption(
        f"A day counts as **at target** at ≥{DEFICIT_TARGET_HIT_FRACTION:.0%} of "
        f"**{target:,.0f} kcal** ({deficit_target_threshold(target):,.0f} kcal). "
        f"A week counts when the **average logged day** that week is at target. "
        f"The plan line is target × **logged** days (unlogged days stay gray, not short). "
        f"Gold = hit · crimson = short."
    )

    heat_col, week_col = st.columns([1.15, 1.0])
    with heat_col:
        st.markdown("**Days at target**")
        st.markdown(deficit_heatmap_html(daily, today=today, weeks=12), unsafe_allow_html=True)
    with week_col:
        st.markdown("**Weekly deficit**")
        week_plot = weekly.tail(12).copy()
        if week_plot.empty or not week_plot["logged_days"].any():
            st.caption("Not enough weeks logged yet.")
        else:
            week_plot["Deficit"] = week_plot["deficit"]
            bars = (
                alt.Chart(week_plot)
                .mark_bar(size=18, cornerRadiusEnd=2)
                .encode(
                    x=alt.X("week_ts:T", title=None, axis=alt.Axis(format="%b %d")),
                    y=alt.Y("Deficit:Q", title="kcal"),
                    color=alt.Color(
                        "status:N",
                        scale=alt.Scale(
                            domain=["hit", "miss", "empty"],
                            range=["#C9A84C", "#8B1A1A", "#3a3a3a"],
                        ),
                        legend=None,
                    ),
                    tooltip=[
                        alt.Tooltip("week_start:T", title="Week of"),
                        alt.Tooltip("deficit:Q", title="Deficit", format=",.0f"),
                        alt.Tooltip("week_target:Q", title="Target", format=",.0f"),
                        alt.Tooltip("hit_days:Q", title="Days at target"),
                        alt.Tooltip("logged_days:Q", title="Days logged"),
                    ],
                )
            )
            rule = (
                alt.Chart(pd.DataFrame({"y": [float(target) * 7]}))
                .mark_rule(strokeDash=[4, 3], color="#E8E0D0", strokeWidth=1.2)
                .encode(y="y:Q")
            )
            st.altair_chart(_deficit_chart_theme(bars + rule).properties(height=168), width="stretch")

    st.markdown("**Daily deficit**")
    day_plot = daily.tail(28).copy()
    day_plot = day_plot[day_plot["logged"]]
    if day_plot.empty:
        st.caption("No logged deficit days in the last 4 weeks.")
    else:
        bars = (
            alt.Chart(day_plot)
            .mark_bar(size=8, cornerRadiusEnd=1)
            .encode(
                x=alt.X("day_ts:T", title=None, axis=alt.Axis(format="%b %d")),
                y=alt.Y("deficit:Q", title="kcal"),
                color=alt.Color(
                    "status:N",
                    scale=alt.Scale(domain=["hit", "miss"], range=["#C9A84C", "#8B1A1A"]),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("day:T", title="Day"),
                    alt.Tooltip("deficit:Q", title="Deficit", format=",.0f"),
                    alt.Tooltip("target:Q", title="Target", format=",.0f"),
                ],
            )
        )
        rule = (
            alt.Chart(pd.DataFrame({"y": [target]}))
            .mark_rule(strokeDash=[4, 3], color="#E8E0D0", strokeWidth=1.2)
            .encode(y="y:Q")
        )
        st.altair_chart(_deficit_chart_theme(bars + rule).properties(height=180), width="stretch")

    st.markdown("**Cumulative deficit vs plan**")
    cum_plot = daily.copy()
    cum_long = cum_plot.melt(
        id_vars=["day_ts"],
        value_vars=["cumulative", "planned_cumulative"],
        var_name="series",
        value_name="kcal",
    )
    cum_long["series"] = cum_long["series"].map(
        {"cumulative": "Actual", "planned_cumulative": "Plan (target × days)"}
    )
    line = (
        alt.Chart(cum_long)
        .mark_line(strokeWidth=2.4)
        .encode(
            x=alt.X("day_ts:T", title=None, axis=alt.Axis(format="%b %d")),
            y=alt.Y("kcal:Q", title="kcal"),
            color=alt.Color(
                "series:N",
                scale=alt.Scale(
                    domain=["Actual", "Plan (target × days)"],
                    range=["#C9A84C", "#E8E0D0"],
                ),
                legend=alt.Legend(title=None),
            ),
            strokeDash=alt.StrokeDash(
                "series:N",
                scale=alt.Scale(
                    domain=["Actual", "Plan (target × days)"],
                    range=[[], [4, 3]],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("day_ts:T", title="Day"),
                alt.Tooltip("series:N", title=""),
                alt.Tooltip("kcal:Q", title="kcal", format=",.0f"),
            ],
        )
    )
    st.altair_chart(_deficit_chart_theme(line).properties(height=200), width="stretch")
    if vs_plan is not None:
        if vs_plan >= 0:
            st.caption(
                f"Ahead of the daily target plan by **{vs_plan:,.0f} kcal** "
                f"(actual **{stats['cumulative']:,.0f}** vs plan **{stats['planned']:,.0f}**)."
            )
        else:
            st.caption(
                f"Behind the daily target plan by **{abs(vs_plan):,.0f} kcal** "
                f"(actual **{stats['cumulative']:,.0f}** vs plan **{stats['planned']:,.0f}**)."
            )


def compute_avg_daily_weight_loss(hist, lookback_days=30):
    """Average daily scale loss (positive = down). Uses span between first and last weigh-in."""
    if hist is None or hist.empty or "weight_lbs" not in hist.columns:
        return None, 0
    w = hist.dropna(subset=["weight_lbs"]).copy()
    w = w[pd.to_numeric(w["weight_lbs"], errors="coerce") > 0]
    if w.empty:
        return None, 0
    w = w.sort_values("log_date")
    if lookback_days:
        cutoff = pd.Timestamp(date.today() - timedelta(days=int(lookback_days)))
        w = w[w["log_date"] >= cutoff]
    if len(w) < 2:
        return None, int(len(w))
    first = float(w.iloc[0]["weight_lbs"])
    last = float(w.iloc[-1]["weight_lbs"])
    span_days = max(1, int((w.iloc[-1]["log_date"] - w.iloc[0]["log_date"]).days))
    return (first - last) / span_days, span_days


def count_workouts_in_days(hist, lookback_days=7, today=None):
    today = today or date.today()
    if hist is None or hist.empty or "workout" not in hist.columns:
        return 0
    df = hist.copy()
    df["day"] = pd.to_datetime(df["log_date"]).dt.date
    window = df[df["day"] >= today - timedelta(days=lookback_days - 1)]
    if window.empty:
        return 0
    return int(window["workout"].map(is_training_workout).sum())


def average_sleep_score(hist, lookback_days=7, today=None):
    today = today or date.today()
    if hist is None or hist.empty or "sleep_score" not in hist.columns:
        return None
    df = hist.copy()
    df["day"] = pd.to_datetime(df["log_date"]).dt.date
    window = df[df["day"] >= today - timedelta(days=lookback_days - 1)]
    scores = pd.to_numeric(window.get("sleep_score"), errors="coerce").dropna()
    scores = scores[scores > 0]
    if scores.empty:
        return None
    return float(scores.mean())


def analyze_cut_adjustments(hist, settings, current_weight=None, goal_weight=None):
    """Coach when scale disagrees with deficit — muscle gain from 5–6× training, or poor sleep."""
    suggestions = []
    if hist is None or hist.empty:
        return suggestions

    today = date.today()
    rollups = compute_deficit_rollups(hist, today)
    week_def = rollups["weekly"]
    avg_daily_def = rollups["avg_daily"]
    workouts_7 = count_workouts_in_days(hist, 7, today)
    workouts_14 = count_workouts_in_days(hist, 14, today)
    sleep_avg = average_sleep_score(hist, 7, today)
    sleep_label = sleep_quality_from_score(sleep_avg) if sleep_avg is not None else None
    loss_per_day, _loss_span = compute_avg_daily_weight_loss(hist, lookback_days=14)
    expected_fat_week = (week_def / KCAL_PER_LB_FAT) if week_def and week_def > 0 else None
    actual_week_loss = (loss_per_day * 7.0) if loss_per_day is not None else None
    training_volume = True  # program is 5–6 sessions/week even if this week's log is incomplete
    real_week_deficit = week_def is not None and week_def >= 1500

    if training_volume and real_week_deficit and expected_fat_week is not None and actual_week_loss is not None:
        gap = expected_fat_week - actual_week_loss
        if gap >= 0.25:
            suggestions.append(
                {
                    "kind": "mass_gain",
                    "level": "info",
                    "title": "Scale may be hiding fat loss — training looks like mass gain",
                    "body": (
                        f"Plan is **{EXPECTED_WEEKLY_WORKOUTS[0]}–{EXPECTED_WEEKLY_WORKOUTS[1]} workouts/week** "
                        f"(logged **{workouts_7}** this week, **{workouts_14}** in 14 days). "
                        f"Calorie math says ~**{expected_fat_week:.2f} lb** of fat from this week's deficit, "
                        f"but the scale moved about **{actual_week_loss:+.2f} lb**. "
                        f"That **{gap:.1f} lb** gap is often glycogen, water, and lean mass from lifting — "
                        f"not a failed cut. Don't slash calories. Keep the deficit, watch waist/photos, "
                        f"and treat the scale as lagging while you train this often."
                    ),
                }
            )

    if sleep_label in ("Poor", "Fair"):
        slow_note = ""
        if expected_fat_week is not None and actual_week_loss is not None and actual_week_loss < expected_fat_week * 0.7:
            slow_note = (
                f" Fat-loss pace is also slower than the deficit predicts "
                f"(~{actual_week_loss:.2f} lb vs ~{expected_fat_week:.2f} lb expected). "
            )
        suggestions.append(
            {
                "kind": "sleep",
                "level": "warning",
                "title": "Poor sleep will slow the cut",
                "body": (
                    f"Recent sleep has been **{sleep_label}**"
                    f"{f' (avg score {sleep_avg:.0f})' if sleep_avg is not None else ''}. "
                    f"Bad sleep drops NEAT, raises hunger, and can slow fat loss ~15–25% even in a real deficit. "
                    f"{slow_note}"
                    f"With **{EXPECTED_WEEKLY_WORKOUTS[0]}–{EXPECTED_WEEKLY_WORKOUTS[1]} workouts/week**, "
                    f"fix sleep before adding more deficit. Aim for **Good** or **Excellent** recovery nights."
                ),
            }
        )

    if not suggestions and avg_daily_def is not None and avg_daily_def > 150:
        goal = float(goal_weight if goal_weight is not None else goal_weight_lbs(settings))
        current = float(current_weight or settings.get("current_weight_lbs") or 0)
        remaining = remaining_cut_to_goal(current, goal)
        if remaining["kcal_remaining"] > 0 and avg_daily_def > 0:
            days_eta = remaining["kcal_remaining"] / avg_daily_def
            suggestions.append(
                {
                    "kind": "on_track",
                    "level": "success",
                    "title": "Deficit is doing the work",
                    "body": (
                        f"Average **{avg_daily_def:.0f} kcal/day** deficit. "
                        f"**{remaining['lbs_remaining']:.1f} lb** (~{remaining['kcal_remaining']:,.0f} kcal) "
                        f"to **{goal:.0f} lb**. At this pace, about **{days_eta:.0f} days** "
                        f"if sleep stays solid and training doesn't add much scale weight."
                    ),
                }
            )
    return suggestions


def historical_steps_average(daily, lookback_days=14):
    if daily.empty or "steps" not in daily.columns:
        return None
    df = daily.dropna(subset=["steps"]).copy()
    df = df[df["steps"] > 0]
    if lookback_days:
        cutoff = pd.Timestamp(date.today() - timedelta(days=int(lookback_days)))
        df = df[df["log_date"] >= cutoff]
    if df.empty:
        return None
    return float(df["steps"].mean())


def resolve_fat_loss_week(daily, settings, fat_fraction):
    """Pick the best available fat-loss rate from history."""
    min_days = int(settings.get("min_trend_days") or 14)
    tr = trend_rate(daily, min_days) if not daily.empty else None
    if tr and tr["weight_loss_lbs_week"] > 0:
        rate = tr["weight_loss_lbs_week"] * fat_fraction
        return rate, "weight_trend", {
            "weight_loss_lbs_week": tr["weight_loss_lbs_week"],
            "r2": tr.get("r2"),
            "n": tr.get("n"),
        }

    avg_def = compute_historical_average_deficit(daily, settings, lookback_days=30)
    if avg_def is not None and avg_def > 25:
        cal = load_composition_calibration()
        kcal_per_lb = float(cal.get("kcal_per_lb_fat") or 3500.0)
        rate = avg_def * 7 / kcal_per_lb * fat_fraction
        if rate > 0:
            return rate, "avg_deficit", {"avg_deficit_kcal": avg_def}

    cal = load_composition_calibration()
    kcal_per_lb = float(cal.get("kcal_per_lb_fat") or 3500.0)
    target = float(settings.get("target_deficit") or 500)
    rate = target * 7 / kcal_per_lb * fat_fraction
    return rate, "target_deficit", {"target_deficit_kcal": target}


def forecast_source_label(fc):
    source = fc.get("forecast_source") or "target_deficit"
    meta = fc.get("forecast_source_meta") or {}
    if source == "cumulative_deficit":
        avg = meta.get("avg_deficit_kcal")
        days = meta.get("logged_days")
        if avg is not None and days:
            return f"Cumulative deficit since DEXA ({avg:.0f} kcal/day over {int(days)} days)"
        if avg is not None:
            return f"Cumulative deficit since DEXA ({avg:.0f} kcal/day)"
        return "Cumulative deficit since DEXA"
    if source == "weight_trend":
        wk = meta.get("weight_loss_lbs_week")
        if wk is not None:
            return f"Weight trend ({wk:.2f} lb/wk scale loss)"
    if source == "avg_deficit":
        avg = meta.get("avg_deficit_kcal")
        if avg is not None:
            return f"Avg deficit history ({avg:.0f} kcal/day)"
    return "Target deficit plan"


def trend_rate(df, min_days=14):
    data = df.dropna(subset=["weight_lbs"]).copy()
    if len(data) < min_days:
        return None
    data = data.tail(max(int(min_days), min(len(data), 60)))
    data["x"] = (data["log_date"] - data["log_date"].min()).dt.days
    if data["x"].nunique() < 3:
        return None
    slope, intercept, r, p, se = stats.linregress(data["x"], data["weight_lbs"])
    return {
        "weight_loss_lbs_week": -slope * 7,
        "slope": slope,
        "intercept": intercept,
        "r2": r*r,
        "n": len(data),
        "start_date": data["log_date"].min(),
        "end_date": data["log_date"].max(),
    }


def latest_dexa_or_settings(dexa, s):
    if not dexa.empty:
        r = dexa.iloc[-1]
        return {
            "date": r["scan_date"].date(),
            "weight": float(r["weight_lbs"]),
            "bf": float(r["body_fat_pct"]),
            "fat_mass": float(r["fat_mass_lbs"]),
            "lean_mass": float(r["lean_mass_lbs"]),
        }
    w = s["current_weight_lbs"]
    bf = s["current_body_fat_pct"]
    return {"date": None, "weight": w, "bf": bf, "fat_mass": w*bf/100, "lean_mass": w*(1-bf/100)}


def forecast_goal(daily, dexa, s):
    """Goal date and body-fat progress from DEXA + cumulative (Oura − FatSecret) deficit."""
    anchor = latest_dexa_or_settings(dexa, s)
    comp = estimate_current_composition(daily, dexa, s)
    current_weight = comp["current_weight"]
    current_fat = comp["current_fat_mass"]
    current_lean = comp["current_lean_mass"]
    current_bf = comp["current_bf"]
    goal_bf_pct = float(s.get("goal_body_fat_pct") or 10.0)
    target_weight = goal_weight_from_lean(current_lean, goal_bf_pct)
    target_fat = goal_fat_mass_lbs(current_lean, goal_bf_pct)
    fat_to_lose = max(0.0, current_fat - target_fat)
    kcal_to_goal = fat_to_lose * KCAL_PER_LB_FAT
    cumulative = float(comp.get("cumulative_deficit_kcal") or 0)
    logged_days = int(comp.get("logged_deficit_days") or 0)

    avg_def = None
    if logged_days > 0:
        avg_def = cumulative / logged_days
    planned_def = float(s.get("target_deficit") or 500)
    if avg_def is not None and avg_def > 25:
        pace = avg_def
        forecast_source = "cumulative_deficit"
        forecast_meta = {"avg_deficit_kcal": avg_def, "logged_days": logged_days}
    elif avg_def is not None:
        pace = None
        forecast_source = "cumulative_deficit"
        forecast_meta = {"avg_deficit_kcal": avg_def, "logged_days": logged_days}
    else:
        pace = planned_def if planned_def > 0 else None
        forecast_source = "target_deficit"
        forecast_meta = {"target_deficit_kcal": planned_def}

    days_est = None
    weeks = None
    if kcal_to_goal <= 0:
        days_est = 0.0
        weeks = 0.0
    elif pace and pace > 0:
        days_est = kcal_to_goal / pace
        weeks = days_est / 7.0

    fat_loss_week = (pace * 7 / KCAL_PER_LB_FAT) if pace and pace > 0 else 0.0
    today = date.today()
    goal_date = today + timedelta(days=int(round(days_est))) if days_est is not None else None
    tr = trend_rate(daily, int(s["min_trend_days"])) if not daily.empty else None
    original_fat_to_lose = fat_to_lose_to_goal_bf(anchor["lean_mass"], anchor["fat_mass"], goal_bf_pct)
    original_kcal = original_fat_to_lose * KCAL_PER_LB_FAT
    if original_kcal <= 0:
        kcal_progress = 1.0
    else:
        kcal_progress = max(0.0, min(1.0, cumulative / original_kcal))

    return anchor, {
        "current_weight": current_weight,
        "current_fat_mass": current_fat,
        "current_lean_mass": current_lean,
        "current_bf": current_bf,
        "fat_to_lose": fat_to_lose,
        "target_weight": target_weight,
        "target_fat_mass": target_fat,
        "fat_loss_week": fat_loss_week,
        "weeks": weeks,
        "days": days_est,
        "goal_date": goal_date,
        "trend": tr,
        "forecast_source": forecast_source,
        "forecast_source_meta": forecast_meta,
        "composition_method": comp.get("estimation_method"),
        "composition_anchor": comp.get("anchor_label"),
        "calibration_intervals": comp.get("calibration_intervals"),
        "annual_lean_gain_lbs": 0.0,
        "projected_lean_gain_lbs": 0.0,
        "lean_at_goal": current_lean,
        "strong_lean_available": strong_lean_gain_available(),
        "cumulative_deficit_kcal": cumulative,
        "kcal_to_goal": kcal_to_goal,
        "kcal_progress": kcal_progress,
        "avg_daily_deficit": avg_def if avg_def is not None else pace,
        "logged_deficit_days": logged_days,
        "scale_weight": comp.get("scale_weight"),
        "scale_date": comp.get("scale_date"),
        "goal_body_fat_pct": goal_bf_pct,
        "original_kcal_to_goal": original_kcal,
        "dexa_date": anchor.get("date"),
    }


MUSCLE_GAIN_FRACTION_BY_MISSION = {
    "muscle_gain": 0.60,
    "strength_gain": 0.50,
}


def lean_mass_fraction_for_weight_change(settings, weight_delta):
    """How scale weight change splits into lean vs fat based on mission direction."""
    cal = load_composition_calibration()
    lean_frac, _fat_frac = effective_composition_fractions(
        settings, cal, weight_delta, metrics=None
    )
    return lean_frac


def estimate_current_composition(daily, dexa, settings, as_of=None):
    """Estimate current fat and lean mass from DEXA anchor + calibrated model."""
    anchor = latest_dexa_or_settings(dexa, settings)
    comp = estimate_composition_from_anchor(anchor, daily, settings, as_of=as_of)
    return {
        "current_weight": comp["current_weight"],
        "current_fat_mass": comp["current_fat_mass"],
        "current_lean_mass": comp["current_lean_mass"],
        "current_bf": comp["current_bf"],
        "weight_delta": comp["weight_delta"],
        "lean_fraction": comp["lean_fraction"],
        "fat_fraction": comp.get("fat_fraction"),
        "anchor_label": comp["anchor_label"],
        "estimation_method": comp.get("estimation_method"),
        "calibration_intervals": comp.get("calibration_intervals"),
        "cumulative_deficit_kcal": float(comp.get("cumulative_deficit_kcal") or 0),
        "logged_deficit_days": int(comp.get("logged_deficit_days") or 0),
        "scale_weight": comp.get("scale_weight"),
        "scale_date": comp.get("scale_date"),
    }


def _daily_row_is_resistance_day(row):
    workout = str(row.get("workout") or "").lower()
    if any(tag in workout for tag in ("workout a", "workout b", "workout c")):
        return True
    if "stair" in workout or "legs" in workout:
        return True
    notes = str(row.get("notes") or "").lower()
    return "[workout]" in notes or "workout" in notes


def compute_muscle_gain_analysis(daily, dexa, settings):
    """
    Estimate lean mass gain using weight trend, FatSecret intake, and workout logs.
    Best on muscle_gain / strength_gain missions; still usable if user tracks all three.
    """
    mode = get_mission_mode()
    if mode not in ("muscle_gain", "strength_gain"):
        return None

    comp = estimate_current_composition(daily, dexa, settings)
    lookback = max(int(settings.get("min_trend_days") or 14), 14)
    protein_target = float(settings.get("protein_target_g") or 190)
    target_surplus = abs(float(settings.get("target_deficit") or 0)) if float(settings.get("target_deficit") or 0) < 0 else 200.0

    if daily.empty:
        return {
            **comp,
            "current_lean_lbs": comp["current_lean_mass"],
            "lean_gain_period_lbs": 0.0,
            "lean_gain_lbs_week": 0.0,
            "lookback_days": lookback,
            "training_days": 0,
            "protein_adherence_pct": None,
            "surplus_adherence_pct": None,
            "effective_lean_fraction": comp["lean_fraction"],
            "trend_r2": None,
            "summary": "Log weight, FatSecret, and workouts to estimate lean mass gain.",
            "anchor_label": comp["anchor_label"],
        }

    df = daily.copy().sort_values("log_date")
    cutoff = pd.Timestamp(date.today()) - pd.Timedelta(days=lookback)
    window = df[df["log_date"] >= cutoff]
    if window.empty:
        window = df.tail(lookback)

    training_days = int(sum(1 for _, row in window.iterrows() if _daily_row_is_resistance_day(row)))

    protein_rows = window[window["protein_g"].notna() & (window["protein_g"] > 0)]
    protein_adherence_pct = None
    if not protein_rows.empty:
        hits = (protein_rows["protein_g"] >= protein_target * 0.9).sum()
        protein_adherence_pct = 100.0 * float(hits) / float(len(protein_rows))

    cal_rows = window[window["calories"].notna() & (window["calories"] > 0)]
    surplus_adherence_pct = None
    if not cal_rows.empty:
        baseline = float(settings.get("baseline_maintenance") or 2700)
        step_rate = float(settings.get("step_calories_per_1000") or 45)
        surplus_hits = 0
        for _, row in cal_rows.iterrows():
            steps = float(row.get("steps") or settings.get("default_step_goal") or 12000)
            maint = baseline + steps / 1000.0 * step_rate
            if float(row["calories"]) - maint >= target_surplus * 0.45:
                surplus_hits += 1
        surplus_adherence_pct = 100.0 * surplus_hits / float(len(cal_rows))

    tr = trend_rate(df, lookback)
    trend_r2 = float(tr["r2"]) if tr else None
    weight_gain_week = (-float(tr["weight_loss_lbs_week"]) if tr else 0.0)

    weight_series = window["weight_lbs"].dropna()
    lean_gain_period = 0.0
    if len(weight_series) >= 2:
        period_delta = float(weight_series.iloc[-1]) - float(weight_series.iloc[0])
        lean_gain_period = period_delta * comp["lean_fraction"]

    effective_lean_fraction = float(comp["lean_fraction"])
    if protein_adherence_pct is not None:
        effective_lean_fraction *= 0.72 + 0.28 * (protein_adherence_pct / 100.0)
    if surplus_adherence_pct is not None:
        effective_lean_fraction *= 0.78 + 0.22 * (surplus_adherence_pct / 100.0)
    if training_days > 0:
        effective_lean_fraction *= min(1.12, 0.82 + training_days / 10.0)
    effective_lean_fraction = max(0.20, min(0.85, effective_lean_fraction))

    lean_gain_week = max(0.0, weight_gain_week * effective_lean_fraction)

    parts = []
    if weight_gain_week > 0.05:
        parts.append(f"Scale up ~{weight_gain_week:.2f} lb/wk")
        parts.append(f"≈{lean_gain_week:.2f} lb/wk lean (est.)")
    elif weight_gain_week < -0.05:
        parts.append(f"Scale down ~{abs(weight_gain_week):.2f} lb/wk — check surplus")
    else:
        parts.append("Weight trend flat — increase surplus or training consistency")

    if protein_adherence_pct is not None and protein_adherence_pct < 70:
        parts.append(f"protein low ({protein_adherence_pct:.0f}% of days on target)")
    if surplus_adherence_pct is not None and surplus_adherence_pct < 60:
        parts.append(f"surplus low ({surplus_adherence_pct:.0f}% of days)")
    if training_days < 2:
        parts.append("few resistance sessions logged")

    return {
        "current_lean_lbs": comp["current_lean_mass"],
        "lean_gain_period_lbs": lean_gain_period,
        "lean_gain_lbs_week": lean_gain_week,
        "lookback_days": lookback,
        "training_days": training_days,
        "protein_adherence_pct": protein_adherence_pct,
        "surplus_adherence_pct": surplus_adherence_pct,
        "effective_lean_fraction": effective_lean_fraction,
        "trend_r2": trend_r2,
        "weight_gain_lbs_week": weight_gain_week,
        "summary": " · ".join(parts) + ".",
        "anchor_label": comp["anchor_label"],
    }






IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
INBOX_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}
IMAGE_QUEUE_TYPES = {"FatSecret", "Oura", "DEXA", "Workout", "Scale", "Apple Health Weight"}
FILENAME_CLASSIFIED_TYPES = {
    "DEXA", "Oura", "Oura Export", "FatSecret", "Workout", "Scale", "Apple Health Weight",
    "Strong CSV", "FatSecret CSV", "Apple Health XML",
}

OURA_ACTIVITY_KEYWORDS = [
    "total burn", "activity burn", "goal progress", "training frequency",
    "training volume", "recovery time", "edit activity goal", "activity time",
    "key metrics", "activities", "walking",
]

OURA_SLEEP_KEYWORDS = [
    "sleep score", "readiness", "readiness score", "total sleep", "sleep contributors",
    "deep sleep", "rem sleep", "sleep stages", "resting heart rate",
    "heart rate variability", "hrv", "bedtime", "wake-up time", "time in bed",
    "sleep balance", "sleep timing",
]

OURA_SLEEP_LABEL_SPECS = [
    ("sleep_score", [
        re.compile(r"SLEEP\s+SCORE", re.I),
        re.compile(r"SLEEP\s+CONTRIBUTORS", re.I),
    ]),
    ("readiness_score", [
        re.compile(r"READINESS", re.I),
        re.compile(r"RECOVERY", re.I),
    ]),
    ("sleep_minutes", [
        re.compile(r"TOTAL\s+SLEEP", re.I),
        re.compile(r"TIME\s+IN\s+BED", re.I),
        re.compile(r"SLEEP\s+TIME", re.I),
    ]),
]

OURA_ACTIVITY_LABEL_SPECS = [
    ("oura_burn", [
        re.compile(r"TOTAL\s+BURN", re.I),
        re.compile(r"T[O0Q][T7]?[AaLl1]+\s+B[UUV][RPN][N1M]?", re.I),
    ]),
    ("active_energy", [
        re.compile(r"ACTIVITY\s+BURN", re.I),
        re.compile(r"ACT[1I]?V[1I]?[T7][YV]?\s+B[UUV][RPN][N1M]?", re.I),
    ]),
    ("oura_activity_time_min", [
        re.compile(r"ACTIVITY\s+TIME", re.I),
        re.compile(r"ACT[1I]?V[1I]?[T7][YV]?\s+T[1I][Mm][E3]?", re.I),
    ]),
    ("oura_goal_progress", [
        re.compile(r"GOAL\s+PROGRESS", re.I),
        re.compile(r"G[O0Q][Aa][Ll1]\s+P[RPN][O0Q][Gg][RPN][E3][Ss5][Ss5]?", re.I),
    ]),
]

OURA_VALIDATION_STEPS = [
    {"key": "log_date", "label": "Log date", "widget": "date"},
    {
        "key": "oura_burn",
        "label": "Total burn (kcal)",
        "widget": "number",
        "help": "TOTAL BURN — used for deficit calculations",
    },
    {
        "key": "active_energy",
        "label": "Activity burn (kcal)",
        "widget": "number",
        "help": "ACTIVITY BURN — exercise calories only",
    },
    {"key": "oura_activity_time_min", "label": "Activity time (minutes)", "widget": "number"},
    {
        "key": "oura_goal_progress",
        "label": "Goal progress",
        "widget": "text",
        "placeholder": "8 / 10",
    },
    {"key": "sleep_score", "label": "Sleep score", "widget": "number"},
    {"key": "readiness_score", "label": "Readiness score", "widget": "number"},
    {"key": "sleep_minutes", "label": "Sleep minutes", "widget": "number"},
]

OCR_TERMINAL_STATUSES = frozenset({"imported", "skipped"})
OCR_WIZARD_TYPES = IMAGE_QUEUE_TYPES
OCR_CLEAN_CONFIRMATIONS_TO_TRUST = 1

OCR_VALIDATION_STEPS = {
    "FatSecret": [
        {"key": "log_date", "label": "Log date", "widget": "date"},
        {"key": "calories", "label": "Calories", "widget": "number", "help": "Cals — day summary total"},
        {"key": "protein_g", "label": "Protein (g)", "widget": "number", "help": "Prot"},
        {"key": "carbs_g", "label": "Net carbs (g)", "widget": "number", "help": "Net C"},
        {"key": "fat_g", "label": "Fat (g)", "widget": "number"},
        {"key": "fiber_g", "label": "Fiber (g)", "widget": "number"},
        {"key": "sodium_mg", "label": "Sodium (mg)", "widget": "number", "help": "Sod"},
    ],
    "Oura": OURA_VALIDATION_STEPS,
    "DEXA": [
        {"key": "scan_date", "label": "Scan date", "widget": "date"},
        {"key": "weight_lbs", "label": "Weight", "widget": "mass_unit", "step": 0.1,
         "help": "Patient weight or Total Mass from the DXA Results Summary."},
        {"key": "body_fat_pct", "label": "Body fat %", "widget": "number", "step": 0.1,
         "help": "Total / whole-body % Fat from the DXA Results Summary table."},
        {"key": "fat_mass_lbs", "label": "Fat mass", "widget": "mass_unit", "step": 0.1,
         "help": "Fat Mass column on the report — usually grams on FITLAB/Hologic scans."},
        {"key": "lean_mass_lbs", "label": "Lean + BMC", "widget": "mass_unit", "step": 0.1,
         "help": "Lean + BMC column on the report — usually grams on FITLAB/Hologic scans."},
        {"key": "vat_mass_g", "label": "VAT mass (g)", "widget": "number",
         "help": "Estimated VAT mass — already in grams on the report."},
    ],
    "Workout": [
        {"key": "log_date", "label": "Log date", "widget": "date"},
        {"key": "workout", "label": "Workout name", "widget": "text", "placeholder": "Push / Pull / Legs"},
        {"key": "active_energy", "label": "Observed burn (kcal)", "widget": "number"},
        {"key": "workout_intensity", "label": "Intensity (1–10)", "widget": "number"},
    ],
    "Scale": [
        {"key": "log_date", "label": "Log date", "widget": "date"},
        {"key": "weight_lbs", "label": "Weight (lbs)", "widget": "number", "step": 0.1},
    ],
    "Apple Health Weight": [
        {"key": "log_date", "label": "Log date", "widget": "date"},
        {"key": "weight_lbs", "label": "Weight (lbs)", "widget": "number", "step": 0.1},
    ],
}

OCR_TEXT_FIELD_KEYS = {"oura_goal_progress", "workout", "scan_date", "log_date"}
OCR_DATE_FIELD_KEYS = {"log_date", "scan_date"}
MASS_UNIT_OPTIONS = ("g", "kg", "lb")
DEXA_MASS_UNIT_FIELDS = {
    "weight_lbs": {"gram_key": "total_mass_g", "default_unit": "g"},
    "fat_mass_lbs": {"gram_key": "fat_mass_g", "default_unit": "g"},
    "lean_mass_lbs": {"gram_key": "lean_bmc_g", "default_unit": "g"},
}
WORKOUT_STRONG_KEYWORDS = [
    "strong", "sets", "reps", "bench press", "squat", "deadlift", "1rm",
    "barbell", "dumbbell", "set 1", "set 2", "personal record", "lifting",
]
DEXA_STRONG_KEYWORDS = [
    "fitpal", "fitlab", "hologic", "body composition results", "body composition",
    "dxa results", "lean + bmc", "lean+ bmc", "whole body", "horizon wi",
    "total body % fat", "vat mass", "android", "gynoid", "scan type",
    "adipose indices", "lean indices", "scan date", "dexafit", "% fat",
]

CATEGORY_KEYWORDS = {
    "FatSecret": [
        "fatsecret", "food diary", "day summary", "net c", "prot", "cals", "calories",
        "protein", "carbs", "carbohydrate", "kcal", "nutrition", "macros", "food log",
        "remaining", "budget", "meal", "snack", "breakfast", "lunch", "dinner",
        "snacks/other", "snacks", "fiber", "sodium",
    ],
    "Oura": [
        "oura", "readiness", "sleep score", "activity score", "hrv", "resting heart rate",
        "heart rate variability", "recovery", "sleep contributors", "activity balance",
        "body temperature", "ring", "oura ring", "sleep stages", "deep sleep", "rem sleep",
        "total burn", "activity burn", "goal progress", "training frequency",
        "training volume", "recovery time", "edit activity goal", "activity time",
    ],
    "DEXA": [
        "hologic", "dxa", "dexa", "lean + bmc", "lean mass", "fat mass", "vat",
        "body composition results", "fitpal", "fitlab", "dexafit", "body fat %", "total body fat",
        "android", "gynoid", "bone mineral", "visceral adipose", "composition report",
        "whole body", "horizon wi", "scan type", "dxa results", "dxa results summary",
        "adipose indices", "scan date", "scan information", "% fat", "total mass",
    ],
    "Workout": [
        "strong", "workout", "sets", "reps", "volume", "1rm", "exercise",
        "bench press", "squat", "deadlift", "overhead", "barbell", "dumbbell", "set 1",
        "set 2", "duration", "personal record", "pr ", "lifting",
    ],
    "Scale": [
        "withings", "renpho", "eufy", "smart scale", "body+ ", "body scan",
        "weigh in", "weigh-in", "bmi", "muscle mass", "body water",
    ],
    "Apple Health Weight": [
        "all data", "measurements", "this month", "health", "browse",
    ],
}

def ensure_journey_table():
    c = conn()
    c.execute("""
        CREATE TABLE IF NOT EXISTS journey_start (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            start_date TEXT,
            start_days REAL,
            start_body_fat_pct REAL,
            start_weight_lbs REAL
        )
    """)
    for col, typ in [
        ("mission_mode", "TEXT"),
        ("start_metric", "REAL"),
        ("goal_metric", "REAL"),
        ("metric_type", "TEXT"),
        ("start_lean_lbs", "REAL"),
    ]:
        try:
            c.execute(f"ALTER TABLE journey_start ADD COLUMN {col} {typ}")
        except sqlite3.OperationalError:
            pass
    c.commit()
    c.close()


def _journey_row_to_dict(row, fc, settings):
    """Normalize journey_start row (legacy BF-only or mission-aware)."""
    if row is None:
        return None
    keys = [
        "start_date", "start_days", "start_body_fat_pct", "start_weight_lbs",
        "mission_mode", "start_metric", "goal_metric", "metric_type", "start_lean_lbs",
    ]
    data = {k: row[i] if i < len(row) else None for i, k in enumerate(keys)}
    mission = data.get("mission_mode") or "fat_loss"
    current_bf = float(fc.get("current_bf") or settings.get("current_body_fat_pct") or 0)
    current_weight = float(fc.get("current_weight") or settings.get("current_weight_lbs") or 0)
    if data.get("start_metric") is None:
        data["start_metric"] = float(data.get("start_body_fat_pct") or current_bf)
    if data.get("goal_metric") is None:
        data["goal_metric"] = float(settings.get("goal_body_fat_pct") or 10.0)
    if not data.get("metric_type"):
        data["metric_type"] = "bf_pct"
    data["mission_mode"] = mission
    data["start_days"] = float(data.get("start_days") or max(float(fc.get("days") or 1), 1.0))
    data["start_body_fat_pct"] = float(data.get("start_body_fat_pct") or current_bf)
    data["start_weight_lbs"] = float(data.get("start_weight_lbs") or current_weight)
    if data.get("start_lean_lbs") is not None:
        data["start_lean_lbs"] = float(data["start_lean_lbs"])
    return data


def metric_progress_frac(current, start, goal, increasing):
    span = abs(float(goal) - float(start))
    if span < 1e-6:
        return 0.0
    if increasing:
        return max(0.0, min(1.0, (float(current) - float(start)) / span))
    return max(0.0, min(1.0, (float(start) - float(current)) / span))


def estimate_weight_loss_days(current_w, goal_w, settings):
    deficit = float(settings.get("target_deficit") or 650)
    to_lose = max(0.0, float(current_w) - float(goal_w))
    if to_lose <= 0:
        return 0
    return int(max(1, round(to_lose / (deficit * 7.0 / 3500.0) * 7.0)))


def estimate_gain_mission_days(mission, current, goal, settings, daily, dexa):
    lookback = max(int(settings.get("min_trend_days") or 14), 14)
    rate = 0.0
    if daily is not None and not daily.empty:
        tr = trend_rate(daily, lookback)
        if tr:
            rate = max(0.0, -float(tr["weight_loss_lbs_week"]))
        if mission in ("muscle_gain", "strength_gain"):
            comp = estimate_current_composition(daily, dexa or pd.DataFrame(), settings)
            frac = lean_mass_fraction_for_weight_change(settings, rate)
            rate = rate * frac
            if mission == "strength_gain" and comp["current_lean_mass"] > 0:
                rate = rate / comp["current_lean_mass"] * 100.0
    remaining = max(0.0, float(goal) - float(current))
    if rate > 0.02 and remaining > 0:
        return int(max(28, round(remaining / rate * 7.0)))
    return 84 if mission == "muscle_gain" else 70


def format_journey_metric(metric_type, value, prefix=""):
    v = float(value)
    if metric_type == "bf_pct":
        return f"{v:.1f}%"
    if metric_type == "strength_pct":
        return f"+{v:.1f}%"
    if metric_type == "weight_lbs":
        return f"{v:.1f} lb"
    if metric_type == "lean_lbs":
        return f"{v:.1f} lb"
    return f"{v:.1f}"


def latest_dexa_journey_anchor(dexa, settings, fc=None):
    """DEXA scan values used as the default journey start anchor."""
    anchor = latest_dexa_or_settings(dexa, settings)
    start_date = anchor["date"] or date.today()
    return {
        "start_date": start_date,
        "start_body_fat_pct": float(anchor["bf"]),
        "start_weight_lbs": float(anchor["weight"]),
        "start_lean_lbs": float(anchor["lean_mass"]),
    }


def _coerce_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if hasattr(value, "date") and callable(value.date):
        try:
            return value.date()
        except Exception:
            pass
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def journey_total_days(start_date, goal_date, fallback_days=28):
    sd = _coerce_date(start_date)
    gd = _coerce_date(goal_date)
    if sd and gd:
        return max((gd - sd).days, 1)
    return max(int(round(float(fallback_days or 28))), 1)


def journey_elapsed_days(start_date, as_of=None):
    sd = _coerce_date(start_date)
    if not sd:
        return 0
    end = _coerce_date(as_of) or date.today()
    return max((end - sd).days, 0)


def compute_mission_seed(mission, fc, settings, daily=None, dexa=None, anchor_override=None):
    daily_df = daily if daily is not None else pd.DataFrame()
    dexa_df = dexa if dexa is not None else pd.DataFrame()
    anchor = dict(anchor_override or latest_dexa_journey_anchor(dexa_df, settings, fc))
    start_date = _coerce_date(anchor.get("start_date")) or date.today()
    start_bf = float(anchor.get("start_body_fat_pct") or settings.get("current_body_fat_pct") or 0)
    start_weight = float(anchor.get("start_weight_lbs") or settings.get("current_weight_lbs") or 0)
    start_lean = float(anchor.get("start_lean_lbs") or 0)
    if start_lean <= 0 and start_weight > 0 and start_bf > 0:
        start_lean = start_weight * (1.0 - start_bf / 100.0)

    goal_bf = float(settings.get("goal_body_fat_pct") or 10.0)
    goal_date = fc.get("goal_date") if fc else None
    start_days = journey_total_days(start_date, goal_date, fc.get("days") if fc else 28)

    if mission == "weight_loss":
        gw = goal_weight_lbs(settings, fc)
        return {
            "start_date": start_date.isoformat(),
            "start_days": float(start_days),
            "start_metric": start_weight,
            "goal_metric": gw,
            "metric_type": "weight_lbs",
            "start_lean_lbs": start_lean,
            "start_body_fat_pct": start_bf,
            "start_weight_lbs": start_weight,
        }
    if mission == "muscle_gain":
        goal = start_lean * (1.0 + MUSCLE_GAIN_TARGET_PCT / 100.0)
        return {
            "start_date": start_date.isoformat(),
            "start_days": float(start_days),
            "start_metric": start_lean,
            "goal_metric": goal,
            "metric_type": "lean_lbs",
            "start_lean_lbs": start_lean,
            "start_body_fat_pct": start_bf,
            "start_weight_lbs": start_weight,
        }
    if mission == "strength_gain":
        return {
            "start_date": start_date.isoformat(),
            "start_days": float(start_days),
            "start_metric": 0.0,
            "goal_metric": STRENGTH_GAIN_TARGET_PCT,
            "metric_type": "strength_pct",
            "start_lean_lbs": start_lean,
            "start_body_fat_pct": start_bf,
            "start_weight_lbs": start_weight,
        }
    return {
        "start_date": start_date.isoformat(),
        "start_days": float(start_days),
        "start_metric": start_bf,
        "goal_metric": goal_bf,
        "metric_type": "bf_pct",
        "start_lean_lbs": start_lean,
        "start_body_fat_pct": start_bf,
        "start_weight_lbs": start_weight,
    }


def save_journey_start_record(seed, mission):
    ensure_journey_table()
    c = conn()
    c.execute(
        """
        INSERT OR REPLACE INTO journey_start
        (id, start_date, start_days, start_body_fat_pct, start_weight_lbs,
         mission_mode, start_metric, goal_metric, metric_type, start_lean_lbs)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seed["start_date"],
            seed["start_days"],
            seed["start_body_fat_pct"],
            seed["start_weight_lbs"],
            mission,
            seed["start_metric"],
            seed["goal_metric"],
            seed["metric_type"],
            seed.get("start_lean_lbs"),
        ),
    )
    c.commit()
    c.close()


def reseed_journey_start(mission, fc, settings, daily=None, dexa=None, anchor_override=None):
    seed = compute_mission_seed(mission, fc, settings, daily, dexa, anchor_override=anchor_override)
    save_journey_start_record(seed, mission)
    return seed

def _milestone_value_label(metric_type, value):
    return format_journey_metric(metric_type, value)


def render_mission_milestones(milestone_x_fn, path_y_fn, mission, start_metric, goal_metric, metric_type, increasing):
    blocks = []
    items = []
    if mission == "fat_loss":
        items = [(v, l) for v, l in POMPEII_MILESTONES if v <= float(start_metric) + 0.05]
    elif mission == "weight_loss":
        span = float(start_metric) - float(goal_metric)
        items = [(float(start_metric) - span * frac, label) for frac, label in WEIGHT_ROAD_CHECKPOINTS]
    elif mission == "strength_gain":
        items = list(GAIN_ROAD_MILESTONES)
    else:
        span = float(goal_metric) - float(start_metric)
        items = [
            (float(start_metric) + span * 0.25, "Base"),
            (float(start_metric) + span * 0.50, "Mid"),
            (float(start_metric) + span * 0.75, "Push"),
        ]

    for val, label in items:
        if increasing and val < float(start_metric) - 0.001:
            continue
        if not increasing and val > float(start_metric) + 0.05:
            continue
        mx = milestone_x_fn(val)
        my = path_y_fn(mx)
        display = _milestone_value_label(metric_type, val)
        label_w = max(78, len(label) * 7 + 24)
        blocks.append(f"""
          <line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx:.1f}" y2="{my - 78:.1f}" stroke="{ROMAN_GOLD}" stroke-dasharray="4 4" opacity=".55"/>
          <circle cx="{mx:.1f}" cy="{my:.1f}" r="7" fill="{ROMAN_CRIMSON}" stroke="{ROMAN_GOLD}" stroke-width="2"/>
          <rect x="{mx - label_w / 2:.1f}" y="{my - 128:.1f}" width="{label_w:.1f}" height="52" rx="8"
                fill="{ROMAN_NAVY}" fill-opacity=".96" stroke="{ROMAN_GOLD}" stroke-opacity=".45" filter="url(#labelShadow)"/>
          <text x="{mx:.1f}" y="{my - 104:.1f}" text-anchor="middle" fill="{ROMAN_IVORY}" font-size="16" font-weight="900" font-family="Cinzel, Georgia, serif">{display}</text>
          <text x="{mx:.1f}" y="{my - 86:.1f}" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="9" font-weight="800" letter-spacing=".4" font-family="Cinzel, Georgia, serif">{label.upper()}</text>
        """)
    return "".join(blocks)


def render_pompeii_milestones(milestone_x_fn, path_y_fn, start_bf):
    return render_mission_milestones(
        milestone_x_fn, path_y_fn, "fat_loss", start_bf, 10.0, "bf_pct", False
    )

def apply_manual_overrides_to_forecast(fc, settings):
    """Scale-weight display override only — body-fat path stays DEXA + cumulative deficit."""
    fc = dict(fc or {})
    manual_weight_flag = get_text_setting("current_weight_manual_override") == "1"
    if manual_weight_flag:
        manual_weight = float(settings.get("current_weight_lbs", fc.get("current_weight") or 0) or 0)
        if manual_weight > 0:
            fc["scale_weight"] = manual_weight
        fc["manual_override_active"] = True
        return fc
    fc["manual_override_active"] = False
    saved = float(settings.get("current_weight_lbs") or 0)
    if saved > 0:
        fc["scale_weight"] = saved
    return fc


def mission_journey_context(fc, settings, daily=None, dexa=None, mission_override=None):
    mission = mission_override or get_mission_mode()
    if mission_override and mission_override != get_mission_mode():
        seed = compute_mission_seed(mission, fc, settings, daily, dexa)
        js = {
            "start_date": seed["start_date"],
            "start_days": seed["start_days"],
            "start_body_fat_pct": seed["start_body_fat_pct"],
            "start_weight_lbs": seed["start_weight_lbs"],
            "mission_mode": mission,
            "start_metric": seed["start_metric"],
            "goal_metric": seed["goal_metric"],
            "metric_type": seed["metric_type"],
            "start_lean_lbs": seed.get("start_lean_lbs"),
        }
    else:
        js = get_or_create_journey_start(fc, settings, daily, dexa)

    meta = MISSION_ROAD_META[mission]
    metric_type = js["metric_type"]
    start_metric = float(js["start_metric"])
    goal_metric = float(js["goal_metric"])
    start_days = float(js["start_days"])
    start_lean = float(js.get("start_lean_lbs") or 0)

    daily_df = daily if daily is not None else pd.DataFrame()
    dexa_df = dexa if dexa is not None else pd.DataFrame()
    comp = estimate_current_composition(daily_df, dexa_df, settings)

    if metric_type == "bf_pct":
        dexa_anchor = latest_dexa_or_settings(dexa_df, settings)
        if dexa_anchor.get("date") and dexa_anchor.get("bf"):
            js = dict(js)
            js["start_date"] = dexa_anchor["date"].isoformat()
            js["start_body_fat_pct"] = float(dexa_anchor["bf"])
            js["start_metric"] = float(dexa_anchor["bf"])
            js["start_weight_lbs"] = float(dexa_anchor["weight"])
            js["start_lean_lbs"] = float(dexa_anchor["lean_mass"])
            start_metric = float(dexa_anchor["bf"])
            start_lean = float(dexa_anchor["lean_mass"])
        current = float(fc["current_bf"]) if fc.get("current_bf") is not None else float(settings.get("current_body_fat_pct") or 0)
        days = int(round(fc.get("days") or 0)) if fc.get("days") is not None else 0
        goal_metric = float(settings.get("goal_body_fat_pct") or goal_metric or 10.0)
        goal_date = fc.get("goal_date")
    elif metric_type == "weight_lbs":
        current = float(fc.get("current_weight") or settings.get("current_weight_lbs") or 0)
        days = estimate_weight_loss_days(current, goal_metric, settings)
        goal_date = date.today() + timedelta(days=days) if days else date.today()
    elif metric_type == "lean_lbs":
        current = float(comp["current_lean_mass"])
        days = estimate_gain_mission_days("muscle_gain", current, goal_metric, settings, daily_df, dexa_df)
        goal_date = date.today() + timedelta(days=days)
    else:
        if start_lean <= 0:
            start_lean = float(comp["current_lean_mass"])
        current = (
            max(0.0, (float(comp["current_lean_mass"]) - start_lean) / start_lean * 100.0)
            if start_lean > 0
            else 0.0
        )
        days = estimate_gain_mission_days("strength_gain", current, goal_metric, settings, daily_df, dexa_df)
        goal_date = date.today() + timedelta(days=days)

    increasing = meta["decreasing"] is False
    current_days = max(float(days), 0.0)
    journey_start = _coerce_date(js.get("start_date"))
    journey_elapsed = journey_elapsed_days(journey_start)

    if metric_type == "bf_pct" and fc.get("kcal_progress") is not None:
        metric_prog = max(0.0, min(1.0, float(fc.get("kcal_progress") or 0)))
        elapsed = max(float(journey_elapsed), 0.0)
        total_est = elapsed + current_days
        if total_est > 0:
            start_days = total_est
            time_prog = max(0.0, min(1.0, elapsed / total_est))
        else:
            time_prog = 1.0 if metric_prog >= 1 else 0.0
    else:
        metric_prog = metric_progress_frac(current, start_metric, goal_metric, increasing)
        time_prog = (start_days - current_days) / max(start_days, 1.0)
        time_prog = max(0.0, min(1.0, time_prog))

    journey_total = journey_total_days(journey_start, goal_date, start_days)
    dexa_markers = _dexa_journey_markers(dexa_df, js, metric_type)

    if increasing:
        victory = current >= goal_metric - (0.05 if metric_type == "strength_pct" else 0.3)
    elif metric_type == "weight_lbs":
        victory = current <= goal_metric + 0.5
    else:
        victory = current <= goal_metric + 0.05 or float(fc.get("kcal_progress") or 0) >= 0.995

    return {
        "mission": mission,
        "meta": meta,
        "js": js,
        "metric_type": metric_type,
        "start_metric": start_metric,
        "goal_metric": goal_metric,
        "current": current,
        "start_days": start_days,
        "days": int(round(current_days)),
        "goal_date": goal_date,
        "metric_progress": metric_prog,
        "time_progress": time_prog,
        "increasing": increasing,
        "victory": victory,
        "start_lean_lbs": start_lean,
        "comp": comp,
        "journey_start": journey_start,
        "journey_total_days": journey_total,
        "journey_elapsed_days": journey_elapsed,
        "dexa_markers": dexa_markers,
    }


def get_or_create_journey_start(fc, settings, daily=None, dexa=None):
    """Keeps the original start axis fixed; re-seeds when mission changes."""
    ensure_journey_table()
    mission = get_mission_mode()
    c = conn()
    row = c.execute(
        """
        SELECT start_date, start_days, start_body_fat_pct, start_weight_lbs,
               mission_mode, start_metric, goal_metric, metric_type, start_lean_lbs
        FROM journey_start WHERE id = 1
        """
    ).fetchone()
    c.close()

    js = _journey_row_to_dict(row, fc, settings)
    if js is None or js.get("mission_mode") != mission:
        reseed_journey_start(mission, fc, settings, daily, dexa)
        c = conn()
        row = c.execute(
            """
            SELECT start_date, start_days, start_body_fat_pct, start_weight_lbs,
                   mission_mode, start_metric, goal_metric, metric_type, start_lean_lbs
            FROM journey_start WHERE id = 1
            """
        ).fetchone()
        c.close()
        js = _journey_row_to_dict(row, fc, settings)
    return js


def journey_progress(fc, settings, daily=None, dexa=None):
    ctx = mission_journey_context(fc, settings, daily, dexa)
    return ctx["js"], ctx["time_progress"]


def ensure_goal_date_history_table():
    c = conn()
    c.execute('''
        CREATE TABLE IF NOT EXISTS goal_date_history (
            snapshot_date TEXT PRIMARY KEY,
            goal_date TEXT,
            days_remaining REAL,
            estimated_body_fat_pct REAL,
            fat_remaining_lbs REAL,
            notes TEXT
        )
    ''')
    c.commit()
    c.close()
def save_goal_snapshot(fc):
    ensure_goal_date_history_table()
    gd = fc.get("goal_date")
    if gd is None:
        return
    snapshot = date.today().isoformat()
    gd_text = gd.isoformat() if hasattr(gd, "isoformat") else str(gd)
    meta = fc.get("forecast_source_meta") or {}
    notes = (
        f"{fc.get('forecast_source') or 'target_deficit'};"
        f" avg_def={meta.get('avg_deficit_kcal')};"
        f" wt_wk={meta.get('weight_loss_lbs_week')}"
    )
    c = conn()
    c.execute(
        "INSERT OR REPLACE INTO goal_date_history VALUES (?, ?, ?, ?, ?, ?)",
        (
            snapshot,
            gd_text,
            float(fc.get("days") or 0),
            float(fc.get("current_bf") or 0),
            float(fc.get("fat_to_lose") or 0),
            notes,
        ),
    )
    c.commit()
    c.close()
def load_goal_history():
    ensure_goal_date_history_table()
    c = conn()
    try:
        df = pd.read_sql(
            "SELECT * FROM goal_date_history ORDER BY snapshot_date",
            c,
            parse_dates=["snapshot_date", "goal_date"],
        )
    except Exception:
        df = pd.DataFrame()
    c.close()
    return df
def goal_date_momentum(fc):
    hist = load_goal_history()
    current_goal = fc.get("goal_date")
    if current_goal is None:
        return {"days_moved": 0, "label": "Need more data", "direction": "neutral"}
    if hist.empty or hist["goal_date"].dropna().empty:
        return {"days_moved": 0, "label": "First forecast captured", "direction": "neutral"}

    seven_days_ago = pd.Timestamp(date.today() - timedelta(days=7))
    prior = hist[hist["snapshot_date"] <= seven_days_ago]
    if prior.empty:
        prior = hist.head(1)

    prior_goal = prior.iloc[-1]["goal_date"]
    if pd.isna(prior_goal):
        return {"days_moved": 0, "label": "First forecast captured", "direction": "neutral"}

    current_ts = pd.Timestamp(current_goal)
    days_moved = int((prior_goal - current_ts).days)

    if days_moved > 0:
        return {"days_moved": days_moved, "label": f"{days_moved} days closer this week", "direction": "improving"}
    if days_moved < 0:
        return {"days_moved": days_moved, "label": f"{abs(days_moved)} days later this week", "direction": "worsening"}
    return {"days_moved": 0, "label": "Goal date unchanged this week", "direction": "neutral"}
def pompeii_asset_uri(filename):
    asset_path = Path("assets") / filename
    if not asset_path.exists():
        return None
    encoded = base64.standard_b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def victoria_dashboard_html(fc, settings, js, daily):
    current_bf = float(fc.get("current_bf") or settings.get("current_body_fat_pct", 0) or 0)
    goal_bf = float(settings.get("goal_body_fat_pct", 10.0) or 10.0)
    days = int(round(fc.get("days") or 0)) if fc.get("days") is not None else 0
    avg_def = compute_campaign_average_deficit(daily, settings, js)
    avg_def_label = f"{avg_def:.0f} kcal/day" if avg_def is not None else "Not enough data yet"
    start_bf = float(js.get("start_body_fat_pct") or current_bf)
    bg_uri = pompeii_asset_uri("pompeii_victoria.png")
    bg_layer = (
        f'<image href="{bg_uri}" x="0" y="0" width="1200" height="520" preserveAspectRatio="xMidYMid slice" opacity=".85"/>'
        if bg_uri
        else ""
    )
    return (
        f"""
    <style>
      {ROMAN_GOOGLE_FONTS}
      * {{ box-sizing:border-box; }}
      html, body {{ margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:{ROMAN_BLACK}; }}
      .tu-hero-wrap {{ width:100%; max-width:100%; margin:0; }}
      .tu-shell {{
        background:{ROMAN_NAVY};
        border:1px solid {ROMAN_GOLD_BORDER};
        border-radius:16px;
        padding:8px 12px 6px 12px;
        color:{ROMAN_IVORY};
        font-family: Georgia, "Cinzel Decorative", serif;
        box-shadow: inset 0 0 28px rgba(201,168,76,.08), 0 14px 36px rgba(0,0,0,.45);
        width:100%; max-width:100%;
      }}
      .tu-road {{
        position:relative; height:380px; border-radius:14px; overflow:hidden;
        border:1px solid {ROMAN_GOLD_BORDER};
        box-shadow: inset 0 0 40px rgba(201,168,76,.06), 0 8px 32px rgba(0,0,0,.5);
        background: linear-gradient(180deg, {ROMAN_BLACK} 0%, {ROMAN_NAVY} 42%, #1a0f0f 100%);
      }}
      .tu-road svg {{ position:absolute; inset:0; width:100%; height:100%; }}
    </style>
    <div class="tu-hero-wrap">
    <div class="tu-shell">
      <div class="tu-road">
        <svg viewBox="0 0 1200 520" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="victoryHaze" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="{ROMAN_BLACK}" stop-opacity=".55"/>
              <stop offset="45%" stop-color="{ROMAN_NAVY}" stop-opacity=".35"/>
              <stop offset="100%" stop-color="{ROMAN_BLACK}" stop-opacity=".88"/>
            </linearGradient>
            <filter id="labelShadow"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity=".45"/></filter>
          </defs>
          {bg_layer}
          <rect x="0" y="0" width="1200" height="520" fill="url(#victoryHaze)"/>
          <text x="600" y="72" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="54" font-weight="900"
                letter-spacing="6" font-family="Cinzel, Georgia, serif" filter="url(#labelShadow)">VICTORIA</text>
          <text x="600" y="102" text-anchor="middle" fill="{ROMAN_IVORY}" font-size="15" font-weight="800"
                letter-spacing="2.2" font-family="Cinzel, Georgia, serif" opacity=".95">INSIDE POMPEII AMPHITHEATER</text>
          <rect x="180" y="128" width="840" height="118" rx="16" fill="{ROMAN_NAVY}" fill-opacity=".94" stroke="{ROMAN_GOLD}" stroke-opacity=".35"/>
          <text x="300" y="162" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="10" font-weight="800" letter-spacing=".7" font-family="Cinzel, Georgia, serif">CURRENT BODY FAT</text>
          <text x="300" y="192" text-anchor="middle" fill="{ROMAN_IVORY}" font-size="28" font-weight="900" font-family="Cinzel, Georgia, serif">{current_bf:.1f}%</text>
          <text x="450" y="162" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="10" font-weight="800" letter-spacing=".7" font-family="Cinzel, Georgia, serif">GOAL BODY FAT</text>
          <text x="450" y="192" text-anchor="middle" fill="{ROMAN_IVORY}" font-size="28" font-weight="900" font-family="Cinzel, Georgia, serif">{goal_bf:.1f}%</text>
          <text x="600" y="162" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="10" font-weight="800" letter-spacing=".7" font-family="Cinzel, Georgia, serif">DAYS REQUIRED</text>
          <text x="600" y="192" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="28" font-weight="900" font-family="Cinzel, Georgia, serif">{days}</text>
          <text x="780" y="162" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="10" font-weight="800" letter-spacing=".7" font-family="Cinzel, Georgia, serif">AVG DEFICIT</text>
          <text x="780" y="192" text-anchor="middle" fill="{ROMAN_IVORY}" font-size="24" font-weight="900" font-family="Cinzel, Georgia, serif">{avg_def_label}</text>
          <text x="600" y="292" text-anchor="middle" fill="{ROMAN_GOLD}" font-size="17" font-weight="900"
                letter-spacing="3.5" font-family="Cinzel, Georgia, serif" filter="url(#labelShadow)">SENATVS POPVLVSQVE ROMANVS</text>
          <text x="600" y="322" text-anchor="middle" fill="{ROMAN_IVORY}" font-size="15" font-weight="600"
                font-style="italic" opacity=".95">"The Senate and People of Rome salute your discipline and perseverance."</text>
        </svg>
      </div>
    </div>
    </div>
    """
    )


FILENAME_KEYWORDS = {
    "DEXA": ["dexa", "fitpal", "hologic", "dexafit", "bodycomp", "body_comp"],
    "Oura": ["oura", "sleep", "readiness", "hrv", "recovery"],
    "FatSecret": ["fatsecret", "fat_secret", "food", "diary", "macro", "nutrition"],
    "Workout": ["strong", "workout", "lift", "gym", "exercise"],
    "Scale": ["scale", "weight", "withings", "renpho", "eufy", "weigh"],
    "Apple Health Weight": ["apple health", "health weight", "weight history"],
}


def normalize_ocr_for_classification(text):
    t = (text or "").lower()
    t = re.sub(r"(\d)\s*[iIl1][bB]\b", r"\1 lb", t)
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    return t


def _has_workout_strength_evidence(text):
    t = normalize_ocr_for_classification(text)
    return any(kw in t for kw in WORKOUT_STRONG_KEYWORDS) or bool(
        re.search(r"\b\d+\s*[x×]\s*\d+\b", t) or re.search(r"\bset\s*\d+", t)
    )


def detect_strong_category(text, filename=""):
    """High-confidence category overrides from OCR layout and source clues."""
    t = normalize_ocr_for_classification(text)
    name = (filename or "").lower()
    workout_evidence = _has_workout_strength_evidence(text)

    weight_entries = re.findall(r"\b(\d{2,3}\.\d)\s*lb\b", t)
    if ("all data" in t and "measurements" in t) or (
        "all data" in t and len(weight_entries) >= 2
    ):
        return "Apple Health Weight"

    oura_hits = sum(1 for kw in OURA_ACTIVITY_KEYWORDS if kw in t)
    oura_sleep_hits = sum(1 for kw in OURA_SLEEP_KEYWORDS if kw in t)
    if (
        ("total burn" in t and "activity burn" in t)
        or (oura_hits >= 2 and not workout_evidence)
        or (oura_sleep_hits >= 2 and not workout_evidence)
        or ("activity" in t and "goal progress" in t and not workout_evidence)
        or ("sleep score" in t and "readiness" in t and not workout_evidence)
    ):
        return "Oura"

    if ("fitpal" in t or "fitlab" in t) and any(
        clue in t for clue in ["whole body", "body composition", "scan date", "horizon wi", "scan information", "dxa results"]
    ):
        return "DEXA"
    if "fitpal llc" in t or "fitlab llc" in t or "hologic" in t:
        return "DEXA"
    dexa_hits = sum(1 for kw in DEXA_STRONG_KEYWORDS if kw in t)
    if dexa_hits >= 2:
        return "DEXA"
    if "body composition results" in t or "dxa results" in t:
        return "DEXA"
    if "whole body" in t and re.search(r"weight[:\s]+[\d.]+", t) and (
        "scan date" in t or "scan information" in t or re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", t)
    ):
        return "DEXA"

    fatsecret_markers = ["calories", "breakfast", "lunch", "dinner", "net c", "prot"]
    fatsecret_hits = sum(1 for kw in fatsecret_markers if kw in t)
    snacks_other = "snacks/other" in t or "snacks" in t or "other" in t
    if fatsecret_hits >= 5 or (fatsecret_hits >= 4 and snacks_other):
        return "FatSecret"

    return None


def is_image_file(path):
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def list_inbox_image_files(scan_dir):
    """All OCR image candidates under the inbox folder (.png/.jpg/.jpeg/.heic)."""
    scan_dir = Path(scan_dir).expanduser()
    if not scan_dir.exists():
        return []
    return [
        p for p in scan_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in INBOX_IMAGE_EXTENSIONS
    ]


def ocr_entry_for_hash(file_hash):
    c = conn()
    row = c.execute(
        "SELECT detected_type, ocr_text, status, created_at FROM ocr_queue WHERE file_hash = ?",
        (file_hash,),
    ).fetchone()
    c.close()
    if not row:
        return None
    return {
        "detected_type": row[0],
        "ocr_text": row[1] or "",
        "status": row[2],
        "created_at": row[3],
    }


def ocr_manually_finalized(file_hash):
    entry = ocr_entry_for_hash(file_hash)
    return bool(entry and entry.get("status") in OCR_TERMINAL_STATUSES)


def ocr_fully_processed(file_hash):
    """True when this hash is confirmed/skipped or has OCR text and a real category."""
    entry = ocr_entry_for_hash(file_hash)
    if not entry:
        return False
    if entry.get("status") in OCR_TERMINAL_STATUSES:
        return True
    if entry["detected_type"] in (None, "", "Unclassified Image"):
        return False
    return bool(entry["ocr_text"].strip())


def _register_heif_opener():
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        return True
    except Exception:
        return False


def convert_heic_to_png(heic_path, png_path=None):
    heic_path = Path(heic_path)
    if heic_path.suffix.lower() != ".heic":
        return None
    png_path = Path(png_path) if png_path else heic_path.with_suffix(".png")
    try:
        _register_heif_opener()
        img = Image.open(heic_path)
        img.save(png_path, "PNG")
        return png_path
    except Exception:
        return None


def image_display_path(path):
    path = Path(path)
    if path.suffix.lower() == ".heic":
        png = path.with_suffix(".png")
        if png.exists():
            return png
    return path


def prepare_ocr_image_path(path):
    path = Path(path)
    if path.suffix.lower() == ".heic":
        png = convert_heic_to_png(path)
        if png:
            return png, True
    return path, False


_TESSERACT_STATUS = {"checked": False, "configured": False, "path": "", "error": ""}


def find_tesseract_executable():
    import shutil

    found = shutil.which("tesseract")
    if found:
        return found
    if os.name == "nt":
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
        ]
        for candidate in candidates:
            exe = Path(candidate)
            if exe.exists():
                return str(exe)
    return None


def configure_tesseract():
    global _TESSERACT_STATUS
    if _TESSERACT_STATUS.get("checked"):
        return _TESSERACT_STATUS
    try:
        import pytesseract
    except ImportError:
        _TESSERACT_STATUS = {
            "checked": True,
            "configured": False,
            "path": "",
            "error": "pytesseract is not installed. OCR will be skipped until it is available.",
        }
        return _TESSERACT_STATUS

    exe = find_tesseract_executable()
    if exe:
        pytesseract.pytesseract.tesseract_cmd = exe
        _TESSERACT_STATUS = {
            "checked": True,
            "configured": True,
            "path": exe,
            "error": "",
        }
    else:
        _TESSERACT_STATUS = {
            "checked": True,
            "configured": False,
            "path": "",
            "error": "Tesseract was not found on PATH or in standard Windows install locations.",
        }
    return _TESSERACT_STATUS


def get_tesseract_status():
    return dict(configure_tesseract())


def run_ocr(path):
    """Run OCR on an image and return structured status for UI/logging."""
    path = Path(path)
    tesseract = configure_tesseract()
    result = {
        "text": "",
        "status": "unavailable",
        "error": tesseract.get("error") or "OCR unavailable.",
        "engine": "tesseract",
        "tesseract_path": tesseract.get("path") or "",
        "char_count": 0,
        "source_path": str(path),
    }
    if not tesseract.get("configured"):
        return result
    try:
        import pytesseract

        ocr_path, _ = prepare_ocr_image_path(path)
        img = Image.open(ocr_path)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img) or ""
        result["text"] = text
        result["char_count"] = len(text.strip())
        if result["char_count"]:
            result["status"] = "ok"
            result["error"] = ""
        else:
            result["status"] = "empty"
            result["error"] = "Tesseract ran successfully but returned no text."
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)
    return result


def try_ocr_image(path):
    """Best-effort local OCR. HEIC files are converted to PNG automatically before OCR."""
    return run_ocr(path).get("text", "")


def truncate_ocr_text(text, limit=240):
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def _parsed_field_count(dtype, parsed):
    if not parsed:
        return 0
    if dtype == "DEXA":
        keys = ["body_fat_pct", "fat_mass_lbs", "lean_mass_lbs", "weight_lbs", "vat_mass_g"]
    elif dtype == "FatSecret":
        keys = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sodium_mg"]
    elif dtype == "Oura":
        keys = [
            "sleep_score", "readiness_score", "sleep_minutes", "oura_burn",
            "active_energy", "oura_activity_time_min", "oura_goal_progress", "steps",
        ]
    elif dtype == "Workout":
        keys = ["workout", "active_energy", "sets", "reps", "weight_lbs"]
    elif dtype == "Scale":
        keys = ["weight_lbs"]
    elif dtype == "Apple Health Weight":
        keys = ["weight_lbs"]
    else:
        keys = list(parsed.keys())
    return sum(1 for k in keys if parsed.get(k) not in (None, "", 0, 0.0))


def score_image_categories(text, filename=""):
    t = normalize_ocr_for_classification(text)
    name = (filename or "").lower()
    scores = {cat: 0 for cat in IMAGE_QUEUE_TYPES}
    workout_evidence = _has_workout_strength_evidence(text)

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                scores[cat] += 2
            if kw in name:
                scores[cat] += 3

    for cat, keywords in FILENAME_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                scores[cat] += 4

    for cat in IMAGE_QUEUE_TYPES:
        parsed = parse_by_type(cat, text)
        scores[cat] += _parsed_field_count(cat, parsed) * 4

    if scores["Scale"] > 0 and scores["DEXA"] > 0:
        dexa_parsed = parse_by_type("DEXA", text)
        scale_parsed = parse_by_type("Scale", text)
        if dexa_parsed.get("body_fat_pct") or dexa_parsed.get("lean_mass_lbs") or dexa_parsed.get("fat_mass_lbs"):
            scores["DEXA"] += 8
            scores["Scale"] = max(0, scores["Scale"] - 4)
        elif scale_parsed.get("weight_lbs") and not dexa_parsed.get("body_fat_pct"):
            if not any(kw in t for kw in ["fitpal", "hologic", "body composition", "whole body", "dxa"]):
                scores["Scale"] += 4

    oura_activity_hits = sum(1 for kw in OURA_ACTIVITY_KEYWORDS if kw in t)
    oura_sleep_hits = sum(1 for kw in OURA_SLEEP_KEYWORDS if kw in t)
    if oura_activity_hits >= 2 and not workout_evidence:
        scores["Oura"] += oura_activity_hits * 2
        scores["Workout"] = max(0, scores["Workout"] - 6)
    if oura_sleep_hits >= 2 and not workout_evidence:
        scores["Oura"] += oura_sleep_hits * 2
        scores["Workout"] = max(0, scores["Workout"] - 6)

    if ("all data" in t and "measurements" in t) or (
        "all data" in t and len(re.findall(r"\b\d{2,3}\.\d\s*lb\b", t)) >= 2
    ):
        scores["Apple Health Weight"] += 12
        scores["Workout"] = max(0, scores["Workout"] - 8)

    dexa_hits = sum(1 for kw in DEXA_STRONG_KEYWORDS if kw in t)
    if dexa_hits:
        scores["DEXA"] += dexa_hits

    if not workout_evidence and scores["Workout"] <= 4:
        scores["Workout"] = max(0, scores["Workout"] - 2)

    return scores


def classify_from_text(text, fallback="Unclassified Image"):
    strong = detect_strong_category(text)
    if strong:
        return strong
    scores = score_image_categories(text)
    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score >= 4:
        return best_type
    if best_score > 0:
        return best_type
    return fallback


def classify_image(path, ocr_text):
    path = Path(path)
    strong = detect_strong_category(ocr_text, path.name)
    if strong:
        return strong

    name_hint = detect_file_type(path)
    if name_hint in FILENAME_CLASSIFIED_TYPES and name_hint not in {"Unclassified Image", "Unknown"}:
        if name_hint == "Strong CSV":
            return "Workout"
        return name_hint

    scores = score_image_categories(ocr_text, path.name)
    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score >= 4:
        return best_type
    if best_score > 0:
        return best_type
    if name_hint not in {"Unclassified Image", "Unknown"}:
        return name_hint
    return "Unclassified Image"


def ocr_queue_label(dtype):
    labels = {
        "FatSecret": "Nutrition OCR",
        "Oura": "Oura OCR",
        "DEXA": "DEXA OCR",
        "Workout": "Workout OCR",
        "Scale": "Weight OCR",
        "Apple Health Weight": "Apple Health Weight OCR",
    }
    return labels.get(dtype, dtype or "Unknown")


def format_parsed_preview(parsed):
    if not parsed:
        return ""
    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except Exception:
            return parsed[:120]
    entries = parsed.get("weight_entries")
    if entries:
        count = len(entries)
        first = entries[0]
        preview = f"{count} weights"
        if first.get("weight_lbs") is not None:
            preview += f", first={first['weight_lbs']} lb"
        if first.get("measured_at"):
            preview += f" @ {first['measured_at']}"
        return preview
    parts = []
    for key, val in parsed.items():
        if val in (None, "", 0, 0.0) or key == "notes":
            continue
        parts.append(f"{key}={val}")
    return ", ".join(parts[:8])


def load_ocr_intelligence_rows():
    reg = load_file_registry()
    queue = load_ocr_queue()
    rows = []
    seen_paths = set()
    if not queue.empty:
        for _, q in queue.iterrows():
            parsed = q.get("parsed_json") or "{}"
            status = q.get("status") or "unknown"
            preview = format_parsed_preview(parsed)
            if status == "imported":
                values = preview or "confirmed"
            elif status == "skipped":
                values = q.get("notes") or "skipped"
            else:
                values = preview or "awaiting confirmation"
            stored = str(q.get("stored_path") or "")
            seen_paths.add(stored)
            rows.append({
                "file": Path(stored).name if stored else "",
                "category": q.get("detected_type") or "",
                "ocr_queue": ocr_queue_label(q.get("detected_type")),
                "ocr_status": status,
                "ocr_engine_status": "ok" if (q.get("ocr_text") or "").strip() else "empty",
                "ocr_text": truncate_ocr_text(q.get("ocr_text") or ""),
                "extracted_values": values,
                "updated": q.get("created_at") or "",
            })
    if not reg.empty:
        image_reg = reg[reg["detected_type"].isin(list(IMAGE_QUEUE_TYPES) + ["Unclassified Image"])]
        for _, r in image_reg.iterrows():
            stored = str(r.get("stored_path") or "")
            if stored in seen_paths:
                continue
            rows.append({
                "file": r.get("file_name") or Path(stored).name,
                "category": r.get("detected_type") or "",
                "ocr_queue": ocr_queue_label(r.get("detected_type")),
                "ocr_status": r.get("status") or "stored",
                "extracted_values": r.get("notes") or "",
                "updated": r.get("first_seen") or "",
            })
    return pd.DataFrame(rows)


def registry_entry_for_hash(file_hash):
    c = conn()
    row = c.execute(
        "SELECT detected_type, stored_path, status FROM file_registry WHERE file_hash = ?",
        (file_hash,),
    ).fetchone()
    c.close()
    if not row:
        return None
    return {"detected_type": row[0], "stored_path": row[1], "status": row[2]}


def reclassify_stored_image(path, stored_path, file_hash, source_label):
    stored_path = Path(stored_path)
    if not stored_path.exists():
        return None
    ocr = run_ocr(stored_path)
    ocr_text = ocr.get("text") or ""
    dtype = classify_image(path, ocr_text)
    if stored_path.suffix.lower() == ".heic":
        convert_heic_to_png(stored_path, stored_path.with_suffix(".png"))
    parsed = parse_by_type(dtype, ocr_text)
    ocr_note = f"ocr={ocr.get('status')}; chars={ocr.get('char_count', 0)}"
    prior = ocr_entry_for_hash(file_hash)
    finalized = bool(prior and prior.get("status") in OCR_TERMINAL_STATUSES)
    reg_status = prior.get("status") if finalized else "pending_confirmation"
    register_file(
        file_hash,
        path,
        stored_path,
        dtype,
        reg_status,
        f"{source_label} reclassified | {ocr_queue_label(dtype)} | {ocr_note}",
        file_name=path.name,
        file_size=path.stat().st_size,
        file_mtime=path.stat().st_mtime,
    )
    if not finalized:
        upsert_ocr_queue(
            file_hash,
            stored_path,
            dtype,
            ocr_text,
            parsed,
            status="pending_confirmation",
            notes=f"{ocr_queue_label(dtype)} | reclassified | {ocr_note}",
        )
        if dtype == "FatSecret" and parsed.get("calories"):
            upsert_fatsecret_from_screenshot(parsed, parse_inbox_image_date(path))
        if dtype in ("Apple Health Weight", "Scale") and parsed.get("weight_lbs"):
            if not (dtype == "Apple Health Weight" and parsed.get("weight_entries")):
                upsert_weight_from_screenshot(parsed, parse_inbox_image_date(path), dtype, file_hash=file_hash)
    return {
        "file": str(path),
        "status": "imported",
        "type": dtype,
        "stored": str(stored_path),
        "detail": f"reclassified to {dtype}; {format_parsed_preview(parsed) or 'queued for OCR confirmation'}",
        "ocr_status": ocr.get("status"),
        "ocr_chars": ocr.get("char_count", 0),
        "ocr_text": truncate_ocr_text(ocr_text, 400),
        "rows": 0,
    }


def reclassify_stored_pdf(path, stored_path, file_hash, source_label):
    """Re-classify a generic PDF that now matches FatSecret or DEXA rules."""
    path = Path(path)
    stored_path = Path(stored_path) if stored_path else path
    src = stored_path if stored_path.exists() else path
    if not src.exists() or src.suffix.lower() != ".pdf":
        return None
    text = extract_pdf_text(src)
    dtype = classify_pdf(src, text)
    if dtype in {"PDF", "Unknown"}:
        return None

    rows_imported, struct_detail = auto_import_structured_file(src, dtype)

    dest = stored_path if stored_path.exists() else src
    dest_folder = target_folder_for_type(dtype)
    if dest.exists() and dest_folder != dest.parent:
        dest_folder.mkdir(parents=True, exist_ok=True)
        moved = dest_folder / dest.name
        if moved.resolve() != dest.resolve():
            shutil.move(str(dest), str(moved))
            dest = moved
    if dtype == "DEXA" and rows_imported <= 0:
        parsed = parse_dexa_ocr(text)
        summary = auto_import_dexa_parsed(
            parsed,
            source_path=str(dest),
            notes=f"DEXA PDF reclassify | {source_label}",
        )
        if summary:
            rows_imported = 1
            struct_detail = summary.get("message") or "DEXA PDF imported"

    register_file(
        file_hash,
        path,
        dest,
        dtype,
        "stored",
        f"{source_label} reclassified | {ocr_queue_label(dtype)} | {struct_detail or 'classified'}",
        file_name=path.name,
        file_size=path.stat().st_size if path.exists() else None,
        file_mtime=path.stat().st_mtime if path.exists() else None,
    )
    return {
        "file": str(path),
        "status": "imported",
        "type": dtype,
        "stored": str(dest),
        "detail": f"reclassified to {dtype}; {struct_detail or 'classified'}",
        "rows": rows_imported,
    }


def reclassify_other_uploads(source_label="Classification Rule Reclassify"):
    """Re-apply classification rules to imported screenshot files under TU Uploads."""
    other_dir = UPLOAD_DIR / "Other"
    summary = {
        "folder": str(other_dir),
        "processed": 0,
        "reclassified": 0,
        "ocr_ok": 0,
        "ocr_empty": 0,
        "ocr_failed": 0,
        "files": [],
    }

    queue_df = load_ocr_queue()
    ocr_by_hash = {}
    if not queue_df.empty:
        for _, q in queue_df.iterrows():
            ocr_by_hash[q["file_hash"]] = q.get("ocr_text") or ""

    c = conn()
    try:
        rows = c.execute(
            """
            SELECT file_hash, file_name, source_path, stored_path, detected_type
            FROM file_registry
            WHERE stored_path LIKE '%TU Uploads%'
            ORDER BY first_seen
            """
        ).fetchall()
    except Exception:
        rows = []
    c.close()

    for row in rows:
        fh, file_name, source_path, stored_path, old_type = row
        stored_path = Path(stored_path)
        source_path = Path(source_path) if source_path else stored_path
        if not is_image_file(stored_path):
            continue
        if not stored_path.exists():
            summary["files"].append(
                {
                    "file": file_name or stored_path.name,
                    "previous_type": old_type,
                    "new_type": old_type,
                    "ocr_status": "missing_file",
                    "ocr_chars": 0,
                    "ocr_text": "",
                    "detail": "stored file missing on disk",
                }
            )
            continue

        summary["processed"] += 1
        ocr_text = ocr_by_hash.get(fh, "")
        if ocr_text.strip():
            ocr = {"status": "cached", "char_count": len(ocr_text.strip()), "error": ""}
            summary["ocr_ok"] += 1
        else:
            ocr = run_ocr(stored_path)
            ocr_text = ocr.get("text") or ""
            if ocr.get("status") == "ok":
                summary["ocr_ok"] += 1
            elif ocr.get("status") == "empty":
                summary["ocr_empty"] += 1
            else:
                summary["ocr_failed"] += 1

        dtype = classify_image(source_path, ocr_text)
        parsed = parse_by_type(dtype, ocr_text)
        new_stored_path = stored_path

        if dtype != "Unclassified Image" and target_folder_for_type(dtype) != stored_path.parent:
            dest_folder = target_folder_for_type(dtype)
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / stored_path.name
            if dest_path.resolve() != stored_path.resolve():
                shutil.move(str(stored_path), str(dest_path))
                if stored_path.suffix.lower() == ".heic":
                    png_src = stored_path.with_suffix(".png")
                    if png_src.exists():
                        shutil.move(str(png_src), str(dest_path.with_suffix(".png")))
                new_stored_path = dest_path

        if new_stored_path.suffix.lower() == ".heic":
            convert_heic_to_png(new_stored_path, new_stored_path.with_suffix(".png"))

        ocr_note = f"ocr={ocr.get('status')}; chars={ocr.get('char_count', 0)}"
        prior = ocr_entry_for_hash(fh)
        finalized = bool(prior and prior.get("status") in OCR_TERMINAL_STATUSES)
        reg_status = prior.get("status") if finalized else "pending_confirmation"
        register_file(
            fh,
            source_path,
            new_stored_path,
            dtype,
            reg_status,
            f"{source_label} | {ocr_queue_label(dtype)} | {ocr_note}",
            file_name=file_name or source_path.name,
            file_size=new_stored_path.stat().st_size,
            file_mtime=new_stored_path.stat().st_mtime,
        )
        if not finalized:
            upsert_ocr_queue(
                fh,
                new_stored_path,
                dtype,
                ocr_text,
                parsed,
                status="pending_confirmation",
                notes=f"{ocr_queue_label(dtype)} | {source_label} | {ocr_note}",
            )
            date_path = source_path if source_path.exists() else new_stored_path
            if dtype == "FatSecret" and parsed.get("calories"):
                upsert_fatsecret_from_screenshot(parsed, parse_inbox_image_date(date_path))
            if dtype in ("Apple Health Weight", "Scale") and parsed.get("weight_lbs"):
                if not (dtype == "Apple Health Weight" and parsed.get("weight_entries")):
                    upsert_weight_from_screenshot(parsed, parse_inbox_image_date(date_path), dtype)

        if dtype != old_type:
            summary["reclassified"] += 1

        summary["files"].append(
            {
                "file": file_name or new_stored_path.name,
                "previous_type": old_type,
                "new_type": dtype,
                "ocr_status": ocr.get("status"),
                "ocr_chars": ocr.get("char_count", 0),
                "ocr_text": truncate_ocr_text(ocr_text, 400),
                "stored": str(new_stored_path),
                "detail": ocr.get("error") or format_parsed_preview(parsed) or "classification updated",
            }
        )

    return summary


FS_SUMMARY_LABEL_SPECS = [
    ("carbs_g", re.compile(r"Net\s*C(?:arbs?)?", re.I)),
    ("fiber_g", re.compile(r"Fiber", re.I)),
    ("sodium_mg", re.compile(r"Sod(?:ium)?", re.I)),
    ("protein_g", re.compile(r"Prot(?:ein)?", re.I)),
    ("calories", re.compile(r"Cal(?:ories)?(?:s)?", re.I)),
]


def _fatsecret_labels_on_line(line):
    """Return summary label keys left-to-right on one OCR line."""
    found = []
    for key, pat in FS_SUMMARY_LABEL_SPECS:
        for match in pat.finditer(line):
            found.append((match.start(), key))
    found.sort(key=lambda item: item[0])
    ordered = []
    seen = set()
    for _, key in found:
        if key not in seen:
            seen.add(key)
            ordered.append(key)
    return ordered


def _fatsecret_numbers_on_line(line, min_value=None, max_value=None):
    values = []
    for token in re.findall(r"[\d,]+\.?\d*", line):
        try:
            val = float(token.replace(",", ""))
        except ValueError:
            continue
        if min_value is not None and val < min_value:
            continue
        if max_value is not None and val > max_value:
            continue
        values.append(val)
    return values


def _fatsecret_collect_summary_values(label_line, next_line, num_labels):
    """
    FatSecret OCR often splits the summary value row across two lines:
      'Net C Fiber Sod Prot Calories 205.13 17.2'
      '2119.0 194.57 2183.0'
    Combine trailing numbers on the label line with the next line.
    """
    label_keys = _fatsecret_labels_on_line(label_line)
    if not label_keys:
        return []

    label_end = 0
    for _, pat in FS_SUMMARY_LABEL_SPECS:
        for match in pat.finditer(label_line):
            label_end = max(label_end, match.end())

    same_line_nums = _fatsecret_numbers_on_line(label_line[label_end:])
    next_line_nums = _fatsecret_numbers_on_line(next_line or "")
    combined = same_line_nums + next_line_nums

    if len(combined) >= num_labels:
        return combined[:num_labels]
    if len(combined) >= len(label_keys):
        return combined[: len(label_keys)]
    return combined


def _fatsecret_summary_pair_valid(pair):
    """Reject column-shifted OCR rows using plausible macro ranges."""
    cal = pair.get("calories")
    prot = pair.get("protein_g")
    carbs = pair.get("carbs_g")
    fiber = pair.get("fiber_g")
    sodium = pair.get("sodium_mg")

    if cal is not None and not (400 <= float(cal) <= 8000):
        return False
    if prot is not None and not (20 <= float(prot) <= 400):
        return False
    if carbs is not None and not (0 <= float(carbs) <= 600):
        return False
    if fiber is not None and not (0 <= float(fiber) <= 150):
        return False
    if sodium is not None and not (200 <= float(sodium) <= 12000):
        return False
    if sodium is not None and cal is not None and float(sodium) > float(cal) * 2:
        return False
    return bool(cal or prot or carbs)


def _parse_fatsecret_summary_columns(text):
    """
    FatSecret Today summary: each label sits directly above its value.
    Find the label row first, then read the numeric row immediately below —
    never infer values left-to-right without label anchors.
    """
    out = {}
    if not text:
        return out

    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if ln]

    candidate_pairs = []
    for idx in range(len(lines) - 1):
        label_keys = _fatsecret_labels_on_line(lines[idx])
        if not label_keys:
            continue
        if len(label_keys) < 3:
            continue

        context = " ".join(lines[max(0, idx - 2) : min(len(lines), idx + 3)]).lower()
        if any(meal in context for meal in ("breakfast", "lunch", "dinner", "snacks/other", "snacks")):
            if "today" not in context and "meal plans" not in context:
                continue

        value_nums = _fatsecret_collect_summary_values(lines[idx], lines[idx + 1], len(label_keys))
        if not value_nums:
            value_nums = _fatsecret_numbers_on_line(lines[idx + 1])
        if not value_nums:
            continue

        pair = {}
        for label_idx, key in enumerate(label_keys):
            if label_idx >= len(value_nums):
                break
            pair[key] = value_nums[label_idx]
        if not pair or not _fatsecret_summary_pair_valid(pair):
            continue

        score = len(pair)
        label_set = set(label_keys)
        if {"carbs_g", "fiber_g", "sodium_mg"}.issubset(label_set):
            score += 20
        if {"protein_g", "calories"}.issubset(label_set):
            score += 20
        if len(pair) >= 5:
            score += 15
        if "today" in context or "meal plans" in context:
            score += 10
        candidate_pairs.append((score, pair))

    if not candidate_pairs:
        return out

    candidate_pairs.sort(key=lambda item: item[0], reverse=True)
    for _, pair in candidate_pairs:
        for key, value in pair.items():
            if key not in out:
                out[key] = value
    return out


def parse_fatsecret_ocr(text, apply_learning=True):
    out = {}
    if not text:
        return out

    out.update(_parse_fatsecret_summary_columns(text))

    # Legacy food-diary paste row: Fat | Net C | Prot | Cals (4 columns, different layout).
    if not out.get("calories"):
        m = re.search(
            r"Fat\s+Net\s*C\s+Prot\s+Cals\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
            text,
            re.I | re.S,
        )
        if m:
            out["fat_g"] = float(m.group(1))
            out["carbs_g"] = float(m.group(2))
            out["protein_g"] = float(m.group(3))
            out["calories"] = float(m.group(4))

    # Only fill fields still missing; avoid same-line horizontal reads for summary labels.
    label_patterns = [
        (r"(?:total\s*)?fat[^0-9]{0,12}([\d.]+)\s*g", "fat_g"),
    ]
    for pat, key in label_patterns:
        if key in out:
            continue
        m = re.search(pat, text, re.I)
        if m:
            out[key] = float(m.group(1).replace(",", ""))

    consumed_match = re.search(
        r"Calories\s+Consumed\s+([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if consumed_match:
        consumed = float(consumed_match.group(1).replace(",", ""))
        if consumed >= 400:
            summary_cal = out.get("calories")
            if summary_cal is None:
                out["calories"] = consumed
            elif abs(float(summary_cal) - consumed) > 30:
                out["calories"] = consumed

    diary = parse_fatsecret_food_diary_pdf(text)
    if diary.get("calories"):
        prefer_diary = any(marker in (text or "").lower() for marker in _FATSECRET_PDF_TEXT_MARKERS)
        if prefer_diary or not out.get("calories"):
            for key, val in diary.items():
                if val not in (None, "") and (prefer_diary or key not in out):
                    out[key] = val

    if apply_learning:
        evidence = _fatsecret_extract_field_evidence(text)
        out = apply_learned_ocr_to_parsed("FatSecret", out, evidence)
    return out


APPLE_HEALTH_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_apple_health_weight_line(line):
    norm = normalize_ocr_for_classification(line)
    match = re.search(r"(\d{2,3}(?:\.\d)?)\s*(?:lbs?|lb\.?)\b", norm, re.I)
    if not match:
        return None
    val = float(match.group(1))
    if 80 <= val <= 400:
        return val
    return None


def _parse_apple_health_datetime_line(line):
    match = re.search(
        r"(?i)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+"
        r"(\d{1,2}),?\s+"
        r"(\d{4})\s+"
        r"at\s+"
        r"(\d{1,2}):(\d{2})\s*"
        r"(AM|PM)?",
        line or "",
    )
    if not match:
        return None
    month = APPLE_HEALTH_MONTHS.get(match.group(1).lower()[:3])
    if not month:
        return None
    day = int(match.group(2))
    year = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))
    ampm = (match.group(6) or "").upper()
    if ampm == "PM" and hour < 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    try:
        dt = datetime(year, month, day, hour, minute)
    except ValueError:
        return None
    return dt.isoformat(timespec="minutes")


def _pair_apple_health_weight_entries(lines):
    """Pair weight lines with the datetime line directly below (Apple Health layout)."""
    entries = []
    idx = 0
    while idx < len(lines):
        weight = _parse_apple_health_weight_line(lines[idx])
        if weight is not None:
            paired = False
            for look_ahead in range(idx + 1, min(idx + 4, len(lines))):
                measured_at = _parse_apple_health_datetime_line(lines[look_ahead])
                if measured_at:
                    entries.append(
                        {
                            "weight_lbs": weight,
                            "measured_at": measured_at,
                            "log_date": measured_at[:10],
                        }
                    )
                    idx = look_ahead + 1
                    paired = True
                    break
            if not paired:
                idx += 1
        else:
            idx += 1
    return entries


def parse_apple_health_weight_ocr(text, apply_learning=True):
    """Extract every weight + timestamp pair from an Apple Health weight history screenshot."""
    out = {"weight_entries": []}
    if not text:
        return out

    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n") if ln.strip()]
    entries = _pair_apple_health_weight_entries(lines)

    if len(entries) <= 1:
        weights = []
        datetimes = []
        for line in lines:
            weight = _parse_apple_health_weight_line(line)
            if weight is not None:
                weights.append(weight)
                continue
            measured_at = _parse_apple_health_datetime_line(line)
            if measured_at:
                datetimes.append(measured_at)
        if len(weights) >= 2 and len(weights) == len(datetimes):
            entries = [
                {"weight_lbs": w, "measured_at": dt, "log_date": dt[:10]}
                for w, dt in zip(weights, datetimes)
            ]

    out["weight_entries"] = entries
    if entries:
        out["weight_lbs"] = entries[0]["weight_lbs"]
        out["log_date"] = entries[0]["log_date"]
    if apply_learning:
        evidence = _scale_extract_field_evidence(text)
        learned = apply_learned_ocr_to_parsed("Apple Health Weight", dict(out), evidence)
        if learned.get("weight_lbs") and entries:
            entries[0]["weight_lbs"] = learned["weight_lbs"]
            out["weight_lbs"] = learned["weight_lbs"]
    return out


def save_weight_measurements(entries, source="Apple Health Weight", file_hash=None, notes=""):
    if not entries:
        return 0
    now = datetime.now().isoformat(timespec="seconds")
    saved = 0
    c = conn()
    for entry in entries:
        weight = entry.get("weight_lbs")
        measured_at = entry.get("measured_at")
        if weight is None or float(weight) <= 0 or not measured_at:
            continue
        log_date = entry.get("log_date") or str(measured_at)[:10]
        c.execute(
            """
            INSERT INTO weight_measurements
                (measured_at, log_date, weight_lbs, source, file_hash, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(measured_at, weight_lbs) DO UPDATE SET
                log_date=excluded.log_date,
                source=excluded.source,
                file_hash=COALESCE(excluded.file_hash, weight_measurements.file_hash),
                notes=excluded.notes
            """,
            (str(measured_at), str(log_date), float(weight), source, file_hash, notes, now),
        )
        saved += 1
    c.commit()
    c.close()
    return saved


def sync_daily_log_from_weight_entries(entries, source="Apple Health Weight", source_path=None):
    """Update daily_log with the latest weight per calendar day."""
    if not entries:
        return
    by_date = {}
    for entry in entries:
        log_date = entry.get("log_date") or str(entry.get("measured_at", ""))[:10]
        weight = entry.get("weight_lbs")
        measured_at = entry.get("measured_at") or log_date
        if not log_date or weight is None:
            continue
        prior = by_date.get(log_date)
        if not prior or str(measured_at) > str(prior["measured_at"]):
            by_date[log_date] = {"weight_lbs": float(weight), "measured_at": measured_at}
    for log_date, payload in by_date.items():
        upsert_daily(
            {
                "log_date": log_date,
                "weight_lbs": payload["weight_lbs"],
                "measured_at": payload["measured_at"],
                "_data_ts": payload["measured_at"],
                "notes": f"{source} screenshot OCR",
            },
            source=source,
            source_path=source_path,
        )


def upsert_weight_from_screenshot(parsed, log_day, source_dtype, file_hash=None, source_path=None):
    if source_dtype == "Apple Health Weight" and parsed.get("weight_entries"):
        notes = tag_import_notes("Apple Health Weight", "OCR weight log import")
        save_weight_measurements(
            parsed["weight_entries"],
            source=source_dtype,
            file_hash=file_hash,
            notes=notes,
        )
        sync_daily_log_from_weight_entries(parsed["weight_entries"], source=source_dtype, source_path=source_path)
        return True
    weight = parsed.get("weight_lbs")
    if weight is None or float(weight) <= 0:
        return False
    source = "Apple Health Weight" if source_dtype == "Apple Health Weight" else "Scale"
    return upsert_daily(
        {
            "log_date": log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day),
            "weight_lbs": float(weight),
            "notes": f"{source} screenshot OCR",
        },
        source=source,
        source_path=source_path,
        file_hash=file_hash,
        data_ts=parse_document_timestamp(source_path, log_day),
    )

def fatsecret_screenshot_notes(parsed):
    extras = []
    if parsed.get("fiber_g"):
        extras.append(f"fiber_g={parsed['fiber_g']:.1f}")
    if parsed.get("sodium_mg"):
        extras.append(f"sodium_mg={parsed['sodium_mg']:.0f}")
    base = "FatSecret screenshot OCR"
    return f"{base} | {', '.join(extras)}" if extras else base


def upsert_fatsecret_from_screenshot(parsed, log_day, source_path=None):
    if not parsed.get("calories"):
        return False
    notes = fatsecret_screenshot_notes(parsed)
    if source_path:
        notes = f"{notes} | {Path(source_path).name}"
    row = {
        "log_date": log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day),
        "calories": parsed.get("calories"),
        "protein_g": parsed.get("protein_g"),
        "carbs_g": parsed.get("carbs_g"),
        "fat_g": parsed.get("fat_g"),
        "notes": notes,
    }
    return upsert_daily(row, source="FatSecret", source_path=source_path)


def oura_activity_screenshot_notes(parsed):
    bits = ["Oura Activity OCR"]
    goal = parsed.get("oura_goal_progress")
    if goal:
        bits.append(f"goal_progress={goal}")
    activity_time = parsed.get("oura_activity_time_min")
    if activity_time is not None:
        bits.append(f"activity_time={int(activity_time)}min")
    return " | ".join(bits)


def oura_sleep_screenshot_notes(parsed):
    bits = ["Oura Sleep OCR"]
    if parsed.get("sleep_score"):
        bits.append(f"sleep_score={int(parsed['sleep_score'])}")
    if parsed.get("readiness_score"):
        bits.append(f"readiness={int(parsed['readiness_score'])}")
    if parsed.get("sleep_minutes"):
        hours = int(parsed["sleep_minutes"]) // 60
        mins = int(parsed["sleep_minutes"]) % 60
        bits.append(f"sleep={hours}h{mins:02d}m")
    return " | ".join(bits)


def oura_screenshot_notes(parsed):
    has_activity = any(parsed.get(k) for k in ("oura_burn", "active_energy", "oura_goal_progress"))
    has_sleep = any(parsed.get(k) for k in ("sleep_score", "readiness_score", "sleep_minutes"))
    if has_activity and has_sleep:
        return oura_activity_screenshot_notes(parsed) + " | " + oura_sleep_screenshot_notes(parsed)
    if has_sleep:
        return oura_sleep_screenshot_notes(parsed)
    return oura_activity_screenshot_notes(parsed)


def oura_has_sync_fields(parsed):
    if not parsed:
        return False
    keys = (
        "oura_burn", "active_energy", "sleep_score", "readiness_score",
        "sleep_minutes", "steps",
    )
    return any(parsed.get(k) not in (None, "", 0) for k in keys)


def _oura_activity_labels_on_line(line):
    found = []
    for key, patterns in OURA_ACTIVITY_LABEL_SPECS:
        pats = patterns if isinstance(patterns, (list, tuple)) else [patterns]
        for pat in pats:
            for match in pat.finditer(line):
                found.append((match.start(), key))
                break
    found.sort(key=lambda item: item[0])
    ordered = []
    seen = set()
    for _, key in found:
        if key not in seen:
            seen.add(key)
            ordered.append(key)
    return ordered


def _oura_activity_value_chunks(line):
    line = str(line or "").strip()
    parts = re.split(r"\s{2,}|\t", line)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]
    tokens = line.split()
    chunks = []
    idx = 0
    while idx < len(tokens):
        if idx + 2 < len(tokens) and tokens[idx + 1] == "/":
            chunks.append(f"{tokens[idx]} / {tokens[idx + 2]}")
            idx += 3
            continue
        chunks.append(tokens[idx])
        idx += 1
    return chunks


def _oura_label_patterns_for_key(field_key):
    for key, patterns in OURA_ACTIVITY_LABEL_SPECS:
        if key == field_key:
            return patterns if isinstance(patterns, (list, tuple)) else [patterns]
    return []


def _oura_parse_near_label_line(line, field_key):
    """Same-line fallback: label followed by value on one OCR line."""
    for pat in _oura_label_patterns_for_key(field_key):
        match = pat.search(line)
        if not match:
            continue
        tail = line[match.end() :].strip()
        if not tail:
            continue
        parsed_val = _parse_oura_activity_field(field_key, tail)
        if parsed_val is not None:
            return parsed_val, tail, line
    return None, None, None


def _oura_extract_field_evidence(text):
    """Capture raw OCR snippets per field for learning and wizard hints."""
    evidence = {}
    if not text:
        return evidence

    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if ln]

    for idx in range(len(lines) - 1):
        label_keys = _oura_activity_labels_on_line(lines[idx])
        if not label_keys:
            continue
        value_chunks = _oura_activity_value_chunks(lines[idx + 1])
        for label_idx, key in enumerate(label_keys):
            if label_idx >= len(value_chunks):
                continue
            if key in evidence:
                continue
            evidence[key] = {
                "raw_snippet": value_chunks[label_idx],
                "label_context": lines[idx],
                "value_line": lines[idx + 1],
                "column_index": label_idx,
            }

    for key, _ in OURA_ACTIVITY_LABEL_SPECS:
        if key in evidence:
            continue
        for line in lines:
            parsed_val, raw_snippet, label_context = _oura_parse_near_label_line(line, key)
            if parsed_val is not None:
                evidence[key] = {
                    "raw_snippet": raw_snippet or "",
                    "label_context": label_context or "",
                    "value_line": line,
                    "column_index": None,
                }
                break

    for key, patterns in OURA_SLEEP_LABEL_SPECS:
        if key in evidence:
            continue
        for idx, line in enumerate(lines):
            if not any(pat.search(line) for pat in patterns):
                continue
            value_line = lines[idx + 1] if idx + 1 < len(lines) else line
            if key == "sleep_minutes":
                m = re.search(r"(\d+)\s*h\s*(\d+)\s*m", value_line, re.I)
                if m:
                    evidence[key] = {
                        "raw_snippet": m.group(0),
                        "label_context": line,
                        "value_line": value_line,
                        "column_index": None,
                    }
                    break
            m = re.search(r"(\d{1,3})", value_line.replace(",", ""))
            if m:
                evidence[key] = {
                    "raw_snippet": m.group(0),
                    "label_context": line,
                    "value_line": value_line,
                    "column_index": None,
                }
                break
    return evidence


def _fatsecret_extract_field_evidence(text):
    evidence = {}
    if not text:
        return evidence
    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if ln]
    for idx in range(len(lines) - 1):
        label_keys = _fatsecret_labels_on_line(lines[idx])
        if not label_keys:
            continue
        value_nums = _fatsecret_collect_summary_values(lines[idx], lines[idx + 1], len(label_keys))
        if not value_nums:
            value_nums = _fatsecret_numbers_on_line(lines[idx + 1])
        value_line = lines[idx + 1]
        for label_idx, key in enumerate(label_keys):
            if label_idx >= len(value_nums):
                continue
            if key in evidence:
                continue
            evidence[key] = {
                "raw_snippet": str(value_nums[label_idx]),
                "label_context": lines[idx],
                "value_line": value_line,
                "column_index": label_idx,
            }
    return evidence


def _dexa_apply_gram_fields(out):
    """Convert FITLAB/Hologic gram columns to the lb fields used by the app."""
    out = dict(out or {})
    if out.get("fat_mass_g") and not out.get("fat_mass_lbs"):
        out["fat_mass_lbs"] = _dexa_grams_to_lbs(out["fat_mass_g"])
    if out.get("lean_bmc_g") and not out.get("lean_mass_lbs"):
        out["lean_mass_lbs"] = _dexa_grams_to_lbs(out["lean_bmc_g"])
    if out.get("total_mass_g") and not out.get("weight_lbs"):
        out["weight_lbs"] = _dexa_grams_to_lbs(out["total_mass_g"])
    return out


def _dexa_extract_field_evidence(text):
    evidence = {}
    if not text:
        return evidence
    specs = [
        ("scan_date", r"(?:scan\s*date|date\s*of\s*scan)[^\n]{0,40}(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})"),
        ("weight_lbs", r"weight[^0-9\n]{0,25}([\d.]+)\s*lb"),
        ("body_fat_pct", r"(?:total\s+body\s+)?%?\s*fat[^0-9\n]{0,20}([\d.]+)"),
        ("fat_mass_lbs", r"fat\s*mass[^0-9\n]{0,20}([\d.]+)\s*lb"),
        ("lean_mass_lbs", r"lean(?:\s*\+\s*bmc|\s*mass)?[^0-9\n]{0,20}([\d.]+)\s*lb"),
        ("vat_mass_g", r"(?:est\.\s*)?vat[^0-9\n]{0,15}([\d.]+)\s*g"),
    ]
    for key, pat in specs:
        match = re.search(pat, text, re.I)
        if match:
            evidence[key] = {
                "raw_snippet": match.group(1),
                "label_context": match.group(0)[:120],
                "value_line": "",
                "column_index": None,
            }

    gram_specs = [
        ("fat_mass_g", r"fat\s*mass[^0-9\n]{0,40}([\d.,]+)\s*g"),
        ("lean_bmc_g", r"lean\s*\+\s*bmc[^0-9\n]{0,40}([\d.,]+)\s*g"),
        ("total_mass_g", r"total\s*mass[^0-9\n]{0,40}([\d.,]+)\s*g"),
    ]
    for key, pat in gram_specs:
        match = re.search(pat, text, re.I)
        if match:
            grams = float(match.group(1).replace(",", ""))
            evidence[key] = {
                "raw_snippet": f"{grams} g",
                "label_context": match.group(0)[:120],
                "value_line": "",
                "column_index": None,
            }
            lb_key = {
                "fat_mass_g": "fat_mass_lbs",
                "lean_bmc_g": "lean_mass_lbs",
                "total_mass_g": "weight_lbs",
            }[key]
            evidence.setdefault(
                lb_key,
                {
                    "raw_snippet": f"{grams} g = {_dexa_grams_to_lbs(grams)} lb",
                    "label_context": match.group(0)[:120],
                    "value_line": "",
                    "column_index": None,
                },
            )

    parsed_row = _dexa_apply_gram_fields(_parse_dexa_composition_total_row(text))
    for gram_key, lb_key in (
        ("fat_mass_g", "fat_mass_lbs"),
        ("lean_bmc_g", "lean_mass_lbs"),
        ("total_mass_g", "weight_lbs"),
    ):
        grams = parsed_row.get(gram_key)
        lbs = parsed_row.get(lb_key)
        if grams and lb_key not in evidence:
            evidence[gram_key] = {
                "raw_snippet": f"{grams} g",
                "label_context": "DXA Results Summary Total row",
                "value_line": "",
                "column_index": None,
            }
            evidence[lb_key] = {
                "raw_snippet": f"{grams} g = {lbs} lb",
                "label_context": "DXA Results Summary Total row",
                "value_line": "",
                "column_index": None,
            }
    if parsed_row.get("body_fat_pct") and "body_fat_pct" not in evidence:
        evidence["body_fat_pct"] = {
            "raw_snippet": str(parsed_row["body_fat_pct"]),
            "label_context": "DXA Results Summary Total row % Fat",
            "value_line": "",
            "column_index": None,
        }
    return evidence


def _workout_extract_field_evidence(text):
    evidence = {}
    if not text:
        return evidence
    match = re.search(r"(?:calories|burn|energy)[^0-9]{0,15}([\d,]{2,5})", text, re.I)
    if match:
        evidence["active_energy"] = {
            "raw_snippet": match.group(1),
            "label_context": match.group(0)[:80],
            "value_line": "",
            "column_index": None,
        }
    exercise_names = [
        "bench press", "squat", "deadlift", "overhead press", "row", "pull-up", "pull up",
        "lat pulldown", "leg press", "romanian deadlift", "incline press",
    ]
    low = text.lower()
    for name in exercise_names:
        if name in low:
            idx = low.find(name)
            evidence["workout"] = {
                "raw_snippet": text[idx : idx + len(name)],
                "label_context": name,
                "value_line": "",
                "column_index": None,
            }
            break
    return evidence


def _scale_extract_field_evidence(text):
    evidence = {}
    if not text:
        return evidence
    norm = normalize_ocr_for_classification(text)
    match = re.search(r"(\d{2,3}(?:\.\d)?)\s*(?:lbs?|lb\.?)\b", norm, re.I)
    if match:
        evidence["weight_lbs"] = {
            "raw_snippet": match.group(0),
            "label_context": match.group(0),
            "value_line": "",
            "column_index": None,
        }
        return evidence
    match = re.search(r"(\d{2,3}(?:\.\d)?)\s*(?:kg|kilograms?)\b", text, re.I)
    if match:
        evidence["weight_lbs"] = {
            "raw_snippet": match.group(0),
            "label_context": match.group(0),
            "value_line": "",
            "column_index": None,
        }
    return evidence


def extract_ocr_field_evidence(dtype, text):
    if dtype == "FatSecret":
        return _fatsecret_extract_field_evidence(text)
    if dtype == "Oura":
        return _oura_extract_field_evidence(text)
    if dtype == "DEXA":
        return _dexa_extract_field_evidence(text)
    if dtype == "Workout":
        return _workout_extract_field_evidence(text)
    if dtype in ("Scale", "Apple Health Weight"):
        return _scale_extract_field_evidence(text)
    return {}


def _normalize_ocr_snippet(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _coerce_learned_value(field_key, corrected_str):
    if corrected_str is None or corrected_str == "":
        return None
    if field_key in OCR_TEXT_FIELD_KEYS:
        return str(corrected_str)
    if field_key == "oura_activity_time_min":
        try:
            return int(float(corrected_str))
        except (TypeError, ValueError):
            return None
    try:
        return float(str(corrected_str).replace(",", ""))
    except (TypeError, ValueError):
        return corrected_str


def save_ocr_field_correction(document_type, field_key, raw_snippet, ocr_extracted, corrected_value, label_context=""):
    corrected_str = str(corrected_value)
    ocr_str = "" if ocr_extracted is None else str(ocr_extracted)
    raw_norm = _normalize_ocr_snippet(raw_snippet)
    now = datetime.now().isoformat(timespec="seconds")
    c = conn()
    row = c.execute(
        """
        SELECT id, use_count FROM ocr_field_corrections
        WHERE document_type = ? AND field_key = ?
          AND COALESCE(raw_snippet, '') = ? AND COALESCE(ocr_extracted, '') = ?
          AND corrected_value = ?
        """,
        (document_type, field_key, raw_norm, ocr_str, corrected_str),
    ).fetchone()
    if row:
        c.execute(
            """
            UPDATE ocr_field_corrections
            SET use_count = ?, updated_at = ?, label_context = COALESCE(?, label_context)
            WHERE id = ?
            """,
            (int(row[1]) + 1, now, label_context or None, row[0]),
        )
    else:
        c.execute(
            """
            INSERT INTO ocr_field_corrections
            (document_type, field_key, raw_snippet, ocr_extracted, corrected_value, label_context, use_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (document_type, field_key, raw_norm, ocr_str, corrected_str, label_context or "", now, now),
        )
    c.commit()
    c.close()


def lookup_learned_ocr_value(document_type, field_key, raw_snippet=None, ocr_extracted=None):
    c = conn()
    raw_norm = _normalize_ocr_snippet(raw_snippet)
    ocr_str = "" if ocr_extracted is None else str(ocr_extracted)

    if raw_norm:
        row = c.execute(
            """
            SELECT corrected_value, use_count FROM ocr_field_corrections
            WHERE document_type = ? AND field_key = ? AND raw_snippet = ?
            ORDER BY use_count DESC, updated_at DESC LIMIT 1
            """,
            (document_type, field_key, raw_norm),
        ).fetchone()
        if row:
            c.close()
            return _coerce_learned_value(field_key, row[0])

    if ocr_str:
        row = c.execute(
            """
            SELECT corrected_value, use_count FROM ocr_field_corrections
            WHERE document_type = ? AND field_key = ? AND ocr_extracted = ?
            ORDER BY use_count DESC, updated_at DESC LIMIT 1
            """,
            (document_type, field_key, ocr_str),
        ).fetchone()
        if row:
            c.close()
            return _coerce_learned_value(field_key, row[0])

    c.close()
    return None


def apply_learned_ocr_to_parsed(document_type, parsed, evidence=None):
    parsed = dict(parsed or {})
    evidence = evidence or {}
    for field_key, ev in evidence.items():
        raw = ev.get("raw_snippet")
        current = parsed.get(field_key)
        learned = lookup_learned_ocr_value(
            document_type,
            field_key,
            raw_snippet=raw,
            ocr_extracted=current if current is not None else None,
        )
        if learned is not None:
            parsed[field_key] = learned
            continue
        if current is None or current == 0 or current == "":
            learned = lookup_learned_ocr_value(document_type, field_key, raw_snippet=raw)
            if learned is not None:
                parsed[field_key] = learned
    return parsed


def record_ocr_validation_corrections(document_type, ocr_original, final_values, evidence=None):
    evidence = evidence or {}
    for field_key, final_val in (final_values or {}).items():
        if field_key in OCR_DATE_FIELD_KEYS:
            continue
        orig_val = (ocr_original or {}).get(field_key)
        if _ocr_values_equivalent(field_key, orig_val, final_val):
            continue
        ev = evidence.get(field_key, {})
        save_ocr_field_correction(
            document_type,
            field_key,
            ev.get("raw_snippet", ""),
            orig_val,
            final_val,
            label_context=ev.get("label_context", ""),
        )


def count_ocr_field_corrections(document_type=None):
    c = conn()
    if document_type:
        row = c.execute(
            "SELECT COUNT(*), COALESCE(SUM(use_count), 0) FROM ocr_field_corrections WHERE document_type = ?",
            (document_type,),
        ).fetchone()
    else:
        row = c.execute("SELECT COUNT(*), COALESCE(SUM(use_count), 0) FROM ocr_field_corrections").fetchone()
    c.close()
    return int(row[0] or 0), int(row[1] or 0)


def get_ocr_type_trust(document_type):
    c = conn()
    row = c.execute(
        "SELECT auto_confirm_enabled, clean_confirmations, updated_at FROM ocr_type_trust WHERE document_type = ?",
        (document_type,),
    ).fetchone()
    c.close()
    if not row:
        return {"auto_confirm_enabled": False, "clean_confirmations": 0, "updated_at": ""}
    return {
        "auto_confirm_enabled": bool(row[0]),
        "clean_confirmations": int(row[1] or 0),
        "updated_at": row[2] or "",
    }


def ocr_type_auto_confirm_enabled(document_type):
    return get_ocr_type_trust(document_type).get("auto_confirm_enabled", False)


def list_ocr_auto_confirm_types():
    c = conn()
    try:
        rows = c.execute(
            "SELECT document_type FROM ocr_type_trust WHERE auto_confirm_enabled = 1 ORDER BY document_type"
        ).fetchall()
    except Exception:
        rows = []
    c.close()
    return [row[0] for row in rows]


def record_ocr_type_validation_outcome(document_type, had_corrections):
    """After manual validation: trust the type when OCR needed no fixes; reset trust on corrections."""
    now = datetime.now().isoformat(timespec="seconds")
    trust = get_ocr_type_trust(document_type)
    c = conn()
    if had_corrections:
        c.execute(
            """
            INSERT INTO ocr_type_trust (document_type, auto_confirm_enabled, clean_confirmations, updated_at)
            VALUES (?, 0, 0, ?)
            ON CONFLICT(document_type) DO UPDATE SET
                auto_confirm_enabled = 0,
                clean_confirmations = 0,
                updated_at = excluded.updated_at
            """,
            (document_type, now),
        )
        c.commit()
        c.close()
        return {"trusted_now": False, "auto_confirm_enabled": False, "clean_confirmations": 0}

    clean = int(trust.get("clean_confirmations") or 0) + 1
    auto_on = clean >= OCR_CLEAN_CONFIRMATIONS_TO_TRUST
    c.execute(
        """
        INSERT INTO ocr_type_trust (document_type, auto_confirm_enabled, clean_confirmations, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(document_type) DO UPDATE SET
            auto_confirm_enabled = excluded.auto_confirm_enabled,
            clean_confirmations = excluded.clean_confirmations,
            updated_at = excluded.updated_at
        """,
        (document_type, 1 if auto_on else 0, clean, now),
    )
    c.commit()
    c.close()
    return {
        "trusted_now": auto_on and not trust.get("auto_confirm_enabled"),
        "auto_confirm_enabled": auto_on,
        "clean_confirmations": clean,
    }


OCR_NUMERIC_FIELD_KEYS = frozenset({
    "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sodium_mg",
    "weight_lbs", "body_fat_pct", "fat_mass_lbs", "lean_mass_lbs", "vat_mass_g",
    "active_energy", "oura_burn", "sleep_score", "readiness_score", "sleep_minutes",
    "workout_intensity", "oura_activity_time_min",
})


def _ocr_values_equivalent(field_key, left, right):
    if left == right:
        return True
    if left in (None, "", 0) and right in (None, "", 0):
        return True
    if field_key in OCR_NUMERIC_FIELD_KEYS:
        try:
            return abs(float(left) - float(right)) < 0.55
        except (TypeError, ValueError):
            pass
    return str(left).strip() == str(right).strip()


def _ocr_field_values_differ(field_key, orig, final):
    if field_key in OCR_DATE_FIELD_KEYS:
        return False
    return not _ocr_values_equivalent(field_key, orig, final)


def _ocr_queue_user_reviewed(qr):
    notes = str(qr.get("notes") or "").lower()
    return any(
        token in notes
        for token in (
            "confirmed and imported",
            "confirmed — skipped",
            "user skipped",
            "user_validated",
            "mark as reviewed",
        )
    )


def _backfill_fatsecret_parsed_from_daily(parsed, daily_df, log_day):
    data = get_fatsecret_day_data(daily_df, log_day)
    if not data:
        return parsed, False
    out = dict(parsed or {})
    changed = False
    for key in ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sodium_mg"):
        if out.get(key) in (None, "", 0) and data.get(key) is not None:
            out[key] = data[key]
            changed = True
    return out, changed


def _ocr_validation_had_corrections(dtype, ocr_original, final_values):
    for step in OCR_VALIDATION_STEPS.get(dtype, []):
        fk = step["key"]
        if _ocr_field_values_differ(fk, (ocr_original or {}).get(fk), (final_values or {}).get(fk)):
            return True
    return False


def build_auto_confirm_values(qr, dtype):
    ocr_text = qr.get("ocr_text") if hasattr(qr, "get") else qr["ocr_text"]
    ocr_text = ocr_text or ""
    parsed = json.loads(qr.get("parsed_json") or "{}") if hasattr(qr, "get") else json.loads(qr["parsed_json"] or "{}")
    evidence = extract_ocr_field_evidence(dtype, ocr_text)
    if ocr_text:
        raw_parsed = parse_by_type(dtype, ocr_text, apply_learning=False)
    else:
        raw_parsed = dict(parsed)
    values = apply_learned_ocr_to_parsed(dtype, dict(raw_parsed), evidence)
    if dtype == "DEXA":
        values["scan_date"] = values.get("scan_date") or _dexa_default_scan_date(values, qr["stored_path"]).isoformat()
    elif dtype in ("FatSecret", "Oura", "Workout", "Scale", "Apple Health Weight"):
        values["log_date"] = values.get("log_date") or parse_inbox_image_date(qr["stored_path"]).isoformat()
    return values, raw_parsed


def _ocr_auto_confirm_has_data(dtype, values):
    if dtype == "FatSecret":
        cal = (values or {}).get("calories")
        try:
            return cal is not None and float(cal) > 0
        except (TypeError, ValueError):
            return False
    if dtype == "Apple Health Weight":
        entries = (values or {}).get("weight_entries") or []
        if entries:
            return True
    for step in OCR_VALIDATION_STEPS.get(dtype, []):
        fk = step["key"]
        if fk in OCR_DATE_FIELD_KEYS:
            continue
        val = (values or {}).get(fk)
        if val not in (None, "", 0):
            return True
    return bool((values or {}).get("log_date") or (values or {}).get("scan_date"))


def try_auto_confirm_ocr_item(qr):
    dtype = qr["detected_type"]
    if dtype not in OCR_WIZARD_TYPES:
        return False
    if str(qr.get("status") or "") != "pending_confirmation":
        return False
    if not ocr_type_auto_confirm_enabled(dtype):
        return False

    final_values, _raw_parsed = build_auto_confirm_values(qr, dtype)
    if not _ocr_auto_confirm_has_data(dtype, final_values):
        return False
    import_confirmed_queue_item(qr, final_values)
    return True


def try_auto_confirm_ocr_by_hash(file_hash):
    c = conn()
    try:
        df = pd.read_sql(
            "SELECT * FROM ocr_queue WHERE file_hash = ? AND status = 'pending_confirmation'",
            c,
            params=(file_hash,),
        )
    except Exception:
        df = pd.DataFrame()
    c.close()
    if df.empty:
        return False
    return try_auto_confirm_ocr_item(df.iloc[0])


def auto_confirm_pending_ocr_items():
    qdf = load_ocr_review_queue()
    if qdf.empty:
        return []
    auto_confirmed = []
    for _, qr in qdf.iterrows():
        if try_auto_confirm_ocr_item(qr):
            auto_confirmed.append(qr)
    return auto_confirmed


def _parse_oura_activity_field(key, raw):
    raw = re.sub(r"(?i)\bcal\b", "", str(raw or "")).strip()
    if not raw:
        return None
    if key == "oura_goal_progress":
        match = re.search(r"([\d.]+)\s*/\s*([\d.]+)", raw)
        if match:
            left = match.group(1)
            right = match.group(2)
            left_fmt = str(int(float(left))) if float(left).is_integer() else left
            right_fmt = str(int(float(right))) if float(right).is_integer() else right
            return f"{left_fmt} / {right_fmt}"
        return raw
    if key == "oura_activity_time_min":
        low = raw.lower()
        match = re.search(r"(\d+)\s*h(?:ours?)?\s*(\d+)\s*m(?:in(?:ute)?s?)?", low)
        if match:
            return int(match.group(1)) * 60 + int(match.group(2))
        match = re.search(r"(\d+)\s*m(?:in(?:ute)?s?)?", low)
        if match:
            return int(match.group(1))
        match = re.search(r"^(\d+)$", raw)
        return int(match.group(1)) if match else None
    match = re.search(r"([\d,]+\.?\d*)", raw.replace(",", ""))
    return float(match.group(1)) if match else None


def _parse_oura_activity_vertical(text):
    """Find Oura Activity labels and read the value directly below each column."""
    out = {}
    if not text:
        return out

    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if ln]

    candidate_pairs = []
    for idx in range(len(lines) - 1):
        label_keys = _oura_activity_labels_on_line(lines[idx])
        if not label_keys:
            continue
        value_chunks = _oura_activity_value_chunks(lines[idx + 1])
        if len(value_chunks) < len(label_keys):
            continue
        pair = {}
        for label_idx, key in enumerate(label_keys):
            parsed_val = _parse_oura_activity_field(key, value_chunks[label_idx])
            if parsed_val is not None:
                pair[key] = parsed_val
        if not pair:
            continue
        score = len(pair)
        if "oura_burn" in pair:
            score += 20
        if "active_energy" in pair:
            score += 10
        candidate_pairs.append((score, pair))

    for idx in range(len(lines) - 1):
        label_keys = _oura_activity_labels_on_line(lines[idx])
        if len(label_keys) != 1:
            continue
        key = label_keys[0]
        parsed_val = _parse_oura_activity_field(key, lines[idx + 1])
        if parsed_val is not None:
            candidate_pairs.append((12 if key == "oura_burn" else 8, {key: parsed_val}))

    for key, _ in OURA_ACTIVITY_LABEL_SPECS:
        for line in lines:
            parsed_val, _, _ = _oura_parse_near_label_line(line, key)
            if parsed_val is not None:
                candidate_pairs.append((14 if key == "oura_burn" else 9, {key: parsed_val}))
                break

    if not candidate_pairs:
        return out

    candidate_pairs.sort(key=lambda item: item[0], reverse=True)
    for _, pair in candidate_pairs:
        for key, value in pair.items():
            if key not in out:
                out[key] = value
    return out


def _parse_oura_sleep_vertical(text):
    out = {}
    if not text:
        return out
    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if ln]
    for idx in range(len(lines) - 1):
        label_line = lines[idx]
        value_line = lines[idx + 1]
        for key, patterns in OURA_SLEEP_LABEL_SPECS:
            if key in out:
                continue
            if not any(pat.search(label_line) for pat in patterns):
                continue
            if key == "sleep_minutes":
                m = re.search(r"(\d+)\s*h\s*(\d+)\s*m", value_line, re.I)
                if m:
                    out[key] = int(m.group(1)) * 60 + int(m.group(2))
                    continue
                m = re.search(r"(\d{1,2}):(\d{2})", value_line)
                if m:
                    out[key] = int(m.group(1)) * 60 + int(m.group(2))
                    continue
            m = re.search(r"(\d{1,3})", value_line.replace(",", ""))
            if m:
                out[key] = float(m.group(1))
    return out


def parse_oura_ocr(text, apply_learning=True):
    out = {}
    if not text:
        return out

    evidence = _oura_extract_field_evidence(text)
    out.update(_parse_oura_activity_vertical(text))
    out.update(_parse_oura_sleep_vertical(text))

    patterns = [
        ("sleep_score", r"sleep\s*(?:score)?[^0-9]{0,20}(\d{1,3})"),
        ("readiness_score", r"readiness[^0-9]{0,20}(\d{1,3})"),
        ("steps", r"steps[^0-9]{0,20}([\d,]{3,7})"),
    ]
    for key, pat in patterns:
        if key in out:
            continue
        m = re.search(pat, text, re.I)
        if m:
            out[key] = float(m.group(1).replace(",", ""))

    if "notes" not in out:
        m = re.search(r"hrv[^0-9]{0,20}([\d.]+)", text, re.I)
        if m:
            out["notes"] = f"HRV {m.group(1)}"
    m = re.search(r"recovery[^0-9]{0,20}(\d{1,3})", text, re.I)
    if m and "readiness_score" not in out:
        out["readiness_score"] = float(m.group(1))

    if "sleep_minutes" not in out and "oura_activity_time_min" not in out:
        m = re.search(r"total\s+sleep[^0-9]{0,20}(\d+)\s*h\s*(\d+)\s*m", text, re.I)
        if m:
            out["sleep_minutes"] = int(m.group(1)) * 60 + int(m.group(2))
        m = re.search(r"(\d+)\s*h\s*(\d+)\s*m", text, re.I)
        if m and not re.search(r"activity\s+time", text, re.I):
            out["sleep_minutes"] = int(m.group(1)) * 60 + int(m.group(2))
        m = re.search(r"(\d{1,2}):(\d{2})\s*(?:total|sleep)", text, re.I)
        if m:
            out["sleep_minutes"] = int(m.group(1)) * 60 + int(m.group(2))

    if apply_learning:
        out = apply_learned_ocr_to_parsed("Oura", out, evidence)
    if out.get("oura_burn") or out.get("active_energy") or out.get("sleep_score") or out.get("sleep_minutes"):
        out["notes"] = oura_screenshot_notes(out)
    return out


def _dexa_grams_to_lbs(grams):
    return round(float(grams) / 453.592, 2)


def _mass_to_lbs(value, unit):
    val = float(value or 0)
    if unit == "lb":
        return round(val, 2)
    if unit == "g":
        return _dexa_grams_to_lbs(val)
    if unit == "kg":
        return round(val * 1000.0 / 453.592, 2)
    return round(val, 2)


def _mass_from_lbs(lbs, unit):
    val = float(lbs or 0)
    if unit == "lb":
        return round(val, 2)
    if unit == "g":
        return round(val * 453.592, 1)
    if unit == "kg":
        return round(val * 453.592 / 1000.0, 2)
    return val


def _dexa_default_mass_unit(field_key, ocr_original, values):
    spec = DEXA_MASS_UNIT_FIELDS.get(field_key, {})
    gram_key = spec.get("gram_key")
    lbs_val = float((values or {}).get(field_key) or (ocr_original or {}).get(field_key) or 0)
    if field_key == "weight_lbs" and 80 <= lbs_val <= 400:
        return "lb"
    if gram_key and ((values or {}).get(gram_key) or (ocr_original or {}).get(gram_key)):
        return "g"
    return spec.get("default_unit", "lb")


def _dexa_mass_display_value(field_key, unit, values, ocr_original):
    spec = DEXA_MASS_UNIT_FIELDS.get(field_key, {})
    gram_key = spec.get("gram_key")
    stored_lbs = float((values or {}).get(field_key) or 0)
    if unit == "g" and gram_key:
        grams = (values or {}).get(gram_key) or (ocr_original or {}).get(gram_key)
        if grams and stored_lbs == 0:
            return float(grams)
    if stored_lbs:
        return _mass_from_lbs(stored_lbs, unit)
    if unit == "g" and gram_key:
        grams = (values or {}).get(gram_key) or (ocr_original or {}).get(gram_key)
        if grams:
            return float(grams)
    return 0.0


def _dexa_is_body_fat_pct(value):
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return False
    return 3.0 <= pct <= 65.0


def _dexa_parse_floats_from_text(chunk):
    return [float(token.replace(",", "")) for token in re.findall(r"\d[\d,]*\.?\d*|\.\d+", str(chunk or ""))]


def _dexa_row_from_three_numbers(nums):
    """FITLAB compact table: Fat Mass (g), Lean + BMC (g), % Fat on the Total row."""
    if len(nums) < 3:
        return None
    fat_g, lean_bmc_g, pct = nums[-3:]
    if not _dexa_is_body_fat_pct(pct):
        return None
    if fat_g <= 0 or lean_bmc_g <= 0:
        return None
    # Whole-body Total row — reject regional rows (e.g. Head ~1300 g fat).
    if fat_g < 8000 or lean_bmc_g < 30000:
        return None
    total_g = fat_g + lean_bmc_g
    return {
        "body_fat_pct": round(float(pct), 1),
        "fat_mass_lbs": _dexa_grams_to_lbs(fat_g),
        "lean_mass_lbs": _dexa_grams_to_lbs(lean_bmc_g),
        "weight_lbs": _dexa_grams_to_lbs(total_g),
        "fat_mass_g": round(float(fat_g), 1),
        "lean_bmc_g": round(float(lean_bmc_g), 1),
        "total_mass_g": round(float(total_g), 1),
    }


def _dexa_row_from_four_numbers_lb(nums):
    """FITLAB lb table: Fat Mass (lb), Lean+BMC (lb), Total Mass (lb), % Fat."""
    if len(nums) < 4:
        return None
    fat_lb, lean_bmc_lb, total_lb, pct = nums[-4:]
    if not _dexa_is_body_fat_pct(pct):
        return None
    if fat_lb <= 0 or lean_bmc_lb <= 0 or total_lb <= 0:
        return None
    if fat_lb > 120 or lean_bmc_lb > 300 or total_lb > 400:
        return None
    return {
        "body_fat_pct": round(float(pct), 1),
        "fat_mass_lbs": round(float(fat_lb), 2),
        "lean_mass_lbs": round(float(lean_bmc_lb), 2),
        "weight_lbs": round(float(total_lb), 2),
    }


def _dexa_coalesce_total_row(row_nums):
    """Accept FITLAB Total rows in lb (4-col), full 6-column g, or compact 3-column g."""
    return (
        _dexa_row_from_four_numbers_lb(row_nums)
        or _dexa_row_from_six_numbers(row_nums)
        or _dexa_row_from_three_numbers(row_nums)
    )


def _dexa_row_from_six_numbers(nums):
    """Hologic/FITLAB Total row: BMC, Fat Mass, Lean Mass, Lean+BMC, Total Mass (g), % Fat."""
    if len(nums) < 6:
        return None
    bmc_g, fat_g, lean_g, lean_bmc_g, total_g, pct = nums[-6:]
    if not _dexa_is_body_fat_pct(pct):
        return None
    if fat_g <= 0 or lean_bmc_g <= 0 or total_g <= 0:
        return None
    return {
        "body_fat_pct": round(float(pct), 1),
        "fat_mass_lbs": _dexa_grams_to_lbs(fat_g),
        "lean_mass_lbs": _dexa_grams_to_lbs(lean_bmc_g),
        "weight_lbs": _dexa_grams_to_lbs(total_g),
        "fat_mass_g": round(float(fat_g), 1),
        "lean_bmc_g": round(float(lean_bmc_g), 1),
        "total_mass_g": round(float(total_g), 1),
        "bmc_g": round(float(bmc_g), 2),
    }


def _parse_dexa_scan_date(text):
    match = re.search(r"Scan\s*Date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})", text, re.I)
    if match:
        try:
            return pd.to_datetime(match.group(1)).date().isoformat()
        except Exception:
            pass
    match = re.search(r"Scan\s*Date[:\s]+(\d{4}-\d{2}-\d{2})", text, re.I)
    if match:
        return match.group(1)
    return None


def _parse_dexa_patient_weight_lb(text):
    norm = normalize_ocr_for_classification(text)
    for pattern in [
        r"Weight[:\s]+([\d.]+)\s*(?:lb|ib)\b",
        r"(?:^|\n)\s*Weight\s+([\d.]+)\b",
    ]:
        match = re.search(pattern, norm, re.I)
        if match:
            weight = float(match.group(1))
            if 80 <= weight <= 400:
                return weight
    return None


def _parse_dexa_composition_total_row(text):
    """
    Parse FITLAB / Hologic Horizon DXA Results Summary table.
    The whole-body Total row (not Subtotal) ends with % Fat in the last column.
    """
    candidates = []
    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if ln]

    for idx, line in enumerate(lines):
        lower = line.lower()
        if lower.startswith("subtotal"):
            continue
        if not re.match(r"^total\b", lower):
            continue

        row_nums = _dexa_parse_floats_from_text(re.sub(r"^total\b", "", line, flags=re.I))
        parsed = _dexa_coalesce_total_row(row_nums)
        if parsed:
            candidates.append((100 if len(row_nums) >= 6 else 98, parsed))
            continue

        if idx + 1 < len(lines):
            next_line = lines[idx + 1]
            if not re.match(r"^(l|r|subtotal|head|tbar)\b", next_line, re.I):
                next_nums = _dexa_parse_floats_from_text(next_line)
                parsed = _dexa_coalesce_total_row(next_nums)
                if parsed:
                    candidates.append((90 if len(next_nums) >= 6 else 92, parsed))

    for match in re.finditer(
        r"(?<![A-Za-z])Total\s+(?!Mass\b)([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)",
        text,
        re.I,
    ):
        nums = [float(g.replace(",", "")) for g in match.groups()]
        parsed = _dexa_row_from_six_numbers(nums)
        if parsed:
            candidates.append((80, parsed))

    for match in re.finditer(
        r"(?<![A-Za-z])Total\s+(?!Mass\b)([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)(?!\s+[\d.,])",
        text,
        re.I,
    ):
        nums = [float(g.replace(",", "")) for g in match.groups()]
        parsed = _dexa_row_from_four_numbers_lb(nums)
        if parsed:
            candidates.append((97, parsed))

    for match in re.finditer(
        r"(?<![A-Za-z])Total\s+(?!Mass\b)([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)(?!\s+[\d.,])",
        text,
        re.I,
    ):
        nums = [float(g.replace(",", "")) for g in match.groups()]
        parsed = _dexa_row_from_three_numbers(nums)
        if parsed:
            candidates.append((88, parsed))

    # OCR sometimes drops the label row — grab the last numeric line before TBAR/footer codes.
    for idx, line in enumerate(lines):
        if re.search(r"\btbar\d+", line, re.I):
            for back in range(1, 4):
                if idx - back < 0:
                    break
                prev = lines[idx - back]
                if re.match(r"^(total|subtotal|head)\b", prev, re.I):
                    continue
                nums = _dexa_parse_floats_from_text(prev)
                parsed = _dexa_row_from_six_numbers(nums)
                if parsed:
                    candidates.append((60, parsed))
                    break

    # % Fat column only: value below "Total" when table columns survive but numbers split.
    for idx, line in enumerate(lines):
        if re.fullmatch(r"Total", line.strip(), re.I) and idx + 1 < len(lines):
            nums = _dexa_parse_floats_from_text(lines[idx + 1])
            parsed = _dexa_coalesce_total_row(nums)
            if parsed:
                candidates.append((95, parsed))
            elif nums and _dexa_is_body_fat_pct(nums[-1]):
                pct = float(nums[-1])
                candidates.append((50, {"body_fat_pct": round(pct, 1)}))

    # Compact 3-column table lines ending in % Fat (Fat Mass g, Lean+BMC g, % Fat).
    for line in lines:
        if re.match(r"^(head|l\s|r\s|subtotal|tbar|region)\b", line, re.I):
            continue
        nums = _dexa_parse_floats_from_text(line)
        if len(nums) != 3:
            continue
        parsed = _dexa_row_from_three_numbers(nums)
        if parsed:
            score = 96 if re.match(r"^total\b", line, re.I) else 45
            candidates.append((score, parsed))
    for line in lines:
        if re.match(r"^(head|l\s|r\s|subtotal|tbar)\b", line, re.I):
            continue
        nums = _dexa_parse_floats_from_text(line)
        if len(nums) < 6:
            continue
        parsed = _dexa_row_from_six_numbers(nums)
        if not parsed:
            continue
        weight_lb = parsed.get("weight_lbs") or 0
        if 100 <= weight_lb <= 400:
            candidates.append((55, parsed))

    # Multiline Total row: label on one line, numbers on the next 1-2 lines.
    for idx, line in enumerate(lines):
        if not re.match(r"^total\b", line.strip(), re.I):
            continue
        if re.match(r"^total\s+mass\b", line.strip(), re.I):
            continue
        chunk = re.sub(r"^total\b", "", line, flags=re.I)
        for offset in range(0, 3):
            if offset:
                if idx + offset >= len(lines):
                    break
                chunk = f"{chunk} {lines[idx + offset]}"
            nums = _dexa_parse_floats_from_text(chunk)
            parsed = _dexa_coalesce_total_row(nums)
            if parsed:
                candidates.append((85, parsed))
                break

    if not candidates:
        return {}

    candidates.sort(key=lambda item: item[0], reverse=True)
    for _score, parsed in candidates:
        bf = parsed.get("body_fat_pct")
        fat = parsed.get("fat_mass_lbs")
        lean = parsed.get("lean_mass_lbs")
        wt = parsed.get("weight_lbs")
        if dexa_scan_values_sane(bf, fat, lean, wt):
            best = dict(parsed)
            break
    else:
        best = dict(candidates[0][1])
    patient_weight = _parse_dexa_patient_weight_lb(text)
    if patient_weight:
        best["weight_lbs"] = patient_weight
    return best


def parse_dexa_ocr(text, apply_learning=True):
    out = {}
    if not text:
        return out

    auth = _parse_dexa_fitpal_authoritative(text)
    if auth:
        out.update(auth)

    scan_date = _parse_dexa_scan_date(text)
    if scan_date and not out.get("scan_date"):
        out["scan_date"] = scan_date

    patient_weight = _parse_dexa_patient_weight_lb(text)
    if patient_weight:
        out["weight_lbs"] = patient_weight

    comp = _parse_dexa_composition_total_row(text)
    for key, val in (comp or {}).items():
        if val in (None, "", 0):
            continue
        if key not in out or out.get(key) in (None, "", 0):
            out[key] = val

    if not out.get("body_fat_pct"):
        match = re.search(r"Total\s+(?:Body\s+)?%?\s*Fat[^0-9]{0,20}([\d.]+)", text, re.I)
        if match and _dexa_is_body_fat_pct(match.group(1)):
            out["body_fat_pct"] = float(match.group(1))

    if not out.get("body_fat_pct"):
        pct_section = text
        if re.search(r"DXA Results", text, re.I):
            pct_section = text[text.lower().rfind("dxa results") :]
        pct_matches = re.findall(r"(?<![\d.])([\d]{1,2}\.[\d])(?![\d.])", pct_section)
        for candidate in reversed(pct_matches):
            if _dexa_is_body_fat_pct(candidate):
                out["body_fat_pct"] = float(candidate)
                break

    if not out.get("fat_mass_lbs"):
        match = re.search(
            r"Total Fat Mass Results[\s\S]{0,400}?(\d{2}/\d{2}/\d{4})\s+\d+\s+([\d.]+)",
            text,
            re.I,
        )
        if match:
            out["fat_mass_lbs"] = float(match.group(2))
            if not out.get("scan_date"):
                try:
                    out["scan_date"] = pd.to_datetime(match.group(1)).date().isoformat()
                except Exception:
                    pass
    if not out.get("fat_mass_lbs"):
        match = re.search(r"fat\s*mass[^0-9]{0,15}([\d.]+)\s*lb", text, re.I)
        if match:
            out["fat_mass_lbs"] = float(match.group(1))
    if not out.get("fat_mass_lbs"):
        match = re.search(r"fat\s*mass[^0-9\n]{0,40}([\d.,]+)\s*g", text, re.I)
        if match:
            out["fat_mass_g"] = float(match.group(1).replace(",", ""))
            out["fat_mass_lbs"] = _dexa_grams_to_lbs(out["fat_mass_g"])
    if not out.get("lean_mass_lbs"):
        match = re.search(r"lean(?:\s*\+\s*bmc|\s*mass)?[^0-9]{0,15}([\d.]+)\s*lb", text, re.I)
        if match:
            out["lean_mass_lbs"] = float(match.group(1))
    if not out.get("lean_mass_lbs"):
        match = re.search(r"lean\s*\+\s*bmc[^0-9\n]{0,40}([\d.,]+)\s*g", text, re.I)
        if match:
            out["lean_bmc_g"] = float(match.group(1).replace(",", ""))
            out["lean_mass_lbs"] = _dexa_grams_to_lbs(out["lean_bmc_g"])

    match = re.search(r"Est\.\s*VAT\s*Mass[^0-9]{0,20}([\d.]+)", text, re.I)
    if match:
        out["vat_mass_g"] = float(match.group(1))
    match = re.search(r"Est\.\s*VAT\s*Volume[^0-9]{0,20}([\d.]+)", text, re.I)
    if match:
        out["vat_volume_cm3"] = float(match.group(1))
    match = re.search(r"Est\.\s*VAT\s*Area[^0-9]{0,20}([\d.]+)", text, re.I)
    if match:
        out["vat_area_cm2"] = float(match.group(1))
    match = re.search(r"vat[^0-9]{0,12}([\d.]+)\s*g", text, re.I)
    if match and "vat_mass_g" not in out:
        out["vat_mass_g"] = float(match.group(1))

    if out.get("body_fat_pct") and out.get("weight_lbs") and not out.get("fat_mass_lbs"):
        out["fat_mass_lbs"] = round(out["weight_lbs"] * out["body_fat_pct"] / 100.0, 2)
    if out.get("weight_lbs") and out.get("fat_mass_lbs") and not out.get("lean_mass_lbs"):
        out["lean_mass_lbs"] = round(out["weight_lbs"] - out["fat_mass_lbs"], 2)

    out = _dexa_apply_gram_fields(out)

    if apply_learning:
        evidence = _dexa_extract_field_evidence(text)
        out = apply_learned_ocr_to_parsed("DEXA", out, evidence)
        out = _dexa_apply_gram_fields(out)
    return out


def _dexa_default_scan_date(parsed, stored_path):
    raw = (parsed or {}).get("scan_date")
    if raw:
        try:
            return pd.to_datetime(raw).date()
        except Exception:
            pass
    return parse_inbox_image_date(stored_path)


def parse_workout_ocr(text, apply_learning=True):
    out = {}
    if not text:
        return out
    out["notes"] = text[:500]
    m = re.search(r"(?:calories|burn|energy)[^0-9]{0,15}([\d,]{2,5})", text, re.I)
    if m:
        out["active_energy"] = float(m.group(1).replace(",", ""))
    exercise_names = [
        "bench press", "squat", "deadlift", "overhead press", "row", "pull-up", "pull up",
        "lat pulldown", "leg press", "romanian deadlift", "incline press", "curl", "extension",
    ]
    for name in exercise_names:
        if name in text.lower():
            out["workout"] = name.title()
            break
    if "workout" not in out:
        m = re.search(r"^([A-Z][A-Za-z0-9 /+-]{3,40})$", text, re.M)
        if m:
            out["workout"] = m.group(1).strip()
    m = re.search(r"(\d+)\s*[x×]\s*(\d+)", text, re.I)
    if m:
        out["sets"] = int(m.group(1))
        out["reps"] = int(m.group(2))
    m = re.search(r"set\s*(\d+)[^\d]{0,20}(\d+)\s*rep", text, re.I)
    if m:
        out["sets"] = int(m.group(1))
        out["reps"] = int(m.group(2))
    m = re.search(r"(\d{2,3}(?:\.\d)?)\s*(?:lbs?|lb\.?|kg)\b", text, re.I)
    if m:
        val = float(m.group(1))
        if "kg" in text.lower()[max(0, m.start() - 5):m.end() + 5].lower():
            val = round(val * 2.20462, 1)
        out["weight_lbs"] = val
    if apply_learning:
        evidence = _workout_extract_field_evidence(text)
        out = apply_learned_ocr_to_parsed("Workout", out, evidence)
    return out


def parse_scale_ocr(text, apply_learning=True, document_type="Scale"):
    out = {}
    if not text:
        return out
    norm = normalize_ocr_for_classification(text)
    if re.search(r"hologic|dexa|dexafit|lean\s*\+\s*bmc|fat\s*mass|fitpal|body composition", norm, re.I):
        return out
    candidates = []
    for m in re.finditer(r"(\d{2,3}(?:\.\d)?)\s*(?:lbs?|lb\.?)\b", norm, re.I):
        val = float(m.group(1))
        if 80 <= val <= 400:
            candidates.append(val)
    if candidates:
        out["weight_lbs"] = candidates[0]
    else:
        for m in re.finditer(r"(\d{2,3}(?:\.\d)?)\s*(?:kg|kilograms?)\b", text, re.I):
            val = float(m.group(1))
            if 35 <= val <= 180:
                out["weight_lbs"] = round(val * 2.20462, 1)
                break
        if not out.get("weight_lbs"):
            m = re.search(r"(?:weight|wt)[:\s]+([\d.]+)", text, re.I)
            if m:
                out["weight_lbs"] = float(m.group(1))
    if apply_learning:
        evidence = _scale_extract_field_evidence(text)
        out = apply_learned_ocr_to_parsed(document_type, out, evidence)
    return out


def parse_by_type(dtype, text, apply_learning=True):
    if dtype == "FatSecret":
        return parse_fatsecret_ocr(text, apply_learning=apply_learning)
    if dtype == "Oura":
        return parse_oura_ocr(text, apply_learning=apply_learning)
    if dtype == "DEXA":
        return parse_dexa_ocr(text, apply_learning=apply_learning)
    if dtype == "Workout":
        return parse_workout_ocr(text, apply_learning=apply_learning)
    if dtype == "Scale" or dtype == "Apple Health Weight":
        if dtype == "Apple Health Weight":
            return parse_apple_health_weight_ocr(text, apply_learning=apply_learning)
        return parse_scale_ocr(text, apply_learning=apply_learning, document_type=dtype)
    return {}


def dedupe_ocr_queue_rows(cur=None):
    """Keep one ocr_queue row per file_hash, preferring imported/skipped over pending."""
    close_after = False
    if cur is None:
        c = conn()
        cur = c.cursor()
        close_after = True
    status_rank = {"imported": 3, "skipped": 2, "pending_confirmation": 1}
    rows = cur.execute(
        "SELECT id, file_hash, status FROM ocr_queue WHERE file_hash IS NOT NULL AND file_hash != '' ORDER BY id"
    ).fetchall()
    best_by_hash = {}
    for row_id, file_hash, status in rows:
        rank = status_rank.get(str(status or ""), 0)
        prev = best_by_hash.get(file_hash)
        if not prev or rank > prev[0] or (rank == prev[0] and row_id > prev[1]):
            best_by_hash[file_hash] = (rank, row_id)
    keep_ids = {item[1] for item in best_by_hash.values()}
    drop_ids = [row[0] for row in rows if row[0] not in keep_ids]
    for drop_id in drop_ids:
        cur.execute("DELETE FROM ocr_queue WHERE id = ?", (drop_id,))
    if close_after:
        c.commit()
        c.close()


def sync_pending_ocr_with_registry(cursor=None):
    sql = """
        UPDATE ocr_queue
        SET status = 'imported',
            notes = CASE
                WHEN notes IS NULL OR notes = '' THEN 'Synced from confirmed file registry'
                WHEN notes LIKE '%Synced from confirmed file registry%' THEN notes
                ELSE notes || ' | Synced from confirmed file registry'
            END
        WHERE status = 'pending_confirmation'
          AND file_hash IN (
            SELECT file_hash FROM file_registry WHERE status IN ('imported', 'skipped')
          )
        """
    if cursor is not None:
        cursor.execute(sql)
        return
    c = conn()
    c.execute(sql)
    c.commit()
    c.close()


def reconcile_ocr_queue():
    sync_pending_ocr_with_registry()
    c = conn()
    cur = c.cursor()
    dedupe_ocr_queue_rows(cur)
    c.commit()
    c.close()
    sync_imported_ocr_to_daily_log(reparse_missing=True)
    return auto_confirm_pending_ocr_items()


def upsert_ocr_queue(file_hash, stored_path, detected_type, ocr_text, parsed, status="pending_confirmation", notes="", preserve_terminal_status=True):
    c = conn()
    existing = c.execute("SELECT id, status FROM ocr_queue WHERE file_hash = ?", (file_hash,)).fetchone()
    if existing and preserve_terminal_status and existing[1] in OCR_TERMINAL_STATUSES:
        status = existing[1]
    payload = (
        detected_type,
        ocr_text or "",
        json.dumps(parsed or {}),
        status,
        notes,
        str(stored_path),
        file_hash,
    )
    if existing:
        c.execute(
            """
            UPDATE ocr_queue
            SET detected_type = ?, ocr_text = ?, parsed_json = ?, status = ?, notes = ?, stored_path = ?
            WHERE file_hash = ?
            """,
            payload,
        )
    else:
        c.execute(
            "INSERT INTO ocr_queue (created_at, file_hash, stored_path, detected_type, ocr_text, parsed_json, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now().isoformat(timespec="seconds"),
                file_hash,
                str(stored_path),
                detected_type,
                ocr_text or "",
                json.dumps(parsed or {}),
                status,
                notes,
            ),
        )
    c.commit()
    c.close()


def enqueue_ocr(file_hash, stored_path, detected_type, ocr_text, parsed, status="pending_confirmation", notes=""):
    upsert_ocr_queue(file_hash, stored_path, detected_type, ocr_text, parsed, status=status, notes=notes)


def load_ocr_queue(status=None):
    c = conn()
    q = "SELECT * FROM ocr_queue"
    params = ()
    if status:
        q += " WHERE status = ?"
        params = (status,)
    q += " ORDER BY created_at DESC"
    try:
        df = pd.read_sql(q, c, params=params)
    except Exception:
        df = pd.DataFrame()
    c.close()
    return df


def update_ocr_status(queue_id, status, notes=""):
    c = conn()
    c.execute("UPDATE ocr_queue SET status = ?, notes = ? WHERE id = ?", (status, notes, int(queue_id)))
    c.commit()
    c.close()


def update_file_registry_status(file_hash, status, notes=None):
    c = conn()
    if notes is None:
        c.execute("UPDATE file_registry SET status = ? WHERE file_hash = ?", (status, file_hash))
    else:
        c.execute("UPDATE file_registry SET status = ?, notes = ? WHERE file_hash = ?", (status, notes, file_hash))
    c.commit()
    c.close()


def finalize_ocr_queue_item(row, status, notes="", parsed_values=None):
    file_hash = row.get("file_hash") if hasattr(row, "get") else row["file_hash"]
    queue_id = int(row["id"])
    c = conn()
    if file_hash:
        if parsed_values is not None:
            c.execute(
                "UPDATE ocr_queue SET status = ?, parsed_json = ?, notes = ? WHERE file_hash = ?",
                (status, json.dumps(parsed_values or {}), notes, file_hash),
            )
        else:
            c.execute(
                "UPDATE ocr_queue SET status = ?, notes = ? WHERE file_hash = ?",
                (status, notes, file_hash),
            )
    elif parsed_values is not None:
        c.execute(
            "UPDATE ocr_queue SET status = ?, parsed_json = ?, notes = ? WHERE id = ?",
            (status, json.dumps(parsed_values or {}), notes, queue_id),
        )
    else:
        c.execute("UPDATE ocr_queue SET status = ?, notes = ? WHERE id = ?", (status, notes, queue_id))
    c.commit()
    c.close()
    if file_hash:
        update_file_registry_status(file_hash, status, notes)


def import_confirmed_queue_item(row, values):
    dtype = row["detected_type"]
    stored_path = row["stored_path"]
    default_day = parse_inbox_image_date(stored_path)

    if dtype in ["FatSecret", "Oura", "Workout", "Scale", "Apple Health Weight"]:
        if dtype == "Apple Health Weight":
            entries = values.get("weight_entries") or []
            if not entries and values.get("weight_lbs"):
                log_day = values.get("log_date") or default_day.isoformat()
                entries = [
                    {
                        "weight_lbs": values["weight_lbs"],
                        "log_date": log_day,
                        "measured_at": values.get("measured_at") or f"{log_day}T12:00",
                    }
                ]
            if entries:
                notes = tag_import_notes(
                    "Apple Health Weight",
                    values.get("notes") or "OCR confirmed weight log",
                )
                save_weight_measurements(
                    entries,
                    source=dtype,
                    file_hash=row.get("file_hash"),
                    notes=notes,
                )
                sync_daily_log_from_weight_entries(entries, source=dtype, source_path=stored_path)
                stored_values = {
                    "weight_entries": entries,
                    "notes": notes,
                    "weight_lbs": entries[0]["weight_lbs"],
                    "log_date": entries[0]["log_date"],
                }
                finalize_ocr_queue_item(row, "imported", "Confirmed and imported", parsed_values=stored_values)
                return

        values["log_date"] = values.get("log_date") or default_day.isoformat()
        if dtype == "Apple Health Weight":
            values["notes"] = tag_import_notes("Apple Health Weight", values.get("notes") or "OCR confirmed weight import")
        elif dtype == "FatSecret":
            parsed = {k: values.get(k) for k in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sodium_mg"] if values.get(k)}
            if parsed.get("fiber_g") or parsed.get("sodium_mg"):
                values["notes"] = fatsecret_screenshot_notes(parsed)
        elif dtype == "Oura":
            values["notes"] = oura_screenshot_notes(values)
        applied = upsert_daily(
            values,
            source=dtype,
            source_path=stored_path,
            file_hash=row.get("file_hash"),
            data_ts=parse_document_timestamp(stored_path, values.get("log_date")),
        )
        if not applied:
            finalize_ocr_queue_item(row, "imported", "Confirmed — skipped (newer data already on file)", parsed_values=values)
            return
        if dtype in ["Workout", "Strong"] and values.get("active_energy") and values.get("workout"):
            save_workout_observation(values["workout"], values["active_energy"])
    elif dtype == "DEXA":
        scan_date = values.get("scan_date") or default_day.isoformat()
        weight = values.get("weight_lbs")
        bf = values.get("body_fat_pct")
        fat_mass = values.get("fat_mass_lbs")
        lean_mass = values.get("lean_mass_lbs")
        if weight and bf and fat_mass and lean_mass:
            apply_dexa_scan_record(
                (scan_date, weight, bf, fat_mass, lean_mass, values.get("vat_mass_g"), values.get("vat_volume_cm3"), values.get("vat_area_cm2"), stored_path, "OCR confirmed DEXA import")
            )
    finalize_ocr_queue_item(row, "imported", "Confirmed and imported", parsed_values=values)


def load_ocr_review_queue():
    df = load_ocr_queue()
    if df.empty:
        return df
    pending = df[df["status"] == "pending_confirmation"].copy()
    if pending.empty:
        return pending
    imported_hashes = set(df.loc[df["status"].isin(OCR_TERMINAL_STATUSES), "file_hash"].dropna())
    if imported_hashes:
        pending = pending[~pending["file_hash"].isin(imported_hashes)]
    return pending


def ocr_queue_status_marker(status):
    css_class = {
        "pending_confirmation": "ocr-q-status-pending",
        "imported": "ocr-q-status-imported",
        "skipped": "ocr-q-status-skipped",
    }.get(str(status or ""), "ocr-q-status-pending")
    return f'<div class="{css_class}" style="display:none;height:0;margin:0;padding:0;"></div>'


def ocr_queue_item_title(qr, preview=""):
    status = str(qr.get("status") or "")
    tag = {
        "pending_confirmation": "Pending",
        "imported": "Confirmed",
        "skipped": "Skipped",
    }.get(status, status.replace("_", " ").title())
    name = Path(qr["stored_path"]).name
    base = f"{tag} | {ocr_queue_label(qr['detected_type'])} | {qr['detected_type']} | {name}"
    if preview:
        return f"{base} | {preview}"
    return base


def _render_ocr_queue_item_form(qr, values, dtype, key_prefix):
    if dtype in ["FatSecret", "Oura", "Workout", "Scale", "Apple Health Weight"]:
        values["log_date"] = st.date_input(
            "Log date",
            value=parse_inbox_image_date(qr["stored_path"]),
            key=f"{key_prefix}_logdate_{qr['id']}",
        ).isoformat()
        if dtype == "FatSecret":
            c1, c2, c3, c4 = st.columns(4)
            values["calories"] = c1.number_input("Calories", value=float(values.get("calories", 0) or 0), key=f"{key_prefix}_cal_{qr['id']}")
            values["protein_g"] = c2.number_input("Protein g", value=float(values.get("protein_g", 0) or 0), key=f"{key_prefix}_pro_{qr['id']}")
            values["carbs_g"] = c3.number_input("Net C g", value=float(values.get("carbs_g", 0) or 0), key=f"{key_prefix}_carb_{qr['id']}")
            values["fat_g"] = c4.number_input("Fat g", value=float(values.get("fat_g", 0) or 0), key=f"{key_prefix}_fat_{qr['id']}")
            f1, f2 = st.columns(2)
            values["fiber_g"] = f1.number_input("Fiber g", value=float(values.get("fiber_g", 0) or 0), key=f"{key_prefix}_fiber_{qr['id']}")
            values["sodium_mg"] = f2.number_input("Sodium mg", value=float(values.get("sodium_mg", 0) or 0), key=f"{key_prefix}_sodium_{qr['id']}")
        elif dtype == "Oura":
            c1, c2, c3, c4 = st.columns(4)
            values["oura_burn"] = c1.number_input(
                "Total burn (kcal)",
                value=float(values.get("oura_burn", 0) or 0),
                key=f"{key_prefix}_burn_{qr['id']}",
                help="TOTAL BURN — used for deficit calculations",
            )
            values["active_energy"] = c2.number_input(
                "Activity burn (kcal)",
                value=float(values.get("active_energy", 0) or 0),
                key=f"{key_prefix}_act_burn_{qr['id']}",
                help="ACTIVITY BURN — exercise calories only",
            )
            values["oura_activity_time_min"] = c3.number_input(
                "Activity time (min)",
                value=float(values.get("oura_activity_time_min", 0) or 0),
                key=f"{key_prefix}_act_time_{qr['id']}",
            )
            values["oura_goal_progress"] = c4.text_input(
                "Goal progress",
                value=str(values.get("oura_goal_progress", "") or ""),
                key=f"{key_prefix}_goal_prog_{qr['id']}",
                placeholder="8 / 10",
            )
            s1, s2, s3 = st.columns(3)
            values["sleep_score"] = s1.number_input(
                "Sleep score", value=float(values.get("sleep_score", 0) or 0), key=f"{key_prefix}_sleep_{qr['id']}"
            )
            values["readiness_score"] = s2.number_input(
                "Readiness", value=float(values.get("readiness_score", 0) or 0), key=f"{key_prefix}_ready_{qr['id']}"
            )
            values["sleep_minutes"] = s3.number_input(
                "Sleep minutes", value=float(values.get("sleep_minutes", 0) or 0), key=f"{key_prefix}_mins_{qr['id']}"
            )
        elif dtype == "Workout":
            c1, c2, c3 = st.columns(3 if key_prefix == "hub" else 2)
            values["workout"] = c1.text_input("Workout", value=str(values.get("workout", "") or ""), key=f"{key_prefix}_wo_{qr['id']}")
            values["active_energy"] = c2.number_input(
                "Observed burn", value=float(values.get("active_energy", 0) or 0), key=f"{key_prefix}_wo_burn_{qr['id']}"
            )
            if key_prefix == "hub":
                values["workout_intensity"] = c3.number_input(
                    "Intensity 1-10", value=float(values.get("workout_intensity", 0) or 0), key=f"{key_prefix}_wo_int_{qr['id']}"
                )
        elif dtype == "Scale":
            values["weight_lbs"] = st.number_input(
                "Weight (lbs)",
                value=float(values.get("weight_lbs", 0) or 0),
                step=0.1,
                key=f"{key_prefix}_scale_wt_{qr['id']}",
            )
        elif dtype == "Apple Health Weight":
            values["weight_lbs"] = st.number_input(
                "Weight (lbs)",
                value=float(values.get("weight_lbs", 0) or 0),
                step=0.1,
                key=f"{key_prefix}_ah_wt_{qr['id']}",
            )
    elif dtype == "DEXA":
        values["scan_date"] = st.date_input(
            "Scan date",
            value=_dexa_default_scan_date(values, qr["stored_path"]),
            key=f"{key_prefix}_scan_{qr['id']}",
        ).isoformat()
        c1, c2, c3, c4 = st.columns(4)
        values["weight_lbs"] = c1.number_input("Weight lb", value=float(values.get("weight_lbs", 0) or 0), key=f"{key_prefix}_dxw_{qr['id']}")
        values["body_fat_pct"] = c2.number_input("Body fat %", value=float(values.get("body_fat_pct", 0) or 0), key=f"{key_prefix}_dxbf_{qr['id']}")
        values["fat_mass_lbs"] = c3.number_input("Fat mass lb", value=float(values.get("fat_mass_lbs", 0) or 0), key=f"{key_prefix}_dxfat_{qr['id']}")
        values["lean_mass_lbs"] = c4.number_input("Lean + BMC lb", value=float(values.get("lean_mass_lbs", 0) or 0), key=f"{key_prefix}_dxlean_{qr['id']}")
        values["vat_mass_g"] = st.number_input("VAT mass g", value=float(values.get("vat_mass_g", 0) or 0), key=f"{key_prefix}_dxvat_{qr['id']}")
    return values


def _dexa_sync_wizard_from_ocr(wiz, qr):
    """Fill missing DEXA lb fields from a fresh gram-aware OCR parse."""
    ocr_text = (qr.get("ocr_text") if hasattr(qr, "get") else qr["ocr_text"]) or ""
    if not ocr_text:
        return wiz
    fresh = _dexa_apply_gram_fields(parse_dexa_ocr(ocr_text, apply_learning=False))
    if not fresh:
        return wiz
    wiz.setdefault("ocr_original", {})
    wiz.setdefault("values", {})
    for key in (
        "fat_mass_lbs", "lean_mass_lbs", "body_fat_pct", "weight_lbs",
        "fat_mass_g", "lean_bmc_g", "total_mass_g", "scan_date",
    ):
        if fresh.get(key) is None:
            continue
        wiz["ocr_original"][key] = fresh[key]
        current = wiz["values"].get(key)
        if current in (None, "", 0, 0.0):
            wiz["values"][key] = fresh[key]
    wiz["evidence"] = extract_ocr_field_evidence("DEXA", ocr_text)
    wiz.setdefault("units", {})
    for field_key in DEXA_MASS_UNIT_FIELDS:
        if field_key not in wiz["units"]:
            wiz["units"][field_key] = _dexa_default_mass_unit(
                field_key, wiz.get("ocr_original"), wiz.get("values")
            )
    return wiz


def _ocr_wizard_session_key(key_prefix, queue_id):
    return f"{key_prefix}_ocr_wizard_{queue_id}"


def _ocr_wizard_init_state(qr, parsed, dtype):
    ocr_text = qr.get("ocr_text") if hasattr(qr, "get") else qr["ocr_text"]
    ocr_text = ocr_text or ""
    evidence = extract_ocr_field_evidence(dtype, ocr_text)
    if ocr_text:
        raw_parsed = parse_by_type(dtype, ocr_text, apply_learning=False)
    else:
        raw_parsed = dict(parsed)
    if dtype == "DEXA":
        raw_parsed = _dexa_apply_gram_fields(raw_parsed)
    learned = apply_learned_ocr_to_parsed(dtype, dict(raw_parsed), evidence)
    if dtype == "DEXA":
        learned = _dexa_apply_gram_fields(learned)
    state = {
        "step": 0,
        "values": learned,
        "ocr_original": raw_parsed,
        "evidence": evidence,
        "dtype": dtype,
    }
    if dtype == "DEXA":
        state["scan_date"] = _dexa_default_scan_date(learned, qr["stored_path"]).isoformat()
        state["units"] = {
            field_key: _dexa_default_mass_unit(field_key, raw_parsed, learned)
            for field_key in DEXA_MASS_UNIT_FIELDS
        }
    elif dtype in ("FatSecret", "Oura", "Workout", "Scale", "Apple Health Weight"):
        state["log_date"] = parse_inbox_image_date(qr["stored_path"]).isoformat()
    return state


def _ocr_format_field_hint(field_key, ocr_original, evidence, dtype=None):
    orig = ocr_original.get(field_key)
    ev = evidence.get(field_key, {})
    raw = ev.get("raw_snippet")
    bits = []
    gram_key = {
        "fat_mass_lbs": "fat_mass_g",
        "lean_mass_lbs": "lean_bmc_g",
        "weight_lbs": "total_mass_g",
    }.get(field_key)
    grams_on_report = ocr_original.get(gram_key) if gram_key else None
    if dtype == "DEXA" and grams_on_report:
        bits.append(
            f"Report shows **{grams_on_report} g** on the Total row "
            f"(= **{_dexa_grams_to_lbs(grams_on_report)} lb**)"
        )
    if raw:
        bits.append(f'Raw OCR text: "{raw}"')
    if orig not in (None, "", 0):
        bits.append(f"Parsed as: **{orig}**")
    elif raw and not grams_on_report:
        bits.append("Could not parse a value from raw text.")
    elif not raw and not grams_on_report:
        bits.append("OCR did not detect this field.")
    label_ctx = ev.get("label_context")
    if label_ctx:
        bits.append(f'Near label: "{label_ctx}"')
    return " · ".join(bits)


def _ocr_wizard_store_field(wiz, step_spec, entered):
    field_key = step_spec["key"]
    if step_spec.get("widget") == "date" or field_key in OCR_DATE_FIELD_KEYS:
        wiz[field_key] = entered
    else:
        wiz["values"][field_key] = entered


def _ocr_wizard_mass_unit_widget(step_spec, wiz, key_prefix, queue_id, dtype):
    field_key = step_spec["key"]
    values = wiz["values"]
    ocr_original = wiz.get("ocr_original") or {}
    wiz.setdefault("units", {})
    default_unit = wiz["units"].get(field_key) or _dexa_default_mass_unit(
        field_key, ocr_original, values
    )
    unit_labels = list(MASS_UNIT_OPTIONS)
    unit_key = f"{key_prefix}_{dtype}_unit_{queue_id}_{field_key}"

    unit_col, val_col = st.columns([1, 2.2])
    with unit_col:
        unit = st.selectbox(
            "Unit",
            unit_labels,
            index=unit_labels.index(default_unit) if default_unit in unit_labels else 0,
            key=unit_key,
        )
    val_key = f"{key_prefix}_{dtype}_val_{queue_id}_{field_key}_{unit}"
    display_val = _dexa_mass_display_value(field_key, unit, values, ocr_original)
    step = 0.1 if unit == "g" else (step_spec.get("step") or 0.01)
    with val_col:
        entered = st.number_input(
            step_spec["label"],
            value=float(display_val or 0),
            step=float(step),
            key=val_key,
            help=step_spec.get("help"),
        )

    wiz["units"][field_key] = unit
    lbs = _mass_to_lbs(entered, unit)
    if entered:
        wiz["values"][field_key] = lbs
        gram_key = DEXA_MASS_UNIT_FIELDS.get(field_key, {}).get("gram_key")
        if gram_key:
            wiz["values"][gram_key] = round(_mass_from_lbs(lbs, "g"), 1)
        st.caption(
            f"**{entered:g} {unit}** = **{_mass_from_lbs(lbs, 'g'):g} g** = **{_mass_from_lbs(lbs, 'kg')} kg** = **{lbs} lb** (stored)"
        )
    return lbs


def _ocr_wizard_widget(step_spec, wiz, key_prefix, queue_id, dtype):
    field_key = step_spec["key"]
    widget = step_spec["widget"]
    values = wiz["values"]
    widget_key = f"{key_prefix}_{dtype}_w_{queue_id}_{field_key}"

    if widget == "mass_unit":
        return _ocr_wizard_mass_unit_widget(step_spec, wiz, key_prefix, queue_id, dtype)

    if widget == "date":
        default_iso = wiz.get(field_key) or date.today().isoformat()
        default_day = date.fromisoformat(default_iso)
        return st.date_input(
            step_spec["label"],
            value=default_day,
            key=widget_key,
            help=step_spec.get("help"),
        ).isoformat()

    if widget == "text":
        return st.text_input(
            step_spec["label"],
            value=str(values.get(field_key, "") or ""),
            key=widget_key,
            placeholder=step_spec.get("placeholder", ""),
            help=step_spec.get("help"),
        )

    default_num = float(values.get(field_key, 0) or 0)
    num_kwargs = {"help": step_spec.get("help")}
    if step_spec.get("step") is not None:
        num_kwargs["step"] = step_spec["step"]
    return st.number_input(step_spec["label"], value=default_num, key=widget_key, **num_kwargs)


def _ocr_wizard_review_payload(wiz, steps, dtype):
    review = dict(wiz["values"])
    for step in steps:
        fk = step["key"]
        if fk in OCR_DATE_FIELD_KEYS:
            review[fk] = wiz.get(fk)
    return review


def render_ocr_validation_wizard(qr, parsed, dtype, key_prefix):
    """Step-by-step field validation with correction learning."""
    queue_id = qr["id"]
    wiz_key = _ocr_wizard_session_key(key_prefix, queue_id)
    steps = OCR_VALIDATION_STEPS.get(dtype, [])
    if not steps:
        return False

    if wiz_key not in st.session_state:
        st.session_state[wiz_key] = _ocr_wizard_init_state(qr, parsed, dtype)

    wiz = st.session_state[wiz_key]
    if dtype == "DEXA":
        wiz = _dexa_sync_wizard_from_ocr(wiz, qr)
        st.session_state[wiz_key] = wiz
    step_idx = int(wiz.get("step", 0))

    learned_count, learned_uses = count_ocr_field_corrections(dtype)
    st.caption(
        f"Guided validation · {dtype} · "
        f"{('Review' if step_idx >= len(steps) else f'Step {step_idx + 1} of {len(steps)}')} · "
        f"{learned_count} learned patterns ({learned_uses} uses)"
    )
    st.progress(min(1.0, (step_idx + 1) / len(steps)))

    p = image_display_path(qr["stored_path"])
    slug = re.sub(r"[^A-Za-z0-9]+", "_", dtype).lower()

    if step_idx >= len(steps):
        st.markdown("### Review and confirm")
        if p.exists() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            st.image(str(p), width=400)
        review = _ocr_wizard_review_payload(wiz, steps, dtype)
        review_keys = [s["key"] for s in steps]
        st.json({k: review.get(k) for k in review_keys})

        corrections = []
        for step in steps:
            fk = step["key"]
            orig = wiz["ocr_original"].get(fk)
            final = review.get(fk)
            if _ocr_field_values_differ(fk, orig, final):
                corrections.append(f"{step['label']}: {orig} → {final}")
        had_corrections = bool(corrections)
        if corrections:
            st.info("Your corrections will be saved so OCR improves next time:\n" + "\n".join(f"- {c}" for c in corrections))
        else:
            st.success("All values match OCR — no corrections needed.")
            if not ocr_type_auto_confirm_enabled(dtype):
                st.caption("One clean confirm like this teaches the system to auto-import this document type.")

        c_confirm, c_skip, c_back = st.columns(3)
        if c_back.button("← Edit fields", key=f"{key_prefix}_{slug}_review_back_{queue_id}"):
            wiz["step"] = len(steps) - 1
            st.session_state[wiz_key] = wiz
            st.rerun()
        if c_skip.button("Mark as reviewed / skip", key=f"{key_prefix}_{slug}_skip_{queue_id}"):
            finalize_ocr_queue_item(qr, "skipped", "User skipped guided validation")
            del st.session_state[wiz_key]
            st.warning("Skipped.")
            return True
        if c_confirm.button("Confirm and import", key=f"{key_prefix}_{slug}_confirm_{queue_id}", type="primary"):
            record_ocr_validation_corrections(dtype, wiz["ocr_original"], review, wiz.get("evidence"))
            trust_outcome = record_ocr_type_validation_outcome(dtype, had_corrections)
            import_confirmed_queue_item(qr, review)
            del st.session_state[wiz_key]
            if trust_outcome.get("trusted_now"):
                st.success(f"Imported. {dtype} OCR is now trusted — matching scans will auto-import without validation.")
            elif had_corrections:
                st.success("Imported. OCR learned from your corrections; this type stays in manual validation until a clean confirm.")
            else:
                st.success("Imported. OCR learned from any corrections.")
            return True
        return False

    step_spec = steps[step_idx]
    field_key = step_spec["key"]
    is_date_step = step_spec.get("widget") == "date" or field_key in OCR_DATE_FIELD_KEYS

    col_img, col_field = st.columns([1.1, 1])
    with col_img:
        if p.exists() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            st.image(str(p), use_container_width=True)
        with st.expander("OCR text", expanded=False):
            ocr_txt = qr.get("ocr_text") if hasattr(qr, "get") else qr["ocr_text"]
            st.text(ocr_txt or "(empty)")

    with col_field:
        st.markdown(f"### {step_spec['label']}")
        if is_date_step:
            st.caption("Confirm the date for this document, or skip if unknown.")
        else:
            st.markdown(_ocr_format_field_hint(field_key, wiz["ocr_original"], wiz["evidence"], dtype=dtype))
            st.caption("Skip if this value is not on the screenshot.")

        entered = _ocr_wizard_widget(step_spec, wiz, key_prefix, queue_id, dtype)
        if step_spec.get("widget") == "mass_unit":
            st.session_state[wiz_key] = wiz

        nav1, nav2, nav3, nav4 = st.columns(4)
        if nav1.button("← Back", key=f"{key_prefix}_{slug}_back_{queue_id}", disabled=(step_idx == 0)):
            _ocr_wizard_store_field(wiz, step_spec, entered)
            wiz["step"] = max(0, step_idx - 1)
            st.session_state[wiz_key] = wiz
            st.rerun()

        skip_clicked = nav2.button("Skip field", key=f"{key_prefix}_{slug}_skipf_{queue_id}_{field_key}")

        next_clicked = nav3.button(
            "Next →" if step_idx < len(steps) - 1 else "Review",
            key=f"{key_prefix}_{slug}_next_{queue_id}_{field_key}",
            type="primary",
        )
        restart = nav4.button("Restart", key=f"{key_prefix}_{slug}_restart_{queue_id}")

        if restart:
            st.session_state[wiz_key] = _ocr_wizard_init_state(qr, parsed, dtype)
            st.rerun()

        if skip_clicked:
            if is_date_step:
                wiz[field_key] = None
            else:
                wiz["values"][field_key] = None
            wiz["step"] = step_idx + 1
            st.session_state[wiz_key] = wiz
            st.rerun()

        if next_clicked:
            _ocr_wizard_store_field(wiz, step_spec, entered)
            wiz["step"] = step_idx + 1
            st.session_state[wiz_key] = wiz
            st.rerun()

    return False


def _apple_health_wizard_session_key(key_prefix, queue_id):
    return f"{key_prefix}_ah_weight_wiz_{queue_id}"


def _normalize_apple_health_entries(entries):
    normalized = []
    for entry in entries or []:
        weight = entry.get("weight_lbs")
        measured_at = entry.get("measured_at")
        if weight is None or float(weight) <= 0:
            continue
        log_date = entry.get("log_date") or (str(measured_at)[:10] if measured_at else None)
        if not log_date:
            continue
        if not measured_at:
            measured_at = f"{log_date}T12:00"
        normalized.append(
            {
                "weight_lbs": round(float(weight), 1),
                "measured_at": str(measured_at),
                "log_date": str(log_date),
            }
        )
    return normalized


def _apple_health_entries_changed(original, final):
    def signature(entries):
        return sorted(
            (
                round(float(e.get("weight_lbs") or 0), 1),
                str(e.get("measured_at") or ""),
                str(e.get("log_date") or ""),
            )
            for e in _normalize_apple_health_entries(entries)
        )

    return signature(original) != signature(final)


def render_apple_health_weight_wizard(qr, parsed, key_prefix):
    """Review every weight + timestamp pair from an Apple Health weight history screenshot."""
    queue_id = qr["id"]
    wiz_key = _apple_health_wizard_session_key(key_prefix, queue_id)

    if wiz_key not in st.session_state:
        ocr_text = qr.get("ocr_text") if hasattr(qr, "get") else qr["ocr_text"]
        ocr_text = ocr_text or ""
        if ocr_text:
            raw_parsed = parse_apple_health_weight_ocr(ocr_text, apply_learning=False)
        else:
            raw_parsed = dict(parsed)
        entries = _normalize_apple_health_entries(raw_parsed.get("weight_entries") or [])
        if not entries and raw_parsed.get("weight_lbs"):
            default_day = parse_inbox_image_date(qr["stored_path"]).isoformat()
            entries = [
                {
                    "weight_lbs": float(raw_parsed["weight_lbs"]),
                    "log_date": default_day,
                    "measured_at": f"{default_day}T12:00",
                }
            ]
        st.session_state[wiz_key] = {
            "entries": entries,
            "ocr_original": [dict(e) for e in entries],
            "raw_parsed": raw_parsed,
        }

    wiz = st.session_state[wiz_key]
    entries = wiz.get("entries") or []
    learned_count, learned_uses = count_ocr_field_corrections("Apple Health Weight")
    st.caption(
        f"Apple Health weight log · {len(entries)} measurement(s) detected · "
        f"{learned_count} learned patterns ({learned_uses} uses)"
    )

    p = image_display_path(qr["stored_path"])
    col_img, col_data = st.columns([1.05, 1.25])
    with col_img:
        if p.exists() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            st.image(str(p), use_container_width=True)
        with st.expander("OCR text", expanded=False):
            ocr_txt = qr.get("ocr_text") if hasattr(qr, "get") else qr["ocr_text"]
            st.text(ocr_txt or "(empty)")

    with col_data:
        st.markdown("### Review all measurements")
        st.caption("Each row is one weight with the timestamp directly below it in the screenshot.")
        if entries:
            editor_df = pd.DataFrame(entries)
            edited_df = st.data_editor(
                editor_df,
                column_config={
                    "weight_lbs": st.column_config.NumberColumn("Weight (lb)", step=0.1, format="%.1f"),
                    "log_date": st.column_config.TextColumn("Date (YYYY-MM-DD)"),
                    "measured_at": st.column_config.TextColumn("Measured at"),
                },
                num_rows="dynamic",
                use_container_width=True,
                key=f"{key_prefix}_ah_editor_{queue_id}",
            )
            wiz["entries"] = _normalize_apple_health_entries(edited_df.to_dict(orient="records"))
        else:
            st.warning("No weight entries detected from OCR. Add rows manually or skip this screenshot.")

        had_corrections = _apple_health_entries_changed(wiz.get("ocr_original"), wiz.get("entries"))
        if had_corrections:
            st.info("Your edits will be saved so OCR improves on future scans.")
        elif entries:
            st.success("All values match OCR — no corrections needed.")
            if not ocr_type_auto_confirm_enabled("Apple Health Weight"):
                st.caption(
                    "One clean confirm teaches the system to auto-import Apple Health weight logs."
                )

        c_confirm, c_skip, c_restart = st.columns(3)
        if c_restart.button("Re-scan OCR", key=f"{key_prefix}_ah_restart_{queue_id}"):
            del st.session_state[wiz_key]
            st.rerun()
        if c_skip.button("Mark as reviewed / skip", key=f"{key_prefix}_ah_skip_{queue_id}"):
            finalize_ocr_queue_item(qr, "skipped", "User skipped Apple Health weight log")
            del st.session_state[wiz_key]
            st.warning("Skipped.")
            return True
        if c_confirm.button(
            f"Confirm and import {len(wiz.get('entries') or [])} measurement(s)",
            key=f"{key_prefix}_ah_confirm_{queue_id}",
            type="primary",
            disabled=not wiz.get("entries"),
        ):
            final_entries = wiz.get("entries") or []
            trust_outcome = record_ocr_type_validation_outcome("Apple Health Weight", had_corrections)
            import_confirmed_queue_item(qr, {"weight_entries": final_entries})
            del st.session_state[wiz_key]
            if trust_outcome.get("trusted_now"):
                st.success(
                    "Imported all measurements. Apple Health Weight OCR is now trusted — "
                    "matching scans will auto-import without validation."
                )
            elif had_corrections:
                st.success(
                    f"Imported {len(final_entries)} measurement(s). "
                    "Manual validation stays on until a clean confirm."
                )
            else:
                st.success(f"Imported {len(final_entries)} measurement(s).")
            return True

    st.session_state[wiz_key] = wiz
    return False


def render_oura_validation_wizard(qr, parsed, key_prefix):
    return render_ocr_validation_wizard(qr, parsed, "Oura", key_prefix)


def render_ocr_confirmation_queue(key_prefix, show_preview_in_title=False):
    auto_confirmed = reconcile_ocr_queue()
    if auto_confirmed:
        labels = sorted({str(qr["detected_type"]) for qr in auto_confirmed})
        st.success(
            f"Auto-imported {len(auto_confirmed)} trusted OCR item(s) "
            f"({', '.join(labels)}) — no validation needed."
        )
        st.rerun()
        return

    qdf = load_ocr_review_queue()
    if qdf.empty:
        trusted = list_ocr_auto_confirm_types()
        if trusted:
            st.success(
                "No pending OCR items. Auto-import is on for: "
                + ", ".join(trusted)
                + "."
            )
        else:
            st.success("No pending OCR items — all confirmed items stay out of this queue.")
        return

    pending_count = len(qdf)
    trusted = list_ocr_auto_confirm_types()
    if trusted:
        st.caption(f"Auto-import enabled for: {', '.join(trusted)}")
    st.info(f"{pending_count} pending — review before importing.")

    for _, qr in qdf.iterrows():
        parsed = json.loads(qr["parsed_json"] or "{}")
        preview = format_parsed_preview(parsed) if show_preview_in_title else ""
        title = ocr_queue_item_title(qr, preview)
        with st.expander(title, expanded=(qr["status"] == "pending_confirmation")):
            st.markdown(ocr_queue_status_marker(qr["status"]), unsafe_allow_html=True)
            p = image_display_path(qr["stored_path"])
            if p.exists() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                st.image(str(p), width=500)

            st.caption(f"OCR status: {qr['status']} | Queue: {ocr_queue_label(qr['detected_type'])}")
            st.caption("Parsed values")
            st.json(parsed)

            if qr["status"] != "pending_confirmation":
                continue

            dtype = qr["detected_type"]

            if dtype == "Apple Health Weight":
                if render_apple_health_weight_wizard(qr, parsed, key_prefix):
                    st.rerun()
                continue

            if dtype in OCR_WIZARD_TYPES:
                st.caption("Pre-filled values — confirm one field at a time below.")
                if render_ocr_validation_wizard(qr, parsed, dtype, key_prefix):
                    st.rerun()
                continue

            values = dict(parsed)
            values = _render_ocr_queue_item_form(qr, values, dtype, key_prefix)

            c_confirm, c_skip = st.columns(2)
            if c_confirm.button("Confirm and import", key=f"{key_prefix}_confirm_{qr['id']}"):
                import_confirmed_queue_item(qr, values)
                st.success("Imported.")
                st.rerun()
            if c_skip.button("Mark as reviewed / skip", key=f"{key_prefix}_skip_{qr['id']}"):
                finalize_ocr_queue_item(qr, "skipped", "User skipped")
                st.warning("Skipped.")
                st.rerun()


def file_sha256(path, block_size=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(block_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def registry_contains(file_hash):
    c = conn()
    row = c.execute("SELECT file_hash FROM file_registry WHERE file_hash = ?", (file_hash,)).fetchone()
    c.close()
    return row is not None


def ocr_queue_has_hash(file_hash):
    c = conn()
    row = c.execute("SELECT id FROM ocr_queue WHERE file_hash = ?", (file_hash,)).fetchone()
    c.close()
    return row is not None


def find_duplicate_import(path, file_hash):
    """Skip only when the exact content hash is already OCR-processed and classified."""
    if is_image_file(path):
        if not ocr_fully_processed(file_hash):
            return None
        prior = registry_entry_for_hash(file_hash)
        if prior and prior.get("detected_type") == "Unclassified Image":
            return "unclassified_reclassify"
        return "content_hash"
    if registry_contains(file_hash):
        prior = registry_entry_for_hash(file_hash)
        if prior and str(prior.get("detected_type") or "") == "PDF":
            return "unclassified_reclassify"
        return "content_hash"
    return None


def register_file(file_hash, source_path, stored_path, detected_type, status="stored", notes="", file_name=None, file_size=None, file_mtime=None):
    src = Path(source_path)
    c = conn()
    c.execute(
        """
        INSERT OR REPLACE INTO file_registry
        (file_hash, first_seen, source_path, stored_path, detected_type, status, notes, file_name, file_size, file_mtime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            file_hash,
            datetime.now().isoformat(timespec="seconds"),
            str(source_path),
            str(stored_path),
            detected_type,
            status,
            notes,
            file_name or src.name,
            int(file_size) if file_size is not None else int(src.stat().st_size),
            float(file_mtime) if file_mtime is not None else float(src.stat().st_mtime),
        ),
    )
    c.commit()
    c.close()


def load_file_registry():
    c = conn()
    try:
        df = pd.read_sql("SELECT * FROM file_registry ORDER BY first_seen DESC", c)
    except Exception:
        df = pd.DataFrame()
    c.close()
    return df


def detect_file_type(path):
    name = path.name.lower()
    ext = path.suffix.lower()

    if ext in [".xml"] and "export" in name:
        return "Apple Health XML"
    if ext in [".zip"]:
        try:
            with zipfile.ZipFile(path) as zf:
                names = [n.lower() for n in zf.namelist()]
                if any("sleep" in n and n.endswith(".json") for n in names):
                    return "Oura Export"
                if any("readiness" in n and n.endswith(".json") for n in names):
                    return "Oura Export"
        except Exception:
            pass
        if "oura" in name or "ring" in name:
            return "Oura Export"
    if ext in [".json"] and any(token in name for token in ("oura", "sleep", "readiness", "activity")):
        return "Oura Export"
    if ext in [".csv"]:
        if "strong" in name or "workout" in name:
            return "Strong CSV"
        if csv_looks_like_strong(path):
            return "Strong CSV"
        if "fatsecret" in name or "fat_secret" in name:
            return "FatSecret CSV"
        return "Generic CSV"

    if ext in [".xlsx", ".xls"]:
        if "fatsecret" in name or "food" in name or "diary" in name:
            return "FatSecret CSV"
        return "Generic CSV"

    if ext in [".jpg", ".jpeg", ".png", ".heic", ".webp"]:
        if "dexa" in name or "fitpal" in name or "hologic" in name or "dexafit" in name:
            return "DEXA"
        if "oura" in name or "sleep" in name or "readiness" in name:
            return "Oura"
        if "fatsecret" in name or "food" in name or "diary" in name or "macro" in name:
            return "FatSecret"
        if "strong" in name or "workout" in name or "lift" in name or "training" in name:
            return "Workout"
        if "scale" in name or "weight" in name or "withings" in name or "body comp" in name:
            return "Scale"
        return "Unclassified Image"

    if ext in [".pdf"]:
        if "dexa" in name or "hologic" in name or "dexafit" in name:
            return "DEXA"
        if filename_looks_like_fatsecret_pdf(path):
            return "FatSecret"
        return "PDF"

    return "Unknown"


def target_folder_for_type(detected_type):
    if detected_type == "DEXA":
        return UPLOAD_DIR / "DEXA"
    if detected_type == "Oura":
        return UPLOAD_DIR / "Oura"
    if detected_type == "Oura Export":
        return UPLOAD_DIR / "Oura"
    if detected_type == "Scale":
        return UPLOAD_DIR / "Other"
    if detected_type == "Apple Health Weight":
        return UPLOAD_DIR / "AppleHealth"
    if detected_type in ["FatSecret", "FatSecret CSV"]:
        return UPLOAD_DIR / "FatSecret"
    if detected_type in ["Workout", "Strong CSV"]:
        return UPLOAD_DIR / "Workouts"
    if detected_type == "Apple Health XML":
        return UPLOAD_DIR / "AppleHealth"
    return UPLOAD_DIR / "Other"


def ingest_inbox_file(path, source_label):
    path = Path(path)
    stat = path.stat()
    fh = file_sha256(path)
    dtype = detect_file_type(path)
    ocr_text = ""
    ocr_meta = {"status": "skipped", "char_count": 0, "error": ""}
    is_pdf = path.suffix.lower() == ".pdf"
    if is_image_file(path):
        ocr_meta = run_ocr(path)
        ocr_text = ocr_meta.get("text") or ""
        dtype = classify_image(path, ocr_text)
    elif is_pdf:
        ocr_text = extract_pdf_text(path)
        ocr_meta = {
            "status": "ok" if ocr_text else "empty",
            "char_count": len(ocr_text),
            "error": "" if ocr_text else "no_text_extracted",
        }
        dtype = classify_pdf(path, ocr_text)

    folder = target_folder_for_type(dtype)
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.name)
    dest = folder / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe}"
    shutil.copy2(path, dest)
    if path.suffix.lower() == ".heic":
        convert_heic_to_png(dest, dest.with_suffix(".png"))

    is_image = is_image_file(path)
    parsed = parse_by_type(dtype, ocr_text)
    queue_status = "pending_confirmation" if is_image else "stored"
    ocr_note = f"ocr={ocr_meta.get('status')}; chars={ocr_meta.get('char_count', 0)}"
    register_file(
        fh,
        path,
        dest,
        dtype,
        queue_status,
        f"{source_label} import | {ocr_queue_label(dtype)} | {ocr_note}",
        file_name=path.name,
        file_size=stat.st_size,
        file_mtime=stat.st_mtime,
    )
    auto_confirmed = False
    image_detail_notes = []
    if is_image:
        enqueue_ocr(
            fh,
            dest,
            dtype,
            ocr_text,
            parsed,
            status=queue_status,
            notes=f"{ocr_queue_label(dtype)} | {source_label} | {ocr_note}",
        )
        auto_confirmed = try_auto_confirm_ocr_by_hash(fh)
        if not auto_confirmed:
            if dtype == "FatSecret" and parsed.get("calories"):
                fs_applied = upsert_fatsecret_from_screenshot(parsed, parse_inbox_image_date(path), source_path=path)
                if fs_applied:
                    image_detail_notes.append(f"daily_log updated for {parse_inbox_image_date(path).isoformat()}")
                else:
                    image_detail_notes.append(
                        f"FatSecret skipped for {parse_inbox_image_date(path).isoformat()} (newer data on file)"
                    )
            if dtype in ("Apple Health Weight", "Scale") and parsed.get("weight_lbs"):
                if not (dtype == "Apple Health Weight" and parsed.get("weight_entries")):
                    weight_applied = upsert_weight_from_screenshot(
                        parsed, parse_inbox_image_date(path), dtype, file_hash=fh, source_path=path
                    )
                    if weight_applied:
                        image_detail_notes.append(f"{dtype} → daily_log {parse_inbox_image_date(path).isoformat()}")
                    else:
                        image_detail_notes.append(f"{dtype} skipped (newer data on file)")

    rows_imported, struct_detail = auto_import_structured_file(path, dtype)
    detail_parts = [struct_detail] if struct_detail else []
    detail_parts.extend(image_detail_notes)
    if is_pdf and dtype == "DEXA" and rows_imported <= 0:
        parsed = parse_by_type(dtype, ocr_text)
        summary = auto_import_dexa_parsed(
            parsed,
            source_path=str(dest),
            notes=f"DEXA PDF import | {source_label}",
        )
        if summary:
            rows_imported = 1
            detail_parts.append(summary.get("message") or "DEXA PDF imported")
        elif parsed.get("body_fat_pct"):
            detail_parts.append(
                f"DEXA PDF parsed ({parsed.get('scan_date')}) — missing fields for auto-import"
            )
    if is_pdf and dtype == "FatSecret" and rows_imported <= 0:
        parsed = parse_fatsecret_food_diary_pdf(ocr_text, path.name)
        if parsed.get("calories"):
            if not parsed.get("log_date"):
                parsed["log_date"] = infer_fatsecret_log_date(path, parsed).isoformat()
            if upsert_daily(
                parsed,
                source="FatSecret",
                source_path=path,
                data_ts=parse_document_timestamp(path, parsed.get("log_date")),
            ):
                rows_imported = 1
                detail_parts.append(
                    f"FatSecret food diary PDF imported ({parsed.get('log_date')}, {int(float(parsed['calories']))} kcal)"
                )
            else:
                detail_parts.append("FatSecret food diary PDF skipped — newer data already on file")
    if is_image:
        if auto_confirmed:
            detail_parts.append(f"auto-imported trusted {dtype} OCR")
        else:
            detail_parts.append("queued for OCR confirmation")
    detail = "; ".join(p for p in detail_parts if p) or "archived"

    save_import_batch(
        source_label,
        dtype,
        1,
        rows_imported,
        "imported",
        f"{path.name} | {detail}",
    )
    return {
        "file": str(path),
        "status": "imported",
        "type": dtype,
        "stored": str(dest),
        "detail": detail,
        "rows": rows_imported,
    }


def import_inbox_folder(scan_dir, source_label="Auto Inbox Scanner"):
    scan_dir = Path(scan_dir).expanduser()
    summary = {"folder": str(scan_dir), "found": 0, "imported": 0, "skipped": 0, "failed": 0, "files": []}

    if not scan_dir.exists():
        summary["failed"] = 1
        summary["files"].append(
            {"file": str(scan_dir), "status": "failed", "type": "", "stored": "", "detail": "missing_folder"}
        )
        save_import_batch(source_label, str(scan_dir), 0, 0, "failed", "Inbox folder missing")
        return summary

    allowed = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".pdf", ".csv", ".xml", ".txt", ".xlsx", ".xls"}
    inbox_files = [
        path for path in scan_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed
    ]
    for path in sorted(inbox_files, key=lambda p: p.stat().st_mtime):
        summary["found"] += 1
        try:
            fh = file_sha256(path)
            dup_reason = find_duplicate_import(path, fh)
            if dup_reason:
                if dup_reason == "unclassified_reclassify":
                    prior = registry_entry_for_hash(fh)
                    stored = (prior or {}).get("stored_path") or str(path)
                    if path.suffix.lower() == ".pdf" or str(stored).lower().endswith(".pdf"):
                        reclassified = reclassify_stored_pdf(path, stored, fh, source_label)
                    else:
                        reclassified = reclassify_stored_image(path, stored, fh, source_label)
                    if reclassified:
                        summary["imported"] += 1
                        summary["files"].append(reclassified)
                        save_import_batch(
                            source_label,
                            reclassified["type"],
                            1,
                            int(reclassified.get("rows") or 0),
                            "reclassified",
                            reclassified["detail"],
                        )
                        continue
                summary["skipped"] += 1
                summary["files"].append(
                    {
                        "file": str(path),
                        "status": "skipped",
                        "type": detect_file_type(path),
                        "stored": "",
                        "detail": f"duplicate ({dup_reason})",
                    }
                )
                continue

            result = ingest_inbox_file(path, source_label)
            summary["imported"] += 1
            summary["files"].append(result)
        except Exception as exc:
            summary["failed"] += 1
            summary["files"].append(
                {"file": str(path), "status": "failed", "type": "", "stored": "", "detail": str(exc)}
            )
            save_import_batch(source_label, detect_file_type(path) if path else "Unknown", 1, 0, "failed", str(exc))

    save_import_batch(
        source_label,
        "Inbox Summary",
        summary["found"],
        summary["imported"],
        "summary",
        f"found={summary['found']} imported={summary['imported']} skipped={summary['skipped']} failed={summary['failed']}",
    )
    return summary


def diagnose_inbox_folder(scan_dir=None):
    """Enumerate every inbox file and report OCR candidate status."""
    scan_dir = Path(scan_dir or get_inbox_folder()).expanduser()
    allowed = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".pdf", ".csv", ".xml", ".txt", ".xlsx", ".xls"}
    rows = []
    if not scan_dir.exists():
        return pd.DataFrame([{
            "filename": str(scan_dir),
            "hash": "",
            "extension": "",
            "file_mtime": "",
            "discovered": False,
            "image_candidate": False,
            "skipped": True,
            "skip_reason": "inbox folder missing",
            "ocr_run": False,
            "final_category": "",
        }])

    all_on_disk = sorted([p for p in scan_dir.rglob("*") if p.is_file()], key=lambda p: p.name.lower())
    image_paths = {p.resolve() for p in list_inbox_image_files(scan_dir)}
    for path in all_on_disk:
        ext = path.suffix.lower()
        fh = file_sha256(path)
        mtime = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
        is_img = path.resolve() in image_paths
        ocr_entry = ocr_entry_for_hash(fh) if is_img else None
        dup = find_duplicate_import(path, fh) if is_img else ("content_hash" if registry_contains(fh) else None)
        ocr_run = bool(ocr_entry and ocr_entry.get("ocr_text", "").strip())
        final_category = ocr_entry.get("detected_type", "") if ocr_entry else (detect_file_type(path) if is_img else detect_file_type(path))

        if not is_img:
            skipped = bool(registry_contains(fh))
            skip = "structured/non-image duplicate" if skipped else "structured/non-image — not OCR candidate"
        elif ocr_fully_processed(fh):
            skipped = True
            skip = "ocr-processed and classified (content_hash)"
        elif dup == "unclassified_reclassify":
            skipped = False
            skip = "would reclassify unclassified image"
        elif dup:
            skipped = True
            skip = f"duplicate ({dup})"
        else:
            skipped = False
            skip = "none — would ingest"

        rows.append({
            "filename": path.name,
            "extension": ext,
            "hash": fh,
            "file_mtime": mtime,
            "discovered": True,
            "image_candidate": is_img,
            "skipped": skipped,
            "skip_reason": skip,
            "ocr_run": ocr_run,
            "final_category": final_category or "",
        })
    return pd.DataFrame(rows)


def reprocess_inbox_images(scan_dir, source_label="Reprocess Inbox Images"):
    """OCR every inbox image; skip only exact hashes already OCR-processed and classified."""
    scan_dir = Path(scan_dir).expanduser()
    summary = {"folder": str(scan_dir), "found": 0, "imported": 0, "skipped": 0, "failed": 0, "files": []}

    if not scan_dir.exists():
        summary["failed"] = 1
        summary["files"].append(
            {"file": str(scan_dir), "status": "failed", "type": "", "stored": "", "detail": "missing_folder"}
        )
        return summary

    inbox_files = list_inbox_image_files(scan_dir)
    for path in sorted(inbox_files, key=lambda p: p.stat().st_mtime):
        summary["found"] += 1
        try:
            fh = file_sha256(path)
            dup_reason = find_duplicate_import(path, fh)
            if dup_reason == "unclassified_reclassify":
                prior = registry_entry_for_hash(fh)
                reclassified = reclassify_stored_image(path, prior["stored_path"], fh, source_label)
                if reclassified:
                    summary["imported"] += 1
                    summary["files"].append(reclassified)
                    continue
            if dup_reason:
                summary["skipped"] += 1
                summary["files"].append(
                    {
                        "file": str(path),
                        "status": "skipped",
                        "type": detect_file_type(path),
                        "stored": "",
                        "detail": f"duplicate ({dup_reason})",
                    }
                )
                continue
            result = ingest_inbox_file(path, source_label)
            summary["imported"] += 1
            summary["files"].append(result)
        except Exception as exc:
            summary["failed"] += 1
            summary["files"].append(
                {"file": str(path), "status": "failed", "type": "", "stored": "", "detail": str(exc)}
            )

    save_import_batch(
        source_label,
        "Reprocess Summary",
        summary["found"],
        summary["imported"],
        "summary",
        f"found={summary['found']} imported={summary['imported']} skipped={summary['skipped']} failed={summary['failed']}",
    )
    return summary


def scan_inbox_folder(scan_dir):
    summary = import_inbox_folder(scan_dir, source_label="Auto Inbox Scanner")
    return summary["files"]


def run_startup_inbox_import(inbox_folder=None):
    folder = Path(inbox_folder).expanduser() if inbox_folder else get_inbox_folder()
    return import_inbox_folder(folder, source_label="Startup Auto Import")


def unique_inbox_copy_dest(inbox_dir, filename):
    inbox_dir = Path(inbox_dir)
    inbox_dir.mkdir(parents=True, exist_ok=True)
    dest = inbox_dir / filename
    if not dest.exists():
        return dest
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return inbox_dir / f"{dest.stem}_{ts}{dest.suffix}"


def _inbox_content_hash_index(inbox_dir):
    hashes = {}
    inbox_dir = Path(inbox_dir)
    if not inbox_dir.exists():
        return hashes
    for path in inbox_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            hashes[file_sha256(path)] = path
        except OSError:
            pass
    return hashes


def sync_health_data_source_to_inbox(source_dir=None, inbox_dir=None):
    """Copy new files from Health Data source folder into TU Inbox (copy only, no moves)."""
    source_dir = Path(source_dir or get_health_data_source_folder()).expanduser()
    inbox_dir = Path(inbox_dir or get_inbox_folder()).expanduser()
    summary = {
        "folder": str(source_dir),
        "inbox": str(inbox_dir),
        "found": 0,
        "copied": 0,
        "skipped": 0,
        "failed": 0,
        "files": [],
    }

    if not source_dir.exists():
        summary["failed"] = 1
        summary["files"].append(
            {"file": str(source_dir), "status": "failed", "stored": "", "detail": "source_folder_missing"}
        )
        return summary

    inbox_hashes = _inbox_content_hash_index(inbox_dir)
    for path in sorted(source_dir.rglob("*"), key=lambda p: p.stat().st_mtime):
        if not path.is_file() or path.suffix.lower() not in HEALTH_DATA_SYNC_EXTENSIONS:
            continue
        summary["found"] += 1
        try:
            fh = file_sha256(path)
            if fh in inbox_hashes:
                summary["skipped"] += 1
                summary["files"].append(
                    {
                        "file": str(path),
                        "status": "skipped",
                        "stored": str(inbox_hashes[fh]),
                        "detail": "duplicate_content_hash",
                    }
                )
                continue
            dest = unique_inbox_copy_dest(inbox_dir, path.name)
            shutil.copy2(path, dest)
            inbox_hashes[fh] = dest
            detail = "copied"
            if dest.name != path.name:
                detail = f"filename_conflict; saved as {dest.name}"
            summary["copied"] += 1
            summary["files"].append(
                {"file": str(path), "status": "copied", "stored": str(dest), "detail": detail}
            )
        except Exception as exc:
            summary["failed"] += 1
            summary["files"].append(
                {"file": str(path), "status": "failed", "stored": "", "detail": str(exc)}
            )

    save_import_batch(
        "Startup Source Sync",
        str(source_dir),
        summary["found"],
        summary["copied"],
        "summary",
        f"found={summary['found']} copied={summary['copied']} skipped={summary['skipped']} failed={summary['failed']}",
    )
    return summary


def format_startup_sync_caption(sync_summary, import_summary):
    sync_summary = sync_summary or {}
    import_summary = import_summary or {}
    folder = sync_summary.get("folder") or str(get_health_data_source_folder())
    details = [f.get("detail") for f in (sync_summary.get("files") or [])]
    if "source_folder_missing" in details:
        return (
            f"Google Drive Health Data folder not found (`{folder}`). "
            "Start Google Drive for Desktop, then use **Sync Google Drive now**."
        )
    copied = int(sync_summary.get("copied") or 0)
    skipped = int(sync_summary.get("skipped") or 0)
    imported = int(import_summary.get("imported") or 0)
    failed = int(sync_summary.get("failed") or 0) + int(import_summary.get("failed") or 0)
    return (
        f"Google Drive Health Data: **{copied}** new file(s) copied, "
        f"**{imported}** imported, **{skipped}** already on file"
        + (f", **{failed}** failed" if failed else "")
        + "."
    )


def run_startup_health_data_pipeline(source_folder=None, inbox_folder=None, wait_for_drive=True):
    """Copy new Google Drive Health Data files into the inbox and import them."""
    source = Path(source_folder).expanduser() if source_folder else None
    if source is None and wait_for_drive:
        source = wait_for_health_data_source_folder()
    elif source is None:
        source = get_health_data_source_folder()
    sync_summary = sync_health_data_source_to_inbox(source, inbox_folder)
    import_summary = run_startup_inbox_import(inbox_folder or get_inbox_folder())
    try:
        refresh_apple_health_xml_weights()
    except Exception:
        pass
    return sync_summary, import_summary


def save_import_batch(import_type, source_name, file_count=0, row_count=0, status="saved", notes=""):
    c = conn()
    c.execute(
        "INSERT INTO import_batches (import_date, import_type, source_name, file_count, row_count, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), import_type, source_name, int(file_count), int(row_count), status, notes),
    )
    c.commit()
    c.close()


def load_import_batches():
    c = conn()
    try:
        df = pd.read_sql("SELECT * FROM import_batches ORDER BY import_date DESC", c)
    except Exception:
        df = pd.DataFrame()
    c.close()
    return df


def import_status_cards(daily, dexa, screens):
    last_daily = daily["log_date"].max().date().isoformat() if not daily.empty else "None"
    last_dexa = dexa["scan_date"].max().date().isoformat() if not dexa.empty else "None"
    last_screen = latest_screenshot_import_timestamp(screens)
    return last_daily, last_dexa, last_screen


def format_import_timestamp(value):
    if value is None or value == "None":
        return "None"
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d %H:%M")
    except Exception:
        text = str(value).strip()
        if len(text) >= 16 and text[10] == "T":
            return text[:10] + " " + text[11:16]
        return text[:19] if len(text) > 10 else text


def latest_screenshot_import_timestamp(screens=None):
    """Most recent screenshot/OCR image import time across screenshots, OCR queue, and file registry."""
    stamps = []
    screens = screens if screens is not None else load_screenshots()
    if not screens.empty and "upload_date" in screens.columns:
        stamps.extend(screens["upload_date"].dropna().astype(str).tolist())

    queue = load_ocr_queue()
    if not queue.empty:
        imported = queue[queue["status"].isin(OCR_TERMINAL_STATUSES)]
        if not imported.empty and "created_at" in imported.columns:
            stamps.extend(imported["created_at"].dropna().astype(str).tolist())

    reg = load_file_registry()
    if not reg.empty:
        image_rows = reg[reg["detected_type"].isin(IMAGE_QUEUE_TYPES)]
        if not image_rows.empty and "first_seen" in image_rows.columns:
            stamps.extend(image_rows["first_seen"].dropna().astype(str).tolist())

    if not stamps:
        return "None"
    return max(stamps)


def sync_imported_ocr_to_daily_log(reparse_missing=False):
    """
    Push confirmed OCR imports into daily_log (and related tables).
    Re-open only unreviewed FatSecret imports that still lack calorie data.
    """
    queue = load_ocr_queue()
    if queue.empty:
        return {"synced": 0, "reopened": 0, "details": []}

    daily_df = load_daily()
    synced = 0
    reopened = 0
    details = []

    for _, qr in queue.iterrows():
        status = str(qr.get("status") or "")
        if status not in OCR_TERMINAL_STATUSES or status == "skipped":
            continue

        dtype = qr.get("detected_type")
        parsed = json.loads(qr.get("parsed_json") or "{}")
        stored_path = qr.get("stored_path") or ""
        log_day = infer_fatsecret_log_date(stored_path, parsed, qr.get("created_at"))

        if reparse_missing and qr.get("ocr_text") and not _ocr_queue_user_reviewed(qr):
            fresh = parse_by_type(dtype, qr.get("ocr_text") or "", apply_learning=True)
            for key, val in (fresh or {}).items():
                if val not in (None, "", 0, 0.0):
                    parsed[key] = val
            if dtype == "FatSecret" and fresh:
                upsert_ocr_queue(
                    qr.get("file_hash"),
                    qr.get("stored_path"),
                    dtype,
                    qr.get("ocr_text") or "",
                    parsed,
                    status=status,
                    notes=qr.get("notes") or "",
                    preserve_terminal_status=True,
                )

        if dtype == "FatSecret":
            calories = parsed.get("calories")
            has_calories = calories is not None and float(calories) > 0
            if not has_calories:
                parsed, backfilled = _backfill_fatsecret_parsed_from_daily(parsed, daily_df, log_day)
                if backfilled:
                    calories = parsed.get("calories")
                    has_calories = calories is not None and float(calories) > 0
                    if has_calories and qr.get("file_hash"):
                        upsert_ocr_queue(
                            qr.get("file_hash"),
                            qr.get("stored_path"),
                            dtype,
                            qr.get("ocr_text") or "",
                            parsed,
                            status=status,
                            notes=qr.get("notes") or "",
                            preserve_terminal_status=True,
                        )
            if not has_calories:
                if _ocr_queue_user_reviewed(qr):
                    continue
                if get_fatsecret_intake(daily_df, log_day) is not None:
                    continue
                if status == "skipped":
                    continue
                update_ocr_status(
                    int(qr["id"]),
                    "pending_confirmation",
                    "Re-opened: FatSecret OCR has no calorie data — confirm values manually",
                )
                if qr.get("file_hash"):
                    update_file_registry_status(
                        qr["file_hash"],
                        "pending_confirmation",
                        "Re-opened for FatSecret validation",
                    )
                reopened += 1
                details.append(f"Re-opened FatSecret {Path(stored_path).name}")
                continue
            existing_row = None
            if not daily_df.empty:
                day_rows = daily_df[daily_df["log_date"].dt.date == log_day]
                for _, dr in day_rows.iterrows():
                    if is_fatsecret_intake_row(dr.to_dict()):
                        existing_row = dr.to_dict()
                        break
            if existing_row:
                prot = parsed.get("protein_g")
                same_cal = float(existing_row.get("calories") or 0) == float(calories)
                same_prot = prot is None or float(existing_row.get("protein_g") or 0) == float(prot)
                if same_cal and same_prot:
                    continue
            if upsert_fatsecret_from_screenshot(parsed, log_day, source_path=stored_path):
                synced += 1
                details.append(f"FatSecret → daily_log {log_day.isoformat()}")
                daily_df = load_daily()
            else:
                details.append(f"FatSecret skipped {log_day.isoformat()} (newer data on file)")
            continue

        if dtype == "Oura":
            if not oura_has_sync_fields(parsed):
                continue
            values = dict(parsed)
            values["log_date"] = log_day.isoformat()
            values["notes"] = oura_screenshot_notes(values)
            if upsert_daily(
                values,
                source=dtype,
                source_path=stored_path,
                file_hash=qr.get("file_hash"),
                data_ts=parse_document_timestamp(stored_path, log_day),
            ):
                synced += 1
                details.append(f"Oura → daily_log {log_day.isoformat()}")
            else:
                details.append(f"Oura skipped {log_day.isoformat()} (newer data on file)")
            continue

        if dtype in ("Scale", "Apple Health Weight"):
            if dtype == "Apple Health Weight" and parsed.get("weight_entries"):
                save_weight_measurements(
                    parsed["weight_entries"],
                    source=dtype,
                    file_hash=qr.get("file_hash"),
                    notes=tag_import_notes(dtype, "OCR sync import"),
                )
                sync_daily_log_from_weight_entries(
                    parsed["weight_entries"], source=dtype, source_path=stored_path
                )
                synced += 1
                details.append(f"Apple Health weights → {len(parsed['weight_entries'])} measurements")
            elif parsed.get("weight_lbs"):
                if upsert_weight_from_screenshot(
                    parsed, log_day, dtype, file_hash=qr.get("file_hash"), source_path=stored_path
                ):
                    synced += 1
                    details.append(f"{dtype} → daily_log {log_day.isoformat()}")
                else:
                    details.append(f"{dtype} skipped {log_day.isoformat()} (newer data on file)")
            continue

        if dtype == "DEXA":
            scan_date = parsed.get("scan_date") or log_day.isoformat()
            weight = parsed.get("weight_lbs")
            bf = parsed.get("body_fat_pct")
            fat_mass = parsed.get("fat_mass_lbs")
            lean_mass = parsed.get("lean_mass_lbs")
            if weight and bf and fat_mass and lean_mass:
                apply_dexa_scan_record(
                    (
                        scan_date,
                        weight,
                        bf,
                        fat_mass,
                        lean_mass,
                        parsed.get("vat_mass_g"),
                        parsed.get("vat_volume_cm3"),
                        parsed.get("vat_area_cm2"),
                        stored_path,
                        "OCR sync import",
                    )
                )
                synced += 1
                details.append(f"DEXA → scans {scan_date}")

    return {"synced": synced, "reopened": reopened, "details": details}


def load_workout_calibration():
    c = conn()
    df = pd.read_sql("SELECT * FROM workout_calibration ORDER BY workout", c)
    c.close()
    return df


def format_workout_calibration_table(df):
    if df.empty:
        return df
    out = df.copy()
    if "burn_source" not in out.columns:
        out["burn_source"] = "estimate"
    out["Source"] = out["burn_source"].fillna("estimate").map(
        lambda src: "Observed" if str(src).lower() == "observed" else "Estimate (MET)"
    )
    if "expected_burn" in out.columns:
        out["Expected burn (kcal)"] = out["expected_burn"].map(
            lambda v: f"{v:.0f}" if pd.notna(v) else "—"
        )
    if "met_used" in out.columns:
        out["MET used"] = out["met_used"].map(lambda v: f"{v:.1f}" if pd.notna(v) else "—")
    if "duration_min" in out.columns:
        out["Avg duration (min)"] = out["duration_min"].map(
            lambda v: f"{v:.0f}" if pd.notna(v) else "—"
        )
    if "observed_count" in out.columns:
        out["Observations"] = out["observed_count"].fillna(0).astype(int)
    if "last_updated" in out.columns:
        out["Last updated"] = out["last_updated"].fillna("").astype(str).str[:10]
    display_cols = [
        c
        for c in [
            "workout",
            "Expected burn (kcal)",
            "Source",
            "MET used",
            "Avg duration (min)",
            "Observations",
            "Last updated",
        ]
        if c in out.columns
    ]
    out = out[display_cols].rename(columns={"workout": "Workout"})
    return out


def get_workout_expected_burn(workout_name, s):
    if not workout_name:
        return 0.0
    c = conn()
    row = c.execute("SELECT expected_burn FROM workout_calibration WHERE workout = ?", (workout_name,)).fetchone()
    c.close()
    if row and row[0] is not None:
        return float(row[0])
    return float(s.get("default_workout_burn", 350.0))


def save_workout_estimate(workout_name, estimated_burn, met=None, duration_min=None):
    """Save MET-based burn estimate; never overwrites observed calibration."""
    if not workout_name or estimated_burn is None:
        return
    c = conn()
    existing = c.execute(
        "SELECT burn_source FROM workout_calibration WHERE workout = ?",
        (workout_name,),
    ).fetchone()
    if existing and str(existing[0] or "").lower() == "observed":
        c.close()
        return

    now = datetime.now().isoformat(timespec="seconds")
    c.execute(
        """
        INSERT INTO workout_calibration
            (workout, expected_burn, observed_count, last_updated, burn_source, met_used, duration_min)
        VALUES (?, ?, 0, ?, 'estimate', ?, ?)
        ON CONFLICT(workout) DO UPDATE SET
            expected_burn = excluded.expected_burn,
            observed_count = 0,
            last_updated = excluded.last_updated,
            burn_source = 'estimate',
            met_used = excluded.met_used,
            duration_min = excluded.duration_min
        WHERE workout_calibration.burn_source IS NULL
           OR workout_calibration.burn_source != 'observed'
        """,
        (workout_name, float(estimated_burn), now, met, duration_min),
    )
    c.commit()
    c.close()


def save_workout_observation(workout_name, observed_burn):
    if not workout_name or observed_burn is None:
        return
    c = conn()
    existing = c.execute("SELECT expected_burn, observed_count FROM workout_calibration WHERE workout = ?", (workout_name,)).fetchone()
    if existing:
        old, n = float(existing[0]), int(existing[1] or 1)
        new = (old * n + float(observed_burn)) / (n + 1)
        c.execute(
            """
            UPDATE workout_calibration
            SET expected_burn = ?, observed_count = ?, last_updated = ?, burn_source = 'observed'
            WHERE workout = ?
            """,
            (new, n + 1, datetime.now().isoformat(timespec="seconds"), workout_name),
        )
    else:
        c.execute(
            """
            INSERT INTO workout_calibration
            (workout, expected_burn, observed_count, last_updated, burn_source)
            VALUES (?, ?, ?, ?, 'observed')
            """,
            (workout_name, float(observed_burn), 1, datetime.now().isoformat(timespec="seconds")),
        )
    c.commit()
    c.close()


def estimate_end_of_day_deficit(row, s, projected_steps=None, workout_name=None, workout_done=False):
    calories = float(row.get("calories") or 0)
    current_steps = float(row.get("steps") or 0)
    steps = projected_steps if projected_steps is not None else max(current_steps, float(s.get("default_step_goal", 12000)))
    base = float(s["baseline_maintenance"]) + float(s.get("adaptive_maintenance_adjustment", 0))
    step_burn = steps / 1000 * float(s["step_calories_per_1000"])
    active_energy = float(row.get("active_energy") or 0)
    resting_energy = float(row.get("resting_energy") or 0)
    workout_burn = get_workout_expected_burn(workout_name or row.get("workout"), s) if workout_done or workout_name else 0
    oura_total_burn = float(row.get("oura_burn") or 0)

    if oura_total_burn > 0:
        total_burn = oura_total_burn
    elif active_energy > 0 and resting_energy > 0:
        total_burn = active_energy + resting_energy + workout_burn
    else:
        total_burn = base + step_burn + workout_burn

    deficit = total_burn - calories
    target = float(s["target_deficit"])
    extra_deficit = max(0, deficit - target)
    snack_unit = float(s.get("snack_calorie_unit", 150))
    snack_units = int(round(extra_deficit / snack_unit)) if extra_deficit > snack_unit / 2 else 0

    return {
        "projected_steps": steps,
        "total_burn": total_burn,
        "calories": calories,
        "deficit": deficit,
        "target_deficit": target,
        "extra_deficit": extra_deficit,
        "snack_recommendation_calories": extra_deficit,
        "snack_units": snack_units,
        "workout_burn": workout_burn,
    }


def load_fuel_workout_schedule():
    raw = get_text_setting("fuel_workout_by_date", "{}")
    try:
        data = json.loads(raw or "{}")
        return data if isinstance(data, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def save_fuel_workout_for_date(log_day, workout_type):
    if not workout_type:
        return
    day_key = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)
    schedule = load_fuel_workout_schedule()
    schedule[day_key] = str(workout_type)
    save_text_setting("fuel_workout_by_date", json.dumps(schedule))


def get_fuel_workout_for_date(log_day):
    day_key = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)
    saved = load_fuel_workout_schedule().get(day_key)
    if saved in FUEL_WORKOUT_DEFAULTS:
        return saved
    return None


def suggest_rotated_workout(for_day):
    """Next A → B → C workout after the most recent saved rotation day before for_day."""
    day_key = for_day.isoformat() if hasattr(for_day, "isoformat") else str(for_day)
    schedule = load_fuel_workout_schedule()
    prior_dates = sorted(d for d in schedule.keys() if d < day_key)
    last_workout = None
    for d_str in reversed(prior_dates):
        workout = schedule.get(d_str)
        if workout in FUEL_ROTATION_WORKOUTS:
            last_workout = workout
            break
    if last_workout is None:
        return FUEL_ROTATION_WORKOUTS[0]
    idx = FUEL_ROTATION_WORKOUTS.index(last_workout)
    return FUEL_ROTATION_WORKOUTS[(idx + 1) % len(FUEL_ROTATION_WORKOUTS)]


def resolve_fuel_workout_for_day(fuel_day):
    saved = get_fuel_workout_for_date(fuel_day)
    if saved:
        return saved
    return suggest_rotated_workout(fuel_day)


def is_fuel_workout_confirmed_for_date(fuel_day):
    day_key = fuel_day.isoformat() if hasattr(fuel_day, "isoformat") else str(fuel_day)
    return get_text_setting("fuel_workout_confirmed_date", "") == day_key


def mark_fuel_workout_confirmed(fuel_day):
    day_key = fuel_day.isoformat() if hasattr(fuel_day, "isoformat") else str(fuel_day)
    save_text_setting("fuel_workout_confirmed_date", day_key)


def sync_fuel_workout_session_state(fuel_day):
    """Keep workout type stable across reloads; refresh when fuel plan date changes."""
    day_key = fuel_day.isoformat() if hasattr(fuel_day, "isoformat") else str(fuel_day)
    resolved = resolve_fuel_workout_for_day(fuel_day)
    if st.session_state.get("fuel_workout_active_day") != day_key:
        st.session_state.fuel_workout_active_day = day_key
        st.session_state.fuel_workout_type = resolved
    elif "fuel_workout_type" not in st.session_state:
        st.session_state.fuel_workout_type = resolved
    elif get_fuel_workout_for_date(fuel_day) and st.session_state.fuel_workout_type != get_fuel_workout_for_date(fuel_day):
        st.session_state.fuel_workout_type = get_fuel_workout_for_date(fuel_day)


def carb_minimum_for_workout(workout_type):
    """Daily net-carb floor by workout / rest day and active mission."""
    floors = get_mission_carb_minimums()
    return float(floors.get(workout_type, FUEL_CARB_DEFAULT_MINIMUM))


def carb_day_type_label(workout_type):
    if workout_type == "Workout B":
        return "leg day"
    if workout_type in ("Workout A", "Workout C"):
        return "A/C workout day"
    if workout_type in ("None", "Long walk / high step day"):
        return "rest day"
    return str(workout_type or "rest day").lower()


def fuel_minimum_target_status(gap, unit="g", tolerance=5.0):
    """Positive gap = logged amount is below the minimum target."""
    if gap is None:
        return "—", ""
    if float(gap) > tolerance:
        return f"{float(gap):.0f} {unit} below", "warn"
    return "On target", "good"


def fuel_calorie_target_status(calorie_adjustment, tolerance=5.0):
    """Positive adjustment = room left before hitting deficit target."""
    if calorie_adjustment is None:
        return "—", ""
    adj = float(calorie_adjustment)
    if adj > tolerance:
        return f"{adj:.0f} kcal room", ""
    if adj < -tolerance:
        return f"{abs(adj):.0f} kcal over", "warn"
    return "On target", "good"


def apply_fuel_target_status(enriched):
    """Attach calorie / protein / carb target status labels for Daily Sync."""
    cal_adj = enriched.get("calorie_adjustment")
    enriched["calorie_target"] = enriched.get("recommended_intake")
    if cal_adj is not None:
        enriched["calorie_status"], enriched["calorie_status_tone"] = fuel_calorie_target_status(cal_adj)
    else:
        enriched["calorie_status"] = "—"
        enriched["calorie_status_tone"] = ""

    pgap = enriched.get("protein_gap")
    enriched["protein_status"], enriched["protein_status_tone"] = fuel_minimum_target_status(pgap, unit="g")

    cgap = enriched.get("carb_gap")
    enriched["carb_target_g"] = enriched.get("carb_minimum_g")
    enriched["carb_status"], enriched["carb_status_tone"] = fuel_minimum_target_status(cgap, unit="g")
    return enriched


def build_carb_increase_steps(carb_g_needed, planned_foods=None):
    """Suggest carb-dense adds when below the workout-day carb floor."""
    remaining = max(0.0, float(carb_g_needed))
    steps = []
    planned = planned_foods or {}

    if remaining > 5:
        k_cfg = FUEL_FOOD_CALORIES["krispies"]
        add_g = min(float(k_cfg["max_g"]), remaining / KRISPIES_CARB_FRACTION)
        if add_g >= 15:
            carb_add = add_g * KRISPIES_CARB_FRACTION
            steps.append(
                f"Add {k_cfg['label']} {add_g:.0f}g (~{carb_add:.0f} g carbs)"
            )
            remaining -= carb_add

    if not planned.get("has_peach") and remaining >= FRUIT_CARB_GRAMS * 0.85:
        steps.append(
            f"Add 1 {FUEL_FOOD_CALORIES['peach']['label'].lower()} (~{FRUIT_CARB_GRAMS:.0f} g carbs)"
        )
        remaining -= FRUIT_CARB_GRAMS

    if not planned.get("has_nectarine") and remaining >= FRUIT_CARB_GRAMS * 0.85:
        steps.append(
            f"Add 1 {FUEL_FOOD_CALORIES['nectarine']['label'].lower()} (~{FRUIT_CARB_GRAMS:.0f} g carbs)"
        )
        remaining -= FRUIT_CARB_GRAMS

    if remaining > 10:
        extra_g = min(120.0, remaining / KRISPIES_CARB_FRACTION)
        steps.append(f"Add ~{extra_g:.0f} g fast carbs (rice, potatoes, or fruit)")

    return steps


def estimate_daily_fuel_target(settings, expected_steps, workout_type, observed_workout_calories=None):
    """Plan today's calorie allowance from activity — does not affect forecasting."""
    baseline = float(settings["baseline_maintenance"]) + float(settings.get("adaptive_maintenance_adjustment", 0))
    steps = max(float(expected_steps or 0), 0.0)
    step_burn = steps / 1000.0 * float(settings["step_calories_per_1000"])

    default_workout_burn = float(FUEL_WORKOUT_DEFAULTS.get(workout_type, 0))
    observed = float(observed_workout_calories or 0)
    if observed > 0:
        workout_burn = observed
        workout_source = "observed"
    else:
        workout_burn = default_workout_burn
        workout_source = "estimated"

    total_expenditure = baseline + step_burn + workout_burn
    target_deficit = float(settings["target_deficit"])
    recommended_intake = total_expenditure - target_deficit
    protein_target = float(settings["protein_target_g"])
    carb_minimum_g = carb_minimum_for_workout(workout_type)

    return {
        "baseline": baseline,
        "step_burn": step_burn,
        "workout_burn": workout_burn,
        "workout_source": workout_source,
        "workout_type": workout_type,
        "expected_steps": steps,
        "total_expenditure": total_expenditure,
        "target_deficit": target_deficit,
        "recommended_intake": recommended_intake,
        "protein_target_g": protein_target,
        "carb_minimum_g": carb_minimum_g,
        "carb_day_type": carb_day_type_label(workout_type),
    }


def compute_daily_burn_snapshot(
    settings,
    day_row,
    steps_so_far,
    step_goal,
    workout_type,
    workout_complete,
    manual_burn_so_far=None,
    oura_burn_so_far=None,
    workout_burn_override=None,
):
    """Live burn so far vs projected end-of-day total from steps, workout, and Oura/manual."""
    row = dict(day_row or {})
    row["workout"] = workout_type
    row["steps"] = steps_so_far

    imported_oura = float(row.get("oura_burn") or 0)
    if oura_burn_so_far is not None and float(oura_burn_so_far) > 0:
        row["oura_burn"] = float(oura_burn_so_far)
    oura = float(row.get("oura_burn") or 0)
    oura_entered_manually = (
        oura_burn_so_far is not None
        and float(oura_burn_so_far) > 0
        and (imported_oura <= 0 or float(oura_burn_so_far) != imported_oura)
    )

    baseline = float(settings["baseline_maintenance"]) + float(settings.get("adaptive_maintenance_adjustment", 0))
    step_rate = float(settings["step_calories_per_1000"])

    steps_so_far = max(0.0, float(steps_so_far or 0))
    step_goal = max(steps_so_far, float(step_goal or settings.get("default_step_goal", 12000)))

    step_burn_so_far = steps_so_far / 1000.0 * step_rate
    step_burn_projected = step_goal / 1000.0 * step_rate

    default_workout_burn = (
        float(FUEL_WORKOUT_DEFAULTS.get(workout_type, 0))
        if workout_type and workout_type != "None"
        else 0.0
    )
    observed = float(workout_burn_override or 0)
    planned_workout_burn = observed if observed > 0 else default_workout_burn

    if workout_complete and workout_type and workout_type != "None":
        workout_burn = planned_workout_burn
        workout_source = "observed" if observed > 0 else "estimated"
    else:
        workout_burn = 0.0
        workout_source = "pending"

    oura = float(row.get("oura_burn") or 0)

    if oura > 0:
        burn_so_far = oura
        burn_so_far_source = "oura_entered" if oura_entered_manually else "oura"
        projected = oura
    elif manual_burn_so_far and float(manual_burn_so_far) > 0:
        burn_so_far = float(manual_burn_so_far)
        burn_so_far_source = "manual"
        projected = float(manual_burn_so_far)
    else:
        day_fraction = min(1.0, steps_so_far / step_goal) if step_goal > 0 else 0.35
        burn_so_far = baseline * day_fraction + step_burn_so_far + workout_burn
        burn_so_far_source = "estimated"
        w_burn = planned_workout_burn if workout_type and workout_type != "None" else 0.0
        projected = baseline + step_burn_projected + w_burn

    projected_workout_burn = planned_workout_burn if workout_type and workout_type != "None" else 0.0

    return {
        "burn_so_far": burn_so_far,
        "projected_daily_burn": projected,
        "baseline": baseline,
        "step_burn_so_far": step_burn_so_far,
        "step_burn_projected": step_burn_projected,
        "workout_burn": projected_workout_burn,
        "workout_burn_so_far": workout_burn,
        "workout_complete": bool(workout_complete),
        "workout_source": workout_source,
        "steps_so_far": steps_so_far,
        "step_goal": step_goal,
        "step_progress_pct": 100.0 * steps_so_far / step_goal if step_goal > 0 else 0.0,
        "burn_so_far_source": burn_so_far_source,
        "undercount": None,
        "oura_burn": oura if oura > 0 else None,
    }


def fuel_plan_from_burn_snapshot(settings, snapshot, workout_type):
    """Build fuel-plan dict using projected daily burn from activity snapshot."""
    target_deficit = float(settings["target_deficit"])
    total = float(snapshot["projected_daily_burn"])
    return {
        "baseline": float(snapshot["baseline"]),
        "step_burn": float(snapshot["step_burn_projected"]),
        "workout_burn": float(snapshot["workout_burn"]),
        "workout_source": snapshot.get("workout_source") or "estimated",
        "workout_type": workout_type,
        "expected_steps": float(snapshot["step_goal"]),
        "total_expenditure": total,
        "projected_daily_burn": total,
        "target_deficit": target_deficit,
        "recommended_intake": total - target_deficit,
        "protein_target_g": float(settings["protein_target_g"]),
        "carb_minimum_g": carb_minimum_for_workout(workout_type),
        "carb_day_type": carb_day_type_label(workout_type),
        "burn_so_far": float(snapshot["burn_so_far"]),
        "burn_so_far_source": snapshot.get("burn_so_far_source"),
        "steps_so_far": float(snapshot["steps_so_far"]),
        "step_goal": float(snapshot["step_goal"]),
        "step_progress_pct": float(snapshot.get("step_progress_pct") or 0),
        "step_burn_so_far": float(snapshot.get("step_burn_so_far") or 0),
        "workout_complete": bool(snapshot.get("workout_complete")),
        "workout_burn_so_far": float(snapshot.get("workout_burn_so_far") or 0),
        "undercount": snapshot.get("undercount"),
        "oura_burn": snapshot.get("oura_burn"),
    }


def is_meal_plan_intake_row(row):
    """Editable daily meal-plan row (template amounts + meals_eaten), not OCR-only."""
    if not row:
        return False
    notes = str(row.get("notes") or "").lower()
    return "meal_items=" in notes or "daily meal template" in notes


def is_fatsecret_intake_row(row):
    if not row:
        return False
    notes = str(row.get("notes") or "").lower()
    is_fs = "[fatsecret]" in notes or "fatsecret" in notes
    if not is_fs:
        return False
    cal = row.get("calories")
    if cal is None or (isinstance(cal, float) and pd.isna(cal)):
        return False
    # Meal planner rows exist before anything is logged (0 kcal) — still valid intake source.
    if is_meal_plan_intake_row(row):
        return float(cal) >= 0
    return float(cal) > 0


def day_has_meal_plan(daily, log_day):
    if daily.empty:
        return False
    rows = daily[daily["log_date"].dt.date == log_day]
    for _, row in rows.iterrows():
        if is_meal_plan_intake_row(row.to_dict()):
            return True
    return False


def _float_or_none(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


FATSECRET_DISPLAY_FIELDS = [
    ("carbs_g", "Net C", "g"),
    ("fiber_g", "Fiber", "g"),
    ("sodium_mg", "Sod", "mg"),
    ("protein_g", "Prot", "g"),
    ("calories", "Calories", "kcal"),
    ("fat_g", "Fat", "g"),
]


def _fatsecret_extras_from_notes(notes):
    extras = {}
    notes = str(notes or "")
    for key in ("fiber_g", "sodium_mg", "lunch_veg_g"):
        match = re.search(rf"{key}=([\d.]+)", notes)
        if match:
            extras[key] = float(match.group(1))
    return extras


def _fatsecret_parsed_from_daily_row(rowd):
    parsed = {
        "calories": _float_or_none(rowd.get("calories")),
        "protein_g": _float_or_none(rowd.get("protein_g")),
        "carbs_g": _float_or_none(rowd.get("carbs_g")),
        "fat_g": _float_or_none(rowd.get("fat_g")),
    }
    parsed.update(_fatsecret_extras_from_notes(rowd.get("notes")))
    return parsed


def format_fatsecret_upload_ts(raw):
    if not raw:
        return "Unknown upload time"
    try:
        return pd.to_datetime(str(raw)).strftime("%b %d, %Y · %I:%M %p")
    except Exception:
        return str(raw)


def _fatsecret_record_from_queue_row(qr, log_day):
    status = str(qr.get("status") or "")
    if status == "skipped":
        return None
    parsed = json.loads(qr.get("parsed_json") or "{}")
    img_date = infer_fatsecret_log_date(qr.get("stored_path") or "", parsed, qr.get("created_at"))
    if img_date != log_day:
        return None
    cal = parsed.get("calories")
    has_cal = cal is not None and float(cal) > 0
    if not has_cal and status in OCR_TERMINAL_STATUSES:
        return None
    stored_path = qr.get("stored_path") or ""
    priority = 3 if status in OCR_TERMINAL_STATUSES else 1
    return {
        "calories": _float_or_none(parsed.get("calories")),
        "protein_g": _float_or_none(parsed.get("protein_g")),
        "carbs_g": _float_or_none(parsed.get("carbs_g")),
        "fat_g": _float_or_none(parsed.get("fat_g")),
        "fiber_g": _float_or_none(parsed.get("fiber_g")),
        "sodium_mg": _float_or_none(parsed.get("sodium_mg")),
        "ts": str(qr.get("created_at") or ""),
        "origin": "ocr_queue",
        "source_path": Path(stored_path).name if stored_path else None,
        "stored_path": stored_path,
        "queue_id": int(qr["id"]),
        "file_hash": qr.get("file_hash"),
        "status": status,
        "parsed": dict(parsed),
        "priority": priority,
        "ocr_text": qr.get("ocr_text") or "",
    }


def collect_fatsecret_records_for_day(daily, log_day):
    """All FatSecret uploads for a calendar day, newest first."""
    records = []
    queue = load_ocr_queue()
    if not queue.empty:
        for _, qr in queue.iterrows():
            if qr.get("detected_type") != "FatSecret":
                continue
            rec = _fatsecret_record_from_queue_row(qr, log_day)
            if rec:
                records.append(rec)

    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            rowd = row.to_dict()
            if not is_fatsecret_intake_row(rowd):
                continue
            notes = str(rowd.get("notes") or "")
            source_name = None
            if "|" in notes:
                tail = notes.split("|")[-1].strip()
                if tail.lower().endswith((".png", ".jpg", ".jpeg", ".heic")):
                    source_name = tail
            records.append(
                {
                    "calories": float(rowd["calories"]),
                    "protein_g": _float_or_none(rowd.get("protein_g")),
                    "carbs_g": _float_or_none(rowd.get("carbs_g")),
                    "fat_g": _float_or_none(rowd.get("fat_g")),
                    "fiber_g": _float_or_none(_fatsecret_parsed_from_daily_row(rowd).get("fiber_g")),
                    "sodium_mg": _float_or_none(_fatsecret_parsed_from_daily_row(rowd).get("sodium_mg")),
                    "ts": f"{log_day.isoformat()}T00:00:00",
                    "origin": "daily_log",
                    "source_path": source_name,
                    "stored_path": None,
                    "queue_id": None,
                    "file_hash": None,
                    "status": "daily_log",
                    "parsed": _fatsecret_parsed_from_daily_row(rowd),
                    "priority": 2,
                    "ocr_text": "",
                }
            )

    records.sort(key=lambda r: (r.get("priority", 0), str(r.get("ts") or "")), reverse=True)
    return records


def _fatsecret_records_match(a, b):
    if not a or not b:
        return False
    if a.get("queue_id") and b.get("queue_id"):
        return int(a["queue_id"]) == int(b["queue_id"])
    return (
        a.get("origin") == b.get("origin")
        and str(a.get("ts") or "") == str(b.get("ts") or "")
        and float(a.get("calories") or 0) == float(b.get("calories") or 0)
    )


def save_fatsecret_intake_edits(log_day, parsed, record):
    """Persist corrected FatSecret values to OCR queue and daily_log."""
    log_day_str = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)
    clean = {"log_date": log_day_str}
    for key, _, _ in FATSECRET_DISPLAY_FIELDS:
        val = parsed.get(key)
        if val is not None:
            clean[key] = float(val)
    if not clean.get("calories"):
        return {"synced": 0, "error": "Calories required"}

    stored_path = record.get("stored_path")
    queue_id = record.get("queue_id")
    if queue_id is not None:
        qdf = load_ocr_queue()
        match = qdf[qdf["id"] == int(queue_id)]
        if not match.empty:
            qr = match.iloc[0]
            status = str(qr.get("status") or "imported")
            if status not in OCR_TERMINAL_STATUSES:
                status = "imported"
            upsert_ocr_queue(
                qr.get("file_hash"),
                qr.get("stored_path"),
                "FatSecret",
                qr.get("ocr_text") or "",
                clean,
                status=status,
                notes=f"Corrected in Daily Sync · {datetime.now().isoformat(timespec='seconds')}",
                preserve_terminal_status=True,
            )
            stored_path = stored_path or qr.get("stored_path")

    upsert_fatsecret_from_screenshot(clean, log_day, source_path=stored_path)
    return sync_imported_ocr_to_daily_log(reparse_missing=False)


def fatsecret_validator_css():
    return """
<style>
  .fs-val-card {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui, sans-serif;
    background: #ffffff;
    border: 1px solid #e5e5ea;
    border-radius: 14px;
    padding: 10px 12px;
    margin: 6px 0 10px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }
  .fs-val-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f2f2f7;
  }
  .fs-val-title {
    font-size: 11px;
    font-weight: 700;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: .06em;
  }
  .fs-val-ts {
    font-size: 11px;
    font-weight: 600;
    color: #636366;
    white-space: nowrap;
  }
  .fs-val-active {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    color: #248a3d;
    background: #e8f7ec;
    padding: 3px 8px;
    border-radius: 999px;
    margin-bottom: 8px;
  }
  .fs-val-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid #f2f2f7;
    line-height: 1.2;
  }
  .fs-val-row:last-child { border-bottom: none; padding-bottom: 0; }
  .fs-val-row.fs-val-highlight {
    background: #f2f2f7;
    margin: 0 -12px;
    padding: 10px 12px;
    border-bottom: none;
    border-radius: 10px;
  }
  .fs-val-label {
    font-size: 13px;
    font-weight: 600;
    color: #636366;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .fs-val-value {
    font-size: 17px;
    font-weight: 700;
    color: #1c1c1e;
    letter-spacing: -.02em;
    text-align: right;
    white-space: nowrap;
  }
  .fs-val-unit {
    font-size: 12px;
    font-weight: 600;
    color: #8e8e93;
    margin-left: 3px;
  }
  .fs-val-empty { color: #c7c7cc; font-weight: 600; }
</style>
"""


def _format_fatsecret_display_value(field_key, val):
    if val is None:
        return None
    v = float(val)
    if field_key == "calories":
        return f"{v:,.0f}"
    if field_key == "sodium_mg":
        return f"{v:,.0f}"
    disp = f"{v:.2f}".rstrip("0").rstrip(".")
    return disp


def fatsecret_capture_card_html(parsed, uploaded_ts, is_active=False):
    rows = []
    for field_key, label, unit in FATSECRET_DISPLAY_FIELDS:
        val = parsed.get(field_key)
        disp = _format_fatsecret_display_value(field_key, val)
        highlight = " fs-val-highlight" if field_key == "calories" else ""
        if disp is None:
            value_html = '<span class="fs-val-empty">—</span>'
        else:
            value_html = f'<span class="fs-val-value">{disp}<span class="fs-val-unit">{unit}</span></span>'
        rows.append(
            f'<div class="fs-val-row{highlight}">'
            f'<span class="fs-val-label">{label}</span>{value_html}</div>'
        )
    active_badge = '<div class="fs-val-active">Active for Daily Sync</div>' if is_active else ""
    return fatsecret_validator_css() + f"""
<div class="fs-val-card">
  <div class="fs-val-head">
    <span class="fs-val-title">Captured intake</span>
    <span class="fs-val-ts">{uploaded_ts}</span>
  </div>
  {active_badge}
  {"".join(rows)}
</div>
"""


def default_daily_intake_values(settings=None):
    """Usual daily calories/protein/carbs — meal template or saved default."""
    template = load_daily_meal_template()
    totals = resolve_meal_template_totals(template)
    raw_cal = get_text_setting("default_daily_calories", "")
    raw_prot = get_text_setting("default_daily_protein_g", "")
    raw_carbs = get_text_setting("default_daily_carbs_g", "")
    try:
        cal = float(raw_cal) if raw_cal else float(totals.get("calories") or 2720)
    except ValueError:
        cal = 2720.0
    try:
        prot = float(raw_prot) if raw_prot else float(totals.get("protein_g") or 190)
    except ValueError:
        prot = 190.0
    try:
        carbs = float(raw_carbs) if raw_carbs else float(totals.get("carbs_g") or 320)
    except ValueError:
        carbs = 320.0
    return {"calories": cal, "protein_g": prot, "carbs_g": carbs}


def logged_intake_for_day(daily, log_day):
    if daily.empty:
        return None
    rows = daily[daily["log_date"].dt.date == log_day]
    for _, row in rows.iterrows():
        rd = row.to_dict()
        if is_fatsecret_intake_row(rd) or (rd.get("calories") and float(rd["calories"]) > 0):
            return {
                "calories": float(rd.get("calories") or 0),
                "protein_g": float(rd.get("protein_g") or 0),
                "carbs_g": _float_or_none(rd.get("carbs_g")),
            }
    return None


def save_simple_daily_intake(log_day, calories, protein_g, carbs_g=None, save_as_default=False):
    notes = tag_import_notes("FatSecret", "Daily intake (manual)")
    upsert_daily(
        {
            "log_date": log_day.isoformat(),
            "calories": float(calories),
            "protein_g": float(protein_g),
            "carbs_g": float(carbs_g) if carbs_g is not None else None,
            "notes": notes,
        },
        source="FatSecret",
        force=True,
        data_ts=pd.Timestamp.now(),
    )
    if save_as_default:
        save_text_setting("default_daily_calories", str(float(calories)))
        save_text_setting("default_daily_protein_g", str(float(protein_g)))
        if carbs_g is not None:
            save_text_setting("default_daily_carbs_g", str(float(carbs_g)))


def render_simple_daily_intake(daily, log_day, settings, key_prefix="ds_intake"):
    """Prefilled calories/protein/carbs — edit and save; no OCR required."""
    logged = logged_intake_for_day(daily, log_day)
    defaults = default_daily_intake_values(settings)
    cal_default = logged["calories"] if logged else defaults["calories"]
    prot_default = logged["protein_g"] if logged else defaults["protein_g"]
    if logged and logged.get("carbs_g") is not None:
        carb_default = float(logged["carbs_g"])
    else:
        carb_default = defaults["carbs_g"]

    st.markdown("**Daily intake**")
    c1, c2, c3 = st.columns(3)
    cal = c1.number_input(
        "Calories",
        min_value=0.0,
        value=float(cal_default),
        step=50.0,
        key=f"{key_prefix}_cal",
    )
    prot = c2.number_input(
        "Protein (g)",
        min_value=0.0,
        value=float(prot_default),
        step=5.0,
        key=f"{key_prefix}_prot",
    )
    carbs = c3.number_input(
        "Carbs (g)",
        min_value=0.0,
        value=float(carb_default),
        step=5.0,
        key=f"{key_prefix}_carbs",
    )
    save_default = st.checkbox(
        "Use as default prefill",
        value=False,
        key=f"{key_prefix}_save_def",
        help="Tomorrow and future days start with these numbers.",
    )
    if st.button("Save intake", key=f"{key_prefix}_save", use_container_width=True, type="primary"):
        save_simple_daily_intake(log_day, cal, prot, carbs_g=carbs, save_as_default=save_default)
        st.rerun()
    if logged:
        st.caption(f"Saved for **{log_day.isoformat()}** — change values and save again to override.")
    else:
        st.caption("Prefilled from your usual day. Edit if today is different, then save.")
    return {
        "calories": float(cal),
        "protein_g": float(prot),
        "carbs_g": float(carbs),
        "saved": logged is not None,
    }


def render_dexa_milestone_entry(dexa, settings, fc, daily):
    """Manual DEXA entry — first scan = journey start, later scans = road milestones."""
    st.markdown("**DEXA milestone**")
    st.caption("First entry sets **Start** on the journey. Later entries show as milestones on the road.")
    scan_count = 0 if dexa is None or dexa.empty else len(dexa)
    if scan_count == 0:
        st.info("No scans yet — your first entry becomes the journey start.")

    bf_default = float(settings.get("current_body_fat_pct") or 15.0)
    weight_default = float(settings.get("current_weight_lbs") or 176.0)
    if dexa is not None and not dexa.empty:
        last = dexa.sort_values("scan_date").iloc[-1]
        bf_default = float(last["body_fat_pct"])
        weight_default = float(last["weight_lbs"])

    d1, d2, d3 = st.columns([1.2, 1, 1])
    scan_date = d1.date_input("Scan date", value=date.today(), key="dexa_milestone_date")
    bf = d2.number_input(
        "Body fat %",
        min_value=3.0,
        max_value=50.0,
        value=bf_default,
        step=0.1,
        key="dexa_milestone_bf",
    )
    weight = d3.number_input(
        "Weight (lb)",
        min_value=80.0,
        max_value=400.0,
        value=weight_default,
        step=0.5,
        key="dexa_milestone_weight",
    )

    if st.button("Post to journey", type="primary", key="dexa_milestone_save", use_container_width=True):
        fat_mass = weight * bf / 100.0
        lean_mass = weight - fat_mass
        row = (
            scan_date.isoformat(),
            float(weight),
            float(bf),
            float(fat_mass),
            float(lean_mass),
            None,
            None,
            None,
            None,
            "Manual DEXA milestone",
        )
        is_first = scan_count == 0
        summary = apply_dexa_scan_record(
            row, daily=daily, settings=settings, reseed_journey=is_first
        )
        if summary.get("ok"):
            if is_first:
                st.success(f"Journey **start** set — {bf:.1f}% BF on {scan_date.isoformat()}.")
            else:
                st.success(f"Milestone posted — {bf:.1f}% BF on {scan_date.isoformat()}.")
        else:
            st.error(summary.get("message") or "Could not save scan.")
        st.rerun()

    if dexa is not None and not dexa.empty:
        hist = dexa.sort_values("scan_date")[["scan_date", "body_fat_pct", "weight_lbs"]].tail(5).copy()
        hist["scan_date"] = hist["scan_date"].astype(str).str[:10]
        hist.columns = ["Date", "BF %", "Weight (lb)"]
        st.caption("Recent scans")
        st.dataframe(hist, use_container_width=True, hide_index=True)


def render_fatsecret_intake_validator(daily, log_day, key_prefix="ds_fs"):
    """Expandable FatSecret capture review — Apple Health-style rows, editable values."""
    active = get_fatsecret_day_data(daily, log_day)
    records = collect_fatsecret_records_for_day(daily, log_day)

    with st.expander("FatSecret intake — validate & edit", expanded=False):
        if not records:
            st.caption("No FatSecret upload captured for this date yet.")
            st.caption("Drop a FatSecret screenshot in TU Inbox, then scan from Auto Inbox.")
            return

        def _record_label(idx):
            rec = records[idx]
            ts = format_fatsecret_upload_ts(rec.get("ts"))
            src = rec.get("source_path") or ("daily log" if rec.get("origin") == "daily_log" else "screenshot")
            active_tag = " · active" if active and _fatsecret_records_match(rec, active) else ""
            return f"{ts} — {src}{active_tag}"

        pick = 0
        if len(records) > 1:
            pick = st.selectbox(
                "Upload history",
                range(len(records)),
                format_func=_record_label,
                key=f"{key_prefix}_record_pick",
            )
        rec = records[pick]
        parsed = dict(rec.get("parsed") or {})
        is_active = bool(active and _fatsecret_records_match(rec, active))

        st.markdown(
            fatsecret_capture_card_html(parsed, format_fatsecret_upload_ts(rec.get("ts")), is_active),
            unsafe_allow_html=True,
        )

        src_name = rec.get("source_path") or rec.get("origin") or "unknown"
        st.caption(f"File: **{src_name}** · Status: **{rec.get('status') or '—'}**")
        if not is_active and active:
            st.caption("Another upload is active for fuel math. Save here if this summary is correct.")

        stored = rec.get("stored_path")
        if stored:
            preview = image_display_path(stored)
            if preview.exists() and preview.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".heic"}:
                with st.expander("Screenshot reference", expanded=False):
                    st.image(str(preview), use_container_width=True)

        with st.expander("Edit values", expanded=False):
            edited = {}
            for field_key, label, unit in FATSECRET_DISPLAY_FIELDS:
                default = float(parsed[field_key]) if parsed.get(field_key) is not None else 0.0
                step = 1.0 if field_key == "calories" else (10.0 if field_key == "sodium_mg" else 0.1)
                min_val = 0.0 if field_key != "calories" else 400.0
                edited[field_key] = st.number_input(
                    f"{label} ({unit})",
                    min_value=min_val,
                    value=max(min_val, default),
                    step=step,
                    key=f"{key_prefix}_edit_{field_key}_{pick}",
                )

            save_col, reparse_col = st.columns(2)
            if save_col.button("Save corrections", key=f"{key_prefix}_save_{pick}", use_container_width=True):
                sync_result = save_fatsecret_intake_edits(log_day, edited, rec)
                st.session_state.ocr_daily_sync_summary = sync_result
                st.success("Saved.")
                st.rerun()
            if reparse_col.button("Re-parse OCR", key=f"{key_prefix}_reparse_{pick}", use_container_width=True):
                if rec.get("ocr_text"):
                    fresh = parse_fatsecret_ocr(rec.get("ocr_text"), apply_learning=True)
                    sync_result = save_fatsecret_intake_edits(log_day, fresh, rec)
                    st.session_state.ocr_daily_sync_summary = sync_result
                    st.success("Re-parsed and saved.")
                    st.rerun()
                else:
                    st.warning("No OCR text stored for this record.")


def get_fatsecret_day_data(daily, log_day):
    """Latest FatSecret intake for an exact date — imported OCR wins over daily_log."""
    records = collect_fatsecret_records_for_day(daily, log_day)
    fuel_records = [
        r
        for r in records
        if r.get("calories") is not None
        and (
            (
                r.get("origin") == "daily_log"
                and float(r["calories"]) >= 0
            )
            or (
                float(r["calories"]) > 0
                and str(r.get("status") or "") in OCR_TERMINAL_STATUSES
            )
        )
    ]
    if not fuel_records:
        return None
    winner = max(fuel_records, key=lambda r: (r.get("priority", 0), str(r.get("ts") or "")))
    return {
        "calories": float(winner["calories"]),
        "protein_g": winner.get("protein_g"),
        "carbs_g": winner.get("carbs_g"),
        "fat_g": winner.get("fat_g"),
        "fiber_g": winner.get("fiber_g"),
        "sodium_mg": winner.get("sodium_mg"),
        "ts": winner.get("ts"),
        "origin": winner.get("origin"),
        "source_path": winner.get("source_path"),
        "queue_id": winner.get("queue_id"),
        "parsed": winner.get("parsed"),
        "status": winner.get("status"),
    }


def get_fatsecret_intake(daily, log_day):
    data = get_fatsecret_day_data(daily, log_day)
    return data["calories"] if data else None


def latest_apple_health_weight(daily):
    if daily.empty:
        return None
    df = daily[daily["weight_lbs"].notna()].copy()
    if df.empty:
        return None
    mask = df["notes"].fillna("").str.lower().str.contains(r"\[apple health weight\]|apple health", regex=True)
    ah = df[mask]
    if ah.empty:
        return None
    ah = ah.sort_values("log_date")
    return float(ah.iloc[-1]["weight_lbs"])


def collect_imported_weight_candidates(daily, dexa):
    candidates = []

    c = conn()
    try:
        wm = pd.read_sql(
            "SELECT measured_at, weight_lbs, source FROM weight_measurements ORDER BY measured_at DESC",
            c,
        )
    except Exception:
        wm = pd.DataFrame()
    c.close()
    if not wm.empty:
        for _, row in wm.iterrows():
            try:
                weight = float(row["weight_lbs"])
            except (TypeError, ValueError):
                continue
            if not live_weight_sane(weight):
                continue
            candidates.append(
                {
                    "weight": weight,
                    "source": f"{row.get('source') or 'Weight measurement'}",
                    "priority": 2,
                    "ts": str(row["measured_at"]),
                }
            )

    queue = load_ocr_queue()
    if not queue.empty:
        for _, row in queue.iterrows():
            dtype = row.get("detected_type")
            if dtype not in ("Scale", "Apple Health Weight"):
                continue
            parsed = json.loads(row.get("parsed_json") or "{}")
            weight = parsed.get("weight_lbs")
            if weight is None or not live_weight_sane(weight):
                continue
            ts = str(row.get("created_at") or "")
            if dtype == "Scale" and row.get("status") == "imported":
                candidates.append({"weight": float(weight), "source": "Scale OCR (confirmed)", "priority": 1, "ts": ts})
            elif dtype == "Scale":
                candidates.append({"weight": float(weight), "source": "Scale OCR", "priority": 1, "ts": ts})
            else:
                candidates.append({"weight": float(weight), "source": "Apple Health Weight OCR", "priority": 2, "ts": ts})

    if not daily.empty:
        df = daily[daily["weight_lbs"].notna()].copy()
        for _, row in df.iterrows():
            notes = str(row.get("notes") or "").lower()
            ts = str(row.get("log_date") or "")
            try:
                weight = float(row["weight_lbs"])
            except (TypeError, ValueError):
                continue
            if not live_weight_sane(weight):
                continue
            if "[scale]" in notes or "scale screenshot" in notes:
                candidates.append({"weight": weight, "source": "Scale import", "priority": 1, "ts": ts})
            elif "[apple health weight]" in notes or "apple health" in notes:
                candidates.append({"weight": weight, "source": "Apple Health Weight import", "priority": 2, "ts": ts})
            elif "apple health xml" in notes:
                candidates.append({"weight": weight, "source": "Apple Health XML", "priority": 3, "ts": ts})
            else:
                candidates.append({"weight": weight, "source": "Daily log", "priority": 3, "ts": ts})

    if dexa is not None and not dexa.empty:
        dexa_sorted = dexa.sort_values("scan_date")
        latest = dexa_sorted.iloc[-1]
        candidates.append(
            {
                "weight": float(latest["weight_lbs"]),
                "source": "DEXA",
                "priority": 4,
                "ts": str(latest["scan_date"]),
            }
        )

    return candidates


def best_imported_weight_candidate(daily, dexa):
    candidates = collect_imported_weight_candidates(daily, dexa)
    if not candidates:
        return None

    def rank(c):
        try:
            priority = int(c.get("priority") or 99)
        except (TypeError, ValueError):
            priority = 99
        return (parse_import_ts(c.get("ts")), -priority)

    live = [
        c
        for c in candidates
        if int(c.get("priority") or 99) <= 3 and live_weight_sane(c.get("weight"))
    ]
    dexa_group = [c for c in candidates if int(c.get("priority") or 99) == 4]
    if live:
        best_live = max(live, key=rank)
        if dexa_group:
            best_dexa = max(dexa_group, key=rank)
            if parse_import_ts(best_dexa.get("ts")) > parse_import_ts(best_live.get("ts")):
                return best_dexa
        return best_live
    if dexa_group:
        return max(dexa_group, key=rank)
    return None


def latest_imported_weight(daily, dexa):
    candidate = best_imported_weight_candidate(daily, dexa)
    if not candidate:
        return None, None
    return candidate["weight"], candidate["source"]


def latest_trusted_dexa_body_fat(dexa):
    if dexa is None or dexa.empty:
        return None, None
    latest = dexa.sort_values("scan_date").iloc[-1]
    bf = latest.get("body_fat_pct")
    if bf is None or (isinstance(bf, float) and pd.isna(bf)):
        return None, None
    scan_date = latest.get("scan_date")
    if hasattr(scan_date, "date"):
        scan_date = scan_date.date().isoformat()
    elif hasattr(scan_date, "isoformat"):
        scan_date = scan_date.isoformat()
    else:
        scan_date = str(scan_date)
    return float(bf), scan_date


def apply_startup_import_overrides(settings_dict, daily, dexa):
    """Load saved settings first; override only import-owned fields when newer/higher-priority."""
    s = dict(settings_dict)
    sources = {}

    if get_text_setting("current_weight_manual_override") != "1":
        candidate = best_imported_weight_candidate(daily, dexa)
        if candidate:
            save_weight_from_import(
                candidate["weight"],
                candidate["source"],
                candidate["priority"],
                candidate["ts"],
                clear_manual=False,
            )
            s["current_weight_lbs"] = float(candidate["weight"])
            sources["current_weight_lbs"] = candidate["source"]
        else:
            sources["current_weight_lbs"] = setting_field_source("current_weight_lbs")
    else:
        sources["current_weight_lbs"] = "Manual Override"

    if get_text_setting("current_body_fat_manual_override") != "1":
        bf, scan_date = latest_trusted_dexa_body_fat(dexa)
        if bf is not None:
            saved_ts = get_text_setting("current_body_fat_import_ts")
            if import_beats_saved(4, scan_date, 4, saved_ts):
                save_body_fat_from_dexa(bf, scan_date, clear_manual=False)
                s["current_body_fat_pct"] = float(bf)
                sources["current_body_fat_pct"] = "DEXA"
            else:
                sources["current_body_fat_pct"] = setting_field_source("current_body_fat_pct")
        else:
            sources["current_body_fat_pct"] = setting_field_source("current_body_fat_pct")
    else:
        s = ensure_manual_body_fat_restored(s)
        sources["current_body_fat_pct"] = "Manual Override"

    return s, sources


def sync_current_weight_from_imports(daily, dexa, settings):
    return apply_startup_import_overrides(settings, daily, dexa)


def sync_current_weight_from_apple_health(daily, settings):
    settings_dict, _sources = apply_startup_import_overrides(settings, daily, load_dexa())
    return settings_dict


def get_fatsecret_plan_text(daily, log_day):
    """Collect FatSecret OCR / diary text for an exact date."""
    texts = []
    queue = load_ocr_queue()
    if not queue.empty:
        for _, qr in queue.iterrows():
            if qr.get("detected_type") != "FatSecret":
                continue
            if parse_inbox_image_date(qr.get("stored_path") or "") != log_day:
                continue
            chunk = str(qr.get("ocr_text") or "").strip()
            if chunk:
                texts.append(chunk)
    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            if is_fatsecret_intake_row(row.to_dict()):
                notes = str(row.get("notes") or "").strip()
                if notes and notes.lower() not in {t.lower() for t in texts}:
                    texts.append(notes)
    return "\n".join(texts)


def parse_planned_snack_foods(text):
    """Detect snack items already on the FatSecret daily plan from diary text."""
    result = {
        "krispies_g": 0.0,
        "milk_g": 0.0,
        "has_peach": False,
        "has_nectarine": False,
        "cookie_count": 0,
    }
    if not text or not str(text).strip():
        return result

    lower = str(text).lower()
    for m in re.finditer(r"rice\s*krisp(?:ies|y)?[^0-9\n]{0,32}(\d+(?:\.\d+)?)\s*g", lower):
        result["krispies_g"] += float(m.group(1))
    for m in re.finditer(r"rice\s*crisps?(?:\s*cereal)?[^0-9\n]{0,32}(\d+(?:\.\d+)?)\s*g", lower):
        result["krispies_g"] += float(m.group(1))

    for m in re.finditer(r"(?<![a-z])(?:whole\s+|skim\s+|2\s*%?\s*)?milk(?!\s*chocolate)[^0-9\n]{0,32}(\d+(?:\.\d+)?)\s*g", lower):
        result["milk_g"] += float(m.group(1))

    result["has_peach"] = bool(re.search(r"(?<![a-z])peach(?:es)?(?![a-z])", lower)) and "peach yogurt" not in lower
    result["has_nectarine"] = bool(re.search(r"(?<![a-z])nectarine(?![a-z])", lower))
    result["cookie_count"] = len(re.findall(r"(?<![a-z])cookies?(?![a-z])", lower))
    return result


def detect_fatsecret_planned_snacks(daily, log_day, meal_item_amounts=None):
    text_result = parse_planned_snack_foods(get_fatsecret_plan_text(daily, log_day))
    template = load_daily_meal_template()
    amounts = meal_item_amounts or load_meal_item_amounts(daily, log_day, template)

    notes_text = ""
    if not daily.empty:
        rows = daily[daily["log_date"].dt.date == log_day]
        for _, row in rows.iterrows():
            if is_fatsecret_intake_row(row.to_dict()):
                notes_text = str(row.get("notes") or "")
                break

    use_items = (
        meal_item_amounts is not None
        or _meal_items_from_notes(notes_text)
        or get_fatsecret_day_data(daily, log_day) is not None
    )
    if use_items:
        item_result = planned_snacks_from_meal_items(amounts)
        return {**text_result, **item_result}
    return text_result


def build_increase_food_plan(kcal_needed, planned_foods=None):
    """Incremental snack adds beyond what is already on today's FatSecret plan."""
    remaining = max(0.0, float(kcal_needed))
    steps = []
    planned = planned_foods or {}
    prior_slots = []

    for _ in range(8):
        if remaining <= 5:
            break
        snack_id = recommend_next_snack(remaining, planned, prior_slots)
        portion = default_snack_portion(snack_id, remaining, prior_slots)
        if portion <= 0:
            break
        line = format_snack_portion_line(snack_id, portion)
        if not line or line == "—":
            break
        steps.append(f"Add {line}")
        kcal = snack_portion_kcal(snack_id, portion)
        prior_slots.append({"snack_id": snack_id, "portion": portion, "kcal": kcal})
        remaining -= kcal

    return steps


def build_reduction_food_plan(kcal_to_cut, planned_foods=None):
    """Suggest removing planned snacks to lower intake toward target deficit."""
    remaining = max(0.0, float(kcal_to_cut))
    if remaining <= 5:
        return []

    planned = planned_foods or {}
    steps = []
    krispies_left = float(planned.get("krispies_g") or 0)

    def try_remove(snack_id, portion):
        nonlocal remaining, krispies_left
        if remaining <= 5 or portion <= 0:
            return False
        kcal = snack_portion_kcal(snack_id, portion)
        if kcal <= 0:
            return False
        line = format_snack_portion_line(snack_id, portion)
        if not line or line == "—":
            return False
        steps.append(f"Remove {line} (~{kcal:.0f} kcal)")
        remaining -= kcal
        if snack_id == "krispies_milk":
            krispies_left = max(0.0, krispies_left - float(portion))
        return True

    cookie_count = int(planned.get("cookie_count") or 0)
    for _ in range(cookie_count):
        if remaining <= 5:
            break
        try_remove("cookie", 1)

    if remaining > 5 and planned.get("has_peach"):
        try_remove("peach", 1)
    if remaining > 5 and planned.get("has_nectarine"):
        try_remove("nectarine", 1)

    while remaining > 5 and krispies_left >= 5:
        rate = _krispies_milk_rate_per_g()
        grams = min(krispies_left, max(5.0, round(remaining / rate / 5.0) * 5.0))
        if not try_remove("krispies_milk", grams):
            break

    if remaining > 25:
        if steps:
            steps.append(f"Still ~{remaining:.0f} kcal over — trim main meals if needed")
        else:
            steps.append(f"Trim ~{remaining:.0f} kcal from meals or optional snacks")

    return steps[:6]


def _gap_krispies_total_cap_g():
    return float(FUEL_FOOD_CALORIES["krispies"]["max_g"])


def _gap_krispies_cap_left(prior_slots):
    prior_slots = prior_slots or []
    return max(0.0, _gap_krispies_total_cap_g() - _krispies_grams_in_slots(prior_slots))


def _gap_krispies_add_g(kcal_needed, prior_slots=None):
    """Rice Krispies grams sized to close kcal_needed, capped by the daily krispies limit."""
    rate = _krispies_milk_rate_per_g()
    ideal_g = max(5.0, float(kcal_needed)) / rate
    rounded = max(15.0, round(ideal_g / 5.0) * 5.0)
    cap_left = _gap_krispies_cap_left(prior_slots)
    if cap_left < 5:
        return 0.0
    return min(cap_left, rounded)


def _krispies_milk_kcal(krispies_g):
    milk_g = float(krispies_g) * MILK_TO_KRISPIES_RATIO
    k_cfg = FUEL_FOOD_CALORIES["krispies"]
    m_cfg = FUEL_FOOD_CALORIES["milk"]
    return krispies_g * k_cfg["kcal_per_g"] + milk_g * m_cfg["kcal_per_g"]


def _krispies_milk_rate_per_g():
    k_cfg = FUEL_FOOD_CALORIES["krispies"]
    m_cfg = FUEL_FOOD_CALORIES["milk"]
    return k_cfg["kcal_per_g"] + MILK_TO_KRISPIES_RATIO * m_cfg["kcal_per_g"]


def _toast_butter_serving_kcal():
    b = FUEL_FOOD_CALORIES["butter"]
    return float(FUEL_FOOD_CALORIES["toast"]["kcal_each"]) + float(b["serving_g"]) * b["kcal_per_g"]


def snack_portion_kcal(snack_id, portion):
    portion = float(portion or 0)
    if portion <= 0:
        return 0.0
    if snack_id == "krispies_milk":
        return _krispies_milk_kcal(portion)
    if snack_id == "toast_butter":
        return portion * _toast_butter_serving_kcal()
    if snack_id in ("peach", "nectarine", "cookie"):
        return portion * float(FUEL_FOOD_CALORIES[snack_id]["kcal_each"])
    return 0.0


def _krispies_grams_in_slots(prior_slots):
    return sum(float(slot.get("portion") or 0) for slot in prior_slots if slot.get("snack_id") == "krispies_milk")


def _gap_fruit_pieces_used(prior_slots):
    total = 0
    for slot in prior_slots or []:
        if slot.get("snack_id") in ("peach", "nectarine"):
            total += int(float(slot.get("portion") or 0))
    return total


def _gap_fruit_portion_cap(prior_slots):
    return max(0, GAP_MAX_FRUIT_PIECES - _gap_fruit_pieces_used(prior_slots))


def _gap_cookies_used(prior_slots):
    total = 0
    for slot in prior_slots or []:
        if slot.get("snack_id") == "cookie":
            total += int(float(slot.get("portion") or 0))
    return total


def _gap_cookie_portion_cap(prior_slots):
    return max(0, 3 - _gap_cookies_used(prior_slots))


def default_snack_portion(snack_id, kcal_needed, prior_slots=None):
    """Default portion for one slot — sized to close kcal_needed when possible."""
    prior_slots = prior_slots or []
    kcal_needed = max(0.0, float(kcal_needed))
    if snack_id == "krispies_milk":
        cap_left = _gap_krispies_cap_left(prior_slots)
        if cap_left < 5:
            return 0.0
        ideal_g = _gap_krispies_add_g(kcal_needed, prior_slots)
        return min(ideal_g, cap_left)
    if snack_id == "toast_butter":
        serving_kcal = _toast_butter_serving_kcal()
        return max(1, int(round(kcal_needed / serving_kcal))) if kcal_needed > 0 else 1
    if snack_id in ("peach", "nectarine"):
        unit_kcal = float(FUEL_FOOD_CALORIES[snack_id]["kcal_each"])
        ideal = max(1, int(round(kcal_needed / unit_kcal))) if kcal_needed > 0 else 1
        budget = _gap_fruit_portion_cap(prior_slots)
        if budget <= 0:
            return 0
        return min(ideal, budget)
    if snack_id == "cookie":
        unit_kcal = float(FUEL_FOOD_CALORIES["cookie"]["kcal_each"])
        ideal = max(1, int(round(kcal_needed / unit_kcal))) if kcal_needed > 0 else 1
        budget = _gap_cookie_portion_cap(prior_slots)
        if budget <= 0:
            return 0
        return min(ideal, budget)
    return 1


def gap_portion_field_spec(snack_id):
    """Independent portion limits for the optional gap planner."""
    if snack_id == "krispies_milk":
        return "Rice Krispies (g)", 0.0, _gap_krispies_total_cap_g(), 5.0
    if snack_id == "toast_butter":
        return "Slices", 0, 8, 1
    if snack_id in ("peach", "nectarine"):
        return "Count", 0, 5, 1
    if snack_id == "cookie":
        return "Count", 0, 6, 1
    return "Amount", 0.0, 500.0, 1.0


def gap_snack_rate_hint(snack_id):
    if snack_id == "krispies_milk":
        return f"~{_krispies_milk_rate_per_g():.1f} kcal/g krispies (+ milk)"
    if snack_id == "toast_butter":
        return f"~{_toast_butter_serving_kcal():.0f} kcal/slice"
    if snack_id in ("peach", "nectarine", "cookie"):
        return f"~{float(FUEL_FOOD_CALORIES[snack_id]['kcal_each']):.0f} kcal each"
    return ""


def portion_field_spec(snack_id, prior_slots=None):
    prior_slots = prior_slots or []
    if snack_id == "krispies_milk":
        cap_left = _gap_krispies_cap_left(prior_slots)
        return "Rice Krispies (g)", 0.0, cap_left, 5.0
    if snack_id == "toast_butter":
        return "Toast slices", 0, 6, 1
    if snack_id in ("peach", "nectarine"):
        fruit_cap = _gap_fruit_portion_cap(prior_slots)
        return "Count", 0, fruit_cap, 1
    if snack_id == "cookie":
        cookie_cap = _gap_cookie_portion_cap(prior_slots)
        return "Count", 0, cookie_cap, 1
    return "Amount", 0.0, 500.0, 1.0


def format_snack_portion_line(snack_id, portion):
    portion = float(portion or 0)
    if portion <= 0:
        return "—"
    if snack_id == "krispies_milk":
        milk_g = portion * MILK_TO_KRISPIES_RATIO
        carb_est = portion * KRISPIES_CARB_FRACTION
        return f"{portion:.0f}g Rice Krispies + {milk_g:.0f}g milk (~{carb_est:.0f}g carbs)"
    if snack_id == "toast_butter":
        b = FUEL_FOOD_CALORIES["butter"]
        butter_g = portion * float(b["serving_g"])
        noun = "slice" if int(portion) == 1 else "slices"
        return f"{int(portion)} toast {noun} + {butter_g:.0f}g butter"
    if snack_id in ("peach", "nectarine", "cookie"):
        label = FUEL_FOOD_CALORIES[snack_id]["label"].lower()
        count = int(portion)
        suffix = "" if count == 1 else "s"
        return f"{count} {label}{suffix}"
    return ""


def recommend_next_snack(remaining, planned, prior_slots):
    """Pick the next frequent snack to stack toward closing the gap."""
    remaining = max(0.0, float(remaining))
    planned = planned or {}
    prior_slots = prior_slots or []

    fruit_used = _gap_fruit_pieces_used(prior_slots)
    fruit_left = GAP_MAX_FRUIT_PIECES - fruit_used
    krispies_used = _krispies_grams_in_slots(prior_slots)
    krispies_cap = _gap_krispies_total_cap_g()

    # Rice Krispies first when calories are needed and room remains under the daily cap.
    if remaining > 25 and krispies_used < krispies_cap - 4.5:
        return "krispies_milk"

    peach_kcal = float(FUEL_FOOD_CALORIES["peach"]["kcal_each"])
    nectarine_kcal = float(FUEL_FOOD_CALORIES["nectarine"]["kcal_each"])
    if fruit_left > 0:
        if not planned.get("has_peach") and remaining >= peach_kcal * 0.85:
            return "peach"
        if not planned.get("has_nectarine") and remaining >= nectarine_kcal * 0.85:
            return "nectarine"
        if remaining >= peach_kcal * 0.85:
            return "peach"

    cookie_kcal = float(FUEL_FOOD_CALORIES["cookie"]["kcal_each"])
    cookies_left = _gap_cookie_portion_cap(prior_slots)
    if cookies_left > 0 and remaining >= cookie_kcal * 0.85:
        return "cookie"

    toast_kcal = _toast_butter_serving_kcal()
    if remaining >= toast_kcal * 0.85:
        return "toast_butter"

    return "cookie"


def compute_snack_suggestion(snack_id, kcal_needed, planned_foods=None):
    """Extra intake to add on top of today's logged FatSecret plan."""
    planned = planned_foods or {}
    kcal_needed = max(5.0, float(kcal_needed))
    portion = default_snack_portion(snack_id, kcal_needed)
    total_kcal = snack_portion_kcal(snack_id, portion)
    summary = format_snack_portion_line(snack_id, portion)
    detail_lines = [f"Extra needed to close gap: {kcal_needed:.0f} kcal"]
    if snack_id == "krispies_milk":
        uncapped_g = max(15.0, round((kcal_needed / _krispies_milk_rate_per_g()) / 5.0) * 5.0)
        logged = ""
        if float(planned.get("krispies_g") or 0) > 0:
            logged = f" (you already logged {planned['krispies_g']:.0f}g krispies today)"
        detail_lines.append(logged.strip())
        detail_lines.append(
            f"Milk is {MILK_TO_KRISPIES_RATIO:.1f}× the Rice Krispies grams."
        )
        krispies_cap = _gap_krispies_total_cap_g()
        detail_lines.append(
            f"Max **{krispies_cap:.0f}g** Rice Krispies total in close-the-gap (across all snack rows)."
        )
        if uncapped_g > krispies_cap + 0.5:
            detail_lines.append("Use additional snacks below to finish closing the gap.")
    if snack_id == "toast_butter":
        b = FUEL_FOOD_CALORIES["butter"]
        detail_lines.append(
            f"Per slice: 1 toast + {b['serving_g']:.0f}g butter (~{_toast_butter_serving_kcal():.0f} kcal)"
        )
    if snack_id in ("peach", "nectarine", "cookie"):
        unit_kcal = float(FUEL_FOOD_CALORIES[snack_id]["kcal_each"])
        detail_lines.append(f"~{unit_kcal:.0f} kcal each")
        if snack_id in ("peach", "nectarine"):
            detail_lines.append(
                f"Max **{GAP_MAX_FRUIT_PIECES}** extra fruit total in close-the-gap (peach + nectarine combined)."
            )
    return {
        "summary": f"Add **{summary}** → **+{total_kcal:.0f} kcal**",
        "detail_lines": [line for line in detail_lines if line],
        "kcal": total_kcal,
        "portion": portion,
    }


def build_daily_fuel_plan(
    s,
    daily,
    fuel_day,
    fuel_workout,
    fuel_steps,
    fuel_observed,
    live_intake=None,
    steps_so_far=None,
    step_goal=None,
    workout_complete=False,
    manual_burn_so_far=None,
    oura_burn_so_far=None,
    day_row=None,
):
    if steps_so_far is not None and step_goal is not None:
        snapshot = compute_daily_burn_snapshot(
            s,
            day_row or {},
            steps_so_far,
            step_goal,
            fuel_workout,
            workout_complete,
            manual_burn_so_far=manual_burn_so_far,
            oura_burn_so_far=oura_burn_so_far,
            workout_burn_override=fuel_observed if fuel_observed > 0 else None,
        )
        plan = fuel_plan_from_burn_snapshot(s, snapshot, fuel_workout)
    else:
        plan = estimate_daily_fuel_target(
            s,
            expected_steps=fuel_steps,
            workout_type=fuel_workout,
            observed_workout_calories=fuel_observed if fuel_observed > 0 else None,
        )
    return enrich_fuel_plan(plan, daily, fuel_day, live_intake=live_intake)


def enrich_fuel_plan(plan, daily, fuel_day, live_intake=None):
    enriched = dict(plan)
    fs = get_fatsecret_day_data(daily, fuel_day)
    if live_intake is not None and float(live_intake.get("calories") or 0) > 0:
        live_fs = {
            "calories": float(live_intake["calories"]),
            "protein_g": _float_or_none(live_intake.get("protein_g")),
            "carbs_g": _float_or_none(live_intake.get("carbs_g")),
            "fat_g": fs.get("fat_g") if fs else None,
            "origin": "live_form",
        }
        fs = live_fs
        enriched["intake_saved"] = bool(live_intake.get("saved"))
    elif fs is None:
        logged = logged_intake_for_day(daily, fuel_day)
        if logged:
            fs = {
                "calories": float(logged["calories"]),
                "protein_g": logged.get("protein_g"),
                "carbs_g": logged.get("carbs_g"),
                "fat_g": None,
                "origin": "daily_log",
            }
    burn = float(plan.get("projected_daily_burn") or plan["total_expenditure"])
    target_deficit = float(plan["target_deficit"])
    protein_target = float(plan["protein_target_g"])
    carb_min = carb_minimum_for_workout(plan.get("workout_type"))
    enriched["carb_minimum_g"] = carb_min
    enriched["carb_day_type"] = plan.get("carb_day_type")

    for key in (
        "burn_so_far",
        "burn_so_far_source",
        "projected_daily_burn",
        "steps_so_far",
        "step_goal",
        "step_progress_pct",
        "step_burn_so_far",
        "workout_complete",
        "workout_burn_so_far",
        "undercount",
        "oura_burn",
    ):
        if key in plan:
            enriched[key] = plan[key]
    enriched["total_expenditure"] = burn

    enriched["fatsecret_data"] = fs
    enriched["has_fatsecret"] = fs is not None
    enriched["fatsecret_calories"] = fs["calories"] if fs else None
    enriched["fatsecret_protein_g"] = fs.get("protein_g") if fs else None
    enriched["fatsecret_carbs_g"] = fs.get("carbs_g") if fs else None
    enriched["fatsecret_fat_g"] = fs.get("fat_g") if fs else None
    enriched["recommended_intake"] = float(plan["recommended_intake"])

    if not fs:
        enriched["projected_deficit"] = None
        enriched["calorie_adjustment"] = None
        enriched["action_label"] = "Log today's intake"
        enriched["adjustment_direction"] = "missing"
        enriched["intake_headline"] = "Intake not saved"
        enriched["intake_subline"] = "Enter calories and protein below, then save."
        enriched["adjustment_kcal"] = None
        enriched["food_plan"] = []
        enriched["protein_planned"] = None
        enriched["protein_gap"] = None
        enriched["carb_gap"] = None
        enriched["intake_saved"] = False
        return apply_fuel_target_status(enriched)

    fs_cal = float(fs["calories"])
    projected_deficit = burn - fs_cal
    calorie_adjustment = projected_deficit - target_deficit

    enriched["projected_deficit"] = projected_deficit
    if enriched.get("burn_so_far") is not None:
        enriched["deficit_so_far"] = float(enriched["burn_so_far"]) - fs_cal
    enriched["calorie_adjustment"] = calorie_adjustment
    enriched["adjustment_kcal"] = abs(calorie_adjustment)

    protein_planned = fs.get("protein_g")
    if protein_planned is not None:
        enriched["protein_planned"] = float(protein_planned)
        enriched["protein_gap"] = protein_target - float(protein_planned)
    else:
        enriched["protein_planned"] = None
        enriched["protein_gap"] = None

    carbs = fs.get("carbs_g")
    if carbs is not None:
        enriched["carb_gap"] = carb_min - float(carbs)
    else:
        enriched["carb_gap"] = None

    planned_snacks = detect_fatsecret_planned_snacks(daily, fuel_day)
    enriched["planned_snacks"] = planned_snacks

    if calorie_adjustment > 5:
        enriched["adjustment_direction"] = "increase"
        enriched["action_label"] = f"{calorie_adjustment:.0f} kcal room"
        enriched["intake_headline"] = f"{calorie_adjustment:.0f} kcal room (optional)"
        enriched["intake_subline"] = (
            f"Intake {fs_cal:.0f} kcal · burn {burn:.0f} kcal · target deficit {target_deficit:.0f} kcal"
        )
        enriched["food_plan"] = build_increase_food_plan(calorie_adjustment, planned_snacks)
    elif calorie_adjustment < -5:
        enriched["adjustment_direction"] = "reduce"
        enriched["action_label"] = f"Reduce {abs(calorie_adjustment):.0f} kcal"
        enriched["intake_headline"] = enriched["action_label"]
        enriched["intake_subline"] = (
            f"Intake {fs_cal:.0f} kcal · burn {burn:.0f} kcal · target deficit {target_deficit:.0f} kcal"
        )
        enriched["food_plan"] = build_reduction_food_plan(abs(calorie_adjustment), planned_snacks)
    else:
        enriched["adjustment_direction"] = "on_target"
        enriched["action_label"] = "On target"
        enriched["intake_headline"] = "On target"
        enriched["intake_subline"] = f"Intake {fs_cal:.0f} kcal aligned with target deficit"
        enriched["food_plan"] = []

    return apply_fuel_target_status(enriched)


def daily_sync_styles_html():
    return """
<style>
.ds-sync-page-marker { display:none; }
div[data-testid="stHorizontalBlock"]:has(.ds-sync-page-marker) {
  align-items: stretch !important;
  gap: 16px !important;
}
div[data-testid="column"]:has(.ds-sync-page-marker),
div[data-testid="stColumn"]:has(.ds-sync-page-marker) {
  background: #ffffff !important;
  border: 1px solid rgba(8, 36, 92, 0.12);
  border-radius: 18px;
  padding: 18px 14px 20px 14px !important;
  box-shadow: 0 2px 10px rgba(8, 36, 92, 0.08);
}
div[data-testid="column"]:has(.ds-sync-page-marker) label,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) label,
div[data-testid="column"]:has(.ds-sync-page-marker) p,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) p,
div[data-testid="column"]:has(.ds-sync-page-marker) span,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) span,
div[data-testid="column"]:has(.ds-sync-page-marker) small,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) small,
div[data-testid="column"]:has(.ds-sync-page-marker) [data-testid="stMarkdownContainer"],
div[data-testid="stColumn"]:has(.ds-sync-page-marker) [data-testid="stMarkdownContainer"],
div[data-testid="column"]:has(.ds-sync-page-marker) [data-testid="stCaptionContainer"],
div[data-testid="stColumn"]:has(.ds-sync-page-marker) [data-testid="stCaptionContainer"] {
  color: #1c1c1e !important;
}
div[data-testid="column"]:has(.ds-sync-page-marker) [data-baseweb="select"] > div,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) [data-baseweb="select"] > div,
div[data-testid="column"]:has(.ds-sync-page-marker) input,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) input {
  background: #f2f2f7 !important;
  border-color: rgba(8, 36, 92, 0.18) !important;
  color: #1c1c1e !important;
}
div[data-testid="column"]:has(.ds-sync-page-marker) [data-testid="stNumberInput"] input,
div[data-testid="stColumn"]:has(.ds-sync-page-marker) [data-testid="stNumberInput"] input {
  color: #1c1c1e !important;
}
.ds-sync-side-title {
  color: #c47a00 !important;
  -webkit-text-fill-color: #c47a00 !important;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.1px;
  text-transform: uppercase;
  margin: 0 0 4px 0;
}
.ds-sync-side-heading {
  color: #061528 !important;
  -webkit-text-fill-color: #061528 !important;
  font-size: 22px;
  font-weight: 900;
  letter-spacing: .3px;
  margin: 0 0 14px 0;
  line-height: 1.1;
}
.ds-sync-shell {
  font-family: "Segoe UI", system-ui, sans-serif;
  background: transparent;
}
.ds-sync-shell .ds-sync-card,
.ds-sync-shell .ds-sync-metric,
.ds-sync-shell .ds-sync-action-list li {
  color: #08245c;
}
.ds-sync-hero {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  min-height: 148px;
  margin-bottom: 14px;
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 12px 32px rgba(8, 36, 92, 0.16);
  color: #ffffff;
  background:
    linear-gradient(115deg, rgba(6, 21, 40, 0.08) 0%, rgba(6, 21, 40, 0.02) 42%, rgba(255,255,255,0) 68%),
    linear-gradient(180deg, #0a1f3d 0%, #1a3d72 38%, #8eb6df 72%, #eef6ff 100%);
}
.ds-sync-hero-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 78% 22%, rgba(244, 189, 79, 0.22) 0%, rgba(244, 189, 79, 0) 42%),
    linear-gradient(90deg, rgba(6, 21, 40, 0.88) 0%, rgba(6, 21, 40, 0.62) 52%, rgba(6, 21, 40, 0.42) 100%);
}
.ds-sync-hero-content {
  position: relative;
  z-index: 1;
  padding: 20px 22px 18px 22px;
}
.ds-sync-hero-panel {
  display: inline-block;
  max-width: 440px;
  background: rgba(6, 21, 40, 0.94);
  border: 1px solid rgba(244, 189, 79, 0.32);
  border-radius: 14px;
  padding: 16px 18px 14px 18px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.32);
}
.ds-sync-hero-kicker {
  color: #f4bd4f;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.45);
}
.ds-sync-hero-intake {
  color: #ffffff;
  font-size: 46px;
  font-weight: 900;
  line-height: 1;
  margin-top: 6px;
  letter-spacing: -1px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}
.ds-sync-hero-intake span {
  font-size: 18px;
  font-weight: 800;
  color: #f4bd4f;
  margin-left: 6px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
}
.ds-sync-hero-caption {
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  margin-top: 8px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
}
.ds-sync-hero-warn {
  color: #ffe08a;
  font-size: 14px;
  font-weight: 800;
  margin-top: 10px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
}
.ds-sync-card {
  background: #fffdf8;
  border: 1px solid #e6edf7;
  border-radius: 16px;
  padding: 16px 16px 14px 16px;
  margin-bottom: 12px;
  box-shadow: 0 8px 24px rgba(8, 36, 92, 0.08);
}
.ds-sync-card-title {
  color: #08245c;
  font-size: 12px;
  font-weight: 850;
  letter-spacing: .9px;
  text-transform: uppercase;
  margin: 0 0 12px 0;
}
.ds-sync-card-title.gold { color: #c47a00; }
.ds-sync-metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
.ds-sync-metrics.cols-5 { grid-template-columns: repeat(5, minmax(0, 1fr)); }
@media (max-width: 1100px) {
  .ds-sync-metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.ds-sync-metric {
  background: #ffffff;
  border: 1px solid #e6edf7;
  border-radius: 14px;
  padding: 12px 12px 10px 12px;
  min-height: 74px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.9);
}
.ds-sync-metric.accent {
  border-color: rgba(217, 140, 0, 0.35);
  background: linear-gradient(180deg, #fffaf2 0%, #ffffff 100%);
}
.ds-sync-metric-label {
  color: #4f638a;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .55px;
  text-transform: uppercase;
  line-height: 1.2;
}
.ds-sync-metric-value {
  color: #08245c;
  font-size: 24px;
  font-weight: 900;
  line-height: 1.05;
  margin-top: 6px;
  letter-spacing: -.3px;
}
.ds-sync-metric-value.gold { color: #d98c00; }
.ds-sync-metric-value .ds-unit {
  font-size: 12px;
  font-weight: 800;
  color: #6b7280;
  margin-left: 2px;
}
.ds-sync-action-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.ds-sync-action-list li {
  background: #ffffff;
  border: 1px solid #e6edf7;
  border-left: 4px solid #d98c00;
  border-radius: 10px;
  padding: 9px 12px;
  color: #08245c;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.35;
}
.ds-sync-action-list li.primary {
  background: linear-gradient(90deg, rgba(217,140,0,.12), rgba(255,255,255,.95));
  border-left-color: #d98c00;
  font-weight: 850;
  color: #08245c;
}
.ds-sync-action-list li.muted {
  border-left-color: #94a3b8;
  font-weight: 650;
}
div[data-testid="stExpander"]:has(.ds-sync-expander-marker) {
  background: #fffdf8;
  border: 1px solid #e6edf7;
  border-radius: 14px;
}
div[data-testid="stExpander"]:has(.ds-sync-expander-marker) label,
div[data-testid="stExpander"]:has(.ds-sync-expander-marker) p,
div[data-testid="stExpander"]:has(.ds-sync-expander-marker) span {
  color: #08245c !important;
}
</style>
"""


def daily_sync_embedded_css():
    return """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui, sans-serif;
    background: #f2f2f7;
    color: #1c1c1e;
    font-size: 14px;
    line-height: 1.3;
    -webkit-font-smoothing: antialiased;
  }
  .ah-shell { padding: 8px 10px 12px 10px; }
  .ah-energy-strip {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 6px;
  }
  .ah-energy-math {
    font-size: 12px;
    color: #636366;
    text-align: center;
    margin: 0 4px 12px 4px;
    line-height: 1.35;
  }
  .ah-pill {
    background: #fff;
    border-radius: 12px;
    padding: 10px 8px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0,0,0,.05);
  }
  .ah-pill-label {
    display: block;
    font-size: 11px;
    font-weight: 600;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-bottom: 3px;
  }
  .ah-pill-value {
    display: block;
    font-size: 17px;
    font-weight: 700;
    color: #1c1c1e;
    letter-spacing: -.02em;
  }
  .ah-pill-sub {
    display: block;
    font-size: 11px;
    color: #8e8e93;
    margin-top: 2px;
  }
  .ah-tiles {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 12px;
  }
  .ah-tile {
    background: #fff;
    border-radius: 14px;
    padding: 12px 8px 10px 8px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 148px;
  }
  .ah-tile-title {
    font-size: 12px;
    font-weight: 600;
    color: #8e8e93;
    margin-bottom: 6px;
  }
  .ah-ring-wrap {
    position: relative;
    width: 76px;
    height: 76px;
    margin-bottom: 6px;
  }
  .ah-ring-center {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    line-height: 1.05;
  }
  .ah-ring-num {
    font-size: 16px;
    font-weight: 700;
    color: #1c1c1e;
    letter-spacing: -.02em;
  }
  .ah-ring-unit {
    font-size: 10px;
    font-weight: 600;
    color: #8e8e93;
  }
  .ah-tile-target {
    font-size: 11px;
    color: #8e8e93;
    margin-bottom: 5px;
  }
  .ah-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 999px;
    letter-spacing: .01em;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .ah-badge-good { background: #e8f8ec; color: #248a3d; }
  .ah-badge-warn { background: #fff4e5; color: #c93400; }
  .ah-badge-neutral { background: #f2f2f7; color: #636366; }
  .ah-next {
    background: #fff;
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }
  .ah-next-title {
    font-size: 13px;
    font-weight: 700;
    color: #1c1c1e;
    margin-bottom: 8px;
  }
  .ah-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
  }
  .ah-chip {
    font-size: 12px;
    font-weight: 650;
    padding: 5px 10px;
    border-radius: 999px;
    background: #f2f2f7;
    color: #1c1c1e;
  }
  .ah-chip-warn { background: #fff4e5; color: #c93400; }
  .ah-chip-good { background: #e8f8ec; color: #248a3d; }
  .ah-next-steps {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .ah-next-steps li {
    font-size: 12px;
    color: #636366;
    padding: 4px 0 4px 14px;
    position: relative;
    line-height: 1.35;
  }
  .ah-next-steps li::before {
    content: "•";
    position: absolute;
    left: 0;
    color: #aeaeb2;
  }
  .ah-empty-banner {
    background: #fff;
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }
  .ah-empty-banner p {
    font-size: 14px;
    color: #636366;
    margin-top: 8px;
    line-height: 1.4;
  }
  .ah-group-label {
    font-size: 13px;
    font-weight: 600;
    color: #6c6c70;
    margin: 0 0 8px 4px;
  }
</style>
"""


def _target_ring_pct(current, target):
    if current is None or target is None or float(target) <= 0:
        return 0.0
    return min(100.0, max(0.0, (float(current) / float(target)) * 100.0))


def _ring_svg(pct, color):
    radius = 30
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1.0 - float(pct) / 100.0)
    return f"""
    <svg class="ah-ring-svg" width="76" height="76" viewBox="0 0 76 76" aria-hidden="true">
      <circle cx="38" cy="38" r="{radius}" fill="none" stroke="#ebebf0" stroke-width="7"/>
      <circle cx="38" cy="38" r="{radius}" fill="none" stroke="{color}" stroke-width="7"
        stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"
        stroke-linecap="round" transform="rotate(-90 38 38)"/>
    </svg>
    """


def _badge_html(status, tone):
    cls = {"good": "ah-badge-good", "warn": "ah-badge-warn"}.get(tone or "", "ah-badge-neutral")
    short = str(status or "—")
    if " below" in short:
        short = short.replace(" below", " ↓")
    elif " above" in short:
        short = short.replace(" above", " ↑")
    return f'<span class="ah-badge {cls}">{short}</span>'


def _metric_tile(title, current, target, unit, status, tone, accent):
    pct = _target_ring_pct(current, target)
    ring_color = {"good": "#34c759", "warn": "#ff9500"}.get(tone or "", accent)
    if current is None:
        display = "—"
    elif unit == "kcal":
        display = f"{float(current):,.0f}"
    else:
        display = f"{float(current):.0f}" if float(current) >= 100 else f"{float(current):.1f}"
    target_txt = f"{float(target):,.0f}" if unit == "kcal" else f"{float(target):.0f}"
    return f"""
    <div class="ah-tile">
      <div class="ah-tile-title">{title}</div>
      <div class="ah-ring-wrap">
        {_ring_svg(pct, ring_color)}
        <div class="ah-ring-center">
          <span class="ah-ring-num">{display}</span>
          <span class="ah-ring-unit">{unit}</span>
        </div>
      </div>
      <div class="ah-tile-target">of {target_txt} {unit}</div>
      {_badge_html(status, tone)}
    </div>
    """


def _energy_strip(burn, intake, target_deficit, projected_deficit=None, calorie_target=None, burn_so_far=None):
    burn_val = float(burn)
    intake_val = float(intake) if intake is not None else None
    if projected_deficit is not None:
        proj = float(projected_deficit)
    elif intake_val is not None:
        proj = burn_val - intake_val
    else:
        proj = float(target_deficit)
    intake_txt = f"{intake_val:,.0f}" if intake_val is not None else "—"
    eat_target = f"{float(calorie_target):,.0f}" if calorie_target else "—"
    deficit_so_far_txt = ""
    if burn_so_far is not None and intake_val is not None and float(burn_so_far) > 0:
        deficit_so_far = float(burn_so_far) - intake_val
        deficit_so_far_txt = f'<div class="ah-pill"><span class="ah-pill-label">Deficit so far</span><span class="ah-pill-value">{deficit_so_far:,.0f}</span><span class="ah-pill-sub">burn so far − intake</span></div>'
    burn_sub = f"{float(burn_so_far):,.0f} so far · {burn_val:,.0f} projected" if burn_so_far is not None and float(burn_so_far) > 0 else "kcal projected EOD"
    return f"""
    <div class="ah-energy-strip">
      <div class="ah-pill">
        <span class="ah-pill-label">Intake</span>
        <span class="ah-pill-value">{intake_txt}</span>
        <span class="ah-pill-sub">kcal today</span>
      </div>
      <div class="ah-pill">
        <span class="ah-pill-label">Burn</span>
        <span class="ah-pill-value">{burn_val:,.0f}</span>
        <span class="ah-pill-sub">{burn_sub}</span>
      </div>
      {deficit_so_far_txt}
      <div class="ah-pill">
        <span class="ah-pill-label">Deficit</span>
        <span class="ah-pill-value">{proj:,.0f}</span>
        <span class="ah-pill-sub">projected · goal {float(target_deficit):,.0f}</span>
      </div>
    </div>
    <div class="ah-energy-math">Eat up to <strong>{eat_target}</strong> kcal to hit the {float(target_deficit):,.0f} kcal deficit goal.</div>
    """


def _compact_actions(fuel_plan, protein_target, carb_target):
    direction = fuel_plan.get("adjustment_direction")
    gap = fuel_plan.get("protein_gap")
    carb_gap = fuel_plan.get("carb_gap")
    chips = []
    steps = []

    if direction == "increase":
        chips.append(
            f'<span class="ah-chip">{fuel_plan["calorie_adjustment"]:.0f} kcal room</span>'
        )
    elif direction == "reduce":
        chips.append(
            f'<span class="ah-chip ah-chip-warn">−{abs(fuel_plan["calorie_adjustment"]):.0f} kcal</span>'
        )
    elif direction == "on_target":
        chips.append('<span class="ah-chip ah-chip-good">Calories OK</span>')

    if gap is not None and gap > 5:
        chips.append(f'<span class="ah-chip ah-chip-warn">+{gap:.0f}g protein</span>')
    elif gap is not None:
        chips.append('<span class="ah-chip ah-chip-good">Protein OK</span>')

    if carb_gap is not None and carb_gap > 5:
        chips.append(f'<span class="ah-chip ah-chip-warn">+{carb_gap:.0f}g carbs</span>')
    elif carb_gap is not None:
        chips.append('<span class="ah-chip ah-chip-good">Carbs OK</span>')

    if not chips:
        chips.append('<span class="ah-chip ah-chip-good">All on target</span>')

    if direction == "reduce":
        for step in (fuel_plan.get("food_plan") or [])[:4]:
            steps.append(f"<li>{step}</li>")

    steps_html = f'<ul class="ah-next-steps">{"".join(steps)}</ul>' if steps else ""
    chips_html = f'<div class="ah-chips">{"".join(chips)}</div>'

    if not steps and direction == "on_target" and (gap is None or gap <= 5) and (carb_gap is None or carb_gap <= 5):
        return ""

    return f"""
    <div class="ah-next">
      <div class="ah-next-title">Next steps</div>
      {chips_html}
      {steps_html}
    </div>
    """


def daily_sync_dashboard_html(fuel_plan):
    has_fs = fuel_plan.get("has_fatsecret")
    protein_target = float(fuel_plan.get("protein_target_g") or 0)
    calorie_target = float(fuel_plan.get("calorie_target") or fuel_plan.get("recommended_intake") or 0)
    carb_target = float(fuel_plan.get("carb_target_g") or fuel_plan.get("carb_minimum_g") or 0)

    if not has_fs:
        return daily_sync_embedded_css() + f"""
<div class="ah-shell">
  {_energy_strip(fuel_plan['total_expenditure'], None, fuel_plan['target_deficit'], None, calorie_target)}
  <div class="ah-group-label">Daily targets</div>
  <div class="ah-tiles">
    {_metric_tile("Calories", None, calorie_target, "kcal", "Enter intake", "warn", "#ff9500")}
    {_metric_tile("Protein", None, protein_target, "g", "—", "", "#007aff")}
    {_metric_tile("Carbs", None, carb_target, "g", "—", "", "#34c759")}
  </div>
  <div class="ah-empty-banner">
    <strong>No intake yet</strong>
    <p>Enter calories and protein on the left — rings update live.</p>
  </div>
</div>
"""

    fs_cal = float(fuel_plan["fatsecret_calories"])
    calorie_status = fuel_plan.get("calorie_status") or "—"
    calorie_status_tone = fuel_plan.get("calorie_status_tone") or ""
    protein_status = fuel_plan.get("protein_status") or "—"
    protein_status_tone = fuel_plan.get("protein_status_tone") or ""
    carb_status = fuel_plan.get("carb_status") or "—"
    carb_status_tone = fuel_plan.get("carb_status_tone") or ""

    protein_planned = fuel_plan.get("fatsecret_protein_g")
    carbs = fuel_plan.get("fatsecret_carbs_g")

    tiles_html = (
        _metric_tile("Calories", fs_cal, calorie_target, "kcal", calorie_status, calorie_status_tone, "#ff9500")
        + _metric_tile("Protein", protein_planned, protein_target, "g", protein_status, protein_status_tone, "#007aff")
        + _metric_tile("Carbs", carbs, carb_target, "g", carb_status, carb_status_tone, "#34c759")
    )
    actions_html = _compact_actions(fuel_plan, protein_target, carb_target)

    return daily_sync_embedded_css() + f"""
<div class="ah-shell">
  {_energy_strip(
      fuel_plan['total_expenditure'],
      fs_cal,
      fuel_plan['target_deficit'],
      fuel_plan.get('projected_deficit'),
      calorie_target,
      burn_so_far=fuel_plan.get('burn_so_far'),
  )}
  <div class="ah-tiles">{tiles_html}</div>
  {actions_html}
</div>
"""


def render_daily_sync_dashboard(fuel_plan):
    st.markdown(daily_sync_styles_html(), unsafe_allow_html=True)
    height = 450 if fuel_plan.get("has_fatsecret") else 410
    components.html(daily_sync_dashboard_html(fuel_plan), height=height, scrolling=False)


def morning_weight_prompt_done_for(day=None):
    day = day or date.today()
    day_iso = day.isoformat() if hasattr(day, "isoformat") else str(day)[:10]
    return get_text_setting("morning_weight_prompt_done", "") == day_iso


def mark_morning_weight_prompt_done(day=None):
    day = day or date.today()
    day_iso = day.isoformat() if hasattr(day, "isoformat") else str(day)[:10]
    save_text_setting("morning_weight_prompt_done", day_iso)


def morning_weight_logged_for_day(daily, log_day=None):
    log_day = log_day or date.today()
    if daily.empty:
        return False
    rows = daily[daily["log_date"].dt.date == log_day]
    if rows.empty:
        return False
    weight = rows.iloc[0].get("weight_lbs")
    return weight is not None and not pd.isna(weight) and float(weight) > 0


def default_morning_weight(settings, daily, log_day=None):
    log_day = log_day or date.today()
    if not daily.empty:
        prior = daily[(daily["log_date"].dt.date <= log_day) & daily["weight_lbs"].notna()].copy()
        if not prior.empty:
            return float(prior.iloc[-1]["weight_lbs"])
    return float(settings.get("current_weight_lbs") or DEFAULTS["current_weight_lbs"])


def save_morning_weight(weight_lbs, log_day=None):
    """Log morning weigh-in to daily history and live weight."""
    log_day = log_day or date.today()
    log_day_iso = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)[:10]
    weight = float(weight_lbs)
    existing = get_daily_row(log_day_iso) or {}
    merged = dict(existing)
    merged["log_date"] = log_day_iso
    merged["weight_lbs"] = weight
    merged["notes"] = tag_import_notes("Scale", merged.get("notes") or "Morning weigh-in")
    upsert_daily(merged, source="Scale", force=True, data_ts=pd.Timestamp.now())
    save_setting("current_weight_lbs", weight)
    save_text_setting("current_weight_source", "Morning weigh-in")
    save_text_setting("current_weight_manual_override", "")
    mark_morning_weight_prompt_done(log_day)


def should_show_morning_weight_prompt(daily, log_day=None):
    log_day = log_day or date.today()
    if log_day != date.today():
        return False
    if morning_weight_logged_for_day(daily, log_day):
        if not morning_weight_prompt_done_for(log_day):
            mark_morning_weight_prompt_done(log_day)
        return False
    return not morning_weight_prompt_done_for(log_day)


def render_morning_weight_prompt(daily, settings):
    """Prompt for today's morning weight on first app use each day."""
    today = date.today()
    if not should_show_morning_weight_prompt(daily, today):
        return settings

    default_weight = default_morning_weight(settings, daily, today)
    with st.container(border=True):
        st.markdown("### Morning weigh-in")
        st.caption(
            f"Log **{today.strftime('%A, %b %d')}** weight to keep trends and your completion timeline accurate."
        )
        weight = st.number_input(
            "Weight (lb)",
            min_value=50.0,
            max_value=500.0,
            value=float(default_weight),
            step=0.1,
            key="morning_weight_input",
        )
        save_col, skip_col = st.columns([1, 1])
        with save_col:
            if st.button("Save morning weight", type="primary", use_container_width=True, key="morning_weight_save"):
                save_morning_weight(weight, today)
                settings["current_weight_lbs"] = float(weight)
                st.rerun()
        with skip_col:
            if st.button("Skip for today", use_container_width=True, key="morning_weight_skip"):
                mark_morning_weight_prompt_done(today)
                st.rerun()
    return settings


def render_daily_activity_panel(log_day, settings, day_row, fuel_workout):
    """Steps progress, workout done, burn so far — feeds live fuel-plan updates."""
    day_key = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)[:10]
    day_row = day_row or {}
    close = get_daily_day_close(log_day)

    default_step_goal = float(settings.get("default_step_goal", 12000))
    default_steps_so_far = float(day_row.get("steps") or 0)
    if close and close.get("steps") is not None:
        default_steps_so_far = float(close["steps"])
    if default_steps_so_far <= 0 and float(day_row.get("oura_burn") or 0) > 0:
        default_steps_so_far = 0.0

    default_workout_done = is_fuel_workout_confirmed_for_date(log_day)
    if not default_workout_done and is_observed_workout_burn_row(day_row):
        default_workout_done = True

    st.markdown("**Activity & burn**")
    workout_complete = st.checkbox(
        "Workout complete",
        value=default_workout_done,
        key=f"ds_workout_done_{day_key}",
        help="Check after your session — adds workout burn to today's totals.",
    )

    step_col, goal_col = st.columns(2)
    with step_col:
        steps_so_far = st.number_input(
            "Steps so far",
            min_value=0.0,
            value=default_steps_so_far,
            step=250.0,
            key=f"ds_steps_so_far_{day_key}",
        )
    with goal_col:
        step_goal = st.number_input(
            "Step target",
            min_value=0.0,
            value=default_step_goal,
            step=500.0,
            key=f"ds_step_goal_{day_key}",
        )

    step_progress = min(1.0, steps_so_far / step_goal) if step_goal > 0 else 0.0
    st.progress(step_progress)
    st.caption(f"**{steps_so_far:,.0f}** / **{step_goal:,.0f}** steps ({100 * step_progress:.0f}% of target)")

    burn_row = dict(day_row)
    burn_row["workout"] = fuel_workout
    burn_row["steps"] = steps_so_far
    imported_oura = float(day_row.get("oura_burn") or 0)

    oura_col, burn_col = st.columns(2)
    with oura_col:
        oura_burn_so_far = st.number_input(
            "Oura burn so far (kcal)",
            min_value=0.0,
            value=imported_oura,
            step=25.0,
            key=f"ds_oura_burn_{day_key}",
            help="Total calories burned today from Oura — edit if not imported yet or app shows a newer total.",
        )
    with burn_col:
        manual_burn_so_far = None
        if oura_burn_so_far <= 0:
            auto_burn_info = resolve_day_calories_burned(burn_row, settings)
            default_manual = float(auto_burn_info.get("calories_burned") or 0)
            manual_burn_so_far = st.number_input(
                "Burn so far (no Oura)",
                min_value=0.0,
                value=default_manual,
                step=25.0,
                key=f"ds_burn_so_far_{day_key}",
                help="Used only when Oura burn is 0 — enter estimated burn so far.",
            )

    if imported_oura > 0 and oura_burn_so_far == imported_oura:
        st.caption(f"Oura import on file: **{imported_oura:,.0f} kcal** — edit above if your app shows more.")
    elif oura_burn_so_far > 0:
        st.caption(f"Using Oura burn so far: **{oura_burn_so_far:,.0f} kcal**.")
    elif manual_burn_so_far and manual_burn_so_far > 0:
        st.caption(f"No Oura — using estimated burn so far: **{manual_burn_so_far:,.0f} kcal**.")
    else:
        st.caption("Enter **Oura burn so far** from the Oura app, or leave at 0 to use step-based estimate.")

    default_observed = float(day_row.get("active_energy") or 0) if is_observed_workout_burn_row(day_row) else 0.0
    fuel_observed = 0.0
    if fuel_workout != "None" and workout_complete:
        fuel_observed = st.number_input(
            "Workout burn override (kcal)",
            min_value=0.0,
            value=default_observed,
            step=25.0,
            key=f"ds_workout_burn_{day_key}",
            help="0 = use workout-type estimate (A/B/C/StairMaster). Enter actual burn to override.",
        )

    snapshot = compute_daily_burn_snapshot(
        settings,
        day_row,
        steps_so_far,
        step_goal,
        fuel_workout,
        workout_complete,
        manual_burn_so_far=manual_burn_so_far,
        oura_burn_so_far=oura_burn_so_far if oura_burn_so_far > 0 else None,
        workout_burn_override=fuel_observed if fuel_observed > 0 else None,
    )

    burn_so_far = float(snapshot["burn_so_far"])
    projected = float(snapshot["projected_daily_burn"])
    st.markdown(
        f"**{burn_so_far:,.0f}** kcal burned so far "
        f"({burn_source_label(snapshot.get('burn_so_far_source'))}) · "
        f"**{projected:,.0f}** kcal projected for the day"
    )

    return {
        "steps_so_far": steps_so_far,
        "step_goal": step_goal,
        "workout_complete": workout_complete,
        "manual_burn_so_far": manual_burn_so_far,
        "oura_burn_so_far": oura_burn_so_far if oura_burn_so_far > 0 else None,
        "fuel_observed": fuel_observed,
        "burn_snapshot": snapshot,
    }


def save_daily_sync_day(log_day, settings, fuel_plan, intake, fuel_workout, fuel_steps, fuel_observed, weight_lbs=None, calories_burned=None, notes="", workout_complete=False, step_goal=None, oura_burn_so_far=None):
    """Persist intake, activity, burn, and deficit snapshot for history and forecasting."""
    log_day_iso = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)[:10]
    daily_row = {
        "log_date": log_day_iso,
        "calories": float(intake.get("calories") or 0),
        "protein_g": float(intake.get("protein_g") or 0),
        "carbs_g": float(intake.get("carbs_g") or 0) if intake.get("carbs_g") is not None else None,
        "steps": float(fuel_steps or 0),
        "workout": fuel_workout,
    }
    if weight_lbs is not None and float(weight_lbs) > 0:
        daily_row["weight_lbs"] = float(weight_lbs)
    if fuel_observed and float(fuel_observed) > 0:
        daily_row["active_energy"] = float(fuel_observed)
    if oura_burn_so_far is not None and float(oura_burn_so_far) > 0:
        daily_row["oura_burn"] = float(oura_burn_so_far)

    existing = get_daily_row(log_day_iso) or {}
    merged = dict(existing)
    for key, val in daily_row.items():
        if val is not None:
            merged[key] = val
    merged["log_date"] = log_day_iso
    merged["notes"] = tag_import_notes("Rebalance", merged.get("notes") or "Daily Sync end-of-day log")

    upsert_daily(merged, source="Rebalance", force=True, data_ts=pd.Timestamp.now())
    save_fuel_workout_for_date(log_day, fuel_workout)

    if workout_complete:
        mark_fuel_workout_confirmed(log_day)

    if calories_burned is not None and float(calories_burned) > 0:
        burn = float(calories_burned)
    else:
        burn = float(fuel_plan.get("projected_daily_burn") or fuel_plan.get("total_expenditure") or 0)
    intake_kcal = float(merged.get("calories") or 0)
    projected_deficit = burn - intake_kcal if burn > 0 and intake_kcal > 0 else fuel_plan.get("projected_deficit")
    target_deficit = float(fuel_plan.get("target_deficit") or settings.get("target_deficit") or 500)
    save_daily_day_close(
        {
            "log_date": log_day_iso,
            "weight_lbs": merged.get("weight_lbs"),
            "calories": merged.get("calories"),
            "protein_g": merged.get("protein_g"),
            "carbs_g": merged.get("carbs_g"),
            "fat_g": merged.get("fat_g"),
            "steps": merged.get("steps"),
            "step_goal": float(step_goal) if step_goal is not None else fuel_plan.get("step_goal"),
            "workout": fuel_workout,
            "workout_complete": 1 if workout_complete else 0,
            "burn_so_far": fuel_plan.get("burn_so_far"),
            "total_burn": burn,
            "projected_deficit": float(projected_deficit) if projected_deficit is not None else None,
            "target_deficit": target_deficit,
            "finalized": 1,
            "finalized_at": datetime.now().isoformat(timespec="seconds"),
            "notes": notes or "End-of-day log from Daily Sync",
        }
    )
    if (log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)[:10]) == date.today().isoformat():
        if merged.get("weight_lbs"):
            mark_morning_weight_prompt_done(date.today())


def save_cut_day_log(log_day, settings, calories_in, calories_burned, weight_lbs, sleep_quality, workout):
    """Persist the five daily cut inputs: intake, burn, weight, sleep, workout."""
    log_day_iso = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)[:10]
    existing = get_daily_row(log_day_iso) or {}
    merged = dict(existing)
    merged["log_date"] = log_day_iso
    merged["calories"] = float(calories_in or 0)
    if weight_lbs is not None and float(weight_lbs) > 0:
        merged["weight_lbs"] = float(weight_lbs)
    merged["sleep_score"] = sleep_score_from_quality(sleep_quality)
    merged["workout"] = workout
    burn = float(calories_burned or 0)
    if burn > 0:
        merged["oura_burn"] = burn
    merged["notes"] = tag_import_notes("Rebalance", merged.get("notes") or "Daily cut log")
    upsert_daily(merged, source="Rebalance", force=True, data_ts=pd.Timestamp.now())
    save_fuel_workout_for_date(log_day, workout)
    workout_complete = is_training_workout(workout)
    if workout_complete:
        mark_fuel_workout_confirmed(log_day)
    intake_kcal = float(merged.get("calories") or 0)
    deficit = (burn - intake_kcal) if burn > 0 and intake_kcal > 0 else None
    target_deficit = float(settings.get("target_deficit") or 500)
    save_daily_day_close(
        {
            "log_date": log_day_iso,
            "weight_lbs": merged.get("weight_lbs"),
            "calories": intake_kcal,
            "workout": workout,
            "total_burn": burn if burn > 0 else None,
            "projected_deficit": deficit,
            "target_deficit": target_deficit,
            "finalized": 1,
            "finalized_at": datetime.now().isoformat(timespec="seconds"),
            "notes": "Cut log: calories in/out, weight, sleep, workout",
        }
    )
    if merged.get("weight_lbs") and log_day_iso == date.today().isoformat():
        save_setting("current_weight_lbs", float(merged["weight_lbs"]))
        save_text_setting("current_weight_source", "Daily cut log")
        save_text_setting("current_weight_manual_override", "")
        mark_morning_weight_prompt_done(date.today())


def default_logged_burn(day_row, settings, close=None):
    oura = float((day_row or {}).get("oura_burn") or 0)
    if oura > 0:
        return oura
    if close and close.get("total_burn"):
        try:
            burn = float(close["total_burn"])
            if burn > 0:
                return burn
        except (TypeError, ValueError):
            pass
    resolved = resolve_day_calories_burned(day_row or {}, settings)
    return float(resolved.get("calories_burned") or 0)


def render_simple_cut_day_form(log_day, settings, daily, day_row=None):
    """Only five inputs: calories in, calories burned, weight, sleep quality, workout."""
    day_row = day_row or {}
    close = get_daily_day_close(log_day)
    day_key = log_day.isoformat() if hasattr(log_day, "isoformat") else str(log_day)[:10]

    logged = logged_intake_for_day(daily, log_day)
    cal_default = float(logged["calories"]) if logged else float(day_row.get("calories") or 0)
    if cal_default <= 0:
        cal_default = float(default_daily_intake_values(settings).get("calories") or 0)

    burn_default = default_logged_burn(day_row, settings, close)
    weight_default = float(day_row.get("weight_lbs") or 0)
    if weight_default <= 0:
        weight_default = default_morning_weight(settings, daily, log_day)

    saved_sleep = day_row.get("sleep_score")
    sleep_default = sleep_quality_from_score(saved_sleep) if saved_sleep else "Good"
    if sleep_default not in SLEEP_QUALITY_OPTIONS:
        sleep_default = "Good"

    saved_workout = get_fuel_workout_for_date(log_day) or day_row.get("workout") or resolve_fuel_workout_for_day(log_day)
    if saved_workout not in SIMPLE_DAILY_WORKOUTS:
        saved_workout = "None"

    st.markdown("**Today's log**")
    st.caption("FatSecret intake, Oura burn as reported, Apple Health weight.")

    calories_in = st.number_input(
        "Calories in (FatSecret)",
        min_value=0.0,
        value=float(cal_default),
        step=50.0,
        key=f"cut_cal_in_{day_key}",
        help="Daily calories eaten from FatSecret. Leave as imported — do not adjust.",
    )
    calories_burned = st.number_input(
        "Calories burned (Oura)",
        min_value=0.0,
        value=float(burn_default),
        step=25.0,
        key=f"cut_cal_burn_{day_key}",
        help="Oura total burn as shown in the app. Used as-is — no workout or step add-on.",
    )
    weight = st.number_input(
        "Weight (lb)",
        min_value=50.0,
        max_value=500.0,
        value=float(weight_default),
        step=0.1,
        key=f"cut_weight_{day_key}",
    )
    sleep_quality = st.selectbox(
        "Sleep quality",
        SLEEP_QUALITY_OPTIONS,
        index=SLEEP_QUALITY_OPTIONS.index(sleep_default),
        key=f"cut_sleep_{day_key}",
        help="Poor sleep slows fat loss even in a deficit. Good/Excellent keeps the cut on pace.",
    )
    workout = st.selectbox(
        "Workout",
        SIMPLE_DAILY_WORKOUTS,
        index=SIMPLE_DAILY_WORKOUTS.index(saved_workout),
        key=f"cut_workout_{day_key}",
        help=f"Training plan is {EXPECTED_WEEKLY_WORKOUTS[0]}–{EXPECTED_WEEKLY_WORKOUTS[1]} sessions/week.",
    )

    preview_deficit = None
    if calories_in > 0 and calories_burned > 0:
        preview_deficit = calories_burned - calories_in
        tone = "surplus" if preview_deficit < 0 else "deficit"
        st.caption(f"Today: **{preview_deficit:,.0f} kcal {tone}** (Oura − FatSecret)")

    if close and close.get("finalized"):
        st.caption(f"Saved for **{day_key}**. Change any field and save again to update.")

    if st.button("Save day", type="primary", use_container_width=True, key=f"cut_save_{day_key}"):
        save_cut_day_log(
            log_day,
            settings,
            calories_in,
            calories_burned,
            weight,
            sleep_quality,
            workout,
        )
        st.success(f"Saved **{day_key}**.")
        st.rerun()

    return {
        "calories": float(calories_in),
        "calories_burned": float(calories_burned),
        "weight_lbs": float(weight),
        "sleep_quality": sleep_quality,
        "workout": workout,
        "preview_deficit": preview_deficit,
        "saved": bool(close and close.get("finalized")),
    }


def _fmt_kcal(value):
    if value is None:
        return "—"
    return f"{value:,.0f}"


def render_deficit_tracker_panel(hist, settings, live=None, fc=None):
    """Cumulative caloric deficit from DEXA toward the goal body-fat %."""
    fc = fc or {}
    live = live or {}
    goal_bf = float(fc.get("goal_body_fat_pct") or settings.get("goal_body_fat_pct") or 10.0)
    goal_weight = float(fc.get("target_weight") or goal_weight_lbs(settings, fc) or 0)
    current_bf = float(fc.get("current_bf") or settings.get("current_body_fat_pct") or 0)
    scale_weight = float(live.get("weight_lbs") or fc.get("scale_weight") or settings.get("current_weight_lbs") or 0)
    fat_to_lose = float(fc.get("fat_to_lose") or 0)
    kcal_needed = float(fc.get("kcal_to_goal") or fat_to_lose * KCAL_PER_LB_FAT)
    cumulative = fc.get("cumulative_deficit_kcal")
    kcal_progress = float(fc.get("kcal_progress") or 0)
    remaining = remaining_cut_to_goal(
        scale_weight,
        goal_weight,
        fat_to_lose=fat_to_lose,
    )
    rollups = compute_deficit_rollups(hist)
    today_def = live.get("preview_deficit")
    if today_def is None:
        today_def = rollups["daily"]
    avg_def = fc.get("avg_daily_deficit")
    if avg_def is None:
        avg_def = rollups["avg_daily"]
    days_left = fc.get("days")
    goal_date = fc.get("goal_date")
    anchor_label = fc.get("composition_anchor") or "DEXA"

    st.markdown(f"### Cut to {goal_bf:.1f}% body fat")
    st.caption(
        f"Baseline **{anchor_label}**. Lean mass held constant. "
        f"Live weight is the latest scale/log"
        f"{f' ({scale_weight:.1f} lb)' if scale_weight else ''}. "
        f"Deficit = **Oura burn − FatSecret intake** (Oura used as reported). "
        f"Progress is cumulative kcal since the scan · **{KCAL_PER_LB_FAT:.0f} kcal = 1 lb fat**."
    )

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Est. body fat", f"{current_bf:.1f}%" if current_bf else "—")
    g2.metric("Goal", f"{goal_bf:.1f}%")
    g3.metric("Fat still to lose", f"{remaining['lbs_remaining']:.1f} lb")
    g4.metric("kcal still needed", f"{remaining['kcal_remaining']:,.0f}")
    if remaining["lbs_remaining"] <= 0:
        st.success(f"At or below **{goal_bf:.1f}%** body fat on the deficit model — hold with maintenance.")
    else:
        st.progress(min(1.0, max(0.0, kcal_progress)))
        st.caption(
            f"Cumulative deficit **{_fmt_kcal(cumulative)}** kcal of "
            f"**{float(fc.get('original_kcal_to_goal') or remaining['kcal_remaining'] + (cumulative or 0)):,.0f}** kcal "
            f"from DEXA to {goal_bf:.1f}% · scale **{scale_weight:.1f} lb** · "
            f"goal weight **{goal_weight:.1f} lb**."
        )

    st.markdown("**Calorie deficit**")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Today", _fmt_kcal(today_def), help="Oura − FatSecret for the selected day.")
    d2.metric("This week", _fmt_kcal(rollups["weekly"]), help=f"{rollups['weekly_days']} logged day(s) in the last 7.")
    d3.metric("This month", _fmt_kcal(rollups["monthly"]), help=f"{rollups['monthly_days']} logged day(s) in the last 30.")
    d4.metric("Since DEXA", _fmt_kcal(cumulative if cumulative is not None else rollups["total"]))

    st.markdown("**Pace to goal**")
    a1, a2, a3 = st.columns(3)
    a1.metric("Avg daily deficit", f"{avg_def:,.0f} kcal" if avg_def is not None else "—")
    if days_left is not None:
        a2.metric("Days to complete", f"{int(round(days_left))}")
    else:
        a2.metric("Days to complete", "—")
    if goal_date:
        a3.metric("ETA", goal_date.strftime("%b %d, %Y").replace(" 0", " "))
    else:
        a3.metric("ETA", "—")

    st.markdown("**Target deficit — days, weeks, cumulative**")
    render_deficit_pace_visuals(hist, settings, fc=fc, key_prefix="ds_defvis", live=live)


def render_end_of_day_log(log_day, settings, fuel_plan, intake, fuel_workout, fuel_steps, fuel_observed, day_row=None, workout_complete=False, step_goal=None, oura_burn_so_far=None):
    """Save the full day to history — editable later on the Trends tab."""
    day_row = day_row or {}
    close = get_daily_day_close(log_day)
    st.markdown("**End-of-day log**")
    if close and close.get("finalized"):
        finalized_at = close.get("finalized_at") or "earlier"
        st.caption(f"Saved for **{log_day.isoformat()}** ({finalized_at}). Update values and save again to edit.")

    default_burn = float(
        fuel_plan.get("projected_daily_burn") or fuel_plan.get("total_expenditure") or 0
    )
    if close and close.get("total_burn"):
        default_burn = float(close["total_burn"])

    intake_kcal = float(intake.get("calories") or day_row.get("calories") or 0)
    burn_so_far = fuel_plan.get("burn_so_far")
    if burn_so_far is not None and float(burn_so_far) > 0:
        st.caption(
            f"Burn so far: **{float(burn_so_far):,.0f} kcal** · "
            f"Projected daily: **{default_burn:,.0f} kcal** · "
            f"Intake: **{intake_kcal:.0f} kcal**."
        )
    else:
        st.caption(
            f"Deficit = **Oura − FatSecret**. Intake: **{intake_kcal:.0f} kcal**."
        )

    default_weight = float(day_row.get("weight_lbs") or settings.get("current_weight_lbs") or 0)
    w_col, b_col = st.columns(2)
    with w_col:
        weight = st.number_input(
            "Weight (lb, optional)",
            min_value=0.0,
            value=default_weight,
            step=0.1,
            key=f"eod_weight_{log_day.isoformat()}",
        )
    with b_col:
        calories_burned = st.number_input(
            "Total calories burned (kcal, EOD)",
            min_value=0.0,
            value=default_burn,
            step=25.0,
            key=f"eod_burn_{log_day.isoformat()}",
            help="Oura total burn as reported. Do not add workout or remaining-step calories.",
        )
    if intake_kcal > 0 and calories_burned > 0:
        deficit_preview = calories_burned - intake_kcal
        if burn_so_far is not None and float(burn_so_far) > 0:
            st.caption(
                f"→ Deficit so far: **{float(burn_so_far) - intake_kcal:.0f} kcal** · "
                f"Projected EOD deficit: **{deficit_preview:.0f} kcal**"
            )
        else:
            st.caption(f"→ Deficit preview: **{deficit_preview:.0f} kcal** (burn − intake)")

    notes = st.text_input(
        "Notes (optional)",
        value=str(close.get("notes") or "") if close else "",
        key=f"eod_notes_{log_day.isoformat()}",
    )
    if st.button("Save day's log", key=f"eod_save_{log_day.isoformat()}", type="primary", use_container_width=True):
        save_daily_sync_day(
            log_day,
            settings,
            fuel_plan,
            intake={
                "calories": intake.get("calories"),
                "protein_g": intake.get("protein_g"),
                "carbs_g": intake.get("carbs_g"),
            },
            fuel_workout=fuel_workout,
            fuel_steps=fuel_steps,
            fuel_observed=fuel_observed,
            weight_lbs=weight if weight > 0 else None,
            calories_burned=calories_burned,
            notes=notes,
            workout_complete=workout_complete,
            step_goal=step_goal,
            oura_burn_so_far=oura_burn_so_far,
        )
        st.session_state.pop(f"eod_apply_burn_adj_{log_day.isoformat()}", None)
        st.success(f"Day saved for **{log_day.isoformat()}** — trends update on the History tab.")
        st.rerun()


def history_analysis_lines(hist, fc, settings, js):
    lines = []
    if hist.empty:
        return ["Log a day on Daily Sync (calories in/out, weight, sleep, workout) to build history."]

    logged = hist[hist["calories"].notna() & (hist["calories"] > 0)]
    finalized = hist[hist.get("day_finalized", False)] if "day_finalized" in hist.columns else pd.DataFrame()
    lines.append(f"**{len(logged)}** days with intake logged · **{len(finalized)}** saved days.")

    rollups = compute_deficit_rollups(hist)
    if rollups["total"] is not None:
        lines.append(
            f"Deficit — today **{_fmt_kcal(rollups['daily'])}** · week **{_fmt_kcal(rollups['weekly'])}** · "
            f"month **{_fmt_kcal(rollups['monthly'])}** · total **{_fmt_kcal(rollups['total'])}** kcal."
        )
    if rollups["avg_daily"] is not None:
        lines.append(f"Average daily deficit: **{rollups['avg_daily']:.0f} kcal**.")

    loss_per_day, loss_span = compute_avg_daily_weight_loss(hist, lookback_days=30)
    if loss_per_day is not None:
        lines.append(f"Average daily weight loss: **{loss_per_day:.3f} lb/day** over {loss_span} days.")

    workouts_7 = count_workouts_in_days(hist, 7)
    lines.append(
        f"Workouts this week: **{workouts_7}** (plan **{EXPECTED_WEEKLY_WORKOUTS[0]}–{EXPECTED_WEEKLY_WORKOUTS[1]}**/week)."
    )
    sleep_avg = average_sleep_score(hist, 7)
    if sleep_avg is not None:
        lines.append(f"Recent sleep: **{sleep_quality_from_score(sleep_avg)}** (avg score {sleep_avg:.0f}).")

    goal_bf = float(fc.get("goal_body_fat_pct") or settings.get("goal_body_fat_pct") or 10.0)
    fat_to_lose = float(fc.get("fat_to_lose") or 0)
    kcal_needed = float(fc.get("kcal_to_goal") or 0)
    cum = fc.get("cumulative_deficit_kcal")
    days_left = fc.get("days")
    if kcal_needed > 0 or fat_to_lose > 0:
        lines.append(
            f"**{fat_to_lose:.1f} lb** fat / **{kcal_needed:,.0f} kcal** remaining to **{goal_bf:.1f}%** body fat"
            f"{f' · **{int(round(days_left))} days** at current pace' if days_left is not None else ''}."
        )
        if cum is not None:
            lines.append(f"Cumulative deficit since DEXA: **{cum:,.0f} kcal**.")
    return lines


def render_history_trends_tab(daily, dexa, settings, fc):
    st.markdown("### History & Trends")
    st.caption(
        "Deficit = **Oura burn − FatSecret intake**. Oura is used as reported. "
        "Goal and ETA are from the latest DEXA plus cumulative deficit to your goal body-fat %."
    )
    hist = build_history_dataframe(daily, settings)
    js = get_or_create_journey_start(fc, settings, daily, dexa)

    for line in history_analysis_lines(hist, fc, settings, js):
        st.markdown(line)

    for note in analyze_cut_adjustments(hist, settings, current_weight=settings.get("current_weight_lbs")):
        body = f"**{note['title']}**  \n{note['body']}"
        if note["level"] == "warning":
            st.warning(body)
        elif note["level"] == "success":
            st.success(body)
        else:
            st.info(body)

    tab_trends, tab_log, tab_forecast = st.tabs(["Trend charts", "Day log editor", "Goal date history"])

    with tab_trends:
        if hist.empty:
            st.info("No history yet. Save a day on Daily Sync.")
        else:
            chart_df = hist.copy()
            chart_df["day"] = chart_df["log_date"].dt.date
            rollups = compute_deficit_rollups(hist)
            loss_per_day, _span = compute_avg_daily_weight_loss(hist, lookback_days=30)

            c1, c2, c3, c4 = st.columns(4)
            weight_rows = chart_df.dropna(subset=["weight_lbs"])
            c1.metric("Latest weight", f"{weight_rows.iloc[-1]['weight_lbs']:.1f} lb" if not weight_rows.empty else "—")
            c2.metric("Avg daily deficit", f"{rollups['avg_daily']:.0f}" if rollups["avg_daily"] is not None else "—")
            c3.metric("Avg daily loss", f"{loss_per_day:.3f} lb" if loss_per_day is not None else "—")
            c4.metric("Total deficit", _fmt_kcal(rollups["total"]))

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Today", _fmt_kcal(rollups["daily"]))
            r2.metric("Week", _fmt_kcal(rollups["weekly"]))
            r3.metric("Month", _fmt_kcal(rollups["monthly"]))
            r4.metric(
                "Fat to goal",
                f"{float(fc.get('fat_to_lose') or 0):.1f} lb",
            )

            st.markdown("**Weight**")
            w_chart = chart_df.dropna(subset=["weight_lbs"]).set_index("log_date")[["weight_lbs", "weight_7d_avg"]]
            if not w_chart.empty:
                st.line_chart(w_chart.rename(columns={"weight_lbs": "Daily", "weight_7d_avg": "7-day avg"}))
            else:
                st.caption("No weight entries yet.")

            st.markdown("**Calories in vs burned**")
            energy_df = chart_df.dropna(subset=["calories_burned"]).copy()
            energy_df = energy_df[energy_df["calories"].notna() & (energy_df["calories"] > 0)]
            if not energy_df.empty:
                e_chart = energy_df.set_index("log_date")[["calories", "calories_burned"]].rename(
                    columns={"calories": "Calories in", "calories_burned": "Calories burned"}
                )
                st.line_chart(e_chart)
            else:
                st.caption("Log calories consumed and burned to compare energy in vs out.")

            st.markdown("**Target deficit — days, weeks, cumulative**")
            render_deficit_pace_visuals(hist, settings, fc=fc, key_prefix="hist_defvis")

            if "sleep_score" in chart_df.columns:
                st.markdown("**Sleep quality**")
                sleep_chart = chart_df.dropna(subset=["sleep_score"]).set_index("log_date")[["sleep_score"]]
                if not sleep_chart.empty:
                    st.line_chart(sleep_chart.rename(columns={"sleep_score": "Sleep score"}))
                else:
                    st.caption("Log sleep quality on Daily Sync to see recovery trend.")

    with tab_log:
        st.caption("Edit past days. Fields: calories in, calories burned, weight, sleep, workout.")
        if hist.empty:
            st.info("No days to edit yet.")
        else:
            edit_df = hist.sort_values("log_date", ascending=False).head(60).copy()
            edit_df["date"] = edit_df["log_date"].dt.date.astype(str)
            if "sleep_score" in edit_df.columns:
                edit_df["sleep_quality"] = edit_df["sleep_score"].map(sleep_quality_from_score)
            else:
                edit_df["sleep_quality"] = "Good"
            display_cols = [
                "date", "weight_lbs", "calories", "calories_burned", "actual_deficit",
                "sleep_quality", "workout", "day_finalized",
            ]
            display_cols = [c for c in display_cols if c in edit_df.columns]
            editor_df = edit_df[display_cols].rename(
                columns={
                    "date": "Date",
                    "weight_lbs": "Weight",
                    "calories": "Calories in",
                    "calories_burned": "Calories burned",
                    "actual_deficit": "Deficit",
                    "sleep_quality": "Sleep",
                    "workout": "Workout",
                    "day_finalized": "Finalized",
                }
            )
            edited = st.data_editor(
                editor_df,
                num_rows="fixed",
                disabled=["Date", "Deficit", "Finalized"],
                column_config={
                    "Sleep": st.column_config.SelectboxColumn("Sleep", options=SLEEP_QUALITY_OPTIONS),
                    "Workout": st.column_config.SelectboxColumn("Workout", options=SIMPLE_DAILY_WORKOUTS),
                },
                key="history_day_editor",
                use_container_width=True,
            )
            if st.button("Save day log edits", type="primary", key="history_save_edits"):
                for _, row in edited.iterrows():
                    day_str = str(row["Date"])[:10]
                    log_day = date.fromisoformat(day_str)
                    cal_in = float(row["Calories in"]) if pd.notna(row.get("Calories in")) else None
                    cal_burn = float(row["Calories burned"]) if pd.notna(row.get("Calories burned")) else None
                    sleep_q = str(row["Sleep"]) if pd.notna(row.get("Sleep")) else "Good"
                    upsert_daily(
                        {
                            "log_date": day_str,
                            "weight_lbs": float(row["Weight"]) if pd.notna(row.get("Weight")) and row.get("Weight") else None,
                            "calories": cal_in,
                            "sleep_score": sleep_score_from_quality(sleep_q),
                            "workout": str(row["Workout"]) if pd.notna(row.get("Workout")) and row.get("Workout") else None,
                        },
                        source="Rebalance",
                        force=True,
                        data_ts=pd.Timestamp.now(),
                    )
                    if row.get("Workout"):
                        save_fuel_workout_for_date(log_day, str(row["Workout"]))
                    close = get_daily_day_close(log_day) or {
                        "log_date": day_str,
                        "finalized": 1,
                        "target_deficit": float(settings.get("target_deficit") or 500),
                    }
                    close.update(
                        {
                            "weight_lbs": float(row["Weight"]) if pd.notna(row.get("Weight")) and row.get("Weight") else close.get("weight_lbs"),
                            "calories": cal_in if cal_in is not None else close.get("calories"),
                            "workout": str(row["Workout"]) if pd.notna(row.get("Workout")) and row.get("Workout") else close.get("workout"),
                            "total_burn": cal_burn if cal_burn is not None else close.get("total_burn"),
                            "projected_deficit": (cal_burn - cal_in) if cal_burn and cal_in else close.get("projected_deficit"),
                            "finalized_at": datetime.now().isoformat(timespec="seconds"),
                            "notes": (close.get("notes") or "") + " · edited on History tab",
                        }
                    )
                    save_daily_day_close(close)
                st.success("Day log updated.")
                st.rerun()

    with tab_forecast:
        goal_hist = load_goal_history()
        if goal_hist.empty:
            st.info("Goal date snapshots appear after you use the app for a few days.")
        else:
            st.caption("How your predicted goal date has moved over time.")
            chart = goal_hist.set_index("snapshot_date")[["days_remaining"]]
            st.line_chart(chart.rename(columns={"days_remaining": "Days to goal"}))
            st.dataframe(
                goal_hist.assign(
                    goal_date=goal_hist["goal_date"].dt.date,
                    snapshot_date=goal_hist["snapshot_date"].dt.date,
                ),
                use_container_width=True,
                hide_index=True,
            )


def render_snack_gap_picker(fuel_plan, key_prefix="ds_snack", nested=False, fuel_day=None):
    """Optional snack planner — list all choices and let the user mix freely."""
    if not fuel_plan.get("has_fatsecret"):
        return
    direction = fuel_plan.get("adjustment_direction")
    kcal_gap = float(fuel_plan.get("calorie_adjustment") or 0)
    if direction != "increase" or kcal_gap <= 5:
        return

    if fuel_day is None:
        fuel_day = st.session_state.get("fuel_planner_date", date.today())
    if isinstance(fuel_day, str):
        fuel_day = date.fromisoformat(fuel_day[:10])
    elif hasattr(fuel_day, "date"):
        fuel_day = fuel_day.date()

    day_key = fuel_day.isoformat()
    dismiss_key = f"{key_prefix}_gap_dismiss_{day_key}"
    enabled_key = f"{key_prefix}_gap_enabled_{day_key}"
    snack_options = list(FREQUENT_SNACK_PRESETS.keys())

    def _body():
        if st.session_state.get(dismiss_key):
            st.caption("Snack planner hidden for today.")
            if st.button("Show snack planner", key=f"{key_prefix}_gap_undismiss_{day_key}"):
                st.session_state.pop(dismiss_key, None)
                st.session_state.pop(enabled_key, None)
                st.rerun()
            return

        if not st.session_state.get(enabled_key):
            st.caption(
                f"You have **{kcal_gap:.0f} kcal room** before today's deficit target. "
                "Planning extra snacks is completely optional."
            )
            open_col, skip_col = st.columns(2)
            with open_col:
                if st.button("Open snack planner", key=f"{key_prefix}_gap_open_{day_key}"):
                    st.session_state[enabled_key] = True
                    st.rerun()
            with skip_col:
                if st.button("Skip for today", key=f"{key_prefix}_gap_skip_{day_key}"):
                    st.session_state[dismiss_key] = True
                    st.rerun()
            return

        st.caption(
            f"**Gap before snacks: {kcal_gap:.0f} kcal** — pick portions below to see what's left."
        )

        selections = []
        for snack_id in snack_options:
            label = FREQUENT_SNACK_PRESETS[snack_id]["label"]
            portion_key = f"{key_prefix}_gap_{snack_id}_{day_key}"
            portion_label, min_v, max_v, step = gap_portion_field_spec(snack_id)
            if portion_key not in st.session_state:
                st.session_state[portion_key] = 0.0 if snack_id == "krispies_milk" else 0

            label_col, input_col = st.columns([1.55, 1.0])
            with label_col:
                hint = gap_snack_rate_hint(snack_id)
                st.markdown(f"**{label}**")
                if hint:
                    st.caption(hint)
            with input_col:
                if snack_id == "krispies_milk":
                    portion = st.number_input(
                        portion_label,
                        min_value=float(min_v),
                        max_value=float(max_v),
                        step=float(step),
                        key=portion_key,
                        label_visibility="collapsed",
                    )
                else:
                    portion = st.number_input(
                        portion_label,
                        min_value=int(min_v),
                        max_value=int(max_v),
                        step=int(step),
                        key=portion_key,
                        label_visibility="collapsed",
                    )

            slot_kcal = snack_portion_kcal(snack_id, portion)
            if float(portion or 0) > 0:
                st.caption(
                    f"→ {format_snack_portion_line(snack_id, portion)} · **+{slot_kcal:.0f} kcal**"
                )
            selections.append(
                {"snack_id": snack_id, "portion": portion, "kcal": slot_kcal}
            )

        total_added = sum(float(slot["kcal"] or 0) for slot in selections)
        gap_remaining = kcal_gap - total_added
        gap_after = max(0.0, gap_remaining)
        over_by = max(0.0, -gap_remaining)

        st.markdown("#### Gap tracker")
        if kcal_gap > 0 and total_added > 0:
            st.progress(min(1.0, total_added / kcal_gap))

        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Gap before snacks",
            f"{kcal_gap:.0f} kcal",
            help="Calorie room before any snacks in this planner.",
        )
        m2.metric(
            "Snacks planned",
            f"+{total_added:.0f} kcal",
            help="Total calories from your selections above.",
        )
        if over_by > 5:
            m3.metric(
                "Gap after snacks",
                "0 kcal",
                delta=f"{over_by:.0f} over",
                delta_color="inverse",
                help="Your snacks exceed the gap — that's fine if intentional.",
            )
        elif gap_after <= 12 and total_added > 0:
            m3.metric(
                "Gap after snacks",
                f"{gap_after:.0f} kcal",
                delta="Gap closed",
                delta_color="normal",
                help="Within ~12 kcal of closing the gap.",
            )
        else:
            m3.metric(
                "Gap after snacks",
                f"{gap_after:.0f} kcal",
                delta=f"-{total_added:.0f}" if total_added > 0 else None,
                delta_color="normal",
                help="Calorie room left after your planned snacks.",
            )

        if total_added > 0:
            if over_by > 5:
                st.markdown(
                    f"`{kcal_gap:.0f}` before − `{total_added:.0f}` snacks = "
                    f"**{over_by:.0f} kcal over** the gap"
                )
            else:
                st.markdown(
                    f"`{kcal_gap:.0f}` before − `{total_added:.0f}` snacks = "
                    f"**{gap_after:.0f} kcal left**"
                )
                if gap_after > 12:
                    st.caption(f"→ Add about **{gap_after:.0f} kcal** more to close the gap.")
        else:
            st.caption("No snacks selected yet — gap unchanged.")

        active = [slot for slot in selections if float(slot.get("portion") or 0) > 0]
        if len(active) > 1:
            st.markdown("**Your mix**")
            for idx, slot in enumerate(active, start=1):
                st.markdown(
                    f"{idx}. {format_snack_portion_line(slot['snack_id'], slot['portion'])} "
                    f"(+{slot['kcal']:.0f} kcal)"
                )

        hide_col, _ = st.columns([1, 3])
        with hide_col:
            if st.button("Hide for today", key=f"{key_prefix}_gap_hide_{day_key}"):
                st.session_state[dismiss_key] = True
                st.rerun()

        quick_adds = fuel_plan.get("food_plan") or []
        if quick_adds:
            with st.expander("Example mix (optional)", expanded=False):
                st.caption("One possible combination — use as inspiration, not a requirement.")
                for step in quick_adds[:6]:
                    st.markdown(f"- {step}")

    title = f"Optional snack planner ({kcal_gap:.0f} kcal room)"
    if nested:
        with st.expander(title, expanded=False):
            _body()
    else:
        with st.container(border=True):
            st.markdown(f"##### {title}")
            _body()
init_db()
seed_import_provenance_once()

if os.environ.get("TELLUM_HEADLESS_SYNC") == "1":
    sync_summary, import_summary = run_startup_health_data_pipeline(wait_for_drive=False)
    print(json.dumps({
        "sync": {
            "copied": (sync_summary or {}).get("copied"),
            "skipped": (sync_summary or {}).get("skipped"),
            "failed": (sync_summary or {}).get("failed"),
            "files": (sync_summary or {}).get("files"),
        },
        "import": {
            "found": (import_summary or {}).get("found"),
            "imported": (import_summary or {}).get("imported"),
            "skipped": (import_summary or {}).get("skipped"),
            "failed": (import_summary or {}).get("failed"),
            "files": (import_summary or {}).get("files"),
        },
        "caption": format_startup_sync_caption(sync_summary, import_summary),
    }, default=str))
    raise SystemExit(0)

if "startup_source_sync_summary" not in st.session_state:
    with st.spinner("Checking Google Drive Health Data for new documents…"):
        sync_summary, import_summary = run_startup_health_data_pipeline()
    st.session_state.startup_source_sync_summary = sync_summary
    st.session_state.startup_import_summary = import_summary
    st.session_state.classification_reclassify_summary = None
    st.session_state.startup_import_done = True
    st.session_state.ocr_daily_sync_summary = {}
    st.session_state.startup_sync_notice = format_startup_sync_caption(sync_summary, import_summary)

_daily_prefetch = load_daily()
_dexa_prefetch = load_dexa()
s = load_persisted_settings()
s, _setting_sources = apply_startup_import_overrides(s, _daily_prefetch, _dexa_prefetch)
_latest_weight_candidate = best_imported_weight_candidate(_daily_prefetch, _dexa_prefetch)

if "fuel_planner_date" not in st.session_state:
    st.session_state.fuel_planner_date = get_fuel_planner_date()
else:
    _persisted_fuel_day = get_fuel_planner_date()
    if _persisted_fuel_day > st.session_state.fuel_planner_date:
        st.session_state.fuel_planner_date = _persisted_fuel_day

if "main_nav_tab" not in st.session_state:
    st.session_state.main_nav_tab = 0


def main_tab_labels():
    return ["🎯 Command", "🔄 Daily Sync", "📈 History"]


def render_sidebar_setting(key, label, s, latest_weight_candidate=None):
    step = 0.05 if key == "fat_loss_fraction" else 0.5
    value = st.number_input(label, value=float(s[key]), step=step, key=f"sidebar_{key}")
    if value != s[key]:
        save_setting(key, value)
        if key == "current_weight_lbs":
            save_text_setting("current_weight_manual_override", "1")
            save_text_setting("current_weight_source", "Manual Override")
        elif key == "current_body_fat_pct":
            save_text_setting("current_body_fat_manual_override", "1")
            save_text_setting("current_body_fat_source", "Manual Override")
        s[key] = value
    if key in IMPORT_OVERRIDABLE_SETTINGS:
        st.caption(f"Source: {setting_field_source(key)}")
    if key == "current_weight_lbs" and latest_weight_candidate:
        if st.button("Use latest imported weight", key="sync_latest_imported_weight"):
            save_weight_from_import(
                _latest_weight_candidate["weight"],
                _latest_weight_candidate["source"],
                _latest_weight_candidate["priority"],
                _latest_weight_candidate["ts"],
                clear_manual=True,
            )
            s["current_weight_lbs"] = float(_latest_weight_candidate["weight"])
            st.rerun()
    return s


st.markdown(classic_app_theme_css(), unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align:center;padding:8px 0 4px 0;'>"
    f"<span style='font-family:Cinzel,Georgia,serif;font-size:28px;font-weight:900;color:#08245c;'>"
    f"{APP_NAME}</span><br/>"
    f"<span style='font-size:13px;color:#6b7280;font-style:italic;'>{MOTTO}</span></div>",
    unsafe_allow_html=True,
)

daily = load_daily()
dexa = load_dexa()
if get_text_setting("goal_weight_migrated_165", "") != "1":
    save_text_setting("goal_weight_lbs", str(GOAL_WEIGHT_AT_10PCT_BF))
    save_text_setting("goal_weight_migrated_165", "1")
repair_corrupt_dexa_scans()
backfill_composition_calibration(dexa, daily, s)
_anchor, fc = forecast_goal(daily, dexa, s)
fc = apply_manual_overrides_to_forecast(fc, s)
save_goal_snapshot(fc)
momentum = goal_date_momentum(fc)

_sync_notice = st.session_state.get("startup_sync_notice") or ""
if _sync_notice:
    copied = int((st.session_state.get("startup_source_sync_summary") or {}).get("copied") or 0)
    imported = int((st.session_state.get("startup_import_summary") or {}).get("imported") or 0)
    if copied or imported:
        st.success(_sync_notice)
    elif "not found" in _sync_notice.lower():
        st.warning(_sync_notice)
    else:
        st.caption(_sync_notice)

with st.sidebar:
    st.header("Settings")
    snap1, snap2 = st.columns(2)
    snap1.metric("Est. BF", f"{float(fc.get('current_bf') if fc.get('current_bf') is not None else s['current_body_fat_pct']):.1f}%")
    snap2.metric("Goal BF", f"{float(s['goal_body_fat_pct']):.1f}%")
    st.caption(
        f"DEXA lean held constant → **{goal_weight_lbs(s, fc):.1f} lb** at goal. "
        f"Live weight **{float(fc.get('scale_weight') or s.get('current_weight_lbs') or 0):.1f} lb**. "
        "Deficit = Oura − FatSecret."
    )

    with st.expander("Campaign targets", expanded=True):
        goal_bf = st.number_input(
            "Goal body fat %",
            min_value=5.0,
            max_value=25.0,
            value=float(s["goal_body_fat_pct"]),
            step=0.1,
            key="sidebar_goal_body_fat_pct",
            help="Default 10%. Time to complete uses cumulative deficit from the latest DEXA.",
        )
        if abs(goal_bf - float(s["goal_body_fat_pct"])) > 0.001:
            save_setting("goal_body_fat_pct", float(goal_bf))
            s["goal_body_fat_pct"] = float(goal_bf)
            st.rerun()
        st.caption(
            f"At DEXA lean mass this is **{goal_weight_lbs(s, fc):.1f} lb**. "
            f"**{float(fc.get('fat_to_lose') or 0):.1f} lb** fat / "
            f"**{float(fc.get('kcal_to_goal') or 0):,.0f} kcal** remaining."
        )
        s = render_sidebar_setting("target_deficit", "Planned daily deficit (if no history yet)", s, _latest_weight_candidate)

    with st.expander("Google Drive Health Data", expanded=False):
        health_folder = get_health_data_source_folder()
        st.caption(f"`{health_folder}`")
        folder_input = st.text_input(
            "Health Data folder",
            value=str(health_folder),
            key="health_data_source_folder_setting",
            help="Local Google Drive for Desktop path. New screenshots and exports are copied into TU Inbox and imported on startup.",
        )
        if folder_input and folder_input != str(health_folder):
            save_text_setting("health_data_source_folder_path", folder_input)
        st.caption(
            st.session_state.get("startup_sync_notice")
            or "Checked on each app launch."
        )
        if st.button("Sync Google Drive now", use_container_width=True, key="manual_gdrive_health_sync"):
            with st.spinner("Checking Google Drive Health Data for new documents…"):
                sync_summary, import_summary = run_startup_health_data_pipeline()
            st.session_state.startup_source_sync_summary = sync_summary
            st.session_state.startup_import_summary = import_summary
            st.session_state.startup_sync_notice = format_startup_sync_caption(sync_summary, import_summary)
            st.rerun()

    render_dexa_milestone_entry(dexa, s, fc, daily)

tab_labels = main_tab_labels()
main_nav_tab = st.radio(
    "Navigation",
    range(len(tab_labels)),
    format_func=lambda i: tab_labels[i],
    horizontal=True,
    key="main_nav_radio",
    label_visibility="collapsed",
)
st.session_state.main_nav_tab = main_nav_tab

if main_nav_tab == 0:
    st.markdown(command_center_tab_css() + '<div class="cc-page-marker"></div>', unsafe_allow_html=True)
    render_mission_command_center(s, daily=daily, dexa=dexa, fc=fc, momentum=momentum)
    st.caption(
        f"Progress and time-to-goal from **DEXA + cumulative deficit** (Oura burn as reported − FatSecret intake). "
        f"**{forecast_source_label(fc)}**."
    )

if main_nav_tab == 1:
    st.markdown(daily_sync_styles_html(), unsafe_allow_html=True)
    fuel_day = st.session_state.fuel_planner_date
    if isinstance(fuel_day, str):
        fuel_day = date.fromisoformat(fuel_day[:10])
    elif hasattr(fuel_day, "date"):
        fuel_day = fuel_day.date()

    ds_main, ds_side = st.columns([1.55, 1.0])
    with ds_side:
        st.markdown('<div class="ds-sync-page-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="ds-sync-side-title">Daily Sync</div>', unsafe_allow_html=True)
        picked_day = st.date_input(
            "Log date",
            value=fuel_day,
            max_value=date.today(),
            key="ds_log_date_pick",
        )
        if picked_day != fuel_day:
            st.session_state.fuel_planner_date = picked_day
            save_text_setting("fuel_planner_date", picked_day.isoformat())
            st.rerun()
        fuel_day = picked_day
        day_rows = daily[daily["log_date"].dt.date == fuel_day] if not daily.empty else pd.DataFrame()
        day_row = day_rows.iloc[0].to_dict() if not day_rows.empty else {}
        live_log = render_simple_cut_day_form(fuel_day, s, daily, day_row=day_row)

    with ds_main:
        hist = build_history_dataframe(daily, s)
        render_deficit_tracker_panel(hist, s, live=live_log, fc=fc)

if main_nav_tab == 2:
    render_history_trends_tab(daily, dexa, s, fc)
