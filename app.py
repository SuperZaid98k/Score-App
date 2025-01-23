from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

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
        return None  # Return None if no data to plot

    plt.figure(figsize=(10, 6))
    plt.bar(scores_df["Project Name/ID"], scores_df["Total Score"], color='skyblue')
    plt.title("Projects and Their Total Scores", fontsize=16)
    plt.xlabel("Project Name/ID", fontsize=12)
    plt.ylabel("Total Score", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Landing page
@app.route('/')
def home():
    plot_url = generate_bar_plot()
    if plot_url:
        plot_html = f'<img src="data:image/png;base64,{plot_url}" alt="Bar Plot">'
    else:
        plot_html = "<p>No data available to plot.</p>"
    return f"""
    <h1>Welcome to the Scoring App</h1>
    <a href="/login">Login to Continue</a>
    <h2>Projects and Their Total Scores</h2>
    {plot_html}
    """

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':  # Set your desired password here
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "<h1>Invalid Password</h1><a href='/login'>Try Again</a>"
    return """
    <form method="POST">
        <label for="password">Enter Password:</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    """

# Scoring form (index page)
@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return f"""
    <h1>Project Scoring Form</h1>
    {render_template('index.html')}
    <br>
    <a href="/"><button>Go to Home</button></a>
    """

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

# Results page with delete functionality
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
    return f"""
    <h1>Scoring Results</h1>
    {scores_html}
    <br>
    <form method="POST">
        <label for="delete_project_name">Delete Project by Name:</label>
        <input type="text" id="delete_project_name" name="delete_project_name" required>
        <button type="submit">Delete</button>
    </form>
    <p>{message}</p>
    <br>
    <a href="/"><button>Go to Home</button></a>
    <br>
    <a href="/index">Back to Form</a>
    """

if __name__ == '__main__':
    app.run(debug=True)
