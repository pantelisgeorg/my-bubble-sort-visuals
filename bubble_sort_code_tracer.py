"""
Bubble Sort — Code-level visual tracer (matplotlib)

What this does
- Runs bubble sort on a random array and animates:
  - Bar chart of the array (right)
  - The actual bubble-sort source code as text with the "currently executing" line highlighted (left)
  - Small status panel with current indices, pass number, comparisons and swaps
- The animation steps correspond to real compare / swap events and also show when the algorithm checks loop headers.
- Save as bubble_sort_code_tracer.py and run:
    pip install matplotlib numpy
    python bubble_sort_code_tracer.py
- Optional CLI args:
    --n N        number of elements (default 18)
    --interval MS   ms between frames (default 220)
    --seed S     random seed

Notes
- This is self-contained and intended for local use (desktop Python).
- The displayed source is the same algorithm executed by the tracer generator, so the highlighted lines map to actual operations.
"""

import argparse
import random
import textwrap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# The source code we will display (must match the traced logic below).
SOURCE = textwrap.dedent("""
def bubble_sort(a):
    n = len(a)
    if n <= 1:
        return a
    for passnum in range(n - 1):
        made_swap = False
        # inner loop: compare adjacent pairs
        for j in range(n - passnum - 1):
            # compare a[j] and a[j+1]
            if a[j] > a[j+1]:
                # swap them
                a[j], a[j+1] = a[j+1], a[j]
                made_swap = True
        # optional early exit
        if not made_swap:
            break
    return a
""").strip().splitlines()


def bubble_sort_trace(arr):
    """
    Generator that executes bubble sort on a copy of arr and yields tracing frames.

    Each yielded frame is a dict:
      { 'action': 'enter'|'compare'|'swap'|'pass_end'|'done',
        'line': <line_index in SOURCE (0-based) to highlight>,
        'passnum': current pass number or -1,
        'i': index j used for comparisons / swaps or -1,
        'j': index j+1 or -1,
        'array': snapshot list
      }
    """
    a = arr[:]  # work copy
    n = len(a)

    # initial / function entry
    yield dict(action='enter', line=0, passnum=-1, i=-1, j=-1, array=a.copy())

    # n = len(a)
    yield dict(action='enter', line=1, passnum=-1, i=-1, j=-1, array=a.copy())

    if n <= 1:
        # return a
        yield dict(action='done', line=2, passnum=-1, i=-1, j=-1, array=a.copy())
        return

    # for passnum in range(n - 1):
    for passnum in range(n - 1):
        # highlight line that sets made_swap
        yield dict(action='enter', line=3, passnum=passnum, i=-1, j=-1, array=a.copy())

        made_swap = False
        # comment / inner loop header
        yield dict(action='enter', line=4, passnum=passnum, i=-1, j=-1, array=a.copy())

        for j in range(n - passnum - 1):
            # compare line (line 6 in SOURCE: the if a[j] > a[j+1])
            yield dict(action='compare', line=6, passnum=passnum, i=j, j=j + 1, array=a.copy())
            if a[j] > a[j + 1]:
                # swap line (line 8)
                a[j], a[j + 1] = a[j + 1], a[j]
                made_swap = True
                yield dict(action='swap', line=8, passnum=passnum, i=j, j=j + 1, array=a.copy())
        # optional early exit line (line 10)
        yield dict(action='pass_end', line=10, passnum=passnum, i=-1, j=-1, array=a.copy())
        if not made_swap:
            break

    # final return
    yield dict(action='done', line=11, passnum=passnum if n>1 else -1, i=-1, j=-1, array=a.copy())


def make_tracer_animation(arr, interval=220, title="Bubble Sort: code tracer"):
    steps = list(bubble_sort_trace(arr))
    if not steps:
        raise RuntimeError("No trace steps produced.")

    n = len(arr)
    indices = np.arange(n)

    # Build figure with three areas: code (left), bars (right), status (bottom)
    fig = plt.figure(figsize=(13, 6))
    # Grid layout: left 40% (code), right 60% (bars)
    gs = fig.add_gridspec(2, 3, height_ratios=[6, 1], width_ratios=[2, 2, 1], hspace=0.25, wspace=0.3)

    # Code axes (left two rows, first col)
    ax_code = fig.add_subplot(gs[:, 0])
    ax_code.axis('off')
    ax_code.set_title("Source (highlighted line executes)")

    # Bars axes (spanning two cols)
    ax_bars = fig.add_subplot(gs[0, 1:])
    ax_bars.set_title("Array state")
    ax_bars.set_xlim(-0.5, n - 0.5)
    padding = max(1, int(max(arr) * 0.05))
    ax_bars.set_ylim(0, max(arr) + padding)

    # Status / counters
    ax_status = fig.add_subplot(gs[1, 1:])
    ax_status.axis('off')

    # Prepare code text layout
    # Precompute text objects for each line
    code_y = np.linspace(0.95, 0.05, len(SOURCE))  # top to bottom
    code_texts = []
    for i, line in enumerate(SOURCE):
        t = ax_code.text(0.01, code_y[i], line.rstrip(), transform=ax_code.transAxes,
                         fontsize=10, fontfamily='monospace', va='top', color='#000000')
        code_texts.append(t)

    # Rectangle to highlight current line (using axes coords)
    highlight_rect = ax_code.add_patch(plt.Rectangle((0, 0), 1, 0.06, transform=ax_code.transAxes,
                                                    color='gold', alpha=0.18, zorder=0))
    highlight_rect.set_visible(False)

    # Bars (rects) initialization
    bars = ax_bars.bar(indices, arr, align='center', color='#4f83ff', edgecolor='black')
    bar_texts = []
    for rect, val in zip(bars, arr):
        txt = ax_bars.text(rect.get_x() + rect.get_width() / 2, val + 0.02 * max(arr), str(val),
                           ha='center', va='bottom', color='white', fontsize=9, fontfamily='monospace')
        bar_texts.append(txt)

    # Status text objects
    op_text = ax_status.text(0.01, 0.65, "op: idle", transform=ax_status.transAxes, fontsize=11, fontfamily='monospace')
    info_text = ax_status.text(0.01, 0.15, "", transform=ax_status.transAxes, fontsize=10, fontfamily='monospace', color='#000000')

    comparisons = 0
    swaps = 0

    def update(frame_index):
        nonlocal comparisons, swaps
        step = steps[frame_index]
        arr_snap = step['array']
        action = step['action']
        line_idx = step['line']
        passnum = step.get('passnum', -1)
        i = step.get('i', -1)
        j = step.get('j', -1)

        # Highlight current source line
        # compute rectangle position based on code_y
        if 0 <= line_idx < len(SOURCE):
            # Use the code text y coordinate to place rectangle. Rectangle height relative approximated.
            y_top = code_y[line_idx]  # top anchor for text
            # Because text is anchored top, move rectangle slightly down to cover the text line area
            rect_height = 0.06
            highlight_rect.set_y(y_top - rect_height + 0.01)
            highlight_rect.set_height(rect_height)
            highlight_rect.set_visible(True)
        else:
            highlight_rect.set_visible(False)

        # Update bars heights and colors
        for idx, rect in enumerate(bars):
            rect.set_height(arr_snap[idx])
            # default idle color
            rect.set_color('#4f83ff')  # blue
            bar_texts[idx].set_text(str(arr_snap[idx]))
            bar_texts[idx].set_y(arr_snap[idx] + 0.02 * max(arr) + 0.5)

        if action == 'compare':
            comparisons += 1
            op_text.set_text(f"op: compare indices {i} ↔ {j} (pass {passnum})")
            if 0 <= i < n:
                bars[i].set_color('gold')
            if 0 <= j < n:
                bars[j].set_color('gold')
        elif action == 'swap':
            swaps += 1
            op_text.set_text(f"op: swap indices {i} ↔ {j} (pass {passnum})")
            if 0 <= i < n:
                bars[i].set_color('crimson')
            if 0 <= j < n:
                bars[j].set_color('crimson')
        elif action == 'pass_end':
            op_text.set_text(f"op: pass end (pass {passnum})")
            # optionally color the tail that's known sorted
            tail_start = n - (passnum + 1)
            for k in range(tail_start, n):
                if 0 <= k < n:
                    bars[k].set_color('seagreen')
        elif action == 'enter':
            op_text.set_text("op: entering / loop header")
        elif action == 'done':
            op_text.set_text("op: done — sorted")
            for rect in bars:
                rect.set_color('seagreen')

        info_text.set_text(f"pass: {passnum if passnum>=0 else '-'}    comparisons: {comparisons}    swaps: {swaps}")

        return (*bars, op_text, info_text, highlight_rect)

    ani = animation.FuncAnimation(fig, update, frames=len(steps), interval=interval, blit=False, repeat=False)
    fig.suptitle(title, fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return ani


def main():
    parser = argparse.ArgumentParser(description="Bubble Sort code tracer visualization")
    parser.add_argument('--n', type=int, default=18, help='number of elements (default 18)')
    parser.add_argument('--interval', type=int, default=220, help='ms between frames (default 220)')
    parser.add_argument('--seed', type=int, default=None, help='random seed')
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    if args.n <= 0:
        raise SystemExit("n must be > 0")

    arr = list(np.random.randint(1, args.n * 4 + 1, size=args.n))
    print("Initial array:", arr)

    ani = make_tracer_animation(arr, interval=args.interval,
                                title="Bubble Sort — Code-level tracer (highlighting executing source line)")

    plt.show()


if __name__ == '__main__':
    main()
