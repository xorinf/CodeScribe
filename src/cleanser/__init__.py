"""
Cleanser package for CodeScribe.
Provides data cleansing utilities to remove noise, boilerplate, and secrets from scraped data.
"""

from .pipeline import CleanserPipeline

__all__ = ["CleanserPipeline"]
