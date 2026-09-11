"""Dependency-free, millimetre-based calibration target generation."""
from .patterns import Pattern, generate_pattern, object_points, PRESETS

__all__ = ['Pattern', 'generate_pattern', 'object_points', 'PRESETS']
