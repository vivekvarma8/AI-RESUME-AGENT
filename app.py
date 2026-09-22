from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Lazy loading - don't initialize at startup
_agent = None
_resume_parser = None

def get_agent():
    """Initialize agent only on first request"""
    global _agent
    if _agent is None:
        print("🤖 Initializing AI Agent...")
        from agent.graph import create_agent_graph
        _agent = create_agent_graph()
        print("✅ Agent ready!")
    return _agent

def get_resume_parser():
    """Initialize parser only when needed"""
    global _resume_parser
    if _resume_parser is None:
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
    return jsonify({'status': 'healthy'}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process resume and job description"""
    try:
        # Get lazy-loaded components
        agent = get_agent()
        resume_parser = get_resume_parser()
        
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        resume_text = ''
        
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    resume_text = resume_parser.parse(filepath)
                except Exception as e:
                    return jsonify({'error': f'Error parsing resume: {str(e)}'}), 400
                finally:
                    if os.path.exists(filepath):
                        os.remove(filepath)
        
        if not resume_text:
            resume_text = request.form.get('resume_text', '').strip()
        
        if not resume_text:
            return jsonify({'error': 'Resume is required (file or text)'}), 400
        
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
        
        result = agent.invoke(initial_state)
        
        response = {
            'success': True,
            'match_percentage': result['match_percentage'],
            'matched_skills': result['matched_skills'],
            'missing_skills': result['missing_skills'],
            'resume_skills': result['resume_skills'],
            'job_skills': result['job_skills'],
            'rag_context': result['rag_context'][:500],
            'recommendations': result.get('recommendations', 'No recommendations available'),
            'report': result['final_report']
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)