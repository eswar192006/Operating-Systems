
import heapq

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.predicted_burst = burst_time
        self.completion_time = 0
        self.first_response = -1

    def __repr__(self):
        return f"P{self.pid}"

def arra_scheduler(process_data, aging_interval=10, aging_factor=2.0, alpha=0.5):
    processes = [Process(pid, at, bt) for pid, at, bt in process_data]

    ready_queue = []           
    current_time = 0
    completed = 0
    n = len(processes)
    tie_breaker = 0
    gantt = []                 

    while completed < n:
       
        for p in processes:
            if (p.arrival_time <= current_time and
                p.remaining_time > 0 and
                not any(item[3] is p for item in ready_queue)):

                wait = current_time - p.arrival_time - (p.burst_time - p.remaining_time)
                rr = (wait + p.predicted_burst) / p.predicted_burst
                boost = (wait // aging_interval) * aging_factor
                priority = rr + boost

                heapq.heappush(ready_queue, (-priority, -rr, tie_breaker, p))
                tie_breaker += 1

        if not ready_queue:
            current_time += 1
            continue

        
        _, _, _, current = heapq.heappop(ready_queue)

        
        if not gantt or gantt[-1][1] != current.pid:
            gantt.append([current_time, current.pid])

        if current.first_response == -1:
            current.first_response = current_time

        
        current.remaining_time -= 1
        current_time += 1

        
        if current.remaining_time == 0:
            current.completion_time = current_time
            completed += 1
            current.predicted_burst = alpha * current.burst_time + (1 - alpha) * current.predicted_burst
        else:
            
            wait = current_time - current.arrival_time - (current.burst_time - current.remaining_time)
            rr = (wait + current.predicted_burst) / current.predicted_burst
            boost = (wait // aging_interval) * aging_factor
            priority = rr + boost
            heapq.heappush(ready_queue, (-priority, -rr, tie_breaker, current))
            tie_breaker += 1

    return processes, gantt, current_time

# ========================= MAIN =========================
if __name__ == "__main__":
    print("=" * 65)
    print("    ARRA - Adaptive Response-Ratio with Aging Scheduler")
    print("=" * 65)

    n = int(input("\nEnter number of processes: "))

    print("\nEnter Arrival Time and Burst Time for each process:")
    process_data = []
    for i in range(1, n+1):
        at, bt = map(int, input(f"P{i} → AT BT: ").split())
        process_data.append([i, at, bt])

    print("\nParameters (Press Enter for default):")
    ai = input("  Aging Interval (default 10): ").strip()
    af = input("  Aging Factor   (default 2.0): ").strip()
    al = input("  Alpha value    (default 0.5): ").strip()

    aging_interval = int(ai) if ai else 10
    aging_factor   = float(af) if af else 2.0
    alpha          = float(al) if al else 0.5

    print("\nRunning ARRA Scheduling Simulation...\n")

    completed_processes, gantt, final_time = arra_scheduler(
        process_data,
        aging_interval=aging_interval,
        aging_factor=aging_factor,
        alpha=alpha
    )

    # GANTT CHART
    print("=" * 75)
    print("                           GANTT CHART")
    print("=" * 75)

    i = 0
    while i < len(gantt):
        start = gantt[i][0]
        pid = gantt[i][1]
        j = i
        while j < len(gantt) and gantt[j][1] == pid:
            j += 1
        end = gantt[j][0] if j < len(gantt) else final_time
        print(f"| P{pid} ({start}→{end}) ", end="")
        i = j
    print("|\n")
    print(f"Total Completion Time: {final_time} units")
    print("=" * 75)

    # RESULTS TABLE
    print("\nPID\tAT\tBT\tCT\tTAT\tWT")
    print("-" * 55)
    total_tat = total_wt = 0
    for p in completed_processes:
        tat = p.completion_time - p.arrival_time
        wt = tat - p.burst_time
        total_tat += tat
        total_wt += wt
        print(f"P{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.completion_time}\t{tat}\t\t{wt}")
    print("-" * 55)
    print(f"Average Turnaround Time = {total_tat/n:.2f}")
    print(f"Average Waiting Time    = {total_wt/n:.2f}")
    print("=" * 65)
    print("Simulation completed successfully!")