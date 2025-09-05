"""
Pump management module for IrkPUMP.
Handles pump data import from Excel and data persistence.
"""

import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class PumpManager:
    """Manages pump data import and export operations."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize pump manager.
        
        Args:
            data_dir: Directory to store pump data files. Defaults to current directory.
        """
        self.data_dir = data_dir or Path(__file__).parent
        self.catalog_dir = self.data_dir / "catalog"
        self.catalog_dir.mkdir(exist_ok=True)
        self.pumps_file = self.data_dir / "pumps.pkl"
        self.pumps: List[Dict[str, Any]] = []
        self.load_pumps()
    
    def load_pumps(self) -> None:
        """Load pumps from pickle file."""
        if self.pumps_file.exists():
            try:
                with open(self.pumps_file, 'rb') as f:
                    self.pumps = pickle.load(f)
            except (pickle.PickleError, IOError) as e:
                print(f"Error loading pumps: {e}", file=sys.stderr)
                self.pumps = []
        else:
            self.pumps = []
    
    def save_pumps(self) -> None:
        """Save pumps to pickle file."""
        try:
            with open(self.pumps_file, 'wb') as f:
                pickle.dump(self.pumps, f)
        except IOError as e:
            print(f"Error saving pumps: {e}", file=sys.stderr)
    
    def import_from_excel(self, excel_path: str) -> Dict[str, Any]:
        """Import pumps from Excel file.
        
        Expected Excel columns:
        - model: Pump model name
        - nominal_q_m3: Nominal flow rate (m³/day)
        - min_q_m3: Minimum flow rate (m³/day)
        - max_q_m3: Maximum flow rate (m³/day)
        - nominal_head_m: Nominal head (m)
        - min_head_m: Minimum head (m)
        - max_head_m: Maximum head (m)
        - nominal_power_kw: Nominal power (kW)
        - efficiency: Efficiency (%)
        - stages: Number of stages
        - manufacturer: Manufacturer name
        - notes: Additional notes
        
        Args:
            excel_path: Path to Excel file (can be relative to catalog dir or absolute)
            
        Returns:
            Dict with import results: {'success': bool, 'imported': int, 'errors': List[str]}
        """
        try:
            # Handle both absolute and relative paths
            if not Path(excel_path).is_absolute():
                # Try catalog directory first, then current directory
                catalog_path = self.catalog_dir / excel_path
                if catalog_path.exists():
                    excel_path = str(catalog_path)
                else:
                    # Try current directory
                    current_path = self.data_dir / excel_path
                    if current_path.exists():
                        excel_path = str(current_path)
                    else:
                        return {
                            'success': False,
                            'imported': 0,
                            'errors': [f"File not found: {excel_path}"]
                        }
            
            # Read Excel file
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # Required columns
            required_cols = [
                'model', 'nominal_q_m3', 'min_q_m3', 'max_q_m3',
                'nominal_head_m', 'min_head_m', 'max_head_m',
                'nominal_power_kw', 'efficiency', 'stages'
            ]
            
            # Check for required columns
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    'success': False,
                    'imported': 0,
                    'errors': [f"Missing required columns: {', '.join(missing_cols)}"]
                }
            
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Create pump dictionary
                    pump = {
                        'id': f"pump_{len(self.pumps) + imported_count + 1}",
                        'model': str(row['model']).strip(),
                        'nominal_q_m3': float(row['nominal_q_m3']),
                        'min_q_m3': float(row['min_q_m3']),
                        'max_q_m3': float(row['max_q_m3']),
                        'nominal_head_m': float(row['nominal_head_m']),
                        'min_head_m': float(row['min_head_m']),
                        'max_head_m': float(row['max_head_m']),
                        'nominal_power_kw': float(row['nominal_power_kw']),
                        'efficiency': float(row['efficiency']),
                        'stages': int(row['stages']),
                        'manufacturer': str(row.get('manufacturer', '')).strip(),
                        'notes': str(row.get('notes', '')).strip()
                    }
                    
                    # Validate data
                    if pump['nominal_q_m3'] <= 0 or pump['min_q_m3'] <= 0 or pump['max_q_m3'] <= 0:
                        errors.append(f"Row {index + 2}: Invalid flow rates")
                        continue
                    
                    if pump['nominal_head_m'] <= 0 or pump['min_head_m'] <= 0 or pump['max_head_m'] <= 0:
                        errors.append(f"Row {index + 2}: Invalid head values")
                        continue
                    
                    if pump['efficiency'] <= 0 or pump['efficiency'] > 100:
                        errors.append(f"Row {index + 2}: Invalid efficiency value")
                        continue
                    
                    if pump['stages'] <= 0:
                        errors.append(f"Row {index + 2}: Invalid stages count")
                        continue
                    
                    self.pumps.append(pump)
                    imported_count += 1
                    
                except (ValueError, TypeError) as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
                    continue
            
            # Save updated pumps
            if imported_count > 0:
                self.save_pumps()
            
            return {
                'success': True,
                'imported': imported_count,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'imported': 0,
                'errors': [f"Error reading Excel file: {str(e)}"]
            }
    
    def get_pumps(self) -> List[Dict[str, Any]]:
        """Get all pumps."""
        return self.pumps.copy()
    
    def get_pump_by_id(self, pump_id: str) -> Optional[Dict[str, Any]]:
        """Get pump by ID."""
        for pump in self.pumps:
            if pump['id'] == pump_id:
                return pump
        return None
    
    def delete_pump(self, pump_id: str) -> bool:
        """Delete pump by ID."""
        for i, pump in enumerate(self.pumps):
            if pump['id'] == pump_id:
                del self.pumps[i]
                self.save_pumps()
                return True
        return False
    
    def export_to_excel(self, output_path: str) -> bool:
        """Export pumps to Excel file.
        
        Args:
            output_path: Path for output Excel file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.pumps:
                return False
            
            df = pd.DataFrame(self.pumps)
            df.to_excel(output_path, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}", file=sys.stderr)
            return False
    
    def export_to_text(self, output_path: str) -> bool:
        """Export pumps to human-readable text file.
        
        Args:
            output_path: Path for output text file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.pumps:
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("IrkPUMP - Каталог насосов\n")
                f.write("=" * 50 + "\n\n")
                
                for i, pump in enumerate(self.pumps, 1):
                    f.write(f"Насос #{i}: {pump.get('model', 'N/A')}\n")
                    f.write(f"  Производитель: {pump.get('manufacturer', 'N/A')}\n")
                    f.write(f"  Дебит: {pump.get('min_q_m3', 0):.1f} - {pump.get('max_q_m3', 0):.1f} м³/сут\n")
                    f.write(f"  Напор: {pump.get('min_head_m', 0):.1f} - {pump.get('max_head_m', 0):.1f} м\n")
                    f.write(f"  Мощность: {pump.get('nominal_power_kw', 0):.1f} кВт\n")
                    f.write(f"  КПД: {pump.get('efficiency', 0):.1f}%\n")
                    f.write(f"  Ступени: {pump.get('stages', 0)}\n")
                    if pump.get('notes'):
                        f.write(f"  Примечания: {pump['notes']}\n")
                    f.write("\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to text: {e}", file=sys.stderr)
            return False
    
    def get_pump_count(self) -> int:
        """Get total number of pumps."""
        return len(self.pumps)
    
    def clear_pumps(self) -> None:
        """Clear all pumps from memory and file."""
        self.pumps = []
        self.save_pumps()
    
    def search_pumps(self, query: str) -> List[Dict[str, Any]]:
        """Search pumps by model or manufacturer.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching pumps
        """
        if not query:
            return self.pumps.copy()
        
        query_lower = query.lower()
        matches = []
        
        for pump in self.pumps:
            model = pump.get('model', '').lower()
            manufacturer = pump.get('manufacturer', '').lower()
            
            if query_lower in model or query_lower in manufacturer:
                matches.append(pump)
        
        return matches


def create_sample_excel(file_path: str) -> None:
    """Create a sample Excel file with pump data template.
    
    Args:
        file_path: Path for the sample Excel file
    """
    sample_data = {
        'model': ['ESP-100', 'ESP-200', 'ESP-300'],
        'nominal_q_m3': [50.0, 100.0, 150.0],
        'min_q_m3': [20.0, 40.0, 60.0],
        'max_q_m3': [80.0, 160.0, 240.0],
        'nominal_head_m': [500.0, 800.0, 1200.0],
        'min_head_m': [200.0, 300.0, 450.0],
        'max_head_m': [800.0, 1300.0, 2000.0],
        'nominal_power_kw': [15.0, 30.0, 50.0],
        'efficiency': [65.0, 70.0, 75.0],
        'stages': [10, 15, 20],
        'manufacturer': ['PumpCorp', 'PumpCorp', 'PumpCorp'],
        'notes': ['Standard model', 'High capacity', 'Heavy duty']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel(file_path, index=False, engine='openpyxl')


def get_catalog_files(catalog_dir: Path) -> List[str]:
    """Get list of Excel files in catalog directory.
    
    Args:
        catalog_dir: Path to catalog directory
        
    Returns:
        List of Excel file names
    """
    if not catalog_dir.exists():
        return []
    
    excel_files = []
    for file_path in catalog_dir.glob("*.xlsx"):
        excel_files.append(file_path.name)
    for file_path in catalog_dir.glob("*.xls"):
        excel_files.append(file_path.name)
    
    return sorted(excel_files)


if __name__ == "__main__":
    # Create sample Excel file
    create_sample_excel("sample_pumps.xlsx")
    print("Sample Excel file created: sample_pumps.xlsx")
