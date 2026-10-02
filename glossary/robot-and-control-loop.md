---
type: glossary
tags: [glossary, control, chunking, async]
sources: [resources/serving/lerobot-async-inference-docs.md, resources/serving/vla-simd.md, resources/serving/real-time-chunking.md]
---
# Robot and control loop

## Summary
How the robot side of a VLA is described: how often commands go out, what a chunk is, and how model latency relates to execution. Chunk duration, latency, stale and lagged are the wiki's own meanings (convention) and are loaded into project sessions.

## Terms
| Term                                            | Meaning                                                                                                                               | Scope      | Defined in                                                                               |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------- |
| control step, control period (dt), control rate | The robot sends a new command every control period dt; the control rate is one over dt, in hertz (Hz, per second).                    | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| action                                          | One command for one control step, for example target positions for the joints.                                                        | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| action chunk (H, n, K)                          | The H actions returned by one model call. The wiki writes the count as H, n or K depending on the source.                             | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| chunk duration                                  | H × dt: how long one chunk keeps the robot supplied.                                                                                  | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| latency (l)                                     | Time of one model call, from observation in to chunk out. It is not end-to-end task time.                                             | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| asynchronous (async) execution                  | The robot keeps executing queued actions while the next call runs, so inference overlaps motion.                                      | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| stale actions                                   | Actions of a late chunk that describe moments already passed because the call took time. Dropping them is "discarding stale actions". | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| lagged execution                                | Executing a late chunk from its start anyway instead of discarding its stale actions.                                                 | convention | [serving methods](../knowledge/serving-methods.md)                                       |
| chunk stitching                                 | Blending a late chunk with the actions already queued so motion stays consistent; real-time chunking (RTC) is one method.             | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| dual system                                     | A large slow model that plans plus a small fast policy that runs at the control rate.                                                 | field      | [serving methods](../knowledge/serving-methods.md)                                       |
| open loop                                       | Executing several actions of a chunk without taking a new observation.                                                                | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| temporal ensembling                             | Averaging overlapping chunks into one action sequence.                                                                                | field      | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |

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
