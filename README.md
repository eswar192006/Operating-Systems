# Operating-Systems

CPU SCHEDULING ALGORITHMS:

CPU Scheduling is one of the most important functions of an operating system. Since the CPU is the most critical and expensive resource, the operating system must decide which process gets the CPU and for how long, especially when multiple processes are ready to run.
CPU Scheduling Algorithms are the rules or policies used by the operating system to make this decision efficiently and fairly.

Goal of CPU Scheduling:
To maximize:
    ● CPU utilization (keep CPU as busy as possible)
    ● Throughput (number of processes completed per unit time)
    ● Fairness (no process should starve)
To minimize:
    ● Turnaround time (total time taken to finish a process)
    ● Waiting time (time spent waiting in ready queue)
    ● Response time (time from request to first response – important in interactive systems)

Types of CPU Scheduling Algorithms:
    1. Non-Preemptive: Process runs until it finishes or blocks. Simple, fewer context switches. FCFS, SJF, HRRN are some examples.
    2. Preemptive: OS can forcefully take CPU from running process. Better response time, more overhead. Round Robin, SRTF are some examples.

Common Classical Algorithms:

  1. First Come First Serve (FCFS)
      ● Advantage: Simple
      ● Major Problem: Convoy effect, long average waiting.
  2. Shortest Job First (SJF)
      ● Advantage: Minimum average waiting time.
      ● Major Problem: Starvation of long jobs.
  3. Round Robin
      ● Advantage: Excellent response time.
      ● Major Problem: High waiting if time quantum is bad.
  4. Shortest Remaining Time First (SRTF)
      ● Advantage: Minimum average waiting time.
      ● Major Problem: Starvation of long jobs.
  5. Priority Scheduling
      ● Advantage: Important jobs first
      ● Major Problem: Starvation of low priority jobs.
  6. Highest Response Ration Next (HRRN)
      ● Advantage: Non-preemptive, fair to long jobs.
      ● Major Problem: Still allows starvation in extreme cases, poor response time.

Existing classical algorithms suffer from either starvation (SJF/SRTF), poor response time (HRRN), or high overhead (Round Robin). To overcome these limitations, we propose a new preemptive scheduling algorithm called ARRA – Adaptive Response-Ratio with Aging, which intelligently combines the strengths of SRTF and HRRN while eliminating starvation through a controlled aging mechanism.


INTRODUCTION TO ARRA:

ARRA stands for Adaptive Response-Ratio with Aging, a new preemptive CPU scheduling algorithm specially designed for uni-processor systems to overcome the major drawbacks of existing popular algorithms.
Classical algorithms suffer from the following critical problems:
    ● SJF and SRTF give the best average waiting time but cause starvation of long jobs.
    ● HRRN improves fairness using response ratio but is non-preemptive and can still starve long jobs in extreme cases.
    ● Round-Robin gives good response time but increases average waiting and turnaround time when the time quantum is not perfect.

ARRA successfully eliminates all the above problems by intelligently combining three powerful concepts:
    1. Response Ratio (from HRRN) Favors processes that have waited long compared to their burst time Response Ratio = (Waiting Time + Predicted Burst Time) / Predicted Burst Time
    2. Shortest Remaining Time philosophy (from SRTF) Uses exponentially averaged predicted burst time, so short jobs are naturally preferred.
    3. Controlled Aging Mechanism (stronger than traditional aging) Adds an extra boost = floor (Waiting Time / Aging_Interval) × Aging_Factor
Guarantees that even the longest job will eventually get the highest priority → zero starvation.

Final Priority Formula of ARRA:

Priority = Response Ratio + Aging Boost = (W + P)/P + floor(W / Aging_Interval) × Aging_Factor where W = waiting time so far, P = predicted burst time


ADVANTAGES & DISADVANTAGES:

  1. Advantages:
      ● Completely eliminates starvation of long processes
      ● Provides near-optimal average waiting time and turnaround time (very close to SRTF)
      ● Gives excellent response time to short and newly arrived jobs
      ● Has significantly fewer context switches compared to SRTF
      ● More responsive and fairer than non-preemptive HRRN
      ● Works reliably even when burst time prediction is inaccurate
      ● Uses controlled aging – long-waiting jobs automatically get very high priority
      ● Requires only three simple parameters with sensible defaults (10, 2.0, 0.5)
      ● Highly suitable for interactive, time-sharing, and general-purpose systems

  2. Disadvantages:
      ● More complex to implement than FCFS, SJF, or HRRN
      ● Higher computational overhead due to frequent priority recalculation
      ● More context switches than non-preemptive algorithms
      ● Performance depends on proper tuning of Aging_Interval, Aging_Factor, and α
      ● Slightly higher memory usage (stores predicted burst for each process)
      ● Uses floating-point calculations (not ideal for very tiny embedded systems)
      ● Not mathematically optimal in every case (SRTF is still slightly better when exact burst times are known)
      ● May be considered overkill for extremely simple or hard real-time systems


ALGORITHM:

ARRA (Adaptive Response-Ratio with Aging) is a preemptive CPU scheduling algorithm that selects the next process to run based on the highest dynamic priority, calculated as:
  Priority = Response Ratio + Aging Boost
    Where:
      ● Response Ratio = (favors short & waiting jobs) RR = (Waiting Time + Predicted Burst Time) / Predicted Burst Time
      ● Aging Boost (prevents starvation) Boost = floor(Waiting Time / Aging_Interval) × Aging_Factor

The process with the highest priority gets the CPU. Priority is recalculated every time unit and on every new arrival.
