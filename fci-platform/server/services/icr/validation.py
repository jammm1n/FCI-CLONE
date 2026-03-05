"""
Validation engine.
Collects field requirements from all processors that will run,
deduplicates, and returns a unified list of errors.
"""


def validate_for_processing(session_data, params, processors):
    """
    Check that all required manual fields are provided
    based on which processors will run with the available data.

    Args:
        session_data: Session dict with detected_files, uol_data etc.
        params: Dict of manual form fields from the frontend
        processors: List of processor instances

    Returns:
        List of error dicts: [{"field": "nationality", "message": "..."}]
    """
    available_files = set(session_data.get('detected_files', {}).keys())

    # Check if UOL provides data equivalent to certain file types
    uol_data = session_data.get('uol_data', {})
    if uol_data and uol_data.get('fiat_withdrawals'):
        available_files.add('UOL_FIAT_WITHDRAWALS')

    # Collect all required fields from processors that will run
    required_fields = {}  # field_name -> set of reasons

    for processor in processors:
        if not processor.should_run(available_files, params):
            continue

        for req in processor.required_fields:
            field = req['field']
            message = req.get('message', f'{field} is required')

            # Check 'when' condition
            when = req.get('when', 'always')
            if when == 'always':
                should_require = True
            elif callable(when):
                should_require = when(available_files, params)
            else:
                should_require = True

            if should_require:
                if field not in required_fields:
                    required_fields[field] = message

    # Check each required field against params
    errors = []
    for field, message in required_fields.items():
        value = params.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            errors.append({'field': field, 'message': message})
        elif isinstance(value, (int, float)) and value == 0:
            # Numeric fields that are 0 are considered empty
            errors.append({'field': field, 'message': message})

    return errors