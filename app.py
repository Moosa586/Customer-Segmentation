import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Define path for static folder to store plots
app.config['UPLOAD_FOLDER'] = 'static'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return "No file selected"
        
        file = request.files['file']

        # Ensure file is selected
        if file.filename == '':
            return "No file selected"
        
        # Load the CSV data
        try:
            data = pd.read_csv(file)
        except Exception as e:
            return f"Error reading file: {str(e)}"

        # Convert categorical variables to numeric (Label Encoding)
        for column in data.columns:
            if data[column].dtype == 'object':  # Check if the column is categorical
                le = LabelEncoder()
                data[column] = le.fit_transform(data[column])

        # Check if data is valid for clustering
        if data.shape[1] < 2:
            return "Data must have at least two features for clustering."

        # Get selected model from the form
        model_type = request.form.get('model')

        # Apply clustering algorithm (K-Means as an example)
        if model_type == 'kmeans':
            model = KMeans(n_clusters=3)  # You can change the number of clusters
            model.fit(data)
            labels = model.labels_

            # Add cluster labels to the dataframe
            data['Cluster'] = labels

            # Create a scatter plot (assuming the first two features for simplicity)
            plt.figure(figsize=(10, 6))
            plt.scatter(data.iloc[:, 0], data.iloc[:, 1], c=labels, cmap='viridis', marker='o', s=100)
            plt.title("Customer Segments")
            plt.xlabel("Feature 1")
            plt.ylabel("Feature 2")

            # Save the plot as cluster_plot.png in the static folder
            plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cluster_plot.png')
            plt.savefig(plot_path)
            plt.close()

            # Print for debugging
            print(f"Plot saved at: {plot_path}")

            # Return the number of clusters and display the plot
            return render_template('index.html', segments=len(set(labels)), plot_url=url_for('static', filename='cluster_plot.png'))

    return "Something went wrong. Please try again."

if __name__ == '__main__':
    app.run(debug=True)