#!/usr/bin/env python3
"""
Load Shedding Intelligence Service for Derivco Facilities
Manages power outages, backup systems, and critical operations
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadSheddingStage(Enum):
    """Load shedding stages"""
    NO_LOAD_SHEDDING = 0
    STAGE_1 = 1
    STAGE_2 = 2
    STAGE_3 = 3
    STAGE_4 = 4
    STAGE_5 = 5
    STAGE_6 = 6
    STAGE_7 = 7
    STAGE_8 = 8

class PowerStatus(Enum):
    """Current power status"""
    MAINS_POWER = "mains"
    GENERATOR = "generator"
    UPS = "ups"
    NO_POWER = "no_power"

class EquipmentPriority(Enum):
    """Equipment priority levels"""
    CRITICAL = "critical"      # Servers, security, safety
    HIGH = "high"             # HVAC, lighting, elevators
    MEDIUM = "medium"         # Office equipment, printers
    LOW = "low"              # Non-essential equipment

@dataclass
class LoadSheddingSchedule:
    """Load shedding schedule entry"""
    area: str
    stage: LoadSheddingStage
    start_time: datetime
    end_time: datetime
    probability: float  # 0-1

@dataclass
class EquipmentItem:
    """Facility equipment with power requirements"""
    id: str
    name: str
    location: str
    priority: EquipmentPriority
    power_consumption: float  # kW
    backup_supported: bool
    current_status: str

@dataclass
class BackupSystem:
    """Backup power system"""
    id: str
    type: str  # generator, ups, solar
    capacity: float  # kW
    fuel_level: float  # percentage
    runtime_remaining: float  # hours
    status: str
    location: str

class LoadSheddingIntelligence:
    """Main load shedding management service"""

    def __init__(self, data_folder: str = None):
        self.data_folder = data_folder or os.path.join(os.getcwd(), 'data', 'load_shedding')
        os.makedirs(self.data_folder, exist_ok=True)

        # Initialize data
        self.current_status = PowerStatus.MAINS_POWER
        self.current_stage = LoadSheddingStage.NO_LOAD_SHEDDING
        self.schedules: List[LoadSheddingSchedule] = []
        self.equipment: List[EquipmentItem] = []
        self.backup_systems: List[BackupSystem] = []

        # Load existing data
        self._load_data()

        # Derivco specific areas (you can customize these)
        self.derivco_areas = [
            "Durban CBD Block 1",
            "Durban CBD Block 2",
            "Pinetown Area",
            "Umhlanga Ridge"
        ]

    def _load_data(self):
        """Load saved data"""
        try:
            config_file = os.path.join(self.data_folder, 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    # Load equipment and backup systems from config
                    self.equipment = [EquipmentItem(**item) for item in data.get('equipment', [])]
                    self.backup_systems = [BackupSystem(**sys) for sys in data.get('backup_systems', [])]
            else:
                # Initialize with sample Derivco equipment
                self._create_sample_equipment()

        except Exception as e:
            logger.error(f"Error loading load shedding data: {e}")
            self._create_sample_equipment()

    def _create_sample_equipment(self):
        """Create sample equipment for Derivco facilities"""
        self.equipment = [
            EquipmentItem("srv-001", "Data Center Servers", "Server Room", EquipmentPriority.CRITICAL, 45.0, True, "operational"),
            EquipmentItem("hvac-001", "Main HVAC System", "Basement", EquipmentPriority.HIGH, 25.0, True, "operational"),
            EquipmentItem("sec-001", "Security System", "Entrance", EquipmentPriority.CRITICAL, 5.0, True, "operational"),
            EquipmentItem("lift-001", "Main Elevator", "Lobby", EquipmentPriority.HIGH, 15.0, False, "operational"),
            EquipmentItem("light-001", "Office Lighting", "Open Plan", EquipmentPriority.MEDIUM, 12.0, False, "operational"),
            EquipmentItem("kit-001", "Kitchen Equipment", "Canteen", EquipmentPriority.LOW, 8.0, False, "operational")
        ]

        self.backup_systems = [
            BackupSystem("gen-001", "generator", 100.0, 85.0, 12.0, "ready", "Basement"),
            BackupSystem("ups-001", "ups", 20.0, 100.0, 0.5, "online", "Server Room"),
            BackupSystem("ups-002", "ups", 15.0, 100.0, 0.5, "online", "Security Room")
        ]

    def get_eskom_schedule(self, area: str) -> List[LoadSheddingSchedule]:
        """
        Get load shedding schedule from Eskom API or similar service.
        For now, this is a simulation - in production, you'd integrate with:
        - EskomSePush API
        - City Power API
        - Municipal electricity provider APIs
        """
        try:
            # Simulated schedule for Derivco areas
            now = datetime.now()
            schedules = []

            # Generate next 24 hours of potential load shedding
            for hour in range(24):
                time_slot = now + timedelta(hours=hour)

                # Simulate stage based on time (higher stages during peak times)
                if 6 <= time_slot.hour <= 10 or 17 <= time_slot.hour <= 22:
                    # Peak times - higher probability of load shedding
                    stage = LoadSheddingStage.STAGE_2 if hour % 4 == 0 else LoadSheddingStage.NO_LOAD_SHEDDING
                    probability = 0.7 if stage != LoadSheddingStage.NO_LOAD_SHEDDING else 0.3
                else:
                    # Off-peak times
                    stage = LoadSheddingStage.STAGE_1 if hour % 6 == 0 else LoadSheddingStage.NO_LOAD_SHEDDING
                    probability = 0.4 if stage != LoadSheddingStage.NO_LOAD_SHEDDING else 0.6

                if stage != LoadSheddingStage.NO_LOAD_SHEDDING:
                    schedules.append(LoadSheddingSchedule(
                        area=area,
                        stage=stage,
                        start_time=time_slot,
                        end_time=time_slot + timedelta(hours=2.5),
                        probability=probability
                    ))

            return schedules

        except Exception as e:
            logger.error(f"Error fetching Eskom schedule: {e}")
            return []

    def get_current_power_status(self) -> Dict[str, Any]:
        """Get current power status for Derivco facilities"""
        try:
            # In production, this would check actual power meters/sensors
            # For now, we simulate based on schedule

            current_time = datetime.now()
            active_outages = []

            for area in self.derivco_areas:
                schedule = self.get_eskom_schedule(area)
                for entry in schedule:
                    if entry.start_time <= current_time <= entry.end_time:
                        active_outages.append({
                            'area': entry.area,
                            'stage': entry.stage.value,
                            'remaining_time': (entry.end_time - current_time).total_seconds() / 3600
                        })

            # Determine overall status
            if active_outages:
                self.current_status = PowerStatus.GENERATOR
                self.current_stage = LoadSheddingStage(max([o['stage'] for o in active_outages]))
            else:
                self.current_status = PowerStatus.MAINS_POWER
                self.current_stage = LoadSheddingStage.NO_LOAD_SHEDDING

            return {
                'current_status': self.current_status.value,
                'current_stage': self.current_stage.value,
                'active_outages': active_outages,
                'backup_systems_status': [
                    {
                        'id': bs.id,
                        'type': bs.type,
                        'status': bs.status,
                        'fuel_level': bs.fuel_level,
                        'runtime_remaining': bs.runtime_remaining
                    }
                    for bs in self.backup_systems
                ],
                'timestamp': current_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting power status: {e}")
            return {
                'current_status': 'unknown',
                'current_stage': 0,
                'active_outages': [],
                'backup_systems_status': [],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def get_equipment_priorities(self, stage: LoadSheddingStage) -> Dict[str, List[EquipmentItem]]:
        """Get equipment categorized by what should stay on during load shedding"""
        try:
            categorized = {
                'keep_running': [],    # Critical equipment
                'conditional': [],     # High priority if backup available
                'shutdown': []         # Everything else
            }

            for equipment in self.equipment:
                if equipment.priority == EquipmentPriority.CRITICAL:
                    categorized['keep_running'].append(equipment)
                elif equipment.priority == EquipmentPriority.HIGH and equipment.backup_supported:
                    if stage.value <= 3:  # Only if not too severe
                        categorized['conditional'].append(equipment)
                    else:
                        categorized['shutdown'].append(equipment)
                else:
                    categorized['shutdown'].append(equipment)

            return categorized

        except Exception as e:
            logger.error(f"Error categorizing equipment: {e}")
            return {'keep_running': [], 'conditional': [], 'shutdown': []}

    def get_backup_capacity_analysis(self) -> Dict[str, Any]:
        """Analyze backup power capacity vs requirements"""
        try:
            total_backup_capacity = sum(bs.capacity for bs in self.backup_systems if bs.status == 'ready')

            critical_load = sum(eq.power_consumption for eq in self.equipment
                              if eq.priority == EquipmentPriority.CRITICAL)

            high_priority_load = sum(eq.power_consumption for eq in self.equipment
                                   if eq.priority == EquipmentPriority.HIGH and eq.backup_supported)

            full_load = sum(eq.power_consumption for eq in self.equipment)

            return {
                'total_backup_capacity': total_backup_capacity,
                'critical_load': critical_load,
                'high_priority_load': high_priority_load,
                'full_load': full_load,
                'critical_coverage': (total_backup_capacity >= critical_load),
                'high_priority_coverage': (total_backup_capacity >= (critical_load + high_priority_load)),
                'capacity_utilization': {
                    'critical': (critical_load / total_backup_capacity * 100) if total_backup_capacity > 0 else 0,
                    'with_high_priority': ((critical_load + high_priority_load) / total_backup_capacity * 100) if total_backup_capacity > 0 else 0
                },
                'estimated_runtime': {
                    'critical_only': min([bs.runtime_remaining for bs in self.backup_systems]) if self.backup_systems else 0,
                    'with_high_priority': min([bs.runtime_remaining * 0.6 for bs in self.backup_systems]) if self.backup_systems else 0
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing backup capacity: {e}")
            return {}

    def get_upcoming_outages(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming load shedding schedule"""
        try:
            all_upcoming = []

            for area in self.derivco_areas:
                schedules = self.get_eskom_schedule(area)
                for schedule in schedules:
                    all_upcoming.append({
                        'area': schedule.area,
                        'stage': schedule.stage.value,
                        'start_time': schedule.start_time.isoformat(),
                        'end_time': schedule.end_time.isoformat(),
                        'duration_hours': (schedule.end_time - schedule.start_time).total_seconds() / 3600,
                        'probability': schedule.probability,
                        'hours_until': (schedule.start_time - datetime.now()).total_seconds() / 3600
                    })

            # Sort by start time
            all_upcoming.sort(key=lambda x: x['start_time'])

            return all_upcoming

        except Exception as e:
            logger.error(f"Error getting upcoming outages: {e}")
            return []

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary data for Smart Insights integration"""
        try:
            power_status = self.get_current_power_status()
            upcoming = self.get_upcoming_outages(24)
            capacity = self.get_backup_capacity_analysis()

            # Next outage info
            next_outage = None
            if upcoming:
                next_outage = upcoming[0]

            return {
                'current_power_status': power_status['current_status'],
                'current_stage': power_status['current_stage'],
                'next_outage': next_outage,
                'backup_ready': all(bs.status == 'ready' for bs in self.backup_systems),
                'critical_coverage': capacity.get('critical_coverage', False),
                'fuel_level': min([bs.fuel_level for bs in self.backup_systems]) if self.backup_systems else 0,
                'total_outages_24h': len(upcoming),
                'generator_status': power_status['backup_systems_status'][0]['status'] if power_status['backup_systems_status'] else 'unknown'
            }

        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {
                'current_power_status': 'unknown',
                'current_stage': 0,
                'next_outage': None,
                'backup_ready': False,
                'critical_coverage': False,
                'fuel_level': 0,
                'total_outages_24h': 0,
                'generator_status': 'unknown',
                'error': str(e)
            }

# Global instance
_load_shedding_service = None

def get_load_shedding_service() -> LoadSheddingIntelligence:
    """Get global load shedding service instance"""
    global _load_shedding_service
    if _load_shedding_service is None:
        _load_shedding_service = LoadSheddingIntelligence()
    return _load_shedding_service