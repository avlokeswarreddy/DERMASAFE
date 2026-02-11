"""
DermaSafe Backend API
======================
A Flask-based REST API for skin-type based product safety detection.

This application analyzes cosmetic product ingredients against user skin profiles
to provide personalized safety recommendations.

Author: Senior Backend Engineer
Version: 1.0.0
"""
from llm_service import LocalLLMService
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import re
import logging
import ssl

# Bypass SSL certificate verification for model downloads (like EasyOCR models)
ssl._create_default_https_context = ssl._create_unverified_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# FLASK APPLICATION SETUP
# ============================================

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend integration

app.config['JSON_SORT_KEYS'] = False  # Preserve JSON key order

# ============================================
# USER MANAGEMENT & EMAIL
# ============================================

import json
import os

# ============================================
# USER MANAGEMENT & EMAIL
# ============================================

USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file to persist data across restarts."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(db):
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

users_db = load_users()  # Load content on startup

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    # ------------------------------------------------------------------
    # IMPORTANT: To send real emails, you must configure these values.
    # For Gmail, you need an "App Password", not your login password.
    # ------------------------------------------------------------------
    SMTP_CONFIG = {
        # 1. Set this to True to enable real email sending
        "enabled": True,  
        
        "server": "smtp.gmail.com",
        "port": 587,
        
        # 2. Enter your GMAIL address here (inside quotes)
        "email": "dermasafe.2007@gmail.com",

        
        # 3. Enter your Google App Password here (NOT your login password)
        # Go to https://myaccount.google.com/apppasswords to generate one
        "password": "Darshini@123" 
    }

    @staticmethod
    def send_welcome_email(to_email, name):
        """
        Sends a welcome email.
        If SMTP is disabled (default) or fails, saves to 'simulated_emails.txt'.
        """
        smtp_error = None
        
        if EmailService.SMTP_CONFIG["enabled"]:
            try:
                msg = MIMEMultipart()
                msg['From'] = EmailService.SMTP_CONFIG["email"]
                msg['To'] = to_email
                msg['Subject'] = "Welcome to DermaSafe!"

                body = f"""
                Hi {name},

                Welcome to DermaSafe! 
                
                Your account has been successfully created. We are excited to help you analyze skincare products safely.

                Best regards,
                The DermaSafe Team
                """
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP(EmailService.SMTP_CONFIG["server"], EmailService.SMTP_CONFIG["port"])
                server.starttls()
                server.login(EmailService.SMTP_CONFIG["email"], EmailService.SMTP_CONFIG["password"])
                server.send_message(msg)
                server.quit()
                print(f"✅ Real email sent successfully to {to_email}")
                return True
            except Exception as e:
                smtp_error = str(e)
                print(f"❌ Failed to send real email: {smtp_error}")
                print("⚠️ Falling back to simulation mode.")
        
        # Simulation Mode: Log to file
        log_content = (
            f"\n------------ 📨 NEW EMAIL (SIMULATION) 📨 ------------\n"
            f"Time: {datetime.utcnow().isoformat()}\n"
            f"To: {to_email}\n"
            f"Subject: Welcome to DermaSafe!\n"
            f"Body: Hi {name}, thanks for registering with DermaSafe. Your profile is now active.\n"
        )
        
        if smtp_error:
            log_content += f"\n⚠️ REAL EMAIL FAILED: {smtp_error}\n"
            log_content += "HINT: Check if you are using a Google App Password (not your login password).\n"
            
        log_content += f"--------------------------------------------------\n"
        
        # Print to console
        print(log_content)
        
        # Save to file so user can see it
        try:
            with open("simulated_emails.txt", "a", encoding="utf-8") as f:
                f.write(log_content)
            print("✅ Email saved to 'simulated_emails.txt'")
        except Exception as e:
            print(f"❌ Failed to save simulated email: {e}")
            
        return True

# ============================================
# INGREDIENT SAFETY DATABASE
# ============================================

class IngredientDatabase:
    """
    Central database of ingredient safety information.
    Maps ingredients to their risk levels and associated concerns.
    """
    
    # Risk levels: 'safe', 'low', 'moderate', 'high', 'severe'
    INGREDIENT_RISKS = {
        # Fragrances & Perfumes
        'fragrance': {
            'risk_level': 'high',
            'concerns': ['allergic reactions', 'irritation', 'sensitivity'],
            'affected_skin_types': ['sensitive', 'dry'],
            'category': 'fragrance'
        },
        'parfum': {
            'risk_level': 'high',
            'concerns': ['allergic reactions', 'irritation', 'sensitivity'],
            'affected_skin_types': ['sensitive', 'dry'],
            'category': 'fragrance'
        },
        
        # Alcohols
        'alcohol denat': {
            'risk_level': 'moderate',
            'concerns': ['dryness', 'irritation', 'barrier disruption'],
            'affected_skin_types': ['dry', 'sensitive'],
            'category': 'alcohol'
        },
        'denatured alcohol': {
            'risk_level': 'moderate',
            'concerns': ['dryness', 'irritation', 'barrier disruption'],
            'affected_skin_types': ['dry', 'sensitive'],
            'category': 'alcohol'
        },
        'ethanol': {
            'risk_level': 'moderate',
            'concerns': ['dryness', 'irritation'],
            'affected_skin_types': ['dry', 'sensitive'],
            'category': 'alcohol'
        },
        
        # Sulfates
        'sodium lauryl sulfate': {
            'risk_level': 'moderate',
            'concerns': ['dryness', 'irritation', 'oil stripping'],
            'affected_skin_types': ['dry', 'sensitive', 'normal'],
            'category': 'sulfate'
        },
        'sodium laureth sulfate': {
            'risk_level': 'low',
            'concerns': ['mild dryness', 'potential irritation'],
            'affected_skin_types': ['dry', 'sensitive'],
            'category': 'sulfate'
        },
        'sls': {
            'risk_level': 'moderate',
            'concerns': ['dryness', 'irritation', 'oil stripping'],
            'affected_skin_types': ['dry', 'sensitive', 'normal'],
            'category': 'sulfate'
        },
        'sles': {
            'risk_level': 'low',
            'concerns': ['mild dryness', 'potential irritation'],
            'affected_skin_types': ['dry', 'sensitive'],
            'category': 'sulfate'
        },
        
        # Parabens
        'methylparaben': {
            'risk_level': 'moderate',
            'concerns': ['hormone disruption', 'allergic reactions'],
            'affected_skin_types': ['sensitive'],
            'category': 'paraben'
        },
        'propylparaben': {
            'risk_level': 'moderate',
            'concerns': ['hormone disruption', 'allergic reactions'],
            'affected_skin_types': ['sensitive'],
            'category': 'paraben'
        },
        'butylparaben': {
            'risk_level': 'moderate',
            'concerns': ['hormone disruption', 'allergic reactions'],
            'affected_skin_types': ['sensitive'],
            'category': 'paraben'
        },
        
        # Essential Oils
        'essential oil': {
            'risk_level': 'moderate',
            'concerns': ['allergic reactions', 'photosensitivity', 'irritation'],
            'affected_skin_types': ['sensitive'],
            'category': 'essential-oil'
        },
        'lavender oil': {
            'risk_level': 'low',
            'concerns': ['allergic reactions', 'sensitivity'],
            'affected_skin_types': ['sensitive'],
            'category': 'essential-oil'
        },
        'tea tree oil': {
            'risk_level': 'moderate',
            'concerns': ['irritation', 'allergic reactions'],
            'affected_skin_types': ['sensitive', 'dry'],
            'category': 'essential-oil'
        },
        'peppermint oil': {
            'risk_level': 'moderate',
            'concerns': ['irritation', 'tingling sensation'],
            'affected_skin_types': ['sensitive'],
            'category': 'essential-oil'
        },
        
        # Retinoids
        'retinol': {
            'risk_level': 'moderate',
            'concerns': ['increased sensitivity', 'dryness', 'peeling'],
            'affected_skin_types': ['sensitive', 'dry'],
            'category': 'retinoid'
        },
        'retinyl palmitate': {
            'risk_level': 'low',
            'concerns': ['mild sensitivity', 'photosensitivity'],
            'affected_skin_types': ['sensitive'],
            'category': 'retinoid'
        },
        'tretinoin': {
            'risk_level': 'high',
            'concerns': ['severe irritation', 'peeling', 'photosensitivity'],
            'affected_skin_types': ['sensitive', 'dry', 'normal'],
            'category': 'retinoid'
        },
        
        # Acids
        'salicylic acid': {
            'risk_level': 'low',
            'concerns': ['mild dryness', 'sensitivity'],
            'affected_skin_types': ['dry', 'sensitive'],
            'category': 'acid'
        },
        'glycolic acid': {
            'risk_level': 'moderate',
            'concerns': ['irritation', 'photosensitivity', 'dryness'],
            'affected_skin_types': ['sensitive', 'dry'],
            'category': 'acid'
        },
        'lactic acid': {
            'risk_level': 'low',
            'concerns': ['mild sensitivity', 'photosensitivity'],
            'affected_skin_types': ['sensitive'],
            'category': 'acid'
        },
        
        # Preservatives
        'formaldehyde': {
            'risk_level': 'high',
            'concerns': ['allergic reactions', 'irritation', 'carcinogenic'],
            'affected_skin_types': ['all'],
            'category': 'preservative'
        },
        'dmdm hydantoin': {
            'risk_level': 'moderate',
            'concerns': ['formaldehyde release', 'allergic reactions'],
            'affected_skin_types': ['sensitive'],
            'category': 'preservative'
        },
        
        # Comedogenic Ingredients
        'coconut oil': {
            'risk_level': 'moderate',
            'concerns': ['pore clogging', 'acne breakouts'],
            'affected_skin_types': ['oily', 'combination'],
            'category': 'oil'
        },
        'isopropyl myristate': {
            'risk_level': 'moderate',
            'concerns': ['pore clogging', 'acne'],
            'affected_skin_types': ['oily', 'combination'],
            'category': 'emollient'
        },
    }
    
    # Safe, beneficial ingredients (for reference)
    SAFE_INGREDIENTS = {
        'hyaluronic acid', 'niacinamide', 'ceramide', 'peptide', 'vitamin c',
        'vitamin e', 'glycerin', 'squalane', 'allantoin', 'panthenol',
        'centella asiatica', 'green tea extract', 'aloe vera', 'water',
        'aqua', 'dimethicone', 'caprylic triglyceride'
    }
    
    @classmethod
    def get_ingredient_info(cls, ingredient_name):
        """
        Retrieve safety information for a specific ingredient.
        
        Args:
            ingredient_name (str): Name of the ingredient to look up
            
        Returns:
            dict: Ingredient safety information or None if not found
        """
        ingredient_lower = ingredient_name.lower().strip()
        
        # Direct match
        if ingredient_lower in cls.INGREDIENT_RISKS:
            return cls.INGREDIENT_RISKS[ingredient_lower]
        
        # Partial match (for compound names)
        for key, value in cls.INGREDIENT_RISKS.items():
            if key in ingredient_lower or ingredient_lower in key:
                return value
        
        return None
    
    @classmethod
    def is_safe_ingredient(cls, ingredient_name):
        """Check if ingredient is in the safe list."""
        ingredient_lower = ingredient_name.lower().strip()
        return any(safe in ingredient_lower for safe in cls.SAFE_INGREDIENTS)


# ============================================
# SAFETY ANALYZER ENGINE
# ============================================

class SafetyAnalyzer:
    """
    Core analysis engine that evaluates product safety based on
    user skin profile and ingredient composition.
    """
    
    # Sensitivity level multipliers for risk scoring
    SENSITIVITY_MULTIPLIERS = {
        'none': 1.0,
        'mild': 1.3,
        'moderate': 1.6,
        'severe': 2.0
    }
    
    # Risk level scores
    RISK_SCORES = {
        'safe': 0,
        'low': 1,
        'moderate': 2,
        'high': 3,
        'severe': 4
    }
    
    @staticmethod
    def parse_ingredients(ingredient_string):
        """
        Parse ingredient string into a clean list.
        
        Args:
            ingredient_string (str): Comma-separated ingredient list
            
        Returns:
            list: Clean list of ingredient names
        """
        # Split by comma and clean each ingredient
        ingredients = [
            ing.strip() 
            for ing in re.split(r'[,;]', ingredient_string) 
            if ing.strip()
        ]
        return ingredients
    
    @staticmethod
    def analyze_ingredient(ingredient, skin_type, sensitivity, user_allergies):
        """
        Analyze a single ingredient against user profile.
        
        Args:
            ingredient (str): Ingredient name
            skin_type (str): User's skin type
            sensitivity (str): User's sensitivity level
            user_allergies (list): List of user's known allergies
            
        Returns:
            dict: Analysis result for this ingredient
        """
        ingredient_info = IngredientDatabase.get_ingredient_info(ingredient)

        # Normalize user allergies
        normalized_allergies = [a.rstrip('s').lower() for a in (user_allergies or [])]

        # Safely extract ingredient metadata
        if ingredient_info:
            category = ingredient_info.get('category', '').lower()
            affected_types = ingredient_info.get('affected_skin_types', [])
            concerns = ingredient_info.get('concerns', [])
            base_risk = ingredient_info.get('risk_level', 'safe')
        else:
            category = ''
            affected_types = []
            concerns = []
            base_risk = 'safe'

        # Allergy matching
        is_allergen = category in normalized_allergies

        # Check if ingredient affects user's skin type
        affects_skin_type = (skin_type in affected_types) or ('all' in affected_types)

        # Apply sensitivity multiplier
        sensitivity_mult = SafetyAnalyzer.SENSITIVITY_MULTIPLIERS.get(sensitivity, 1.0)

        # Initialize risk score from base risk mapping
        risk_score = SafetyAnalyzer.RISK_SCORES.get(base_risk, 0)

        # Adjust score for allergies and skin-type impact
        if is_allergen:
            risk_score += 2  # Significant increase for known allergens
        if affects_skin_type:
            risk_score = int(risk_score * sensitivity_mult)

        # Determine final status and reason
        # If ingredient is a known allergen or it specifically affects the user's skin type,
        # mark it as not recommended (unsafe).
        if is_allergen or affects_skin_type or risk_score >= 4:
            status = 'not_recommended'
            if is_allergen:
                reason = 'Known allergen for you'
            elif affects_skin_type:
                reason = f'Unsuitable for {skin_type} skin'
            else:
                reason = f'High risk for {skin_type} skin with {sensitivity} sensitivity'
        elif risk_score >= 2:
            status = 'caution'
            reason = f"May cause {', '.join(concerns[:2])}" if concerns else 'Potential irritation or sensitivity'
        else:
            status = 'safe'
            reason = 'Low risk based on your profile'

        return {
            'name': ingredient,
            'risk_level': base_risk,
            'status': status,
            'concerns': concerns,
            'reason': reason,
            'category': category
        }
    
    @staticmethod
    def determine_overall_safety(analyzed_ingredients):
        """
        Determine overall product safety based on individual ingredient analyses.
        
        Args:
            analyzed_ingredients (list): List of analyzed ingredient dicts
            
        Returns:
            tuple: (safety_status, recommendation_message)
        """
        not_recommended_count = sum(
            1 for ing in analyzed_ingredients if ing['status'] == 'not_recommended'
        )
        caution_count = sum(
            1 for ing in analyzed_ingredients if ing['status'] == 'caution'
        )
        
        if not_recommended_count > 0:
            status = 'not_recommended'
            message = (
                f"This product contains {not_recommended_count} high-risk ingredient(s) "
                f"that may cause adverse reactions. We strongly recommend avoiding this "
                f"product and choosing alternatives without these ingredients."
            )
        elif caution_count >= 3:
            status = 'caution'
            message = (
                f"This product contains {caution_count} ingredients that require caution. "
                f"We recommend patch testing on a small area before full application and "
                f"monitoring for any adverse reactions."
            )
        elif caution_count > 0:
            status = 'caution'
            message = (
                f"This product contains {caution_count} ingredient(s) that may require "
                f"caution. Consider patch testing and use as directed."
            )
        else:
            status = 'safe'
            message = (
                "This product appears safe for your skin type and profile. "
                "No problematic ingredients detected."
            )
        
        return status, message
    
    @classmethod
    def analyze_product(cls, skin_type, sensitivity, allergies, ingredients_string):
        """
        Main analysis method - analyzes complete product.
        
        Args:
            skin_type (str): User's skin type
            sensitivity (str): User's sensitivity level
            allergies (list): List of known allergies
            ingredients_string (str): Product ingredient list
            
        Returns:
            dict: Complete analysis results
        """
        # Parse ingredients
        ingredients = cls.parse_ingredients(ingredients_string)
        
        # Analyze each ingredient
        analyzed_ingredients = [
            cls.analyze_ingredient(ing, skin_type, sensitivity, allergies)
            for ing in ingredients
        ]

        # Identify unsafe ingredients
        unsafe_ingredients = [
            ing['name'] for ing in analyzed_ingredients
            if ing['status'] == 'not_recommended'
        ]

        # Generate LLM explanation
        llm_explanation = LocalLLMService.generate_explanation(
            skin_type,
            sensitivity,
            ingredients,
            unsafe_ingredients
        )
        
        # Separate by status
        flagged = [ing for ing in analyzed_ingredients if ing['status'] != 'safe']
        safe = [ing for ing in analyzed_ingredients if ing['status'] == 'safe']
        
        # Determine overall safety
        overall_status, recommendation = cls.determine_overall_safety(analyzed_ingredients)
        
        # Calculate counts and add boolean flags for convenience
        not_recommended_count = sum(1 for ing in analyzed_ingredients if ing.get('status') == 'not_recommended')
        caution_count = sum(1 for ing in analyzed_ingredients if ing.get('status') == 'caution')

        for ing in analyzed_ingredients:
            ing['is_unsafe'] = (ing.get('status') != 'safe')

        return {
            'overall_safety': overall_status,
            'is_safe': (overall_status == 'safe'),
            'recommendation': recommendation,
            'llm_explanation': llm_explanation,
            'total_ingredients': len(ingredients),
            'flagged_ingredients': flagged,
            'safe_ingredients': safe[:5],  # Return top 5 safe ingredients
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
            'not_recommended_count': not_recommended_count,
            'caution_count': caution_count,
            'analyzed_ingredients': analyzed_ingredients
        }   


# ============================================
# API ENDPOINTS
# ============================================

@app.route('/', methods=['GET'])
def home():
    """Serve the frontend application."""
    return send_from_directory('../front', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from the front directory."""
    return send_from_directory('../front', filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve assets from the assets directory."""
    return send_from_directory('../assets', filename)

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        'status': 'online',
        'service': 'DermaSafe API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/analyze': 'Analyze product safety',
            'GET /api/health': 'Health check',
            'GET /api/ingredients': 'List known ingredients'
        },
        'documentation': 'See README for API usage examples'
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'database_size': len(IngredientDatabase.INGREDIENT_RISKS)
    }), 200


@app.route('/api/ingredients', methods=['GET'])
def list_ingredients():
    """
    List all ingredients in the database.
    Query params:
        - category: filter by category (optional)
        - risk_level: filter by risk level (optional)
    """
    category = request.args.get('category')
    risk_level = request.args.get('risk_level')
    
    ingredients = IngredientDatabase.INGREDIENT_RISKS
    
    # Apply filters if provided
    if category:
        ingredients = {
            k: v for k, v in ingredients.items() 
            if v.get('category') == category
        }
    
    if risk_level:
        ingredients = {
            k: v for k, v in ingredients.items() 
            if v.get('risk_level') == risk_level
        }
    
    return jsonify({
        'count': len(ingredients),
        'ingredients': ingredients
    }), 200


@app.route('/api/scan-image', methods=['POST'])
def scan_image():
    """
    Handle image upload and perform OCR to extract product name.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        import io
        import numpy as np
        from PIL import Image
        
        # Read the uploaded image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL Image to numpy array
        image_np = np.array(image)
        
        # Try to use EasyOCR if available
        try:
            import easyocr
            
            # Initialize reader (cached for performance)
            if not hasattr(scan_image, 'reader'):
                logger.info("Initializing EasyOCR reader (this may take a moment on first run)...")
                scan_image.reader = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR reader initialized successfully")
            
            # Perform OCR
            logger.info("Performing OCR on uploaded image...")
            results = scan_image.reader.readtext(image_np)
            
            if not results:
                raise Exception("No text detected in image")
            
            # Extract text from results
            detected_texts = [text for (bbox, text, confidence) in results if confidence > 0.3]
            
            if not detected_texts:
                raise Exception("No confident text detected")
            
            # Find the most likely product name
            # Look for longer text segments that might be product names
            product_name = extract_product_name(detected_texts)
            
            logger.info(f"OCR detected product name: {product_name}")
            
            return jsonify({
                'status': 'success',
                'product_name': product_name,
                'confidence': 0.85,
                'method': 'ocr'
            })
            
        except ImportError:
            logger.warning("EasyOCR not installed, falling back to simulation mode")
            raise Exception("OCR library not available")
            
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        
        # Fallback to simulation mode
        import time
        import random
        time.sleep(1.0)
        
        detected_products = [
            "Advanced Repair Lotion",
            "Gentle Hydrating Cleanser",
            "Sunscreen SPF 50",
            "Night Recovery Cream",
            "Acne Control Gel"
        ]
        
        detected_name = random.choice(detected_products)
        
        return jsonify({
            'status': 'success',
            'product_name': detected_name,
            'confidence': 0.70,
            'method': 'simulation',
            'note': 'Install EasyOCR for real image recognition: pip install easyocr'
        })


def extract_product_name(texts):
    """
    Extract the most likely product name from OCR results.
    Uses heuristics to identify product names.
    """
    if not texts:
        return "Unknown Product"
    
    # Filter out very short texts (likely noise)
    meaningful_texts = [t for t in texts if len(t.strip()) > 3]
    
    if not meaningful_texts:
        return texts[0] if texts else "Unknown Product"
    
    # Look for common product keywords
    product_keywords = [
        'cream', 'lotion', 'serum', 'gel', 'cleanser', 'moisturizer',
        'sunscreen', 'toner', 'mask', 'oil', 'balm', 'wash', 'scrub',
        'treatment', 'repair', 'hydrating', 'anti-aging', 'acne', 'spf'
    ]
    
    # Score each text based on likelihood of being a product name
    scored_texts = []
    for text in meaningful_texts:
        text_lower = text.lower()
        score = 0
        
        # Longer texts are more likely to be product names
        score += len(text) * 0.5
        
        # Contains product keywords
        for keyword in product_keywords:
            if keyword in text_lower:
                score += 10
        
        # Contains numbers (like SPF 50)
        if any(char.isdigit() for char in text):
            score += 5
        
        # Mixed case suggests a brand/product name
        if any(c.isupper() for c in text) and any(c.islower() for c in text):
            score += 3
        
        scored_texts.append((score, text))
    
    # Sort by score and return the highest
    scored_texts.sort(reverse=True)
    
    # Return the best match, or combine top 2 if they're both good
    if len(scored_texts) >= 2 and scored_texts[0][0] > 10 and scored_texts[1][0] > 10:
        # Combine top 2 results if both seem relevant
        return f"{scored_texts[0][1]} {scored_texts[1][1]}"
    
    return scored_texts[0][1] if scored_texts else meaningful_texts[0]


@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user and send a welcome email."""
    if not request.is_json:
        return jsonify({'error': 'JSON payload required'}), 400
        
    data = request.get_json()
    name = data.get('name')
    email = data.get('email', '').strip().lower()  # Normalize email
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400
        
    if email in users_db:
        return jsonify({'error': 'User already registered'}), 409
        
    # save user
    users_db[email] = {'name': name, 'password': password, 'joined_at': datetime.utcnow().isoformat()}
    save_users(users_db)  # Persist to disk
    
    # Send email (Simulated)
    EmailService.send_welcome_email(email, name)
    
    return jsonify({'status': 'success', 'message': 'Registration successful!'}), 201


@app.route('/api/login', methods=['POST'])
def login_user():
    """Simple login check."""
    if not request.is_json:
        return jsonify({'error': 'JSON payload required'}), 400
        
    data = request.get_json()
    email = data.get('email', '').strip().lower()  # Normalize email
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
        
    user = users_db.get(email)
    
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    return jsonify({
        'status': 'success', 
        'user': {'name': user['name'], 'email': email}
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_product():
    """
    Main analysis endpoint - analyzes product safety.
    
    Request Body (JSON):
    {
        "skin_profile": {
            "skin_type": "sensitive",
            "sensitivity": "moderate",
            "allergies": ["fragrance", "parabens"]
        },
        "product": {
            "name": "Product Name",
            "ingredients": "water, glycerin, fragrance, ..."
        }
    }
    
    Returns:
        JSON response with safety analysis
    """
    # Validate request
    if not request.is_json:
        return jsonify({
            'error': 'Content-Type must be application/json'
        }), 400
    
    data = request.get_json()
    
    # Validate required fields
    if 'skin_profile' not in data or 'product' not in data:
        return jsonify({
            'error': 'Missing required fields: skin_profile and product'
        }), 400
    
    skin_profile = data['skin_profile']
    product = data['product']
    
    # Validate skin profile fields
    required_profile_fields = ['skin_type', 'sensitivity', 'allergies']
    for field in required_profile_fields:
        if field not in skin_profile:
            return jsonify({
                'error': f'Missing required field in skin_profile: {field}'
            }), 400
    
    # Validate product fields
    if 'name' not in product and 'ingredients' not in product:
        return jsonify({
            'error': 'Missing required fields: product name or ingredients'
        }), 400
    
    # If ingredients are missing, try to fetch them
    if not product.get('ingredients') and product.get('name'):
        product['ingredients'] = LocalLLMService.get_ingredients_for_product(product['name'])

    if not product.get('ingredients'):
         return jsonify({
            'error': 'Could not determine ingredients for this product.'
        }), 400
    
    # Validate skin_type
    valid_skin_types = ['normal', 'dry', 'oily', 'combination', 'sensitive']
    if skin_profile['skin_type'] not in valid_skin_types:
        return jsonify({
            'error': f'Invalid skin_type. Must be one of: {", ".join(valid_skin_types)}'
        }), 400
    
    # Validate sensitivity
    valid_sensitivities = ['none', 'mild', 'moderate', 'severe']
    if skin_profile['sensitivity'] not in valid_sensitivities:
        return jsonify({
            'error': f'Invalid sensitivity. Must be one of: {", ".join(valid_sensitivities)}'
        }), 400
    
    # Perform analysis
    try:
        analysis_result = SafetyAnalyzer.analyze_product(
            skin_type=skin_profile['skin_type'],
            sensitivity=skin_profile['sensitivity'],
            allergies=skin_profile['allergies'],
            ingredients_string=product['ingredients']
        )
        
        # Build response
        response = {
            'status': 'success',
            'product_name': product.get('name', 'Unknown Product'),
            'analysis': analysis_result
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


# ============================================
# APPLICATION ENTRY POINT
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("DermaSafe Backend API")
    print("=" * 50)
    print(f"Starting server...")
    print(f"Loaded {len(IngredientDatabase.INGREDIENT_RISKS)} ingredients")
    print(f"Server will run on http://localhost:5000")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
