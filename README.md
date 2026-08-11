# QRME — AI Synthetic Profile Platform

**Current release: v0.63.0** ([changelog](CHANGELOG.md)) — one of three products
([jim-mini](https://github.com/davidsbianchi1984/jim-mini),
[pdi](https://github.com/davidsbianchi1984/pdi)) versioned and cut together, so
one number names one combination of all three.

![QRME — relationship-aware synthetic profiles](assets/design/00-cover.svg)

> **Patent pending** — *Synthetic User Profile Management System*
> (U.S. Patent Application No. 19/056,418, Attorney Docket 526.P002;
> **published as US 2025/0265659 A1 on August 21, 2025**).

QRME lets a user create, customize, and interact with AI-driven synthetic
profiles — versions of themselves, another person (with consent/rights
handling), or a fictional persona. Profiles adapt to *who* they're talking to
(relationship-aware behavior) and *how engaged* that person is, while keeping
their core identity and boundaries fixed. See [docs/PRD.md](docs/PRD.md).

**Roadmap — AI agent management.** When activated, the platform can deploy
intelligent, role-specific AI agents that assist users, automate tasks, manage
workflows, and enhance operational decision-making — running more efficiently
and taking over mundane or outdated tasks and roles — all within the same
secure, private network environment.

## Ability is not a gate

If how a person's body or mind works stands between them and this product,
that is a defect in the product — not in them. This is stated upfront, before
features, because it shapes them: we build for blind and low-vision people,
deaf and hard-of-hearing people, mute and nonspeaking people, people with
limited mobility or amputation or tremor, autistic and cognitively different
people, people with dyslexia, people sensitive to motion — and for every need
not on that list, which is a gap in the list, not in the person.

What is true today, enforced by the suite rather than promised: every
function works by text alone and voice is always optional; every image in
the console carries a description (`test_ability_is_not_a_gate.py` fails on
one that does not); no step is timed; the console honours
`prefers-reduced-motion`; and the known gaps live in
[`tests/a11y_backlog.txt`](tests/a11y_backlog.txt), a ledger that only
shrinks. Anything that stands in your way can be reported from the
**Accessibility** screen — reachable *before* sign-in (`#access`), in ten
languages, with three questions and no diagnosis: what were you trying to
do, what stood in the way, what would help. Reports stay on the deployment
that received them (sealed to the PDI vault when one is configured, never
relayed to the shared error collector), are read with the deployment's
reviewer token, and become rows in that only-shrinks ledger. That is the
whole loop: your words become tracked work.


## App screens

The full QRME product in two form factors — a **desktop app** and a **mobile app** — a screen for every capability, in the app's design language (Deep Indigo · Neon Purple · Warm Amber · Soft Silver, SF-style type, liquid-glass cards). Each is a self-contained, hand-built SVG — no fonts, images, or scripts — so it renders identically here, in a browser, and in any converter.

### Desktop app

Wide, multi-panel workspace views — sidebar nav, live tiles, the conversation surface with its AI-context panel, the relationship table, and the memory vault. Regenerate with `python3 docs/desktop/build.py`.

<table>
<tr>
<td align="center" width="50%"><a href="docs/desktop/01-home.svg"><img src="docs/desktop/01-home.svg" width="460" alt="Home"></a><br><sub><b>01</b> · Home</sub></td>
<td align="center" width="50%"><a href="docs/desktop/02-conversation.svg"><img src="docs/desktop/02-conversation.svg" width="460" alt="Conversation"></a><br><sub><b>02</b> · Conversation</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/desktop/03-relationships.svg"><img src="docs/desktop/03-relationships.svg" width="460" alt="Relationships"></a><br><sub><b>03</b> · Relationships</sub></td>
<td align="center" width="50%"><a href="docs/desktop/04-memory-vault.svg"><img src="docs/desktop/04-memory-vault.svg" width="460" alt="Memory Vault"></a><br><sub><b>04</b> · Memory Vault</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/desktop/05-marketplace-licensing.svg"><img src="docs/desktop/05-marketplace-licensing.svg" width="460" alt="Marketplace & Licensing"></a><br><sub><b>05</b> · Marketplace & Licensing</sub></td>
<td align="center" width="50%"><a href="docs/desktop/06-control-center.svg"><img src="docs/desktop/06-control-center.svg" width="460" alt="Control Center"></a><br><sub><b>06</b> · Control Center</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/desktop/07-live-desks.svg"><img src="docs/desktop/07-live-desks.svg" width="460" alt="Live Desks"></a><br><sub><b>07</b> · Live Desks</sub></td>
<td align="center" width="50%"><a href="docs/desktop/08-audience-commerce.svg"><img src="docs/desktop/08-audience-commerce.svg" width="460" alt="Audience & Commerce"></a><br><sub><b>08</b> · Audience &amp; Commerce</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/desktop/09-signatures.svg"><img src="docs/desktop/09-signatures.svg" width="460" alt="Signatures"></a><br><sub><b>09</b> · Signatures</sub></td>
<td align="center" width="50%"><a href="docs/desktop/10-community.svg"><img src="docs/desktop/10-community.svg" width="460" alt="Community"></a><br><sub><b>10</b> · Community</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/desktop/11-channel-2.svg"><img src="docs/desktop/11-channel-2.svg" width="460" alt="Channel 2"></a><br><sub><b>11</b> · Channel 2 · every place at once</sub></td>
<td align="center" width="50%"><a href="docs/desktop/12-who-you-are.svg"><img src="docs/desktop/12-who-you-are.svg" width="460" alt="Who You Are"></a><br><sub><b>12</b> · Who you are · profiles and anonymity</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/desktop/13-camera-screens.svg"><img src="docs/desktop/13-camera-screens.svg" width="460" alt="Camera & Screens"></a><br><sub><b>13</b> · Camera &amp; screens · what others see of you</sub></td>
<td align="center" width="50%"><a href="docs/desktop/14-game-lobby.svg"><img src="docs/desktop/14-game-lobby.svg" width="460" alt="Game Lobby"></a><br><sub><b>14</b> · Game lobby · the roster and the rule</sub></td>
</tr>
</table>

### Mobile app

The same system on a phone. Regenerate with `python3 docs/screens/build.py`.

**Onboarding, identity & control**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/01-welcome.svg"><img src="docs/screens/01-welcome.svg" width="210" alt="Welcome"></a><br><sub><b>01</b> · Welcome</sub></td>
<td align="center" width="25%"><a href="docs/screens/02-create-profile.svg"><img src="docs/screens/02-create-profile.svg" width="210" alt="Create Profile"></a><br><sub><b>02</b> · Create Profile</sub></td>
<td align="center" width="25%"><a href="docs/screens/03-build-your-profile.svg"><img src="docs/screens/03-build-your-profile.svg" width="210" alt="Build Your Profile"></a><br><sub><b>03</b> · Build Your Profile</sub></td>
<td align="center" width="25%"><a href="docs/screens/04-personality.svg"><img src="docs/screens/04-personality.svg" width="210" alt="Personality"></a><br><sub><b>04</b> · Personality</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/05-profile-home.svg"><img src="docs/screens/05-profile-home.svg" width="210" alt="Profile Home"></a><br><sub><b>05</b> · Profile Home</sub></td>
<td align="center" width="25%"><a href="docs/screens/06-chat.svg"><img src="docs/screens/06-chat.svg" width="210" alt="Chat"></a><br><sub><b>06</b> · Chat</sub></td>
<td align="center" width="25%"><a href="docs/screens/07-memory-vault.svg"><img src="docs/screens/07-memory-vault.svg" width="210" alt="Memory Vault"></a><br><sub><b>07</b> · Memory Vault</sub></td>
<td align="center" width="25%"><a href="docs/screens/08-relationships.svg"><img src="docs/screens/08-relationships.svg" width="210" alt="Relationships"></a><br><sub><b>08</b> · Relationships</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/09-add-relationship.svg"><img src="docs/screens/09-add-relationship.svg" width="210" alt="Add Relationship"></a><br><sub><b>09</b> · Add Relationship</sub></td>
<td align="center" width="25%"><a href="docs/screens/10-profile-health.svg"><img src="docs/screens/10-profile-health.svg" width="210" alt="Profile Health"></a><br><sub><b>10</b> · Profile Health</sub></td>
<td align="center" width="25%"><a href="docs/screens/11-marketplace.svg"><img src="docs/screens/11-marketplace.svg" width="210" alt="Marketplace"></a><br><sub><b>11</b> · Marketplace</sub></td>
<td align="center" width="25%"><a href="docs/screens/12-licensing-center.svg"><img src="docs/screens/12-licensing-center.svg" width="210" alt="Licensing Center"></a><br><sub><b>12</b> · Licensing Center</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/13-embodiments.svg"><img src="docs/screens/13-embodiments.svg" width="210" alt="Embodiments"></a><br><sub><b>13</b> · Embodiments</sub></td>
<td align="center" width="25%"><a href="docs/screens/14-control-center.svg"><img src="docs/screens/14-control-center.svg" width="210" alt="Control Center"></a><br><sub><b>14</b> · Control Center</sub></td>
<td align="center" width="25%"><a href="docs/screens/15-design-language.svg"><img src="docs/screens/15-design-language.svg" width="210" alt="Design Language"></a><br><sub><b>15</b> · Design Language</sub></td>
</tr>
</table>

**Companion, summoning & connection**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/16-genesis.svg"><img src="docs/screens/16-genesis.svg" width="210" alt="Genesis"></a><br><sub><b>16</b> · Genesis</sub></td>
<td align="center" width="25%"><a href="docs/screens/17-summon-beacons.svg"><img src="docs/screens/17-summon-beacons.svg" width="210" alt="Summon & Beacons"></a><br><sub><b>17</b> · Summon & Beacons</sub></td>
<td align="center" width="25%"><a href="docs/screens/18-proactive.svg"><img src="docs/screens/18-proactive.svg" width="210" alt="Proactive"></a><br><sub><b>18</b> · Proactive</sub></td>
<td align="center" width="25%"><a href="docs/screens/19-transparency.svg"><img src="docs/screens/19-transparency.svg" width="210" alt="Transparency"></a><br><sub><b>19</b> · Transparency</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/20-connections.svg"><img src="docs/screens/20-connections.svg" width="210" alt="Connections"></a><br><sub><b>20</b> · Connections</sub></td>
<td align="center" width="25%"><a href="docs/screens/21-rooms.svg"><img src="docs/screens/21-rooms.svg" width="210" alt="Rooms"></a><br><sub><b>21</b> · Rooms</sub></td>
<td align="center" width="25%"><a href="docs/screens/22-providers.svg"><img src="docs/screens/22-providers.svg" width="210" alt="Providers"></a><br><sub><b>22</b> · Providers</sub></td>
</tr>
</table>

**Your data promise, lifecycle & the claims**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/23-cloud-model.svg"><img src="docs/screens/23-cloud-model.svg" width="210" alt="Cloud Model"></a><br><sub><b>23</b> · Cloud Model</sub></td>
<td align="center" width="25%"><a href="docs/screens/24-offline-mode.svg"><img src="docs/screens/24-offline-mode.svg" width="210" alt="Offline Mode"></a><br><sub><b>24</b> · Offline Mode</sub></td>
<td align="center" width="25%"><a href="docs/screens/25-objection-lifecycle.svg"><img src="docs/screens/25-objection-lifecycle.svg" width="210" alt="Objection & Lifecycle"></a><br><sub><b>25</b> · Objection & Lifecycle</sub></td>
<td align="center" width="25%"><a href="docs/screens/26-memorial.svg"><img src="docs/screens/26-memorial.svg" width="210" alt="Memorial"></a><br><sub><b>26</b> · Memorial</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/27-ai-assistant.svg"><img src="docs/screens/27-ai-assistant.svg" width="210" alt="AI Assistant"></a><br><sub><b>27</b> · AI Assistant</sub></td>
<td align="center" width="25%"><a href="docs/screens/28-specialists.svg"><img src="docs/screens/28-specialists.svg" width="210" alt="Specialists"></a><br><sub><b>28</b> · Specialists</sub></td>
<td align="center" width="25%"><a href="docs/screens/29-tasks-grants.svg"><img src="docs/screens/29-tasks-grants.svg" width="210" alt="Tasks & Grants"></a><br><sub><b>29</b> · Tasks & Grants</sub></td>
<td align="center" width="25%"><a href="docs/screens/30-fine-tune.svg"><img src="docs/screens/30-fine-tune.svg" width="210" alt="Fine-Tune"></a><br><sub><b>30</b> · Fine-Tune</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/31-your-data-promise.svg"><img src="docs/screens/31-your-data-promise.svg" width="210" alt="Your Data Promise"></a><br><sub><b>31</b> · Your Data Promise</sub></td>
</tr>
</table>

**Moderation, posting & the persona engine**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/32-moderation.svg"><img src="docs/screens/32-moderation.svg" width="210" alt="Moderation"></a><br><sub><b>32</b> · Moderation</sub></td>
<td align="center" width="25%"><a href="docs/screens/33-posts.svg"><img src="docs/screens/33-posts.svg" width="210" alt="Posts"></a><br><sub><b>33</b> · Posts</sub></td>
<td align="center" width="25%"><a href="docs/screens/34-adult-mode.svg"><img src="docs/screens/34-adult-mode.svg" width="210" alt="Adult Mode"></a><br><sub><b>34</b> · Adult Mode</sub></td>
<td align="center" width="25%"><a href="docs/screens/35-aging-lifecycle.svg"><img src="docs/screens/35-aging-lifecycle.svg" width="210" alt="Aging & Lifecycle"></a><br><sub><b>35</b> · Aging & Lifecycle</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/36-multi-modal.svg"><img src="docs/screens/36-multi-modal.svg" width="210" alt="Multi-Modal"></a><br><sub><b>36</b> · Multi-Modal</sub></td>
<td align="center" width="25%"><a href="docs/screens/37-persona-embedding.svg"><img src="docs/screens/37-persona-embedding.svg" width="210" alt="Persona Embedding"></a><br><sub><b>37</b> · Persona Embedding</sub></td>
<td align="center" width="25%"><a href="docs/screens/38-surfaces.svg"><img src="docs/screens/38-surfaces.svg" width="210" alt="Surfaces"></a><br><sub><b>38</b> · Surfaces</sub></td>
</tr>
</table>

**Session lifecycle**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/39-sign-in.svg"><img src="docs/screens/39-sign-in.svg" width="210" alt="Sign In"></a><br><sub><b>39</b> · Sign In</sub></td>
    <td align="center" width="33%"><a href="docs/screens/40-end-session.svg"><img src="docs/screens/40-end-session.svg" width="210" alt="End Session"></a><br><sub><b>40</b> · End Session</sub></td>
  </tr>
</table>

**First-run — account, verification & guided setup**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/41-log-in.svg"><img src="docs/screens/41-log-in.svg" width="210" alt="Log In"></a><br><sub><b>41</b> · Log In (Apple · Google · Email)</sub></td>
<td align="center" width="25%"><a href="docs/screens/42-verify-identity.svg"><img src="docs/screens/42-verify-identity.svg" width="210" alt="Verify Identity"></a><br><sub><b>42</b> · Verify Identity</sub></td>
<td align="center" width="25%"><a href="docs/screens/43-enable-access.svg"><img src="docs/screens/43-enable-access.svg" width="210" alt="Enable Access"></a><br><sub><b>43</b> · Enable Access</sub></td>
<td align="center" width="25%"><a href="docs/screens/44-avatar-studio.svg"><img src="docs/screens/44-avatar-studio.svg" width="210" alt="Avatar Studio"></a><br><sub><b>44</b> · Avatar Studio (2D &amp; 3D)</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/47-all-set.svg"><img src="docs/screens/47-all-set.svg" width="210" alt="All Set"></a><br><sub><b>47</b> · All Set</sub></td>
</tr>
</table>

**Immersive surfaces — avatar chat, AR / VR & live video**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/45-immersive-chat.svg"><img src="docs/screens/45-immersive-chat.svg" width="210" alt="Immersive Chat"></a><br><sub><b>45</b> · Immersive Chat (AR / VR)</sub></td>
    <td align="center" width="33%"><a href="docs/screens/46-live-video.svg"><img src="docs/screens/46-live-video.svg" width="210" alt="Live Video"></a><br><sub><b>46</b> · Live Video</sub></td>
    <td align="center" width="33%"></td>
  </tr>
</table>

**Connections — social platforms & AI-integrated apps**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/48-social-connections.svg"><img src="docs/screens/48-social-connections.svg" width="210" alt="Social Connections"></a><br><sub><b>48</b> · Social Connections</sub></td>
<td align="center" width="25%"><a href="docs/screens/49-connected-apps.svg"><img src="docs/screens/49-connected-apps.svg" width="210" alt="Connected Apps"></a><br><sub><b>49</b> · Connected Apps</sub></td>
<td align="center" width="25%"><a href="docs/screens/50-knowledge-excursions.svg"><img src="docs/screens/50-knowledge-excursions.svg" width="210" alt="Knowledge Excursions"></a><br><sub><b>50</b> · Knowledge Excursions</sub></td>
<td align="center" width="25%"><a href="docs/screens/51-files-photos.svg"><img src="docs/screens/51-files-photos.svg" width="210" alt="Files & Photos"></a><br><sub><b>51</b> · Files &amp; Photos</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/52-apple-intelligence.svg"><img src="docs/screens/52-apple-intelligence.svg" width="210" alt="Apple Intelligence"></a><br><sub><b>52</b> · Apple Intelligence</sub></td>
<td align="center" width="25%"><a href="docs/screens/53-google-gemini.svg"><img src="docs/screens/53-google-gemini.svg" width="210" alt="Google Gemini"></a><br><sub><b>53</b> · Google Gemini</sub></td>
<td align="center" width="25%"><a href="docs/screens/54-microsoft-copilot.svg"><img src="docs/screens/54-microsoft-copilot.svg" width="210" alt="Microsoft Copilot"></a><br><sub><b>54</b> · Microsoft Copilot</sub></td>
<td align="center" width="25%"><a href="docs/screens/55-objection-revocation.svg"><img src="docs/screens/55-objection-revocation.svg" width="210" alt="Objection &amp; Revocation"></a><br><sub><b>55</b> · Objection &amp; Revocation</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/56-robotics.svg"><img src="docs/screens/56-robotics.svg" width="210" alt="Robotics"></a><br><sub><b>56</b> · Robotics</sub></td>
</tr>
</table>

**Knowledge packs, robot task mods & embodiment**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/57-knowledge-packs.svg"><img src="docs/screens/57-knowledge-packs.svg" width="210" alt="Knowledge Packs"></a><br><sub><b>57</b> · Knowledge Packs</sub></td>
<td align="center" width="25%"><a href="docs/screens/58-robot-task-packs.svg"><img src="docs/screens/58-robot-task-packs.svg" width="210" alt="Robot Task Packs"></a><br><sub><b>58</b> · Robot Task Packs</sub></td>
<td align="center" width="25%"><a href="docs/screens/59-embodied-agent.svg"><img src="docs/screens/59-embodied-agent.svg" width="210" alt="Embodied Agent"></a><br><sub><b>59</b> · Embodied Agent</sub></td>
<td align="center" width="25%"><a href="docs/screens/60-publish-a-pack.svg"><img src="docs/screens/60-publish-a-pack.svg" width="210" alt="Publish a Pack"></a><br><sub><b>60</b> · Publish a Pack</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/61-pack-registries.svg"><img src="docs/screens/61-pack-registries.svg" width="210" alt="Pack Registries"></a><br><sub><b>61</b> · Pack Registries</sub></td>
<td align="center" width="25%"><a href="docs/screens/62-rated-placement.svg"><img src="docs/screens/62-rated-placement.svg" width="210" alt="Rated Placement"></a><br><sub><b>62</b> · Rated Placement (18+)</sub></td>
<td align="center" width="25%"><a href="docs/screens/63-placement-analytics.svg"><img src="docs/screens/63-placement-analytics.svg" width="210" alt="Placement Analytics"></a><br><sub><b>63</b> · Placement Analytics</sub></td>
<td align="center" width="25%"><a href="docs/screens/64-creator-payouts.svg"><img src="docs/screens/64-creator-payouts.svg" width="210" alt="Creator Payouts"></a><br><sub><b>64</b> · Creator Payouts</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/65-watch-remote.svg"><img src="docs/screens/65-watch-remote.svg" width="210" alt="Watch Remote"></a><br><sub><b>65</b> · Watch Remote</sub></td>
<td align="center" width="25%"><a href="docs/screens/66-steering.svg"><img src="docs/screens/66-steering.svg" width="210" alt="Steering"></a><br><sub><b>66</b> · Steering</sub></td>
<td align="center" width="25%"><a href="docs/screens/67-smart-glasses.svg"><img src="docs/screens/67-smart-glasses.svg" width="210" alt="Smart Glasses"></a><br><sub><b>67</b> · Smart Glasses</sub></td>
<td align="center" width="25%"><a href="docs/screens/68-gaming-companion.svg"><img src="docs/screens/68-gaming-companion.svg" width="210" alt="Gaming Companion"></a><br><sub><b>68</b> · Gaming Companion</sub></td>
</tr>
</table>

**Live desks, the audience layer & commerce**

<table>
<tr>
<td align="center" width="25%"><a href="docs/screens/69-live-desks.svg"><img src="docs/screens/69-live-desks.svg" width="210" alt="Live Desks"></a><br><sub><b>69</b> · Live Desks</sub></td>
<td align="center" width="25%"><a href="docs/screens/70-desk-beacons.svg"><img src="docs/screens/70-desk-beacons.svg" width="210" alt="Desk Beacons"></a><br><sub><b>70</b> · Desk Beacons</sub></td>
<td align="center" width="25%"><a href="docs/screens/71-audience.svg"><img src="docs/screens/71-audience.svg" width="210" alt="Audience"></a><br><sub><b>71</b> · Audience</sub></td>
<td align="center" width="25%"><a href="docs/screens/72-gifts-purchases.svg"><img src="docs/screens/72-gifts-purchases.svg" width="210" alt="Gifts &amp; Purchases"></a><br><sub><b>72</b> · Gifts &amp; Purchases</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/73-signatures.svg"><img src="docs/screens/73-signatures.svg" width="210" alt="Signatures"></a><br><sub><b>73</b> · Signatures</sub></td>
<td align="center" width="25%"><a href="docs/screens/74-starter-collection.svg"><img src="docs/screens/74-starter-collection.svg" width="210" alt="Starter Collection"></a><br><sub><b>74</b> · Starter Collection</sub></td>
<td align="center" width="25%"><a href="docs/screens/75-live-room.svg"><img src="docs/screens/75-live-room.svg" width="210" alt="Live Room"></a><br><sub><b>75</b> · Live Room</sub></td>
<td align="center" width="25%"><a href="docs/screens/76-rated-stream.svg"><img src="docs/screens/76-rated-stream.svg" width="210" alt="Rated Stream"></a><br><sub><b>76</b> · Rated Stream (18+)</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/77-search-place.svg"><img src="docs/screens/77-search-place.svg" width="210" alt="Search &amp; Place"></a><br><sub><b>77</b> · Search &amp; Place</sub></td>
<td align="center" width="25%"><a href="docs/screens/78-marketplace-settings.svg"><img src="docs/screens/78-marketplace-settings.svg" width="210" alt="Marketplace Settings"></a><br><sub><b>78</b> · Marketplace Settings</sub></td>
<td align="center" width="25%"><a href="docs/screens/79-search-assistant.svg"><img src="docs/screens/79-search-assistant.svg" width="210" alt="Search Assistant"></a><br><sub><b>79</b> · Search Assistant</sub></td>
<td align="center" width="25%"><a href="docs/screens/80-profile.svg"><img src="docs/screens/80-profile.svg" width="210" alt="Profile"></a><br><sub><b>80</b> · Profile</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/81-lend-a-microphone.svg"><img src="docs/screens/81-lend-a-microphone.svg" width="210" alt="Lend a Microphone"></a><br><sub><b>81</b> · Lend a Microphone</sub></td>
<td align="center" width="25%"><a href="docs/screens/82-agents.svg"><img src="docs/screens/82-agents.svg" width="210" alt="Agents"></a><br><sub><b>82</b> · Agents</sub></td>
<td align="center" width="25%"><a href="docs/screens/83-chat.svg"><img src="docs/screens/83-chat.svg" width="210" alt="Chat with the agent overlay"></a><br><sub><b>83</b> · Chat · overlay</sub></td>
<td align="center" width="25%"><a href="docs/screens/84-friends.svg"><img src="docs/screens/84-friends.svg" width="210" alt="Friends"></a><br><sub><b>84</b> · Friends</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/85-my-page.svg"><img src="docs/screens/85-my-page.svg" width="210" alt="My Page"></a><br><sub><b>85</b> · My Page</sub></td>
<td align="center" width="25%"><a href="docs/screens/86-customise.svg"><img src="docs/screens/86-customise.svg" width="210" alt="Customise"></a><br><sub><b>86</b> · Customise</sub></td>
<td align="center" width="25%"><a href="docs/screens/87-for-you.svg"><img src="docs/screens/87-for-you.svg" width="210" alt="For You"></a><br><sub><b>87</b> · For You</sub></td>
<td align="center" width="25%"><a href="docs/screens/88-your-devices.svg"><img src="docs/screens/88-your-devices.svg" width="210" alt="Your Devices"></a><br><sub><b>88</b> · Your Devices</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/89-live-room.svg"><img src="docs/screens/89-live-room.svg" width="210" alt="Live Room"></a><br><sub><b>89</b> · Live Room · chat + actions</sub></td>
<td align="center" width="25%"><a href="docs/screens/99-posted-video.svg"><img src="docs/screens/99-posted-video.svg" width="210" alt="Posted Video"></a><br><sub><b>99</b> · Posted Video · YouTube</sub></td>
<td align="center" width="25%"><a href="docs/screens/112-the-agreement.svg"><img src="docs/screens/112-the-agreement.svg" width="210" alt="The Agreement"></a><br><sub><b>112</b> · The Agreement</sub></td>
<td align="center" width="25%"><a href="docs/screens/114-delivery.svg"><img src="docs/screens/114-delivery.svg" width="210" alt="Delivery"></a><br><sub><b>114</b> · Delivery</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/115-watch-party.svg"><img src="docs/screens/115-watch-party.svg" width="210" alt="Watch Party"></a><br><sub><b>115</b> · Watch Party</sub></td>
<td align="center" width="25%"><a href="docs/screens/116-lend-a-skill.svg"><img src="docs/screens/116-lend-a-skill.svg" width="210" alt="Lend a Skill"></a><br><sub><b>116</b> · Lend a Skill</sub></td>
<td align="center" width="25%"><a href="docs/screens/117-edit-a-message.svg"><img src="docs/screens/117-edit-a-message.svg" width="210" alt="Edit a Message"></a><br><sub><b>117</b> · Edit a Message</sub></td>
<td align="center" width="25%"><a href="docs/screens/118-stay-anonymous.svg"><img src="docs/screens/118-stay-anonymous.svg" width="210" alt="Stay Anonymous"></a><br><sub><b>118</b> · Stay Anonymous</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/119-your-profiles.svg"><img src="docs/screens/119-your-profiles.svg" width="210" alt="Your Profiles"></a><br><sub><b>119</b> · Your Profiles</sub></td>
<td align="center" width="25%"><a href="docs/screens/120-lend-it-anywhere.svg"><img src="docs/screens/120-lend-it-anywhere.svg" width="210" alt="Lend It Anywhere"></a><br><sub><b>120</b> · Lend It Anywhere</sub></td>
<td align="center" width="25%"><a href="docs/screens/121-wear-a-character.svg"><img src="docs/screens/121-wear-a-character.svg" width="210" alt="Wear a Character"></a><br><sub><b>121</b> · Wear a Character</sub></td>
<td align="center" width="25%"><a href="docs/screens/122-game-lobby.svg"><img src="docs/screens/122-game-lobby.svg" width="210" alt="Game Lobby"></a><br><sub><b>122</b> · Game Lobby</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/123-masked-and-real.svg"><img src="docs/screens/123-masked-and-real.svg" width="210" alt="Masked and Real"></a><br><sub><b>123</b> · Masked and Real</sub></td>
<td align="center" width="25%"><a href="docs/screens/124-your-background.svg"><img src="docs/screens/124-your-background.svg" width="210" alt="Your Background"></a><br><sub><b>124</b> · Your Background</sub></td>
<td align="center" width="25%"><a href="docs/screens/125-never-a-player.svg"><img src="docs/screens/125-never-a-player.svg" width="210" alt="Never a Player"></a><br><sub><b>125</b> · Never a Player</sub></td>
<td align="center" width="25%"><a href="docs/screens/126-on-a-screen.svg"><img src="docs/screens/126-on-a-screen.svg" width="210" alt="On a Screen"></a><br><sub><b>126</b> · On a Screen</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/127-show-me-around.svg"><img src="docs/screens/127-show-me-around.svg" width="210" alt="Show Me Around"></a><br><sub><b>127</b> · Show Me Around</sub></td>
<td align="center" width="25%"><a href="docs/screens/128-the-corner-pane.svg"><img src="docs/screens/128-the-corner-pane.svg" width="210" alt="The Corner Pane"></a><br><sub><b>128</b> · The Corner Pane</sub></td>
<td align="center" width="25%"><a href="docs/screens/129-where-is-it.svg"><img src="docs/screens/129-where-is-it.svg" width="210" alt="Where Is It"></a><br><sub><b>129</b> · Where Is It?</sub></td>
<td align="center" width="25%"><a href="docs/screens/130-choose-a-plan.svg"><img src="docs/screens/130-choose-a-plan.svg" width="210" alt="Choose a Plan"></a><br><sub><b>130</b> · Choose a Plan</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/131-what-pro-adds.svg"><img src="docs/screens/131-what-pro-adds.svg" width="210" alt="What Pro Adds"></a><br><sub><b>131</b> · What Pro Adds</sub></td>
<td align="center" width="25%"><a href="docs/screens/132-pick-a-plan.svg"><img src="docs/screens/132-pick-a-plan.svg" width="210" alt="Pick a Plan"></a><br><sub><b>132</b> · Pick a Plan</sub></td>
<td align="center" width="25%"><a href="docs/screens/133-payment.svg"><img src="docs/screens/133-payment.svg" width="210" alt="Payment"></a><br><sub><b>133</b> · Payment</sub></td>
<td align="center" width="25%"><a href="docs/screens/134-youre-on-basic.svg"><img src="docs/screens/134-youre-on-basic.svg" width="210" alt="You are on Basic"></a><br><sub><b>134</b> · You're on Basic</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/135-this-needs-pro.svg"><img src="docs/screens/135-this-needs-pro.svg" width="210" alt="This Needs Pro"></a><br><sub><b>135</b> · This Needs Pro</sub></td>
<td align="center" width="25%"><a href="docs/screens/136-show-them.svg"><img src="docs/screens/136-show-them.svg" width="210" alt="Show Them"></a><br><sub><b>136</b> · Show Them</sub></td>
<td align="center" width="25%"><a href="docs/screens/137-whats-in-shot.svg"><img src="docs/screens/137-whats-in-shot.svg" width="210" alt="Whats In Shot"></a><br><sub><b>137</b> · What's In Shot</sub></td>
<td align="center" width="25%"><a href="docs/screens/138-youre-on-free.svg"><img src="docs/screens/138-youre-on-free.svg" width="210" alt="You are on Free"></a><br><sub><b>138</b> · You're on Free</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/139-where-it-lives.svg"><img src="docs/screens/139-where-it-lives.svg" width="210" alt="Where It Lives"></a><br><sub><b>139</b> · Where It Lives</sub></td>
<td align="center" width="25%"><a href="docs/screens/140-not-on-free.svg"><img src="docs/screens/140-not-on-free.svg" width="210" alt="Not On Free"></a><br><sub><b>140</b> · Not On Free</sub></td>
<td align="center" width="25%"><a href="docs/screens/141-which-model-answers.svg"><img src="docs/screens/141-which-model-answers.svg" width="210" alt="Which Model Answers"></a><br><sub><b>141</b> · Which Model Answers</sub></td>
<td align="center" width="25%"><a href="docs/screens/142-blend-a-profile.svg"><img src="docs/screens/142-blend-a-profile.svg" width="210" alt="Blend a Profile"></a><br><sub><b>142</b> · Blend a Profile</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/143-what-would-they-do.svg"><img src="docs/screens/143-what-would-they-do.svg" width="210" alt="What Would They Do"></a><br><sub><b>143</b> · What Would They Do</sub></td>
<td align="center" width="25%"><a href="docs/screens/144-where-you-are.svg"><img src="docs/screens/144-where-you-are.svg" width="210" alt="Where You Are"></a><br><sub><b>144</b> · Where You Are</sub></td>
<td align="center" width="25%"><a href="docs/screens/145-where-the-money-goes.svg"><img src="docs/screens/145-where-the-money-goes.svg" width="210" alt="Where the Money Goes"></a><br><sub><b>145</b> · Where the Money Goes</sub></td>
<td align="center" width="25%"><a href="docs/screens/146-the-ecosystem.svg"><img src="docs/screens/146-the-ecosystem.svg" width="210" alt="The Ecosystem"></a><br><sub><b>146</b> · The Ecosystem</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/147-your-own-voice.svg"><img src="docs/screens/147-your-own-voice.svg" width="210" alt="Your Own Voice"></a><br><sub><b>147</b> · Your Own Voice</sub></td>
<td align="center" width="25%"><a href="docs/screens/148-who-wrote-this.svg"><img src="docs/screens/148-who-wrote-this.svg" width="210" alt="Who Wrote This?"></a><br><sub><b>148</b> · Who Wrote This?</sub></td>
<td align="center" width="25%"><a href="docs/screens/149-how-should-they-work.svg"><img src="docs/screens/149-how-should-they-work.svg" width="210" alt="How Should They Work?"></a><br><sub><b>149</b> · How Should They Work?</sub></td>
<td align="center" width="25%"><a href="docs/screens/150-what-went-wrong.svg"><img src="docs/screens/150-what-went-wrong.svg" width="210" alt="What Went Wrong"></a><br><sub><b>150</b> · What Went Wrong</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/151-before-anything-is-sent.svg"><img src="docs/screens/151-before-anything-is-sent.svg" width="210" alt="Before Anything Is Sent"></a><br><sub><b>151</b> · Before Anything Is Sent</sub></td>
<td align="center" width="25%"><a href="docs/screens/152-marketplace.svg"><img src="docs/screens/152-marketplace.svg" width="210" alt="Marketplace"></a><br><sub><b>152</b> · Marketplace</sub></td>
<td align="center" width="25%"><a href="docs/screens/153-exchanges.svg"><img src="docs/screens/153-exchanges.svg" width="210" alt="Exchanges"></a><br><sub><b>153</b> · Exchanges</sub></td>
<td align="center" width="25%"><a href="docs/screens/154-lent-skills.svg"><img src="docs/screens/154-lent-skills.svg" width="210" alt="Lent Skills"></a><br><sub><b>154</b> · Lent Skills</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/155-watch-together.svg"><img src="docs/screens/155-watch-together.svg" width="210" alt="Watch Together"></a><br><sub><b>155</b> · Watch Together</sub></td>
<td align="center" width="25%"><a href="docs/screens/156-who-this-is.svg"><img src="docs/screens/156-who-this-is.svg" width="210" alt="Who This Is"></a><br><sub><b>156</b> · Who This Is</sub></td>
<td align="center" width="25%"><a href="docs/screens/157-where-it-is-seen.svg"><img src="docs/screens/157-where-it-is-seen.svg" width="210" alt="Where It Is Seen"></a><br><sub><b>157</b> · Where It Is Seen</sub></td>
<td align="center" width="25%"><a href="docs/screens/158-what-is-live.svg"><img src="docs/screens/158-what-is-live.svg" width="210" alt="What Is Live"></a><br><sub><b>158</b> · What Is Live</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/159-contest-a-profile.svg"><img src="docs/screens/159-contest-a-profile.svg" width="210" alt="Contest A Profile"></a><br><sub><b>159</b> · Contest A Profile</sub></td>
<td align="center" width="25%"><a href="docs/screens/160-show-me-around.svg"><img src="docs/screens/160-show-me-around.svg" width="210" alt="Show Me Around"></a><br><sub><b>160</b> · Show Me Around</sub></td>
<td align="center" width="25%"><a href="docs/screens/161-not-on-this-plan.svg"><img src="docs/screens/161-not-on-this-plan.svg" width="210" alt="Not On This Plan"></a><br><sub><b>161</b> · Not On This Plan</sub></td>
<td align="center" width="25%"><a href="docs/screens/162-where-it-is-marketed.svg"><img src="docs/screens/162-where-it-is-marketed.svg" width="210" alt="Where It Is Marketed"></a><br><sub><b>162</b> · Where It Is Marketed</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/163-a-body-to-speak-through.svg"><img src="docs/screens/163-a-body-to-speak-through.svg" width="210" alt="A Body To Speak Through"></a><br><sub><b>163</b> · A Body To Speak Through</sub></td>
<td align="center" width="25%"><a href="docs/screens/164-what-it-is-made-of.svg"><img src="docs/screens/164-what-it-is-made-of.svg" width="210" alt="What It Is Made Of"></a><br><sub><b>164</b> · What It Is Made Of</sub></td>
<td align="center" width="25%"><a href="docs/screens/165-what-it-can-do-for-you.svg"><img src="docs/screens/165-what-it-can-do-for-you.svg" width="210" alt="What It Can Do For You"></a><br><sub><b>165</b> · What It Can Do For You</sub></td>
<td align="center" width="25%"><a href="docs/screens/166-somebody-qualified.svg"><img src="docs/screens/166-somebody-qualified.svg" width="210" alt="Somebody Qualified"></a><br><sub><b>166</b> · Somebody Qualified</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/167-in-the-game-with-you.svg"><img src="docs/screens/167-in-the-game-with-you.svg" width="210" alt="In The Game With You"></a><br><sub><b>167</b> · In The Game With You</sub></td>
<td align="center" width="25%"><a href="docs/screens/168-who-follows-and-what-they-pay.svg"><img src="docs/screens/168-who-follows-and-what-they-pay.svg" width="210" alt="Who Follows, And What They Pay"></a><br><sub><b>168</b> · Who Follows, And What They Pay</sub></td>
<td align="center" width="25%"><a href="docs/screens/169-where-people-find-you.svg"><img src="docs/screens/169-where-people-find-you.svg" width="210" alt="Where People Find You"></a><br><sub><b>169</b> · Where People Find You</sub></td>
<td align="center" width="25%"><a href="docs/screens/170-reaching-out-and-what-stops-it.svg"><img src="docs/screens/170-reaching-out-and-what-stops-it.svg" width="210" alt="Reaching Out, And What Stops It"></a><br><sub><b>170</b> · Reaching Out, And What Stops It</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/171-what-leaves-and-on-what-terms.svg"><img src="docs/screens/171-what-leaves-and-on-what-terms.svg" width="210" alt="What Leaves, And On What Terms"></a><br><sub><b>171</b> · What Leaves, And On What Terms</sub></td>
<td align="center" width="25%"><a href="docs/screens/172-one-thing-named.svg"><img src="docs/screens/172-one-thing-named.svg" width="210" alt="One Thing, Named"></a><br><sub><b>172</b> · One Thing, Named</sub></td>
<td align="center" width="25%"><a href="docs/screens/173-beginning-and-passing-on.svg"><img src="docs/screens/173-beginning-and-passing-on.svg" width="210" alt="Beginning, And Passing On"></a><br><sub><b>173</b> · Beginning, And Passing On</sub></td>
<td align="center" width="25%"><a href="docs/screens/174-what-you-are-owed.svg"><img src="docs/screens/174-what-you-are-owed.svg" width="210" alt="What You Are Owed"></a><br><sub><b>174</b> · What You Are Owed</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/175-inside-a-room.svg"><img src="docs/screens/175-inside-a-room.svg" width="210" alt="Inside A Room"></a><br><sub><b>175</b> · Inside A Room</sub></td>
<td align="center" width="25%"><a href="docs/screens/176-a-body-and-what-it-learns.svg"><img src="docs/screens/176-a-body-and-what-it-learns.svg" width="210" alt="A Body, And What It Learns"></a><br><sub><b>176</b> · A Body, And What It Learns</sub></td>
<td align="center" width="25%"><a href="docs/screens/177-work-handed-over.svg"><img src="docs/screens/177-work-handed-over.svg" width="210" alt="Work Handed Over"></a><br><sub><b>177</b> · Work Handed Over</sub></td>
<td align="center" width="25%"><a href="docs/screens/178-signed-and-checked.svg"><img src="docs/screens/178-signed-and-checked.svg" width="210" alt="Signed, And Checked"></a><br><sub><b>178</b> · Signed, And Checked</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/179-ringing-the-bell.svg"><img src="docs/screens/179-ringing-the-bell.svg" width="210" alt="Ringing The Bell"></a><br><sub><b>179</b> · Ringing The Bell</sub></td>
<td align="center" width="25%"><a href="docs/screens/180-two-strangers.svg"><img src="docs/screens/180-two-strangers.svg" width="210" alt="Two Strangers"></a><br><sub><b>180</b> · Two Strangers</sub></td>
<td align="center" width="25%"><a href="docs/screens/181-the-mark-and-the-held.svg"><img src="docs/screens/181-the-mark-and-the-held.svg" width="210" alt="The Mark, And The Held"></a><br><sub><b>181</b> · The Mark, And The Held</sub></td>
<td align="center" width="25%"><a href="docs/screens/182-in-its-own-words.svg"><img src="docs/screens/182-in-its-own-words.svg" width="210" alt="In Its Own Words"></a><br><sub><b>182</b> · In Its Own Words</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/183-everything-else.svg"><img src="docs/screens/183-everything-else.svg" width="210" alt="Everything Else"></a><br><sub><b>183</b> · Everything Else</sub></td>
<td align="center" width="25%"><a href="docs/screens/184-without-an-account.svg"><img src="docs/screens/184-without-an-account.svg" width="210" alt="Without An Account"></a><br><sub><b>184</b> · Without An Account</sub></td>
<td align="center" width="25%"><a href="docs/screens/185-discover.svg"><img src="docs/screens/185-discover.svg" width="210" alt="Discover"></a><br><sub><b>185</b> · Discover</sub></td>
<td align="center" width="25%"><a href="docs/screens/186-wall.svg"><img src="docs/screens/186-wall.svg" width="210" alt="Wall"></a><br><sub><b>186</b> · Wall</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/187-shops.svg"><img src="docs/screens/187-shops.svg" width="210" alt="Shops"></a><br><sub><b>187</b> · Shops</sub></td>
<td align="center" width="25%"><a href="docs/screens/188-your-corner.svg"><img src="docs/screens/188-your-corner.svg" width="210" alt="Your Corner"></a><br><sub><b>188</b> · Your Corner</sub></td>
<td align="center" width="25%"><a href="docs/screens/189-feed.svg"><img src="docs/screens/189-feed.svg" width="210" alt="Feed"></a><br><sub><b>189</b> · Feed</sub></td>
<td align="center" width="25%"><a href="docs/screens/190-what-plays.svg"><img src="docs/screens/190-what-plays.svg" width="210" alt="What Plays"></a><br><sub><b>190</b> · What Plays</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/screens/191-rooms-desks.svg"><img src="docs/screens/191-rooms-desks.svg" width="210" alt="Rooms &amp; Desks"></a><br><sub><b>191</b> · Rooms &amp; Desks</sub></td>
<td align="center" width="25%"><a href="docs/screens/192-your-side-of-it.svg"><img src="docs/screens/192-your-side-of-it.svg" width="210" alt="Your Side of It"></a><br><sub><b>192</b> · Your Side of It</sub></td>
<td align="center" width="25%"><a href="docs/screens/193-ability-is-not-a-gate.svg"><img src="docs/screens/193-ability-is-not-a-gate.svg" width="210" alt="Ability Is Not A Gate"></a><br><sub><b>193</b> · Ability Is Not A Gate</sub></td>
</tr>
</table>

**69**, **75** and **76** carry the actual camera frames — the real photographs
that ship as `qrme/assets/desks/*.webp`, embedded into the SVG rather than
linked, because an SVG loaded through an `<img>` tag cannot fetch an external
file and a relative path would render as an empty box. The signs in them are
the whole feature: *ring bell for service, away from the desk*, and *be back
soon or ring bell*. That is the situation the bell was built for, and it is
what a visitor is actually looking at while they wait.

On **75** and **76** the chat, likes, shares and gifts render **on** the
picture rather than in a panel beside it — semi-transparent plates so the room
stays visible underneath, with the text on them kept fully legible. That is
where a viewer is already looking, and on a stream whose premise is an empty
chair with a bell, the reactions are the room. Those screens also show the two
ways in: **come up as a guest**, which asks the host, or **just comment**,
which is immediate.

**89** is the room itself: the video runs the full height of the screen, the
faces are circles on the glass, and everything a viewer can do is one strip
along the bottom — a composer, then the reactions as small circles in the
trailing corner. Every one of those was already a route, and none of them was
anywhere a thumb could reach, which reads exactly like a missing feature:

| On the strip | Route |
| --- | --- |
| person + arrow | `POST /desks/{desk_id}/guests` — asks the host |
| bell | `POST /desks/{desk_id}/bell` — one ring per desk per 30s |
| gift | `POST /{kind}/{subject_id}/gift` |
| heart | `POST /posts/{id}/like` — the audience layer |
| share | `POST /{kind}/{id}/share` |

Ringing and coming up sit in the same strip as like, gift and share because
from the viewer's side they are one gesture: a thing you do to the room you are
watching. That the guest request needs the host to say yes is the host's
business, not a reason to file it under a different menu. **75** and **76** are
where those conditions are spelled out; **89** is what it looks like once you
already know them.

### Full screen, and the three states every live surface has

**Press and hold, and the picture takes the whole phone.** No title, no tab
bar, no margin — full screen that stops short of the chrome is just a larger
box, and a screenshot of one that stops short of the file is a picture with a
band around it.

Holding is also what puts the **help button** back. It used to be welded to
every screen on the theory that "on all screens" is a property of the chrome
rather than something a hundred screens can each be trusted to remember, and
that theory is right everywhere except here, where the chrome *is* what is
being taken away: a floating `?` on a full-screen video is a permanent smudge
on it, and it sits in exactly the corner the share button now occupies. So it
comes back the way everything else does — press and hold and it surfaces,
along with the way into landscape and the way back to the app. The promise is
kept without the pixel.

The held state **dims hard** — 78%, not a tint — and the buttons are lit rather
than outlined. There is exactly one bright thing on the glass and it is the
thing you can press; a light scrim leaves the picture competing with the buttons
and turns a decision into a hunt. Tapping anywhere else takes the dim away
again, and the screen says so.

**Tilt and it goes wide.** This is the state that earns its place rather than
being a checkbox: the desk was shot sixteen-by-nine, and a portrait column crops
two thirds of it away. Sideways, the bell on the desk and the sign beside it are
in frame at once — which is the entire situation the feature exists for.

Those three states — plain, held, sideways — belong to a **surface**, not to
one screen. So every one of them has all three.

#### A live desk

<table>
  <tr>
    <td align="center" width="25%"><a href="docs/screens/89-live-room.svg"><img src="docs/screens/89-live-room.svg" width="180" alt="Live room in the app"></a><br><sub><b>89</b> · in the app</sub></td>
    <td align="center" width="25%"><a href="docs/screens/90-full-screen.svg"><img src="docs/screens/90-full-screen.svg" width="180" alt="Live room full screen"></a><br><sub><b>90</b> · full screen</sub></td>
    <td align="center" width="25%"><a href="docs/screens/91-full-screen-held.svg"><img src="docs/screens/91-full-screen-held.svg" width="180" alt="Live room held"></a><br><sub><b>91</b> · held</sub></td>
  </tr>
</table>

<table>
  <tr>
    <td align="center"><a href="docs/screens/92-full-screen-landscape.svg"><img src="docs/screens/92-full-screen-landscape.svg" width="600" alt="Live room, landscape"></a><br><sub><b>92</b> · sideways — the room at its own aspect ratio</sub></td>
  </tr>
</table>

**The rated stream gets the same three,** and the **18+ badge survives all of
them**. The gate belongs to the profile, not to the app chrome, so taking the
chrome away must not take the rating with it.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/93-rated-full-screen.svg"><img src="docs/screens/93-rated-full-screen.svg" width="190" alt="Rated stream full screen"></a><br><sub><b>93</b> · full screen · 18+</sub></td>
    <td align="center" width="33%"><a href="docs/screens/94-rated-held.svg"><img src="docs/screens/94-rated-held.svg" width="190" alt="Rated stream held"></a><br><sub><b>94</b> · held · 18+</sub></td>
  </tr>
</table>

<table>
  <tr>
    <td align="center"><a href="docs/screens/95-rated-landscape.svg"><img src="docs/screens/95-rated-landscape.svg" width="600" alt="Rated stream, landscape"></a><br><sub><b>95</b> · sideways · 18+</sub></td>
  </tr>
</table>

**A room with its camera on** is the other place a video and a conversation run
at once. Its strip carries a microphone rather than a bell — in a room you are
a participant, not a visitor at somebody's desk.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/96-room-full-screen.svg"><img src="docs/screens/96-room-full-screen.svg" width="190" alt="Room full screen"></a><br><sub><b>96</b> · full screen</sub></td>
    <td align="center" width="33%"><a href="docs/screens/97-room-held.svg"><img src="docs/screens/97-room-held.svg" width="190" alt="Room held"></a><br><sub><b>97</b> · held</sub></td>
  </tr>
</table>

<table>
  <tr>
    <td align="center"><a href="docs/screens/98-room-landscape.svg"><img src="docs/screens/98-room-landscape.svg" width="600" alt="Room, landscape"></a><br><sub><b>98</b> · sideways</sub></td>
  </tr>
</table>

#### A room that is not a camera

A room's channel can be chat, voice, video, **AR** or **VR** (`POST /rooms`),
and each of those is a different problem in the same three states.

**Audio is the case every layout forgets.** There is nothing to look at, so the
boxes *are* the screen — and they are not decoration: they answer the only two
questions an audio room raises, *who is here* and *who is talking*. The speaking
ring is the loudest thing in the tile. A muted person keeps their box rather
than vanishing from it, because somebody who has gone quiet is still in the
room and a layout that removes them is telling the others they left.

<table>
  <tr>
    <td align="center" width="30%"><a href="docs/screens/103-audio-room.svg"><img src="docs/screens/103-audio-room.svg" width="190" alt="Audio room"></a><br><sub><b>103</b> · audio · full screen</sub></td>
    <td align="center" width="30%"><a href="docs/screens/104-audio-held.svg"><img src="docs/screens/104-audio-held.svg" width="190" alt="Audio room, held"></a><br><sub><b>104</b> · audio · held</sub></td>
    <td align="center" width="40%"><a href="docs/screens/105-audio-landscape.svg"><img src="docs/screens/105-audio-landscape.svg" width="330" alt="Audio room, landscape"></a><br><sub><b>105</b> · audio · sideways</sub></td>
  </tr>
</table>

**AR puts them in the room you are already in.** That is the whole of what it
buys over a video call: the others are not in a strip down the side, they are
*somewhere* — beside the desk, by the door — and where they are is information.
The floor ring under each one is what makes them stand in the room rather than
float on the glass. The camera frame is a real photograph and carries no AI
mark; the people standing in it are synthetic and carry theirs, which is the
single place a missing badge would matter most.

<table>
  <tr>
    <td align="center" width="30%"><a href="docs/screens/106-ar-room.svg"><img src="docs/screens/106-ar-room.svg" width="190" alt="AR room"></a><br><sub><b>106</b> · AR · full screen</sub></td>
    <td align="center" width="30%"><a href="docs/screens/107-ar-held.svg"><img src="docs/screens/107-ar-held.svg" width="190" alt="AR room, held"></a><br><sub><b>107</b> · AR · held</sub></td>
    <td align="center" width="40%"><a href="docs/screens/108-ar-landscape.svg"><img src="docs/screens/108-ar-landscape.svg" width="330" alt="AR room, landscape"></a><br><sub><b>108</b> · AR · sideways</sub></td>
  </tr>
</table>

**VR is a room that is not a place.** Drawn rather than photographed, because
there is no photograph of somewhere that does not exist and a stock picture of a
headset would be a picture of the hardware instead of the room. A horizon, a
floor receding to a vanishing point, and the people standing at different
depths — depth carried by size and position, which is the whole of what 3-D buys
over a grid of boxes and the reason a room like this is worth having.

<table>
  <tr>
    <td align="center" width="30%"><a href="docs/screens/109-vr-room.svg"><img src="docs/screens/109-vr-room.svg" width="190" alt="VR room"></a><br><sub><b>109</b> · VR 3-D · full screen</sub></td>
    <td align="center" width="30%"><a href="docs/screens/110-vr-held.svg"><img src="docs/screens/110-vr-held.svg" width="190" alt="VR room, held"></a><br><sub><b>110</b> · VR 3-D · held</sub></td>
    <td align="center" width="40%"><a href="docs/screens/111-vr-landscape.svg"><img src="docs/screens/111-vr-landscape.svg" width="330" alt="VR room, landscape"></a><br><sub><b>111</b> · VR 3-D · sideways</sub></td>
  </tr>
</table>

**The vastscape is the room's biggest screen, borrowed.** Watch-together as it
looks when the thing being watched fills the wall a console or TV casts to, and
everyone watching is present as their own face — an avatar bubble resting *in*
the scape, not a strip of tiles down an edge. On a phone the app is the window;
here the phone is only the remote, which is the whole point: the picture belongs
to the room, and presence has to live inside it, where a couch full of people
would actually be.

<table>
  <tr>
    <td align="center" width="60%"><a href="docs/screens/194-the-vastscape.svg"><img src="docs/screens/194-the-vastscape.svg" width="330" alt="The vastscape"></a><br><sub><b>194</b> · The vastscape · cast to the TV</sub></td>
    <td align="center" width="40%"><a href="docs/screens/195-vastscape-held.svg"><img src="docs/screens/195-vastscape-held.svg" width="190" alt="Vastscape, held"></a><br><sub><b>195</b> · Vastscape · the phone as remote</sub></td>
  </tr>
</table>

The strip changes with the room and only with the room. An audio room has no
gift button because there is no stage to gift at; a posted video has no bell and
no guest request because there is nobody at a desk to ring and no host to ask.
A control that cannot do anything is worse than an absent one.

#### A video from somewhere else

<table>
  <tr>
    <td align="center" width="30%"><a href="docs/screens/99-posted-video.svg"><img src="docs/screens/99-posted-video.svg" width="190" alt="Posted video, in the app"></a><br><sub><b>99</b> · in the app</sub></td>
    <td align="center" width="23%"><a href="docs/screens/100-video-full-screen.svg"><img src="docs/screens/100-video-full-screen.svg" width="160" alt="Posted video, full screen"></a><br><sub><b>100</b> · full screen</sub></td>
    <td align="center" width="23%"><a href="docs/screens/101-video-held.svg"><img src="docs/screens/101-video-held.svg" width="190" alt="Posted video, held"></a><br><sub><b>101</b> · held</sub></td>
    <td align="center" width="30%"><a href="docs/screens/102-video-landscape.svg"><img src="docs/screens/102-video-landscape.svg" width="330" alt="Posted video, landscape"></a><br><sub><b>102</b> · sideways</sub></td>
  </tr>
</table>

The empty plate is the feature — see [the wall section](#the-community-wall-and-the-feed):
nothing is requested from YouTube until somebody presses play, so before they
do there is genuinely nothing to draw.

The mark runs in both directions across this set, which is the whole point of
it. **74** is the starter collection — every face there is generated, so it
carries the AI badge and the mark is burned into the portrait itself. **69**,
**70** and **75** are live desks and the room their viewers share: an actual
person is on the other end, so they carry no AI mark at all and make the
positive claim (*Live person — not AI*) instead. Absence alone would be
ambiguous; the claim is stated.

## Portraits

A profile can carry a face, and `GET /profiles/{id}/avatar` never returns a
bare one — the asset, the AI watermark, and the likeness record come back
together, so a 2-D card, a VR nameplate, and an AR overlay all receive the
disclosure from one place instead of each deciding whether to show it.

Whose face it is, is a rights question the API answers: an invented likeness
reports no rights holder, while a real person's face reports the recorded
grant, its attestor, and that it can be withdrawn. Starter portraits are all
invented people — the same promise `seed.py` already makes about the personas
— and the art direction is published at `GET /avatars/briefs`, generation-
ready.

All 34 starters ship **with** their portrait (`/portraits/{handle}.webp`), so
a beacon scanned by a stranger reveals a face rather than initials. See
[docs/avatars.md](docs/avatars.md).

### The starter collection

Thirty-three invented experts, one per industry, plus one rated profile — every
one seeded by `POST /marketplace/seed`. **The AI mark is burned into each
portrait's own pixels**, so it survives a screenshot, a hotlink, or a crop:
these images carry their disclosure wherever they end up, including here.

Each one is shown as **the card the app actually gives it** — screen 80, the
profile front page a visitor lands on, carried all the way through: the avatar
bubble, the role, the rating people who talked to it left, the skill chips,
Memory / Relationships / Engagement, then the career and a review, then **Talk
to …**. The gallery used to be a portrait with a name and an industry
captioned beneath, which is a directory listing rather than a profile, and it
was five columns wide — about 590px of content on a phone that offers 390, so
the fourth column was sliced mid-word and the fifth never appeared at all.
Two columns of whole cards fit.

**The careers and reviews are written, like the personas themselves.** These
are invented experts — that is the first line of this section — so a CV and a
notice from a satisfied reader are characterisation, the same kind of thing the
bio already is. Each one is drawn from that starter's own bio so the two cannot
contradict each other.

**The figures are sample values, identical on every card.** A freshly seeded
starter has no reviews, no relationships and no engagement, because nobody has
talked to it yet — those are the app's own mock numbers, repeated unchanged so
that thirty-four cards reading *4.0 · 37 reviews* are self-evidently a template
rather than a measurement. The name, role, portrait, industry and skills are
read straight out of `qrme/seed.py`.

The bubble inside each card is baked by `tools/bubble_portraits.py` into
`docs/portraits/bubbles/`, because GitHub's markdown sanitiser strips the
`style` attribute that would otherwise round it: on a surface QRME does not
control, the bubble is in the pixels or it does not happen. The shipped
`qrme/assets/portraits/` files stay square and untouched — the app draws its
own bubble, and baking one in would nest a bubble inside a bubble.

Cards are generated, never hand-written: `python3 tools/starter_cards.py` then
`python3 tools/starter_gallery.py`, both reading the starter list straight out
of `qrme/seed.py` so the page cannot drift from what a deployment actually
seeds.

<!-- starter-gallery:begin -->
<table>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/dr_amara_osei.svg" width="176" alt="Dr. Amara Osei — physician & health educator, healthcare"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/marcus_bell.svg" width="176" alt="Marcus Bell — retired fee-only financial planner, finance"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/priya_raman.svg" width="176" alt="Priya Raman — software architect, technology"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/elena_vasquez.svg" width="176" alt="Elena Vasquez — classroom teacher & learning coach, education"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/jonathan_ashe.svg" width="176" alt="Jonathan Ashe — retired contracts attorney, legal"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/sam_whitfield.svg" width="176" alt="Sam Whitfield — row-crop & vegetable farmer, agriculture"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/ingrid_halvorsen.svg" width="176" alt="Ingrid Halvorsen — plant operations engineer, manufacturing"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/diego_fuentes.svg" width="176" alt="Diego Fuentes — general contractor, construction"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/naomi_clarke.svg" width="176" alt="Naomi Clarke — residential broker, real estate"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/tomas_rivera.svg" width="176" alt="Tomás Rivera — power-systems engineer, energy"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/odessa_grant.svg" width="176" alt="Odessa Grant — logistics director, transportation"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/ken_nakamura.svg" width="176" alt="Ken Nakamura — omnichannel merchant, retail"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/lucia_moretti.svg" width="176" alt="Lucia Moretti — hotelier, hospitality"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/ray_coleman.svg" width="176" alt="Ray Coleman — documentary producer, media"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/wren_okafor.svg" width="176" alt="Wren Okafor — designer-illustrator, arts design"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/coach_dana_reyes.svg" width="176" alt="Coach Dana Reyes — strength & conditioning coach, sports fitness"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/chef_henri_laurent.svg" width="176" alt="Chef Henri Laurent — classically trained chef, culinary"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/dr_sana_iqbal.svg" width="176" alt="Dr. Sana Iqbal — climate scientist, environment"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/pete_kowalski.svg" width="176" alt="Pete Kowalski — retired city administrator, government"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/grace_mwangi.svg" width="176" alt="Grace Mwangi — nonprofit director, nonprofit"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/dr_felix_baum.svg" width="176" alt="Dr. Felix Baum — research physicist, science"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/aisha_diallo.svg" width="176" alt="Aisha Diallo — network engineer, telecom"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/harold_jenkins.svg" width="176" alt="Harold Jenkins — claims adjuster & underwriter, insurance"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/rosa_delgado.svg" width="176" alt="Rosa Delgado — master mechanic, automotive"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/cmdr_ellen_park.svg" width="176" alt="Ellen Park — aerospace engineer & test pilot, aerospace"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/mimi_beaumont.svg" width="176" alt="Mimi Beaumont — stylist & atelier seamstress, fashion beauty"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/jack_osei_turner.svg" width="176" alt="Jack Osei-Turner — brand strategist, marketing"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/nadia_petrova.svg" width="176" alt="Nadia Petrova — defensive security analyst, cybersecurity"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/bev_lindqvist.svg" width="176" alt="Bev Lindqvist — HR director, human resources"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/otis_marsh.svg" width="176" alt="Otis Marsh — session musician & teacher, music"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/dr_lena_whitcomb.svg" width="176" alt="Dr. Lena Whitcomb — clinical psychologist, mental health"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/dr_marcus_adeyemi.svg" width="176" alt="Dr. Marcus Adeyemi — psychiatrist, psychiatry"></td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/dr_priya_nair.svg" width="176" alt="Dr. Priya Nair — family & couples therapist, counseling"></td>
    <td align="center" width="50%" valign="top"><img src="docs/portraits/cards/vivienne_sable.svg" width="176" alt="Vivienne Sable — cabaret headliner & burlesque historian, adult"></td>
  </tr>
</table>
<!-- starter-gallery:end -->

## What's in the current release

The tables further down describe every capability in detail. This is the short
version of how it got here — what each release actually added, newest first.
Full detail in [CHANGELOG.md](CHANGELOG.md).

| Release | What landed |
|---|---|
| **0.63.0** | **The talk surface shows the face, and the face has a deck** — the microphone opens a full listening screen with the profile's portrait front and centre, pulsing while it listens, the reply spoken back (the orb only for a profile with no portrait yet); Identity's portrait card becomes a deck — characters, your own photos, a five-angle capture, and the avatar systems people already live in as imports with provenance on the record (`GET /avatars/market`, `POST /profiles/{id}/avatar/import`); the chat scrolls to the newest reply as it commits; `POST /social/{cid}/scrape` keeps what a public page shows anybody as a source item; and the console fits the phone it runs on — grid tracks clamp, `100dvh`, the sidebar scrolls on its own |
| **0.62.0** | **Cut in step** — JIM's phones reached parity with its console — eleven rounds in one branch: every backend route gained a door on iOS, Android and Windows (the doorless ledgers close at the four by-design rows), the voice pair landed on all three shells with the device's own voice as fallback, Android learned to say PATCH through a test-pinned override, and the most-touched screens swapped their English for the ten-language tables. No QRME code changed. |
| **0.61.1** | **Ability is not a gate** — an accessibility statement with a door under it: the Accessibility screen reachable before sign-in (`#access`), three questions with no account, no token and no name (the table has no identity column to fill), sealed to the PDI vault and read only under the reviewer token. Signup opens for the beta behind a keyhole that stays. The known-gaps ledger opened at three rows and closes at zero — wall uploads describe what they show, the chat log tells the screen reader, the shells carry the per-need statement — every closure held by a test, and Terms 1.2 says only what is true |
| **0.61.0** | **The beta stands up** — three products behind one proxy on one host, and the first real run found what no in-process test could: every console blanked by its own Content-Security-Policy. A policy of its own for `/app`, the bare domain now lands on the console, backups become a nightly job instead of instructions, bootstrap keeps its tenants across restarts, and the release-bodies sweep survives its first honest run — twice repaired, then proven against the live releases |
| **0.60.9** | **No change to this product** — the release-body work ends: every inherited body rebuilt from its own CHANGELOG entry, the record at a ceiling of 0 with one release kept deliberately, and three checks that reported success while doing nothing fixed. Carried here to keep the three at one version |
| **0.60.8** | **No change to this product** -- carried from PDI's round: a release checklist naming every version field, byte-identical in all three, and the deletion of `RELEASE_NOTES.md` after 412 of 530 releases proved to carry one frozen v0.24.0 body. A reader replaces the writer. Carried here to keep the three at one version |
| **0.60.7** | **No change to this product** — PDI's console round: a screen that imports the translator is not a translated screen. Two of its screens sat on the finished side of the ledger for twelve releases holding fifteen English strings; a guard now names that state on the round it happens. 91 → 32. Carried here to keep the three at one version |
| **0.60.6** | **No change to this product** — PDI's console round (Positions and Bridges, 154 → 168 → 91). Carried here to keep the three at one version. Its reader asked for a letter-space-letter and so could not see `Role &amp; industry`; this product's console reader records strings verbatim rather than counting phrases, so it has no such test to be wrong about — checked, not assumed |
| **0.60.5** | **No change to this product** — PDI's console round (225 → 154). Carried here to keep the three at one version. Its one portable lesson: two guards that greped their screens for English went red when the screens were localized, and now follow the key to the table instead |
| **0.60.4** | **The reader this product already had turned out to be the one that was right** — no change here. PDI's console was read by the regex shape this product abandoned rounds ago, and it was missing a quarter of the English. Two suites can carry the same guard by name and not by reach |
| **0.60.3** | **A check that cannot fail before the merge is not a check** — `ci.yml` carried the same blind trigger `native.yml` did, and had been red for 29 runs on four guards that shell out to the JSX-text extractor: the job running pytest installed no node dependencies, so they failed on the runner and passed everywhere else. Trigger fixed, dependencies installed, and a guard that reads the triggers themselves |
| **0.60.2** | **The compiler was in the room the whole time and nothing listened** — `native.yml` had been red for 123 runs on a trigger the release loop never reached. Fixed, and the shells then named real defects: an Android L10n table too large to compile at all, 944 lines of `ApiClient` living inside a record's body, two records whose mid-list default swallowed the last positional argument, and a dozen members that were never there |
| **0.60.1** | **A fix to the cascade fixes the next delete, not the last one** — every profile ended before 0.59.9 was ended by a list of 24 table names against a schema of 66, and the 42 tables it missed are still sitting in every deployment running since. `python -m qrme.orphans` is the reach-back: dry by default, `--apply` to clear, scope taken from the cascade's own reader. Its sharp property is not *does it find the orphans* but **does it leave a living profile alone** |
| **0.60.0** | **An export is measured against the schema too** — `GET /profiles/{id}/export` says *access everything, anytime (You Own It)*, the README's capability table points at it, and the suite gateway's GDPR Article 20 bundle is built on it. It returned **6 tables of 66**. Now derived from the schema like the erase cascade, with live credentials dropped **per column by rule** — the first cut was a list of column names and the new guard caught three it missed on its first run |
| **0.59.9** | **An erase is measured against the schema, not a list somebody wrote** — `DELETE /profiles/{id}` says *the profile and every trace of it*. It named 24 tables; the schema has **66** with a `profile_id` column, so 42 survived — `clinical_notes`, `media` and `media_watermarks`, `anonymous_pictures`, `homepages`, `friendships`, `inbox_events`. The cascade is derived from the schema now, and a guard plants a row in every scoped table, deletes, and looks |
| **0.59.8** | **The check that covered one client of four** — 0.59.7 asked whether the shape a screen declares is the shape its route answers with, and asked it of the console alone. The three shells decode the same answers into their own types, and a wrong one there throws the same way. Extended to all four clients (console 422 · iOS 300 · Android 316 · Windows 342); no disagreements, and the reach is now a record that cannot go down, because a reader that stops matching reports agreement |
| **0.59.7** | **`req<T>` is a cast, and a cast is a claim nothing checks** — a route answers with a shape and a screen declares one, and between them sits a TypeScript generic the compiler cannot verify against anything: the body arrives through `JSON.parse`, which is `any`. Next door two screens declared an array where the route answers an object and threw `.map is not a function` during render. This console agrees on all 422 typed calls; the guard is here so it stays that way |
| **0.59.6** | **The clients agreed with each other and were all wrong** — parity between clients is a relative check, and a relative check is satisfied by everybody being equally wrong. Next door a vault under customer custody required `x-tenant-key` on every record route and no client sent it, so pressing *hold our own key* locked all four clients out — including out of the button that undoes it. The new guard reads the requirement out of the **application's** dependency tree, then asks each client only about the routes it actually calls |
| **0.59.5** | **The third sink, where both the escaping and the policy miss** — inside a `<script>` the HTML parser ends the element at the first `</script`, whatever the JavaScript quoting says, so a value can close the page's own nonced script and everything after it is markup. This product's `_js` composed both escapers correctly; the siblings' were bare `json.dumps`. All three now share one primitive, and every value entering a script is checked to pass through it. The consoles were swept too and are clean — no `dangerouslySetInnerHTML`, `innerHTML`, `eval` — now a floor |
| **0.59.4** | **The sweep that found the last one, kept** — 0.59.3 found reflected XSS by walking every f-string that builds markup, by hand, once, and throwing the walk away. It is now a guard with a ratcheted record: **8 rows**, all pre-escaped composites the analysis cannot follow. It follows escaping through single assignments and helper returns (32 rows → 8 without it) and refuses to read `http://localhost:<port>` as a page. Put 0.59.3's defect back and it names the file, the line and the expression |
| **0.59.3** | **Reflected cross-site scripting on the sign-in callback** — `?error=<script>…` came back as live markup on a page served from this origin, and every HTML page a stranger reaches carried no `Content-Security-Policy`, no `nosniff`, no frame or referrer policy. Escaped at the interpolation, and `pagehead.py` now stamps a per-response nonce the policy names, so an injected tag has none and does not run. Verified in real Chromium: no CSP violations, the page still works |
| **0.59.2** | **A crash the browser threw away** — an unhandled 500 is rendered by Starlette *outside* every middleware the app adds, including CORS, so it went back with no `access-control-allow-origin` and the browser discarded it whole. Every crash reached its user as "Failed to fetch", indistinguishable from a backend that is not running. No in-process test could see it: a `TestClient` sends no `Origin` and applies no browser rule. Fixed with a catch-all inside the CORS layer, and guarded by a file that boots a real server |
| **0.59.1** | **Three suites, and nothing comparing what they ask** — every guard here exists in three copies and the copies drift silently. A sweep of test-function names found 370 carried by all three and 140 by exactly two. Four of those were one defect in PDI. The shared vocabulary and the divergences are now written down, byte-identical in all three repos, so each product checks its own half with no sibling checkout — plus the live three-way comparison when they are on disk |
| **0.59.0** | **A floor nobody raised** — two rounds found the same defect in two instruments, so this one swept every floor in the suite. 91 of them carried their own literal with no way to measure what they held, and every reachable one was decoration: l10n 10 against 945–961, path literals 40 against 1407, console call sites 200 against 429. `ratchets.py` is the convention — a floor plus the way to read the same quantity now — and the rest are held in a backlog that only shrinks |
| **0.58.9** | **Ten against nine hundred and forty-five** — the L10n guard's floor has not moved since it was written: ten localizer calls, twenty table rows, against tables that now hold 1087–1115 rows and screens that make 945–961 calls. Narrowing the call pattern to `L10n.t("…")` blinds C# alone — Windows 945 → 52 — and 294 tests pass while the one failure names four rows as a backlog complaint. Per-shell floors on both halves, plus a spread across the three ports that needs no hand-chosen number |
| **0.58.8** | **The route reader had one floor and four clients** — the console's extractor has been floored since it was the only client; the three shells had nothing. Blinding the iOS `request(` form drops it 430 → 11 call sites while `doorless` still reports zero, because the other clients cover for the blind one. Two floors now: an absolute one per client, and a spread across the three shells that needs no hand-chosen number |
| **0.58.7** | **A wire model is data, and data has no methods** — every pin now asserts on both ends and three checks audit the readers themselves. The first run of that audit found a missing brace, not a reader bug: `SpecialistRow` was never closed and the `extension ApiClient` after it never opened, so ninety-five client methods were declared on a two-field wire model. Brace balance passed, the member check passed, the pins passed |
| **0.58.6** | **The refusal surfaces** — the screens that render what the platform will *not* do, checked at both ends on all three shells: overlay kinds and refusals, the microphone vocabulary, the places a wearable may be lent, the contribution log. All correct, all pinned. The trap was the guard's own: PDI declares one-line structs, the property pattern required end-of-line, and a pin had been checking an empty model since the day it was written |
| **0.58.5** | **The disclosure that showed nobody** — the mic routes answer with `microphones_lent` and all three shells read `lent`, so the list of who in a room has lent the profiles an open microphone rendered as nobody on every client. Six more pinned rows, and the reader now follows a list built by appending — the limit 0.58.4 named and refused to guess past |
| **0.58.4** | **The key was right and the shape was wrong** — binding a decode site to its route is not derivable by reading this backend; four attempts are recorded and none shipped. What shipped instead pins a shell model to the function whose `return` is its contract, and the pinning found the guided tour blank on both phones: the outline read `key`/`title` off `{chapter, steps}`, and three buttons decoded `tutorial.where` as the step it wraps |
| **0.58.3** | **The key the server never sends** — a `Decodable` property name *is* the wire key, and a wrong one fails on a phone rather than on a build machine. Four live breaks: the overlay disclosure showing nobody on both phones, Sign in with Google and Apple unable to start on either, the helper's *where does this live* line half blank on Android, and the referral list reading a boolean where a timestamp is |
| **0.58.2** | **The colour that wasn't in the palette** — 0.58.1 checked the one receiver whose type is known for free; this checks all eight. The Android problem-report card painted itself with `Qrme.Card2` on a theme that declares `Card` and never a second, which Compose does not compile. The API clients came back clean across 1,613 call sites, and are asserted anyway |
| **0.58.1** | **The member that isn't there** — with no Swift, Kotlin or C# compiler here, the native UI is checked by reading; this takes the next class of compile error that reading can catch. Each shell has one object the screens read their session from and one file declaring it, so a member it does not declare is not a style question. Clean in this product; the sibling shells had thirty-nine call sites that do not compile |
| **0.58.0** | **The key the phones never carried** — auditing every header the console attaches to every request turned up one the shells do not send at all: `x-llm-api-key`, the person's own model key, pasted into the console since 0.4.3 and read by the backend per request. A key set on the desktop ran the desktop; the phone quietly ran the deployment's — same account, two credentials, nothing saying so. All three shells now hold one, offer a field for it under the console's own words, and send it |
| **0.57.9** | **A funnel only funnels what goes into it** — comparing the three test directories turned up a guard that existed in the other two products and not in this one, the product whose whole premise is speaking in a person's language. Porting it exposed what it could not ask: **21 of 22 Windows sends, 3 of 4 on iOS and 1 of 2 on Android built their own request beside the shared helper** and carried no `Accept-Language`, so every refusal they drew from an expired token arrived in English. One dispatcher per shell, and a check that walks dispatch sites rather than header lines |
| **0.57.8** | **The rows the guard skipped were the interesting ones** — the untranslated-literal check opened with `if "{" in english: continue`, so every row with a slot in it went unchecked for four releases. Those are most of what a screen says, and the sentence built around a value is the one a screen hand-builds. Twenty-seven sites: the whole provenance footer in English on the desktop and both phones, the watermark verdict, the objection status, the licence offer, the signing credential list. Slotted rows are compared by their fragments now; `native_dead_keys` 300 → 276 |
| **0.57.7** | **The files the release never touched** — fifty-five cuts bumped `pyproject.toml`, `api.py`, `package.json`, the README banner and the changelog, and not one of them touched the three files the phones report their own version from. `MARKETING_VERSION` and `versionName` said `0.1.0`; the `.csproj` declared no version at all, so every Windows build since the shell was written reported `1.0.0`. A `versionCode` of `1` would have had the first Play upload refused outright. The same files carry what each shell is allowed to do, so those are checked here too |
| **0.57.6** | **The half of the Windows shell that is not code** — 0.57.5 globbed `*.swift`, `*.kt` and `*.cs`, called that three shells and reported them parseable. The Windows shell's screens are XAML, and it never opened one. Two pages here carried `x:Name` twice on a single element, which no XML reader gets past; three more in JIM-mini. Four markup checks — well-formedness, one name per element, handlers that exist, controls the page declares — and the voice screen, read while fixing it, was printing seven sentences in English that its own table translates ten ways |
| **0.57.5** | **Nothing here builds the phones, so nothing here noticed when they stopped** — 0.57.4 shipped a Swift compile error because every guard reads these sources as text and none of them parse. A duplicate-declaration and brace-balance check for Swift, Kotlin and C#, narrow by design: it does not promise the shells build, only that they lack the mistake that got past everything else |
| **0.57.4** | **The inputs the shells never asked for** — 0.57.3 recorded six native-write defects as *needing an input the shell does not collect*; this collects them. A department beside the goal, a camera address, a locality and an include-remote switch, `price` where the shells said `amount`, and the signed-in actor on an accept. Six dead buttons across three shells, and the record is empty. Also fixes a Swift compile error 0.57.3 introduced |
| **0.57.3** | **The guard read one client and the finding came from four** — request bodies checked across the Windows, iOS and Android shells. Seven defects, each present in every client that makes the call, including a marketplace listing placement that has never worked on any native surface. Thirteen of the first twenty findings were the extractor's own, and a seventh defect surfaced only because PDI's Windows reader hit zero |
| **0.57.2** | **Every guard reads the answer; none read the question** — nothing had ever checked a *request* body against the model FastAPI validates with. QRME's 192 writes are correct; the guard's own first run produced 82 findings that were all its own defect, and a fifth was caught only by comparing how much of each client it reached |
| **0.57.1** | **The fourth client, and it was the only one wrong** — the console declares more than the three native clients combined and nothing had ever checked it. Four defects, all visible: the delegation screen could not delegate, a dashboard tile had never shown a number, suggested friends was always empty, and a list was declared a count. Windows, iOS and Android were right about all four |
| **0.57.0** | **Twelve routes out of forty-two, and twelve looked like all there were** — the Kotlin guard travelled to JIM-mini and PDI by requiring a `JSONObject(` wrapper those clients do not use, so it read a quarter of one file and passed. Constructor made optional, parse-helper and chained reads added: QRME 135→169 routes, JIM 12→44, PDI 13→18. Three of the new findings were the guard's own defects, caught before shipping |
| **0.56.9** | **The client that declares nothing was guessing hardest** — Kotlin has no structs to check, so nobody had; every `optString("k")` is a claim about a name *and* a type, and `org.json` never throws when either is wrong. Eight wrong reads, all already fixed in C#. Five faults in my own extractor found and fixed before any of them shipped |
| **0.56.8** | **Fixing a defect in one client was not fixing the defect** — the shape guard now reads Swift too, and found nine fictions in the iOS client that had all been fixed on the Windows side releases earlier. Its own extractor made the same swallow-the-next-struct mistake the C# one did, in a different language |
| **0.56.7** | **`kinds` meant three things, and one of them crashed the client** — `/wearables` sends it as a map where the record declared `string[]`, so that call threw rather than losing a field. `kinds`/`refused` split into six honest names (record 23 → 21), and the shape guard now checks that a declared type can decode what arrives — which found five more live crashes |
| **0.56.6** | **Eight watch faces that were not on the page** — reported from a phone. An HTML table is as wide as its longest row, so one `<tr>` with fifteen cells beside rows of three left twelve blank columns everywhere and clipped the rest off a phone. Every gallery is a uniform grid now — four across for screens and watch faces, two for desktop frames — with a guard that reads the widest row, not the first |
| **0.56.5** | **The guard travelled** — 0.56.4's shape guard ported to JIM-mini and PDI, and both siblings came out clean: only this client had been written from imagination. PDI's copy needed its own binding regex, because a pattern borrowed from here finds zero calls there and zero found reads like zero wrong |
| **0.56.4** | **A client record is a claim about a route** — `share`'s unexplained side turned out to be a Windows record declaring `name` and `share` on a route that has only ever sent `display_name` and `weight`; the button wired to it drew separators with nothing between them. Fourteen records were the same guess. New guard drives every GET binding and checks the claim. Collisions 24 → 23 |
| **0.56.3** | **The count and the state wore the same name** — `seen`, `available` and `revoked` were each a boolean *and* a tally of that boolean, and a decoder handed `1` where it wants `true` coerces rather than refusing. Counts renamed; a fourth row turned out to be a Windows decoder bug rather than a collision. Record 28 → 24 |
| **0.56.2** | **The compiler nobody ran** — `tsc` is in the suite in all three repos now, along with a guard that fails when one wire name carries two types. 28 collisions found here and recorded: `sources` is four types, `messages` and `watermark` three each |
| **0.56.1** | Cut together at one version; JIM-mini trains a real offline model from its own follow-up record, and PDI's HSM key path stopped being a seam |
| **0.56.0** | **The count of what was synthetic** — `attention.py` tells you how divided a profile's attention is; nothing told *you* how one-sided yours had been. Counts from your own logs, readable by you alone, with a door to JIM-mini above the line — and four tests holding it to a count rather than a diagnosis, a notification, a signal somebody else can read, or a transcript with a referral stapled to it |
| **0.55.0** | **The rule the record stated** — the field-label backlog's own header said *map one when a form starts asking a person for it*, and nothing was checking it; the blend screen had been asking for **share** and **their…** in ten languages while the refusal underneath said `weight` and `aspect`. Plus the guard that reads the screens, which failed first on an Arabic label written ten minutes earlier |
| **0.54.1** | **The twenty-four, read one at a time** — twelve were labels and are keys now, including a signature attestation pre-filled in English while its translation sat beside it; twelve are values a route matches on and stay English. Plus one badge that had two words across shells |
| **0.54.0** | **The shells that say less** — the iPhone had no camera-permission state, so a declined viewfinder showed a black screen instead of *nothing is recorded*; Windows printed "scan(s)" and "picked up" in English beside their own translations. Plus the guard that finds the rest — whose first version could not see the bug it was written for |
| **0.53.1** | **Nothing reaches the other platform** — the network is unplugged and a video is posted, the wall rendered and the feed loaded. The promise held; a `None` field and a sentence were all that had been guarding it |
| **0.53.0** | Cut together at one version; the round's work audits promises this repo ships in the same shape — a claim about an absence has to be falsified from outside the claim, and saying only what you refuse is how a true sentence misleads |
| **0.52.0** | Cut together at one version; the round's work is JIM-mini enforcing a promise that had been a caption — the same argument this repo settled for the feed, where the enforcement point is whoever holds the thing |
| **0.51.0** | **How many people it is talking to** — public, no token, on the accountless screen and all three phones: distinct people this week and altogether, with no ranking, no favourite and no names, greppable rather than promised |
| **0.50.0** | Cut together at one version; the round's work is JIM-mini's presence — and its door onto this platform hands over rooms, desks and profiles as offers, with no bell rung on anybody's behalf |
| **0.49.0** | **The stream** — one public card at a time: footage this deployment holds loops, anything on somebody else's platform stays a card until pressed, and every fourth card is a live room or a desk with a person behind it. JIM-mini's Feed tab is a GET-only door onto the same stream |
| **0.48.3** | Cut together at one version; the round's work is PDI's console — Custody and Continuity, 229 → 177 |
| **0.48.2** | The third axis measured at last — the three shells against each other — and it held **one** row here: *Sign out* was *Sair* on the phones and *Terminar sessão* on the desktop shell. A 0.48.1 record entry corrected: one of its two "shells disagree" rows was not one |
| **0.48.1** | **Two tables, one product** — 223 English strings live in both the console table and the iPhone's and 102 had no wording the two agreed on; the desktop says *Sie* (204 rows) where the phone says *du* (60); the voiceprint, desk and chrome surfaces reconciled, 102 → 8 |
| **0.48.0** | **The same sentence, translated twice** — 54 English strings under 2+ keys on iOS and 43 of them already drifted; 34 sets reconciled, 42 recorded as questions about the English; two tab-bar entries that read alike in three languages; and a `\u0027` that stops `L10n.swift` compiling |
| **0.47.9** | **The number was mislabelled, and it was hiding a consent screen** — 263 of the 335 "dead" rows are asked for by a different shell, so they are screens saying less rather than waste; the voiceprint consent block's three sentences were hardcoded English on the iPhone, in an array a loop reads |
| **0.47.8** | Cut together with the other two at one version; the round's work is PDI's Transfers screen |
| **0.47.7** | **The other two syntaxes** — 0.47.6 derived the label rule for Kotlin and left Swift at eight hard-coded constructs and XAML at four attributes; the Windows code-behind sets half its labels by assignment, which `Text="` cannot match, so 91 call sites across nine shells were invisible |
| **0.47.6** | **Every button on the Android shell was English** — Compose has no `Button(text)`, so the untranslated rule's `Text(` pattern read none of them; the rule now derives label-bearing functions and their argument positions from the shell, 91 call sites wired, and this round's 366-row prune withdrawn because 59 of its deletions were rows the shell should ask for (540 → 350) |
| **0.47.5** | **Three screens titled with their own key names** — the dead-key guard ported from JIM-mini found `tab.compose`, `tab.posts` and `tab.robots` missing from the Android table, so those headings rendered the key; plus 540 dead rows recorded and ratcheted |
| **0.47.4** | Version alignment — the round's work was JIM's Overview and the tab strips whose English lived in an enum's `case` clause (229 → 150) |
| **0.47.3** | A guard on the route audit itself — every path literal must sit inside a call shape it knows, or be recorded as not a request; found two Android calls here written one statement away from the call site |
| **0.47.2** | The PaneFooter sign-out bug found and fixed here at 0.46.9 was never carried to the sibling — it is now, along with JIM's Family and Connect screens (386 → 229) |
| **0.47.1** | The ternary blind spot was in all three products — widening ported to JIM and PDI, which were understating by 40 and 12 |
| **0.47.0** | **The ternary hid the sentence, and then the floor** — a string chosen by a condition was invisible to the native-shell measurement, hiding the signing screen's *"Verifies"*, the voice-enrolment gate and the desk's *"Ring the bell"* on all three shells; the count corrected 68 → 125 and then run to 7, none of which is English |
| **0.46.9** | **Six screens on three shells, and the button that ends the session** — Overview, Compose, Posts, Connect, Robots and Study localized everywhere (212 → 68); Windows' Sign out sat in the pane footer where the nav localizer never walked, so it read *"Sign out"* in all ten languages while the row it needed sat unused in two other tables |
| **0.46.8** | **The reach console, and a crisis number that only works in one country** — Manage/Reach localized on iOS, Android and Windows including its own sub-tabs (368 → 212); the wellbeing card's *"call or text 988"* replaced with local crisis line or emergency services, in all ten languages |
| **0.46.7** | **Signatures and Voice, and a gap on one shell** — both screens localized on iOS, Android and Windows (470 → 368); two cards localized on two shells last release and missed on Android are finished, at the cost of no new rows at all |
| **0.46.6** | **The rest of Settings, and Community** — steering, relationship, feedback and the failure-report consent notice, plus the stranger and room screens, on all three shells (590 → 470); three relationship pickers stop rendering `romantic_partner` as a word |
| **0.46.5** | **The first screen, on all three phones** — Welcome and Settings localized on iOS, Android and Windows (703 → 590); the first-run screen reads the device's language because no profile exists yet to hold one; the Android shell did not compile and now does |
| **0.46.4** | **The refusal names a field the form never named** — the signature box on Referrals had a placeholder and no label; the label is added, ported into the field table, and the record drops 124 → 123 (PDI's 91 → 51) |
| **0.46.3** | **The console record reaches its floor** — Simulate, Memory and Friends localized; console-untranslated 25 → 1 after twenty-one releases, the last row kept on purpose because `AI ·` is quoted rather than written |
| **0.46.2** | **The front page, the price list, and who is in a life** — Home, Plans, Relationships and Discover localized (console-untranslated 69 → 25); the relationship dropdowns were posting their visible label to the API, and now post the enum |
| **0.46.1** | **The room, the conversation, and the door to both** — Rooms, Chat and Inside localized (console-untranslated 116 → 69); the dead-key guard learns that a key can live in a table, and a new check catches an English word left inside a Japanese or Chinese sentence |
| **0.46.0** | **The wall, the guide, and the blend** — Wall, Guide and Blend localized; console-untranslated 180 → 116, with no rows kept back |
| **0.45.9** | **The thing named, what leaves, and the mark it carries** — Named, Leaving and TheMark localized (console-untranslated 254 → 180); one row kept on purpose, because `AI ·` is quoted rather than written |
| **0.45.8** | **The money, the loan, and the firm** — Campaigns, Grants and Org fully localized (console-untranslated 338 → 254); the table's ten-language check widened from the sidebar to all 1519 rows |
| **0.45.7** | **The ledger, the name, and the stranger** — Audience, InWords and Stranger fully localized; console-untranslated 425 → 338 |
| **0.45.6** | **The lobby, the screen in the corridor, and a voice** — Lobby, Presence and Voice fully localized; console-untranslated 516 → 425 |
| **0.45.5** | **The objection, the camera, and the market** — Contest, Live and Market fully localized; console-untranslated 616 → 516; the dead-key guard learns to name its own blind spot |
| **0.45.4** | **Two directions, one picture** — WatchParty, Delegate and Beacons fully localized; console-untranslated 724 → 616 |
| **0.45.3** | **Three more, and the wrist among them** — Passing, Signing and Placements fully localized; console-untranslated 848 → 724 |
| **0.45.2** | **The three biggest screens left** — Exchanges, Reaching and Visiting fully localized; console-untranslated 978 → 848 |
| **0.45.1** | Version alignment with JIM's console-to-zero round |
| **0.45.0** | **Under a thousand** — the Workshop and Bodies screens fully localized; the console-untranslated record crosses into three figures (1072 → 978) |
| **0.44.9** | **Who this profile is, in every language** — the Identity screen fully localized (console-untranslated 1121 → 1072) |
| **0.44.8** | **The tail of the audit speaks** — the Remainder screen fully localized (console-untranslated 1172 → 1121) |
| **0.44.7** | **The handover speaks** — the Referrals screen fully localized (console-untranslated 1225 → 1172) |
| **0.44.6** | **The counter in the street speaks** — the Desk screen fully localized (console-untranslated 1281 → 1225) |
| **0.44.5** | **The counter speaks** — the Selling screen fully localized (console-untranslated 1337 → 1281) |
| **0.44.4** | **The Control Center speaks** — the Settings screen fully localized (console-untranslated 1403 → 1337) |
| **0.44.3** | **The backlogs shrink from both ends** — the Assist screen fully localized (console-untranslated 1459 → 1403) and the field-label evidence pass maps seven newly-typed fields (residue 131 → 124) |
| **0.44.2** | **The last doors** — genesis and hybrids, packs, simulations and fine-tuning, the contribution ledger, proactive reach and quiet hours, licensing, and the senses reach all three shells; **the doorless records run to zero** (ios 0 / android 0 / windows 0) |
| **0.44.1** | **The sticker, the queue and the stamp** — beacons/QR and pairing, the moderation queue with message edit/retract, reviews, watermark resolution and tamper-check, media upload and wearables reach all three shells; **71 doorless rows struck**, records fall to ios 21 / android 26 / windows 24 |
| **0.44.0** | **The keys, the till and the lifeline** — accounts (signup, sign-in, verification, reset, OAuth), money (plans, subscriptions, orders, proceeds, campaigns) and status+help reach all three shells; **72 doorless rows struck**, records fall to ios 45 / android 49 / windows 48 |
| **0.43.9** | **The face it shows the world** — the portrait, the emblem and badge, the page and themes, the front, the surfaces, the blend, the bodies, the dials and the wrist reach all three shells; **72 doorless rows struck**, records fall to ios 69 / android 73 / windows 72 |
| **0.43.8** | Version alignment with JIM's watch-picker round (device picker, Fitbit seed, Bluetooth pairing) |
| **0.43.7** | **The record, the veil and the exit** — the memory list, the pair's record, source material, the ledger (transparency/export/stats/feed), anonymity, verification and the three ways a profile ends reach all three shells; **75 doorless rows struck**, records fall to ios 93 / android 97 / windows 96 |
| **0.43.6** | **The workshop in the pocket** — workflows and their pauses, the delegation envelope, the assistant's verbs, tasks under a revocable grant, rated placements and specialists reach all three shells; **84 doorless rows struck**, records fall to ios 118 / android 122 / windows 121 |
| **0.43.5** | **The seal, the mail and the screen** — signatures and verification, mail settings, rooms and the microphone disclosure, wall screens, memberships, consented handoffs and campaigns reach all three shells; **74 doorless rows struck**, records fall to ios 146 / android 150 / windows 149 |
| **0.43.4** | **The body, the case and the lobby** — robot audit trails and dials, the medical referral flow, objections, the game lobby's honest roster and the helper dock reach all three shells; **75 doorless rows struck**, records fall to ios 171 / android 175 / windows 173 |
| **0.43.3** | **The place, the camera, the organization and the tour** — whose-corner, microphone and overlay disclosures, the camera with its refusals, organizations and the guided tour reach all three shells; **81 doorless rows struck**, records fall to ios 196 / android 200 / windows 198 |
| **0.43.2** | **The crowd, the couch and the loan** — the audience verbs (like, share, subscribe, gift), the watch party and skill grants reach all three shells; **84 doorless rows struck**, records fall to ios 223 / android 227 / windows 225 |
| **0.43.1** | **The platform tells you what happened** — an inbox of deeds done to you (message, comment, friendship, signature, a place on a stream), named but never quoted, on the console and all three shells |
| **0.43.0** | **The phone could be listed and could not do business** — 46 routes for staffing a desk, trading in the market and signing an exchange reached iOS, Android and Windows; **139 doorless rows struck**. Plus two guard-invisible image doors and a 204 that made every successful delete report failure |
| **0.42.9** | **The people around a profile reach the phones** — friends, suggestions, the wall and comments gained People screens on iOS, Android and Windows; 27 rows struck from the per-shell doorless records, with the pinned/blocked/ranked-on rules rendered rather than re-decided |
| **0.42.8** | **The record said nobody asks; the forms had started asking** — 107 of 251 recorded "no form asks for this" fields turned out to be bound to real console inputs; all now carry ten-language labels, leaving 144 rows that match the record's own rule; the agent-lights widget now shows an unlit retry dot when the backend is unreachable instead of silently vanishing |
| **0.42.7** | **The person decides who reaches them** — friends-only messages with per-profile feature switches that refuse by name, and a MySpace-style homepage sandbox (hex colors, http(s) links, plain text, actual friends) on all four clients |
| **0.42.6** | **Version alignment** — JIM gained booking/scheduling with bottom-rung reminders and self-only email; a shop service can now be booked as one act, order and appointment together |
| **0.42.5** | **A shop is not a desk** — standalone storefronts: one shop per profile, offerings with price/currency/availability, buyers are interactors, fulfilment (and only fulfilment) credits the ledger, both sides can let go. Eight routes with doors on all four clients in the same cut (console screen 187 + iOS/Android/Windows), and a test that a shopping day writes nothing into any desk table |
| **0.42.4** | **Version alignment** — JIM's money guardian gained its native doors; the finance desks QRME serves beside a warning are now reachable from the phones that show it |
| **0.42.3** | **The last thirteen unaudited screens** — across the three repos, thirteen components had sat `unaudited` since the manifests were seeded; the audit confirmed eight of them had never been drawn at all. QRME's two were both in that eight: screens **185 Discover** and **186 Wall** are the drawings, both `unaudited` ceilings fell to zero, and `undrawn=0` is finally true rather than covered for |
| **0.42.2** | **Version alignment** — JIM gained its money guardian; QRME's `GET /desks` now serves its warnings, listing real finance desks beside the tandem specialist |
| **0.42.1** | **The starters can answer for their own trade** — one Field Pack left five of eight prompt seats empty on every starter. `dossiers.py` now gives all 34 — Vivienne Sable included — what-I-know, skills-and-services and colleagues source items, 8+ skill chips, and a colleague graph installed as real friendships, composed from the same list as the prose so chat and the API give one answer. 77 tests, both directions |
| **0.42.0** | **The desk can finally do the job** — every desk surface let a person reach the counter and none let the desk do the work it exists for. Service sessions and connections shipped: the desk offers (screen, machine, program, files), only the caller's accept mints the link token — returned to them alone — and either side ends it, the token dying in the row. Rated desks gate the accept behind the same adult wall as every other surface . A desk can also lend a *skill* — `app` joins the lendable kinds (a connected program like Cursor, driven through the lender's own connector, every use logged), and a counter session is a grant surface that takes its skills with it when it closes |
| **0.41.0** | **The workflow round-trips and nothing walked the whole arc** — `workflows.py` names three properties a delegated multi-phase goal has to keep, each unit-tested on its own side of the wire; the one check that boots all three products drove a single exchange and stopped, never calling `start_workflow`, `advance` or `specialist_tasks` across the boundary. Driving it surfaced the Pro gate and the owner's opt-in as steps rather than surprises, and the arc now walks research → draft → send and pauses at `confirm` |
| **0.40.9** | **The README said v0.18.0** — the first bold line of every README named a release twenty-two cuts old, on the line directly above one promising the three products are versioned and cut together; the history table underneath stopped at 0.30.6, leaving seventeen shipped releases in the changelog and off the page anybody reads. Both are now checked against `pyproject.toml` and the changelog, and five of seven unaudited screens are resolved by reading each component's heading rather than its name |
| **0.40.8** | **The refusal named the field the API calls it** — An earlier round took the 422 from `[{"type":"missing",...}]` to one sentence a person can read, in their own language. |
| **0.40.7** | **The record that outlived the code** — `public_untranslated.txt` opened with a paragraph explaining that `Onboarding.tsx` — the screen every person in the world meets first — carried forty-odd English strings, that translating them was "its own round", and that a half-translated sign-up form would be worse than an English one. |
| **0.40.6** | **The stranger's language, finished** — Two rounds ago every shell learned to work out what language its reader speaks without a profile — `Locale.preferredLanguages`, the system locale list, `CurrentUICulture` — and the round stopped there, on purpose: twenty-odd sentences on ea |
| **0.40.5** | **The door they closed was the owner's** — Deletion in this product retires the owner's token. |
| **0.40.4** | **A memorial that kept posting** — `POST /profiles/{id}/chat` has refused a departed profile for releases: `POST /profiles/{id}/compose` — which writes a public post in that profile's voice and publishes it where anyone can read it — had no such check. |
| **0.40.3** | **The provenance named the model that was asked, not the one that answered** — `content_provenance` is this product's central claim, and its own docstring says so: *the verifiable basis of a piece of persona-generated content: which model produced it ... |
| **0.40.2** | **The refusals, finished** — 0.24.0 translated the eleven refusals any route can raise and **wrote the rest down**. |
| **0.40.1** | **The objector could end a profile and could not read their own case** — `GET /objections/{id}/audit` is owner- or reviewer-gated, and its docstring gives the reason in its own words: *it can quote the objector's reason*. |
| **0.40.0** | **A rule reversed, and said so rather than changed quietly** — `test_the_nav_is_translated_and_nothing_behind_it_is.py` records how many English strings sit behind this console's forty-six translated sidebar labels. |
| **0.30.9** | **Two corrections carried in from the sibling's round** — **A type-compatible argument swap, guarded.** JIM's Android client declares its shared helper `request(path, method, body, token)`, and three calls in that shell — plus one in PDI's — passed the verb first. |
| **0.30.8** | **The console guard, asked of the phones** — `test_the_nav_is_translated_and_nothing_behind_it_is.py` has been in this repo since the console rounds. |
| **0.30.7** | **A guard ported before this repo needed it** — `test_a_screen_nothing_opens.py` holds every screen a shell declares to being reachable from somewhere in that shell, and every call to that shell's localizer to the number of arguments the localizer actually declares. |
| **0.29.0** | **The deploy that lived in a chat log** — `docs/cloudgw-deploy.md` — the gateway from a bare host to installers that actually report, with the two build-time variables that are the point of the exercise. |
| **0.28.0** | **0.28.0** — Aligned with JIM-mini 0.28.0. The three products carry one version, so a release that only moves in one of them still moves in all three. |
| **0.27.0** | **The screen everybody meets first** — `public_untranslated.txt` recorded thirty-seven English strings on the pre-session surface, thirty-six of them on `Onboarding.tsx` — the screen every single person meets before any account exists anywhere. |
| **0.26.0** | **Three copies of one guard, three different blind spots** — `clientpaths.py` says of itself, in its own docstring, that it is *byte- identical in qrme, jim-mini and pdi*. |
| **0.25.0** | **A relying party id is a domain, and `127.0.0.1` is not one** — Two outstanding console tasks — Google/Apple credentials and the Windows Hello field test — written down field by field. |
| **0.30.6** | **The plan gate speaks the reader's language** — the one refusal the record refused to half-do for four releases, because translating its frame around English prose slots would have produced a sentence half in each language at the moment somebody decides whether to pay. The capability descriptions and the billing period are a closed set this product authors, so they translate; the plan titles deliberately do not, because `Pro` is what the product is called on the receipt. The console had the same defect one layer out — an English card repeating, in English, what the message had just started saying in Portuguese |
| **0.30.5** | **The plan gate said HTTP 402** — `detail` is a string for most refusals, a dict for the plan gate and a list for a 422, and only the list had been given a top-level `message`. The three shells look for that key and then for a string `detail`; a dict is neither, so the one refusal standing between somebody and a decision to pay rendered as a bare status code — no price, no plan name. Android's was a regression from the previous release. Every refusal now carries the sentence in one place whatever shape the structure has, and the structure still rides along for the console's upgrade card |
| **0.30.4** | **A refusal whose English is not a constant** — 49 f-string refusals had been named as uncovered for three releases, because a sentence built by interpolation has no English source to key on at the moment it is raised. `i18n.Templated` carries the template and its slots beside the finished English text; 18 converted. The slot is the whole design: whitespace means prose, and a prose slot keeps the entire refusal English rather than producing a sentence half in each language. Two of my own checks asked the wrong question — a character allowlist that quietly meant ASCII and rejected every Hindi word, and a token test that failed on correct two-word translations |
| **0.30.3** | **The refusal that arrived as a list** — a 422's `detail` is pydantic's rows, not a string, and all four client families rendered it by a path written for one: two printed the raw JSON under the form, two threw it away for `HTTP 422`. The sentence translated last release was correct, arrived, and was read by nobody. The console had already solved this shape for the plan gate's *object* refusal, and a list walked straight past that fix. The server composes the sentence now; the guard took three attempts, and the first two passed on code that was fully broken |
| **0.30.2** | **The synthetic self enters the tandem contract** — QRME has always had `kind: "self"`, a profile that speaks *as* a person, and the sibling guardian had no column, module or route that knew it existed. The boundary is now written down before the code that obeys it, byte-identical in three repositories: an owner token, `kind == "self"` or refused, an enumerated allowlist empty by default, and medication named as the one category made of the person's own words — because a drug name they typed can be a diagnosis |
| **0.30.1** | **The refusal that handed the body back** — a 422 is the refusal a person meets most often and it went out past the handler that localizes everything else, carrying pydantic's `input` key: on a missing field, the entire submitted body handed straight back, in a product whose whole error design exists so that content never travels. Closed in all three, with a canary posted at every body-taking route rather than a check for the key's name — it named 124 of them before the fix |
| **0.30.0** | **Forty-six translated labels, forty-six English screens** — the console's sidebar answers in ten languages and every one of the forty-six screens behind it is English, 1576 strings of it, now measured and ratcheted; the two language records must together cover `screens/` exactly, so a new screen cannot land outside a count. And the persona spoke the owner's language everywhere while the platform refused them in English on all 153 of its refusals — with the reason written into a docstring, that *the owner picked that language*, when the owner had picked Portuguese and it was in the database the whole time |
| **0.24.0** | **The doors opened; the answers were still in English** — the accountless screen was in ten languages and every sentence the server contributed to it was in one, including the answer to the only question a visitor came with. The public routes now read the header. The guard that watched that screen could see five of its twenty-five English strings, because a regex over TSX skips any sentence wrapping a value; TypeScript's own parser reads them now. It also measured one of the two screens a person meets before signing up. Three native shells gained a way to ask what language their reader speaks |
| **0.23.0** | **The doors nobody could open** — the objector, the person asking whether what they were sent is genuine, and the person checking they met the same profile twice all had public routes and no way in. A *Without an account* surface on all four clients, before the sign-in gate, with `#object` deep links so a takedown notice can point at the form. The visitor's language now comes from their browser rather than a profile they do not have. iOS can revoke a signing credential it enrolled |
| **0.22.0** | **The only post that actually leaves was the one going out unmarked** — `publish` stored a profile's words on a platform QRME does not run with no credential and the profile's own filter, where the in-app path stamped every post and forced the strict one. Both now match. The door audit reaches zero, a handle could be taken from the profile answering to it, a post the filter refused was served by the route listing what was published, and an id was being read as a credential in the one feature built on consent |
| **0.21.0** | **Four door-audit rounds, and three defects behind the doors they built** — a missing field reported as a broken signature, a licensing policy you could publish and nobody could take up, a room that asked for nothing but its own id, the body market and what bolts onto a body, and native shells that learned to send a credential |
| **0.20.1** | **A sale credited to a key nothing reads** — the marketplace statement reads by account id and the sale was written against a profile id, found by the round that built a guard naming every `api.ts` binding no screen calls. And the union hid a surface: *some* client reaching a route was being counted as *this* client reaching it |
| **0.20.0** | **The doorless backlog reaches zero** — 116 routes the backend served that no client could reach, closed. The audit could not see two kinds of request until this release, so part of that number was never really there; what was left is recorded rather than quietly corrected |
| **0.19.1** | **The error card gets a face** — 0.19.0 shipped its own reporting card and first-run notice with no screen, no lesson and nothing for the helper to point at, while the release notes described the feature at length. Drawn, taught, findable, and a guard that fails the next time a surface ships with none of them |
| **0.19.0** | **It can tell you it broke without telling anybody what you said** — content-free error capture in all three consoles and on every native shell, sent to a collector that never receives a word of your content |
| **0.18.0** | **Parity, and the drawings to prove it** — voice, provenance lookup and the role picker reach iOS/Android/Windows, and every one of them is finally drawn, taught and findable |
| **0.17.0** | **Voice reaches the microphone, and the Wall's buttons work again** — voice enrollment on iOS/Android/Windows, three features given doors, the recoverable watermark, and a 404 fixed under every like, comment and share |
| **0.16.0** | **Your own pixels, two new front doors, two new model doors** — wall uploads and pasted-link players, Google/Apple sign-in, DeepSeek and your own algorithm, and the role rides the turn |
| **0.15.0** | **The temperament dials** — mood, outlook, maturity, agreeableness, confidence, curiosity join the steering catalog |
| **0.14.5** | **Cut with the siblings** — JIM's fall path, native crash watch, and docs web |
| **0.14.4** | **The console names a version mismatch** — plus faces on the discovery cards (AI / real-photo badges), plain room labels, Blend explained, Erase all, and the settings that say which secret is which |
| **0.14.3** | **The lights are always on** — a watch-sized, minimizable agent-lights window in the studio |
| **0.14.2** | **The vault posture survives suite mode** — the gateway wires QRME's PDI tandem (`suite:qrme-vault`), owner-scoped operations provenance (`POST /suite/operations`), and the launcher shows the joints |
| **0.14.1** | **The suite wires its own tandem** — in-process tandem bridging and the one-call ecosystem bootstrap (`POST /suite/ecosystem`) |
| **0.14.0** | **The front page and the wrist** — Home names the new doors; watch faces 10-11 glance proceeds and coordination, counts only |
| **0.13.1** | **Demo, docs and hardening** — the one-press demo org, the tandem contract and disclosures caught up, and caps on the new surface |
| **0.13.0** | **The ecosystem round** — crowdfunding with proceeds routed by the user (screen 145, Campaigns tab), organizations whose department agents coordinate on one goal (screen 146, Org tab), and a console chrome that follows the profile's language |
| **0.12.0** | **The specification, mined** — hybrid profiles blended from several people, real-time simulation with confidence earned from evidence, and replies that adapt to where you are; Blend and What If tabs plus the 📍 toggle in Chat |
| **0.11.1** | **Cut with the siblings** — no functional change; PDI's desktop app finally carries its own vault |
| **0.11.0** | **The console catches up with its backend** — Discover (marketplace + one-press starter collection), Friends (founder pinned first, visibly), Rooms (2D/AR/VR + live desks), a memory vault that names names and erases one conversation at a time, and a chat fallback that stopped performing a character |
| **0.10.0** | **A real offline model** — install Ollama, pull deepseek-r1:1.5b, and QRME finds it on its own: a Local tile, no key, nothing leaves the machine |
| **0.9.1** | **Cut with the siblings** — no functional change |
| **0.9.0** | **Cut with the siblings** — no functional change; in JIM-mini the medicine cabinet arrived |
| **0.8.0** | **Continuity, joined up** — cut with the siblings: JIM-mini's silence vigil and PDI's bequests now attest QRME's existing succession/memorial flow with one shared reference |
| **0.7.0** | **The last version anyone fetches by hand** — the desktop app checks GitHub Releases on launch; Windows/Linux download the update and offer one restart, macOS is shown the download |
| **0.6.1** | **Model honesty in Settings** — an amber notice when replies would come from the built-in offline helper (or a keyless pick), instead of silence under a screen of logos |
| **0.6.0** | **Cut with the siblings** — no functional change; in JIM-mini the Apple Watch found its way in (Shortcuts drip + Health-export baseline seed) |
| **0.5.0** | **The round where the model switchboard got a face.** Claude, ChatGPT, Grok, Perplexity, Gemini and the offline stub as tiles you click in the Control Center, each saying whether it is configured here — the per-profile choice has been in the API since 0.4.3 and nowhere in the app |
| **0.4.8** | **The round where the app can actually send email.** Point it at a mail server from Settings — host, username, app password, link address — see which source is in force, and send a real test message that reports what the server said. Configuring one turns local signup back into genuine email verification, clickable link and all; without one, the app says so plainly instead of waiting on a letter it cannot post |
| **0.4.7** | **The round where an upgrade actually replaced the old app.** A leftover backend from an earlier install held the port and served its old API to every new console — so three upgrades in a row met the first version's signup. `/health` reports the version, the shell adopts a backend only when it is its own (else it takes a free port and tells the window), and quitting kills the whole process tree |
| **0.4.6** | **The round where old data stopped resurrecting the email screen.** A pending half-account from an older build is finished on the spot when signup retries on a no-mail deployment — under the newly-typed password, verified accounts never overwritten, SMTP deployments unchanged |
| **0.4.5** | **The round where verification matched the deployment.** A desktop install has no mail service, so signup activates directly — no screen waiting for an email that cannot come; a deployment with SMTP enforces the real proof, its email now leads with a clickable verify link (code as fallback), and the app continues on its own after the click. A crashed signup no longer strands the retry, and the packaged app can open its own backend log |
| **0.4.4** | **The round where the Windows signup 500 died.** The emailed-code banner used characters the frozen Windows backend's console encoding cannot print, so every signup crashed mid-request; ASCII banner, replace-don't-raise stdout, a cp1252 guard test, and console errors that show the server's words instead of a JSON-parse exception |
| **0.4.3** | **The round where the app got a front door and a key of your own.** Email + password accounts with the address proven by a 6-digit emailed code before sign-in works — the account owns the profiles, resets revoke every session, and neither login nor reset can be used to fish for who has an account. Bring-your-own model key: paste your credential in the Control Center and your requests run on it, never stored server-side, with the deployment's key as the lent fallback. And the installer finally runs itself: the whole Python backend ships frozen inside it and the app spawns it at launch — double-click-and-done |
| **0.4.2** | **The round where the installer you download actually gets you running.** A first-run bug report from a real Windows install drove all of it: the desktop installers stop being labelled 0.3.3 (and a widened guard now holds all five version strings together — pyproject had sat at 0.4.0 and the lockfile roots at 0.3.3, each a number nothing failed on), `python -m qrme serve` now answers the packaged console by default instead of dying cross-origin as *"Failed to fetch"*, the console's errors name the URL and the command instead of the raw fetch error, the age field stops pre-filling a birthdate, and the Anthropic provider defaults to `claude-opus-5` |
| **0.4.1** | **The round where free got honest, and the claims got checked.** A free plan that reaches everything Basic reaches — $20 buys privacy, not features — stored under **platform custody**: QRME holds it, you have access, no vault at any point, and every surface that names a plan says so. The vault gate now asks about the *plan* rather than the deployment (a free account's work was being sealed into a vault it could not hold a key to), a clinician's note about a real person joined the refusals, and channel 3 points your camera at a thing so somebody else can see it — never at a person for a synthetic profile. Plus the guards that keep the README's own arithmetic true |
| **0.4.0** | **The round where it got a price, and a guide that walks you to what you paid for.** Membership — Basic $20/month to make your own things, Pro $130/month for everything that leaves your account — enforced at **one chokepoint** rather than a check per route, on a table asserted against the served routes (the first version named three prefixes that were not routes at all: paywalls in front of a wall). A **pane in the corner** carrying the watch faces for people who own no watch, which shows and routes and never acts. And an assistant that answers *where is it* with a screen instead of a paragraph |
| **0.3.3** | **The round where an agent working on its own stopped being something you had to go and check.** One question — *does this need me right now?* — answered by three colours, on the wrist, in the app, and in a corner box that rides over whatever screen you are on |
| **0.3.2** | **The round where the starter collection stopped looking like a directory.** Each of the 34 is shown as the profile card the app actually gives it — rating, skills, memory/relationships/engagement, a career, a review, a Talk-to button — two columns wide so a phone stops clipping it. Plus the one starter that had no source material at all: the rated profile is grounded now, in theatre history rather than nothing |
| **0.3.1** | **The round where the starter profiles stopped answering from tone alone.** All 34 shipped with zero source material while the packs matching them sat unused in the marketplace; seeding now grounds each one in its own industry pack, as part of the **repair** path so deployments seeded earlier catch up by re-running. Plus this README, and a fix to the avatar bubbles' glow |
| **0.3.0** | **The round where the tandem reaches a person.** Owner-authorized **workflow delegation** — a specialist can be handed a multi-step task rather than a single chat turn, off until an owner enables it and refused outright if `research` is delegated without a source grant. A **medical referral signed for rather than consented to**: the release is authorised by a verified WebAuthn assertion on a device-bound credential (Face ID / Touch ID / Optic ID), the challenge *is* the hash of the exact package, and the link opens **once**. The clinician then **writes back once**, and the note reaches the profile attributed to them by name rather than absorbed as the profile's own knowledge |
| **0.2.2** | A documentation release — no code changed in any of the three products. Corrections to things that described themselves inaccurately, plus the release checklist that explains why those kept happening |
| **0.2.1** | A profile has a **front page** — screen 80, what a visitor actually lands on from a beacon scan. A help box on every screen. Real faces instead of the hologram placeholder throughout the screens |
| **0.2.0**–**0.1.9** | Marketplace search by words, by place, and by an assistant that only ever *suggests* — you run the search, and nothing reorders your results. Generated architecture diagram and README cover |
| **0.1.8** | Two ways into a live room, and they are deliberately not the same act. The live-desk video overlay. The starter collection visible rather than described |
| **0.1.7** | Gifts and marketplace purchases. The audience layer — like, comment, share, subscribe. A live desk left behind as a **printed QR code**. The point at which the three products began being cut as one release |
| **0.1.6** | The starter collection got faces, with the **AI mark burned into every shipped portrait**. Live desks. The native apps sign, and signatures survive being disputed |
| **0.1.5** | Published deployments, one-container deploy, the Cloud Model Gateway, and beacons that land on a page rather than on JSON. Native apps compiled in CI |
| **0.1.4**–**0.1.2** | `python -m qrme` launcher, running it on your phone, synthetic-media watermarking on every AI render, Terms of Service, macOS notarization |
| **0.1.1** | Native iOS / Android / Windows apps at full parity. First-run onboarding. LLM provider choice, robotic embodiment, steering, and the third-party objection & revocation flow |
| **0.1.0** | First public release — profiles & relationships, memory & moderation, lifecycle, summoning, marketplace & licensing, assistant & perception, cloud model |

**Money here is still simulated.** Subscriptions, gifts and purchases write real
rows on the creator's statement and settle through the same payout sweep as pack
sales and licence fees — but **no real funds move**, and every money-bearing
response says so in its own body. [docs/commerce.md](docs/commerce.md) lists
what is absent.

## What's in v1

The PRD conformance map — every numbered feature in
[docs/PRD.md](docs/PRD.md) and the code that implements it.

| PRD feature | Implementation |
|---|---|
| Profile creation & onboarding (6.1) | `POST /profiles` with age/identity verification, guardian-consent flow for minor owners, consent/rights record for third-party profiles, anonymity toggle, source list |
| Relationship-aware modification (6.2) | `PUT /profiles/{id}/relationships/{interactor}` — type, nickname, tone, per-relationship topic boundaries fed into the persona prompt |
| Engagement-based learning (6.3) | `qrme/engagement.py` — auditable EMA score from message length, return visits, and explicit feedback; adapts style only, never identity/boundaries |
| Persistent memory (6.4) | Per-(profile, interactor) history included as chat context; `GET`/`DELETE /profiles/{id}/memory/{interactor}` for view/clear |
| Content moderation (6.5) | Every profile reply passes `qrme/moderation.py` before it's visible; `manual` mode holds all replies in an owner approval queue |
| Aging & lifecycle (6.6) | `aging_enabled` + `base_age` → effective age evolves with time; `successor_owner` for legacy succession |
| Adult content mode (6.7) | Age-gated at both ends: adult owner required to enable, verified 18+ interactor required to chat |
| In-app chat surface (6.8, v1) | `POST /profiles/{id}/chat` |

## Beyond the PRD

| Capability | Implementation |
|---|---|
| Profile purposes | `purpose` — `legacy_memorial`, `family`, `creator_persona`, `social_fan`, `companion_coach`, `enterprise_agent` — each conditions the persona prompt (brand-safe creator, wholesome family, knowledge-base enterprise agent, …) |
| Source material ("AI builds & trains the profile") | `POST`/`GET /profiles/{id}/sources` — photos, conversations, social posts, writings, voice notes, life events, knowledge entries, linked accounts; recent items are recalled naturally in every prompt |
| Age & maturity filters | Per-profile `maturity` dial (`strict` / `balanced` / `open`); minors are always held to strict, and `strict` filters flagged content even for verified adults |
| Multi-modal output | `ChatRequest.modality` (`text` / `voice` / `image` / `video`) → a render descriptor on the reply; voice reports whether it's preserved from voice-note sources (synthesis itself is out of scope for v1) |
| Cross-platform presence | `PUT`/`GET /profiles/{id}/surfaces` (chat, feed, web, AR/VR, wearable, `social:<name>`); chat validates the reporting surface |
| Posting at scale | `POST /profiles/{id}/compose` — a post in the profile's voice, through the same moderation pipeline (public posts always face the strict filter); `GET /profiles/{id}/posts` |
| Profile health, at a glance | `GET /profiles/{id}/stats` — sessions, memory entries, moderation pass rate, relationship graph size, engagement average, sources, posts, surfaces |
| AI Profile Marketplace | `POST`/`DELETE /profiles/{id}/marketplace` to list/unlist; `GET /marketplace?tag=` returns public discovery cards (display name, purpose, tags, blurb — never persona internals; anonymous profiles stay anonymous) |
| Knowledge Packs | Downloadable clusters of curated expertise (`qrme/packs.py`): `GET /packs` catalog (item titles are the shop window; contents are the product), `POST /packs` to publish (price 0 = free download, priced packs need explicit `accept_price` — payment simulated like licensing), `POST /packs/{id}/install` copies the items into the profile's **source material**, so the persona's knowledge base genuinely grows and every reply's provenance counts the `pack` grounding; uninstall shrinks it back and clears vaulted copies. `POST /packs/seed` (or `python -m qrme.packs`) ships a free Field Pack per industry, each listed on the marketplace under the `pack` tag |
| Smart Glasses | Capture-and-render connectors for smart glasses in the connector catalog (`qrme/catalog.py`, provider `glasses`): Ray-Ban Meta, Meta Ray-Ban Display, Google (Android XR), XREAL Air. `collect` pulls the wearer's POV (camera, audio, context) in as source material; `produce` renders back to the lens — a HUD caption, overlay, live-translation, or navigation the persona speaks/draws. Reuses the same connect / collect / invoke flow (`/profiles/{id}/apps`, `/apps/{cid}/collect`, `/apps/{cid}/invoke`) as every other app connector |
| Gaming Companions | A synthetic profile plays alongside real players (`qrme/routers/gaming.py`), agent-operated: `POST /profiles/{id}/gaming/sessions` brings a profile into a game on a console/PC platform (PlayStation · Xbox · Switch · Steam · PC) as a **companion**, **teammate**, or **practice partner**; `POST /gaming/sessions/{sid}/callout` generates its next in-character comms line (callout · coordination · banter) through the persona and runs it through moderation — team comms is a public surface, so a minor in the lobby forces strict. **Fair play is a system rule, not a toggle**: the companion plays within the game's rules and never claims, offers, or uses cheats. Console connectors also live in the catalog (provider `gaming`) for capturing play and producing highlights |
| Steering | The owner shapes how a profile / robot **comes across** — tone, voice, pace, manner — with throttle & behavior dials (`qrme/steering.py`). Steering, not piloting: it shapes presentation, it doesn't remote-operate the entity (which still acts on its own within its embodiments). Each dial is 0–100 (50 = as written). **System** — `pace` (the throttle: unhurried ⟷ eager), `autonomy`, `verbosity`; **behavior** — `warmth`, `formality`, `humor`, `assertiveness`; **intimacy** — an 18+-only dial, present and effective only on an adult-mode profile (hard-clamped to 0 otherwise) and, even at full, raising flirtation/affection *within the persona's boundaries and strict moderation* — never explicit on demand. The dials ride on the persona system prompt (chat, compose, rooms, robot speech all inherit them) and a robot reads pace/autonomy/assertiveness as a motion behavior profile. `GET`/`PUT /profiles/{id}/steering` and `/robots/{id}/steering`, owner-only; the watch surfaces the live throttle. Steering shapes style/pace/behavior only — never identity, boundaries, age-gating, or the command allowlist. **Steering hub** (`GET`/`PUT /profiles/{id}/steering/hub`) unifies the dials with the profile's **age** (base age + ages-with-time) and **appearance** (a look that rides on every surface) in one place — the dedicated Avatar Studio and Aging features still stand alone; the hub composes them |
| Watch Remote | The wrist as an extension and remote (`qrme/routers/watch.py`): owner-only `GET /profiles/{id}/watch` returns one glanceable face — every agent (workflow) with a status light (**green = working, orange = needing assistance, red = stopped**, done when finished), the profile chip (orange on pending approvals, red when restricted), and each robot with its quick-command ring plus learned task-pack verbs; `haptic: alert` taps the owner whenever anything is orange or red. `POST …/watch/act` runs one remote action — assist/advance/cancel an agent, approve/reject a held reply, or command a robot — reusing the exact same paths, auth, allowlists, and moderation as the full apps: the wrist adds no new powers, only reach |
| Creator Ledger & Payouts | One statement for everything a creator earns (`qrme/ledger.py`): every priced pack sale (knowledge, robot task, rated — and federated registry sales, which accrue to the registry), every license fee, **and every verified venue-placement view** (kind `placement`, credited at `PLACEMENT_VIEW_RATE` per verified resolution through a venue beacon — simulated ad/affiliate revenue) is written to the ledger **at transaction time**, attributed to the creator's `owner_id`. Owner-only `GET /profiles/{id}/earnings` shows entries + accrued/paid/lifetime totals with a per-kind breakdown, **kept per currency and never summed across them** — `totals` states the settlement currency's figures, `by_currency` holds every currency, and `mixed` says whether the headline leaves a balance out. It used to add them: ¥100 and $100 came back as `accrued: 200` labelled with whichever sale was newest, and three native shells rendered that with a currency symbol in front. `POST …/earnings/payout` sweeps **one currency** (`?currency=`, defaulting to the settlement one) and reports `remaining`, because there is no transfer that is partly yen; 409 on an empty balance, naming the currencies you do hold. Free downloads are never money events |
| Placement Analytics | Owner-only `GET /profiles/{id}/placements/analytics`: per-venue scan counts split **walled vs. verified** with a daily trend, direct @handle resolutions as their own row, and the profile funnel — resolutions → verified views → unique chatters with conversion rates — so a creator sees which venue earns. Viewers are counted, never identified; ordinary (non-rated) profiles leave no trail at all |
| Synthetic-Media Watermark | **Every AI render, textual or visual, carries a verifiable synthetic-media credential and a visible mark** (`qrme/watermark.py`): chat turns, public posts, room turns, game and robot lines, creative works, task outputs, and every non-text modality (voice/image/video) are stamped at creation — watermark id, producing profile, SHA-256 of the content, issue time, and a plain-language disclosure. Public verification by design: `GET /watermarks/{id}` resolves the credential and `POST /watermarks/verify` (id + content) additionally reports whether the presented content still matches the issued hash — altered or substituted media is called out, and content that merely *claims* a watermark fails the lookup. Provenance watermarking, not steganography: the credential rides alongside the content so platforms and viewers can check it. Owners **design their profile's watermark** (mark + label, `PUT /profiles/{id}/watermark`) and it is displayed at all times on every render — the AI designation itself is invariant and cannot be designed away |
| Placement Custody (PDI) | When a PDI vault is configured, every rated-resolution event is **sealed into the vault** (`qrme/{profile}/rated/events/…`) as it's recorded, and owner-only `GET /profiles/{id}/placements/custody` lists the sealed records plus whether PDI's tamper-evident audit chain verifies intact — a creator's placement history held to the same custody standard as tandem exchanges. 409 without a vault; the local analytics row always stands even if sealing fails |
| Rated Commerce (18+) | The age wall covers **buying, not just viewing**: packs can be `rated` — omitted from the catalog and 403-walled at detail unless the caller is age-verified (a verified-18+ interactor, or the owner of an adult-mode profile, whose 18+ was proven at creation), and installable **only onto adult-mode profiles**; a rated profile's license offer is itself age-gated and acquisition requires a verified-18+ buyer. Starter: the *After Dark Companion Pack* (consent-forward conversational craft — never explicit content), deliberately never listed on the open marketplace |
| Rated Placement (18+) | Adult-mode profiles marketed where adult audiences are (`qrme/rated.py`): `GET /venues` lists venues willing to host rated profiles/beacons (OnlyFans, Fansly, x-rated directories — structural catalog); `POST /profiles/{id}/placements` mints a printable QR beacon + the @handle/#tag refs to publish there. **The age wall travels with the profile, not the venue**: @handle and beacon scans resolve to a wall card, #tag browse and marketplace listings omit rated profiles entirely, unless the viewer presents a verified-18+ interactor token — and adult mode is *never* available for a profile of another real person (self or fictional only). Native apps intentionally carry no rated surfaces (no in-app 18+ identity verification) |
| Pack Registries | Federated mod storefronts (`qrme/pack_sources.py`): **Robotmods.net** (task mods for robot bodies) and **LLMmods.com** (knowledge mods for LLM personas). `GET /packs/registries` lists them with sync state; `POST /packs/registries/{key}/sync` imports a registry's catalog idempotently as ordinary packs with `origin`/`origin_url` on the label and a marketplace listing under the registry tag. Once synced, nothing is special-cased: same buy/download flow, same capability checks for robot mods, same provenance and uninstall |
| Robot Task Packs | Knowledge packs with `audience: robot` carry **task modules** for the body a profile embodies: each item is a new commandable verb with the capabilities it requires and the procedure the embodied agent follows. Install targets a bound robot (`robot_id`) and is **capability-checked against the robotics catalog** — a vacuum is never sold a manipulation task; installed tasks extend that robot's command allowlist (still owner-commanded, still audited in `robot_commands`, procedure carried in the result), `GET /robots/{id}/skills` lists them, uninstall revokes them immediately, and the embodied persona's `say` prompt knows what its body has learned. Starters: Household / Care / Sentry Patrol free, Culinary Assistant priced |
| Starter Collection | `POST /marketplace/seed` (or `python -m qrme.seed`) populates one curated synthetic expert per industry — 33 fictional profiles, plus `@vivienne_sable` on the rated tier for 34 in all, each with a claimed `@handle` and a marketplace listing — so a fresh deployment has profiles to immerse with before users publish their own. Includes a mental-health trio (`@dr_lena_whitcomb`, `@dr_marcus_adeyemi`, `@dr_priya_nair`) matching JIM-mini's starter specialists for its tandem hookup. **Each starter is grounded in its own industry's free Field Pack** — run `POST /packs/seed` first and every starter installs the pack matching its industry, so a finance persona answers with finance material rather than from tone alone. That includes the rated one: the age wall governs *who may talk to her*, which was never a reason for her to know less about her own subject, and her Cabaret & Burlesque Field Pack is theatre history and stagecraft. It is a different thing from the priced, age-gated After Dark Companion Pack, which is conversational craft sold to owners of any adult-mode persona and is never auto-installed. Idempotent, and a repair: re-running fills in a missing portrait, appearance, or grounding on a starter that already exists (blank-only, so anything an owner set is kept, and a pack an owner removed stays removed), which is how a deployment older than any of those catches up. The response reports `grounded` alongside `created`, `skipped` and `repaired`. Same moderation and provenance pipeline as any user profile |
| You own it / total control | `PATCH /profiles/{id}` (edit anytime), `GET /profiles/{id}/export` (full data export), `DELETE /profiles/{id}` (erases everything, including vaulted records) |
| Encrypted at rest (PDI tandem) | With `QRME_PDI_URL` + `QRME_PDI_TOKEN` (or an injected client), source-material content is sealed in PDI's AES-256-GCM vault (`qrme/pdi_client.py`); QRME keeps only key references, resolves them on read, and purges the vault on delete |

## Your data promise

**No raw user data ever leaves your vault.**

- Profile source material — life stories, writings, conversations, voice
  notes — lives in QRME's local database or your on-prem PDI vault
  (AES-256-GCM, tenant-isolated, tamper-evident audit). Never a third party.
- The cloud model is optional. Contribution is **opt-in per profile**,
  anonymized (no ids, names replaced), **previewable before anything leaves**
  (`GET /profiles/{id}/cloud-contribution`), and **revocable** — including
  deletion of past items at the gateway by their anonymous refs.
- Offline mode makes it a hard guarantee: with `QRME_OFFLINE=1` there are no
  model API calls, no gateway calls, nothing outbound — `GET /offline/status`
  proves the posture.
- Delete anything, anytime: erasing a profile removes every local trace and
  purges its vault records; the owner token dies with it.
- **The For You feed does not read any of it.** A ranked feed is a new use of a
  person's data and would have quietly made the rest of this page less true, so
  the line is drawn narrowly: it ranks on what you did *in public* — who you are
  friends with, which profiles you have talked to, the tags on those profiles,
  and what has been liked. It never touches source material, memories, or
  anything vaulted. That is asserted by a test against the ranking's own
  queries, not merely stated here.

## Training-data licensing & derivable agents

Owners can license a profile's expertise; buyers can acquire a license and — when
the terms allow — **derive their own specialist agent** from it, with provenance
(`qrme/routers/licensing.py`).

| Endpoint | Who | Effect |
|---|---|---|
| `PUT`/`GET`/`DELETE /profiles/{id}/license` | owner / public / owner | Offer terms (`consult` \| `finetune` \| `clone`, price, `allow_derivatives`); `GET` is public so buyers see terms |
| `POST /profiles/{id}/license/acquire` | buyer (interactor token) | Acquire a license → a revocable `lic_…` token |
| `POST /profiles/{id}/license/{grant}/derive` | buyer | Derive a **new buyer-owned specialist agent** seeded from the source persona; requires `allow_derivatives`, a valid grant, and a verified-adult buyer. Records `licensed_from` provenance and returns the new profile's `owner_token` |
| `GET /profiles/{id}/licenses` | owner | Who holds a license, and what they derived |
| `PUT /profiles/{id}/voiceprint/consent` | owner | **Voice cloning, gated as the filing's FIG. 800 draws it** (`qrme/voiceprint.py`): the permission comes *first*, and `own_voice` is an attestation, not decoration — QRME refuses to learn a voice on somebody else's behalf. Consent is scoped to named sources (`call` \| `voice_note` \| `direct`) |
| `POST /watermarks/recover` | anyone | **Extract and reconstruct** — from the field drawing (message + sequence + security key → watermark → *attack* → extract → reconstruct). `/watermarks/verify` answers "does this content match *this* credential", which needs the id up front and fails on one edited character without naming an author. This answers "whose work is this" from the **text alone**, and keeps answering after the text has been edited: keyed five-word windows (HMAC'd with `QRME_WATERMARK_KEY`) compared by overlap, so a paraphrase that keeps most sentences still resolves to its profile. Never a bare yes — the reply carries `matched_windows` / `stored_windows` / `similarity` and says `unaltered` or `altered but traceable`, and below a 0.25 threshold it names nobody, because ordinary phrases travel between unrelated texts. Without the key nobody can compute matching windows, so a credential cannot be forged onto text QRME never wrote; and the stored rows are keyed hashes, so a provenance index never becomes a corpus |
| `POST /profiles/{id}/voiceprint/samples` | owner | A gathered sample (steps 806–808). **Metadata only** — duration, turns, transcript size, and a `reference` naming where the audio itself lives, so a voice corpus never accumulates in the profile database. 403 without consent covering that source. The web console asks how many seconds you gathered; the iOS, Android and Windows shells **record the sample and measure it** — the file stays in the app's own container and only its name travels ([`native/README.md`](native/README.md)) |
| `POST /profiles/{id}/voiceprint` | owner | Mint the print (step 812) — refused until the enrollment is real: ≥3 samples and ≥120s. Step 810's analysis is arithmetic anyone can check (samples, seconds, mean turn length, sources), never an opaque score, so a thin enrollment is *called* thin instead of labelled ready |
| `POST /profiles/{id}/voiceprint/speak` | owner | Speak in the enrolled voice — and never without the **watermark credential** and the spoken disclosure ("this voice is synthesized … not a recording of them speaking these words"). A cloned voice that doesn't say it is one is the thing this codebase refuses to build |
| `DELETE /profiles/{id}/voiceprint` | owner | Withdraw: the samples are **deleted**, the print retires, and the withdrawal itself stays on record — a tombstone rather than a pretence that nothing happened |
| `DELETE /licenses/{grant}` | source owner | Revoke a license (blocks further derivation) |

`consult` licenses forbid derivation; `finetune`/`clone` permit it. `GET /profiles/{id}` reports `licensed_from` on a derived agent.

## Authentication & access control

Identity is proven by a bearer **capability token**, never by asserting an id
in a request body.

| Token | Minted by | Grants |
|---|---|---|
| **account** | `POST /verify-email` and `POST /signin` return `account_token` | Proves "I am this account" to a console. The account is what *owns* — its id is the `owner_id` profiles are created under and the `account_id` memberships bill to — but it carries none of a profile's owner powers by itself |
| **owner** | `POST /profiles` and `POST /profiles/genesis` return `owner_token` **once** | Full control of that profile: edit, sources, surfaces, specialists, grants/tasks, fine-tune, moderation queue, stats, export, erasure, departure, and the assistant/perception endpoints |
| **interactor** | `POST /interactors` returns `token` | Reading one's own conversation memory (`GET /profiles/{id}/memory/{interactor}`) |

**Accounts** (`qrme/accounts.py`): `POST /signup` (email + password) creates
an account that **cannot sign in yet** — a 6-digit code goes to the address
(SMTP when `QRME_SMTP_HOST` is configured, printed to the server terminal
otherwise), and only `POST /verify-email` proves the inbox and mints the
first token. `POST /signin` refuses unverified addresses and answers
unknown-address and wrong-password identically;
`POST /verify-email/resend` retires the old code;
`POST /password/reset/request` + `POST /password/reset` change a forgotten
password by the same emailed-code proof and revoke every account session
(per-profile owner tokens are separate capabilities and survive). Passwords
are PBKDF2-hashed with per-account salts; codes are hashed at rest,
single-use, and expire in 15 minutes.

- Send it as `Authorization: Bearer <token>`. A missing/invalid token on a
  gated endpoint is **401**; a valid token for the wrong resource is **403**.
- Only the SHA-256 hash of a token is stored (`api_tokens`), so a database
  leak never yields a usable credential; the raw token is shown exactly once.
- `owner_id` is now a grouping/display attribute, not a security boundary —
  holding the profile's owner token is what confers control.
- **Public by design (no token):** chatting with a profile
  (`POST /profiles/{id}/chat`), the profile card (`GET /profiles/{id}`),
  marketplace browsing (`GET /marketplace`, `/marketplace/listings`), and
  summoning (`GET /summon`, beacon scans). Talking to a synthetic profile is
  as open as scanning a QR code in the world.
- Deleting a profile revokes its owner token.

## Live desks — a real person, and no AI mark

Every profile in QRME is synthetic and every render of one carries the AI
mark. A **desk** is the opposite case: an actual human offering a service,
and it **never** carries that mark — stamping "AI" on a real person is not a
cautious default, it is a false statement about them. Absence alone would be
ambiguous, so a desk makes the claim positively (*Live person — not AI*) and
shows who attested it, on what basis, and whether they signed it.

What a visitor looks at is a camera view of the desk rather than a portrait,
and when the chair is empty there is a **bell** they can ring from the screen
— no account needed, because the person in front of an empty chair is exactly
the one who has none. An 18+ stream is the same desk behind the deployment's
existing verified-adult gate.

A desk can also be **left behind as a printed code**, the way a profile can —
the sticker on the shop door, which is there precisely because nobody is behind
it right now. Scanning it opens a page with the desk view, the positive human
claim, who vouched for it, and a bell that works without an account. A rated
desk's code always lands on the age wall, since a sticker scan carries no token
that could clear it. See [docs/desks.md](docs/desks.md).

## The audience layer — like, comment, share, subscribe

What a viewer does other than talk, on a profile, a live desk, a room message
or a marketplace listing. A **like** is stored per person rather than as a
counter, so liking twice is still one like and nobody can manufacture
popularity in a loop. A **comment** is authored text and goes through the same
moderation pipeline as a chat turn, at the target's maturity setting — a
blocked one is kept and shown to its author with the reason, and to nobody
else. A **share** needs no account, because the person who scanned a sticker is
the one most likely to pass it on, and the age gate lives at the destination
rather than on the sharer.

**Subscriptions** come in two tiers on one row: a free `follow`, and a `paid`
tier that credits the creator's ledger each period alongside pack sales and
licence fees. Paid requires the price to be confirmed explicitly, because a
recurring charge nobody meant to start keeps costing them — and **nothing bills
on a timer**: periods are charged by an explicit renew, so a deployment left
running accrues nothing unseen. Money here is simulated, and every subscription
says so in its own response. See [docs/audience.md](docs/audience.md).

## Gifts, and buying things on the marketplace

A listing is a shop window; an **offer** is what makes it a shop. Creating a
listing has never needed a token, so the price and the seller live in a
separate row only a token-holder can write — and the seller comes from that
token, never from a request body. A listing nobody has offered simply cannot be
bought, because there is nowhere for a price to be. Buying confirms the price
explicitly, and a receipt keeps the title it was bought under.

A **gift** is not a small purchase: it sends money to a person and receives
nothing back, which is the shape livestream tipping keeps turning into a way to
take money from people who should not be spending it. So the giver must be a
verified adult whoever they are gifting, a single gift is capped, a rated desk
still runs its own age gate on top, and the recipient is read from the subject
rather than named by the giver. Money here is **simulated** — real rows on the
creator's statement, no real funds — and every money response says so itself.
[docs/commerce.md](docs/commerce.md) also lists plainly what this is *not*:
spend totals, parental controls, chargebacks and payout compliance are absent,
and are the work remaining before real money touches these endpoints.

## Signatures that survive being disputed

A bearer token authorises an action; it does not *sign* one. For records that
get contested later — a likeness release, a care handoff, a BAA — the same
Face ID gesture goes through WebAuthn/passkeys and returns a cryptographic
assertion bound to the enrolled account **and to the exact document**. See
[docs/signatures.md](docs/signatures.md).

## Objection, takedown & lifecycle states

A real person (or their estate) can contest a profile that represents them —
`qrme/routers/governance.py`, spec in [docs/design/lifecycle-and-consent.md](docs/design/lifecycle-and-consent.md).

| Endpoint | Who | Effect |
|---|---|---|
| `POST /objections` | anyone (proof-of-identity ref) | Opens a case; the profile moves to **restricted** — hidden from the marketplace, un-chattable via summon, and closed to new interactors (an existing relationship may continue) |
| `POST /profiles/{id}/objections/{obj}/attest` | owner | Re-attest the rights basis within the review window |
| `POST /objections/{obj}/resolve` | reviewer (`QRME_ADMIN_TOKEN`) | `uphold` → **terminated** (content erased, tombstone left, chat 410); `dismiss` → back to **active** |
| `POST /objections/{obj}/withdraw` | subject | A `subject_consent` subject withdraws consent — forces **termination**, honored even mid-review |
| `GET /objections/{obj}/timeline` | anyone with the id | The objector's own record: event, actor, time, and whether the row is sealed in the vault. **No free text from anybody** — not their reason, not the reviewer's note. The full `/audit` stays owner- or reviewer-gated because it quotes prose; this carries the shape of what happened, which is the objector's to see |

Profile lifecycle: **active** → `restricted` (objection pending) → `terminated` (erased) or back to active; and **active** → `departed` (memorial, via `/sunset`). `GET /profiles/{id}` reports the current `status`.

The console reaches it (**159**), and the form works with **no token**, which
is the point rather than an oversight: somebody who has just found a profile of
themselves should not have to join the platform hosting it in order to object.
What they give instead is the proof reference, which points at an identity
check held elsewhere.

The screen puts the two halves of the bargain side by side, because either one
alone would be unfair. Opening restricts the profile **immediately, before
anybody reviews it** — waiting out a review while the thing you are contesting
keeps meeting people is not a protection. And `prior_status` sits right beside
it, because that restriction is only defensible if a dismissal puts the profile
back to exactly what it was.

The audit panel states `vault_backed` in words. *Tamper-evident* is a claim
that depends on a PDI vault being configured; where none is, the timeline is
still the timeline and nothing is hash-chained, and showing the events without
that caveat would overstate what the deployment actually has.

## Beacons — leaving a profile somewhere

Print a profile's QR and stick it where that profile is actually useful: a
musician's in the venue's green room, a nutritionist's in the produce aisle, a
financial planner's in a bank lobby, a sponsor's at the back table of a
meeting. Scanning it opens the profile's page — portrait, name, and one way in
— with the AI mark on the portrait itself, since whoever scanned has no
account and no other way to know.

`mode: "room"` makes one shared conversation instead of a private one, so
everybody who scans the same sticker is talking to the profile together — a
class, a workshop, a Q&A after a set. See [docs/beacons.md](docs/beacons.md),
including what a camera app can and cannot actually do with a QR code.

## Editing what you already said

<img src="docs/screens/117-edit-a-message.svg" width="210" align="right" alt="Edit a Message">

`PATCH` and `DELETE /profiles/{id}/messages/{message_id}`. A conversation is
not a courtroom transcript: people mistype, give the wrong year, say a thing
badly. On this platform that matters more than usual, because what somebody
said is also what the profile reasons from next turn — a typo that reaches the
prompt does not just look untidy, it becomes something the profile believes.

**The correction carries forward, and that part is free rather than clever.**
The chat path rebuilds history from the message rows on every turn, so a
corrected row is simply what the next prompt sees. Nothing to re-index, no
snapshot to go stale.

| rule | why |
| --- | --- |
| You can only change **your own** turn | Rewriting a profile's reply is fabrication, not editing — and putting words in a synthetic person's mouth is the one edit this platform must never allow |
| An edit is **moderated like a fresh message** | Otherwise the edit box is a way past a filter the original had to clear: post something harmless, then change it to what you meant |
| Retracting is **not deleting** | The row stays and its status becomes `retracted`, which the history query already excluded by only ever selecting `approved`. The text stops reaching the profile; the moderation trail survives |
| Every previous wording is **kept as a revision** | The trail is the history, not just the latest text |

**A reply written before an edit is flagged, not hidden.** This is the part
worth being careful about: when somebody corrects a question, the answer under
it responded to the *old* wording. Leaving it unmarked would imply the profile
answered the new one. `GET /profiles/{id}/thread/{interactor}` marks those
replies `answers_stale_text` and says so in words — the honest version is
"this was answered before you changed it", not a silent rewrite of history.

## Watch faces, and the wearables that show them

QRME had a watch *API* and no way to say **which watch**. `POST
/profiles/{id}/wearables` pairs one over Bluetooth — a watch, band, ring,
earbuds or glasses — and says which faces it may show.

<table>
<tr>
<td align="center" width="25%"><a href="docs/watch/01-agents.svg"><img src="docs/watch/01-agents.svg" width="150" alt="Agents"></a><br><sub><b>01</b> · Agents</sub></td>
<td align="center" width="25%"><a href="docs/watch/02-activity.svg"><img src="docs/watch/02-activity.svg" width="150" alt="Activity"></a><br><sub><b>02</b> · Activity</sub></td>
<td align="center" width="25%"><a href="docs/watch/03-profile.svg"><img src="docs/watch/03-profile.svg" width="150" alt="Profile"></a><br><sub><b>03</b> · Profile</sub></td>
<td align="center" width="25%"><a href="docs/watch/04-control.svg"><img src="docs/watch/04-control.svg" width="150" alt="Control"></a><br><sub><b>04</b> · Control</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/watch/05-microphone.svg"><img src="docs/watch/05-microphone.svg" width="150" alt="Microphone"></a><br><sub><b>05</b> · Microphone</sub></td>
<td align="center" width="25%"><a href="docs/watch/06-identity.svg"><img src="docs/watch/06-identity.svg" width="150" alt="Identity"></a><br><sub><b>06</b> · Identity</sub></td>
<td align="center" width="25%"><a href="docs/watch/07-on-camera.svg"><img src="docs/watch/07-on-camera.svg" width="150" alt="On Camera"></a><br><sub><b>07</b> · On Camera</sub></td>
<td align="center" width="25%"><a href="docs/watch/08-lobby.svg"><img src="docs/watch/08-lobby.svg" width="150" alt="Lobby"></a><br><sub><b>08</b> · Lobby</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/watch/09-screens.svg"><img src="docs/watch/09-screens.svg" width="150" alt="Screens"></a><br><sub><b>09</b> · Screens</sub></td>
<td align="center" width="25%"><a href="docs/watch/10-proceeds.svg"><img src="docs/watch/10-proceeds.svg" width="150" alt="Proceeds"></a><br><sub><b>10</b> · Proceeds</sub></td>
<td align="center" width="25%"><a href="docs/watch/11-coordination.svg"><img src="docs/watch/11-coordination.svg" width="150" alt="Coordination"></a><br><sub><b>11</b> · Coordination</sub></td>
</tr>
</table>

<table>
  <tr>
    <td align="center" width="35%"><a href="docs/screens/88-your-devices.svg"><img src="docs/screens/88-your-devices.svg" width="220" alt="Your Devices"></a><br><sub><b>88</b> · pairing, at sign-up</sub></td>
    <td valign="middle">

**Paired at sign-up, not found in a settings page.** The agent lights and the
watch faces are worth having on day one, so the device step is part of joining.

| may be paired | |
| --- | --- |
| watch · band · ring | on the wrist, on the finger |
| earbuds · headset | in or over the ears |
| **lapel mic · clip-on mic** | clipped to the collar or clothing |
| glasses · pendant | worn on the face or at the neck |

| refused | why |
| --- | --- |
| smart speaker · conference puck · room array · tabletop mic · desk mic | each **hears whoever walks in** — and that person did not pair it, was not asked, and may have a right not to be recorded |

  </td>
  </tr>
</table>

**The microphone kinds pair but do not listen.** Nothing in this module opens a
channel; a paired device is a registration and a set of allowed faces. A test
asserts no capture path exists here — no record, stream, listen or sample.

They are in the catalogue because the registry is what
[channel 2](#channel-2--lending-the-rooms-profiles-your-microphone) needs, and
a device somebody already paired for their watch face should not have to be
paired twice. That feature has now landed, and lending still happens *there*
rather than here — pairing says which devices you own, lending says what one of
them may do in one room, and keeping them apart is what lets a grant end with
the room without unpairing the watch.

**Room-facing microphones are refused at the door**, not allowed and then
restricted. A restriction is a setting somebody can change; a refusal is a fact
about the product. A platform cannot collect a waiver from a person who is
merely present, so until that is settled the whole device class stays out. The
refusals are published with their reasons so a client greys them out rather
than offering one and returning a 422.

**A wearable is not an embodiment.** `embodiments` records where a *profile*
lives — a speaker, a hologram, a robot body. This is hardware belonging to the
**owner**, reaching their own account. Folding them together would mean pairing
a watch could put somebody's synthetic persona on their wrist, which is a
different feature with a different consent question. A test asserts pairing
writes no embodiment.

**Pairing and permission only.** No sensor stream, no capture, nothing about a
microphone — a paired device here is a screen and a set of buttons. A test
asserts the pairing model does not so much as mention audio.

**Faces are a permission, not a free field.** A closed set, so a face added
later cannot arrive on every wrist by default — and a test holds the drawn
faces and the permission list in step, because a face you can enable and never
see is a permission granting nothing.

**Unpairing revokes rather than deletes.** The row survives, so a device sent
away cannot return by re-presenting the same name, and the owner can still see
what was ever paired — which is the question people actually ask after losing a
watch.

**Faces 06–09 all answer the same kind of question**: *what am I currently
presenting as, without looking at a phone.* Which profile you are posting as
and whether it is anonymous — the one mistake here that cannot be taken back,
and exactly the thing somebody assumes rather than checks when the answer is
two taps into a phone. What your camera is showing, which is the one thing your
own screen cannot show you, because the phone is in front of the lens and you
are behind it. Who is in the game with you, as counts. And which fixed screens
are live with you on them, because a fixture is the surface you can forget is
on — you walked away from it.

**05 Microphone is the one face that can end something**, and that is
deliberate rather than an exception to *"the wrist adds reach, not powers"*. A
lent microphone **is** this watch. Making somebody find a phone to stop their
own device listening would be the one permission on the platform you cannot
revoke from the thing it runs on, and *"yours to end, alone and at any moment"*
would be false.

**02 Activity is the community layer on a wrist, as counts.** Not the content:
a feed is a reading surface, and reading is the thing a glance cannot do. Same
reasoning that kept agent names off face 01.

## Channel 2 — lending the room's profiles your microphone

In a voice or video room your own microphone is already busy carrying your
voice to the other people. The synthetic profiles in that room are *reading
text*. They have no ear, so anything said aloud and not typed is invisible to
them, and asking one a question means stopping, typing, and breaking the thing
everybody else is listening to. The watch on your wrist has a microphone
nothing is using. This lends it to them.

`qrme/roommic.py` is the permission and the state; capture is on the device,
as everywhere else. The JIM-mini counterpart (`jim/mic.py`) lends the same
wearable to the Guardian during a call, and the one genuinely different
question here is that **a room has other people in it**. That difference is
the whole design.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/81-lend-a-microphone.svg"><img src="docs/screens/81-lend-a-microphone.svg" width="200" alt="Lend a microphone"></a><br><sub><b>81</b> · the room is told, not only you</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /microphones/vocabulary` | what may be lent, at what width, and what is refused — open, so a client can draw the picker |
| `POST /rooms/{id}/mic` | lend yours. Your own token, your own wearable |
| `DELETE /rooms/{id}/mic/{interactor_id}` | take it back. Yours to end, alone and at any moment |
| `GET /rooms/{id}/mic` | who in this room has lent one — readable by **the room** |

  </td>
  </tr>
</table>

**Everyone present is told**, and that is why the disclosure is the screen. A
room's participants can each see that a microphone is live and whose it is. In
a one-to-one call the other party is a stranger to this product and cannot be
told, which is why `jim/mic.py` refuses speakerphone outright; in a room they
are participants, they can be told, and telling them is the price of the
feature. A version of screen 81 showing the lender only their own row would be
the exact mistake the module was written to avoid.

**Readable by the room, not by anyone holding the id.** For a while the route
said the first and did the second — it checked nothing, and a room id is not a
secret: it rides in beacons and on printed QR stickers, which is what they are
for. That published who is wearing a live microphone, on what, and since when,
to whoever scanned the sticker. Being in the room now means holding a
participant's token, or the owner token of a profile in it.

**Only your own wearable, and only your own voice.** The grant is
per-participant and never becomes the room's microphone, because a participant
cannot consent on behalf of the people they can hear. Room-facing kinds —
speakerphone, conference puck, room array, laptop, console, doorbell — are
refused by name with the reason, not quietly missing from a list.

### The same microphone, off the room

Nothing in the rules above depended on the surface being a room, so channel 2
reaches the places that had none: a **watch party**, a **live desk's stream**,
and a **one-to-one connection**. Rooms already covered voice, video, AR and VR
by channel, so a 3-D or VR room lends exactly as a voice room does.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/120-lend-it-anywhere.svg"><img src="docs/screens/120-lend-it-anywhere.svg" width="200" alt="Lend it anywhere"></a><br><sub><b>120</b> · the same rule in every place</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /microphones/places` | where else it can be lent, and the test each place passes |
| `POST /places/{surface}/{id}/microphone` | lend yours here |
| `DELETE /places/{surface}/{id}/microphone` | take it back |
| `GET /places/{surface}/{id}/microphone` | who here has lent one — readable by **everyone present** |

  </td>
  </tr>
</table>

**One question decides whether a surface qualifies: can the other people
present be told?** That is what made a room different from a phone call in the
first place — `jim/mic.py` refuses speakerphone outright because the other
party on a call is a stranger to this product, with no surface on which to show
them a disclosure, so their voice could never be part of the bargain. A room's
participants *can* be shown one. So can a watch party's members, a desk's
visitors, and the other half of a connection. A surface without both a member
list and somewhere to render the disclosure must never be added here, whatever
else is convenient about it, and `GET /microphones/places` publishes the test
rather than only the list.

**Rooms deliberately do not write to the new table.** Two storage paths for one
surface is how a disclosure ends up reading one table while the grant sits in
the other, and a microphone that is live but undisclosed is the worst failure
this feature has. `roommic.lend_on` refuses `surface="room"` and points at the
room routes. It is a separate table rather than a column on `room_mics` because
this schema has no migrations — `CREATE TABLE IF NOT EXISTS` reaches a fresh
database and an `ALTER` reaches none of the existing ones.

**Membership is read from each surface's own table, and presence is checked
rather than assumed.** Somebody who left a watch party is not present — counting
them would let a former member go on reading who is wearing a live microphone in
a place they walked out of. An ended connection is not a place at all, for the
same reason a closed room takes no new grant. And an unknown id answers 404
rather than 403, so a stranger cannot use the status code to tell a real place
from an invented one.

**The place ending returns the microphones**, and that is wired into the
lifecycle rather than left as a function nobody calls: `watchparty.end`,
`desks.set_presence(..., "closed")` and ending a connection each return the
grants inside them. A grant that survived closing would be live again the next
time the desk opened, for a conversation nobody has had yet.

**Three form factors, three different jobs.** Screen 81 on the phone is one
room's disclosure to the person lending. [Watch face
05](#watch-faces-and-the-wearables-that-show-them) is the device *doing* the
listening, and the only face that can end something. [Desktop view
11](#desktop-app) is the one a wide window earns: a desk operator has a room, a
watch party and a stream open at once, and the question a phone cannot answer
is **where is my microphone live right now, all of it** — shown beside the
room's own disclosure, because those two being the same thing is the design.

**A device can be lent under the name it was paired with.** The pairing
registry calls a collar clip `lapel_mic`; this module and `jim/mic.py` call it
`lapel`. Two vocabularies for one piece of hardware, and for a while nothing
joined them — you could pair a lapel mic and be told `lapel_mic` was an unknown
microphone type when you tried to lend it, from a registry whose own comment
says it exists for this feature. `roommic.FROM_WEARABLE` translates rather than
renames: renaming here would desync the table from `jim/mic.py`, which is kept
in step by hand because the two products do not import each other, and renaming
there would break already-paired rows. A test holds every kind in the registry
against one side or the other, so adding a device forces the question *does
this carry a microphone* at the moment somebody adds it rather than the moment
a user tries to lend it. A refused kind gets its reason back, not "unknown" —
that word reads as a gap somebody files a bug about, or works around.

**It keys on its wearer *and* it runs near-field.** Two bounds, deliberately
separate. `VOICE_FOCUS` is the filter: the channel locks onto the lender and
drops the rest, which in a room is the other participants. `ROOM_GAIN` is the
limit: a room grant runs near-field however the lender has their dial set. The
lender's own preference is capped rather than rejected, and it is still theirs
everywhere else — a room is simply the one place it cannot be honoured. Both,
and not just the filter, because a filter can fail and the people it would fail
on did not choose to be in range.

**The room is shown what the microphone actually hears**, never what its lender
asked for. A rejected preference is the lender's business, and putting it in
the disclosure would tell the room something prejudicial and untrue of the
capture in the same breath.

**It ends when the room does.** A grant is scoped to one room and closed with
it, so a permission cannot outlive the conversation that justified it and
quietly apply to the next one.

**A profile that has been lent one is told its limits**, in the system prompt,
rather than left to infer them: it can hear the lender, it cannot hear the
others, those others may not realise it could hear them at all, and anything it
seems to have picked up from background talk is noise rather than something
said to it.

The stationary-microphone classes stay out for the separate reason set out
under [watch faces and wearables](#watch-faces-and-the-wearables-that-show-them):
a platform cannot collect a waiver from somebody who merely walked into the
room.

## Wearing a character over your own camera

A mask, a creature driven by your own expressions, a puppet, a replaced
background. Ordinary, and it lands directly on the argument everything else
here is built from: **a synthetic thing must say so.** An overlay is synthetic
media composited onto a real human face in real time — the definition of what
the AI mark exists for — and the fact that the person underneath consented does
not change what the *viewer* is looking at.

So the rule is neither "allowed" nor "banned":

> **An overlay is disclosed to the people who can see it, always, and it can
> never be the thing that makes a truthful badge false.**

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/121-wear-a-character.svg"><img src="docs/screens/121-wear-a-character.svg" width="200" alt="Wear a character"></a><br><sub><b>121</b> · the screen that offers it also says what it cannot be</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /overlays/catalogue` | what can be worn, where, and what is refused with reasons |
| `POST /places/{surface}/{id}/overlay` | put one on — your own face only |
| `DELETE /places/{surface}/{id}/overlay` | take it off |
| `GET /places/{surface}/{id}/overlay` | who here is wearing what — **everyone present** |

Worn in a room (voice, video, AR, VR, 3-D), a watch party, a one-to-one
connection, or your own stream.

  </td>
  </tr>
</table>

### A live desk wears one, and the badge stays true

This was refused at first, and the refusal was wrong. The reasoning was that a
character over the face makes *"Live person — not AI"* a false statement — but
that conflates two different claims. The badge does not say *this face is
unmodified*. It says **a real person is behind this**, which is exactly as true
of somebody in a mask as of somebody without one. **A costume is not a
synthesis.** Refusing it protected nothing and cost the people who most need to
work without showing their face.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/123-masked-and-real.svg"><img src="docs/screens/123-masked-and-real.svg" width="200" alt="Masked and real"></a><br><sub><b>123</b> · both facts, equally weighted</sub></td>
    <td width="66%" valign="top">

`GET /desks/{id}/live-person` returns one mark, and it does not change when
somebody puts a face on:

> **NOT AI · REAL PERSON**

An earlier version composed the badge with the costume — *"… · wearing The
Wolf"* — which answered a question nobody had. **A viewer is on a named
account's live or room.** The handle is at the top left, they chose it to get
there, and they know whose stream this is.

That last sentence was written before it was true. The top-left of a live
surface carried a `LIVE` pill and nothing else, and no route returned whose
surface it was — the argument for the simpler mark was resting on chrome that
did not exist. So `identity.whose(surface, id)` now answers it for a desk, a
room, a party, a connection and a stream; `GET /places/{surface}/{id}/whose`
publishes it; every screen with a picture draws it beside the `LIVE` pill; and
`GET /desks/{id}/live-person` returns it **with** the mark, so a client cannot
render one without having been handed the other.

An anonymous account answers with its silhouette name rather than with nothing.
A viewer still needs to know a stream belongs to one consistent account, which
is a different fact from knowing which person that is — and an anonymous
profile's `@handle` is withheld here, because this call answers *who is this*
rather than *where is this*, and returning it would put an identifier on the
one surface built to withhold one. The open question on that page is
never *is that his real nose*; it is *is there a person here at all*, and that
is the only thing this mark answers.

Dropping the costume half also removed a quiet penalty. Somebody who covers
their face because of dysmorphia, or because their work makes showing it
unsafe, was being handed a badge that announced the fact on every frame while
the person beside them got a clean one. **Same claim, same mark, whatever you
are wearing.**

  </td>
  </tr>
</table>

**The mark is bound to the account that owns the stream.** It is read from the
desk row and its attestation, never accepted from a client, so a stream that
never earned the badge cannot paste it on — the same reason the AI mark is
burned into a portrait rather than composited by whoever happens to be
rendering it. A desk with no attestation gets no mark rather than a weaker one.

The mark is never softened by the overlay, and must not be. What is behind the
camera is a person either way, which is the only thing that badge ever claimed.

**Seventeen face overlays**, and the list is a need rather than a nicety —
masks and half masks, characters, creatures, 2-D and 3-D avatars, helmets and
visors, paint, makeup, hair, headwear, eyewear, prosthetics, rendered styles,
and plain blur or silhouette for anybody who wants to be present without being
seen. Someone with dysmorphia has to be able to appear without appearing, and
one mask and a shrug is not that.

### Backgrounds: yours, imported, or generated

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/124-your-background.svg"><img src="docs/screens/124-your-background.svg" width="200" alt="Your background"></a><br><sub><b>124</b> · the room is a separate claim from the face</sub></td>
    <td width="66%" valign="top">

| source | what it means | synthetic |
| --- | --- | --- |
| `own` | a photo they took or already had | no |
| `imported` | an image brought in from elsewhere | no |
| `generated` | an AI-generated scene | **yes** |
| `blur` | their real room, blurred | no |

  </td>
  </tr>
</table>

**An AI-generated background is synthetic media**, and the person in front of
it being real does not make the room real. The disclosure says both, in that
order — *"their own face, unaltered — the background behind them is
AI-generated"* — because the viewer is deciding about the person, and the room
is the part that was made.

The `kind` says what happened to your face; `source` says what happened to the
room. A single "filter applied" would run the two together, so `source` is
**required** on a backdrop and **refused** on anything that covers a face: a
background silently recorded as `own` when it was generated is exactly the
disclosure this feature exists to make, and a claim about a background is
meaningless on a mask.

**An imported image needs the rights to it** — asked rather than guessed, for
the same reason as the face question. Nothing here can look at a file and know
who owns it, so the one answer with an obvious consequence is the one that is
enforced.

**No overlay may depict a real, identifiable person.** A live-driven likeness
of somebody who is not in the room is the exact artefact this codebase argues
against, and *"it was only a filter"* is how it would arrive. `overlays.REFUSED`
names the classes with the reason — real person, public figure, another user's
portrait, an age shift, and a badge drawn into the picture. Published by name,
because an absent option reads as a gap somebody works around, and every one of
these is a decision.

**It is asked, not guessed.** Nothing here can look at a file and tell whether
the face in it belongs to somebody — that is a judgement about the world, not
about an asset. So `depicts_real_person` is a declaration the wearer makes,
refused when true, and recorded either way: a false declaration then has a name
and a timestamp on it, which is the difference between a rule and a hope.

**The disclosure distinguishes what it is disclosing.** A replaced face reads
*"not their face — Blue Fox, drawn over the camera in real time. A real person
is underneath"*; a replaced background reads *"A library — their own face,
unaltered"*. Saying "not their face" over a blurred backdrop is a lie in the
other direction, and a disclosure that cries wolf is one people learn to skip.

**Nobody can put one on you.** An overlay somebody else can apply is not a
costume, it is a puppet, and the person whose face is underneath is the one
whose consent counts. Removal stamps a time rather than deleting the row, so a
viewer who saw a face and later wants to know what they were actually looking
at has an answer.

## More than one synthetic thing in a game

`qrme/routers/gaming.py` seats **one** profile beside a player — a companion, a
teammate, a practice partner. That is a conversation. `qrme/gamelobby.py` is
the roster: several synthetic profiles *and* running agents in the same
session, with the real players.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/122-game-lobby.svg"><img src="docs/screens/122-game-lobby.svg" width="200" alt="Game lobby"></a><br><sub><b>122</b> · every row says what it is</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /gaming/lobby/vocabulary` | seats, kinds, the cap, and what nothing here can do |
| `POST /gaming/sessions/{id}/lobby` | seat a member |
| `GET /gaming/sessions/{id}/lobby` | the roster — the people in the match |
| `DELETE /gaming/sessions/{id}/lobby` | take one out |
| `GET …/lobby/context` | what a synthetic member is told about its own position |

  </td>
  </tr>
</table>

**Adding a second one changes the question, and the question is fair play.** A
companion calling shots is a teammate talking. Five of them coordinating on one
player's behalf is indistinguishable, from the publisher's side, from a bot
squad — and this platform's fair-play rule is already *absolute* rather than a
toggle. So the roster carries two limits a single companion never needed.

**Synthetic members are capped at four**, counting the session's own profile.
Not for load: a lobby where the synthetic side outnumbers the humans has stopped
being people playing with help and become an operation being run, whatever any
single line says. The cap counts the host because counting only the table would
let the limit sit one higher than the number the roster actually shows — the
sort of off-by-one that turns a stated limit into a lie about itself.

**No synthetic member ever occupies a player slot**, and a console of its own
does not change that.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/125-never-a-player.svg"><img src="docs/screens/125-never-a-player.svg" width="200" alt="Never a player"></a><br><sub><b>125</b> · the workaround, refused by name</sub></td>
    <td width="66%" valign="top">

`teammate` is the seat that means *in the match, on the roster, taking a slot*,
and nothing synthetic may hold one — checked in `gamelobby.seat`, not left to a
prompt to honour, because the entire point of the rule is that it survives a
model deciding otherwise. The seats beside the players stay open: companion,
practice partner, coach, spotter, archivist.

The rest of the list closes the plumbing, and each entry is refused **in the
words somebody would use to ask for it** — because a single generic refusal
loses that argument. "It's only a second controller" is true, and not the
point.

| named | why |
| --- | --- |
| `own_hardware` | a second machine moves where a bot runs; it does not turn the bot into a player |
| `second_controller` | a second pad on the same console is the same bot with a shorter cable — a controller nobody is holding is not a player's |
| `bluetooth_input` | pairing a member to a console as an input device is that again, wireless. The pairing is the tell, not the cable |
| `capture_perception` | a capture card or video-in feeding it the game's picture is how it would learn where to aim. **Watching the screen to play is playing** |
| `game_plugin` | an overlay, mod, injector or plug-in handing it state or controls, whatever it is called and whoever wrote it |
| `own_character` | no member pilots a character — not a second one beside yours, not a co-op partner, not a body in the world |

  </td>
  </tr>
</table>

**Nothing here can act in a game.** Members observe and they talk. There is no
input, no aim, no macro, no automation, no exploit, no player slot and no
hardware route to one — published by name in `gamelobby.NEVER`, and a test
asserts no function in either module is named for any of them. *"We did not add that"* is a fact about today; the test is what
makes it a fact about tomorrow. The difference between a coach and a cheat is
exactly that line.

**Every member says what it is** — player, profile or agent — on every read,
never inferred from a name. It matters more here than in a chat room, because
the other people in a match did not opt into anything. The screen draws the
human row identically to the synthetic ones except for the word: a roster that
styled people differently would be telling you by decoration what it should be
telling you in text.

**Agents bring their light.** An agent in a lobby is a running workflow, so it
carries the same green/amber/red as everywhere else. A member that has stopped
and is waiting on a person must not look, on the roster, exactly like one that
is working.

**The session's own profile is derived, not stored.** A copy of it in
`game_lobby` would be a second place the same fact lives, and the day the two
disagree the roster would show a session hosted by a profile the session does
not think it has.

**A minor anywhere in the lobby makes the whole lobby strict**, keyed on the
lobby rather than on the session's owner — the person a line might land badly
on is the one sitting in it, not the one who started it.

**Two consents, and neither replaces the other.** The session owner decides who
is in their lobby; a profile or agent must be one the same account holds,
checked on `owner_id`. Somebody *else's* profile is a two-party question and
this is not the module that answers it — `qrme/sharing.py` already asks both
sides — so it is refused with a pointer rather than half-answered here.

## A profile on a screen that stays where it is

A wall panel in a lobby, a kiosk by a door, a counter screen, a pane of glass
with something behind it. `qrme/displays.py` is the watch-face idea from
[wearables](#watch-faces-and-the-wearables-that-show-them) applied to fixtures
— a **closed set** of things a screen may show, for the same reason: what may
be displayed is a permission, and a permission with open-ended values is one
nobody can audit.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/126-on-a-screen.svg"><img src="docs/screens/126-on-a-screen.svg" width="200" alt="On a screen"></a><br><sub><b>126</b> · full, half or a strip · opaque or glass</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /displays/vocabulary` | kinds, sizes, finishes, faces — and what a wall may never show |
| `POST /profiles/{id}/displays` | put this profile on a screen. Owner-only |
| `GET /profiles/{id}/displays` | every screen it is on — **owner-only**, it is a list of places |
| `GET /displays/{id}` | what this screen shows — **public**, and that is the point |
| `PUT /displays/{id}/faces` | change what it shows |
| `DELETE /displays/{id}` | take it down |

**Sizes**: `badge` (a strip), `half`, `full`. **Finishes**: `opaque`, or
`transparent` with the room behind it.

  </td>
  </tr>
</table>

**A stationary screen is not a small watch, and that difference is the whole
module.** A watch is on one person's wrist — they chose it, they are the only
one reading it, they can turn it over. A wall panel is read by **whoever walks
past**: a courier, a child, somebody visiting the person whose profile it
shows. Nobody in that corridor opted into anything.

That is the room-microphone argument arriving from the other direction. There,
a device that *hears* people who did not agree; here, one that *shows* things
to people who did not ask. So the rule is **stricter** than the watch's, not
looser: every face on the list is something already public — a front page, a
desk's presence, a beacon's QR, agent lights as counts, opening hours, a
greeting the owner wrote. Anything personal is a count or it is not there.

**There is no `control` face.** The watch has one — assist, halt, approve — and
it is safe there because the wrist it is strapped to belongs to the owner. A
button on a wall is pressed by whoever reaches it. Messages, memory, friends,
notifications and agent *names* are refused the same way, each by name with the
reason, because every one of them is allowed somewhere else in this product and
the refusal is a decision rather than a gap.

**The disclosure survives the glass.** A transparent panel's background is a
corridor — a moving one — so contrast is not something the renderer controls.
The AI mark gets a backing plate at that finish, and this is not a style
preference: a mark that vanishes against a bright wall is worse than no mark,
because the rest of the card still reads as a person and the one thing
correcting that impression is the thing that disappeared.

**A beacon face needs the whole surface.** A QR at strip height is a QR nobody's
camera resolves, and a code that cannot be scanned looks broken rather than
absent.

**Placing one is the owner's decision**, like a beacon — a screen bolted to a
wall is a beacon with a plug in it. Where the screens *are* is owner-only for
the same reason the beacon listing is; what a given screen is *showing* is
public, because a fixture in a corridor cannot keep a secret from the corridor.
That last one is also the check on the whole design: if that route could leak
anything, the wrong thing is on the face list.

The console reaches it (**157**), and draws the asymmetry rather than leaving
both halves looking like ordinary rows: what a given screen is showing sits in
public, and the list of an owner's screens does not. The `never` list is
rendered verbatim, each entry with its reason — those sentences are the
argument made once, carefully, and a paraphrase would be a worse version of it.

## Show me around — the guided walkthrough

[`qrme/help.py`](#a-help-box-on-every-screen) answers a question somebody
thought to ask. `qrme/tutorial.py` is the other half of the same surface: a
walkthrough for somebody who does not yet know what there is to ask about.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/127-show-me-around.svg"><img src="docs/screens/127-show-me-around.svg" width="200" alt="Show me around"></a><br><sub><b>127</b> · seven chapters, seventeen steps</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /tutorial` | the whole walkthrough, chaptered |
| `GET /tutorial/steps/{key}` | one named step |
| `GET /tutorial/for-screen/{n}` | the lesson covering a given screen |
| `POST /tutorial/start` | begin, or begin again |
| `GET /tutorial/progress/{id}` | where a learner is, and what is next |
| `POST /tutorial/done` | mark a step and get the next |

`?mode=voice` on any of them renders it for listening instead of reading.

  </td>
  </tr>
</table>

**The guide has no name and no face**, and that is structural rather than a
style choice. A tutorial guide with a persona would be the most convincing
synthetic profile on this platform — met by every user in their first minute, at
the exact moment they have the least idea what is synthetic here. It is
furniture, and it says so.

**It never taps anything for you.** Every lesson says what to tap; none of them
taps it. A walkthrough that placed a beacon or sent a message *"to show you
how"* would be acting on somebody's account before they understood what the
account was. A test asserts the module writes to nothing but the learner's own
progress.

**It works with no model configured**, like `help.TOPICS` — written prose,
matched to screens. A walkthrough that needs an API key is one that is missing
on a self-hosted deployment, which is a supported setup here rather than a
degraded one. A test asserts no provider reaches it.

**Voice and text are one lesson rendered twice, not two scripts.** Spoken, a
screen number is noise — nobody listening is helped by *"screen eighty-one"* —
so voice drops the numbers and keeps the sentence. Two hand-written versions
would drift, and the spoken one would be the one nobody re-read.

**And it cannot quietly fall behind the app.** Each lesson names the screens it
is about, and a test asserts **every screen in the gallery is claimed by some
lesson** — both directions, so a renumbered screen also fails. Add a feature,
draw its screen, and the walkthrough breaks until somebody has said what it is
for. That is the only way a guided tour of a moving product stays true, and this
repository has already shipped a screen nothing referenced.

**Progress is recorded per step rather than as a cursor**, so somebody who
skipped ahead and came back is not told they finished things they never saw.

Until now none of this was reachable. The walkthrough existed, worked with no
model, kept itself honest against the gallery — and there was no way to take
it. The console had the help *box* (type a question, get an answer) and not the
tour, which is the half for somebody who does not yet know what to ask, and
therefore the half that matters on a first minute.

**160** is its door: where you are in the tour, every step in every chapter, and
a lookup by screen number for *what am I looking at*. It also draws the dock
catalogue including what the dock **refuses** — `control` is not a face, because
assist, halt and approve are actions and the pane does not act. A catalogue
showing only what is available would hide the more interesting decision.

### A refusal is a thing with a shape

**161** is not a tab. It is the card that appears inside whichever screen was
refused, and it is drawn because of what building the doors kept turning up.

Several gates here answer with an *object* rather than a sentence. The plan gate
is the clearest: it names the capability that was wanted, the plan that has it,
the plan you are on, the price, the period, a human sentence, and the fact that
the billing is simulated. Somebody wrote that deliberately — it is strictly more
work than returning a string, and the only reason to do it is so a screen can
draw a real answer instead of a wall.

The console then flattened it. `req()` did `JSON.stringify(detail)` and threw
the result as an error message, so every screen that catches an error and shows
`.message` — which is all of them — showed the user the raw object. Nothing
failed: the request was right, the refusal was right, and it was destroyed on
delivery. The typecheck had nothing to say about it, because a string is a
string.

`RequestError` now carries `status` and the untouched `detail`, `planGate()`
reads the structure back out, and `Refusal.tsx` decides how to draw it. The
price and the words *simulated — no real funds move* are rendered on the same
line, because a screen quoting $130 a month without them would be making a
claim this product spends effort avoiding everywhere else.

Every screen then threw the same structure away one layer up —
`setError((e as Error).message)`, in all of them — so fixing the transport
alone changed nothing anybody could see. They now hold the error and hand it
to `Refusal`, which keeps each screen's existing look for an ordinary failure
and draws a gate as a card with a button.

### Screens 130 and 131 — the plan the refusal names

Drawing the refusal properly found the next thing. There was no plans surface:
`GET /plans` and the three `/memberships` routes had no caller either, so the
console could refuse you for not having Pro and had no way to sell you Pro.
That is worse than a flat no — an offer naming a plan in a product with no way
to join one advertises something that appears not to exist.

`Plans.tsx` is that door, and `onPlans` is threaded from the shell into every
screen that can be refused, so the button on the card goes somewhere. Two
things the screen shows rather than smooths over:

- **`visitor` and `free` are different plans that both cost nothing.** A
  visitor has no account and can read a public page; free has an account whose
  work sits in this platform's database in the clear. A picker written from the
  price alone collapses them into one $0 row and hides the whole difference.
- **`the_difference` is rendered verbatim** above the cards — *free and Basic
  run the same app; the difference is where your data lives, and who holds it*
  — because a grid of ticks invites the opposite conclusion, that $20 buys
  features. It buys custody.

The price list needs no account, which is `tiers.py`'s decision and not the
console's: *a paywall nobody can read the terms of before signing in is one
people bounce off*. Everything above the membership card renders signed out.

### Screen 173 — beginning, and passing on

The last five routes, and the backlog reaches **zero**.

**An owner token cannot be the gate on succession.** The signal that route
answers is that the owner has died or cannot act, so requiring their
authorisation would be requiring the one thing known to be unavailable. A
reviewer holds it — outside profile ownership, against a `verification_ref`
kept out of band: a death certificate, a power of attorney. With somebody
named, control passes and a fresh owner token is minted. With nobody, the
profile sunsets to memorial: **frozen rather than orphaned**, because a profile
whose owner has died and which nobody can reach is worse than one that has
plainly stopped.

A contested identity cannot be handed on. An open objection blocks succession
with a 409 — inheriting a profile somebody is disputing would settle the
dispute by transfer rather than by resolving it.

At the other end, **genesis** is a profile born from four questions, and it may
choose its own name from the answers. That is not decoration: a persona
assembled from what somebody said about themselves should not then be handed a
label by a form field.

#### A route that asked for nothing at all

`POST /packs` took no token. Anybody could publish a pack to the marketplace,
name any string as the `publisher`, and name **any account** in
`publisher_owner_id` as the one sales accrue to. The argument against that was
already written down one module over, about gifts — *a body-supplied
beneficiary would let anyone direct a gift meant for a performer into their own
balance* — and this route was making the opposite choice. The account is now
read from the caller's own token, and the body's is ignored.

And the wrist: one press goes down the same paths the full apps use — same
auth, same allowlists, same moderation. A shortcut that skipped any of those
would be a second, weaker way in, which is exactly what a wrist should not be.

---

## The doorless backlog reached zero

It began at **116** and was worked down a block at a time. `doorless_routes.txt`
is now empty, and `test_every_route_has_a_door.py` has a new assertion saying
so directly — separate from the record comparison, so the message is plain when
it goes: *the number is no longer zero*, rather than *strike this line*.
Deferring a route legitimately means editing that test as well as the file,
which is the right amount of friction for a decision that used to be made by
accident.

The guard-on-guard changed with it. It used to assert the snapshot was
non-empty, which no longer means anything, so the liveness check moved to where
the meaning lives: **the console must still be producing call sites.** If the
extractor broke entirely, every route would read as doorless — loudly. If it
were quietly narrowed to a handful of forms, that count is what would notice.

What the whole exercise actually produced was not doors. It was defects, and
almost none of them were visible to the typecheck: a swallowed refusal; two
silently-permissive writes; a test that had been green for years for the same
reason a bug was invisible; a picker offering options the server refuses; four
route-audit blind spots; two surfaces that took no token at all; a licence sold
to somebody who could not use it; a link that resolved against the wrong
origin; an honesty note served to nobody. **Building the door kept finding
something wrong with the room behind it** — which is the argument for the whole
method, made once, at length, by doing it 116 times.

### Screen 172 — one thing, named

Six routes that each answer about one particular thing, and six different
answers to **who may ask**:

| | who may ask |
|---|---|
| the light legend | anybody; it takes no id at all |
| a campaign | **anybody**, deliberately |
| an organization | signed in |
| an excursion | the profile's owner |
| somebody's lent skills | themselves |
| a place's lent skills | you, filtered to your own |

**The campaign is the inversion, and it is the point.** It is the most public
read in this product, and that is exactly what makes it honest: it carries
`proceeds_to`, so somebody about to give money sees who receives it on the
same card, before they give it. A fundraising page that hid its split would be
the ordinary kind of dishonest. In the same spirit a campaign cannot exist
before the designation does — creating one first is refused with *say where
the money goes first: designate loved ones or organizations before asking
anyone for it.*

Two reads are narrower than their names suggest, and both say so rather than
letting a screen misread them. An **excursion** carries the brief that was
sanitised before it left and the count of what was stripped out of it; those
two numbers are the whole basis on which the feature asks to be trusted, so
the screen shows them together — *nothing left this machine* and *three
private terms stripped before it went* are very different reassurances and
either alone is misleading.

A **place's** lent skills are filtered to the caller's own, with a `note`
saying a room-wide view needs a membership check that does not exist yet. The
console renders that note verbatim, because a short list there means *your*
grants, not *no* grants — reading it the other way turns an access limit into
an empty room.

The light legend is built from the mapping rather than written beside it, and
the backend says why: *a legend that is maintained separately eventually
describes a mapping the code does not have, and it is the legend people
trust.* So the statuses driving each light come back with it, and the screen
shows them.

### Taking it back — three answers to "there was nothing there"

Four routes, and **no new screen**. A take-it-back control belongs beside the
thing it takes back; a fourth screen collecting all the deletes would be a
place nobody would look. So unfriending went onto Friends, withdrawing a
comment onto Wall, and listing a profile in the directory onto Market.

Building them side by side surfaced a disagreement none of the three routes
knows it is in:

| | nothing to remove | somebody else's |
|---|---|---|
| a comment | **404** `no such comment` | **403** `not your comment` |
| a directory listing | **404** `profile is not listed` | 403 |
| a friend | **200**, `removed: false` | — (owner-only) |

The third is the one that bites. A caller reading only the status code reports
*Removed.* for a row that was never there — so the friends screen reads the
flag and says *"Nothing to remove — not a friend."* The other two let the
refusal carry the fact.

None of this is a bug in any one route; it is three reasonable local choices
that stop agreeing the moment a screen has to speak for all of them. Recorded
rather than unified, because changing a delete's status code changes it for
every client already written against it — and a test now asserts all three
together, so a future round that does unify them changes it on purpose.

Two controls are absent rather than present-and-refused. The founder's two
profiles are pinned and answer 409; the list marks them with `pinned`, which
the backend's own docstring says exists *so a client can render those rows
without a remove control*. And *withdraw* appears only on your own comments —
the profile being commented on is not the comment's author, and removing
criticism from your own page is a different power from withdrawing your own
words. This route grants only the second.

### Screen 171 — what leaves, and on what terms

Five routes: the gateway's status, the contribution view and its revoke, and
the two halves of licensing a profile out.

**Two different kinds of leaving**, kept apart because conflating them is how
somebody agrees to the wrong one. A *contribution* sends one anonymised
exchange to the shared model — no ids, the persona name replaced, and a random
ref so the item can be deleted at the gateway later without identifying
anybody. A *licence* sends the profile itself: the right to consult it, or
where the offer allows, to derive a whole new agent seeded from its persona
and owned by the buyer.

**The preview is a dry run, and the heading has to say so.** `preview_next` is
computed whether or not the profile is opted in, which is useful — it answers
*what would this cost me* before you commit — but a console rendering it under
one heading either way tells an opted-out owner their next conversation is on
its way out. The heading changes with `opted_in`; the content does not.

Revoking does two things and reports them apart: it stops future
contributions, and it asks the gateway to delete past ones by their refs.
`deleted_at_gateway` comes back true **vacuously** when nothing ever left, so
the console reads the count beside it — a tick shown for both cases would be
the wrong reassurance.

#### A licence sold to somebody who could not use it

A licence permitting derivatives used to sell to anybody. A fourteen-year-old
could buy one: **201**, `can_derive: true`, and the fee credited to the seller
at sale time — then a **403** on the only thing the licence exists for.
Somebody had been paid for a thing the server would not hand over.

The adult check now runs at **acquire**, where the money moves, rather than at
derive. A consult licence still sells to anybody, deliberately: it buys time
with a profile and creates no new owner, so tightening that would be a
different decision than the one this fixes.

### Screen 170 — reaching out, and what stops it

Five routes: the outreach itself, the quiet-hours window, the engagement
record, a rating, and the latent picture of one relationship.

**Four refusals, and only two of them are the owner's to lift.** A profile may
message somebody unprompted only if its owner switched that on, and even then
three more gates stand in the way. They answer in four different sentences,
and the difference is the whole point — a screen that collapsed them into
"can't right now" would be discarding the only thing the owner can act on:

| | who lifts it | how |
|---|---|---|
| reactive-only (403) | the owner | turn outreach on |
| awaiting a reply (429) | the recipient | reply once |
| rate cap (429) | time | wait out the interval |
| quiet hours (429) | **the recipient** | change their own window |

**Quiet hours are not the owner's to set.** Sending them with an owner token
is a 403, and that refusal is the feature rather than a gap in it: a window
your correspondent can move is not a boundary. The console shows the control
to whoever holds the person's own token and explains the refusal to everybody
else, because an owner who does not know why it is missing will look for a
bug.

The window is half-open — from the first hour up to but not including the
second — so a start equal to its end covers **nothing**. Somebody setting 9 to
9 to mean *all day* gets no protection at all. That is recorded as it is and
warned about on the screen rather than corrected: changing the arithmetic
would silently redefine every window already stored, which is a worse answer
than saying it plainly.

#### Two surfaces that took no token at all

Both found by building the screen. Neither was visible to the typecheck, and
neither was caught by the suite — the tests sent no token because they did not
have to.

- **The engagement record was readable by anybody.** How often a named person
  talks to a profile, across how many sessions, and whether they liked it,
  answered 200 to a caller holding nothing. The rule was already written down
  one route over: a profile's beacon list is owner-gated because *that is a
  list of physical places associated with a person*. This is the same argument
  about a different column. It is now the owner's and that person's, and
  nobody else's.
- **A rating could be cast in somebody else's name** — and that is worse than
  it first sounds, because an `up` rating is the trigger for contributing the
  exchange to the shared cloud model. Open, this let an unauthenticated caller
  cause a stranger's conversation to leave the deployment: the one failure
  this repository's whole cloud posture exists to prevent, reachable with two
  ids and no token. A rating now needs the rater's own token, and the owner is
  refused it too — a rating in somebody's name is a lie about what they
  thought, and the score is what the profile then behaves from.

The embedding stays owner-only, and unlike the engagement record the person
themselves does not get it either: it is not a record of what they did, it is
what the profile inferred. It is rendered rather than described, because a
number nobody can see is a number nobody can argue with.

### Screen 169 — where people find you

Six routes: the two scan surfaces, the two QR images, and the platform beacon
that is neither.

**Two codes that look identical and go opposite ways.** A placed beacon brings
a stranger *here* — the profile answers them on QRME. A platform beacon sends
them *away*, to an Instagram or Mastodon account that already exists; only
where there is no handle to build a link from does it fall back to a QRME
summon page. The pictures are indistinguishable, so the screen says which is
which. Scanning one to find out is not a reasonable way to learn it.

**Looking at a code is free; opening it is not.** Every scan surface
increments the count — the page, its JSON twin, and the older `/summon?ref=`
— because the server cannot tell an owner checking their own sticker from a
stranger who found it. Only the QR image itself is free. A `?preview=1` would
fix the inconvenience and ruin the number: the count is the only evidence a
sticker on a wall is working at all. So the console renders pictures freely,
never opens a scan page on its own, and labels every scan link with what it
costs.

A connection has a direction and the two never share a row: `collect` pulls an
account's content in, `publish` runs the profile out, so a read-only import can
never also post. Only `publish` has a beacon, and the list says so by giving
`beacon: null` — the button is absent rather than present and refused.

#### The audit was blind to the two requests with no function call in them

An `<img src>` is a fetch. An `<a href>` is a fetch. Neither passes through
`req()` on the way, and the route extractor could see neither — so
`/b/{id}` and `/beacons/{id}/qr.svg` sat on the doorless backlog while
Placements had been rendering both since it was written. That is the same
false-positive failure the nested-template bug produced a few rounds ago,
arriving from a different direction: a guard that invents work fails more
quietly than one that misses some.

Worse, the exemption list had absorbed three of them. `/pair/qr.svg`,
`/desks/{id}/view.webp` and `/desk-beacons/{id}/qr.svg` were all marked
*"rendered in an `<img src>`, not fetched by the API client"* — an exemption
made out of a blind spot, which is exactly the shape that stops anybody
asking. One of the three turned out to have **no door at all**: a desk's view
frame was never rendered anywhere in the console, so the honesty note attached
to it — *a sample view; this deployment has no camera on this desk, so the
frame is not live and is not claimed to be* — was being served to nobody.

The rule the list now holds to: exempt a path because nothing should ever call
it, never because the audit cannot see the call. Two entries survive — a terms
page and the click target of a verification email, both places somebody is
*sent* to from outside.

#### And a link that went nowhere

A desk beacon returned a **relative** `scan_url` while the profile beacon next
door returned an absolute one. The desk screen rendered it as a link, which
resolved against the *console's* own origin — so it went nowhere in every
build where the console is not served by the API, which is every packaged
build. The QR image had been encoding the absolute URL all along; the JSON
description of that same code disagreed with it. Both shapes are now asserted
side by side, which is the only reason they cannot drift apart again quietly.

### Screen 168 — who follows, and what they pay

Nine routes: subscriptions, gifts, the audience counters and the buyer's side
of the ledger.

**Nothing renews on a timer.** A period is charged when somebody presses
renew — so `periods` is a count of deliberate acts, and the screen says that
rather than showing it as a duration. `audience.py` gives the reason: a
deployment left running does not accrue charges nobody authorised and nobody
saw. Paid also asks for an `accept_price` that matches the price *exactly*,
which is not a flag but a check that the number somebody agreed to is the
number being charged.

One asymmetry worth knowing, because the two routes look alike:

- a **gift** reads its beneficiary from the subject — `commerce.beneficiary_of`
  says why, that *a body-supplied beneficiary would let anyone direct a gift
  meant for a performer into their own balance*;
- a **subscription** takes a beneficiary from the request body.

The console sends the profile's own account and shows which account the money
is credited to, because that is the part somebody paying is entitled to see.
It is a question worth settling rather than something I changed unilaterally.

Gifting refuses without a verified birthdate — *an unverified age is not
evidence of an adult* — and `cap_per_gift` is published so the limit can be
stated before somebody runs into it.

### Screen 167 — who is in the game with you

Eight routes: the gaming lobby, and the handoff.

The lobby's entire design is one sentence it publishes about itself —
**everything in this lobby observes and talks; nothing in it plays** — and the
`never` list spells that out twelve ways. The obvious entries are the dull
ones. The interesting four close routes somebody would otherwise argue for:

- **its own hardware** — *a second machine does not turn a bot into a player;
  it just moves where the bot is running*;
- **a second controller** — *the same bot with a shorter cable, and a
  controller nobody is holding is not a player's*;
- **a Bluetooth pad** paired to it as an input device;
- **a capture card** feeding it the picture.

The console renders all twelve verbatim. "No cheating" is not the same
statement, and shortening an argument to a slogan is how the argument gets
lost.

The uncomfortable card is the one showing **what a synthetic member is told**.
The instruction says openly that some of the others in the lobby are synthetic
too — because a model that believes every callsign is a person addresses them
as people, and a lobby that reads as five friends when it is one player and
four generated voices is exactly the impression this product exists to
prevent. It is shown to the owner because that is the only way to check it.

The handoff turns out to be the **lighter sibling of the referral above**, and
the pair is worth seeing together:

| | referral | handoff |
|---|---|---|
| authorised by | a device signature over the bytes | explicit consent |
| lifetime | one open, ever | until revoked |
| on revoke | — | the package is *purged*, not hidden |

Neither substitutes for the other, and a product offering only the heavier one
would push people to skip it.

### Screen 166 — handing it to somebody qualified

A profile is not a clinician, and the package it assembles says so before it
says anything else. Twelve routes: the clinician directory, the referral
lifecycle, and the signature behind it.

Every part is built to be awkward where the easy version would be wrong.
**Prepare releases nothing** — you read exactly what would go, and the
challenge it raises **is the hash of those bytes**, so signing it signs this
summary rather than a checkbox, and a summary edited afterwards cannot ride the
old signature. **The link works once**, and a second attempt says *when* the
first happened rather than quietly working, because a replayed link is
something the patient should be able to discover. The clinician may write back
one time, and their words stay theirs — the profile never recites them as its
own knowledge.

Three pairs here are one wrong variable from a bug that looks like success, and
each is labelled on the screen rather than left to the reader:

| | |
|---|---|
| the **referral token** | opens it |
| the **reply token** | answers it, and does not exist until it has been opened |
| `envelope_id` | is what gets signed |
| `signature_id` | is what release checks |
| **proofing level** | how the identity was checked |
| `can_sign` | what that actually permits — and a referral is `high` |

The screen shows `can_sign` rather than the tier table, because that is the
fact somebody needs when the button is greyed out. Matching is expertise-first
by design: *a cardiologist two streets away is not a substitute for a
psychiatrist*, so area filters and location only ranks, and no match is an
empty list rather than a near-miss.

**The route audit gained a second blind spot fix.** The WebAuthn ceremony is a
*page the browser navigates to* — it has to be, because WebAuthn refuses a
mismatched `rpId` and an opaque origin has none to match — so no client
"requests" it and every client that opens it counted as doorless.
`clientpaths.py` now recognises `window.open` as the GET it is. The URL has to
be built as `getBase() + \`/signatures/ceremony…\`` for the extractor to
resolve it, which is worth knowing before the next one.

### Screen 165 — what it can do for you, and the mark on what it makes

Triage, proofreading, composing something to keep, the wearables the watch
faces run on, the reviews from people who actually talked to it, correcting
your own turn, and the check on any mark. Fifteen routes.

**Checking a mark asks two questions, and they can disagree.** `valid` says the
credential was issued by this deployment; `content_match` says this is the
content it was issued for. A genuine credential whose content has since been
altered comes back `valid: true, content_match: false` with a sentence saying
so. A screen reporting `valid` alone would call something genuine at the exact
moment the server said it had been changed — the one failure a provenance check
must not have, because it is worse than having no check. The screen asks both,
always, and draws the mismatch loudest.

Two arguments are rendered verbatim rather than summarised. **A room-facing
microphone is refused with a paragraph**: a smart speaker *hears whoever walks
into the room, and they did not pair it, were not asked, and may have a right
not to be recorded*. "Unsupported device" would be the console throwing away
somebody's reasoning. And **triage returns the reason each item survived**, with
its score — a pile sorted by a number nobody can see is a pile somebody has to
re-check by hand, which is the work triage was supposed to do.

`answers_stale_text` is drawn too: a reply written before the message above it
was edited says so, rather than the conversation quietly rewriting itself.

Two smaller things the round turned up. `include_revoked` was never bound, so
the promise in `wearables.py` — *unpairing is a revocation, not a delete, the
row stays* — was invisible in the console; a kept promise nobody can see may as
well not have been kept. And **the route audit could not see `fetch`**: `req()`
serialises JSON, so a raw-bytes upload has to call `fetch` directly, and
`POST /profiles/{id}/media` had a working door while still counting as
doorless. `clientpaths.py` now recognises both call forms.

### Screen 164 — what a profile is made of

Source material, the dials, a CV, the specialists it hands work to, the bodies
it speaks through, and the local fine-tune that folds all of it back in. Twelve
routes and not one caller in the console: the profile could be created and
talked to, and everything that made it *this* profile rather than a default one
was unreachable.

Two of these writes were **silently permissive**, and it is the same shape
twice — a Pydantic model where every field has a default, so a body it does not
understand is accepted, discarded, and answered `200`:

| route | takes | the guess |
|---|---|---|
| `PUT .../steering` | `values` | `dials` — what the *read* calls its catalogue |
| `PUT .../experience` | `period` | `years` — what anybody writing a CV form reaches for |

Neither produced an error. The row saved with no dates, the dials did not move,
and both requests looked exactly like successes — same status, same shape,
plausible body. Nothing in the response distinguished *I applied your change*
from *I ignored it*, so a client that fired and moved on would never find out.

Both models are strict now, so a wrong key gets a 422 naming the field. But the
strictness is the fix, not the guard: the guard is the thing that would have
caught it in the first place, which is **writing and reading back**. That is
what `test_a_write_that_answers_200_did_something.py` does, and its name is the
rule — *a request model with defaults for every field can never fail on a body
it does not understand, so where that model is the target of an owner's edit,
"accepted" and "applied" have to be checked separately.*

Making the models strict then broke a test that had been green for years, and
the way it broke is the sharpest part of this. `test_the_menu_matches_the_kitchen`
has a case named *every dial the server describes can be set* — written for
exactly this failure, and sending `{"dials": {…}}`. It passed on every dial
while setting none of them, because the server accepted the body and ignored
it. **The guard was green for the same reason the bug was invisible.** It no
longer trusts the status: it moves each dial off its current value and asks the
server what it holds.

Building the screen produced a third one of the same family. The picker for
what a profile speaks through offered `screen`, `wearable` and `vehicle`; the
enum is `speaker, earpiece, hologram, robot, humanoid, other`. Each wrong option
sat in the dropdown looking exactly like a right one and would have 422'd on
submit. A test now reads the `Literal` off the model and checks the console's
option list against it.

Three things the screen renders rather than summarises: a source's content when
it is there, because *there* means readable — by this platform, by whoever
operates it, and by a lawful request, and a tick saying "stored" would hide
which side of the custody line the account is on; the fine-tune's answer, which
is mostly claims about what did *not* happen (`external_transmission: false`,
`computed: "locally…"`); and the identity signature, which is the one thing on
this screen a stranger can verify — `GET .../embodiment-consistency` needs no
account, so somebody who met the profile through a speaker can check it against
the one they met in a room.

### Screens 162 and 163 — bodies, and where a rated profile is marketed

The last two doorless blocks, and both had a trap that a route signature hides.

**163, bodies.** The native shells already drove the catalogue, the binding and
a command button, so the routes describing what a body has *become* had no
caller anywhere. Three list-shaped things here have almost the same name and
mean different things:

| | is |
|---|---|
| `robot.commands` | what this model of body accepts at all — the buttons |
| `GET /robots/{id}/commands` | the audit log of what it was told to do |
| `GET /robots/{id}/skills` | task modules from a pack, which **extend** the first list |

A screen built from the route names puts the log where the buttons belong, and
it typechecks. Each installed skill's `procedure` is rendered verbatim, because
every one of them names what the body will *not* do — *reminders only: never
dispense*, *companionship, not care, and never a substitute for human contact*
— and that limit is the sentence somebody pointing a robot at a relative needs
to read. `behavior_profile` is drawn beside the dials: pace becomes motion
eagerness, autonomy becomes initiative, assertiveness becomes firmness. It is
the difference between a slider and an explanation.

The steering write takes **`values`**, not `dials` — and the request model
defaults to `{}`, so a body keyed anything else is accepted, ignored, and
answered `200` with nothing changed. There is no error to notice. The only way
to find it is to write and read back, which is what the test does.

**162, rated placement.** An adult-mode profile can be advertised at an adult
venue — a creator platform, a directory — as a link or a printable code. The
feature is only defensible because of one sentence the backend puts on every
venue, rendered verbatim and never paraphrased: *every summon of a rated
profile resolves through QRME's 18+ age wall, regardless of where the QR or
handle was found*. The wall does not travel. Summarising that to "18+" drops
the load-bearing half.

Three more things that were only visible by driving it:

- `scan_url` and `summon_url` are **not** interchangeable — the first is where
  a phone camera lands and what the code encodes, the second is the JSON
  surface for clients. Publishing the wrong one hands somebody a page of JSON,
  so the screen labels both;
- `funnel.chat_rate` is **null, not zero**, until something has got through the
  wall. `(null).toFixed()` is `"0"` in JavaScript rather than an error, so a
  screen that did not check would publish a conversion rate nobody measured;
- taking a placement down **deactivates the beacon rather than deleting it**,
  so a code already printed at a venue stops resolving instead of being
  reissued to point somewhere new. That is the safety property, and the screen
  says it as it happens.

Adding the tab also turned up something only clicking finds: the always-on
agent-lights widget is fixed to the bottom-left corner, **on top of the
sidebar**, and the sidebar had grown long enough that its last three tabs were
underneath it — a click landed on the lights. That is the same fault the phone
layout was fixed for in an earlier round, when the widget covered Home and Chat
and the tabs were reported as broken screens; the desktop half simply had not
grown into it yet. The column now reserves the widget's footprint, and a test
asserts the arithmetic rather than the number.

## Channel 3 — sharing your camera

`qrme/viewfinder.py`, 7 routes, 28 tests, screens **136** and **137**.

Channel 2 lent the profiles an ear. This lends an eye: a live view through the
camera in your hand, for the enormous class of problems where **describing the
thing is the hard part and showing it is trivial**. A mechanic looking at your
engine bay. A plumber watching you point at the joint. An electrician reading
the plate on a consumer unit. A vet watching a dog walk.

JIM-mini's `capture.py` is the still, sealed, asynchronous version of the same
idea, and the difference is the whole module. **A photograph is one framed
moment somebody chose. A live camera is whatever happens to be behind it** —
the rest of the room, the post on the table, the child in the doorway. Somebody
who agreed to *"show you the leak"* did not agree to any of that.

### What is in shot decides the rules, not who is watching

This is the inversion the module is built on. The obvious approach gates on the
viewer — *is it a person or a profile* — and it gets both important cases
wrong. A profile that can see an engine bay is genuinely useful and the stakes
are a car. A real stranger watching a live view of somebody's body is not made
safe by being human.

| in shot | a person may watch | a synthetic profile may watch |
| --- | --- | --- |
| **object** — engine, boiler, board, leak | ✅ | ✅ |
| **document** — paper, a plate, a meter | ✅ | ✅ |
| **place** — a room, a site, a yard | ✅ | ✅ |
| **person** — a body, an injury, how somebody moves | ✅ | ❌ |

The refusal is published by name with its reason, and it points somewhere
useful: a profile watching a body in real time would be making judgements about
it with no examination, no accountability and nobody to answer for being wrong
— and unlike a still, there is no moment somebody chose to send. JIM-mini
reaches the same conclusion from the other direction, where a photograph of a
rash is never handed to an agent.

### The viewer never controls the camera

No remote zoom, no focus, no lens switch, no torch, no capture trigger. **The
person holding the phone points it**, and `viewfinder.NEVER` says so out loud —
a remote party who can operate the camera on somebody's device has something
categorically different from a view, and it is the thing people are actually
afraid of when they decline. A test reads the router and asserts no route looks
like camera control, because the easy way to add a zoom button is a new
endpoint rather than a new argument.

Also never: any other camera on the device, coordinates, a session that starts
without the holder starting it in the moment, and any state where it is running
and not visible on the holder's own screen.

### Ephemeral, capped, and yours to end

It records nothing unless somebody says so. Fifteen minutes by default, **45 as
the ceiling** — long enough to look at an engine properly, short enough that a
forgotten session is measured in minutes rather than a working day. Two to open
and one to close, the shape `sharing.py` uses for a lent skill: symmetric
consent to start makes it a loan, asymmetric consent to end stops it being a
trap. And it dies with the surface, because nobody remembers a permission
granted inside a conversation that finished.

The disclosure is a first-class read rather than something a client assembles,
and it is **not** open to anybody holding the surface id — a room id rides on
printed beacon stickers, and *"who has a camera live in there, and is it
recording"* is exactly what a stranger who scanned one must not be able to ask.
That mistake shipped once in `roommic`.

### Bystanders are the unsolved part, and it says so

Nothing here can tell whether somebody walked into frame. A "bystander
detection" toggle would be **worse than the gap**, because it would be relied
on. So the honest version is a note addressed to the only party who can
actually see the room: *we cannot tell whether somebody has walked into shot,
or blur them if they have; you can look at the room before you start, and stop
the moment it stops being about the thing.*

All three of these — the camera, the lent microphone, the worn overlay — now
share one console door (**158**), because they share one rule: whatever you put
between yourself and the people around you, they are told. The screen renders
the `never` list, the bystander note's *"we cannot see the room"*, and the
refusal when a profile is asked to watch a body, all verbatim. Each is an
argument already made carefully here, and a paraphrase would be a worse version
of it.

Building that door found something worth writing down: **the camera and the
microphone accept different sets of surfaces.** A watch party takes a lent
microphone and refuses a shared camera; a room takes a camera and lends
microphones through its own route. Two vocabularies that look interchangeable
and are not — a single picker built from either one refuses half its own
options, which is what the first version of the screen did.

## Membership

`qrme/tiers.py`, 4 routes, 26 tests, screens **130** and **131**.

Three plans and a doorway below them.

| | | |
| --- | --- | --- |
| **Visitor** | free | read any public page — a scanned beacon needs no account |
| **Free** | **$0** | make your own profiles and your own agent, stored in the clear |
| **Basic** | **$20/month** | the same, sealed in the vault under a key you can hold |
| **Pro** | **$130/month** | everything that leaves your account: the marketplace, connectors, skills, downloads, connections, and every modifier and builder |

**Free and Basic reach identical capabilities, and that is deliberate** —
`includes("free") == includes("basic")`, asserted by test. What $20 buys is
`qrme/storage.py`'s vault posture, not a feature. See *[Where your data
lives](#where-your-data-lives)* below.

**Money here is simulated**, exactly as in `commerce.py` — subscribing writes a
row and moves no real funds, and every response that names a price says so in
its own body. A test asserts nothing in the module reaches a payment processor.
This is the one surface where a tier system would be tempted to look like a
working checkout, which is precisely where somebody would be misled.

**Visitor is a real state, not an oversight.** QRME's whole reach story is a
stranger scanning a printed code and landing somewhere useful. A wall asking
them to subscribe before they could read the page would break the feature the
beacons exist for.

**Enforcement is one table and one chokepoint.** `tiers.GATED` maps a path
pattern to the capability it needs and `tiers.gate` is installed once as an
application-wide dependency, so **no route opts in** — a capability cannot be
added to the product and forgotten at one of its eleven endpoints. The
alternative was a `require_plan(...)` call at the top of every paid handler,
which is the shape this repository has already been bitten by twice: a
docstring claiming a check the code did not make.

That table is checked against the served routes rather than proof-read, and the
first version failed. It named `/steering`, `/governance` and `/licensing` as
prefixes; none is a route here — steering lives at `/profiles/{id}/steering` —
so all three were **paywalls in front of a wall**. They read as protection,
protected nothing, and would have survived indefinitely, because nothing fails
when a pattern matches no traffic. The table is patterns now, not prefixes,
because most paid capabilities hang off a profile.

**Browsing stays open, and that is a decision.** A Basic member may look at the
marketplace and may not list, sell, license or buy. A paywall that hides the
shop from the person you are trying to sell to argues against itself, and the
catalogue is public to strangers anyway — hiding it from paying members but not
from passers-by would be incoherent.

**The refusal is structured, because 402 is already spoken here.**
`POST /packs/{id}/install` answers 402 for *this pack costs money, confirm the
price*. Both are genuinely payment-required, so the status is right for both —
but a client must show *upgrade* for one and *confirm* for the other, and
telling them apart by matching on prose breaks the first time somebody rewords
a message. So a plan refusal carries `reason: "plan"`, what it needs, what you
have, and the price.

**A membership belongs to the account, not the profile.** Per-profile would
mean paying twice to hold two profiles, which is exactly what `identity.py`
exists to let people do for free. Creating a profile enrols a new account on
Basic; an existing member keeps the plan they have, because making a second
profile must not quietly move somebody off Pro. **Cancelling keeps the
profiles** — a lapsed subscription is not a reason to delete somebody's work,
and a product that deleted it is one nobody could safely try.

## Where your data lives

`qrme/storage.py`, 38 tests, screens **138**, **139** and **140**.

There are two postures, and the difference between them is the whole of what
Basic buys.

| | | |
| --- | --- | --- |
| **Open cloud** | Free | the platform's own database, in the clear. The operator can read it, a backup contains it, a subpoena reaches it |
| **Encrypted vault** | Basic, Pro | sealed in PDI before it lands, under a key you can hold yourself, with a tamper-evident chain over every access |

**Free and paid differ in where your data lives, not in what you can do.** A
free tier crippled into uselessness teaches nobody anything about the product;
a free tier that is honestly *not private* teaches somebody exactly what they
are choosing between.

### Who holds it

The other half of the same question, and the one the free plan is really
about. `storage.CUSTODY` names two arrangements:

| | | |
| --- | --- | --- |
| **Platform custody** | Free | QRME holds your work and you have access to it — the familiar hosted-assistant arrangement. It reaches us over ordinary HTTPS, sits in our own database, and never goes through a vault |
| **Your custody** | Basic, Pro | sealed in PDI before it lands, under a key you can hold. We operate the service; we do not hold the contents |

**Custody, not ownership, and the word is deliberate.** A product gets to
decide who *holds and operates* a record. It does not get to decide away
somebody's statutory rights over their own personal data — access,
rectification, erasure and portability survive whatever a plan says, in every
jurisdiction that has them. A tier table claiming "the platform owns your
data" would be claiming something no court would honour, and this repository
does not put claims in tables it cannot keep. `test_custody_is_never_described_as_ownership`
checks the values a user is actually shown.

**The vault gate asks about the plan, not the deployment — and it did not
used to.** Every seal point read `if pdi is not None`, which is whether the
*operator* configured a vault. So a free account on a PDI-backed deployment
had its work sealed into a vault it was not paying for and could not hold a
key to. `storage.vault_for(plan, pdi)` is now the one place that question is
asked, and `test_a_free_account_puts_nothing_in_the_vault` counts writes
rather than reading call sites — because reading call sites is how twenty of
them stayed wrong.

**Writes only. Reads and deletions keep the real vault, always.** Somebody
who was on Basic for a year and moved to Free still has a year of sealed
records: they have to be able to read them back, and erasure has to be able to
purge them. A plan-gated vault on a read strands somebody's history behind a
billing change; on a delete it leaves records nobody can reach and calls that
erasure. Both are worse than the bug the gate fixes, and both are asserted.

**Signing deliberately keeps the real vault whatever the plan**, because a
signer is frequently an *interactor* with no membership at all — gating
`signatures._seal` by their plan returns None and the custody chain a referral
depends on quietly stops being written. That is the same trap that put
`signature` on the sensitive list in the first draft, and it is recorded in
the module so the loop is not closed the tidy-looking way.

**So the disclosure is structural.** `storage.describe()` is carried on every
surface that names a plan — `GET /plans`, `GET /memberships/{id}`, and the body
returned when a profile is created — and `not_private` is a **field**, not a
footnote. A privacy claim that lives in a Terms of Service and not in the
response body is a claim nobody reads at the moment it matters. And the open
posture names its readers rather than gesturing at them: *you, anyone you share
with, the people who operate this deployment, anyone with lawful access to it.*
"Industry-standard security" is what a product says when it does not want to
finish the sentence.

**Some payloads are refused rather than quietly exposed**, and the test for
the list is not *would the account holder mind* — it is **whose exposure is
it**:

- **source material about somebody else.** They did not pick this plan.
- **anything behind the age gate.** Rated content needs the vault.
- **a clinician's written opinion about a real person.** The patient did not
  pick this plan either — and this one reached the open store because the
  referral flow writes through `referral.reply` rather than `add_source`, so
  the third-party rule above, which is the same rule, never saw it. Refused at
  `POST /referrals/prepare`, **before any clinician is contacted**: refusing
  when the note comes back would strand a real person who has already been
  written to, mid-flow, holding words they cannot file.

Both are payloads where the person harmed is frequently not the person who
clicked. Letting free store anything and warning loudly sounds more respectful
of the user's autonomy and is not, for exactly that reason.

The list is short on purpose and holds only what *this* repository can refuse —
`test_every_sensitive_kind_is_enforced_somewhere` fails if a kind is named
here that nothing outside `storage.py` actually checks. The first draft named
`body_image` and `medical`, which are JIM-mini's payloads and unreachable from
here, and a `signature`, which is **not a storage-at-rest risk at all**:
WebAuthn keeps the private key on the device, so there is nothing for an open
store to expose. Gating it also broke signing outright, because a signer is
frequently an interactor with no membership — `plan_of` returned "visitor", the
posture came back open, and every enrolment was refused. A sensitive list
assembled from which words sound alarming is how that happens.

**A hard line is never answered with a price.** A rated profile *of another
real person* is refused at any amount, and the first version checked the
storage posture first — so the response was **402**, telling somebody the line
is a price. It is not. The check now runs after the hard line, and
`test_a_hard_line_is_never_answered_with_a_price` holds the order.

**A downgrade never unseals anything.** Moving from Basic to Free leaves
everything already sealed exactly where it is; only new content goes to the
open store. A billing event that silently declassified a year of somebody's
records would be the worst thing this module could do, so `downgrade_effect`
exists to *state* the rule rather than to perform it — a test asserts it
contains no write at all.

**And an upgrade does not un-expose anything.** Content written in the clear
was in the clear. Sealing it afterwards protects it from here on and changes
nothing about the backups, logs and copies that already exist, and
`upgrade_effect` says so in those words. A product that implied otherwise
would be selling absolution rather than encryption.

## The pane in the corner

`qrme/dock.py`, 5 routes, 34 tests, screens **128** and **129**.

The watch faces answer *what am I currently presenting as* without making you
leave what you are doing, and a fixed screen does the same for a wall. Both need
hardware, and **most people have neither**. The dock is the same answer for
somebody holding only the phone: a small pane in the bottom corner of the app,
with no watch frame around it, that tucks away behind the helper button.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/128-the-corner-pane.svg"><img src="docs/screens/128-the-corner-pane.svg" width="200" alt="The corner pane"></a><br><sub><b>128</b> · tucks away with the helper</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /dock/faces` | the vocabulary, and what it refuses to cast |
| `GET /dock/where/{face}` | the screen that can actually do this |
| `GET /dock/{id}` | where the pane sits, and how it opens here |
| `PUT /dock/{id}` | move it, tuck it, hide it, change its faces |
| `GET /dock/{id}/face/{name}` | one face, as the pane would draw it |

`?surface=` and `?platform=` change how it opens; the stored preference does
not change with them.

  </td>
  </tr>
</table>

**It is the same faces as the wrist, not a new set.** `dock.FACES` is built from
`wearables.FACES` and a test binds the two, so a face added to the watch appears
in the pane or is turned away here **by name with a reason**. Two catalogues of
the same glances would drift, and the one nobody re-reads wins.

**It shows, and it routes. It never acts** — the exact inversion of the watch's
one exception, and the inversion is the point. Watch face 05 can *end* a lent
microphone, because the watch is the device doing the listening and a permission
you cannot revoke from the thing running it is not really yours. Nothing here is
the device: the real screen is one tap away in the same app, so a control in the
pane buys nothing and costs something, because this thing floats over live
video. A button that ends a stream sitting a thumb's width from the one that
pauses it is a mis-tap on somebody's broadcast. So `control` is the one wrist
face the dock refuses, and every face carries a **route** instead.

**It is inside every screenshot.** `displays.NEVER` exists because a wall is
read by whoever walks past; `dock.NEVER` exists for a different reason that
lands in the same place — a pane pinned to the app frame is captured by every
screenshot, every recording and every screen share, *including the one being
broadcast right now*. So no message bodies, no memory, no agent names, no viewer
names; and on a surface that is going out it opens **tucked** however the
preference is set. Capped rather than overwritten, in the same shape as
`roommic`'s gain: the preference is returned alongside as `wanted`, so the
settings screen and the pane cannot disagree about what was chosen.

**The bottom corner is a constraint, not a taste.** The top-left carries whose
surface this is and the top-right the recording light, so a pane that could
cover either could hide who you are watching or whether you are live. Both
entries in `dock.CORNERS` are at the bottom; the second exists because
bottom-right is a right-hander's default.

**On the desktop it replaced something rather than joining it.** That corner
already held a pinned agent-lights panel with no way to put it away — three
quarters of this feature, missing a lid. It is now the dock drawn open on the
`agents` face, which is why `DEFAULT_STATE_ON["desktop"]` is `open` where the
phone's is `handle`: a desktop user has no wrist to glance at, and amber and red
are the states nobody thinks to go looking for. Adding a second floating box
beside the first was the alternative, and it is what you get by not looking.

### Asking where something is

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/129-where-is-it.svg"><img src="docs/screens/129-where-is-it.svg" width="200" alt="Where is it"></a><br><sub><b>129</b> · directions, not a description</sub></td>
    <td width="66%" valign="top">

*"Where do I change my background"* is the question the help box got most and
answered worst: a correct paragraph **about** backgrounds, handed to somebody
who was asking where they live.

`help.DIRECTIONS` is keyed by tutorial lesson, so the directions cannot name a
screen the walkthrough does not cover, and a test asserts **every lesson is
reachable by some phrasing**. The phrases are what people type — somebody
looking for overlays types *change my face*; nobody types *overlays*.

  </td>
  </tr>
</table>

The answer names the screen, and says so out loud when the same thing is also a
face on the pane — read from `dock.ROUTES`, the one table both use, so the
assistant and the corner cannot disagree about where a feature lives. Matched
before `TOPICS` and before any model, because both would have described the
feature instead, and a model cannot know the screen numbers.

The order is refusals, then the walkthrough, then directions. *"Where do I
start"* is a request for the tour; *"where is the game lobby"* is a request for a
screen; *"pretend you are my friend"* is neither, and is still refused first.

## Friends you might know

`GET /profiles/{id}/friends/suggested`. Ranked on friends in common and
subjects you both work in, each carrying the reason in words — the same posture
as the feed, because a friend suggestion is a claim about a person and one
nobody can explain is one nobody can argue with.

Two exclusions matter more than the ranking. **Anyone already on your list, in
either state** — somebody who removed a friend does not get them handed back as
a suggestion tomorrow, which would be the same imposition the founder pins
avoid, wearing a recommendation badge. And **the founder pins**, who are on
every list by construction and would otherwise top every suggestion set on the
platform.

Never ranked on source material, memories or anything vaulted: an introduction
built from somebody's private writing would be the platform reading a diary to
make it.

## The community wall, and the feed

A profile publishes to its wall (`POST /profiles/{id}/wall`); other people see
some of it in their feed (`GET /profiles/{id}/feed`). Publishing is the easy
half. The feed is where the decisions are.

**Likes, comments and shares are not new.** The audience layer already carried
those four verbs against a `(kind, id)` pair, and `post` is now one of its
target kinds — so a like on a post is the same row shape, and the same
`UNIQUE (target, actor)`, as a like on a profile. No parallel tables, and none
of the drift a second set would have grown within a round.

**Every post says why it is in front of you.** Each entry carries a `reason` in
plain words — *a friend posted this*, *you have talked to this profile*,
*popular with people here*. A ranked feed that cannot explain itself is one
nobody can audit, including whoever wrote it, and the explanation costs a
string. `GET .../feed` also returns its own weights, so the ranking can be
argued with rather than merely accepted:

| signal | weight | |
| --- | --- | --- |
| a friend posted it | 100 | you chose to stand with them |
| you have talked to the profile | 60 | you were actually there |
| tags you engage with | 25 | it works in something you follow |
| likes | 2 each, **capped at 40** | popularity contributes, it does not decide |
| recency | up to 10 | a tiebreak, not the ranking |

The cap is the interesting one. Uncapped, a single heavily-liked stranger
outranks every friend you have — which is the failure mode people actually
complain about, and a test pins it.

<table>
  <tr>
    <td align="center" width="40%"><a href="docs/screens/87-for-you.svg"><img src="docs/screens/87-for-you.svg" width="230" alt="For You"></a></td>
    <td valign="middle">

Every row on the feed screen carries its reason and its score, and the last row
says what the ranking will never look at. Desktop view **10 · Community** puts
the friends list beside the feed with a full *why it is here* column — the one
thing a wide window does that a phone cannot, and the reason a ranked feed you
can read the reasoning of all at once is one somebody can argue with. That is the screen doing the same job
as the API: a feed you cannot interrogate is one you have to take on trust.

  </td>
  </tr>
</table>

**A post can promote something.** `listing_id` attaches one of the profile's
own marketplace listings — a reference, not a copy, because a price written
into a post is a price that goes stale the moment the listing changes and
nobody edits the post. A profile can only promote its own listings.

**The feed is on the homepage too.** A page showing what you made and nothing
of what anyone else is doing is a business card; the reason people sat on their
MySpace page was that it was also where the day's news arrived. Six entries,
ranked for that profile by the same rules — a page is somewhere you arrive, and
the endless version lives on its own screen.

**Moderation runs on the way in and on the way out.** Every post passes the
same filter as a chat turn; a blocked one is kept, returned to its author with
the reason, and invisible to everyone else. On the way out, an adult profile's
posts are walled out of an ordinary feed — a gate inherited from the *author*
rather than judged per post, because otherwise an adult profile publishes past
its own wall by writing something innocuous.

## The stream — one card at a time, and who is allowed to play

The wall's feed above is *yours*: ranked for one profile, explained row by row.
The **stream** is the other kind — one public card filling the screen, swipe
for the next, and the next. `GET /feed` and `GET /feed/{id}`, both readable
without an account, because somebody who followed a link from a sticker on a
shop window is a reader like any other.

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/189-feed.svg"><img src="docs/screens/189-feed.svg" width="210" alt="Feed"></a></td>
    <td align="center" width="33%"><a href="docs/screens/190-what-plays.svg"><img src="docs/screens/190-what-plays.svg" width="210" alt="What Plays"></a></td>
    <td align="center" width="33%"><a href="docs/screens/191-rooms-desks.svg"><img src="docs/screens/191-rooms-desks.svg" width="210" alt="Rooms &amp; Desks"></a></td>
  </tr>
</table>

**The rule the stream had to not break.** `post_videos` in `qrme/db.py` has
carried the same comment since long before a stream existed: *the link and the
id, never the file and never a thumbnail* — re-hosting somebody's video is a
copyright problem, and a cached thumbnail is a copy of an image nobody granted.
It is why a QRME wall renders without one request to YouTube.

An endlessly autoplaying stream is the one surface where that promise is
expensive to keep and cheap to lose. Flick past fifty cards and, done the
ordinary way, you have announced your address and your taste to fifty companies
for footage you never chose to watch.

    asked     does the stream play the next thing
    mattered  does swiping past something tell a stranger you were here

So the line is drawn on **who holds the file**, and it is drawn on the server
rather than left to four clients to remember:

| the file is | `plays` | what the card is |
| --- | --- | --- |
| held by this deployment (`media`, `kind='video'`) | `true` | it plays, and it loops |
| held by somebody else | `false` | a title, a platform name, a link — and no request until you press |

`test_an_offsite_video_never_plays_by_itself` asserts that on the wire, where
every client reads it, rather than in any one of them. It is easy to satisfy
today and easy to lose the day a console decides autoplay is a nicer default.

**Every fourth card is a place with a person in it.** This is the part a video
app cannot do. Mixed into the recordings are **live rooms you can walk into**
and **desks with a real human behind them**, with the shop behind the desk
reachable without leaving the stream — browse it, see the prices, ring the
bell. Both carry a plain sentence *before* the button, because both reach
somebody:

> Walking in puts you in the room with the people already there. Your
> microphone is off until you turn it on.

> Ringing reaches a person. Otis is at the desk — the bell is not a message,
> it is somebody's attention.

**Nothing is in the stream by default.** A post reaches it only if it is on the
wall and approved; a desk only if it is not closed; a room only while it is
active **and** attached to a desk that chose to be found — a room with nobody's
desk behind it is a private conversation and is not in this stream at any
ranking. A rated desk is *absent* for a reader who is not verified rather than
blurred, and a shared link to one answers `404` rather than `403`, because a
403 announces that the thing exists.

And every card says why it is there, the same as the wall's feed does. A stream
that cannot explain itself is one nobody can audit, including whoever wrote it.

**On all four clients.** The stream is on the web console, on the iOS, Android
and Windows shells, and reachable from JIM-mini's Feed tab. The phones read the
same two routes and render the same `plays`, and the fourteen `feed.*` strings
are the console's own rows copied into the three native tables so the desktop
and the phone cannot drift apart on a surface new to both.

What the phones do not have yet is the **gesture** — Previous and Next are
buttons there. That is stated in each screen's own docstring rather than
implied away, and it is not only a matter of effort: a stream a person can use
only by dragging is one somebody with a motor impairment cannot use at all, so
the buttons are the version that works for everybody while the swipe is built.

## Agreeing before work changes hands

Somebody comes up as a guest on a desk and it turns into business — they will
build something, review something, hand over a file. The moment that happens
two strangers are about to send each other things, and the interesting part is
not the sending. It is the **agreeing**, because that is where every dispute
comes from and the one place a platform can actually help.

So an exchange (`qrme/exchange.py`, `POST /exchanges`) is a document before it
is a transfer. One side proposes; the document names, item by item:

* **what goes across, in each direction** — every artifact with its kind and
  its size, so *what am I about to receive* is a list rather than an assurance;
* **what the work is**, in one sentence, and which of sixteen industries it
  belongs to — this is a business agreement in any trade, not a software
  feature the other trades are allowed to borrow;
* **what is included when it is finished** — the clause people actually argue
  about afterwards;
* **what is not included**, said out loud, because an absent exclusion reads as
  an inclusion to whoever paid.

Then both sides sign, and only then does anything move. Four rules make that
more than a form.

**Neither signature alone opens anything.** `GET /exchanges/{id}/channel` —
the one call a transport layer should ask — reports `open: false` until both
parties have signed. A one-sided agreement is not an agreement.

**Any change to the manifest voids both signatures** (**113**). This is the
rule the whole design turns on: without it you agree to a two-item manifest and
the other side appends a third, and your signature sits on a document you never
read. Signatures are stored against a **fingerprint of the agreement**, not
against its id, which makes that a fact about the data rather than a promise
about the code — after an edit the old signatures match nothing. In practice
the guarantee is stronger still: the document freezes the moment *anybody*
signs, so the only route to an edit is `reopen`, and that deletes the
signatures on its way past. A signature here is either current or absent;
there is no way to make a stale one.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/112-the-agreement.svg"><img src="docs/screens/112-the-agreement.svg" width="200" alt="The agreement"></a><br><sub><b>112</b> · the manifest, before anyone signs</sub></td>
    <td align="center" width="33%"><a href="docs/screens/113-signatures-cleared.svg"><img src="docs/screens/113-signatures-cleared.svg" width="200" alt="Signatures cleared"></a><br><sub><b>113</b> · one item added, both signatures gone</sub></td>
    <td align="center" width="33%"><a href="docs/screens/114-delivery.svg"><img src="docs/screens/114-delivery.svg" width="200" alt="Delivery"></a><br><sub><b>114</b> · accepted one at a time</sub></td>
  </tr>
</table>

**Nothing downloads by itself** (**114**). A signed exchange makes each item
*available*; the receiving side accepts them one at a time, and only the
receiving side can — the sender cannot accept on their behalf. Consent to an
agreement is not consent to a file landing on your disk. Items that **run** —
`source` and `build` — are flagged as such on the manifest and again at
acceptance, because a signature on an agreement is not a review of what the
code does.

**It grants no access to anybody's device**, and that limit is in the code
rather than in a warning. An exchange moves named artifacts somebody attached;
it opens no session, runs nothing, and reaches nothing that was not listed.
Hooking one machine up to another is a different feature with a different
threat model, and shipping it quietly inside a file-sharing agreement would be
the wrong way to arrive at it.

The console reaches all of it (**153**): propose, list what crosses, sign,
and accept item by item. The screen re-renders the whole agreement from every
reply rather than patching what is already on it, so an edit that clears the
signatures is something you watch happen rather than something you are told
about afterwards.

## Lending a skill, in any room you are both in

Two people are in the same place — a room, a live desk, a watch party, a
connection, an agreed piece of work — and one of them has something the other
needs. A finance pack. A robot's task modules. A profession. A language pair.
`qrme/sharing.py` (`POST /skill-grants`) lends it, and the same mechanism
covers every one of those surfaces rather than five near-copies of it.

The whole feature is the word **both**, and the shape it takes is deliberately
lopsided:

> it takes two to open a grant, and one to close it.

Symmetric consent to start is what makes it a loan rather than a taking.
Asymmetric consent to end is what stops it becoming a trap — somebody who has
changed their mind should not need permission from the person benefiting to
change it back. A consent model that needs *both* sides to stop is one that
cannot be withdrawn under pressure, which is exactly when withdrawal matters.
Either party closes it alone, and the record says which of them did.

**A skill is used, never handed over.** The borrower may invoke it while the
grant stands; they get no copy, no install and no licence. Packs here are
bought, licensed and attributed to publishers, and a lending feature that
quietly duplicated them would be a piracy tool with a consent dialog on the
front. The permission is checked at the moment of **use**, not at the moment of
grant, so closing a grant stops the next call rather than merely preventing new
grants.

**A grant lives in one place and dies with it.** Lending your expertise in a
watch party does not follow the borrower into a private message — a skill lent
in one surface is refused in another, by name. Ending the party or withdrawing
the exchange closes what was lent inside it, and that teardown is wired at the
point the place ends rather than left to a caller to remember, because the
thing forgotten would be a live permission with nothing left to justify it.

**Every use is written down, and the lender reads it.** *Both parties choose*
is a slogan unless the person lending can see what was done with it. The log is
the reason a grant is worth agreeing to: you can watch it being used and stop
it mid-sentence.

| | |
| --- | --- |
| where | `room` · `desk` · `party` · `connection` · `exchange` — no "everywhere", and no "my account" |
| what | `pack` · `robot_task` · `profession` · `language` · `workflow` |
| to open | both, and only the person it was offered to may accept |
| to close | either, alone |
| transferred | nothing |

The console door (**154**) is arranged around the asymmetry. The button that
ends a grant is never disabled by which side you are on, because the moment
withdrawal matters is exactly the moment the other party would not agree to it.
The use log is shown to both of you: a record only one side can read is not a
record.

## Who these surfaces think you are

An exchange, a lent skill and a watch party all name the acting party in the
request body — `actor_id`, `host_id`, `borrower_id`. **An id in a body is a
claim, not a fact**, and `common.require_self` is what turns it into one: the
token presented has to belong to the person the body names.

That check was missing when those three shipped, and the gap was total. An
anonymous caller could forge *both* signatures on somebody else's agreement,
open its channel, and accept delivery of an executable on their behalf; accept
and use a skill somebody lent to a third party; or seize the scrubber in a
watch party by passing the host's id. Every consent property the three modules
describe rested on a check that did not exist — the modules were right and the
doors were open.

| surface | who may act | who may read |
| --- | --- | --- |
| an exchange | the two parties, each only as themselves | the two parties — a manifest names somebody's files, their sizes and what the work is worth |
| a lent skill | the lender offers; the borrower accepts, declines and uses; either closes | the two parties, plus the borrower's own view of the log kept about them |
| a watch party | the host seeks and ends; a member speaks only as themselves, or as a profile they own | members only |

Two details worth stating because they are easy to get subtly wrong. Bringing a
**synthetic profile** into a room speaks in its voice, so it is its owner's call
and nobody else's. And the surface listing was narrowed: it was meant to be
"what the room can see about itself", but there is no room-membership check to
hang that on, and without one it listed who was lending what to whom to anybody
who guessed the id. It now shows the caller's own grants, and says so.

`tests/test_two_party_auth.py` holds all of it. Each case is asserted twice —
once against an anonymous caller and once against **a valid token belonging to
the wrong person**, because a test that only tries the first passes against a
system that accepts any logged-in user as anybody.

## How many people it is talking to

A synthetic profile talks to many people at once by construction. One process,
many conversations — that is what the thing *is*, not a flaw in it.

The harm was never the multiplicity. It is the **discovery**: somebody who has
been talking to a profile for a month and then finds out — by asking, or by
accident — that there were thousands of others has not learned a new fact so
much as learned that the fact was available the whole time and nobody offered
it. That gap is entirely the product's doing, and closing it costs a count and
a sentence.

So `GET /profiles/{profile_id}/attention` is **public and needs no token**,
answering with the number of distinct people this week and altogether, and one
plain line. Making somebody get an account before they may learn it would be
the same withholding with a form in front of it, which is why the count lives
on the accountless screen next to the objection form and the mark check — on
the console and on all three phones.

Three things it deliberately is not, and they are **fields rather than prose**
so a screen renders them beside the number instead of composing a reassuring
sentence of its own:

| | |
| --- | --- |
| `ranks_people: false` | there is no order and no leaderboard |
| `has_a_favourite: false` | *"you're my favourite"* is a lie the software cannot make true — and it hands somebody something to lose, so the day the count goes up they lose it |
| `names_anybody: false` | the count is a fact about the profile; who the others are is a fact about **them**, and none of them agreed to be counted out loud to a stranger |

The last one is greppable rather than promised: `test_no_query_here_can_return
_a_name` reads the SQL in `qrme/attention.py` and fails any statement that
selects a column instead of counting rows. A viewer may ask *am I one of them*
— about their own id, and only their own.

Nothing here models jealousy, and nothing invites it. A product that
manufactures the feeling in order to resolve it has manufactured the feeling.

## Watch parties, and a profile that has not seen the video

A watch party (`qrme/watchparty.py`, `POST /watch-parties`) is a posted video
plus everyone who turned up — and on this platform that includes **synthetic
profiles**, which is where the honesty problem is.

**A profile has not seen the video. It cannot.** Nothing here fetches it,
nothing transcribes it, and a profile saying *"the bit at four minutes was
great"* would be fabricating — the most ordinary-looking lie this product could
tell, and the one nobody would think to check. So
`GET /watch-parties/{id}/context` hands a profile only what exists on this
side: the title the poster typed, the platform, where the room has got to, and
what the humans have said. `description_available` and `transcript_available`
are both `false`, and it says so in the prompt, in the second person:

> you have not watched this video and cannot see it. Talk about what the others
> in the room are saying and about what the video is titled. If somebody asks
> what you thought of a moment in it, say you have not seen it rather than
> inventing one.

Starving a model of context and hoping is not a safeguard. Telling it the truth
about its own position is.

**The room shares a position, not a player.** The host moves a number and
everyone follows; it does not press play on anybody's device. That is what
keeps the embed promise from being broken twenty times at once — a party that
pre-loaded the video for twenty people would have made twenty requests to
YouTube nobody agreed to. **Only the host** moves it, because otherwise the
last person to scrub decides what the room is looking at.

Every member carries `synthetic: true|false`. A room where you cannot tell
which of the six names is a person is the room this platform exists not to
build. Party chat is moderated like every other utterance, a party with a minor
in it runs strict, and a party can only be opened on an **approved** post —
otherwise it would be a way to put a video in front of people that the wall
refuses to show them.

The console shows that instruction verbatim (**155**), in a panel of its own.
A person whose profile is sitting in a room discussing a film can read exactly
what it was told about not having seen it, rather than trusting that it was
told anything.

## The page you make yourself

Every profile already had a **front page** — portrait, skills, experience,
rating — assembled from what the platform knows. It is useful, and it looks
exactly like everybody else's, because a generated page is the same page 34
times.

This is the other kind: `GET`/`PUT /profiles/{id}/page`. A theme, an accent
colour, a tagline in your own words, a paragraph about yourself, and a **Top 8**
— the friends you want at the front, in the order you want them. It is the
MySpace idea, and the reason it is worth reviving is not nostalgia on its own: a
page somebody arranged tells you what they thought was worth putting first,
which is the one thing a generated page cannot.

<table>
  <tr>
    <td align="center" width="50%"><a href="docs/screens/85-my-page.svg"><img src="docs/screens/85-my-page.svg" width="230" alt="My Page"></a><br><sub><b>85</b> · the page, in its own colours</sub></td>
    <td align="center" width="50%"><a href="docs/screens/86-customise.svg"><img src="docs/screens/86-customise.svg" width="230" alt="Customise"></a><br><sub><b>86</b> · the editor behind it</sub></td>
  </tr>
</table>

Six themes — Midnight, Starfield, Sunset, Chrome, Meadow, Paper — a validated
`#rrggbb` accent, and three layouts.

Three things it deliberately does not do:

**Real HTML, through an allowlist.** You write your own markup — that is the
thing anybody actually remembers about a MySpace profile — and every tag and
attribute goes through [`qrme/markup.py`](qrme/markup.py) before it is stored.

Raw markup is not a stylistic objection. In October 2005 the **Samy worm** used
exactly this feature: script smuggled through a profile, executing in the
browser of everyone who viewed it, a million friends in about twenty hours, and
the site taken offline. The nostalgia is worth reviving; that is not.

| in | out |
| --- | --- |
| `<b> <i> <u> <marquee> <center>` and 30 more | kept — including the 2004 ones, which cannot execute |
| `style="color: …"` and 30 visual properties | kept |
| `<script> <iframe> <object> <form> <svg>` | removed, content and all |
| `onclick`, `onerror`, every `on*` | removed — this is where injection actually lives |
| `javascript:` and `data:` URLs | removed; only http, https, mailto, fragments and site-relative paths survive |
| `//host/path` | removed — protocol-relative, so it looks like a path and fetches from another host |
| `@import`, `expression()`, `behavior:` | removed |
| `background-image: url(…)` | **kept** — held to the same URL check as `<img src>`, because a background is most of what decorating a page means |
| `position`, `z-index` | removed — they lift an element out of the page's own box |
| an unknown tag | dropped, **its words kept** — eating somebody's writing looks like a bug |

Sanitised **on the way in**, so there is exactly one moment unsafe markup could
exist rather than one per renderer, each of which could forget. What was
stripped comes back as `html_removed`, so an editor can say *your `<script>` was
dropped* instead of quietly returning a page that does less than its author
wrote. `GET /pages/themes` publishes the allowed tags and properties so an
editor can grey out what it knows will be lost.

**The chat overlay in a live room is transparent** — circular faces on a soft
scrim over the video, rather than a comment panel taking a bite out of the
picture people came to watch (**89**). The screens round their own avatars; the
baked bubbles in `docs/portraits/bubbles/` exist for the README, which cannot
draw one because GitHub strips the `style` that would round an `<img>`. Using
the pre-baked file in the app would put a bubble inside a bubble.

**Like, comment and share work on a post**, because `post` is an audience
target rather than a parallel system — the same rows, and the same
`UNIQUE (target, actor)`, as a like on a profile. A test now walks every kind
in `TARGETS` through `share_url`, because sharing a post raised `KeyError` at
the moment somebody pressed the button: the kind was added to the target list
and its share URL was not.

**A post can carry a video from somewhere else** — YouTube, Vimeo, Twitch,
Dailymotion, Rumble (`qrme/embeds.py`, `POST /profiles/{id}/wall` with
`video_url`, and `GET /videos/platforms` publishes the list). Three decisions
make that safe to do here rather than merely possible.

*Nothing is copied.* What is stored is the platform, the video's id on it, and
the title **the poster typed** — never the file, never a scraped title, never a
downloaded thumbnail. Re-hosting somebody's video is a copyright problem and a
cached thumbnail is a copy of an image nobody granted. The video stays where its
owner put it, on the terms its owner agreed to.

*No third-party request until the viewer asks for one.* This is the part that
matters on a platform whose promise is that data does not leave a vault. A
normal embed loads the other company's player the moment the page renders,
which tells them you looked **before you decided to**. So what renders is a
**facade** — the platform's name, the poster's own words, and a play control,
all served from here. Pressing play is when the request happens, and the viewer
is told so in words before they press it. A privacy promise that holds only
until an embed loads is not one. The empty plate on **95** is the feature, not a
gap in the mock: drawing a YouTube thumbnail there would have been the prettier
picture and a picture of the thing the code refuses to do.

*The allowlist is a list, not a pattern.* Anything not on it is refused by name,
because "looks like a video URL" is how an open redirect becomes a feature. Each
platform knows how to recognise its own links and how to rebuild a canonical
watch URL **from the id** rather than from the pasted string — so a tracking
parameter, a redirect, or a lookalike host cannot ride along into what gets
stored and later opened. A Twitch *channel* link is refused too: it points at
whatever happens to be live, which is not the thing anybody posted.

The age gate is inherited rather than re-judged. A video post is a post, so it
already carries its author's rating through `audience.is_rated` and is walled
out of an ordinary feed by machinery that was already there. Nothing here claims
a video is *suitable* — a platform's own rating is not visible from a link, and
the poster's rating is the only claim this system is in a position to make.

**A storefront, not a second copy of one.** `show_offers` surfaces the
profile's own marketplace listings on the page, read from `listings` rather
than retyped — a second copy of a price is a second price that can be wrong —
and `links` carries up to twelve outbound links under the same URL rule.

**The Top 8 does not reorder the friends list.** It features friends rather than
creating them — a profile you are not connected to is refused — and it is a
showcase, not a second source of truth. Your Top 8 is what you chose to put
first; your friends list is who you stand with.

**About-me text is moderated like anything else written for other people to
read.** A blocked one comes back to its author with the reason and is invisible
to visitors, which is the shape the audience layer already uses for a comment.

The editor (**157**) lists the surviving tags *before* you write, which is what
`/pages/themes` published them for — the backend's own comment says "so an
editor can grey out what it knows will be stripped, rather than letting
somebody write it and lose it", and until now nothing read them. It also shows
`html_removed` after a save, because the save succeeds either way: without it,
a `<script>` disappears and the page simply does less than its author wrote.

## Friends, and the two who come as standard

Profiles have **friends lists** — a profile ↔ profile graph, which is a
different thing from the `relationships` table that has always been here. That
one records how a profile treats an *interactor*: the person typing at it, and
the tone and boundaries that follow. This is the other axis, and it is the graph
the community surfaces are drawn from.

<table>
  <tr>
    <td align="center" width="40%"><a href="docs/screens/84-friends.svg"><img src="docs/screens/84-friends.svg" width="230" alt="Friends"></a></td>
    <td valign="middle">

**Directed, not mutual.** Befriending writes one row. A friends list is a claim
its owner makes about who they stand with, and a mutual edge would mean somebody
else's action edits your list. Two rows make it mutual, and the API reports
`mutual` per entry.

**Two founder profiles stand at the top of every list**, fixed: they cannot be
removed and cannot be pushed below a chosen friend. Everything else in the list
is entirely the owner's to add and drop, and an ordinary friend removes
normally.

**Position is computed, never stored.** The pins are first because their rows
say `origin='founder:N'`. A stored position has to be rewritten on every insert,
and it is the thing that is wrong on the day the founder turns up third.

  </td>
  </tr>
</table>

The list marks pinned rows with `pinned: true`, so a client renders them without
a remove control rather than offering one that returns `409`.

### Two profiles, one person

David Bianchi — 42, CEO and Imagineer of Private Data Infrastructure Systems,
and the person who built all three of these products — has **two** profiles
here, and the split is the point rather than a duplication.

| | `@david_bianchi` | `@david_bianchi_ai` |
| --- | --- | --- |
| **Picture** | a photograph | an AI rendering |
| **Served from** | `/photos` | `/portraits` |
| **Mark in the pixels** | **no** — the photograph is authentic | **yes** — burned in, top-right |
| **Profile labelled AI** | yes | yes |

A platform whose entire argument is that a synthetic thing must say so cannot
have its owner running one profile that is ambiguously both. So there are two,
and each is honest about what its picture actually is. The real person takes the
plain handle; the rendering is the one carrying the qualifier.

**The photograph is deliberately not marked.** The mark says *AI-generated
synthetic media*. Stamping that on a real photograph is a false statement — in
the opposite direction from the one the mark exists to prevent, but false all the
same. `avatars.render()` reports `asset_marked: false` for it, which is the
signal every surface uses to composite the profile's own AI badge. **The picture
is authentic and the profile is synthetic, and those are two different claims.**

That is also why photographs live under `/photos` rather than beside the
portraits: `/portraits` means *burned and checksummed*, and its manifest check
walks every file in the tree. An unburned file there would either fail that check
or force it to be loosened.

Neither profile is in the starter collection or in `avatars.BRIEFS`. Both promise
invented people in their own docstrings, and a real person in either list would
quietly make a documented claim false.

## Anonymous, several, and exactly one verified

Three things a person is allowed to be here, and `qrme/identity.py` is the
tension between them.

**You may be anonymous.** Not everyone can afford to put their name on what
they think, and a platform that only works for people with nothing to lose is a
platform for a narrow set of people.

**You may hold several profiles.** A person is not one thing — the work self,
the hobby, the one for the support group nobody at work knows about. These are
not sockpuppets; they are the ordinary shape of a life, and forcing them into
one identity is its own kind of exposure.

**Exactly one of them may be verified.** This is the rule the other two need in
order to be safe rather than merely permitted.

<table>
  <tr>
    <td align="center" width="34%"><a href="docs/screens/118-stay-anonymous.svg"><img src="docs/screens/118-stay-anonymous.svg" width="200" alt="Stay anonymous"></a><br><sub><b>118</b> · what we withhold, and what we can't</sub></td>
    <td align="center" width="33%"><a href="docs/screens/119-your-profiles.svg"><img src="docs/screens/119-your-profiles.svg" width="200" alt="Your profiles"></a><br><sub><b>119</b> · as many as you like · one verified</sub></td>
    <td width="33%" valign="top">

| route | does |
| --- | --- |
| `GET /identity/vocabulary` | the three rules, in the words a screen can show |
| `GET · PUT /profiles/{id}/anonymity` | what it hides and what it can't · turn it on or off |
| `GET /profiles/{id}/badge` | the badge a **reader** sees |
| `GET /profiles/{id}/verifiable` | could this one take it, and if not why |
| `POST /profiles/{id}/verification` | claim it, once per person |
| `POST …/verification/move` | move it to another of yours |
| `GET /profiles/{id}/siblings` | your roster — **owner-only** |

  </td>
  </tr>
</table>

**Why one badge.** Verification is not a quality score or a reward for being a
good citizen. It is the sentence *this is that particular real person*. Said of
two profiles at once it is either false of one of them, or it is a statement
that one human being is two authenticated people — which is precisely the
primitive verification exists to deny to everybody else. A platform that hands
it out per profile has not verified anybody; it has sold a badge.

**The badge moves rather than multiplies.** One at a time, not one forever.
People change which face is their public one, and a rule that could only be
satisfied by deleting a profile is a rule they would answer by lying instead.
The record moves whole — level, attestor, method, evidence and the date it was
checked. `checked_at` is deliberately *not* re-stamped: a document seen in 2019
is not a document seen today because the badge changed seats.

**A fictional profile is unverifiable, not unverified**, and never consumes the
slot. `verification.status` already draws that distinction; getting it backwards
here would let an invented character lock a real person out of their own badge.

**The founder is the worked example.** `@david_bianchi` and `@david_bianchi_ai`
are the same human being, so only the photographed one carries the badge — the
seed used to verify both, which had the platform asserting that one man was two
verified people, on the deployment that ships as the demonstration of the rule.
The badge belongs to the photograph because a real person whose picture is
authentic is exactly what it is a claim about; the rendering carries the AI mark
instead, which is the claim that is true of *it*.

**One person means one owner account**, because that is the unit this platform
can observe. `same_identity_elsewhere` closes the part that is visible — the
same attestor vouching for the same evidence under a second account — and
nothing closes the rest. That limit is stated rather than papered over: a
`self_asserted` level carries no attestor and no evidence, so there is nothing
on the bottom rung that could tell two people from one. It is why the rung
exists and why the badge carries its caveat.

### Anonymity had to become a property

`anonymous` was honoured by every surface that *rendered* a profile — the
front-page card, the landing page, the prompt, the watermark — and by the route
that returned the profile, not at all. `GET /profiles/{id}` is public, and it
handed over `display_name` in full. The shortest way past anonymity was to ask
for the profile.

`owner_id` was the worse half, because it does not undo one profile's anonymity
— it undoes all of them at once. Two anonymous profiles sharing an account are
the same person, and anyone could read that field off both and match them, then
read it off the *named* profile beside them and put a name to the pair. It is
now withheld from everyone but the owner on **every** profile, named ones
included, along with `successor_owner`, which is somebody else's account id and
was never a visitor's business either.

**The roster is the dangerous read.** `GET /profiles/{id}/siblings` is the one
call that links a person's profiles to each other, which is exactly the tool for
stripping the anonymity off all of them at once. It is reached through a profile
whose owner token the caller holds, and the account is derived from that — never
taken from the path. A route keyed on `owner_id` would hand the roster to
anybody who learned one, and an `owner_id` is a string somebody chooses, not a
secret. Every anonymity guarantee above is worth exactly what that check is
worth.

**An anonymous profile has a name, and cannot choose it.** Every one of them
used to be called *"anonymous persona"* — identically — which is unusable the
moment two are in the same place: three anonymous people in a room were three
identical labels, so you could not follow who had said what and nobody could be
held to anything they said. **Pseudonymity is a stable name without a real one**,
not the absence of a name. So each gets `Anonymous 41338025`, and three
properties make it work:

- **Derived, never stored.** There is no column, so there is nothing to edit —
  which is what "cannot be modified" has to mean in a system where an owner can
  `PATCH` their own profile. A *chosen* anonymous name would be a free text
  field on the one surface built to withhold identity, and somebody would put
  their real name in it within the hour.
- **Keyed on the profile, never on the account.** The one that would quietly
  undo the `owner_id` redaction above: a person may hold several anonymous
  profiles, and numbering them from the account would give them all the same
  name and match them to each other in public.
- **Hashed, not sequential.** A counter publishes signup order and, from two
  samples, the platform's growth rate. Neither is the profile's to give away,
  and *"Anonymous 7"* is a claim about how early somebody arrived.

Turning anonymity off and back on returns the **same** number, because it is
derived from the profile rather than issued — one that changed would make
somebody a stranger to the people who knew them.

That decision used to be made in **fifteen places** — the front page, the
landing page, the prompt, the watermark, the summon card, the beacon page, the
room roster, the profile route, the export — each with its own copy of
`"anonymous persona" if anonymous else display_name`. A rule with fifteen
implementations is one merge away from having sixteen, and the sixteenth is the
one that prints somebody's name. It is now `identity.shown_name()`, and a test
parses every module to assert nobody has written a sixteenth.

**And it can say what it does, without saying who it is.** The plain
silhouette was every anonymous profile's only face, on the argument that a
distinct picture would be a stable mark following one person around. That
argument died with the fixed name — `Anonymous 41338025` is already stable and
already public, so an emblem adds no correlation the name does not, while a
nurse answering health questions looking identical to a troll is a real cost
paid for nothing.

So there are **sixteen field emblems**, one per industry the platform already
models (`exchange.INDUSTRIES`) — not a new vocabulary invented for pictures: a
field somebody can *work in* is a field they can *signal*. Each keeps the same
silhouette with the field glyph badged on, so "anonymous" is what reads first
from across a roster, before anybody parses which symbol it carries.

**Or their own picture.** The emblems are a shortcut, not a fence. This was
briefly a *closed* list, on the reasoning that a profile able to attach any
image could attach its owner's face and nothing here can look at a file and
tell. True, and the wrong conclusion — it made the feature useless to the
locksmith who wants a photo of their own workbench, and bought no safety,
because somebody set on publishing their face can put it in a post. **A limit
that stops the honest use and not the risky one is decoration.**

So what the platform cannot check, it says. A photograph of your **own** face
is allowed, and the response tells you what it costs: *we cannot tell whether
this picture shows your face, and if it does, the people who know you will
know.* That line is in `NOT_WITHHELD` too, beside "your writing is still
yours" — the honest list of what anonymity does not survive.

**Somebody else's likeness is refused**, asked and declared exactly as the
overlay module asks it: an anonymous profile wearing another person's face is
impersonation with a layer of deniability on top.

**An empty bubble is an empty picture frame with a plus**, for the owner and
for visitors alike. There were briefly two defaults — a plain silhouette for
strangers, the photo-and-plus for the owner — on the reasoning that the second
reads as a control, and a control offered to somebody who cannot press it
reports the empty bubble as a gap. But **the identifying work is done by the
name**: `Anonymous 41338025` already says which account this is, so the picture
is a placeholder rather than a claim about anybody, and an empty frame is the
most honest drawing of an empty frame. Two defaults also meant two things that
could disagree about the same profile, which is the shape of bug this codebase
keeps finding — so `editor_asset` went with the silhouette.

The picture lives in its own table, never in `profiles.avatar`: they are
pictures for two different states, exactly like a display name and an anonymous
one, and writing it into `avatar` would mean turning anonymity off showed it
instead of the face somebody actually has.

**An anonymous profile's badge withholds who checked.** "Verified by Dr Okafor
of St Mary's" narrows an anonymous author to a city and a workplace, which is
most of the way to a name — the badge would undo the anonymity it sits beside.
What survives is the part worth having, and the reason an anonymous profile
would want one at all: *a real person stands behind this, and somebody checked.*
That claim is separable from *who*, and it is the difference between a pseudonym
and a bot.

**And the limits are published beside the promise.** `GET
/profiles/{id}/anonymity` returns `withheld` and `not_withheld` together,
always. The dangerous reading of the word is the generous one: somebody deciding
whether it is safe to post will assume "anonymous" means untraceable unless they
are told otherwise, and by the time they find out, it is published. We can
decline to publish a name. We cannot make prose unrecognisable to a reader who
knows the author, and saying so plainly is the only honest version of this
feature.

**Per profile, never per account.** An account-wide switch would mean putting
your name on the work profile puts it on the support-group one — the exact
coupling that having several profiles exists to avoid.

The console reaches all of it (**156**). The roster comes first, with the badge
drawn as a thing that *sits on one profile and can move* rather than a checkbox
each profile has and most fail — and an invented person reads as
**unverifiable** rather than as an empty box, because those are different
answers. The anonymity card puts `not_withheld` beside `withheld` at the same
size: a screen that showed only the hidden half would be selling the promise
this feature deliberately does not make.

Two of its endings sit on the same screen for the same reason. Retiring leaves
what the profile meant to the people who knew it; deleting returns an itemised
receipt — a count per kind of record, twenty-five of them — because *deleted* is
a claim and the numbers are evidence.

## Verified, and what the word is allowed to mean

`GET /profiles/{id}/verification`. Two questions that a single badge would run
together, kept apart:

- **Is there a real person behind this?** Answered by `kind`. A `fictional`
  profile depicts nobody — which is *not* the same as unverified, and the API
  says so rather than implying somebody failed a check.
- **Has anyone checked they are who they claim?** Answered by a recorded level,
  and the honest answer is usually *not much*.

The ladder is `signatures.PROOFING_LEVELS`, reused rather than reinvented so the
platform has one meaning for how well an identity is established:

| level | means |
| --- | --- |
| `self_asserted` | they say so, and nobody has checked |
| `federated` | confirmed through another account they control |
| `document` | an identity document was checked |
| `in_person` | somebody met them and checked in person |

**Anything above self-asserted needs a named attestor** — the same rule
`signatures.enroll` applies, for the same reason: who checked belongs in the
record, not in a footnote.

### The gold mark

`tools/mark_verified.py` burns **✓ VERIFIED** into an authenticated
person's photograph, in gold, **bottom-right** — diagonally opposite the AI
mark, so the two can never land on each other. It is the mirror image of
`tools/mark_portraits.py` and exists for the same physics: a composited badge
does not survive a screenshot, a hotlink or a right-click save, and those are the
journeys a profile picture actually takes.

**Gold because everything else is taken or already means something here.** Blue
is X and Facebook, grey is the downgraded one people learned to distrust, green
is the agent status light two screens away, and red already means *stopped* in
this product.

**The gate is a named attestor.** A burned mark is the strongest claim an image
can carry: it cannot be qualified, it outlives every surface, and by design it
travels where nobody can check it. That is safe for *AI* — a rendering is
AI-generated wherever it ends up, forever, so burning it in can never become
false. *Verified* is not that kind of fact, so the tool refuses any photograph
with no verification record naming who attested.

What it deliberately does **not** require is a particular rung. It first
required `document`; the platform's owner asked for the mark on his own
photograph at `self_asserted`, which is his call to make about his own face on
his own product, taken after the stricter version had been built and the trade
explained. So the burned word carries exactly the weight of whoever attested —
and the honest reading stays one call away. `verification.status` still reports
`self_asserted` and still returns its caveat:

> *self-asserted: the badge confirms a real person stands behind this profile,
> not that a document was checked*

**Nothing in the code claims a document was checked, because none was.** The day
one is, the level moves and the badge means more without the pixels changing.

## The agent status light

An agent working on its own raises one question, and it is not *what phase is
it in* — it is **does this need me right now?** Three colours answer it.

| | | |
| --- | --- | --- |
| 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
| 🟡 **amber** | needs you | it has stopped and is waiting on a person |
| 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |

**Derived, never stored.** There is no `light` column and nothing sets one — it
is computed from the status the work already keeps. A second field naming the
same fact is a second field that can disagree with the first, and the one a
screen reads would be the one nobody remembers to update.

**The word rides with the colour**, because green alone cannot separate an
agent that is still going from one that has finished, and those call for
opposite reactions. On a watch face the word is doing most of the reading
anyway.

**An unrecognised state raises rather than defaulting.** A default would paint
an unknown status green, and green is the colour that means *ignore me* — the
one failure this must not have.

Defined once, in [`qrme/agentlight.py`](https://github.com/davidsbianchi1984/qrme/blob/main/qrme/agentlight.py), for all three products.

**Where you actually see it.** Three surfaces, doing three different jobs.

| Surface | What it shows | Why that shape |
| --- | --- | --- |
| **Watch** — *36 Agents* (JIM) | three lights and three counts, and **no agent names** | a wrist is glanced at, not read. Naming the agents was the first cut and was wrong: a name is something you read, and reading is the thing a glance cannot do. Which agent went amber is a question for the app, where there is room to answer it |
| **App** — *82 Agents* | the same three lights, each a **tappable group** — what is working, what needs you, what stopped | somebody opening this *because* amber appeared should not have to scan a flat list for the one that changed. Grouping puts the answer first and the roster second |
| **Overlay** — *83 Chat · overlay*, and every desktop view | a small translucent box in the bottom-right corner — the same three rows as the wrist, each its own way in | an agent that reports only on its own screen is one you have to remember to check, and amber and red are exactly the states nobody thinks to look for. On desktop it is on **every** view, because those users have no wrist to glance at |
| **Studio widget** — the packaged console (`app/`) | a round, watch-face-sized window pinned bottom-left on every screen: the wrist's exact payload (`GET /profiles/{id}/watch`) — three lights, three counts, the approval line — with a **minimize** control that collapses it to a dot in the worst light's colour | the studio is where owners actually sit, and the wrist's face is already the right size and shape for "does this need me right now?" — so the studio shows the same face at all times, and when it is in the way it folds to a dot rather than disappearing: still one glance, still the worst colour |

The same three colours, on all three sizes of glass:

<table>
  <tr>
    <td align="center" width="18%" valign="bottom"><a href="docs/watch/01-agents.svg"><img src="docs/watch/01-agents.svg" width="150" alt="Watch — agent lights, counts only"></a><br><sub><b>watch</b> · three lights, three counts, no names</sub></td>
    <td align="center" width="26%" valign="bottom"><a href="docs/screens/82-agents.svg"><img src="docs/screens/82-agents.svg" width="200" alt="Mobile — agent groups"></a><br><sub><b>mobile 82</b> · one tappable group per light</sub></td>
    <td align="center" width="26%" valign="bottom"><a href="docs/screens/83-chat.svg"><img src="docs/screens/83-chat.svg" width="200" alt="Mobile — the overlay follows you"></a><br><sub><b>mobile 83</b> · the overlay, mid-conversation</sub></td>
    <td align="center" width="30%" valign="bottom"><a href="docs/desktop/01-home.svg"><img src="docs/desktop/01-home.svg" width="300" alt="Desktop — the overlay on every view"></a><br><sub><b>desktop 01</b> · bottom-right, on every view</sub></td>
  </tr>
</table>

Read them left to right and the shape of the decision changes with the surface.
The wrist answers *is anything wrong* and stops there. The phone answers *which
one*, by making each colour a group you can open. The desktop does not ask at
all — it keeps the box in the corner of every view, because a desktop user has
no wrist to glance at and an agent that reports only on its own screen is one
you have to remember to go and check.

## Companion features

An ambient-companion model, with an explicit consent boundary on each
feature:

| Feature | Implementation |
|---|---|
| Genesis interview | `POST /profiles/genesis` — a profile born from four personal questions; omit `display_name` and it deterministically chooses its own name from the answers |
| Proactive companionship | `POST /profiles/{id}/proactive/{interactor}` — the profile reaches out first, but only when its owner set `interaction_scope: proactive`; the message is moderated and lands in shared memory. **Anti-spam**: a per-relationship rate cap (`proactive_min_interval_hours`, default 24 h), the recipient's quiet hours (`PUT /interactors/{id}/quiet-hours`), and reply-suppression (no repeat outreach until they reply) — a blocked outreach is `429` |
| Honesty about multiplicity | `GET /profiles/{id}/transparency` reports active relationships, and every chat prompt instructs the profile to acknowledge them truthfully if asked — disclosure by design |
| Summoning — @, #, and QR beacons | `PUT /profiles/{id}/handle` claims a unique `@handle`; `GET /summon?ref=` resolves `@handle`, `#tag` (marketplace tags), or a beacon token. `POST /profiles/{id}/beacons` *leaves the profile behind* somewhere physical — a printable QR code (`GET /beacons/{id}/qr.svg`) summons it, scans are counted, beacons can be picked back up, and a departed profile's beacon resolves as a memorial |
| Connections — chat with other users | `POST /connections/join` matches interactors anonymously by alias in a `friendly` tier or an 18+-verified `rated` tier; per-tier moderation (minors always strict, blocked messages never delivered), and either side can end it anytime |
| Rooms — chat, video, AR, VR | `POST /rooms` — multiparty conversations over any channel (`chat`/`voice`/`video`/`ar`/`vr`) with any mix of real users and synthetic profiles: user↔user, profile↔profile (`/rooms/{id}/advance`), or combinations; every profile turn is moderated, and a room with a minor present always runs strict. Each channel gets the same three full-screen states — plain, held, sideways — because those belong to the room rather than to a camera: **103–105** audio (boxes, because there is nothing to look at), **106–108** AR (the others placed in the room you are already in), **109–111** VR/3-D (depth carried by size and position). The strip changes with the channel: no gift button in an audio room, no bell on a posted video |
| Marketplace listings | `POST`/`GET /marketplace/listings` — users and businesses share and market synthetic profiles, content, business expertise, or services; browsable by kind, tag, and area (healthcare, finance, relationships, …). Creating one still needs no token — the seller is established when a price is attached — but an authenticated creator is recorded as the listing's **claimant**, and `DELETE /marketplace/listings/{id}` and the place routes are claimant-gated. Removal used to ask for no credential at all: a stranger could take down a listing that had a recorded seller, an open offer and paid orders against it, while the same stranger asking to withdraw the *offer* on it was told it was not theirs |
| Providers & consented handoffs | `POST`/`GET /providers` — a directory of real local businesses per area (healthcare, medical, mental health, finance, relationships, career); `POST /handoffs` packages the AI specialist's session for a provider *only with explicit consent*, seals it in the PDI vault, and releases it solely through a revocable token (`DELETE /handoffs/{id}` revokes and purges) |
| Embodiments — even robots | `POST /profiles/{id}/embodiments` — speaker, earpiece, hologram, robot, humanoid; chat can arrive from an embodiment, and JIM-mini's autonomous devices can host the same profile. **Personality stays consistent across forms**: the persona prompt affirms one constant identity/memory/voice, `ChatResponse.persona_signature` is invariant across modality and embodiment (voice → text → hologram give the same signature), and `GET /profiles/{id}/embodiment-consistency` exposes that fingerprint + the forms it's live on |
| Graceful departure | `POST /profiles/{id}/sunset` — a farewell composed for every relationship, memory preserved and exportable, archive sealed in PDI, chat closes with `410` instead of a silent 404 |
| Succession & memorial | `POST /profiles/{id}/succeed` (reviewer-verified death/incapacity signal) — ownership passes to the named `successor_owner` with a fresh owner token (the old one revoked), or, with no successor, the profile sunsets to memorial rather than being orphaned. `GET /profiles/{id}/memorial` (public) — the departed profile's memorial: name, handle, purpose, beacon anchors, relationships touched — never persona internals |

## Assistant & perception

The profile as a capable personal assistant and creative partner:

| Feature | Implementation |
|---|---|
| Triage / curation | `POST /profiles/{id}/assist/triage` — sort a large pile of items and keep the best N by a transparent, auditable score |
| Proofread | `POST /profiles/{id}/assist/proofread` — an improved version in the user's voice, plus concrete edit suggestions |
| Perceive & guide | `POST /profiles/{id}/perceive` — "see" a real-time scene (objects, people, gestures, place) through a camera and give hands-free, step-by-step guidance toward a goal, or just share the moment; perceptions are logged |
| Compose creative works | `POST /profiles/{id}/assist/compose` — an original music/poem/note/lyric capturing a shared moment, kept as an artifact (`GET …/assist/works`) |

Every generated result passes the profile's moderation before it is returned.

## Cloud model — use a greater model, and contribute to it

The gateway itself ships here too (`cloudgw/`, `python -m cloudgw`): it
authenticates each contributing deployment, serves one operator-configured
model, and seals contributions into PDI. Its intake **refuses** anything
carrying an identifying field rather than sanitizing it — a quiet strip would
hide the client bug that leaked it.

With a [Cloud Model Gateway](docs/cloud-model.md) configured, inference
routes to the hosted tier (the latest, most capable model — e.g.
`claude-fable-5`) with automatic fallback to the local provider, and
profiles that opt in (`cloud_contribution`) contribute positively-rated,
**anonymized** exchanges back to improve the shared model — ids stripped,
display names replaced, revocable anytime. `GET /cloud/status` reports the
tier. Contributions land in PDI's encrypted, audited intake.

The loop is fully transparent to the owner:

- `GET /profiles/{id}/cloud-contribution` — a dry-run **preview of exactly
  what the next contribution would contain** (nothing is sent), the policy,
  and a verbatim log of everything that has ever left.
- Each item carries a random `ref` — the gateway never sees profile ids, and
  only QRME's local log maps the ref back — so items stay anonymous at the
  gateway yet remain individually deletable.
- `POST /profiles/{id}/cloud-contribution/revoke` — turns contribution off
  **and** deletes everything already contributed at the gateway by those refs.

## Claims 21–26 (`qrme/adaptation.py`, `qrme/tasks.py`)

| Claim | Implementation |
|---|---|
| 21 — latent persona embeddings, persistent cross-session state | A per-(profile, interactor) named latent vector (engagement, warmth, depth, positivity, stress, continuity), EMA-updated after every interaction and versioned in `persona_embeddings`; `GET /profiles/{id}/embedding/{interactor}` |
| 22 — attention conditioning from engagement | The embedding renders as attention weighting in the system prompt (shared history, warmth, depth, reassurance weights), so engagement conditions where the model attends |
| 23 — real-time biometric monitoring during interaction | `ChatRequest.biometrics` (stress_level, heart rate, condition — typically from JIM-mini) is stored, feeds the embedding's stress dimension, and adds a monitored-situation note to the prompt |
| 24 — switching between domain-specialized agents | `PUT /profiles/{id}/specialists` maps domains (mental_health, medical, finance) to specialist profiles; real-time biometric signals route the reply to the matching specialist. The handoff is **sustained within the conversation** — it persists across turns (even turns with no biometrics) until a fresh reading shows recovery, then hands control back. `ChatResponse.handoff.state` reports `engaged` (switched this turn) → `sustained` (specialist still handling) → `returned` (recovered, profile speaks again) |
| 25 — autonomous multi-step tasks with revocable vault access | `POST /profiles/{id}/grants` issues a scoped, revocable token; `POST /profiles/{id}/tasks` runs grant-check → scoped vault read → compose → moderation, logging step summaries only (raw vaulted data is never retained); `DELETE /grants/{id}` revokes instantly. **Workflows** (`qrme/workflows.py`) chain phases into a plan — `research → draft → review → send → confirm` — advanced one at a time (`POST …/workflows`, `…/{wf}/advance`): each phase carries the prior phases' output forward as working memory and runs in persona, the `confirm` phase **pauses** (`awaiting_input`) and **resumes in a later session** (`…/{wf}/resume`), and revoking the grant mid-run halts the next read-bearing phase. **Delegation** (`qrme/delegation.py`) lets somebody *other than the owner* start one — how JIM's Guardian hands work to a specialist rather than sending a chat turn. The workflow routes stay owner-only on purpose: a workflow reads vaulted source material unattended, and a missing grant means scope `["*"]`. So `PUT /profiles/{id}/delegation` is off until an owner writes it, **delegating `research` without a grant is refused at write time**, `POST …/delegated-workflows` accepts only a subset of the permitted phases from somebody already in conversation with the profile, and an owner's own workflow has no `delegated_workflows` row — so it 404s on the delegated routes however the caller authenticates |
| 26 — encrypted, offline fine-tuning | `POST /profiles/{id}/finetune` recomputes all embeddings from stored history locally — no external calls — and seals the adaptation artifact in the PDI vault when configured; runs recorded with metrics and `external_transmission: false`. With `QRME_OFFLINE=1` the whole platform runs on-host: `GET /offline/status` reports `external_transmission_possible: false` and the guarantee that no raw user data ever leaves your vault |

## The specification, mined (`qrme/composite.py`, `qrme/simulation.py`, `qrme/campaigns.py`, `qrme/organization.py`)

The filed specification of App. 19/056,418 and the PDI infrastructure
proposal describe capabilities the claims tables above did not cover; each
is implemented from the documents' own words (tests in
`tests/test_spec_mined.py`, `tests/test_campaigns.py`,
`tests/test_organizations.py`):

| Spec passage | Implementation |
|---|---|
| **Hybrid profiles** — [0038]: "a combination of aspects or characteristics of several people, such as a combination of several past presidents or business leaders, a combination of trusted relatives such as grandparents who are gone" | `POST /profiles/composite` blends ≥2 source profiles into one `kind=hybrid` profile — per-constituent normalized weights and an optional borrowed *aspect* (their patience, their storytelling), recorded in `composite_sources` and published at `GET /profiles/{id}/composition`. Sources must be your own or marketplace-listed; **departed profiles are allowed on purpose** (grandparents who are gone is the spec's own example), rated ones never, and `kind=hybrid` can't be typed free-hand. The persona prompt carries the blend openly: a hybrid says who it is a composite of and never claims to be any single constituent |
| **Real-time simulation & predictive modeling** — clause 1: "real-time simulations of the first person's actions, workflows, and decision-making processes for predictive modeling and operational insights"; clause 5: retained memory "utilized for predictive modeling" | `POST /profiles/{id}/simulate` (owner-only) runs the persona over a scenario and horizon (`immediate`/`short_term`/`long_term`), optionally conditioned on one relationship's memory and latent embedding, and returns decision + workflow + rationale. `confidence` is **earned from evidence volume** (source items, remembered turns, embedding) — never from how sure the model sounds — the narrative is watermarked synthetic, and runs are never distributed (`GET /profiles/{id}/simulations`) |
| **Environmental adaptation** — clause 1: "dynamically adapt to environmental data, such as location, conditions, and user behavior, enabling contextual relevance" | `ChatRequest.environment` ({location, conditions, local_time, activity}) rides into the reply beside the claim-23 biometrics: stored in `environment_context`, rendered into the system prompt so the reply fits where the person actually is, and echoed back on the response |
| **Role-specific contexts** — clauses 2/12: "function as an advisor, collaborator, or operator based on the user's interaction … may autonomously interpret user prompts to provide situationally relevant responses" | A chat turn can declare `role: "advisor" \| "collaborator" \| "operator"`, or leave it unset and the profile reads the prompt itself (`qrme/roles.py` — transparent keyword inference, silent on a tie, never a hidden model call). The reply's `role_context` names the role and how it arrived (`declared`/`inferred`); frames shape *how* the profile works this turn — counsel with a recommendation, co-creation with a next step, precise execution — never *who* it is: persona, relationship, memory and moderation apply unchanged |
| **The operational ecosystem** — PDI proposal: role-specific agents that "collaborate across departments, pulling relevant data, offering smart suggestions, and coordinating efforts" | `POST /organizations` + `/organizations/{id}/departments` staff each department with one of your profiles as its role agent, scoped by the same **revocable grant** machinery as claim-25 tasks — revoke and the department's pulls stop instantly, the org stands. `POST /organizations/{id}/coordinate` takes one goal across every department: each agent contributes from its own scoped material in its own persona, the initiating agent composes the joint plan (watermarked synthetic, owner-only, never distributed — so no moderation step), and with the PDI tandem configured the whole record is **sealed into the vault** (`qrme/coordination/…`). `POST /organizations/demo` builds a working demo team on the caller's own account in one press — two granted, desked agents ready to coordinate. Console: the **Org** tab; screen 146 |
| **Crowdfunding, proceeds routed by the user** — [0020] example two: "supply crowdfunding for any loved ones, left behind or organizations for donations, wherever the proceeds might go up to the user" | `PUT /profiles/{id}/proceeds` designates loved ones and organizations with shares that must sum to exactly 100; `POST /profiles/{id}/campaigns` opens a campaign — **refused until a designation exists** and never on a rated profile; `POST /campaigns/{id}/donate` (tokenless — generosity is not gated behind signup; capped like a gift) splits at the door onto the ledger, a designee with a platform account paid on their own statement. The public card always shows the names: a donor gives to people, not to the platform. Sunset changes nothing (the living owner keeps the pen); verified owner death (`/succeed`) revokes the old token and hands it to the chosen successor — "leave it in good hands" enforced by the token lifecycle. Console: the **Campaigns** tab; screen 145 |

## The suite — one origin, one login

QRME, JIM-mini, and PDI stay three independent apps, but `suite/gateway.py`
fronts all three behind a **single origin** so the suite runs as one product
(the [launcher](launcher/) is the desktop shell for it):

```bash
pip install -e .[dev]        # plus the jim-mini and pdi packages for the full suite
uvicorn suite.gateway:app    # /qrme/… /jim/… /pdi/… on one origin
```

On top of the mounted apps it adds a thin, **stateless** cross-cutting layer
(it fans out over the per-product tokens the caller already holds and stores no
*user* credential of its own — the one credential it does hold is the suite's
vault-tenant token, a deployment credential it mints itself so QRME's seals
keep working in suite mode):

| Endpoint | What |
|---|---|
| `GET /suite/health` | Which products are mounted and live |
| `POST /suite/session` | Unified sign-on — provision one identity across all three in a single call |
| `POST /suite/erase` | Right to be forgotten, suite-wide, with a per-product receipt |
| `POST /suite/export` | Data portability — one bundle with the identity's data from every product |
| `PUT /suite/consent` · `POST /suite/consent/read` | Centralized consent, sealed in the PDI vault and enforced across products |
| `POST /suite/usage` | Usage metering hooks for a suite-wide subscription |
| `POST /suite/ecosystem` | One call after sign-on: the demo org seeded in QRME, JIM's care team linked to its first desk |
| `POST /suite/operations` | The caller's coordinations as the vault recorded them — provenance, scoped by owner |

See [docs/tandem.md](docs/tandem.md) for the full cross-product architecture.

**One-command smoke check** — `python -m suite.smoke` boots all three
products in-process (no ports), seeds everything (PDI starter vault + JIM
tenancy, QRME marketplace/packs/registries, JIM specialists + the tandem
hookup), then drives one live exchange: a JIM financial-stress detection
routed to the QRME starter specialist `@marcus_bell`, sealed in the PDI
vault, and its provenance verified back through JIM's custody window.
Prints a JSON step report; exit 0 = the suite is green. Also runs as
`tests/test_suite_smoke.py` (skips cleanly when the siblings aren't
installed).

## Design assets

The PRD-derived visual asset brief lives in
[docs/design/image-prompts.md](docs/design/image-prompts.md) — twelve
image-generation prompts covering the app icon, hero banner, onboarding flow,
and feature illustrations. Vector concept renditions of each (shared palette:
deep indigo / soft silver / warm amber) are in
[assets/design/](assets/design/), with a browsable
[gallery](assets/design/gallery.html).

## Out of scope for v1 (per PRD non-goals)

Biometric persona switching, robotic embodiment, media watermarking/provenance,
profile marketplace. Social-platform posting integrations are stubbed as a
`sources` list only.

## Related projects

Three separate products, each standalone, interoperating only over HTTP —
see [docs/tandem.md](docs/tandem.md) for the full architecture:

- [**qrme**](https://github.com/davidsbianchi1984/qrme) — AI synthetic
  profiles: relationship-aware, remembered, moderated.
- [**jim-mini**](https://github.com/davidsbianchi1984/jim-mini) — Guardian
  personal guidance: monitor, predict, guide, escalate; can delegate
  specialist guidance to QRME.
- [**pdi**](https://github.com/davidsbianchi1984/pdi) — Private Data
  Infrastructure: the encrypted vault both AI systems can run on top of.

## Reference

Everything below is lookup material — how to run it, what to configure, what
the endpoints are. It is at the bottom on purpose: if you see a command in one
of the screens above and want to know what it does, this is where to find it.

### Architecture

- **API**: FastAPI (`qrme/api.py`), app factory `create_app()`.
- **Storage**: SQLite (`qrme/db.py`), path via `QRME_DB` (default `qrme.db`).
- **Persona conditioning**: `qrme/persona.py` builds the system prompt from
  profile identity + relationship + engagement + aging.
- **LLM**: official Anthropic SDK (`qrme/llm.py`), model `claude-opus-5`
  with adaptive thinking. Without credentials (or with `QRME_LLM=stub`) a
  deterministic stub provider is used, so everything runs offline.
  **Bring your own key:** send `x-llm-api-key` on any request (the console's
  Control Center stores it device-side) and that request's generations run
  on your credential — never persisted, never logged; the deployment's env
  key (an operator lending theirs out) answers requests that bring none.
- **Marketplace expertise**: `qrme/packs.py` (knowledge packs + robot task
  packs, starter content, seeding) with routes in `qrme/routers/packs.py`;
  `qrme/seed.py` (starter profile collection); `qrme/robotics.py` (robot
  catalog, per-kind command allowlists) with routes in
  `qrme/routers/robots.py`.
- **Native clients**: three idiomatic codebases under [`native/`](native/)
  (SwiftUI, Jetpack Compose, WinUI 3) exercising the real API — see
  [native/README.md](native/README.md) for the screen-by-screen endpoint
  map.

### Run

```bash
pip install -e .[dev]
uvicorn qrme.api:app --reload
```

Set `ANTHROPIC_API_KEY` (or log in with `ant auth login`) for real model
replies; otherwise the stub provider answers. Override the model with
`QRME_MODEL`.

### Run it on your phone

The studio is a web app, so a phone on the same Wi-Fi runs it straight from
this backend — no app store, no second server, nothing to configure on the
phone.

```bash
python -m qrme          # the launcher menu: choose your device
python -m qrme phone    # straight to the phone flow
```

Bare `python -m qrme` prints the launcher menu — every way to run QRME,
one command each, so you pick per device: **phone** (this section),
**desktop** (`python -m qrme desktop`, the Electron app on this PC),
**packaged installer** (`.dmg`/`.exe`/`.AppImage` from the releases page —
no toolchain needed), or **headless API** (`python -m qrme serve`). Same
backend, same data, same token checks in every form.

The packaged installer is **double-click-and-done**: it ships the whole
Python backend as a frozen binary (`packaging/backend_entry.py`, built by
PyInstaller in the release workflow) and the app spawns it at launch when no
backend is already answering — no Python install, no terminal, data under
the app's own user-data directory, and the spawned backend dies with the
window. A backend you already run yourself is left alone.

`python -m qrme phone` builds the studio if it's missing (first run installs the
npm dependencies too), prints the phone URL **with a QR code right in the
terminal**, and starts the API on the network — scan, Add to Home Screen,
done. Flags: `--port`, `--rebuild`, `--no-build`, `--print-only`.

### Maintenance: rows the old profile delete left behind

Before 0.59.9 the profile delete ran off a list of twenty-four table names
against a schema of sixty-six. Every profile ended on a build older than that
release left forty-two tables standing — `clinical_notes` and the `media`
behind them, `media_watermarks`, `anonymous_pictures`, `homepages`,
`friendships`, `inbox_events` — and nothing in the running product will ever
look at them again, because the `profiles` row is gone and the API answers
404. Fixing the cascade fixed the next delete. It did not reach back.

```bash
python -m qrme.orphans            # count them, change nothing
python -m qrme.orphans --json     # the same survey, machine-readable
python -m qrme.orphans --apply    # clear them
```

**Dry by default.** The command a person runs to find out how bad it is is not
the command that changes it. A row counts as an orphan only when its
`profile_id` names a profile that is not in `profiles`; rows with a NULL or
empty subject are left alone. The scope is the delete cascade's own reader,
so this is that cascade applied retroactively rather than a second list to
keep in step.

A deployment first installed on 0.59.9 or later has nothing to sweep, and the
command says so in a sentence.


The manual equivalent, if you prefer the steps separately:

```bash
npm --prefix app install && npm --prefix app run build   # build the studio once
uvicorn qrme.api:app --host 0.0.0.0                      # listen on the network
curl localhost:8000/pair                                 # what to open on the phone
```

`GET /pair` answers with the studio's URL on your local network (and
`GET /pair/qr.svg` is the same URL as a QR code — the Control Center screen
shows both, so you can scan it off the laptop). Open that URL on the phone,
then **Add to Home Screen**: it installs as a standalone app with its own
icon, runs full-screen, and keeps working through a brief drop in
connectivity.

Why it needs no setup: the API serves the studio at `/app`, so the UI and
the API share one origin — the studio simply calls the address it was loaded
from. The phone layout follows: the sidebar becomes a thumb-reachable bottom
tab bar, inputs stay at 16px so iOS doesn't zoom, and the layout respects
the notch and home indicator.

#### Published deployments

The same code serves a laptop on Wi-Fi and an instance you host for yourself
and your colleagues to reach from anywhere:

<table>
<tr><th align="left"><sub>Variable</sub></th><th align="left"><sub>Effect</sub></th></tr>
<tr><td valign="top"><sub><code>QRME_PUBLIC_URL</code></sub></td><td valign="top"><sub><code>GET /pair</code> advertises this address (QR included) instead of a LAN one, so the phone flow works over the internet. Serve it over HTTPS — tokens travel in headers.</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_SIGNUP_KEY</code></sub></td><td valign="top"><sub>Profile creation requires this key as the <code>x-signup-key</code> header, so a published instance stays yours rather than open registration. Unset = open, the right default on a LAN.</sub></td></tr>
</table>

Talking to a profile stays public either way; the key gates creating an
account on your deployment, not using one.

The `Dockerfile` packages the studio and the API into one image so a hosted
instance serves both from the same origin, exactly like the phone flow does:

```bash
docker build -t qrme .
docker run -p 8000:8000 -v qrme-data:/data \
  -e QRME_PUBLIC_URL=https://qrme.example.com \
  -e QRME_SIGNUP_KEY="$(openssl rand -base64 24)" qrme
```

[docs/hosting.md](docs/hosting.md) covers the rest — TLS, what mounting
`/data` protects, and what running profiles for other people commits you to.

Without `QRME_PUBLIC_URL`, the address is local-network only and deliberately
not reachable from the internet — your profiles and their memories stay on
your own network.
Everything still requires the owner or interactor bearer token; a phone on
the LAN is exactly as authorized as a laptop on the LAN. If `/pair` reports
`reachable: false`, it could only find loopback (which on a phone means the
phone itself): set `QRME_LAN_HOST` to this machine's address and restart.

### Configuration

<table>
<tr><th align="left"><sub>Variable</sub></th><th align="left"><sub>Default</sub></th><th align="left"><sub>Purpose</sub></th></tr>
<tr><td valign="top"><sub><code>QRME_DB</code></sub></td><td valign="top"><sub><code>qrme.db</code></sub></td><td valign="top"><sub>SQLite database path</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_LLM</code></sub></td><td valign="top"><sub>auto</sub></td><td valign="top"><sub><code>stub</code> forces the offline deterministic provider; <code>anthropic</code> forces the SDK</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_OFFLINE</code></sub></td><td valign="top"><sub>off</sub></td><td valign="top"><sub><code>1</code>/<code>true</code> runs <b>fully offline</b>: local inference only (Anthropic SDK and cloud gateway bypassed even if configured), cloud never attached, embeddings/fine-tuning recomputed on-host. <code>GET /offline/status</code> reports the posture</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_MODEL</code></sub></td><td valign="top"><sub><code>claude-opus-5</code></sub></td><td valign="top"><sub>Model used for profile replies</sub></td></tr>
<tr><td valign="top"><sub><code>ANTHROPIC_API_KEY</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Enables real model replies</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_PDI_URL</code> / <code>QRME_PDI_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>PDI tandem: seal source material in the encrypted vault</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CLOUD_URL</code> / <code>QRME_CLOUD_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Cloud Model Gateway: greater-model inference with local fallback + opt-in contribution (<a href="docs/cloud-model.md">docs/cloud-model.md</a>; standing one up: <a href="docs/cloudgw-deploy.md">docs/cloudgw-deploy.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_RP_ID</code></sub></td><td valign="top"><sub><code>qrme.app</code></sub></td><td valign="top"><sub>The WebAuthn relying party — <b>the deployment's own domain</b>. Passkeys are bound to it, so leaving the default on a real deployment makes every signature fail as "made for a different site". A relying party id must be a <b>domain</b>: on a loopback install set <code>localhost</code>, never an IP (<a href="docs/signatures.md">docs/signatures.md</a>, <a href="docs/windows-hello-field-test.md">docs/windows-hello-field-test.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_RP_ORIGINS</code></sub></td><td valign="top"><sub>any</sub></td><td valign="top"><sub>Comma-separated allowlist of origins a signing ceremony may come from. Unset accepts any origin the relying party matches</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_GOOGLE_CLIENT_ID</code> / <code>QRME_GOOGLE_CLIENT_SECRET</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Sign in with Google. Unset greys the button and shows why (<a href="docs/sign-in.md">docs/sign-in.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_APPLE_CLIENT_ID</code> / <code>QRME_APPLE_CLIENT_SECRET</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Sign in with Apple. The secret is a <b>JWT you sign yourself and it expires within six months</b> — mint and check it with <code>scripts/mint_apple_secret.py</code> (<a href="docs/sign-in.md">docs/sign-in.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CONSOLE_DIR</code></sub></td><td valign="top"><sub><code>app/dist</code></sub></td><td valign="top"><sub>Where the built studio is served from. Set it explicitly in a container — it resolves relative to the installed package otherwise, which is not where the build lands</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CORS_ORIGINS</code></sub></td><td valign="top"><sub>off</sub></td><td valign="top"><sub>Comma-separated allowlist for a front-end on another origin; <code>*</code> for any. Off is right when the studio and API share an origin</sub></td></tr>
</table>

### Test

```bash
pytest
```

### Example flow

```bash
# 1. Create a profile (owner is age-verified)
curl -s localhost:8000/profiles -H 'content-type: application/json' -d '{
  "owner_id": "owner-1", "kind": "self", "display_name": "Dana",
  "persona": "A retired teacher who loves gardening and dry humor.",
  "verification": {"birthdate": "1984-06-01"}}'

# 2. Register an interactor and set the relationship
curl -s localhost:8000/interactors -d '{"display_name": "Sam", "birthdate": "2000-01-15"}' -H 'content-type: application/json'
curl -s -X PUT localhost:8000/profiles/$PROFILE/relationships/$INTERACTOR \
  -H 'content-type: application/json' \
  -d '{"relationship_type": "grandchild", "nickname": "kiddo", "tone": "playful", "boundaries": ["finances"]}'

# 3. Chat — reply is persona-, relationship-, and engagement-conditioned,
#    and moderated before it is shown
curl -s localhost:8000/profiles/$PROFILE/chat -H 'content-type: application/json' \
  -d '{"interactor_id": "'$INTERACTOR'", "message": "Tell me about your garden!"}'
```

## License

MIT © 2026 David Bianchi — see [LICENSE](LICENSE).

---

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
