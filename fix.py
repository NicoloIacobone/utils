import torch

# --------------------------------------------------------
# 1. LOAD FEATURES (shape: [B, C, H, W])
# --------------------------------------------------------

ENCODER_FEATURES = torch.load("encoder_features.pt")   # es: [1, 1024, 24, 37]
DECODER_FEATURES = torch.load("decoder_features.pt")   # es: [1, 768, 24, 37]

# Assumo batch = 1 (modifica se ti serve)
feat1 = ENCODER_FEATURES
feat2 = DECODER_FEATURES

# --------------------------------------------------------
# 2. FLATTEN 2D → TOKEN FORMAT
#    [B, C, H, W] → [B, T, C]
# --------------------------------------------------------

def flatten_features(f):
    B, C, H, W = f.shape
    tokens = f.flatten(2)          # [B, C, H*W]
    tokens = tokens.permute(0, 2, 1)  # [B, T, C]
    return tokens, H, W

tokens1, H, W = flatten_features(feat1)
tokens2, _, _ = flatten_features(feat2)

# --------------------------------------------------------
# 3. CONCAT FEATURES
#    [B, T, C1] + [B, T, C2] → [B, T, C_total]
# --------------------------------------------------------

tokens_cat = torch.cat([tokens1, tokens2], dim=-1)

# --------------------------------------------------------
# 4. RESTORE SPATIAL MAP
#    [B, T, C_total] → [B, C_total, H, W]
# --------------------------------------------------------

def tokens_to_spatial(tokens, H, W):
    B, T, C = tokens.shape
    assert T == H * W, f"Token count mismatch: T={T}, H*W={H*W}"
    x = tokens.reshape(B, H, W, C)     # [B, H, W, C]
    x = x.permute(0, 3, 1, 2)          # [B, C, H, W]
    return x

feat2d_cat = tokens_to_spatial(tokens_cat, H, W)

# --------------------------------------------------------
# OUTPUT
# --------------------------------------------------------

print("Encoder shape:", feat1.shape)
print("Decoder shape:", feat2.shape)
print("Flattened & concatenated tokens:", tokens_cat.shape)
print("Reconstructed 2D feature map:", feat2d_cat.shape)

# Example:
# Encoder shape: [1, 1024, 24, 37]
# Decoder shape: [1, 768, 24, 37]
# Flattened & concatenated tokens: [1, 888, 1792]
# Reconstructed 2D feature map: [1, 1792, 24, 37]