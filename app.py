from flask import Flask, request, jsonify, render_template_string
from analyzer import calculate_match_score, get_recommendations

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Job Search Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0f1e; color: #fff; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #051535, #0a0f1e); padding: 30px; text-align: center; border-bottom: 1px solid #1a3a6a; }
        .header h1 { font-size: 2rem; color: #00aaff; }
        .header p { color: #888; margin-top: 8px; }
        .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .card { background: #0d1b35; border: 1px solid #1a3a6a; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .card h2 { color: #00aaff; margin-bottom: 16px; font-size: 1.1rem; }
        textarea { width: 100%; background: #071228; border: 1px solid #1a3a6a; border-radius: 8px; color: #fff; padding: 14px; font-size: 14px; resize: vertical; min-height: 150px; outline: none; }
        textarea:focus { border-color: #00aaff; }
        button { background: linear-gradient(135deg, #0066cc, #00aaff); color: white; border: none; padding: 14px 40px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; }
        button:hover { opacity: 0.9; }
        .results { display: none; }
        .score-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
        .score-box { background: #071228; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid #1a3a6a; }
        .score-number { font-size: 2.5rem; font-weight: bold; color: #00aaff; }
        .score-label { color: #888; font-size: 0.85rem; margin-top: 4px; }
        .skills-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .skill-tag { display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 13px; margin: 4px; }
        .matched { background: rgba(0,255,150,0.15); border: 1px solid rgba(0,255,150,0.4); color: #00ff96; }
        .missing { background: rgba(255,80,80,0.15); border: 1px solid rgba(255,80,80,0.4); color: #ff6b6b; }
        .rec-item { background: #071228; border-left: 3px solid #00aaff; padding: 12px 16px; border-radius: 0 8px 8px 0; margin-bottom: 10px; font-size: 14px; color: #ccc; }
        .loading { text-align: center; color: #00aaff; padding: 20px; display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Job Search Assistant</h1>
        <p>Built by Avinash Bolligarla &mdash; MS IT Management, Webster University</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Paste Your Resume</h2>
            <textarea id="resume" placeholder="Paste your resume text here..."></textarea>
        </div>
        <div class="card">
            <h2>Paste Job Description</h2>
            <textarea id="jobdesc" placeholder="Paste the job description here..."></textarea>
        </div>
        <button onclick="analyze()">Analyze Match</button>
        <div class="loading" id="loading">Analyzing your resume...</div>
        <div class="results" id="results">
            <br>
            <div class="score-grid">
                <div class="score-box">
                    <div class="score-number" id="matchScore">0%</div>
                    <div class="score-label">Match Score</div>
                </div>
                <div class="score-box">
                    <div class="score-number" id="atsScore">0%</div>
                    <div class="score-label">ATS Score</div>
                </div>
            </div>
            <div class="card">
                <h2>Recommendations</h2>
                <div id="recommendations"></div>
            </div>
            <div class="skills-grid">
                <div class="card">
                    <h2>Matched Skills</h2>
                    <div id="matchedSkills"></div>
                </div>
                <div class="card">
                    <h2>Missing Skills</h2>
                    <div id="missingSkills"></div>
                </div>
            </div>
        </div>
    </div>
    <script>
        async function analyze() {
            const resume = document.getElementById('resume').value;
            const jobdesc = document.getElementById('jobdesc').value;
            if (!resume || !jobdesc) { alert('Please fill both fields!'); return; }
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume: resume, job_description: jobdesc })
            });
            const data = await response.json();
            document.getElementById('loading').style.display = 'none';
            document.getElementById('results').style.display = 'block';
            document.getElementById('matchScore').textContent = data.match_score + '%';
            document.getElementById('atsScore').textContent = data.ats_score + '%';
            document.getElementById('recommendations').innerHTML = data.recommendations.map(r => `<div class="rec-item">${r}</div>`).join('');
            document.getElementById('matchedSkills').innerHTML = data.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join('');
            document.getElementById('missingSkills').innerHTML = data.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join('');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume_text = data.get('resume', '')
    job_description = data.get('job_description', '')
    
    if not resume_text or not job_description:
        return jsonify({'error': 'Both resume and job description are required'}), 400
    
    results = calculate_match_score(resume_text, job_description)
    recommendations = get_recommendations(results['missing_skills'], results['match_score'])
    
    return jsonify({
        'match_score': results['match_score'],
        'ats_score': results['ats_score'],
        'matched_skills': results['matched_skills'],
        'missing_skills': results['missing_skills'],
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)