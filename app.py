from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load or initialize the scoring data
data_file = "scoring_data.xlsx"
#data_file = "scoring_data.xlsx"
try:
    scores_df = pd.read_excel(data_file)
except FileNotFoundError:
    scores_df = pd.DataFrame(columns=[
        "Project Name/ID", "Relevance to Theme", "Creativity and Innovation",
        "Technical Execution", "Functionality", "Presentation",
        "Teamwork", "Environmental Considerations", "Total Score"
    ])
#########

# Function to generate bar plot
import matplotlib.pyplot as plt
import io
import base64

def generate_bar_plot():
    global scores_df
    if scores_df.empty:
        return None  # Return None if no data to plot

    # Sort the DataFrame by Total Score in descending order
    sorted_df = scores_df.groupby("Project Name/ID", as_index=False)["Total Score"].mean().sort_values(by="Total Score", ascending=False)

    # Create the figure and axis
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        sorted_df["Project Name/ID"],
        sorted_df["Total Score"],
        color='#4CAF50',  # Green color for bars
        edgecolor='black',  # Black borders for bars
        linewidth=1.2  # Border thickness
    )

    # Add gridlines for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add titles and labels
    plt.title("Projects and Their Total Scores", fontsize=18, fontweight='bold', color='#333')
    plt.xlabel("Project Name/ID", fontsize=14, labelpad=10, color='#333')
    plt.ylabel("Total Score", fontsize=14, labelpad=10, color='#333')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right', fontsize=10)

    # Add numbers on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,  # x-coordinate
            height + 0.5,  # y-coordinate slightly above the bar
            f"{int(height)}",  # Text to display
            ha='center',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            fontsize=10,
            color='black'  # Text color
        )

    # Add tight layout to avoid overlapping
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)  # Higher DPI for better resolution
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
        try:
            total_score = int(request.form['delete_total_score'])
        except ValueError:
            message = "Please enter a valid total score."
            project_name = None

        if project_name and not scores_df.empty:
            # Check if both the project name and total score match
            condition = (
                (scores_df["Project Name/ID"] == project_name) &
                (scores_df["Total Score"] == total_score)
            )
            if condition.any():
                scores_df = scores_df[~condition]  # Remove matching rows
                scores_df.to_excel(data_file, index=False)
                message = f"Project '{project_name}' with Total Score {total_score} has been deleted."
            else:
                message = f"No project found with name '{project_name}' and Total Score {total_score}."
        elif project_name is None:
            message = "Invalid project name or total score."

    scores_html = scores_df.to_html(classes='table table-striped', index=False)
    return render_template('results.html', scores_html=scores_html, message=message)

@app.route('/download', methods=['GET'])
def download():
    try:
        return send_file(
            data_file,
            as_attachment=True,
            download_name='scoring_data.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except FileNotFoundError:
        return "The file does not exist.", 404


if __name__ == '__main__':
    app.run(debug=True)
