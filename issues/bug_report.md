### Bug Report

**File:** `src/tractusx_sdk/dataspace/services/connector/base_connector_consumer.py`

**Lines:** 324-355

**Description:**
Instead of using 'key' as a parameter for the functions, the implementation should use the filter expression. This change is necessary to improve the functionality.

### Steps to Reproduce:
1. Review the implementation in the specified lines.
2. Identify the use of 'key' as a parameter.

### Suggested Fix:
Update the function parameters to use the filter expression instead of 'key'.