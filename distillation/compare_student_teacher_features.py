import os
import torch
import matplotlib.pyplot as plt
import seaborn as sns
import random
import torch.nn.functional as F

def mean_std_difference(student_embeddings, teacher_embeddings):
    """
    Computes and prints the mean and standard deviation of student and teacher embeddings for each batch,
    as well as the mean and standard deviation of their differences. Also calculates and prints the average
    difference between the means and standard deviations across all batches.

    Args:
        student_embeddings (torch.Tensor): A batch of student embeddings of shape (B, ...), where B is the batch size.
        teacher_embeddings (torch.Tensor): A batch of teacher embeddings of shape (B, ...), where B is the batch size.

    Prints:
        For each batch:
            - Student mean and standard deviation
            - Teacher mean and standard deviation
            - Mean and standard deviation of the difference between student and teacher embeddings
        At the end:
            - Average difference between means across all batches
            - Average difference between standard deviations across all batches
    """
    B = student_embeddings.shape[0]

    student_means = []
    student_stds = []
    teacher_means = []
    teacher_stds = []

    for i in range(B):
        print(f"Batch {i}:")
        s_mean = student_embeddings[i].mean().item()
        s_std = student_embeddings[i].std().item()
        t_mean = teacher_embeddings[i].mean().item()
        t_std = teacher_embeddings[i].std().item()
        print("  Student mean:", s_mean)
        print("  Student std:", s_std)
        print("  Teacher mean:", t_mean)
        print("  Teacher std:", t_std)
        diff = student_embeddings[i] - teacher_embeddings[i]
        print("  Difference mean:", diff.mean().item())
        print("  Difference std:", diff.std().item())
        student_means.append(s_mean)
        student_stds.append(s_std)
        teacher_means.append(t_mean)
        teacher_stds.append(t_std)

    mean_diff = sum(student_means) / B - sum(teacher_means) / B
    std_diff = sum(student_stds) / B - sum(teacher_stds) / B
    print("\nAverage difference between means:", mean_diff)
    print("Average difference between stds:", std_diff)

def heatmap_sanity_check_single_channel(student_embeddings, teacher_embeddings, output_dir):
    """
    Generates and saves side-by-side heatmap visualizations comparing the same randomly selected channel
    from the student and teacher embedding feature maps for all batch elements.

    The function upsamples both the student and teacher feature maps to the larger spatial resolution
    between the two, normalizes them to the [0, 1] range, and plots them as heatmaps for visual inspection.
    The resulting figures are saved to the specified output directory.

    Args:
        student_embeddings (torch.Tensor): Student feature maps of shape (B, C, H_s, W_s).
        teacher_embeddings (torch.Tensor): Teacher feature maps of shape (B, C, H_t, W_t).
        output_dir (str): Directory path where the heatmap images will be saved.

    Returns:
        None
    """
    B, C, H_s, W_s = student_embeddings.shape
    _, _, H_t, W_t = teacher_embeddings.shape

    channel_idx = random.randint(0, C - 1)
    print(f"Selected channel {channel_idx} for all batches.")

    target_H = max(H_s, H_t)
    target_W = max(W_s, W_t)

    for batch_idx in range(B):
        student_map = student_embeddings[batch_idx, channel_idx:channel_idx+1, :, :].unsqueeze(0)
        teacher_map = teacher_embeddings[batch_idx, channel_idx:channel_idx+1, :, :].unsqueeze(0)

        # Upsample to the larger resolution between student and teacher
        student_upsampled = F.interpolate(student_map, size=(target_H, target_W), mode='bilinear', align_corners=False).squeeze()
        teacher_upsampled = F.interpolate(teacher_map, size=(target_H, target_W), mode='bilinear', align_corners=False).squeeze()

        # Normalize to [0,1]
        student_norm = (student_upsampled - student_upsampled.min()) / (student_upsampled.max() - student_upsampled.min() + 1e-8)
        teacher_norm = (teacher_upsampled - teacher_upsampled.min()) / (teacher_upsampled.max() - teacher_upsampled.min() + 1e-8)

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        sns.heatmap(student_norm.cpu().numpy(), ax=axs[0], cbar=True)
        axs[0].set_title(f"Student Embeddings - Batch {batch_idx}, Channel {channel_idx}")
        sns.heatmap(teacher_norm.cpu().numpy(), ax=axs[1], cbar=True)
        axs[1].set_title(f"Teacher Embeddings - Batch {batch_idx}, Channel {channel_idx}")

        plt.tight_layout()
        output_path = os.path.join(output_dir, f"heatmap_batch{batch_idx}_channel{channel_idx}.png")
        plt.savefig(output_path)
        plt.close(fig)

        print(f"Saved heatmap comparison for batch {batch_idx}, channel {channel_idx} to {output_path}")

def heatmap_sanity_check_avg_all_channels(student_embeddings, teacher_embeddings, output_dir):
    """
    Generates and saves side-by-side heatmap visualizations comparing the average feature maps
    across all channels from the student and teacher embeddings for all batch elements.

    The function upsamples both the student and teacher average feature maps to the larger spatial resolution
    between the two, normalizes them to the [0, 1] range, and plots them as heatmaps for visual inspection.
    The resulting figures are saved to the specified output directory.

    Args:
        student_embeddings (torch.Tensor): Student feature maps of shape (B, C, H_s, W_s).
        teacher_embeddings (torch.Tensor): Teacher feature maps of shape (B, C, H_t, W_t).
        output_dir (str): Directory path where the heatmap images will be saved.

    Returns:
        None
    """
    B, C, H_s, W_s = student_embeddings.shape
    _, _, H_t, W_t = teacher_embeddings.shape

    target_H = max(H_s, H_t)
    target_W = max(W_s, W_t)

    for batch_idx in range(B):
        student_map = student_embeddings[batch_idx].mean(dim=0, keepdim=True).unsqueeze(0)
        teacher_map = teacher_embeddings[batch_idx].mean(dim=0, keepdim=True).unsqueeze(0)

        # Upsample to the larger resolution between student and teacher
        student_upsampled = F.interpolate(student_map, size=(target_H, target_W), mode='bilinear', align_corners=False).squeeze()
        teacher_upsampled = F.interpolate(teacher_map, size=(target_H, target_W), mode='bilinear', align_corners=False).squeeze()

        # Normalize to [0,1]
        student_norm = (student_upsampled - student_upsampled.min()) / (student_upsampled.max() - student_upsampled.min() + 1e-8)
        teacher_norm = (teacher_upsampled - teacher_upsampled.min()) / (teacher_upsampled.max() - teacher_upsampled.min() + 1e-8)

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        sns.heatmap(student_norm.cpu().numpy(), ax=axs[0], cbar=True)
        axs[0].set_title(f"Student Embeddings Avg All Channels - Batch {batch_idx}")
        sns.heatmap(teacher_norm.cpu().numpy(), ax=axs[1], cbar=True)
        axs[1].set_title(f"Teacher Embeddings Avg All Channels - Batch {batch_idx}")

        plt.tight_layout()
        output_path = os.path.join(output_dir, f"heatmap_avg_all_channels_batch{batch_idx}.png")
        plt.savefig(output_path)
        plt.close(fig)

        print(f"Saved heatmap comparison for average all channels for batch {batch_idx} to {output_path}")

student_path = "/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/distillation/mapanything"
student_embeddings_name = "student_embeddings.pt"
teacher_path = "/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/distillation/sam2"
teacher_embeddings_name = "teacher_embeddings.pt"
dirs_to_compare = ["box_ufficio", "yokohama", "tenda_ufficio", "sedia_ufficio", "pianta", "car_drift"]
output_dir = "/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/weekly_meetings/Oct_02/output_comparison"

for dir_name in dirs_to_compare:
    student_embeddings_file = os.path.join(student_path, dir_name, student_embeddings_name)
    teacher_embeddings_file = os.path.join(teacher_path, dir_name, teacher_embeddings_name)
    output_dir_this = os.path.join(output_dir, dir_name)
    os.makedirs(output_dir_this, exist_ok=True)

    student_embeddings = torch.load(student_embeddings_file)
    teacher_embeddings = torch.load(teacher_embeddings_file)

    heatmap_sanity_check_single_channel(student_embeddings, teacher_embeddings, output_dir_this)
    heatmap_sanity_check_avg_all_channels(student_embeddings, teacher_embeddings, output_dir_this)