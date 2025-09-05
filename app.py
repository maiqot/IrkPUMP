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
    
    def get_pump_count() -> int:
        """Get total number of pumps."""
        return pump_manager.get_pump_count()
    
    def search_pumps(query: str) -> list:
        """Search pumps by model or manufacturer."""
        return pump_manager.search_pumps(query)
    
    def clear_pumps() -> bool:
        """Clear all pumps."""
        pump_manager.clear_pumps()
        return True
    
    def export_to_text(output_path: str) -> bool:
        """Export pumps to text file."""
        return pump_manager.export_to_text(output_path)
    
    def create_sample_excel() -> str:
        """Create sample Excel file and return path."""
        sample_path = pump_manager.catalog_dir / "sample_pumps.xlsx"
        from pump_manager import create_sample_excel
        create_sample_excel(str(sample_path))
        return str(sample_path)
    
    def get_catalog_files() -> list:
        """Get list of Excel files in catalog directory."""
        from pump_manager import get_catalog_files
        return get_catalog_files(pump_manager.catalog_dir)
    
    def get_catalog_path() -> str:
        """Get catalog directory path."""
        return str(pump_manager.catalog_dir)
    
    return {
        'importPumpsFromExcel': import_pumps_from_excel,
        'getPumps': get_pumps,
        'getPumpCount': get_pump_count,
        'searchPumps': search_pumps,
        'clearPumps': clear_pumps,
        'exportToText': export_to_text,
        'createSampleExcel': create_sample_excel,
        'getCatalogFiles': get_catalog_files,
        'getCatalogPath': get_catalog_path
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


