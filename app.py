import sys
from pathlib import Path

import webview


def get_app_title() -> str:
    return "IrkPUMP"


def get_html_uri() -> str:
    html_path = Path(__file__).parent / "IrkPUMP v6.html"
    return html_path.resolve().as_uri()


def main() -> None:
    window = webview.create_window(get_app_title(), url=get_html_uri())
    webview.start()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to start IrkPUMP: {exc}", file=sys.stderr)
        raise


