# Supervisor paper plan

Source: paper-related content only from messages supplied by Guillem in July 2026. Non-paper discussion has been omitted.

## Publication split proposed by Evgenii (Genia) Vinogradov

1. Turn the thesis into a paper. Compressing the complete work into roughly 10--13 pages is challenging but feasible because a draft already exists.
2. Start with a six-page conference-style paper.
3. Conference paper: focus only on the channel-attenuation priors.
4. Journal extension: give only the minimum detail needed to understand the previously published attenuation prior, then add the rest of the thesis work as the extension.
5. The journal must contain at least 40% new contributions relative to the conference paper.

## Preferred venue sequence

| Priority | Venue | Supervisor-provided timing | Why it fits | Practical issue |
|---|---|---|---|---|
| 1 | Workshop on Propagation Channel Models and Evaluation Methodologies for 6G, part of IEEE GLOBECOM 2026 | Submit Aug. 12; decision Sept. 20; conference in Macau in Dec. 2026 | Highly aligned with channel modeling. A workshop is less prestigious than the GLOBECOM main track, but Genia considers it achievable for a student. | Genia cannot fund travel through his current project. UPC funding would likely be needed, and he may need to present instead of Guillem. |
| 2 | IEEE Wireless Communications and Networking Conference (WCNC) | Submit Sept. 15; conference in Panama in Apr. 2027 | Described by Genia as a top-five communications conference. | Same travel-funding problem. |
| 3 | International Conference on Advanced Communication Technologies and Networking (CommNet) | Submit Sept. 22; Rabat, Morocco | Seven pages rather than six; Genia may be able to organize UPC coverage or request online presentation. | A solid normal conference, but not a top venue. |

## Official venue verification (checked 2026-07-14)

- **IEEE GLOBECOM 2026 WS-15:** the official workshop page confirms the paper deadline of **12 August 2026**, acceptance notification on **20 September 2026**, and camera-ready deadline on **1 October 2026**. Its scope explicitly includes AI-driven/physics-inspired channel modeling, channel reconstruction, novel modeling methods, and evaluation methodologies. Canonical page: <https://globecom2026.ieee-globecom.org/events/ws-15-5th-workshop-propagation-channel-models-and-evaluation-methodologies-6g-0>.
- **IEEE WCNC 2027:** the official call confirms a **15 September 2026** paper deadline, **15 January 2027** notification, and **8 February 2027** camera-ready deadline. Initial submissions are limited to **six printed pages**; accepted papers may use pages 7--8 for a fee. The in-person conference is in Panama City on 5--8 April 2027. Canonical pages: <https://wcnc2027.ieee-wcnc.org/authors/call-papers> and <https://wcnc2027.ieee-wcnc.org/submission-guidelines>.
- **CommNet 2026:** the official CFP confirms a **22 September 2026** paper deadline, **1 November 2026** notification, and **15 November 2026** camera-ready deadline. Papers may use seven IEEE two-column pages, with an optional paid eighth page. The conference is 14--16 December 2026. Canonical page: <https://www.commnet-conf.org/cfp.php>.

The supervisor's suggestion that WCNC or CommNet deadlines might be extended remains only a contingency. Do not plan against an extension until an official venue page publishes it.

## Decision tree proposed by Genia

1. Prepare the attenuation-prior paper.
2. Submit it to the GLOBECOM workshop on Aug. 12.
3. Wait for the decision on Sept. 20.
4. If accepted: proceed with the accepted-paper process.
5. If rejected with mostly positive, actionable feedback: make a quick revision and resubmit to WCNC.
6. If rejected with difficult but fair feedback: make a quick revision and try CommNet.
7. Genia noted that the WCNC and CommNet deadlines might be extended by about two weeks, which could leave only a very short revision window. Treat this as a possibility, not a guaranteed extension.

Alternative: submit directly to CommNet, or locate another nearby conference with a suitable deadline, if travel constraints dominate the venue choice.

## New limitation and future work recorded by Guillem

The current simulation terrain is entirely flat. This limits the validity of the learned/calibrated geometry relationships in environments where slopes, valleys, ridges, or terrain shadowing alter the effective transmitter and receiver heights and the LoS/NLoS boundary.

Future work will introduce non-flat digital terrain, recompute visibility and propagation features relative to local ground elevation, and evaluate whether the priors and residual model transfer without recalibration. This point must appear in both the conference and journal manuscripts.
