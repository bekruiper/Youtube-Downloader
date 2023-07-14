import tkinter as tk
from tkinter import ttk
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
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    thumbnail = ImageTk.PhotoImage(img)
    return thumbnail

# Function to analyze video data and apply the filter
def analyze_video_data(videos, filter_option):
    df = pd.DataFrame(columns=['Title', 'Views', 'Thumbnail', 'Link'])
    for video in videos:
        title = video['snippet']['title']
        views = int(video['statistics']['viewCount'])
        thumbnail_url = video['snippet']['thumbnails']['medium']['url']
        video_id = video['id']['videoId']
        thumbnail = fetch_thumbnail(thumbnail_url)
        df = df.append({'Title': title, 'Views': views, 'Thumbnail': thumbnail, 'Link': f'https://www.youtube.com/watch?v={video_id}'}, ignore_index=True)

    if filter_option == 'alphabetically':
        df = df.sort_values('Title')
    elif filter_option == 'by views':
        df = df.sort_values('Views', ascending=False)

    return df

# Function to display the GUI with the video list
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
        filtered_df = analyze_video_data(videos, filter_option)
        display_video_list(filtered_df, 1)

    filter_button = ttk.Button(root, text='Apply Filter', command=apply_filter)
    filter_button.pack(pady=5)

    # Create scrollable list
    frame = tk.Frame(root)
    frame.pack(pady=10)
    canvas = tk.Canvas(frame, width=800, height=600)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')

    for i, (_, row) in enumerate(df[start_index:end_index].iterrows(), start=start_index+1):
        title = row['Title']
        thumbnail = row['Thumbnail']
        link = row['Link']

        # Create hyperlink label
        hyperlink = tk.Label(inner_frame, text=title, fg='blue', cursor='hand2')
        hyperlink.grid(row=i, column=0, padx=10, pady=5, sticky='w')
        hyperlink.bind('<Button-1>', lambda event, l=link: root.clipboard_append(l))

        # Create thumbnail image
        thumbnail_label = tk.Label(inner_frame, image=thumbnail)
        thumbnail_label.grid(row=i, column=1, padx=10, pady=5)

    # Page selector
    def change_page():
        selected_page = int(page_selector.get())
        display_video_list(df, selected_page)

    page_selector = tk.Spinbox(root, from_=1, to=len(df) // 100 + 1, width=5)
    page_selector.delete(0, tk.END)
    page_selector.insert(0, page_num)
    page_selector.pack(pady=10)
    page_selector.bind('<Return>', lambda event: change_page())

    root.mainloop()


# Fetch video data from YouTube
query = 'data analysis tutorials'
max_results = 500
videos = fetch_video_data(query, max_results)

# Analyze video data and apply filter
filter_option = 'by views'
df = analyze_video_data(videos, filter_option)

# Display video list
display_video_list(df, 1)
