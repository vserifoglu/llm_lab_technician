
import pytest
from dental_data_pipeline.src.models import Case
from dental_data_pipeline.src.reporting import generate_markdown_report

def test_report_generation_structure():
    """Ensure the report contains key sections and histogram tables."""
    # Create dummy stats
    stats_data = {
        "total_cases": 10,
        "jaw_dist": {"Upper": 5, "Lower": 5},
        "crown_counts": {11: 5, 21: 5},
        "margin_stats": {"mean": 200, "min": 50, "max": 400},
        "hist_teeth_per_case": {"1_unit": 8, "10_plus": 2} # Histogram Data
    }
    
    report = generate_markdown_report(stats_data)
    
    # Check for Markdown Headers
    assert "# Dental Data Analysis Report" in report
    assert "## Jaw Distribution" in report
    assert "## Tooth Frequency Heatmap" in report
    
    # Check for Histogram Table formatting
    assert "| Bucket | Count |" in report
    assert "| 1_unit | 8 |" in report
