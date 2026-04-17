#!/usr/bin/env python3
"""
PCTO Manager — Launcher
Doppio click su questo file per avviare il sito!
"""
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("📦 Controllo dipendenze...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

print("🚀 Avvio PCTO Manager...")
subprocess.call([sys.executable, "server.py"])
