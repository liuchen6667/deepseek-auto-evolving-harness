import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Data
generations = ['Initial', 'Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6']
scores = [0.6795, 0.7431, 0.7654, 0.7789, 0.7722, 0.7886, 0.8024]

# Benchmark lines (horizontal)
benchmarks = [
    ('Initial Harness + Official Tool (V4-Pro)', 0.7069, '#E67E22', '--'),
    ('Claude Code + V4-Flash (thinking)', 0.8006, '#9B59B6', '-.'),
    ('Claude Code + V4-Pro (thinking)', 0.806, '#E74C3C', '-.'),
    ('Claude Code + Opus 4.6 (thinking)', 0.8184, '#C0392B', ':'),
]

fig, ax = plt.subplots(figsize=(12, 7))

# Plot evolution curve
x = np.arange(len(generations))
ax.plot(x, scores, color='#2980B9', linewidth=3, marker='o', markersize=12,
        label='Auto-Evolving Harness + Auto-Evolving Tool Call (DeepSeek-V3.2)',
        zorder=5)

# Annotate each point - all labels consistently above their points
for i, (xi, yi) in enumerate(zip(x, scores)):
    offset = 12 if i != 4 else -18  # Gen 4 annotation below to avoid self-overlap
    ax.annotate(f'{yi:.4f}', (xi, yi), textcoords="offset points",
                xytext=(0, offset), ha='center', fontsize=12, fontweight='bold',
                color='#2980B9', zorder=6)

# Plot benchmark lines - labels staggered to avoid overlap
label_positions = [
    (6.35, 0.8200, 'Claude Code + Opus 4.6 (thinking): 0.8184'),  # top
    (6.35, 0.8080, 'Claude Code + V4-Pro (thinking): 0.8060'),
    (6.35, 0.7960, 'Claude Code + V4-Flash (thinking): 0.8006'),
    (6.35, 0.7100, 'Initial Harness + Official Tool (V4-Pro): 0.7069'),  # bottom
]

for i, (label, score, color, style) in enumerate(benchmarks):
    ax.axhline(y=score, color=color, linestyle=style, linewidth=2, alpha=0.8, zorder=3)
    lx, ly, ltext = label_positions[i]
    # Calculate proper vertical alignment
    va = 'center'
    if i == 0:  # top label - align bottom to line
        va = 'top'
    elif i == 3:  # bottom label
        va = 'bottom'
    ax.text(lx, ly, ltext, va=va, ha='left',
            fontsize=10, color=color, fontweight='bold', zorder=4)

ax.set_xlim(-0.3, 7.2)

# Styling
ax.set_xticks(x)
ax.set_xticklabels(generations, fontsize=12)
ax.set_ylim(0.65, 0.83)
ax.set_xlim(-0.3, 6.8)
ax.set_ylabel('Score', fontsize=14, fontweight='bold')
ax.set_xlabel('Evolution Generation', fontsize=14, fontweight='bold')
ax.set_title('DeepSeek Auto-Evolving Harness: Performance Improvement Over Generations\n'
             '(DeepSeek-V3.2 non-thinking mode)', fontsize=15, fontweight='bold', pad=15)

ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
ax.legend(loc='lower right', fontsize=10, framealpha=0.95)

# Format y-axis to show 4 decimal places
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.4f'))

plt.tight_layout()
plt.savefig('auto_evolving_scores.png', dpi=180, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Chart saved to auto_evolving_scores.png")
