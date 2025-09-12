import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURATION ---
CSV_FILE_PATH = '/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/examples/meeting_11_09/benchmark/iou_results.csv'
OUTPUT_DIR = '/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/examples/meeting_11_09/benchmark/benchmark_plots' # Folder where plots will be saved

# Create the output directory if it does not exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 1. DATA LOADING AND PREPARATION ---

print("--- 1. Loading data ---")
try:
    # Load the CSV. Pandas will automatically read the header from the first row.
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Safety check: verify that the expected columns are present
    expected_cols = ['video_name', 'frame_index', 'object_id', 'iou']
    if not all(col in df.columns for col in expected_cols):
        print("WARNING: The columns in the CSV file do not match the expected ones.")
        print(f"Expected columns: {expected_cols}")
        print(f"Found columns: {list(df.columns)}")
        # You may want to exit or handle the error here
    
    print(f"Loaded {len(df)} records from {len(df['video_name'].unique())} videos.")
    print("First 5 rows of data:")
    print(df.head())
    
except FileNotFoundError:
    print(f"ERROR: File not found at '{CSV_FILE_PATH}'. Check the path.")
    exit()

print("\n" + "="*50 + "\n")


# --- 2. AGGREGATED RESULTS CALCULATION ---

print("--- 2. Calculating Aggregated Results ---")

# Total mIoU (on the entire benchmark)
total_miou = df['iou'].mean()
print(f"Total mIoU (on the whole dataset): {total_miou:.4f}\n")

# mIoU for each video
miou_per_video = df.groupby('video_name')['iou'].mean()
print("--- mIoU per Video ---")
print(miou_per_video.to_string())
print("\n")

# mIoU for each frame of each video (useful for detailed analysis)
miou_per_frame = df.groupby(['video_name', 'frame'])['iou'].mean()
print("--- mIoU per Frame (first 10 rows) ---")
print(miou_per_frame.head(10).to_string())


print("\n" + "="*50 + "\n")


# --- 3. PLOT GENERATION ---

print("--- 3. Generating Plots ---")
sns.set_theme(style="whitegrid")

# --- Plot 1: Comparison of average mIoU for each video (Bar Chart) ---
# This plot gives you an immediate overview of which videos are "easy" and which are "difficult".
plt.figure(figsize=(12, 8))
barplot = sns.barplot(x=miou_per_video.index, y=miou_per_video.values, palette="viridis")
barplot.set_title('Average mIoU per Video', fontsize=16)
barplot.set_xlabel('Video Name', fontsize=12)
barplot.set_ylabel('Mean IoU (mIoU)', fontsize=12)
plt.xticks(rotation=45, ha="right", fontsize=10) # Rotate labels to avoid overlap
plt.tight_layout() # Adjust layout to fit labels
plot1_path = os.path.join(OUTPUT_DIR, 'miou_per_video.png')
plt.savefig(plot1_path)
plt.close()
print(f"Plot 1 saved at: {plot1_path}")


# --- Plot 2: mIoU trend over time for specific videos (Line Chart) ---
# This is the most powerful plot for analyzing occlusions and failures.
# Select some videos to plot (e.g., a good one, a bad one).
# MODIFY the `videos_to_plot` list with the names of your most interesting videos.
videos_to_plot = ['video_01_static_short', 'video_24_more_dynamic_long'] 

for video_name in videos_to_plot:
    if video_name in miou_per_frame.index:
        plt.figure(figsize=(12, 6))
        
        # Filter data for the current video
        video_data = miou_per_frame.loc[video_name]
        
        lineplot = sns.lineplot(x=video_data.index, y=video_data.values)
        lineplot.set_title(f'mIoU Trend per Frame - Video: {video_name}', fontsize=16)
        lineplot.set_xlabel('Frame Index', fontsize=12)
        lineplot.set_ylabel('Mean IoU (mIoU)', fontsize=12)
        lineplot.set_ylim(0, 1.05) # Fix Y axis between 0 and 1 for fair comparison
        
        plot2_path = os.path.join(OUTPUT_DIR, f'miou_over_time_{video_name}.png')
        plt.savefig(plot2_path)
        plt.close()
        print(f"Plot 2 for '{video_name}' saved at: {plot2_path}")

# --- Plot 3: Distribution of IoU scores per video (Box Plot) ---
# This plot shows not only the mean, but also the variance, quartiles, and outliers.
# Very useful to see if a video has stable or highly variable performance.
plt.figure(figsize=(12, 8))
boxplot = sns.boxplot(x='video_name', y='iou', data=df, palette="coolwarm")
boxplot.set_title('Distribution of IoU Scores per Video', fontsize=16)
boxplot.set_xlabel('Video Name', fontsize=12)
boxplot.set_ylabel('IoU Score', fontsize=12)
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.tight_layout()
plot3_path = os.path.join(OUTPUT_DIR, 'iou_distribution_per_video.png')
plt.savefig(plot3_path)
plt.close()
print(f"Plot 3 saved at: {plot3_path}")
print("\nAnalysis completed!")