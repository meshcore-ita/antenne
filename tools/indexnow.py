"""Notifica IndexNow (Bing, Yandex, Seznam, Naver) delle pagine della galleria cambiate.

Uso:
  python tools/indexnow.py <sha-precedente> <sha-attuale>
  python tools/indexnow.py --all

La chiave è quella del sito principale: è il nome del file <chiave>.txt alla
radice del repo meshcore-ita.github.io, pubblicato su https://meshcore-ita.github.io/.
Lo script la legge da lì a ogni esecuzione (API pubblica di GitHub) e controlla
che il file sia online: così non c'è una seconda copia da tenere allineata.
Non fa mai fallire il workflow: ogni errore viene solo stampato.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

SITE = "https://meshcore-ita.github.io/"
BASE = SITE + "antenne/"
SITE_REPO_API = "https://api.github.com/repos/meshcore-ita/meshcore-ita.github.io/contents/"
ENDPOINT = "https://api.indexnow.org/IndexNow"
ROOT = Path(__file__).resolve().parent.parent


def antenna_slugs():
    return sorted(p.name for p in (ROOT / "antenne").iterdir() if (p / "antenna.nec").exists())


def all_urls():
    return [BASE, BASE + "guida/"] + [f"{BASE}{s}/" for s in antenna_slugs()]


def changed_urls(before, after):
    if not before or not after or set(before) == {"0"}:
        return []
    files = subprocess.run(["git", "diff", "--name-only", before, after], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()
    urls = set()
    for f in files:
        parts = f.split("/")
        if parts[0] == "antenne" and len(parts) > 2:
            if (ROOT / "antenne" / parts[1] / "antenna.nec").exists():
                urls.add(f"{BASE}{parts[1]}/")
            urls.add(BASE)                        # la tabella dell'indice cambia
        elif parts[0] == "docs":
            urls.add(BASE + "guida/")
        elif parts[0] == "tools" or f == "requirements.txt":
            return all_urls()                     # cambia l'aspetto o i calcoli di tutte le pagine
    return sorted(urls)


def main():
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    urls = all_urls() if a == "--all" else changed_urls(a, sys.argv[2] if len(sys.argv) > 2 else "")
    if not urls:
        print("IndexNow: nessuna pagina cambiata, niente da inviare.")
        return
    try:
        req = urllib.request.Request(SITE_REPO_API, headers={"accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            names = [f["name"] for f in json.load(r)]
        key = next((n[:-4] for n in names if re.fullmatch(r"[0-9a-f]{32}\.txt", n)), None)
        if not key:
            print("IndexNow: nessun file <chiave>.txt nel repo del sito, salto l'invio.")
            return
        with urllib.request.urlopen(f"{SITE}{key}.txt", timeout=10) as r:
            if r.read().decode().strip() != key:
                print("IndexNow: la chiave pubblicata sul sito non corrisponde, salto l'invio.")
                return
        body = json.dumps({"host": "meshcore-ita.github.io", "key": key,
                           "keyLocation": f"{SITE}{key}.txt", "urlList": urls}).encode()
        req = urllib.request.Request(ENDPOINT, data=body,
                                     headers={"content-type": "application/json; charset=utf-8"})
        with urllib.request.urlopen(req, timeout=20) as r:
            status = r.status
    except Exception as e:  # noqa: BLE001
        print(f"IndexNow: errore {e}")
        return
    print(f"IndexNow: {status} per {len(urls)} URL")
    for u in urls:
        print(f"  {u}")


if __name__ == "__main__":
    main()
