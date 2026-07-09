"""
Case-Specific Output Manager
Manages case-specific output folders (integrates with existing UI S3 upload)
"""
import os
import glob
import shutil
from datetime import datetime
from typing import Optional, List, Dict


class CaseOutputManager:
    """
    Manages case-specific output folders
    
    NOTE: S3 upload is handled by UI backend (ui/backend/app.py)
    This class focuses on local file organization into case folders
    """
    
    def __init__(self, case_id: Optional[str] = None):
        """
        Initialize case output manager
        
        Args:
            case_id: Case identifier (e.g., 'case-20260103-191758')
                    If None, will be extracted from input folder or generated
        """
        from agents.config.config import output_folder_dir_path
        
        self.case_id = case_id or self._detect_or_generate_case_id()
        self.case_output_dir = os.path.join(output_folder_dir_path, self.case_id)
        
        # Create case-specific output directory
        os.makedirs(self.case_output_dir, exist_ok=True)
        print(f"✓ Case output directory: {self.case_output_dir}")
    
    def _detect_or_generate_case_id(self) -> str:
        """
        Detect case ID from most recent input folder or generate new one
        
        Returns:
            Case ID string
        """
        from agents.utils.project_context import get_case_input_dir, get_case_id
        
        try:
            # Try to get case ID from project context
            case_id = get_case_id()
            if case_id:
                print(f"✓ Detected case ID from project info: {case_id}")
                return case_id
            
            # Try to get from input directory
            case_dir = get_case_input_dir()
            if case_dir:
                case_id = os.path.basename(case_dir)
                if case_id.startswith('case-'):
                    print(f"✓ Detected case ID from input directory: {case_id}")
                    return case_id
        except:
            pass
        
        # Generate new case ID
        case_id = f"case-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        print(f"✓ Generated new case ID: {case_id}")
        return case_id
    
    def get_output_path(self, filename: str) -> str:
        """
        Get full path for output file in case-specific directory
        
        Args:
            filename: Output filename (e.g., 'aws_business_case.md')
        
        Returns:
            Full path to output file
        """
        return os.path.join(self.case_output_dir, filename)
    
    def save_file(self, filename: str, content: str) -> str:
        """
        Save file to case-specific output directory
        
        Args:
            filename: Output filename
            content: File content (string)
        
        Returns:
            Path to saved file
        
        Note: S3 upload is handled by UI backend
        """
        filepath = self.get_output_path(filename)
        
        # Save locally
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Saved: {filepath}")
        
        return filepath
    
    def copy_file_to_case_dir(self, source_path: str, target_filename: Optional[str] = None) -> str:
        """
        Copy existing file to case-specific output directory
        
        Args:
            source_path: Path to source file
            target_filename: Target filename (defaults to source filename)
        
        Returns:
            Path to copied file
        
        Note: S3 upload is handled by UI backend
        """
        if not target_filename:
            target_filename = os.path.basename(source_path)
        
        target_path = self.get_output_path(target_filename)
        shutil.copy2(source_path, target_path)
        print(f"✓ Copied: {source_path} → {target_path}")
        
        return target_path
    
    def organize_existing_outputs(self) -> Dict[str, str]:
        """
        Move existing output files from root output folder to case-specific folder
        
        Returns:
            Dictionary mapping original paths to new paths
        
        Note: S3 upload is handled by UI backend
        """
        from agents.config.config import output_folder_dir_path
        
        moved_files = {}
        
        # Patterns for output files to organize
        patterns = [
            'aws_business_case.md',
            'vm_to_ec2_mapping.xlsx',
            'it_inventory_aws_pricing_*.xlsx',
            'eks_migration_analysis.xlsx',
            'migration_wave_plan.xlsx'
        ]
        
        for pattern in patterns:
            files = glob.glob(os.path.join(output_folder_dir_path, pattern))
            for filepath in files:
                # Skip if already in a case folder
                if '/case-' in filepath or '\\case-' in filepath:
                    continue
                
                filename = os.path.basename(filepath)
                new_path = self.copy_file_to_case_dir(filepath, filename)
                moved_files[filepath] = new_path
                
                # Optionally remove original (commented out for safety)
                # os.remove(filepath)
        
        if moved_files:
            print(f"✓ Organized {len(moved_files)} output files into case folder")
        
        return moved_files
    
    def list_case_outputs(self) -> List[str]:
        """
        List all output files in case directory
        
        Returns:
            List of filenames
        """
        if not os.path.exists(self.case_output_dir):
            return []
        
        files = []
        for item in os.listdir(self.case_output_dir):
            filepath = os.path.join(self.case_output_dir, item)
            if os.path.isfile(filepath) and not item.startswith('.') and not item.startswith('~$'):
                files.append(item)
        
        return sorted(files)
    
    def get_case_summary(self) -> Dict:
        """
        Get summary of case outputs
        
        Returns:
            Dictionary with case information
        """
        files = self.list_case_outputs()
        
        summary = {
            'case_id': self.case_id,
            'output_directory': self.case_output_dir,
            'file_count': len(files),
            'files': files
        }
        
        return summary


def get_case_output_manager(case_id: Optional[str] = None) -> CaseOutputManager:
    """
    Get or create case output manager instance
    
    Args:
        case_id: Optional case ID
    
    Returns:
        CaseOutputManager instance
    """
    return CaseOutputManager(case_id)
