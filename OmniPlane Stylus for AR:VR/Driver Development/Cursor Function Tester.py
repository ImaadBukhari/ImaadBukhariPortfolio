import random
import time
import subprocess

def simulate_stylus_data(duration=20):
    start_time = time.time()
    pressed = False

    process = subprocess.Popen(
        ['./cursor'],  # Path to your compiled C program
        stdin=subprocess.PIPE,
        text=True
    )

    while time.time() - start_time < duration:
        x = random.randint(0, 1000)
        y = random.randint(0, 1000)

        # Introduce random lifts (False values) occasionally
        if pressed:
            pressed = random.choices([True, False], weights=[0.9, 0.1])[0]
        else:
            pressed = random.choices([True, False], weights=[0.2, 0.8])[0]

        data = f"{x} {y} {int(pressed)}\n"
        process.stdin.write(data)
        process.stdin.flush()
        time.sleep(0.1)

    process.stdin.close()
    process.wait()

if __name__ == "__main__":
    simulate_stylus_data()

