from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

app = Flask(__name__)

GRADE_SCALE = {
    97: ("A+", "Outstanding!", 4.0), 93: ("A", "Excellent!", 4.0), 90: ("A-", "Great!", 3.7),
    87: ("B+", "Very good!", 3.3), 83: ("B", "Good!", 3.0), 80: ("B-", "Decent!", 2.7),
    77: ("C+", "Fair!", 2.3), 73: ("C", "Average!", 2.0), 70: ("C-", "Passing!", 1.7),
    67: ("D+", "Below avg!", 1.3), 63: ("D", "Poor!", 1.0), 60: ("D-", "Barely!", 0.7),
    0: ("F", "Failed!", 0.0)
}

def determine_grade(score):
    for threshold in sorted(GRADE_SCALE.keys(), reverse=True):
        if score >= threshold:
            return GRADE_SCALE[threshold]
    return ("F", "Failed!", 0.0)

HTML_TEMPLATE = """<!DOCTYPE html><html><head><title>Grader 5106</title><style>
body{font-family:Arial;max-width:600px;margin:50px auto;background:#f5f5f5}
.container{background:white;padding:30px;border-radius:8px}h1{color:#4c3f91}
input,button{padding:10px;margin:10px 0;width:100%;border:1px solid #ddd;border-radius:4px}
button{background:#667eea;color:white;cursor:pointer;border:none}button:hover{background:#4c3f91}
.result{margin-top:30px;padding:20px;background:#e8f4fd;border-radius:4px;display:none}
.result.show{display:block}.grade{font-size:36px;color:#4c3f91;font-weight:bold}
</style></head><body><div class="container"><h1>📊 Server 5106</h1>
<form id="f"><input type="text" id="n" placeholder="Name"><input type="text" id="s" placeholder="Subject">
<input type="number" id="sc" placeholder="Score" min="0" max="100" required>
<button type="submit">Grade</button></form>
<div id="r" class="result"><div class="grade" id="g"></div><p id="fb"></p></div></div>
<script>document.getElementById('f').addEventListener('submit',async(e)=>{
e.preventDefault();const r=await fetch('/api/grade',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({score:parseFloat(document.getElementById('sc').value),name:document.getElementById('n').value,subject:document.getElementById('s').value})});
const d=await r.json();document.getElementById('g').textContent=d.letter_grade;
document.getElementById('fb').textContent='Score: '+d.score+'/100 | GPA: '+d.gpa.toFixed(2);
document.getElementById('r').classList.add('show');});</script></body></html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/grade', methods=['POST'])
def grade_test():
    data = request.json
    score = float(data.get('score', 0))
    letter_grade, feedback, gpa = determine_grade(score)
    return jsonify({'score': score, 'letter_grade': letter_grade, 'feedback': feedback, 'gpa': gpa})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5106, debug=False)
