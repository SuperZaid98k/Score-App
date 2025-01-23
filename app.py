from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load or initialize the scoring data
data_file = "scoring_data.xlsx"
try:
    scores_df = pd.read_excel(data_file)
except FileNotFoundError:
    scores_df = pd.DataFrame(columns=[
        "Project Name/ID", "Relevance to Theme", "Creativity and Innovation",
        "Technical Execution", "Functionality", "Presentation",
        "Teamwork", "Environmental Considerations", "Total Score"
    ])

# Function to generate bar plot
def generate_bar_plot():
    global scores_df
    if scores_df.empty:
        return None

    plt.figure(figsize=(10, 6))
    plt.bar(scores_df["Project Name/ID"], scores_df["Total Score"], color='skyblue')
    plt.title("Projects and Their Total Scores", fontsize=16)
    plt.xlabel("Project Name/ID", fontsize=12)
    plt.ylabel("Total Score", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def home():
    plot_url = generate_bar_plot()
    return render_template('home.html', plot_url=plot_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid Password")
    return render_template('login.html', error=None)

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')  # This uses your original index.html file

@app.route('/submit', methods=['POST'])
def submit():
    project_name = request.form['project_name']
    relevance = int(request.form['relevance'])
    creativity = int(request.form['creativity'])
    technical = int(request.form['technical'])
    functionality = int(request.form['functionality'])
    presentation = int(request.form['presentation'])
    teamwork = int(request.form['teamwork'])
    environmental = int(request.form['environmental'])
    total_score = sum([relevance, creativity, technical, functionality, presentation, teamwork, environmental])

    global scores_df
    new_row = pd.DataFrame([{
        "Project Name/ID": project_name,
        "Relevance to Theme": relevance,
        "Creativity and Innovation": creativity,
        "Technical Execution": technical,
        "Functionality": functionality,
        "Presentation": presentation,
        "Teamwork": teamwork,
        "Environmental Considerations": environmental,
        "Total Score": total_score
    }])

    scores_df = pd.concat([scores_df, new_row], ignore_index=True)
    scores_df.to_excel(data_file, index=False)

    return redirect(url_for('index'))

@app.route('/results', methods=['GET', 'POST'])
def results():
    global scores_df
    message = ""

    if request.method == 'POST':
        project_name = request.form['delete_project_name']
        if project_name in scores_df["Project Name/ID"].values:
            scores_df = scores_df[scores_df["Project Name/ID"] != project_name]
            scores_df.to_excel(data_file, index=False)
            message = f"Project '{project_name}' has been deleted."
        else:
            message = f"Project '{project_name}' not found."

    scores_html = scores_df.to_html(classes='table table-striped', index=False)
    return render_template('results.html', scores_html=scores_html, message=message)

if __name__ == '__main__':
    app.run(debug=True)
