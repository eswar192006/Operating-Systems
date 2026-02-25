# Operating Systems

## CPU Scheduling Algorithms

CPU Scheduling is one of the most important functions of an operating system. Since the CPU is the most critical and expensive resource, the operating system must decide which process gets the CPU and for how long, especially when multiple processes are ready to run.

CPU Scheduling Algorithms are the rules or policies used by the operating system to make this decision efficiently and fairly.

---

## Goal of CPU Scheduling

### To Maximize:
- CPU utilization (keep CPU as busy as possible)
- Throughput (number of processes completed per unit time)
- Fairness (no process should starve)

### To Minimize:
- Turnaround time (total time taken to finish a process)
- Waiting time (time spent waiting in ready queue)
- Response time (time from request to first response – important in interactive systems)

---

## Types of CPU Scheduling Algorithms

1. **Non-Preemptive**
   - Process runs until it finishes or blocks.
   - Simple, fewer context switches.
   - Examples: FCFS, SJF, HRRN.

2. **Preemptive**
   - OS can forcefully take CPU from running process.
   - Better response time, more overhead.
   - Examples: Round Robin, SRTF.

---

## Common Classical Algorithms

1. **First Come First Serve (FCFS)**
   - Advantage: Simple
   - Major Problem: Convoy effect, long average waiting time.

2. **Shortest Job First (SJF)**
   - Advantage: Minimum average waiting time.
   - Major Problem: Starvation of long jobs.

3. **Round Robin**
   - Advantage: Excellent response time.
   - Major Problem: High waiting time if time quantum is poorly chosen.

4. **Shortest Remaining Time First (SRTF)**
   - Advantage: Minimum average waiting time.
   - Major Problem: Starvation of long jobs.

5. **Priority Scheduling**
   - Advantage: Important jobs execute first.
   - Major Problem: Starvation of low-priority jobs.

6. **Highest Response Ratio Next (HRRN)**
   - Advantage: Non-preemptive, fair to long jobs.
   - Major Problem: Poor response time; may still starve jobs in extreme cases.

---

# ARRA – Adaptive Response-Ratio with Aging

ARRA (Adaptive Response-Ratio with Aging) is a new preemptive CPU scheduling algorithm designed for uni-processor systems to overcome the major drawbacks of classical algorithms.

Classical algorithms suffer from:
- Starvation (SJF, SRTF)
- Poor response time (HRRN)
- High overhead (Round Robin)

ARRA eliminates these problems by intelligently combining:

1. **Response Ratio (from HRRN)**  
   Favors processes that have waited long compared to their burst time.  
   Response Ratio (RR) = (Waiting Time + Predicted Burst Time) / Predicted Burst Time  

2. **Shortest Remaining Time philosophy (from SRTF)**  
   Uses exponentially averaged predicted burst time so short jobs are naturally preferred.

3. **Controlled Aging Mechanism**  
   Prevents starvation by boosting priority of long-waiting processes.  
   Aging Boost = floor(Waiting Time / Aging_Interval) × Aging_Factor  

---

## Final Priority Formula of ARRA

Priority = Response Ratio + Aging Boost  

Priority = (W + P)/P + floor(W / Aging_Interval) × Aging_Factor  

Where:
- W = Waiting time so far
- P = Predicted burst time

The process with the highest priority gets the CPU.  
Priority is recalculated every time unit and on every new process arrival.

---

## Advantages & Disadvantages

### Advantages
- Completely eliminates starvation of long processes
- Near-optimal average waiting and turnaround time (close to SRTF)
- Excellent response time for short and newly arrived jobs
- Fewer context switches compared to SRTF
- More responsive and fairer than non-preemptive HRRN
- Works even when burst time prediction is inaccurate
- Uses controlled aging for guaranteed fairness
- Requires only three simple parameters
- Suitable for interactive and time-sharing systems

### Disadvantages
- More complex than FCFS, SJF, or HRRN
- Higher computational overhead
- More context switches than non-preemptive algorithms
- Performance depends on proper tuning of Aging_Interval, Aging_Factor, and α
- Slightly higher memory usage
- Uses floating-point calculations
- Not mathematically optimal in every case
- May be unnecessary for extremely simple or hard real-time systems
