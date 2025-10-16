#!/usr/bin/env python3
"""
Real-World Floor Plan Management Service
Handles file upload, processing, and management of floor plan documents
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import zipfile
import tempfile
from PIL import Image, ImageDraw
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FloorPlanProcessor:
    """Processes various floor plan file formats"""

    SUPPORTED_FORMATS = {
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg'],
        'cad': ['.dwg', '.dxf', '.dwf'],
        'pdf': ['.pdf'],
        'office': ['.vsd', '.vsdx', '.ppt', '.pptx']
    }

    def __init__(self, upload_folder: str):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

        # Create subfolders for organization
        (self.upload_folder / 'originals').mkdir(exist_ok=True)
        (self.upload_folder / 'processed').mkdir(exist_ok=True)
        (self.upload_folder / 'thumbnails').mkdir(exist_ok=True)
        (self.upload_folder / 'metadata').mkdir(exist_ok=True)

    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported"""
        ext = Path(filename).suffix.lower()
        for format_group in self.SUPPORTED_FORMATS.values():
            if ext in format_group:
                return True
        return False

    def get_format_type(self, filename: str) -> Optional[str]:
        """Get format type (image, cad, pdf, office)"""
        ext = Path(filename).suffix.lower()
        for format_type, extensions in self.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return format_type
        return None

    def process_uploaded_file(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Process uploaded floor plan file"""
        try:
            file_id = str(uuid.uuid4())
            file_ext = Path(original_filename).suffix.lower()
            format_type = self.get_format_type(original_filename)

            # Create unique filename
            processed_filename = f"{file_id}{file_ext}"
            processed_path = self.upload_folder / 'processed' / processed_filename

            # Copy to processed folder
            import shutil
            shutil.copy2(file_path, processed_path)

            # Generate thumbnail
            thumbnail_path = self._generate_thumbnail(processed_path, file_id)

            # Extract metadata
            metadata = self._extract_metadata(processed_path, original_filename, format_type)

            # Save metadata
            metadata_path = self.upload_folder / 'metadata' / f"{file_id}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

            result = {
                'file_id': file_id,
                'original_filename': original_filename,
                'processed_filename': processed_filename,
                'format_type': format_type,
                'file_size': os.path.getsize(processed_path),
                'thumbnail_path': str(thumbnail_path) if thumbnail_path else None,
                'metadata': metadata,
                'upload_time': datetime.now().isoformat(),
                'status': 'processed'
            }

            logger.info(f"Successfully processed floor plan: {original_filename}")
            return result

        except Exception as e:
            logger.error(f"Error processing floor plan {original_filename}: {str(e)}")
            return {
                'file_id': None,
                'original_filename': original_filename,
                'status': 'error',
                'error': str(e)
            }

    def _generate_thumbnail(self, file_path: Path, file_id: str) -> Optional[Path]:
        """Generate thumbnail for floor plan"""
        try:
            thumbnail_path = self.upload_folder / 'thumbnails' / f"{file_id}.jpg"

            if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                # Process image files
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Create thumbnail
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, 'JPEG', quality=85)
                    return thumbnail_path

            elif file_path.suffix.lower() == '.pdf':
                # For PDF files, create a placeholder thumbnail
                self._create_placeholder_thumbnail(thumbnail_path, 'PDF Floor Plan')
                return thumbnail_path

            elif file_path.suffix.lower() in ['.dwg', '.dxf']:
                # For CAD files, create a placeholder thumbnail
                self._create_placeholder_thumbnail(thumbnail_path, 'CAD Drawing')
                return thumbnail_path

            else:
                # Create generic placeholder
                self._create_placeholder_thumbnail(thumbnail_path, 'Floor Plan')
                return thumbnail_path

        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return None

    def _create_placeholder_thumbnail(self, thumbnail_path: Path, label: str):
        """Create placeholder thumbnail with label"""
        img = Image.new('RGB', (300, 300), color='#f0f0f0')
        draw = ImageDraw.Draw(img)

        # Draw border
        draw.rectangle([(10, 10), (290, 290)], outline='#ccc', width=2)

        # Draw icon (simple building representation)
        draw.rectangle([(80, 120), (220, 200)], outline='#666', width=2)
        draw.rectangle([(90, 130), (130, 160)], outline='#666', width=1)
        draw.rectangle([(140, 130), (180, 160)], outline='#666', width=1)
        draw.rectangle([(190, 130), (210, 160)], outline='#666', width=1)

        # Add text
        draw.text((150, 220), label, fill='#666', anchor='mm')

        img.save(thumbnail_path, 'JPEG', quality=85)

    def _extract_metadata(self, file_path: Path, original_filename: str, format_type: str) -> Dict[str, Any]:
        """Extract metadata from floor plan file"""
        metadata = {
            'original_filename': original_filename,
            'format_type': format_type,
            'file_size': os.path.getsize(file_path),
            'upload_time': datetime.now().isoformat(),
            'dimensions': None,
            'dpi': None,
            'color_mode': None,
            'estimated_scale': None,
            'rooms_detected': [],
            'processing_notes': []
        }

        try:
            if format_type == 'image':
                with Image.open(file_path) as img:
                    metadata['dimensions'] = img.size
                    metadata['color_mode'] = img.mode
                    if hasattr(img, 'info') and 'dpi' in img.info:
                        metadata['dpi'] = img.info['dpi']

                    # Basic room detection (placeholder)
                    metadata['rooms_detected'] = self._detect_rooms_basic(img)

        except Exception as e:
            metadata['processing_notes'].append(f"Metadata extraction error: {str(e)}")

        return metadata

    def _detect_rooms_basic(self, img: Image.Image) -> List[Dict[str, Any]]:
        """Basic room detection for demonstration"""
        # This is a placeholder - in real implementation, you'd use computer vision
        # For now, return sample room data
        return [
            {'room_id': 'R001', 'type': 'office', 'estimated_area': 150, 'confidence': 0.7},
            {'room_id': 'R002', 'type': 'conference', 'estimated_area': 300, 'confidence': 0.8},
            {'room_id': 'R003', 'type': 'storage', 'estimated_area': 80, 'confidence': 0.6}
        ]


class FloorPlanManager:
    """Manages floor plan database and operations"""

    def __init__(self, data_folder: str):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.database_file = self.data_folder / 'floor_plans.json'
        self.processor = FloorPlanProcessor(str(self.data_folder / 'uploads'))

        # Load existing database
        self.floor_plans = self._load_database()

    def _load_database(self) -> Dict[str, Any]:
        """Load floor plan database"""
        try:
            if self.database_file.exists():
                with open(self.database_file, 'r') as f:
                    return json.load(f)
            return {'floor_plans': [], 'buildings': [], 'last_updated': None}
        except Exception as e:
            logger.error(f"Error loading database: {str(e)}")
            return {'floor_plans': [], 'buildings': [], 'last_updated': None}

    def _save_database(self):
        """Save floor plan database"""
        try:
            self.floor_plans['last_updated'] = datetime.now().isoformat()
            with open(self.database_file, 'w') as f:
                json.dump(self.floor_plans, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")

    def add_floor_plan(self, file_path: str, original_filename: str, building_name: str = None,
                      floor_number: str = None, description: str = None) -> Dict[str, Any]:
        """Add new floor plan"""
        try:
            # Process the uploaded file
            processed_result = self.processor.process_uploaded_file(file_path, original_filename)

            if processed_result['status'] == 'error':
                return processed_result

            # Create floor plan record
            floor_plan_record = {
                'id': processed_result['file_id'],
                'original_filename': original_filename,
                'processed_filename': processed_result['processed_filename'],
                'format_type': processed_result['format_type'],
                'file_size': processed_result['file_size'],
                'thumbnail_path': processed_result['thumbnail_path'],
                'building_name': building_name or 'Unknown Building',
                'floor_number': floor_number or 'Unknown Floor',
                'description': description or '',
                'upload_time': processed_result['upload_time'],
                'metadata': processed_result['metadata'],
                'status': 'active',
                'tags': [],
                'spaces': [],
                'people_assignments': {}
            }

            # Add to database
            self.floor_plans['floor_plans'].append(floor_plan_record)
            self._save_database()

            logger.info(f"Added floor plan: {original_filename}")
            return {
                'success': True,
                'floor_plan': floor_plan_record,
                'message': 'Floor plan uploaded and processed successfully'
            }

        except Exception as e:
            logger.error(f"Error adding floor plan: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process floor plan'
            }

    def get_all_floor_plans(self) -> List[Dict[str, Any]]:
        """Get all floor plans"""
        return [fp for fp in self.floor_plans['floor_plans'] if fp['status'] == 'active']

    def get_floor_plan(self, floor_plan_id: str) -> Optional[Dict[str, Any]]:
        """Get specific floor plan by ID"""
        for fp in self.floor_plans['floor_plans']:
            if fp['id'] == floor_plan_id:
                return fp
        return None

    def delete_floor_plan(self, floor_plan_id: str) -> bool:
        """Delete floor plan (mark as inactive)"""
        try:
            for fp in self.floor_plans['floor_plans']:
                if fp['id'] == floor_plan_id:
                    fp['status'] = 'deleted'
                    fp['deleted_time'] = datetime.now().isoformat()
                    self._save_database()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting floor plan: {str(e)}")
            return False

    def update_floor_plan_spaces(self, floor_plan_id: str, spaces: List[Dict[str, Any]]) -> bool:
        """Update spaces for a floor plan"""
        try:
            floor_plan = self.get_floor_plan(floor_plan_id)
            if floor_plan:
                floor_plan['spaces'] = spaces
                floor_plan['last_modified'] = datetime.now().isoformat()
                self._save_database()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating spaces: {str(e)}")
            return False

    def assign_person_to_space(self, floor_plan_id: str, space_id: str, person_data: Dict[str, Any]) -> bool:
        """Assign person to a space"""
        try:
            floor_plan = self.get_floor_plan(floor_plan_id)
            if floor_plan:
                if 'people_assignments' not in floor_plan:
                    floor_plan['people_assignments'] = {}

                floor_plan['people_assignments'][space_id] = person_data
                floor_plan['last_modified'] = datetime.now().isoformat()
                self._save_database()
                return True
            return False
        except Exception as e:
            logger.error(f"Error assigning person: {str(e)}")
            return False

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        active_plans = self.get_all_floor_plans()

        total_buildings = len(set(fp['building_name'] for fp in active_plans))
        total_floors = len(active_plans)
        total_spaces = sum(len(fp.get('spaces', [])) for fp in active_plans)
        total_assignments = sum(len(fp.get('people_assignments', {})) for fp in active_plans)

        # File format breakdown
        format_breakdown = {}
        for fp in active_plans:
            format_type = fp.get('format_type', 'unknown')
            format_breakdown[format_type] = format_breakdown.get(format_type, 0) + 1

        return {
            'total_floor_plans': total_floors,
            'total_buildings': total_buildings,
            'total_spaces': total_spaces,
            'total_assignments': total_assignments,
            'format_breakdown': format_breakdown,
            'recent_uploads': sorted(active_plans, key=lambda x: x['upload_time'], reverse=True)[:5]
        }

# Global instance
_floor_plan_manager = None

def get_floor_plan_manager() -> FloorPlanManager:
    """Get global floor plan manager instance"""
    global _floor_plan_manager
    if _floor_plan_manager is None:
        data_folder = os.path.join(os.getcwd(), 'data', 'floor_plans')
        _floor_plan_manager = FloorPlanManager(data_folder)
    return _floor_plan_manager