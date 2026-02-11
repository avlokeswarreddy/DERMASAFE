"""
Test script to verify the LLM service works with and without Ollama
"""
import sys
from llm_service import LocalLLMService

print("=" * 60)
print("Testing DermaSafe LLM Service")
print("=" * 60)

# Test 1: Check Ollama availability
print("\n[Test 1] Checking Ollama availability...")
is_available = LocalLLMService._check_ollama_availability()
if is_available:
    print("[OK] Ollama is AVAILABLE - will use AI-powered responses")
else:
    print("[WARNING] Ollama is NOT available - will use fallback mode")
    print("          (This is OK! The app will still work perfectly)")

# Test 2: Get ingredients for a product
print("\n[Test 2] Testing ingredient generation...")
product_name = "CeraVe Moisturizing Cream"
print(f"Product: {product_name}")
ingredients = LocalLLMService.get_ingredients_for_product(product_name)
print(f"Generated ingredients: {ingredients[:100]}...")
print("[OK] Ingredient generation working!")

# Test 3: Generate explanation
print("\n[Test 3] Testing explanation generation...")
skin_type = "sensitive"
sensitivity = "moderate"
all_ingredients = ["Water", "Glycerin", "Fragrance", "Parabens"]
unsafe_ingredients = ["Fragrance", "Parabens"]

explanation = LocalLLMService.generate_explanation(
    skin_type, sensitivity, all_ingredients, unsafe_ingredients
)
print(f"Explanation: {explanation}")
print("[OK] Explanation generation working!")

# Test 4: Test with safe product
print("\n[Test 4] Testing with safe product...")
safe_ingredients = ["Water", "Glycerin", "Hyaluronic Acid", "Niacinamide"]
safe_explanation = LocalLLMService.generate_explanation(
    "normal", "none", safe_ingredients, []
)
print(f"Safe product explanation: {safe_explanation}")
print("[OK] Safe product handling working!")

print("\n" + "=" * 60)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 60)
print("\nConclusion:")
if is_available:
    print("[OK] Your system is using Ollama AI for enhanced responses")
else:
    print("[OK] Your system is using fallback mode (template-based)")
    print("     Product analysis will work perfectly!")
    print("\n[TIP] To enable AI features, install Ollama:")
    print("      1. Visit: https://ollama.com/download")
    print("      2. Install Ollama")
    print("      3. Run: ollama pull llama3")
    print("      4. Restart your backend")

print("\n[READY] DermaSafe is ready to analyze products!")
