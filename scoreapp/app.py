from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Load or initialize the scoring data
data_file = "scoring_data.xlsx"
try:
    scores_df = pd.read_excel(data_file)
except FileNotFoundError:
    # Create a new DataFrame if no file exists
    scores_df = pd.DataFrame(columns=[
        "Project Name/ID", "Relevance to Theme", "Creativity and Innovation",
        "Technical Execution", "Functionality", "Presentation",
        "Teamwork", "Environmental Considerations", "Total Score"
    ])

# Route for the scoring form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    project_name = request.form['project_name']
    relevance = int(request.form['relevance'])
    creativity = int(request.form['creativity'])
    technical = int(request.form['technical'])
    functionality = int(request.form['functionality'])
    presentation = int(request.form['presentation'])
    teamwork = int(request.form['teamwork'])
    environmental = int(request.form['environmental'])
    total_score = sum([relevance, creativity, technical, functionality, presentation, teamwork, environmental])

    # Add data to DataFrame
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


    # Save to Excel
    scores_df.to_excel(data_file, index=False)

    return redirect(url_for('index'))

# Route for displaying results
@app.route('/results')
def results():
    global scores_df
    scores_html = scores_df.to_html(classes='table table-striped', index=False)
    return f"""
    <h1>Scoring Results</h1>
    {scores_html}
    <br>
    <a href="/">Back to Form</a>
    """

if __name__ == '__main__':
    app.run(debug=True)
