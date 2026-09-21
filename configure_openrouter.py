#!/usr/bin/env python3
from __future__ import annotations
import getpass, os
from pathlib import Path


def main():
    key=getpass.getpass("OpenRouter API key (input hidden): ").strip()
    if not key:
        raise SystemExit("No key entered")
    referer=input("HTTP-Referer [https://www.jeremycanale.com]: ").strip() or "https://www.jeremycanale.com"
    title=input("X-Title [DGF-Bench]: ").strip() or "DGF-Bench"
    p=Path(__file__).resolve().parent/".env"
    p.write_text(f"OPENROUTER_API_KEY={key}\nOPENROUTER_HTTP_REFERER={referer}\nOPENROUTER_X_TITLE={title}\n",encoding="utf-8")
    try: os.chmod(p,0o600)
    except Exception: pass
    print(f"Saved OpenRouter configuration to {p}. The file is gitignored.")

if __name__=="__main__": main()
