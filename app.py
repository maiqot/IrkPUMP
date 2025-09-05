import sys
from pathlib import Path

import webview

from pump_manager import PumpManager


def get_app_title() -> str:
    return "IrkPUMP"


def get_html_uri() -> str:
    html_path = Path(__file__).parent / "IrkPUMP v6.html"
    return html_path.resolve().as_uri()


def create_api() -> dict:
    """Create API object for JavaScript bridge."""
    pump_manager = PumpManager()
    
    def import_pumps_from_excel(file_path: str) -> dict:
        """Import pumps from Excel file."""
        return pump_manager.import_from_excel(file_path)
    
    def get_pumps() -> list:
        """Get all pumps."""
        return pump_manager.get_pumps()
    
    def create_sample_excel() -> str:
        """Create sample Excel file and return path."""
        sample_path = Path(__file__).parent / "sample_pumps.xlsx"
        from pump_manager import create_sample_excel
        create_sample_excel(str(sample_path))
        return str(sample_path)
    
    return {
        'importPumpsFromExcel': import_pumps_from_excel,
        'getPumps': get_pumps,
        'createSampleExcel': create_sample_excel
    }


def main() -> None:
    api = create_api()
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


