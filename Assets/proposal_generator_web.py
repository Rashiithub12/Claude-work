"""
Upwork Proposal Generator - Web Interface
Run this and open http://localhost:5000 in your browser

Install required package first:
pip install flask
"""

from flask import Flask, render_template_string, request
import re
import random

app = Flask(__name__)

# ============================================
# PROPOSAL TEMPLATES BASED ON RESEARCH
# ============================================

TEMPLATES = {
    "data_annotation": {
        "openers": [
            "I noticed you need help with {main_task}. I have annotated similar datasets before with 98%+ accuracy and understand how important clean labels are for your project.",
            "{main_task} is exactly what I have been doing recently. I can start immediately and deliver quality work.",
            "Your annotation project caught my attention. I have experience with similar labeling tasks and know what quality output looks like."
        ],
        "questions": [
            "Quick question: do you have annotation guidelines ready or should I follow standard practices?",
            "What format do you need for the final output?",
            "Is there a specific tool or platform you prefer for this work?"
        ]
    },
    "virtual_assistant": {
        "openers": [
            "You need someone reliable for {main_task}. That is exactly what I do. I respond fast, follow instructions carefully, and handle tasks without needing constant supervision.",
            "I understand you are looking for help with {main_task}. I have supported similar clients and they appreciate that I just get things done.",
            "{main_task} requires someone organized and responsive. I can manage these tasks efficiently while keeping you updated."
        ],
        "questions": [
            "What timezone are you in? I want to make sure my availability aligns with yours.",
            "Do you prefer email, chat, or calls for communication?",
            "What tools or software are you currently using?"
        ]
    },
    "web_research": {
        "openers": [
            "You need accurate {main_task}. I have built similar lists before and I verify every entry before delivering.",
            "Finding quality {main_task} requires systematic research. I know the sources and methods that produce reliable results.",
            "I have done this exact type of research work. Clean, verified data is what I deliver."
        ],
        "questions": [
            "What specific fields do you need for each entry?",
            "Do you have preferred sources or should I use my standard methods?",
            "How should I handle entries where some information is unavailable?"
        ]
    },
    "data_entry": {
        "openers": [
            "I can handle your {main_task} accurately and quickly. I type fast and double check everything before submitting.",
            "{main_task} with zero errors is what I deliver. I have done similar projects and understand the importance of accuracy.",
            "I have experience with exactly this type of data entry. Clean formatting, no mistakes, on time delivery."
        ],
        "questions": [
            "What is the source format and where should the data be entered?",
            "Are there specific formatting rules I should follow?",
            "What is your expected daily or weekly volume?"
        ]
    }
}

EXPERIENCE_TEMPLATES = {
    "with": [
        "I recently finished a similar project where I {experience}. The client was satisfied with my work.",
        "In my previous project, I {experience}. I bring the same quality approach to every job.",
        "I have {experience} before and know what good results look like."
    ],
    "without": [
        "While I am building my experience in this specific area, I have strong attention to detail and learn quickly. I am ready to prove my quality with a test task.",
        "I would love to take on this project and deliver great work. I am happy to do a small paid sample first so you can see my quality.",
        "This is a great fit for my skills. I am committed to delivering quality and would welcome a trial task to demonstrate that."
    ]
}

CLOSINGS = [
    "Can we start with a small test batch? That way you can check my quality before committing to the full project.",
    "I am available to start today. Would a sample task work as a first step?",
    "Let me know if you have questions about my approach. Happy to jump on a quick call or discuss here.",
    "I can begin within a few hours of hiring. A short sample works if you want to test first.",
    "Ready to start when you are. I am also open to a brief call if that helps."
]

# ============================================
# HTML TEMPLATE
# ============================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Upwork Proposal Generator</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        body {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #14a800;
            text-align: center;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }
        textarea, input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 15px;
        }
        textarea:focus, input:focus {
            border-color: #14a800;
            outline: none;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        button {
            background: #14a800;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #0e8a00;
        }
        .proposal-box {
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 15px;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .version-label {
            background: #14a800;
            color: white;
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 10px;
        }
        .job-type {
            color: #666;
            font-size: 12px;
            margin-bottom: 10px;
        }
        .copy-btn {
            background: #333;
            padding: 8px 20px;
            font-size: 13px;
            width: auto;
            margin-top: 10px;
        }
        .tips {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        .tips h3 {
            margin-top: 0;
            color: #856404;
        }
        .tips ul {
            margin-bottom: 0;
            color: #856404;
        }
        .word-count {
            font-size: 12px;
            color: #666;
            text-align: right;
        }
    </style>
</head>
<body>
    <h1>Upwork Proposal Generator</h1>
    <p style="text-align: center; color: #666;">Based on research from top rated freelancers</p>

    <div class="card">
        <form method="POST">
            <label>Paste the Job Description:</label>
            <textarea name="job_description" placeholder="Paste the full job posting here...">{{ job_description or '' }}</textarea>

            <label>Your Similar Experience (optional):</label>
            <input type="text" name="experience" placeholder="Example: annotated 5000 images for an AI startup" value="{{ experience or '' }}">

            <label>Your Name (optional):</label>
            <input type="text" name="name" placeholder="Your name" value="{{ name or '' }}">

            <button type="submit">Generate Proposals</button>
        </form>
    </div>

    {% if proposals %}
    <div class="card">
        <h2>Your Proposals (3 Versions)</h2>
        <p style="color: #666;">Choose the one that feels most natural, then customize it further.</p>

        {% for p in proposals %}
        <div style="margin-bottom: 30px;">
            <span class="version-label">Version {{ p.version }}</span>
            <div class="job-type">Detected Job Type: {{ p.job_type }}</div>
            <div class="proposal-box" id="proposal{{ p.version }}">{{ p.text }}</div>
            <div class="word-count">{{ p.word_count }} words</div>
            <button class="copy-btn" onclick="copyProposal({{ p.version }})">Copy to Clipboard</button>
        </div>
        {% endfor %}

        <div class="tips">
            <h3>Before Sending:</h3>
            <ul>
                <li>Replace any generic phrases with specifics from the job post</li>
                <li>Add a link to relevant work if you have one</li>
                <li>Use the client name if it is visible in the posting</li>
                <li>Read it aloud once to check it sounds natural</li>
                <li>Keep under 200 words total</li>
            </ul>
        </div>
    </div>
    {% endif %}

    <script>
        function copyProposal(version) {
            const text = document.getElementById('proposal' + version).innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert('Proposal copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

# ============================================
# GENERATOR LOGIC
# ============================================

def detect_job_type(description):
    """Detect job type from description"""
    desc_lower = description.lower()

    keywords = {
        "data_annotation": ["annotation", "label", "tagging", "annotate", "ai training", "machine learning", "bounding box"],
        "virtual_assistant": ["virtual assistant", "admin", "calendar", "email", "scheduling", "assistant", "administrative"],
        "web_research": ["research", "lead", "list building", "scraping", "linkedin", "contact", "find email", "b2b"],
        "data_entry": ["data entry", "typing", "excel", "spreadsheet", "copy", "transcription", "form"]
    }

    scores = {k: sum(1 for word in v if word in desc_lower) for k, v in keywords.items()}
    best = max(scores, key=scores.get)

    return best if scores[best] > 0 else "data_entry"


def extract_main_task(description):
    """Extract the main task from first sentence or two"""
    sentences = description.replace('\n', ' ').split('.')
    if sentences:
        main = sentences[0].strip()
        if len(main) > 120:
            main = main[:120] + "..."
        return main.lower()
    return "this work"


def generate_proposal(job_description, experience=None, name=None):
    """Generate a single proposal"""

    job_type = detect_job_type(job_description)
    main_task = extract_main_task(job_description)

    templates = TEMPLATES[job_type]

    # Build proposal
    parts = []

    # Opening
    opener = random.choice(templates["openers"])
    opener = opener.replace("{main_task}", main_task)
    parts.append(opener)

    # Experience section
    if experience and experience.strip():
        exp_template = random.choice(EXPERIENCE_TEMPLATES["with"])
        exp_text = exp_template.replace("{experience}", experience.strip())
    else:
        exp_text = random.choice(EXPERIENCE_TEMPLATES["without"])
    parts.append(exp_text)

    # Smart question
    question = random.choice(templates["questions"])
    parts.append(question)

    # Closing
    closing = random.choice(CLOSINGS)
    parts.append(closing)

    # Combine
    proposal = "\n\n".join(parts)

    if name and name.strip():
        proposal += f"\n\n{name.strip()}"

    return proposal, job_type.replace("_", " ").title()


def generate_multiple(job_description, experience=None, name=None, count=3):
    """Generate multiple proposal versions"""
    results = []
    for i in range(count):
        text, job_type = generate_proposal(job_description, experience, name)
        word_count = len(text.split())
        results.append({
            "version": i + 1,
            "text": text,
            "job_type": job_type,
            "word_count": word_count
        })
    return results


# ============================================
# ROUTES
# ============================================

@app.route("/", methods=["GET", "POST"])
def home():
    proposals = None
    job_description = ""
    experience = ""
    name = ""

    if request.method == "POST":
        job_description = request.form.get("job_description", "")
        experience = request.form.get("experience", "")
        name = request.form.get("name", "")

        if job_description.strip():
            proposals = generate_multiple(job_description, experience, name)

    return render_template_string(
        HTML_TEMPLATE,
        proposals=proposals,
        job_description=job_description,
        experience=experience,
        name=name
    )


if __name__ == "__main__":
    print("\n" + "="*50)
    print("UPWORK PROPOSAL GENERATOR")
    print("="*50)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
