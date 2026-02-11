"""
DermaSafe API Test Suite
=========================
Test script to validate API functionality and demonstrate usage.
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:5000"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")

def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent))

# ============================================
# TEST CASES
# ============================================

def test_health_check():
    """Test the health check endpoint."""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        
        if response.status_code == 200:
            print_success("API is healthy and running")
            data = response.json()
            print_info(f"Database contains {data['database_size']} ingredients")
            print_json(data)
        else:
            print_error(f"Health check failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to API. Make sure the server is running!")
        print_info("Start the server with: python app.py")
        return False
    
    return True

def test_list_ingredients():
    """Test listing ingredients."""
    print_header("TEST 2: List Ingredients")
    
    try:
        # Get all ingredients
        response = requests.get(f"{BASE_URL}/api/ingredients")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {data['count']} ingredients")
            
            # Show a few examples
            print_info("Sample ingredients:")
            for i, (name, info) in enumerate(list(data['ingredients'].items())[:3]):
                print(f"  {i+1}. {name}: {info['risk_level']} risk - {info['category']}")
        
        # Test filtering by category
        print_info("\nFiltering by category: fragrance")
        response = requests.get(f"{BASE_URL}/api/ingredients?category=fragrance")
        data = response.json()
        print_success(f"Found {data['count']} fragrance ingredients")
        
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    
    return True

def test_safe_product():
    """Test analysis of a safe product."""
    print_header("TEST 3: Safe Product Analysis")
    
    payload = {
        "skin_profile": {
            "skin_type": "normal",
            "sensitivity": "none",
            "allergies": []
        },
        "product": {
            "name": "Gentle Moisturizer",
            "ingredients": "Water, Glycerin, Hyaluronic Acid, Niacinamide, Ceramide, Squalane"
        }
    }
    
    print_info("Testing with:")
    print(f"  Product: {payload['product']['name']}")
    print(f"  Skin Type: {payload['skin_profile']['skin_type']}")
    print(f"  Sensitivity: {payload['skin_profile']['sensitivity']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            safety = data['analysis']['overall_safety']
            
            if safety == "safe":
                print_success(f"Product classified as: {safety.upper()}")
            else:
                print_warning(f"Product classified as: {safety.upper()}")
            
            print_info(f"Total ingredients: {data['analysis']['total_ingredients']}")
            print_info(f"Flagged ingredients: {len(data['analysis']['flagged_ingredients'])}")
            print("\nRecommendation:")
            print(f"  {data['analysis']['recommendation']}")
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_json(response.json())
            
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    
    return True

def test_caution_product():
    """Test analysis of a product requiring caution."""
    print_header("TEST 4: Caution Product Analysis")
    
    payload = {
        "skin_profile": {
            "skin_type": "dry",
            "sensitivity": "mild",
            "allergies": []
        },
        "product": {
            "name": "Exfoliating Toner",
            "ingredients": "Water, Glycolic Acid, Alcohol Denat, Niacinamide, Salicylic Acid"
        }
    }
    
    print_info("Testing with:")
    print(f"  Product: {payload['product']['name']}")
    print(f"  Skin Type: {payload['skin_profile']['skin_type']}")
    print(f"  Sensitivity: {payload['skin_profile']['sensitivity']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            safety = data['analysis']['overall_safety']
            
            if safety == "caution":
                print_warning(f"Product classified as: {safety.upper()}")
            else:
                print_info(f"Product classified as: {safety.upper()}")
            
            print_info(f"Flagged ingredients: {len(data['analysis']['flagged_ingredients'])}")
            
            if data['analysis']['flagged_ingredients']:
                print("\nFlagged Ingredients:")
                for ing in data['analysis']['flagged_ingredients']:
                    print(f"  • {ing['name']}: {ing['reason']}")
                    
        else:
            print_error(f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    
    return True

def test_not_recommended_product():
    """Test analysis of a not recommended product."""
    print_header("TEST 5: Not Recommended Product Analysis")
    
    payload = {
        "skin_profile": {
            "skin_type": "sensitive",
            "sensitivity": "severe",
            "allergies": ["fragrance", "parabens", "sulfates"]
        },
        "product": {
            "name": "Scented Body Wash",
            "ingredients": "Water, Sodium Lauryl Sulfate, Fragrance, Methylparaben, Propylparaben, Glycerin"
        }
    }
    
    print_info("Testing with:")
    print(f"  Product: {payload['product']['name']}")
    print(f"  Skin Type: {payload['skin_profile']['skin_type']}")
    print(f"  Sensitivity: {payload['skin_profile']['sensitivity']}")
    print(f"  Allergies: {', '.join(payload['skin_profile']['allergies'])}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            safety = data['analysis']['overall_safety']
            
            if safety == "not_recommended":
                print_error(f"Product classified as: {safety.upper()}")
            else:
                print_info(f"Product classified as: {safety.upper()}")
            
            print_info(f"Flagged ingredients: {len(data['analysis']['flagged_ingredients'])}")
            
            if data['analysis']['flagged_ingredients']:
                print("\nHigh-Risk Ingredients:")
                for ing in data['analysis']['flagged_ingredients']:
                    if ing['status'] == 'not_recommended':
                        print(f"  ✗ {ing['name']}: {ing['reason']}")
                    else:
                        print(f"  ⚠ {ing['name']}: {ing['reason']}")
            
            print("\nRecommendation:")
            print(f"  {data['analysis']['recommendation']}")
                    
        else:
            print_error(f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    
    return True

def test_validation_errors():
    """Test API validation."""
    print_header("TEST 6: Input Validation")
    
    # Test 1: Missing skin_profile
    print_info("Testing missing skin_profile...")
    payload = {
        "product": {
            "ingredients": "Water, Glycerin"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 400:
        print_success("Validation error caught correctly")
        print(f"  Error: {response.json()['error']}")
    else:
        print_warning("Expected 400 error, got different response")
    
    # Test 2: Invalid skin type
    print_info("\nTesting invalid skin type...")
    payload = {
        "skin_profile": {
            "skin_type": "super_oily",  # Invalid
            "sensitivity": "none",
            "allergies": []
        },
        "product": {
            "ingredients": "Water"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 400:
        print_success("Invalid skin type caught correctly")
        print(f"  Error: {response.json()['error']}")
    else:
        print_warning("Expected 400 error, got different response")
    
    return True

def run_all_tests():
    """Run all test cases."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         DermaSafe API Test Suite                          ║")
    print("║         Testing Backend Functionality                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    tests = [
        ("Health Check", test_health_check),
        ("List Ingredients", test_list_ingredients),
        ("Safe Product", test_safe_product),
        ("Caution Product", test_caution_product),
        ("Not Recommended Product", test_not_recommended_product),
        ("Input Validation", test_validation_errors)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed{Colors.ENDC}\n")

if __name__ == "__main__":
    run_all_tests()
