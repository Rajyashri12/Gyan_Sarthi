# Operating Systems - Deadlocks

A deadlock is a situation in which a set of processes are permanently
blocked because each process is waiting for a resource held by another process.

## Four Necessary Conditions

The four necessary conditions for deadlock are:

1. Mutual Exclusion
2. Hold and Wait
3. No Preemption
4. Circular Wait

All four conditions must hold simultaneously for a deadlock to occur.

## Deadlock Prevention

Deadlock prevention attempts to ensure that at least one necessary
condition for deadlock cannot occur.

## Deadlock Avoidance

Deadlock avoidance dynamically examines resource allocation and ensures
that the system remains in a safe state.

The Banker's Algorithm is a well-known deadlock avoidance algorithm.