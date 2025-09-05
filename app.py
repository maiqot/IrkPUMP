import sys
from pathlib import Path

import webview

from pump_manager import PumpManager
from calc_engine import run_calculation


def get_app_title() -> str:
    return "IrkPUMP"


def get_html_uri() -> str:
    html_path = Path(__file__).parent / "IrkPUMP v6.html"
    return html_path.resolve().as_uri()


class Api:
    """API exposed to the webview as window.pywebview.api"""

    def __init__(self) -> None:
        self.pump_manager = PumpManager()

    # Data accessors
    def importPumpsFromExcel(self, file_path: str) -> dict:  # noqa: N802 (pywebview expects camelCase)
        return self.pump_manager.import_from_excel(file_path)

    def getPumps(self) -> list:  # noqa: N802
        return self.pump_manager.get_pumps()

    def getPumpCount(self) -> int:  # noqa: N802
        return self.pump_manager.get_pump_count()

    def searchPumps(self, query: str) -> list:  # noqa: N802
        return self.pump_manager.search_pumps(query)

    def clearPumps(self) -> bool:  # noqa: N802
        self.pump_manager.clear_pumps()
        return True

    def exportToText(self, output_path: str) -> bool:  # noqa: N802
        return self.pump_manager.export_to_text(output_path)

    # Catalog helpers
    def createSampleExcel(self) -> str:  # noqa: N802
        from pump_manager import create_sample_excel

        sample_path = self.pump_manager.catalog_dir / "sample_pumps.xlsx"
        create_sample_excel(str(sample_path))
        return str(sample_path)

    def getCatalogFiles(self) -> list:  # noqa: N802
        from pump_manager import get_catalog_files

        return get_catalog_files(self.pump_manager.catalog_dir)

    def getCatalogPath(self) -> str:  # noqa: N802
        return str(self.pump_manager.catalog_dir)

    # Calculation entrypoint
    def runFullCalculation(self, params: dict) -> dict:  # noqa: N802
        result = run_calculation(params)
        return {
            'ok': result.ok,
            'message': result.message,
            'echo': result.echo,
        }


def main() -> None:
    api = Api()
    window = webview.create_window(
        get_app_title(), 
        url=get_html_uri(),
        js_api=api
    )
    webview.start(debug=False)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to start IrkPUMP: {exc}", file=sys.stderr)
        raise


