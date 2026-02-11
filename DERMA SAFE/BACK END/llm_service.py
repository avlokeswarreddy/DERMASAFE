import random
import ollama
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalLLMService:
    # Simulated database for ingredient lookup fallback
    PRODUCT_PATTERNS = {
        'moisturizer': "Water, Glycerin, Dimethicone, Petrolatum, Cetearyl Alcohol, Hyaluronic Acid, Niacinamide",
        'moisturizing': "Water, Glycerin, Dimethicone, Petrolatum, Cetearyl Alcohol, Hyaluronic Acid, Niacinamide",
        'cleanser': "Water, Glycerin, Cocamidopropyl Betaine, Sodium Lauryl Sulfate, Salicylic Acid, Ceramides",
        'cleansing': "Water, Glycerin, Cocamidopropyl Betaine, Sodium Lauryl Sulfate, Salicylic Acid, Ceramides",
        'sunscreen': "Water, Zinc Oxide, Titanium Dioxide, Dimethicone, Vitamin E, Aloe Barbadensis Leaf Juice",
        'sunblock': "Water, Zinc Oxide, Titanium Dioxide, Dimethicone, Vitamin E, Aloe Barbadensis Leaf Juice",
        'serum': "Water, Glycerin, Niacinamide, Vitamin C, Ferulic Acid, Sodium Hyaluronate",
        'toner': "Water, Witch Hazel, Glycolic Acid, Panthenol, Allantoin, Tea Tree Oil",
        'cream': "Water, Shea Butter, Stearic Acid, Cetyl Alcohol, Vitamin E, Retinol",
        'cre': "Water, Shea Butter, Stearic Acid, Cetyl Alcohol, Vitamin E, Retinol",  # OCR abbreviation
        'lotion': "Water, Mineral Oil, Glycerin, Carbomer, Phenoxyethanol, Fragrance",
        'acne': "Water, Benzoyl Peroxide, Salicylic Acid, Tea Tree Oil, Witch Hazel",
        'gel': "Water, Alcohol Denat, Glycerin, Carbomer, Aloe Vera, Salicylic Acid",
        'lip balm': "Beeswax, Shea Butter, Coconut Oil, Vitamin E, Peppermint Oil",
        'shampoo': "Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Citric Acid, Fragrance",
        'conditioner': "Water, Cetearyl Alcohol, Behentrimonium Chloride, Panthenol, Dimethicone",
        'mask': "Water, Kaolin, Bentone, Glycerin, Aloe Barbadensis, Phenoxyethanol",
        'wash': "Water, Sodium Laureth Sulfate, Glycerin, Cocamidopropyl Betaine, Fragrance"
    }
    
    # Track Ollama availability
    _ollama_available = None
    _ollama_model = "llama3"

    @classmethod
    def _check_ollama_availability(cls):
        """Check if Ollama is available and cache the result."""
        if cls._ollama_available is not None:
            return cls._ollama_available
        
        try:
            logger.info("Checking Ollama availability...")
            models = ollama.list()
            
            # Check if llama3 model is available
            model_found = any('llama3' in model['name'] for model in models.get('models', []))
            
            if model_found:
                cls._ollama_available = True
                logger.info("[OK] Ollama is available with llama3 model")
            else:
                cls._ollama_available = False
                logger.warning("[WARNING] Ollama is running but llama3 model not found. Using fallback.")
                
        except Exception as e:
            cls._ollama_available = False
            logger.warning(f"[WARNING] Ollama not available: {e}. Using fallback mode.")
        
        return cls._ollama_available

    @classmethod
    def get_ingredients_for_product(cls, product_name):
        """
        Use Ollama LLM to predict likely ingredients for a product.
        Falls back to pattern matching if Ollama is unavailable.
        """
        # First try Ollama
        if cls._check_ollama_availability():
            try:
                prompt = f"""You are a cosmetic ingredient expert. Given a product name, list the most common ingredients typically found in such products.

Product Name: {product_name}

Provide ONLY a comma-separated list of ingredients, nothing else. Example format:
Water, Glycerin, Cetearyl Alcohol, Dimethicone, Niacinamide

Ingredients:"""

                response = ollama.chat(
                    model=cls._ollama_model,
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.3}  # Lower temperature for more consistent results
                )
                
                ingredients = response['message']['content'].strip()
                
                # Validate response - should be comma-separated
                if ',' in ingredients and len(ingredients) > 10:
                    logger.info(f"[OK] Ollama generated ingredients for '{product_name}'")
                    return ingredients
                else:
                    logger.warning("Ollama response invalid, using fallback")
                    
            except Exception as e:
                logger.error(f"Ollama ingredient generation failed: {e}")
                cls._ollama_available = False  # Mark as unavailable for future calls
        
        # Fallback to pattern matching
        logger.info(f"Using pattern-based fallback for '{product_name}'")
        name_lower = product_name.lower()
        
        # Check patterns
        for key, ingredients in cls.PRODUCT_PATTERNS.items():
            if key in name_lower:
                return ingredients
        
        # Default generic formula if no keyword matches
        return "Water, Glycerin, Cetearyl Alcohol, Dimethicone, Phenoxyethanol, Ethylhexylglycerin"

    @classmethod
    def generate_explanation(cls, skin_type, sensitivity, all_ingredients, unsafe_ingredients):
        """
        Use Ollama LLM to generate a dermatologist-style explanation.
        Falls back to template-based generation if Ollama is unavailable.
        """
        # First try Ollama
        if cls._check_ollama_availability():
            try:
                # Build context
                ingredients_str = ', '.join(all_ingredients[:10]) if len(all_ingredients) > 10 else ', '.join(all_ingredients)
                unsafe_str = ', '.join(unsafe_ingredients) if unsafe_ingredients else "none"
                
                prompt = f"""You are a professional dermatologist providing skincare advice. Analyze this product for a patient.

Patient Profile:
- Skin Type: {skin_type}
- Sensitivity Level: {sensitivity}

Product Ingredients: {ingredients_str}
Flagged Ingredients: {unsafe_str}

Provide a brief, professional explanation (2-3 sentences) about whether this product is suitable for the patient. Be specific about the flagged ingredients if any exist. Keep it concise and actionable.

Explanation:"""

                response = ollama.chat(
                    model=cls._ollama_model,
                    messages=[{'role': 'user', 'content': prompt}],
                    options={'temperature': 0.7}  # Moderate temperature for natural language
                )
                
                explanation = response['message']['content'].strip()
                
                # Validate response - should be reasonable length
                if len(explanation) > 20 and len(explanation) < 500:
                    logger.info("[OK] Ollama generated explanation")
                    return explanation
                else:
                    logger.warning("Ollama explanation invalid, using fallback")
                    
            except Exception as e:
                logger.error(f"Ollama explanation generation failed: {e}")
                cls._ollama_available = False  # Mark as unavailable for future calls
        
        # Fallback to template-based generation
        logger.info("Using template-based fallback for explanation")
        try:
            # Deterministic/Template-based generation
            if not unsafe_ingredients:
                positive_notes = [
                    "Great choice! This product uses generally safe ingredients.",
                    "This formulation looks balanced and suitable for your profile.",
                    "A solid option for daily use with minimal risk of irritation."
                ]
                key_benefit = "hydrating" if "glycerin" in str(all_ingredients).lower() else "gentle"
                
                return (
                    f"{random.choice(positive_notes)} "
                    f"It appears to remain {key_benefit} for {skin_type} skin "
                    f"even with {sensitivity} sensitivity."
                )
            
            # If unsafe ingredients found
            count = len(unsafe_ingredients)
            risk_term = "potential irritants" if count > 1 else "a potential irritant"
            
            warning_templates = [
                f"Caution is advised. We detected {risk_term} that might not agree with {skin_type} skin.",
                f"This product contains {risk_term} which could trigger reactions for {sensitivity} sensitivity.",
                f"You might want to patch test this first due to the presence of {risk_term}."
            ]
            
            detail = f"Specifically, {', '.join(unsafe_ingredients[:3])} {'are' if count > 1 else 'is'} known to cause issues."
            
            return f"{random.choice(warning_templates)} {detail} Consider a gentler alternative."

        except Exception as e:
            return "Unable to generate detailed explanation at this time."