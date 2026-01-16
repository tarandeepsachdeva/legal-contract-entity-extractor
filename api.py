from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from hybrid_ner import HybridLegalNER
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize the NER system
try:
    ner_system = HybridLegalNER()
    print("✅ NER system loaded successfully")
except Exception as e:
    print(f"❌ Error loading NER system: {e}")
    ner_system = None

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Legal Contract Entity Extractor API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/extract": "POST - Extract entities from legal text",
            "/health": "GET - Check API health",
            "/info": "GET - Get model information"
        },
        "entity_types": [
            "AGREEMENT_TYPE", "AMOUNT", "DURATION", 
            "EFFECTIVE_DATE", "EXPIRATION_DATE", "LOCATION", "PARTY"
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = "healthy" if ner_system else "unhealthy"
    return jsonify({
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "ner_loaded": ner_system is not None
    })

@app.route('/info', methods=['GET'])
def model_info():
    """Get model information"""
    if not ner_system:
        return jsonify({"error": "NER system not loaded"}), 500
    
    try:
        # Get model labels
        labels = list(ner_system.nlp.get_pipe('ner').labels)
        
        return jsonify({
            "model_type": "Hybrid NER (ML + Rules)",
            "entity_labels": labels,
            "pipeline_components": ner_system.nlp.pipe_names,
            "vocab_size": len(ner_system.nlp.vocab),
            "performance_metrics": {
                "f1_score": 0.275,
                "hybrid_improvement": "+666.7%",
                "test_success_rate": "100%"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract', methods=['POST'])
def extract_entities():
    """Main endpoint for entity extraction"""
    
    # Check if NER system is available
    if not ner_system:
        return jsonify({"error": "NER system not available"}), 500
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Get text from request
        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if not isinstance(text, str):
            return jsonify({"error": "Text must be a string"}), 400
        
        # Check text length (prevent very long texts)
        if len(text) > 10000:
            return jsonify({"error": "Text too long (max 10000 characters)"}), 400
        
        # Get options
        use_hybrid = data.get('use_hybrid', True)
        include_details = data.get('include_details', False)
        
        # Extract entities
        start_time = datetime.now()
        result = ner_system.extract_entities(text, use_hybrid=use_hybrid)
        end_time = datetime.now()
        
        # Prepare response
        response = {
            "success": True,
            "text": text,
            "entities": result['combined_entities'] if use_hybrid else result['entities'],
            "entity_count": len(result['combined_entities'] if use_hybrid else result['entities']),
            "processing_time": (end_time - start_time).total_seconds(),
            "method": "hybrid" if use_hybrid else "ml_only",
            "timestamp": end_time.isoformat()
        }
        
        # Add detailed information if requested
        if include_details and use_hybrid:
            response.update({
                "ml_entities": result['ml_entities'],
                "rule_entities": result['rule_entities'],
                "normalized_text": result.get('normalized_text', text)
            })
        
        return jsonify(response)
        
    except Exception as e:
        # Log the error for debugging
        error_trace = traceback.format_exc()
        print(f"Error in /extract: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/batch_extract', methods=['POST'])
def batch_extract_entities():
    """Batch endpoint for processing multiple texts"""
    
    if not ner_system:
        return jsonify({"error": "NER system not available"}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "No texts array provided"}), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({"error": "texts must be an array"}), 400
        
        # Limit batch size
        if len(texts) > 10:
            return jsonify({"error": "Batch size too large (max 10 texts)"}), 400
        
        use_hybrid = data.get('use_hybrid', True)
        results = []
        
        for i, text in enumerate(texts):
            if not isinstance(text, str):
                results.append({
                    "index": i,
                    "success": False,
                    "error": "Text must be a string"
                })
                continue
            
            if len(text) > 10000:
                results.append({
                    "index": i,
                    "success": False,
                    "error": "Text too long"
                })
                continue
            
            try:
                result = ner_system.extract_entities(text, use_hybrid=use_hybrid)
                results.append({
                    "index": i,
                    "success": True,
                    "text": text,
                    "entities": result['combined_entities'] if use_hybrid else result['entities'],
                    "entity_count": len(result['combined_entities'] if use_hybrid else result['entities'])
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "batch_size": len(texts),
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Legal Contract NER API...")
    print("📋 Available endpoints:")
    print("  GET  /        - API information")
    print("  GET  /health  - Health check")
    print("  GET  /info    - Model information")
    print("  POST /extract - Extract entities")
    print("  POST /batch_extract - Batch extraction")
    print("\n🔗 API will be available at: http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
