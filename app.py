from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create uploads folder
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Lazy loading - don't initialize at startup
_agent = None
_resume_parser = None

def get_agent():
    """Initialize agent only on first request"""
    global _agent
    if _agent is None:
        logger.info("🤖 Initializing AI Agent...")
        from agent.graph import create_agent_graph
        _agent = create_agent_graph()
        logger.info("✅ Agent ready!")
    return _agent

def get_resume_parser():
    """Initialize parser only when needed"""
    global _resume_parser
    if _resume_parser is None:
        logger.info("📄 Initializing resume parser...")
        from parsers.resume_parser import ResumeParser
        _resume_parser = ResumeParser()
    return _resume_parser

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check for Render"""
    return jsonify({'status': 'healthy', 'message': 'AI Resume Agent is running'}), 200

@app.route('/test')
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is working',
        'agent_loaded': _agent is not None
    }), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process resume and job description"""
    logger.info("📥 Received analyze request")
    
    try:
        # Get lazy-loaded components
        logger.info("Loading components...")
        agent = get_agent()
        resume_parser = get_resume_parser()
        
        # Get job description
        job_description = request.form.get('job_description', '').strip()
        logger.info(f"Job description length: {len(job_description)}")
        
        if not job_description:
            logger.warning("No job description provided")
            return jsonify({'error': 'Job description is required'}), 400
        
        # Get resume text
        resume_text = ''
        
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                logger.info(f"Processing file: {file.filename}")
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    resume_text = resume_parser.parse(filepath)
                    logger.info(f"Parsed resume, length: {len(resume_text)}")
                except Exception as e:
                    logger.error(f"Resume parsing error: {str(e)}")
                    return jsonify({'error': f'Error parsing resume: {str(e)}'}), 400
                finally:
                    if os.path.exists(filepath):
                        os.remove(filepath)
        
        # Fallback to text input
        if not resume_text:
            resume_text = request.form.get('resume_text', '').strip()
            logger.info(f"Using text input, length: {len(resume_text)}")
        
        if not resume_text:
            logger.warning("No resume provided")
            return jsonify({'error': 'Resume is required (file or text)'}), 400
        
        # Create initial state
        logger.info("Creating initial state...")
        initial_state = {
            'resume_text': resume_text,
            'job_description': job_description,
            'resume_skills': [],
            'job_skills': [],
            'matched_skills': [],
            'missing_skills': [],
            'match_percentage': 0.0,
            'rag_context': '',
            'recommendations': '',
            'final_report': '',
            'current_step': 'start',
            'errors': []
        }
        
        # Run agent
        logger.info("🚀 Invoking agent workflow...")
        result = agent.invoke(initial_state)
        logger.info("✅ Agent completed successfully")
        
        # Build response
        response = {
            'success': True,
            'match_percentage': float(result.get('match_percentage', 0.0)),
            'matched_skills': result.get('matched_skills', []),
            'missing_skills': result.get('missing_skills', []),
            'resume_skills': result.get('resume_skills', []),
            'job_skills': result.get('job_skills', []),
            'rag_context': str(result.get('rag_context', ''))[:500],
            'recommendations': str(result.get('recommendations', 'No recommendations available')),
            'report': str(result.get('final_report', 'No report available'))
        }
        
        logger.info(f"📊 Match: {response['match_percentage']}%")
        logger.info("Sending response...")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"❌ ERROR in /analyze: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)