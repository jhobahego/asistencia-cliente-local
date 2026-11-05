"""Convert CSV files into GitHub-flavored Markdown tables.

Run from the repository root with any Python 3.10+ interpreter:

    python scripts/csv_to_markdown.py data.csv
    python scripts/csv_to_markdown.py data.csv -o data.md
    cat data.csv | python scripts/csv_to_markdown.py -

Only the standard library is used, so no virtual environment is required.

Behavior:
- The delimiter is detected with ``csv.Sniffer`` and can be forced with
  ``--delimiter``. Detection falls back to a comma when it is ambiguous.
- The first row is treated as the header unless ``--no-header`` is given; in
  that case generic ``Column N`` headers are generated.
- Pipes are escaped and line breaks inside cells become ``<br>`` so the table
  never breaks. Ragged rows are padded and reported on stderr.
- Input defaults to ``utf-8-sig`` (handles Excel BOMs); output is ``utf-8``.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

DEFAULT_ENCODING = "utf-8-sig"
STDIN_MARKER = "-"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a CSV file into a GitHub-flavored Markdown table.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        help="CSV file to read, or '-' to read from stdin.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=STDIN_MARKER,
        help="Markdown file to write, or '-' for stdout (default: stdout).",
    )
    parser.add_argument(
        "--delimiter",
        default=None,
        help="Field delimiter. Detected automatically when omitted.",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Treat the first row as data and generate generic headers.",
    )
    parser.add_argument(
        "--align",
        choices=("none", "left", "center", "right"),
        default="none",
        help="Column alignment applied to every column (default: none).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional Markdown heading placed before the table.",
    )
    parser.add_argument(
        "--encoding",
        default=DEFAULT_ENCODING,
        help=f"Input encoding (default: {DEFAULT_ENCODING}).",
    )
    return parser


def _read_text(path: str, encoding: str) -> str:
    if path == STDIN_MARKER:
        return sys.stdin.read()
    return Path(path).read_text(encoding=encoding)


def _read_rows(text: str, delimiter: str | None) -> tuple[list[str], list[list[str]]]:
    if not text.strip():
        return [], []

    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        detected = delimiter or dialect.delimiter
    except csv.Error:
        detected = delimiter or ","

    reader = csv.reader(io.StringIO(text), delimiter=detected)
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        return [], []

    header = rows[0]
    body = rows[1:]
    return header, body


def _escape_cell(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>").replace("|", "\\|")


def _normalize_width(header: list[str], body: list[list[str]]) -> tuple[list[str], list[list[str]], bool]:
    width = max([len(header), *(len(row) for row in body)]) if body else len(header)
    ragged = any(len(row) != width for row in body) or len(header) != width

    header = header + [f"Column {index}" for index in range(len(header) + 1, width + 1)]
    body = [row + [""] * (width - len(row)) for row in body]
    return header, body, ragged


def _separator(width: int, align: str) -> str:
    cells = {
        "none": "---",
        "left": ":---",
        "center": ":---:",
        "right": "---:",
    }[align]
    return "| " + " | ".join([cells] * width) + " |"


def _render_table(header: list[str], body: list[list[str]], align: str) -> str:
    lines = [
        "| " + " | ".join(_escape_cell(cell) for cell in header) + " |",
        _separator(len(header), align),
    ]
    lines.extend(
        "| " + " | ".join(_escape_cell(cell) for cell in row) + " |" for row in body
    )
    return "\n".join(lines) + "\n"


def convert(
    text: str,
    *,
    delimiter: str | None = None,
    has_header: bool = True,
    align: str = "none",
    title: str | None = None,
    warn=None,
) -> str:
    header, body = _read_rows(text, delimiter)
    if not header:
        return f"# {title}\n\n_(empty table)_\n" if title else "_(empty table)_\n"

    if not has_header:
        body = [header, *body]
        header = [f"Column {index}" for index in range(1, len(header) + 1)]

    header, body, ragged = _normalize_width(header, body)
    if ragged and warn is not None:
        warn("warning: rows have inconsistent column counts; padded with empty cells")

    table = _render_table(header, body, align)
    if title:
        return f"# {title}\n\n{table}"
    return table


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        text = _read_text(args.input, args.encoding)
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as exc:
        print(
            f"error: input is not valid {args.encoding}; try --encoding utf-8: {exc}",
            file=sys.stderr,
        )
        return 1

    markdown = convert(
        text,
        delimiter=args.delimiter,
        has_header=not args.no_header,
        align=args.align,
        title=args.title,
        warn=lambda message: print(message, file=sys.stderr),
    )

    if args.output == STDIN_MARKER:
        sys.stdout.write(markdown)
        return 0

    try:
        Path(args.output).write_text(markdown, encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot write output: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
