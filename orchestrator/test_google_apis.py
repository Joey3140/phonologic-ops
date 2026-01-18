#!/usr/bin/env python3
"""
Quick test script for Google API integrations.
Run: python test_google_apis.py
"""
import os
import sys
import json

# Load from .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_credentials():
    """Test that Google credentials are configured"""
    print("\n=== Testing Google Credentials ===\n")
    
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if creds_json:
        print("✅ GOOGLE_SERVICE_ACCOUNT_JSON is set")
        try:
            creds_dict = json.loads(creds_json)
            print(f"   Project ID: {creds_dict.get('project_id', 'unknown')}")
            print(f"   Client Email: {creds_dict.get('client_email', 'unknown')}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False
    elif creds_path:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS path: {creds_path}")
        if os.path.exists(creds_path):
            print("   File exists")
        else:
            print("❌ File does not exist!")
            return False
    else:
        print("❌ No Google credentials found!")
        print("   Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS")
        return False
    
    return True


def test_drive_api():
    """Test Google Drive API access"""
    print("\n=== Testing Google Drive API ===\n")
    
    try:
        from tools.google_drive_toolkit import GoogleDriveToolkit
        toolkit = GoogleDriveToolkit()
        
        # Try listing files (will use root or default folder)
        result = toolkit.list_files(max_results=5)
        data = json.loads(result)
        
        if "error" in data:
            print(f"❌ Drive API Error: {data['error']}")
            return False
        
        print(f"✅ Drive API working! Found {data.get('count', 0)} files")
        for f in data.get('files', [])[:3]:
            print(f"   - {f['name']} ({f['type']})")
        return True
        
    except Exception as e:
        print(f"❌ Drive API Error: {e}")
        return False


def test_sheets_api():
    """Test Google Sheets API access"""
    print("\n=== Testing Google Sheets API ===\n")
    
    try:
        from tools.google_sheets_toolkit import GoogleSheetsToolkit
        toolkit = GoogleSheetsToolkit()
        
        # Create a test spreadsheet
        result = toolkit.create_spreadsheet(
            title="[TEST] Orchestrator API Test",
            sheet_names=["TestData"]
        )
        data = json.loads(result)
        
        if "error" in data:
            print(f"❌ Sheets API Error: {data['error']}")
            return False
        
        spreadsheet_id = data.get('id')
        print(f"✅ Created test spreadsheet: {data.get('title')}")
        print(f"   URL: {data.get('url')}")
        
        # Write some test data
        write_result = toolkit.write_range(
            spreadsheet_id=spreadsheet_id,
            range_notation="TestData!A1:C2",
            values=[
                ["Name", "Role", "Status"],
                ["Orchestrator", "Test", "✅ Working"]
            ]
        )
        write_data = json.loads(write_result)
        
        if "error" in write_data:
            print(f"❌ Write Error: {write_data['error']}")
        else:
            print(f"✅ Wrote {write_data.get('updated_cells')} cells")
        
        # Read it back
        read_result = toolkit.read_spreadsheet(spreadsheet_id)
        read_data = json.loads(read_result)
        
        if "error" not in read_data:
            print(f"✅ Read back {read_data.get('row_count')} rows")
        
        print(f"\n   📋 Test spreadsheet: {data.get('url')}")
        print("   (You can delete this manually if desired)")
        return True
        
    except Exception as e:
        print(f"❌ Sheets API Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_slides_api():
    """Test Google Slides API access"""
    print("\n=== Testing Google Slides API ===\n")
    
    try:
        from tools.google_slides_toolkit import GoogleSlidesToolkit
        toolkit = GoogleSlidesToolkit()
        
        # Create a test presentation
        result = toolkit.create_presentation(
            title="[TEST] Orchestrator Slides Test"
        )
        data = json.loads(result)
        
        if "error" in data:
            print(f"❌ Slides API Error: {data['error']}")
            return False
        
        presentation_id = data.get('id')
        print(f"✅ Created test presentation: {data.get('title')}")
        print(f"   URL: {data.get('url')}")
        
        # Add a slide
        add_result = toolkit.add_slide(
            presentation_id=presentation_id,
            layout="TITLE_AND_BODY"
        )
        add_data = json.loads(add_result)
        
        if "error" not in add_data:
            print(f"✅ Added slide: {add_data.get('slide_id')}")
        
        print(f"\n   📊 Test presentation: {data.get('url')}")
        print("   (You can delete this manually if desired)")
        return True
        
    except Exception as e:
        print(f"❌ Slides API Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Phonologic Orchestrator - Google API Test")
    print("=" * 50)
    
    # Test credentials first
    if not test_credentials():
        print("\n❌ Credentials not configured. Exiting.")
        sys.exit(1)
    
    results = {
        "Drive": test_drive_api(),
        "Sheets": test_sheets_api(),
        "Slides": test_slides_api()
    }
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for api, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {api}: {status}")
    
    if all(results.values()):
        print("\n🎉 All Google APIs working!")
        sys.exit(0)
    else:
        print("\n⚠️  Some APIs failed. Check errors above.")
        sys.exit(1)
