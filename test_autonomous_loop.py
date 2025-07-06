from core.autonomous_loop import AutonomousLoop

if __name__ == "__main__":
    loop = AutonomousLoop(client_id="default")  # Replace with test client if desired
    loop.run()   # Runs ONCE and exits
