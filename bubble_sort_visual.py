import argparse
import random
import copy
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def bubble_sort_steps(arr):
    """
    Generator yielding steps for visualization.
    Yields tuples: (action, i, j, array_snapshot)
      action: 'compare', 'swap', 'done'
      i, j: indices involved (-1 if none)
      array_snapshot: shallow copy of current array
    """
    a = arr[:]  # work on copy
    n = len(a)
    if n <= 1:
        yield ('done', -1, -1, a.copy())
        return

    for passnum in range(n - 1):
        made_swap = False
        for j in range(n - passnum - 1):
            # comparison step
            yield ('compare', j, j + 1, a.copy())
            if a[j] > a[j + 1]:
                # swap step
                a[j], a[j + 1] = a[j + 1], a[j]
                made_swap = True
                yield ('swap', j, j + 1, a.copy())
        # if no swaps were made, array is sorted -> we can finish early
        if not made_swap:
            break

    yield ('done', -1, -1, a.copy())


def make_animation(data, interval=150, title="Bubble Sort Visualization"):
    """
    Create a matplotlib FuncAnimation from a list of steps produced by bubble_sort_steps.
    """
    steps = list(data)  # materialize generator into frames
    if len(steps) == 0:
        raise ValueError("No steps to animate")

    # final array length from first snapshot
    _, _, _, arr0 = steps[0]
    n = len(arr0)
    indices = np.arange(n)

    fig, ax = plt.subplots(figsize=(max(6, n * 0.25), 4))
    plt.title(title)
    bar_container = ax.bar(indices, arr0, align='center', color='tab:blue', edgecolor='black')
    ax.set_xlim(-0.5, n - 0.5)
    padding = max(1, int(max(arr0) * 0.05))
    ax.set_ylim(0, max(arr0) + padding)

    # Text to show current operation
    op_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=10, verticalalignment='top')

    def update(frame_index):
        action, i, j, arr = steps[frame_index]
        # update bar heights
        for rect, h in zip(bar_container, arr):
            rect.set_height(h)
            rect.set_color('tab:blue')  # default

        # Color-code relevant bars
        if action == 'compare':
            if 0 <= i < n:
                bar_container[i].set_color('gold')
            if 0 <= j < n:
                bar_container[j].set_color('gold')
            op_text.set_text(f"Comparing indices {i} and {j}")
        elif action == 'swap':
            if 0 <= i < n:
                bar_container[i].set_color('crimson')
            if 0 <= j < n:
                bar_container[j].set_color('crimson')
            op_text.set_text(f"Swapped indices {i} and {j}")
        elif action == 'done':
            # mark all bars as sorted (green)
            for rect in bar_container:
                rect.set_color('seagreen')
            op_text.set_text("Sorted ✔")
        else:
            op_text.set_text(str(action))

        return (*bar_container, op_text)

    ani = animation.FuncAnimation(fig, update, frames=len(steps), interval=interval, blit=False, repeat=False)
    return ani


def ascii_visual(arr, width=50):
    """
    Simple ASCII visualization for terminal: prints horizontal bars scaled to width.
    Useful if you can't run the graphical animation.
    """
    maxv = max(arr) if arr else 1
    for v in arr:
        bar = '#' * int((v / maxv) * width)
        print(f"{v:3} |{bar}")


def main():
    # Always parse arguments, but provide sensible defaults for interactive use
    parser = argparse.ArgumentParser(description="Bubble Sort Visualizer")
    parser.add_argument('--n', type=int, default=None, help='number of elements to sort (ignored if --array is given)')
    parser.add_argument('--interval', type=int, default=150, help='milliseconds between frames')
    parser.add_argument('--seed', type=int, default=None, help='random seed')
    parser.add_argument('--ascii', action='store_true', help='print ASCII steps in terminal (non-graphical)')
    parser.add_argument('--array', type=str, default=None, help='comma-separated list of integers to sort (e.g. 5,2,9,1)')
    args, unknown = parser.parse_known_args()

    # If running from VSCode "Run" button, sys.argv will only have the script name
    interactive = (len(sys.argv) == 1)

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    data = []
    if interactive:
        print("No command-line arguments detected. Switching to interactive mode.")
        try:
            user_input = input("Enter a comma or space separated list of integers to sort (e.g. 5,2,9,1 or 5 2 9 1): ")
            raw = user_input.replace(',', ' ').split()
            for x in raw:
                x = x.strip()
                if x:
                    try:
                        data.append(int(float(x)))
                    except ValueError:
                        print(f"Warning: '{x}' is not a valid integer and will be skipped.")
            if len(data) == 0:
                print("Input array must not be empty or must contain at least one valid integer.")
                return
        except Exception as e:
            print("Error parsing input:", e)
            return
        interval = 150
        ascii_mode = False
    else:
        if args.array is not None:
            try:
                raw = args.array.replace(',', ' ').split()
                for x in raw:
                    x = x.strip()
                    if x:
                        try:
                            data.append(int(float(x)))
                        except ValueError:
                            print(f"Warning: '{x}' is not a valid integer and will be skipped.")
                if len(data) == 0:
                    print("Input array must not be empty or must contain at least one valid integer.")
                    return
            except Exception as e:
                print("Error parsing --array:", e)
                return
        elif args.n is not None:
            if args.n <= 0:
                print("n must be > 0 if --array is not provided")
                return
            data = list(np.random.randint(1, args.n * 5 + 1, size=args.n))
        else:
            try:
                user_input = input("Enter a comma or space separated list of integers to sort (e.g. 5,2,9,1 or 5 2 9 1): ")
                raw = user_input.replace(',', ' ').split()
                for x in raw:
                    x = x.strip()
                    if x:
                        try:
                            data.append(int(float(x)))
                        except ValueError:
                            print(f"Warning: '{x}' is not a valid integer and will be skipped.")
                if len(data) == 0:
                    print("Input array must not be empty or must contain at least one valid integer.")
                    return
            except Exception as e:
                print("Error parsing input:", e)
                return
        interval = args.interval
        ascii_mode = args.ascii

    print("Initial array:", data)

    sorted_arr = None

    if ascii_mode:
        import time
        for step in bubble_sort_steps(data[:]):
            action, i, j, arr = step
            print("\033[H\033[J", end="")  # clear terminal (works on many terminals)
            print(f"Action: {action}  indices: {i},{j}")
            ascii_visual(arr, width=60)
            time.sleep(interval / 1000.0)
            if action == 'done':
                sorted_arr = arr
        print("Done.")
        if sorted_arr is not None:
            print("Sorted array:", sorted_arr)
        return

    ani = make_animation(bubble_sort_steps(data[:]), interval=interval,
                         title="Bubble Sort Visualization (blue=idle, yellow=compare, red=swap, green=done)")

    plt.show()

    for step in bubble_sort_steps(data[:]):
        action, i, j, arr = step
        if action == 'done':
            sorted_arr = arr
    if sorted_arr is not None:
        print("Sorted array:", sorted_arr)

    # If you'd like to save the animation to file (mp4 or gif), uncomment below:
    # Requires ffmpeg (for mp4) or pillow (for gif). Example to save:
    # ani.save('bubble_sort.mp4', writer='ffmpeg', fps=1000/args.interval)
    # ani.save('bubble_sort.gif', writer='pillow', fps=1000/args.interval)


if __name__ == '__main__':
    main()