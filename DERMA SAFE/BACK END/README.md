# DermaSafe Backend API

A production-ready Flask REST API for skin-type based product safety detection. Analyzes cosmetic ingredients against user skin profiles to provide personalized safety recommendations.

## 🌟 Features

- **Personalized Analysis**: Evaluates products based on individual skin type and sensitivities
- **Comprehensive Database**: 28+ known problematic ingredients with risk classifications
- **Smart Risk Calculation**: Considers skin type, sensitivity level, and user allergies
- **RESTful API**: Clean, well-documented endpoints
- **Extensible Architecture**: Easy to add new ingredients and customize logic
- **Production Ready**: Proper error handling, validation, and CORS support

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project files**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python app.py
```

The API will start on `http://localhost:5000`

You should see:
```
==================================================
DermaSafe Backend API
==================================================
Starting server...
Loaded 28 ingredients
Server will run on http://localhost:5000
==================================================
```

### Verify Installation

Open a new terminal and run:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-09T10:30:00Z",
  "database_size": 28
}
```

### Verify Installation

Run the test suite to verify everything is working:
```bash
python test_llm_service.py
```

You should see all tests pass, confirming the system is ready!

## 🤖 AI-Powered Features (Optional)

DermaSafe includes **intelligent LLM integration** that enhances the analysis with AI-generated insights:

### What Works Out of the Box

✅ **The system works perfectly WITHOUT any additional setup!**
- Product safety analysis
- Ingredient detection
- Risk assessment
- Template-based explanations

### Enhanced AI Features (Optional)

For even better results, you can optionally install **Ollama** to enable:
- 🧠 AI-generated ingredient predictions for unknown products
- 💬 Natural, personalized dermatologist explanations
- 🎯 More intelligent and context-aware responses

**To enable AI features:**
1. See `OLLAMA_SETUP.md` for detailed installation instructions
2. The system automatically detects and uses Ollama when available
3. If Ollama is not available, it seamlessly falls back to template-based responses

**Test Ollama integration:**
```bash
python test_ollama.py
```

**Note:** Whether you use Ollama or not, DermaSafe will work perfectly. The AI features are an enhancement, not a requirement!

## 📖 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
```
GET /api/health
```

#### 2. List Ingredients
```
GET /api/ingredients
GET /api/ingredients?category=fragrance
GET /api/ingredients?risk_level=high
```

#### 3. Analyze Product (Main Endpoint)
```
POST /api/analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "skin_profile": {
    "skin_type": "sensitive",
    "sensitivity": "moderate",
    "allergies": ["fragrance", "parabens"]
  },
  "product": {
    "name": "Hydrating Cleanser",
    "ingredients": "Water, Glycerin, Sodium Lauryl Sulfate, Fragrance, Niacinamide"
  }
}
```

**Valid Values:**
- `skin_type`: "normal", "dry", "oily", "combination", "sensitive"
- `sensitivity`: "none", "mild", "moderate", "severe"
- `allergies`: ["fragrance", "parabens", "sulfates", "alcohols", "essential-oils", "retinoids"]

**Response:**
```json
{
  "status": "success",
  "product_name": "Hydrating Cleanser",
  "analysis": {
    "overall_safety": "not_recommended",
    "recommendation": "This product contains 2 high-risk ingredient(s)...",
    "total_ingredients": 5,
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
        "concerns": ["allergic reactions", "irritation"],
        "reason": "Known allergen for you",
        "category": "fragrance"
      }
    ],
    "safe_ingredients": [
      {
        "name": "Water",
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

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

The test suite includes:
- ✓ Health check validation
- ✓ Ingredient listing
- ✓ Safe product analysis
- ✓ Caution product analysis
- ✓ Not recommended product analysis
- ✓ Input validation errors

### Manual Testing Examples

**Test a safe product:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "skin_profile": {
      "skin_type": "normal",
      "sensitivity": "none",
      "allergies": []
    },
    "product": {
      "name": "Gentle Moisturizer",
      "ingredients": "Water, Glycerin, Hyaluronic Acid, Niacinamide"
    }
  }'
```

**Test a problematic product:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "skin_profile": {
      "skin_type": "sensitive",
      "sensitivity": "severe",
      "allergies": ["fragrance", "sulfates"]
    },
    "product": {
      "name": "Foaming Cleanser",
      "ingredients": "Water, Sodium Lauryl Sulfate, Fragrance, Glycerin"
    }
  }'
```

## 🏗️ Architecture

### Project Structure
```
.
├── app.py                    # Main Flask application
├── llm_service.py            # LLM integration with Ollama fallback
├── requirements.txt          # Python dependencies
├── test_api.py               # API test suite
├── test_llm_service.py       # LLM service test suite
├── test_ollama.py            # Ollama connection test
├── users.json                # User database (created on first registration)
├── API_DOCUMENTATION.md      # Detailed API docs
├── OLLAMA_SETUP.md           # Ollama installation guide
└── README.md                 # This file
```

### Core Components

1. **IngredientDatabase**
   - Central repository of ingredient safety data
   - 28+ problematic ingredients with risk profiles
   - Categorized by type (fragrance, paraben, sulfate, etc.)

2. **SafetyAnalyzer**
   - Parses ingredient lists
   - Analyzes individual ingredients against user profile
   - Calculates risk scores with sensitivity multipliers
   - Determines overall product safety

3. **LocalLLMService**
   - Intelligent LLM integration with automatic fallback
   - Uses Ollama (llama3) when available for AI-powered responses
   - Generates ingredient predictions for unknown products
   - Creates personalized dermatologist explanations
   - Seamlessly falls back to template-based responses if Ollama unavailable

4. **Flask Routes**
   - `/api/health` - Health monitoring
   - `/api/ingredients` - Ingredient database access
   - `/api/analyze` - Main analysis endpoint
   - `/api/register` - User registration
   - `/api/login` - User authentication
   - `/api/scan-image` - Image-based product detection

### Risk Calculation Logic

```
Base Risk Score (0-4) 
  × Sensitivity Multiplier (1.0-2.0)
  + Allergen Penalty (+2 if matches user allergy)
  + Skin Type Penalty (if ingredient affects user's skin type)
= Final Risk Score
```

**Safety Classification:**
- `safe`: No high-risk ingredients
- `caution`: 1-2 moderate risk ingredients
- `not_recommended`: 1+ high-risk or allergen ingredients

## 🔧 Customization

### Adding New Ingredients

Edit `app.py` and add to `IngredientDatabase.INGREDIENT_RISKS`:

```python
'new_ingredient': {
    'risk_level': 'moderate',  # safe, low, moderate, high, severe
    'concerns': ['irritation', 'dryness'],
    'affected_skin_types': ['sensitive', 'dry'],
    'category': 'preservative'
}
```

### Modifying Risk Logic

Customize `SafetyAnalyzer.analyze_ingredient()` to change how risks are calculated.

### Adding Authentication

Uncomment and configure authentication in `app.py`:

```python
@app.route('/api/analyze', methods=['POST'])
@require_api_key  # Add this decorator
def analyze_product():
    # ... existing code
```

## 📦 Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

Create a `.env` file:
```env
FLASK_ENV=production
PORT=5000
SECRET_KEY=your-secret-key-here
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t dermasafe-api .
docker run -p 5000:5000 dermasafe-api
```

## 🔐 Security Considerations

- **Input Validation**: All inputs are validated before processing
- **CORS**: Configured for cross-origin requests (adjust for production)
- **Rate Limiting**: Consider adding rate limiting for production
- **Authentication**: Add API keys or OAuth for production use
- **HTTPS**: Always use HTTPS in production

## 📊 Database Information

### Ingredient Categories
- Fragrances (2 ingredients)
- Alcohols (3 ingredients)
- Sulfates (4 ingredients)
- Parabens (3 ingredients)
- Essential Oils (4 ingredients)
- Retinoids (3 ingredients)
- Acids (3 ingredients)
- Preservatives (2 ingredients)
- Oils/Emollients (2 ingredients)

### Risk Levels
- **High Risk**: Ingredients likely to cause reactions
- **Moderate Risk**: Ingredients requiring caution
- **Low Risk**: Generally safe with minor concerns

## 🐛 Troubleshooting

**Server won't start:**
- Check if port 5000 is already in use
- Verify Python version (3.8+)
- Ensure all dependencies are installed

**API returns errors:**
- Check request JSON format
- Verify required fields are present
- Review error message in response

**Tests fail:**
- Ensure server is running before running tests
- Check if requests library is installed

## 📝 License

This is a demonstration project. Feel free to use and modify for your needs.

## 🤝 Contributing

To extend this API:
1. Add ingredients to the database
2. Enhance risk calculation logic
3. Add new endpoints
4. Improve test coverage

## 📞 Support

For questions or issues:
- Review the API_DOCUMENTATION.md file
- Check the inline code comments
- Examine the test_api.py examples

---

**Version:** 1.0.0  
**Last Updated:** February 2024  
**Python Version:** 3.8+  
**Framework:** Flask 3.0.0
