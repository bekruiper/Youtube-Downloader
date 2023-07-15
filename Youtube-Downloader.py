import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import pandas as pd
import requests
from io import BytesIO
from googleapiclient.discovery import build

# Set up API key and build the YouTube Data API client
api_key = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to fetch video data from YouTube
def fetch_video_data(query, max_results):
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results
    )
    response = request.execute()
    videos = response['items']
    return videos

# Function to fetch thumbnail images
def fetch_thumbnail(url):
    response = requests.get(url)
    thumbnail = Image.open(BytesIO(response.content))
    thumbnail = thumbnail.resize((120, 90), Image.ANTIALIAS)
    thumbnail = ImageTk.PhotoImage(thumbnail)
    return thumbnail

# Function to analyze video data
def analyze_video_data(videos):
    df = pd.DataFrame(columns=['Title', 'Views', 'Thumbnail', 'Link', 'Selected'])
    for video in videos:
        title = video['snippet']['title']
        views = int(video['statistics']['viewCount'])
        thumbnail_url = video['snippet']['thumbnails']['medium']['url']
        video_id = video['id']['videoId']
        thumbnail = fetch_thumbnail(thumbnail_url)
        df = df.append({'Title': title, 'Views': views, 'Thumbnail': thumbnail, 'Link': f'https://www.youtube.com/watch?v={video_id}', 'Selected': False}, ignore_index=True)
    return df

# Function to display the GUI
def display_video_list(df, page_num):
    start_index = (page_num - 1) * 100
    end_index = start_index + 100

    root = tk.Tk()
    root.title('YouTube Video List')

    # Create filter form
    filter_var = tk.StringVar(value='by views')
    filter_combobox = ttk.Combobox(root, textvariable=filter_var, values=['alphabetically', 'by views'])
    filter_combobox.pack(pady=10)

    # Apply filter button
    def apply_filter():
        filter_option = filter_combobox.get()
        df_filtered = analyze_video_data(videos, filter_option)
        display_video_list(df_filtered, 1)

    apply_filter_btn = ttk.Button(root, text='Apply Filter', command=apply_filter)
    apply_filter_btn.pack(pady=10)

    # Create canvas for video list
    canvas = tk.Canvas(root)
    canvas.pack(fill='both', expand=True)

    # Create inner frame for video list
    inner_frame = tk.Frame(canvas)
    inner_frame.pack()

    # Create scrollbar for canvas
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')

    # Configure canvas and scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')
    inner_frame.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))

    # Add checkbox for each video
    for i, (_, row) in enumerate(df[start_index:end_index].iterrows(), start=start_index+1):
        title = row['Title']
        thumbnail = row['Thumbnail']
        link = row['Link']

        checkbox = tk.Checkbutton(inner_frame)
        checkbox.grid(row=i, column=2)

        thumbnail_label = tk.Label(inner_frame, image=thumbnail)
        thumbnail_label.grid(row=i, column=0, padx=10, pady=5)

        hyperlink = tk.Label(inner_frame, text=title, fg='blue', cursor='hand2')
        hyperlink.grid(row=i, column=1, padx=10, pady=5)
        hyperlink.bind('<Button-1>', lambda event, l=link: messagebox.showinfo('YouTube Video', l))

    # Add Select All button
    def select_all():
        for i in df.index:
            df.at[i, 'Selected'] = True
        display_video_list(df, page_num)

    select_all_btn = ttk.Button(root, text='Select All', command=select_all)
    select_all_btn.pack(pady=10)

    # Add Download Selected button
    def download_selected():
        selected = df[df['Selected'] == True]
        # Download selected videos

    download_selected_btn = ttk.Button(root, text='Download Selected', command=download_selected)
    download_selected_btn.pack(pady=10)

    # Add Download All button
    def download_all():
        # Download all videos

    download_all_btn = ttk.Button(root, text='Download All', command=download_all)
    download_all_btn.pack(pady=10)

    root.mainloop()

# Fetch video data
query = 'data analysis tutorials'
max_results = 500
videos = fetch_video_data(query, max_results)

# Analyze video data
df = analyze_video_data(videos)

# Display video list
display_video_list(df, 1)
