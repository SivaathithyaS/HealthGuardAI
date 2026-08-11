"""
Owned by: Full-stack/Integration role

Contract:
    extract_report_values(file_path: str) -> dict
        returns extracted lab values keyed to the same feature names
        used by prediction_service, e.g. {"glucose": 142, "creatinine": 1.1}

NOTE: extracted values are shown to the user for confirmation/edit before
being sent to /predict — do not auto-submit without a review step.
"""


def extract_report_values(file_path: str) -> dict:
    raise NotImplementedError
