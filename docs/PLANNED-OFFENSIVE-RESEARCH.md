# Planned: offensive research (not shipped)

This page describes a capability that is **planned for a future release** and is **not part of this plugin version**. Nothing on this page is available in the shipped package: there is no profile, no skill, no workflow, no tool and no configuration switch for it.

## What is planned

CyStrat Services, Nextron Systems and **exploit labs** have confirmed their cooperation on this plugin. An offensive-research capability is planned for a later version and will be contributed by **exploit labs**; the cooperation is agreed, the capability is not built. The intended scope is planning work for isolated, authorised labs:

- research and emulation plans with explicit detection expectations
- comparison of planned lab signals against supplied lab telemetry
- documentation of coverage gaps as drafts for the detection team

## What is deliberately absent now

| Absent in this release | Why |
|---|---|
| Offensive/research profiles | The shipped profile set is defense-only: six roles from L1 triage to vulnerability management |
| `authorized-research` skill and offensive workflows | Planning material for offensive work is not distributed with the open version |
| A research-planning tool | No tool in this release accepts a target, scope or rules of engagement |
| Any enable switch | There is nothing to enable; the capability does not exist in this build |

## Why it is gated rather than previewed

An offensive planning surface is only meaningful with a scope checker, an explicit operator opt-in and a tested boundary. Shipping the surface without those would be worse than shipping nothing: a disabled switch implies the capability behind it exists.

When the capability ships, it will come with its own scope validation, an explicit opt-in, a published threat model and tests against refused inputs — and it will be a separate, clearly marked addition rather than a hidden part of the defense toolset.

## Status wording

Any external description of this project may state that exploit labs supports and cooperates on the plugin and that offensive research is planned with them for a later release. It must not state or imply that the offensive-research capability is included, previewable or enabled in this version — cooperation is agreed, delivery is not.
