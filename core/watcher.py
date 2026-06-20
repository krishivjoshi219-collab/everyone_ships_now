# =======================================================================================================================
# 📜 FILE: watcher.py
# 📍 PATH: k/everyone_ships_now/core/watcher.py
# =======================================================================================================================

import sys
import time
import threading

class SandboxWatcher:
    def __init__(self, max_cpu_seconds: float = 1.0, max_api_calls_allowed: int = 3):
        """
        Independent Resource Warden and System Gatekeeper.
        Enforces defensive runtime limits on sandboxed execution spaces.
        """
        self.max_cpu_seconds = max_cpu_seconds
        self.max_api_calls_allowed = max_api_calls_allowed
        self.is_sandbox_idle = True
        self.last_state_change = time.time()
        self.monitored_api_count = 0

    def set_operational_phase(self, is_idle: bool):
        """
        Updates the operational phase tracking matrix.
        Allows the daemon to flag anomalous background spikes during idle cycles.
        """
        self.is_sandbox_idle = is_idle
        self.last_state_change = time.time()
        phase_label = "IDLE (Monitoring Leaks)" if is_idle else "ACTIVE (Computing Patch)"
        print(f"🎛️ WATCHER MATRIX: System shifted to {phase_label} phase.")

    def reset_api_counter(self):
        """Resets the stateful evaluation step counter."""
        self.monitored_api_count = 0

    def register_api_call_event(self) -> bool:
        """
        Tracks API call increments inside the execution matrix.
        Cuts access immediately if the script hits spam thresholds.
        """
        self.monitored_api_count += 1
        if self.monitored_api_count > self.max_api_calls_allowed:
            print(f"🚨 WATCHER SHIELD: Aborted execution! Sandbox hit API limit threshold ({self.max_api_calls_allowed}).")
            return False
        return True

    def monitor_memory_cage_timeout(self, targeted_worker_thread: threading.Thread) -> bool:
        """
        Mechanical Countermeasure: Monitors thread execution lifecycles.
        Slams the execution pipeline shut if a loop attempts to run beyond 1.0 second.
        """
        start_tracking_time = time.time()
        
        # Actively poll the active thread until it finishes or breaches boundaries
        while targeted_worker_thread.is_alive():
            elapsed_time = time.time() - start_tracking_time
            
            if elapsed_time > self.max_cpu_seconds:
                print(f"🚨 WATCHER SHIELD: HARD CUTOFF TRIPPED! Runaway execution killed at {round(elapsed_time, 3)}s.")
                return False  # Instruct the Orchestrator that the sandbox failed security gates
                
            time.sleep(0.02)  # High-speed polling interval to save server tick rates
            
        print(f"✅ WATCHER SUCCESS: Sandbox code exited cleanly in {round(time.time() - start_tracking_time, 3)}s.")
        return True

# =======================================================================================================================
# 🧪 LOCAL COMPONENT INTEGRITY TEST DRILL
# =======================================================================================================================
if __name__ == "__main__":
    print("🛡️ [Watcher Sentinel] Initializing Local Thread Cutoff Test Vector...")
    watcher = SandboxWatcher(max_cpu_seconds=1.0)

    # Simulated malicious input: An infinite loop block function
    def simulated_runaway_loop():
        print("🌀 Sandbox running untrusted test code...")
        while True:
            pass  # Simulating a catastrophic 'while True' logic trap

    test_thread = threading.Thread(target=simulated_runaway_loop, daemon=True)
    watcher.set_operational_phase(is_idle=False)
    test_thread.start()

    # The Watcher steps in to check bounds
    execution_verdict = watcher.monitor_memory_cage_timeout(test_thread)
    watcher.set_operational_phase(is_idle=True)
    
    print(f"\n📊 Watcher Test Verdict: {'PASSED (Thread Contained)' if not execution_verdict else 'FAILED'}")
