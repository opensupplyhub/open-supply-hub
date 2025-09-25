#!/usr/bin/env python3

# Simple test script to verify our changes
import sys
import os
sys.path.append('src/django')

from api.facility_type_processing_type import (
    FACILITY_PROCESSING_TYPES_VALUES,
    ALL_FACILITY_TYPES,
    OFFICE_PROCESSING_TYPES,
    RECRUITMENT_AGENCY,
    UNION_HQ_OFFICE
)

def test_changes():
    print("Testing OSDEV-2112 changes...")
    print("=" * 50)
    
    # Test 1: Recruitment Agency should not be in main facility types
    print("\n1. Checking main facility types:")
    print(f"Available facility types: {list(ALL_FACILITY_TYPES.values())}")
    
    recruitment_in_main = 'Recruitment Agency' in ALL_FACILITY_TYPES.values()
    print(f"❌ Recruitment Agency in main facility types: {recruitment_in_main}")
    assert not recruitment_in_main, "Recruitment Agency should not be in main facility types"
    
    # Test 2: Office/HQ should include both Recruitment Agency and Union Headquarters/Office
    print("\n2. Checking Office/HQ processing types:")
    print(f"Office processing types: {list(OFFICE_PROCESSING_TYPES.values())}")
    
    recruitment_in_office = 'Recruitment Agency' in OFFICE_PROCESSING_TYPES.values()
    union_in_office = 'Union Headquarters/Office' in OFFICE_PROCESSING_TYPES.values()
    
    print(f"✓ Recruitment Agency in Office/HQ: {recruitment_in_office}")
    print(f"✓ Union Headquarters/Office in Office/HQ: {union_in_office}")
    
    assert recruitment_in_office, "Recruitment Agency should be in Office processing types"
    assert union_in_office, "Union Headquarters/Office should be in Office processing types"
    
    # Test 3: API structure should be correct
    print("\n3. Checking API structure:")
    office_hq_data = None
    for item in FACILITY_PROCESSING_TYPES_VALUES:
        if item['facilityType'] == 'Office / HQ':
            office_hq_data = item
            break
    
    assert office_hq_data is not None, "Office / HQ should be in API structure"
    
    print(f"Office / HQ processing types: {office_hq_data['processingTypes']}")
    
    recruitment_in_api = 'Recruitment Agency' in office_hq_data['processingTypes']
    union_in_api = 'Union Headquarters/Office' in office_hq_data['processingTypes']
    
    print(f"✓ Recruitment Agency in API: {recruitment_in_api}")
    print(f"✓ Union Headquarters/Office in API: {union_in_api}")
    
    assert recruitment_in_api, "Recruitment Agency should be in Office/HQ API response"
    assert union_in_api, "Union Headquarters/Office should be in Office/HQ API response"
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Changes are working correctly.")
    print("\nSummary of changes:")
    print("- Recruitment Agency moved from main facility type to Office/HQ processing type")
    print("- Union Headquarters/Office added to Office/HQ processing type")
    print("- API will now show both under Office / HQ facility type")

if __name__ == '__main__':
    test_changes()