---
type: concept
tags: [low-level-policy, control-loop, rl, frequency, community]
sources: [https://github.com/pollen-robotics/microduck]
---
# Low-level policy loop

## Summary
A low-level policy loop is a small network that is called once per control step, reads the robot's own joint and inertial sensors, and writes the next joint targets, with no camera and no language in its input. The one worked example in this wiki is the community repository [microduck](https://github.com/pollen-robotics/microduck) (tag community), a 25 cm biped whose walking policies are trained with reinforcement learning (RL) in simulation. Its loop runs at 50 Hz, one action per call, so the model call and the control step are the same thing. This is the opposite end from a VLA, which returns a chunk of actions from a slow call ([one VLA call](one-vla-call.md)).

```text
one 20 ms tick (50 Hz), one process, one serial bus

 servos x15 + IMU board --one fast read--> sensors
                                             |
 gamepad / app / agent --command (13)-->  [observation, 61 floats]
   (intents, latest value wins)              |
                                             v
                                       [ONNX policy, CPU]
                                             |  14 actions
                                             v
                          home pose + scale x action, low-pass filter
                                             |
                                             v
                                   [safety: refuse NaN, clamp]
                                             |
                                             v
                                 one write of goal positions --> servos

 camera --> separate process --> features (not frames) --> command side
```

## Details
**What goes in and out** (microduck's `robotd` design page).
- Observation, 61 floats: gyro 3, projected gravity 3, joint positions 14, joint velocities 14, last action 14, command 13.
- Command, 13 floats: body velocity 3, head 4, body pose 6. It is a hand-designed vector set by a gamepad, an app or a program, not a learned latent.
- Output, 14 actions, one per joint except the mouth. Target = home pose + scale × action, then a low-pass filter, then a range clamp that also refuses non-finite values.
- Policies are ONNX files, feed-forward or LSTM (explicit hidden state); several are swapped by the loop (walk, stand, sit, kicks), only one runs per tick.

**One tick, mapped to wiki terms.**
- Control step: 20 ms. Model calls, control steps and actions per second are all 50 (see Hz in the glossary).
- No action chunk, no [action queue](action-representation-and-chunking.md), so no stale actions and no asynchronous execution in the policy sense. The model's latency has to fit inside the tick.
- The loop never waits on a client: commands are read as the latest value, and a missed tick is skipped rather than queued. Safety (clamp, deadman, fall handling) sits between the policy and the motors.
- Servo reply delay at the factory setting would cost about 8 ms of the 20 ms tick; the daemon rewrites it at start-up. A hot board throttled to 408 MHz of 1800 is reported as a cause of poor walking.

**Where the policy runs: CPU, via ONNX Runtime.** The repository does not give a reason for CPU over the NPU. What it records:
- The 0.8 TOPS INT8 NPU (RKNN runtime, vendor kernel driver, `.rknn` model files) is used for one model, a camera duck detector. Measured on a Radxa Zero 3 board: 25.7 ms p50 and 58.4 ms p95 per frame (inference plus decode), longer than the 20 ms tick. The detector is meant to run at a few hertz.
- The policy is called through ONNX Runtime loaded at run time. One inference was measured at 0.029 ms on an x86 laptop under emulation of the board's binaries; no on-board figure is given, and the repository tells the reader to measure on the board (`policy-rehearsal` example: p50, p95, p99 and the count of calls over 20 ms).

**Where the camera sits.**
- The camera belongs to a separate process (`mediad`), not to the policy loop. Its H.264 video goes through the board's video encoder to a browser or a remote program; a single raw frame can be requested by a local program.
- The design rule is "derived features, not frames": perception runs next to the sensor and publishes a few bytes (for example a bearing to a ball), which the loop would read as a latest value. The NPU detector inside `mediad` is described as wanted and not yet built.
- Planned fusion: camera gives direction, a depth sensor gives distance, a Bluetooth beacon gives identity.
- Heavy models are meant to run off the robot and drive it through the same command calls; the repository says a slow agent is a high-level controller and reactive control stays local.

**Relation to the other notes.**
- It is not a VLA: it is trained from scratch with RL in simulation, with proprioception and a command as input.
- It is not the [RL fast policy](fast-policy-trained-by-rl.md) of the VLA papers, which sits beside a large VLA; it matches the older RL policies the [Ma et al. survey](../resources/surveys/survey-vla-embodied-ai-ma.md) describes.
- As the small-brain end of a [dual-system VLA](dual-system-vla.md) it differs in two ways: it takes no camera of its own, and the interface from above is an explicit command vector rather than a latent.

## Open questions
- The on-board latency of the policy network and its parameter count are not in the repository docs read so far.
- Why the policy runs on CPU rather than the NPU is not stated.
