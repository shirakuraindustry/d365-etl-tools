# Copilot Instructions for d365-etl-tools

## Project Overview
This repository contains ETL (Extract, Transform, Load) tools for the Shirakura Kogyo D365 migration project. The main focus is on data normalization, validation, and transformation using Python scripts and Pandas.

## Key Components
- **transform_validate.py**: Core script for data normalization and validation. Implements Unicode normalization, email/phone normalization, and whitespace handling.
- **cmt-files/**, **data/**: Contains XML and related data files for import/export and comparison.
- **matched_results.csv**, **sandbox.csv**, **shirakura_industry.csv**: Example or intermediate CSV data files.
- **myenv/**: Python virtual environment (do not commit changes here).
- **azure-pipelines.yml**: CI/CD pipeline configuration for Azure DevOps.

## Developer Workflows
- **Run ETL/validation**: Execute `transform_validate.py` directly with Python 3.10+ (see shebang and imports for requirements).
- **Dependencies**: Use `pip install -r requirements.txt` (if present) or install `pandas`, `pyyaml`, `jsonschema` as needed. The project expects a working Python environment (see `myenv/`).
- **CI/CD**: Azure Pipelines is used for automated builds and checks. See `azure-pipelines.yml` for details.

## Conventions & Patterns
- **Normalization**: All text fields are normalized using NFKC, whitespace trimming, and full/half-width space unification. See `normalize_text()` in `transform_validate.py`.
- **Email/Phone Validation**: Use `normalize_email()` and `normalize_phone_jp()` for standardization and error flagging.
- **Branching**: Follow the strategy in `README.md` (`main`, `dev`, `feature/*`).
- **Schema/Config**: Refer to `/docs/schema_guidelines.md` (if available) for naming and tagging conventions.

## Integration Points
- **Azure Data Factory/Power Platform**: Data flows may be orchestrated externally; this repo focuses on Python-side logic.
- **Jupyter Notebooks**: For ad-hoc data exploration, use the `notebooks/` directory (if present).

## Examples
- To normalize a CSV column: use `normalize_text()` for each cell.
- To validate emails: use `normalize_email()` and check the returned flag.

## Additional Notes
- Do not commit changes to `myenv/` or other environment-specific files.
- For new scripts, follow the structure and style of `transform_validate.py`.
- For questions on schema or naming, consult `/docs/schema_guidelines.md` or project leads.
