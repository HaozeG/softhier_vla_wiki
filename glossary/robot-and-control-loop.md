---
type: glossary
tags: [glossary, control, chunking, async]
sources: [resources/serving/lerobot-async-inference-docs.md, resources/serving/vla-simd.md, resources/serving/real-time-chunking.md]
---
# Robot and control loop

## Summary
How the robot side of a VLA is described: how often commands go out, what a chunk is, and how model latency relates to execution. Chunk duration, latency, stale and lagged are the wiki's own meanings (convention) and are listed by name at the start of project sessions.

## Terms
| Term                                            | Meaning                                                                                                                                                                                                | Scope      | Defined in                                                                               |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------------------- |
| control step, control period (dt), control rate | The robot sends one command at each control step; the control period dt is the time between two steps, and the control rate is one over dt, in hertz. A VLA's chunks have to keep this loop supplied.  | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| action                                          | One command for one control step, for example target positions for the joints. A VLA's output is a sequence of these.                                                                                  | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| action chunk (H, n, K)                          | The group of actions that one model call returns together. The wiki writes the count as H, n or K depending on the source. Chunking is what lets a slow model keep the robot moving between calls.     | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| chunk duration                                  | The number of actions in a chunk times the control period: how long one chunk keeps the robot supplied before the next one is needed.                                                                  | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| latency (l)                                     | The time of one model call, from the observation going in to the chunk coming out. It is not the time to finish a task; it is the delay that asynchronous execution has to hide.                       | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| asynchronous (async) execution                  | The robot keeps executing queued actions while the next call runs, so inference overlaps motion instead of the robot waiting for each answer.                                                          | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| stale actions                                   | Actions of a late chunk that describe moments already passed, because the call took time while the robot kept moving. Dropping them is called discarding stale actions.                                | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| lagged execution                                | Executing a late chunk from its first action anyway instead of discarding its stale actions, so the robot acts on a chunk that was planned for an earlier moment.                                      | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| chunk stitching                                 | Blending a late chunk with the actions already queued so that motion stays consistent when chunks overlap or arrive late. Real-time chunking is one method.                                            | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| real-time chunking (RTC)                        | A chunk-stitching method for diffusion and flow models: the actions that will run while the call is in progress are frozen and the rest are filled in, guided to stay consistent with the frozen ones. | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| dual system                                     | A large, slow model that understands the scene and plans, plus a small, fast policy that produces actions at the control rate, so that the slow model's latency does not set the control rate.         | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| open loop                                       | Executing several actions of a chunk without taking a new observation in between, so the robot does not react to changes until the chunk is used up.                                                   | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| temporal ensembling                             | Averaging overlapping chunks into one action sequence, so that each moment is covered by several predictions.                                                                                          | field      | [serving methods](../knowledge/serving-methods.md)                                       |


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
