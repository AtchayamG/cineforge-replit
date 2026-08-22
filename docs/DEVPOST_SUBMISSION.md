# Devpost Submission Draft — CineForge Replit

## Elevator pitch

CineForge Replit is a zero-setup director-to-shot-packet studio. A filmmaker pastes a scene, adds one creative instruction, and receives an inspectable review packet covering dialogue delivery, lensing, camera movement, lighting, sound, and visual-staging prompts—inside a web app built with Replit Agent and published directly on Replit.

## Inspiration

Small film teams often lose creative intent between a screenplay note and the separate documents used by camera, performance, sound, and VFX collaborators. We wanted one shared, browser-based checkpoint that turns a director's intent into a concrete packet without requiring a local development environment.

## What it does

- Accepts a scene draft and a human director instruction.
- Uses Gemini 3.7 Flash through the official Google GenAI SDK to produce structured creative guidance.
- Presents dialogue, camera, lighting, sound, and visual-staging decisions together for human review.
- Creates a clearly labeled in-session review snapshot.
- Exposes runtime evidence showing whether the process is running in Replit development or as a published Replit App.
- Provides deterministic, visibly labeled demo fixtures when no live Gemini credential is configured.

## How we built it

The app is a compact FastAPI service with a responsive single-page judge interface. `.replit` and `replit.nix` define the Replit run environment. The runtime service reads Replit's official predefined environment variables rather than guessing cloud state. The Gemini service calls `google-genai` in live mode with structured JSON output and strict failure handling.

Replit Agent added and tested the in-session snapshot retrieval endpoint, its judge-visible UI status, and regression coverage. The resulting checkpoint and publishing commit were pushed to the public repository, and the finished app is verified at https://cineforge-replit--atchayamganesh.replit.app with a public health response.

## Challenges

The biggest challenge was separating a compelling product story from unsupported platform claims. The first draft simulated peers and generated branch-like URLs. We removed those claims, converted staging into honest in-memory review snapshots, and made the UI expose actual Replit runtime evidence.

## Accomplishments

- A coherent filmmaker workflow rather than a generic chat interface.
- A deployable, inspectable Replit-native web app.
- Explicit demo/live provenance in every response.
- A regression suite that checks runtime truthfulness and prevents fabricated public URLs from returning.
- Authentic Replit Agent and Replit Publishing evidence, with 14 passing tests and a public `.replit.app` deployment.

## What we learned

Platform evidence is part of product design. For judges, the most useful signal is not a badge saying “cloud ready”; it is an app that can show where it is running, which model path produced the result, and what remains temporary.

## What's next

Durable review packets, authenticated project rooms, exportable shot lists, and real-time presence can build on this foundation. They are roadmap items, not claims in this submission.

## Technologies

Replit Agent, Replit Publishing, Python 3.11, FastAPI, Google GenAI SDK, Gemini 3.7 Flash, HTML, Tailwind CSS, and Pytest.
