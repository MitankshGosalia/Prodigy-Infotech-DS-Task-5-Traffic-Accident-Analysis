import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def load_data():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path)
            messagebox.showinfo("Success", "File loaded successfully!")
            return df
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "No data.")
        except pd.errors.ParserError:
            messagebox.showerror("Error", "Parse error.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("Warning", "No file selected.")
    return None

def analyze_data(df):
    # Prompt the user to select a folder to save the images
    root = tk.Tk()
    root.withdraw()
    save_folder = filedialog.askdirectory()
    if not save_folder:
        messagebox.showwarning("Warning", "No folder selected.")
        return

    # Data Cleaning
    df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    df['End_Time'] = pd.to_datetime(df['End_Time'])
    df = df.dropna(subset=['Start_Lat', 'Start_Lng', 'Weather_Condition', 'Road_Condition'])

    # Create Time_of_Day column
    df['Time_of_Day'] = df['Start_Time'].apply(lambda x: 'Night' if x.hour < 6 else ('Morning' if x.hour < 12 else ('Afternoon' if x.hour < 18 else 'Evening')))

    # EDA: Summary Statistics
    summary_stats = df[['Severity', 'Weather_Condition', 'Road_Condition', 'Time_of_Day']].describe()
    print(summary_stats)

    # EDA: Plotting
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Weather_Condition', order=df['Weather_Condition'].value_counts().index)
    plt.title('Accidents by Weather Condition')
    plt.xticks(rotation=90)
    weather_condition_img_path = os.path.join(save_folder, 'accidents_by_weather_condition.png')
    plt.savefig(weather_condition_img_path)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Road_Condition', order=df['Road_Condition'].value_counts().index)
    plt.title('Accidents by Road Condition')
    plt.xticks(rotation=90)
    road_condition_img_path = os.path.join(save_folder, 'accidents_by_road_condition.png')
    plt.savefig(road_condition_img_path)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Time_of_Day', order=df['Time_of_Day'].value_counts().index)
    plt.title('Accidents by Time of Day')
    time_of_day_img_path = os.path.join(save_folder, 'accidents_by_time_of_day.png')
    plt.savefig(time_of_day_img_path)
    plt.close()

    # Geospatial Analysis: Accident Hotspots
    m = folium.Map(location=[df['Start_Lat'].mean(), df['Start_Lng'].mean()], zoom_start=5)
    heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)
    accident_hotspots_html_path = os.path.join(save_folder, 'accident_hotspots.html')
    m.save(accident_hotspots_html_path)

    # Create HTML to display images and map
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Traffic Accident Analysis</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f0f0f0;
            }}
            h1 {{
                text-align: center;
            }}
            .image-container {{
                text-align: center;
                margin-bottom: 20px;
            }}
            img {{
                width: 80%;
                height: auto;
                border: 2px solid #ccc;
                box-shadow: 2px 2px 12px #aaa;
                margin-bottom: 20px;
            }}
            iframe {{
                width: 100%;
                height: 500px;
                border: none;
            }}
        </style>
    </head>
    <body>
        <h1>Traffic Accident Analysis</h1>
        <div class="image-container">
            <h2>Accidents by Weather Condition</h2>
            <img src="{weather_condition_img_path}" alt="Accidents by Weather Condition">
        </div>
        <div class="image-container">
            <h2>Accidents by Road Condition</h2>
            <img src="{road_condition_img_path}" alt="Accidents by Road Condition">
        </div>
        <div class="image-container">
            <h2>Accidents by Time of Day</h2>
            <img src="{time_of_day_img_path}" alt="Accidents by Time of Day">
        </div>
        <div class="image-container">
            <h2>Accident Hotspots</h2>
            <iframe src="{accident_hotspots_html_path}"></iframe>
        </div>
    </body>
    </html>
    """

    html_file_path = os.path.join(save_folder, 'traffic_accident_analysis.html')
    with open(html_file_path, 'w') as html_file:
        html_file.write(html_content)

    # Open the HTML file in a web browser
    import webbrowser
    webbrowser.open(html_file_path)

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        analyze_data(df)
    else:
        print("No data to analyze.")
