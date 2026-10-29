---
type: glossary
tags: [glossary, control, chunking, async]
sources: [resources/models/smolvla.md, knowledge/one-vla-call.md]
---
# Execution and the robot loop

## Summary
How a policy's output is executed on the robot: how often commands go out, what a chunk is, how chunks are executed or blended, and how model latency relates to execution. Chunk duration, latency, stale and lagged are the wiki's own meanings (convention) and are listed by name at the start of project sessions.

## Terms
| Term                                                | Meaning                                                                                                                                                                                                          | Scope      | Defined in                                                                               |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------- |
| control step, control period (dt), control rate     | The robot sends one command at each control step; the control period dt is the time between two steps, and the control rate is one over dt, in hertz. A VLA's chunks have to keep this loop supplied.            | field      | [one VLA call](../knowledge/one-vla-call.md)                                             |
| action chunk                                        | The group of actions that one model call returns together. The wiki writes the count as H, n or K depending on the source (see symbols). Chunking is what lets a slow model keep the robot moving between calls. | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| chunk duration                                      | The number of actions in a chunk times the control period: how long one chunk keeps the robot supplied before the next one is needed.                                                                            | convention | [one VLA call](../knowledge/one-vla-call.md)                                             |
| latency (l)                                         | The time of one model call, from the observation going in to the chunk coming out. It is not the time to finish a task; it is the delay that asynchronous execution has to hide.                                 | convention | [one VLA call](../knowledge/one-vla-call.md)                                             |
| asynchronous (async) execution                      | The robot keeps executing queued actions while the next call runs, so inference overlaps motion instead of the robot waiting for each answer.                                                                    | field      | [one VLA call](../knowledge/one-vla-call.md)                                             |
| stale actions                                       | Actions of a late chunk that describe moments already passed, because the call took time while the robot kept moving. Dropping them is called discarding stale actions.                                          | convention | [one VLA call](../knowledge/one-vla-call.md)                                             |
| open loop                                           | Executing several actions of a chunk without taking a new observation in between, so the robot does not react to changes until the chunk is used up.                                                             | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| action queue                                        | The list of actions on the robot side, filled from received chunks, from which one action is taken at each control step.                                                                                         | field      | [one VLA call](../knowledge/one-vla-call.md)                                             |
| temporal ensembling                                 | Querying the policy every control step and averaging the overlapping chunks' predictions for the current step, with weights; used by ACT.                                                                        | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| receding horizon (prediction and execution horizon) | Predict a chunk, execute only its first part, then predict again from a new observation. The prediction horizon is the chunk length; the execution horizon is the part executed.                                 | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |



## The robot loop
```text
+------------------------------+                        +----------------------+
| ROBOT + CAMERAS              | -- images + state -->  | VLA MODEL CALL       |
| executes one action every    |     (observation)      | takes latency l      |
| control step                 | <-- chunk of n ------  |                      |
+------------------------------+     actions            +----------------------+

A call returns a whole chunk; the robot works through it while the next
call runs.
```
