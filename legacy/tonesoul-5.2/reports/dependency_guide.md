# Dependency Install Guide (ToneSoul 5.2)

## Minimum Runtime (YSTM + YSS core)
- numpy
- pyyaml
- rich

## Optional (dashboard)
- streamlit
- pandas
- plotly

## Optional (YSTM visualization)
- cairosvg
- pillow

## Development Tools
- pytest
- black
- ruff

## Example (pip)
```
pip install -e .
pip install -e .[dashboard]
pip install -e .[ystm_viz]
pip install -e .[dev]
```

## Notes
- Cairo binaries are required for cairosvg PNG export (see README).
