# DermaSafe Backend API Documentation

## Overview
The DermaSafe Backend API provides skin-type based product safety analysis. It evaluates cosmetic ingredients against user skin profiles to provide personalized safety recommendations.

## Quick Start

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-09T10:30:00Z",
  "database_size": 28
}
```

---

### 2. List Ingredients
**GET** `/api/ingredients`

Get all ingredients in the database. Supports optional filtering.

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "fragrance", "paraben", "sulfate")
- `risk_level` (optional): Filter by risk level (e.g., "low", "moderate", "high")

**Example Request:**
```bash
curl http://localhost:5000/api/ingredients?category=fragrance
```

**Response:**
```json
{
  "count": 2,
  "ingredients": {
    "fragrance": {
      "risk_level": "high",
      "concerns": ["allergic reactions", "irritation", "sensitivity"],
      "affected_skin_types": ["sensitive", "dry"],
      "category": "fragrance"
    },
    "parfum": {
      "risk_level": "high",
      "concerns": ["allergic reactions", "irritation", "sensitivity"],
      "affected_skin_types": ["sensitive", "dry"],
      "category": "fragrance"
    }
  }
}
```

---

### 3. Analyze Product Safety
**POST** `/api/analyze`

Analyze a product's ingredient list against a user's skin profile.

**Request Body:**
```json
{
  "skin_profile": {
    "skin_type": "sensitive",
    "sensitivity": "moderate",
    "allergies": ["fragrance", "parabens"]
  },
  "product": {
    "name": "Hydrating Face Wash",
    "ingredients": "Water, Glycerin, Sodium Lauryl Sulfate, Fragrance, Methylparaben, Niacinamide, Ceramide"
  }
}
```

**Field Descriptions:**

`skin_profile` (required):
- `skin_type` (string, required): One of: "normal", "dry", "oily", "combination", "sensitive"
- `sensitivity` (string, required): One of: "none", "mild", "moderate", "severe"
- `allergies` (array, required): List of allergen categories. Examples: "fragrance", "parabens", "sulfates", "alcohols", "essential-oils", "retinoids"

`product` (required):
- `name` (string, optional): Product name for reference
- `ingredients` (string, required): Comma-separated list of ingredients

**Success Response (200 OK):**
```json
{
  "status": "success",
  "product_name": "Hydrating Face Wash",
  "analysis": {
    "overall_safety": "not_recommended",
    "recommendation": "This product contains 2 high-risk ingredient(s) that may cause adverse reactions. We strongly recommend avoiding this product and choosing alternatives without these ingredients.",
    "total_ingredients": 7,
    "flagged_ingredients": [
      {
        "name": "Sodium Lauryl Sulfate",
        "risk_level": "moderate",
        "status": "caution",
        "concerns": ["dryness", "irritation", "oil stripping"],
        "reason": "May cause dryness, irritation",
        "category": "sulfate"
      },
      {
        "name": "Fragrance",
        "risk_level": "high",
        "status": "not_recommended",
        "concerns": ["allergic reactions", "irritation", "sensitivity"],
        "reason": "Known allergen for you",
        "category": "fragrance"
      },
      {
        "name": "Methylparaben",
        "risk_level": "moderate",
        "status": "not_recommended",
        "concerns": ["hormone disruption", "allergic reactions"],
        "reason": "Known allergen for you",
        "category": "paraben"
      }
    ],
    "safe_ingredients": [
      {
        "name": "Water",
        "risk_level": "safe",
        "status": "safe",
        "concerns": [],
        "reason": "Generally considered safe"
      },
      {
        "name": "Glycerin",
        "risk_level": "safe",
        "status": "safe",
        "concerns": [],
        "reason": "Generally considered safe"
      },
      {
        "name": "Niacinamide",
        "risk_level": "safe",
        "status": "safe",
        "concerns": [],
        "reason": "Generally considered safe"
      },
      {
        "name": "Ceramide",
        "risk_level": "safe",
        "status": "safe",
        "concerns": [],
        "reason": "Generally considered safe"
      }
    ],
    "analysis_timestamp": "2024-02-09T10:35:22.123456Z"
  }
}
```

**Overall Safety Values:**
- `"safe"`: Product is safe for the user's skin profile
- `"caution"`: Product contains ingredients that require caution
- `"not_recommended"`: Product contains high-risk ingredients

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required fields: skin_profile and product"
}
```

```json
{
  "error": "Invalid skin_type. Must be one of: normal, dry, oily, combination, sensitive"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Analysis failed",
  "message": "Error details here"
}
```

---

## Example API Usage

### Using cURL

```bash
# Analyze a product
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "skin_profile": {
      "skin_type": "dry",
      "sensitivity": "mild",
      "allergies": ["sulfates"]
    },
    "product": {
      "name": "Gentle Cleanser",
      "ingredients": "Water, Glycerin, Cetyl Alcohol, Niacinamide, Hyaluronic Acid, Ceramide"
    }
  }'
```

### Using Python Requests

```python
import requests

url = "http://localhost:5000/api/analyze"

payload = {
    "skin_profile": {
        "skin_type": "sensitive",
        "sensitivity": "moderate",
        "allergies": ["fragrance", "essential-oils"]
    },
    "product": {
        "name": "Moisturizing Cream",
        "ingredients": "Water, Glycerin, Shea Butter, Squalane, Ceramide, Niacinamide"
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

### Using JavaScript (Fetch API)

```javascript
const analyzeProduct = async () => {
  const response = await fetch('http://localhost:5000/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      skin_profile: {
        skin_type: 'oily',
        sensitivity: 'none',
        allergies: []
      },
      product: {
        name: 'Oil Control Serum',
        ingredients: 'Water, Niacinamide, Salicylic Acid, Glycerin, Hyaluronic Acid'
      }
    })
  });
  
  const data = await response.json();
  console.log(data);
};

analyzeProduct();
```

---

## Supported Allergen Categories

When specifying allergies in the `skin_profile`, use these category values:

- `"fragrance"` - Fragrances and perfumes
- `"parabens"` - Paraben preservatives
- `"sulfates"` - Sulfate surfactants (SLS, SLES)
- `"alcohols"` - Drying alcohols
- `"essential-oils"` - Essential oils
- `"retinoids"` - Retinol and retinoid derivatives
- `"acid"` - Chemical exfoliants (AHA, BHA)
- `"preservative"` - Various preservatives

---

## Architecture Overview

### Components

1. **IngredientDatabase**: Static database of ingredient safety information
2. **SafetyAnalyzer**: Analysis engine that evaluates ingredients against user profiles
3. **Flask Routes**: REST API endpoints

### Analysis Logic

The safety analysis follows this workflow:

1. **Parse Ingredients**: Split ingredient string into individual components
2. **Individual Analysis**: Each ingredient is evaluated:
   - Check against ingredient database
   - Apply skin type compatibility
   - Apply sensitivity multiplier
   - Check for user-specific allergies
   - Calculate risk score
3. **Overall Assessment**: Determine product-level safety based on:
   - Count of high-risk ingredients
   - Count of moderate-risk ingredients
   - User's sensitivity level
4. **Generate Recommendation**: Provide actionable recommendation

### Risk Scoring System

- Base risk levels: safe (0), low (1), moderate (2), high (3), severe (4)
- Sensitivity multipliers: none (1.0x), mild (1.3x), moderate (1.6x), severe (2.0x)
- Allergen penalty: +2 to risk score
- Skin type matching: Applies sensitivity multiplier

---

## Testing

### Test Scenarios

#### Scenario 1: Safe Product
```json
{
  "skin_profile": {
    "skin_type": "normal",
    "sensitivity": "none",
    "allergies": []
  },
  "product": {
    "name": "Gentle Moisturizer",
    "ingredients": "Water, Glycerin, Hyaluronic Acid, Niacinamide, Ceramide"
  }
}
```
Expected: `overall_safety: "safe"`

#### Scenario 2: Product with Caution
```json
{
  "skin_profile": {
    "skin_type": "dry",
    "sensitivity": "mild",
    "allergies": []
  },
  "product": {
    "name": "Exfoliating Toner",
    "ingredients": "Water, Glycolic Acid, Alcohol Denat, Niacinamide"
  }
}
```
Expected: `overall_safety: "caution"`

#### Scenario 3: Not Recommended Product
```json
{
  "skin_profile": {
    "skin_type": "sensitive",
    "sensitivity": "severe",
    "allergies": ["fragrance", "parabens"]
  },
  "product": {
    "name": "Scented Lotion",
    "ingredients": "Water, Fragrance, Methylparaben, Alcohol Denat"
  }
}
```
Expected: `overall_safety: "not_recommended"`

---

## Extending the System

### Adding New Ingredients

Edit the `IngredientDatabase.INGREDIENT_RISKS` dictionary in `app.py`:

```python
'new_ingredient': {
    'risk_level': 'moderate',  # safe, low, moderate, high, severe
    'concerns': ['concern1', 'concern2'],
    'affected_skin_types': ['sensitive', 'dry'],
    'category': 'category_name'
}
```

### Customizing Risk Logic

Modify the `SafetyAnalyzer.analyze_ingredient()` method to add custom risk calculation logic.

### Adding Authentication

To add API key authentication:

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'AIzaSyBz0aWv7t8vE0tuR5FPdZ5jIKfbqnEs-4A':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Apply to endpoints
@app.route('/api/analyze', methods=['POST'])
@require_api_key
def analyze_product():
    # ... existing code
```

---

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

Create a `.env` file:
```
FLASK_ENV=production
PORT=5000
```

---

## Support

For issues or questions about the API, refer to the code comments or extend the functionality as needed.

**Version:** 1.0.0  
**Last Updated:** February 2024
