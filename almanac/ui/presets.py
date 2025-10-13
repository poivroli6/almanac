"""
Preset Management System

Handles saving, loading, and managing user presets for filter configurations.
"""

import json
from typing import Dict, List, Optional, Any


class PresetManager:
    """
    Manages user presets for filter configurations.
    
    Presets are stored in browser localStorage via Dash's dcc.Store component.
    """
    
    @staticmethod
    def create_preset(name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new preset from current settings.
        
        Args:
            name: Preset name
            settings: Dictionary of current application settings
        
        Returns:
            Preset dictionary with metadata
        """
        import datetime
        
        return {
            'name': name,
            'created_at': datetime.datetime.now().isoformat(),
            'settings': settings
        }
    
    @staticmethod
    def save_preset(presets: Dict[str, Dict], preset_name: str, settings: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Save a preset to the presets dictionary.
        
        Args:
            presets: Existing presets dictionary
            preset_name: Name for the new preset
            settings: Settings to save
        
        Returns:
            Updated presets dictionary
        """
        if not preset_name or not preset_name.strip():
            raise ValueError("Preset name cannot be empty")
        
        preset_name = preset_name.strip()
        
        # Create the preset
        preset = PresetManager.create_preset(preset_name, settings)
        
        # Update presets dictionary
        presets = presets or {}
        presets[preset_name] = preset
        
        return presets
    
    @staticmethod
    def load_preset(presets: Dict[str, Dict], preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a preset by name.
        
        Args:
            presets: Presets dictionary
            preset_name: Name of preset to load
        
        Returns:
            Preset settings dictionary or None if not found
        """
        if not presets or preset_name not in presets:
            return None
        
        return presets[preset_name].get('settings')
    
    @staticmethod
    def delete_preset(presets: Dict[str, Dict], preset_name: str) -> Dict[str, Dict]:
        """
        Delete a preset by name.
        
        Args:
            presets: Presets dictionary
            preset_name: Name of preset to delete
        
        Returns:
            Updated presets dictionary
        """
        if presets and preset_name in presets:
            del presets[preset_name]
        
        return presets or {}
    
    @staticmethod
    def list_presets(presets: Dict[str, Dict]) -> List[Dict[str, str]]:
        """
        Get a list of all preset names and metadata.
        
        Args:
            presets: Presets dictionary
        
        Returns:
            List of preset options for dropdown
        """
        if not presets:
            return []
        
        return [
            {
                'label': f"{name} ({preset.get('created_at', 'Unknown date')[:10]})",
                'value': name
            }
            for name, preset in presets.items()
        ]
    
    @staticmethod
    def export_presets_to_json(presets: Dict[str, Dict]) -> str:
        """
        Export presets to JSON string for download.
        
        Args:
            presets: Presets dictionary
        
        Returns:
            JSON string of presets
        """
        return json.dumps(presets, indent=2)
    
    @staticmethod
    def import_presets_from_json(json_str: str) -> Dict[str, Dict]:
        """
        Import presets from JSON string.
        
        Args:
            json_str: JSON string of presets
        
        Returns:
            Presets dictionary
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
    
    @staticmethod
    def extract_settings_from_state(
        product, start_date, end_date, minute_hour, filters,
        vol_threshold, pct_threshold, timeA_hour, timeA_minute,
        timeB_hour, timeB_minute, intermarket_product,
        trim_percentage, stat_measures
    ) -> Dict[str, Any]:
        """
        Extract settings from callback state into a dictionary.
        
        Args:
            All callback state parameters
        
        Returns:
            Settings dictionary suitable for saving as preset
        """
        return {
            'product': product,
            'start_date': start_date,
            'end_date': end_date,
            'minute_hour': minute_hour,
            'filters': filters,
            'vol_threshold': vol_threshold,
            'pct_threshold': pct_threshold,
            'timeA_hour': timeA_hour,
            'timeA_minute': timeA_minute,
            'timeB_hour': timeB_hour,
            'timeB_minute': timeB_minute,
            'intermarket_product': intermarket_product,
            'trim_percentage': trim_percentage,
            'stat_measures': stat_measures
        }
    
    @staticmethod
    def apply_settings_to_outputs(settings: Dict[str, Any]) -> tuple:
        """
        Convert settings dictionary to output tuple for callbacks.
        
        Args:
            settings: Settings dictionary
        
        Returns:
            Tuple of values in the order expected by callbacks
        """
        return (
            settings.get('product'),
            settings.get('start_date'),
            settings.get('end_date'),
            settings.get('minute_hour'),
            settings.get('filters'),
            settings.get('vol_threshold'),
            settings.get('pct_threshold'),
            settings.get('timeA_hour'),
            settings.get('timeA_minute'),
            settings.get('timeB_hour'),
            settings.get('timeB_minute'),
            settings.get('intermarket_product'),
            settings.get('trim_percentage'),
            settings.get('stat_measures')
        )

