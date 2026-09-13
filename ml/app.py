import os
import sys

# Configure environment variables to prevent Keras 3 / TensorFlow incompatibility issues in Transformers
# Configure environment variables for memory efficiency on 512MB free tier containers
os.environ["MALLOC_ARENA_MAX"] = "2"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from dotenv import load_dotenv

# Load environment variables from environment.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'environment.env')
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from models.crop_recommender import CropRecommender
from models.borewell_risk import BorewellRiskScorer
from models.price_predictor import PricePredictor
from models.yield_predictor import YieldPredictor
from rag.farm_chat import FarmChat

app = Flask(__name__)
CORS(app)

# Initialize light prediction models
print("Loading AgroPredict ML models...")
crop_model = CropRecommender()
borewell_model = BorewellRiskScorer()
price_model = PricePredictor()
yield_model = YieldPredictor()
farm_chat = FarmChat()
print("AgroPredict ML models loaded successfully!")



@app.route('/ml/health', methods=['GET'])
def health():
    # PricePredictor re-fits LinearRegression on-demand from input price arrays.
    # It has no persistent .pkl file — it is always available as long as sklearn imported.
    price_predictor_ok = price_model is not None
    return jsonify({
        'status': 'ok',
        'service': 'agropredict-ml',
        'brand': 'AgroPredict AI',
        'models': {
            'crop_recommender': crop_model.model is not None,
            'borewell_risk': borewell_model.model is not None,
            'price_predictor': price_predictor_ok,
            'price_predictor_type': 'on-demand-linear-regression',  # no .pkl — fits live
            'yield_predictor': yield_model.model is not None
        }
    })


@app.route('/ml/recommend-crops', methods=['POST'])
def recommend_crops():
    try:
        data = request.json
        crops = crop_model.predict(
            soil_type=data.get('soil_type', 'loam'),
            soil_ph=float(data.get('soil_ph', 6.5)),
            avg_temperature=float(data.get('avg_temperature', 30)),
            rainfall_7day=float(data.get('rainfall_7day', 20)),
            humidity=float(data.get('humidity', 65)),
            month=int(data.get('month', 6)),
            elevation=float(data.get('elevation', 200)),
            state=data.get('state', 'Tamil Nadu')
        )
        return jsonify({'crops': crops})
    except Exception as e:
        print(f"Error in recommend-crops: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/ml/predict-yield', methods=['POST'])
def predict_yield():
    try:
        data = request.json
        result = yield_model.predict(
            crop=data.get('crop', 'rice'),
            soil_type=data.get('soil_type', 'loam'),
            soil_ph=float(data.get('soil_ph', 6.5)),
            avg_temperature=float(data.get('avg_temperature', 30.0)),
            rainfall_7day=float(data.get('rainfall_7day', 50.0)),
            humidity=float(data.get('humidity', 60.0)),
            area_acres=float(data.get('area_acres', 1.0)),
            elevation=float(data.get('elevation', 200.0)),
            state=data.get('state', 'Tamil Nadu'),
            month=int(data.get('month', 6))
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error in predict-yield: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/ml/borewell-risk', methods=['POST'])
def borewell_risk():
    try:
        data = request.json
        result = borewell_model.predict(
            elevation=float(data.get('elevation', 200)),
            soil_depth=float(data.get('soil_depth', 100)),
            clay_content=float(data.get('clay_content', 30)),
            annual_rainfall=float(data.get('annual_rainfall', 800)),
            distance_to_river=float(data.get('distance_to_river', 5)),
            ndvi_score=float(data.get('ndvi_score', 0.4)),
            month=int(data.get('month', 6))
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error in borewell-risk: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/ml/price-trend', methods=['POST'])
def price_trend():
    try:
        data = request.json
        prices = data.get('prices', [])
        result = price_model.predict(prices)
        return jsonify(result)
    except Exception as e:
        print(f"Error in price-trend: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/ml/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('query', data.get('message', ''))
        farm_context = data.get('farm_context', {})

        if not query:
            return jsonify({'error': 'query is required'}), 400

        result = farm_chat.chat(query, farm_context)
        return jsonify(result)
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/ml/chat/init', methods=['POST'])
def chat_init():
    try:
        import importlib
        import rag.farm_chat
        importlib.reload(rag.farm_chat)
        from rag.farm_chat import FarmChat
        global farm_chat
        farm_chat = FarmChat()
        farm_chat.initialize()
        return jsonify({'status': 'ok', 'message': 'Knowledge base and chat engine reloaded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ml/chat/health', methods=['GET'])
def chat_health():
    return jsonify(farm_chat.get_status())


@app.route('/ml/vision', methods=['POST'])
def vision_analyze():
    try:
        from rag.vision_analyzer import VisionAnalyzer
        analyzer = VisionAnalyzer()
        data = request.json or {}
        image_b64 = data.get('image', data.get('image_b64', ''))
        crop_hint = data.get('crop_hint', '')

        if not image_b64:
            return jsonify({'error': 'image data is required'}), 400

        result = analyzer.analyze_image(image_b64, crop_hint)
        return jsonify(result)
    except Exception as e:
        print(f"Error in vision analysis: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

