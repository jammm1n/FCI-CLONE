"""
Base processor class.
All ICR processors inherit from this and declare their
requirements, consumed fields, and processing logic.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProcessorResult:
    """Standard return type from all processors."""
    content: str = ''
    has_data: bool = False
    csv_content: Optional[str] = None
    csv_filename: Optional[str] = None
    metadata: Optional[dict] = None


class BaseProcessor:
    """
    Abstract base class for all ICR processors.

    To create a new processor:
    1. Create a new .py file in the processors/ directory
    2. Subclass BaseProcessor
    3. Set the class attributes
    4. Implement process()
    
    The processor will be auto-discovered and registered.
    """

    # --- Identity ---
    id: str = None              # Unique key, e.g. "counterparty"
    label: str = None           # Display name, e.g. "Counterparty Analysis"
    sort_order: int = 50        # Tab display order (lower = earlier)

    # --- Data requirements ---
    # File types this processor needs (at least one must be present)
    required_file_types: list = []
    # File types this processor can optionally use
    optional_file_types: list = []
    # Manual fields required when this processor runs
    # Each entry: {"field": "name", "message": "error msg", "when": "always" | callable}
    required_fields: list = []

    # --- Field tracking for discovery ---
    # Every column this processor reads, keyed by file type.
    # Used by the field discovery engine to identify unused columns.
    #
    # Update this when you add new row.get() or row["key"] calls
    # in the process() method. The dev/field-log endpoint will
    # show any uploaded columns NOT listed here, helping you spot
    # new data from the C360 team.
    #
    # Format: {"FILE_TYPE": ["column_a", "column_b", ...]}
    # Example:
    #   consumed_fields = {
    #       "IT": ["link_user_id", "total_internal_crypto_trans_amt_usd"],
    #       "DEVICE_MAIN": ["top_10_ip_locations", "operation_count"],
    #   }
    consumed_fields: dict = {}

    def should_run(self, available_file_types, params):
        """
        Determine if this processor has enough data to run.
        Default: at least one required file type is available.
        Override for custom logic.
        """
        if not self.required_file_types:
            return False
        return bool(set(self.required_file_types) & set(available_file_types))

    def process(self, file_data, params, context):
        """
        Run the analysis.

        Args:
            file_data: Dict of detected files, keyed by type.
                       Each value has 'rows', 'headers', 'filename'.
            params: Dict of manual form field values.
            context: Dict with shared data:
                     - subject_uid: str
                     - uol_data: dict (customer_info, fiat_withdrawals, etc.)
                     - user_info: dict or None

        Returns:
            ProcessorResult
        """
        raise NotImplementedError(
            f"Processor {self.id} must implement process()"
        )