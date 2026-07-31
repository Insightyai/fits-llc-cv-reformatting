import argparse
import json
import os
import sys
import time
from datetime import date

from agent import TransformError, transform
from extract import ExtractionError, extract_text


def main():
    parser = argparse.ArgumentParser(
        description="Transforma un CV (PDF/DOCX/texto) al JSON canonico de cv-schema.json"
    )
    parser.add_argument("archivo", help="ruta al CV")
    parser.add_argument("--out", help="ruta de salida del JSON (default: stdout)")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY no esta seteada", file=sys.stderr)
        sys.exit(1)

    with open(args.archivo, "rb") as f:
        data = f.read()

    t0 = time.monotonic()

    try:
        extracted = extract_text(os.path.basename(args.archivo), data)
    except ExtractionError as exc:
        print(f"EXTRACCION FALLIDA [{exc.code}]: {exc.detail}", file=sys.stderr)
        sys.exit(1)

    try:
        cv, usage, state = transform(extracted.text, date.today(), api_key=api_key)
    except TransformError as exc:
        print(f"TRANSFORMACION FALLIDA [{exc.code}]: {exc.detail}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.monotonic() - t0
    output = json.dumps(cv, indent=2, ensure_ascii=False)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)

    print(f"\n--- {elapsed:.1f}s, estado={state}, usage={usage} ---", file=sys.stderr)
    warnings = cv["_meta"]["warnings"]
    if warnings:
        print("--- warnings ---", file=sys.stderr)
        for w in warnings:
            print(f"  {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
