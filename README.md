# QRME — AI Synthetic Profile Platform

**Current release: v0.3.3** ([changelog](CHANGELOG.md) ·
[release notes](RELEASE_NOTES.md)) — one of three products
([jim-mini](https://github.com/davidsbianchi1984/jim-mini),
[pdi](https://github.com/davidsbianchi1984/pdi)) versioned and cut together, so
one number names one combination of all three.

![QRME — relationship-aware synthetic profiles](assets/design/00-cover.svg)

> **Patent pending** — *Synthetic User Profile Management System*
> (U.S. Patent Application No. 19/056,418, Attorney Docket 526.P002).

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
</table>

### Mobile app

The same system on a phone. Regenerate with `python3 docs/screens/build.py`.

**Onboarding, identity & control**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/01-welcome.svg"><img src="docs/screens/01-welcome.svg" width="210" alt="Welcome"></a><br><sub><b>01</b> · Welcome</sub></td>
    <td align="center" width="33%"><a href="docs/screens/02-create-profile.svg"><img src="docs/screens/02-create-profile.svg" width="210" alt="Create Profile"></a><br><sub><b>02</b> · Create Profile</sub></td>
    <td align="center" width="33%"><a href="docs/screens/03-build-your-profile.svg"><img src="docs/screens/03-build-your-profile.svg" width="210" alt="Build Your Profile"></a><br><sub><b>03</b> · Build Your Profile</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/04-personality.svg"><img src="docs/screens/04-personality.svg" width="210" alt="Personality"></a><br><sub><b>04</b> · Personality</sub></td>
    <td align="center" width="33%"><a href="docs/screens/05-profile-home.svg"><img src="docs/screens/05-profile-home.svg" width="210" alt="Profile Home"></a><br><sub><b>05</b> · Profile Home</sub></td>
    <td align="center" width="33%"><a href="docs/screens/06-chat.svg"><img src="docs/screens/06-chat.svg" width="210" alt="Chat"></a><br><sub><b>06</b> · Chat</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/07-memory-vault.svg"><img src="docs/screens/07-memory-vault.svg" width="210" alt="Memory Vault"></a><br><sub><b>07</b> · Memory Vault</sub></td>
    <td align="center" width="33%"><a href="docs/screens/08-relationships.svg"><img src="docs/screens/08-relationships.svg" width="210" alt="Relationships"></a><br><sub><b>08</b> · Relationships</sub></td>
    <td align="center" width="33%"><a href="docs/screens/09-add-relationship.svg"><img src="docs/screens/09-add-relationship.svg" width="210" alt="Add Relationship"></a><br><sub><b>09</b> · Add Relationship</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/10-profile-health.svg"><img src="docs/screens/10-profile-health.svg" width="210" alt="Profile Health"></a><br><sub><b>10</b> · Profile Health</sub></td>
    <td align="center" width="33%"><a href="docs/screens/11-marketplace.svg"><img src="docs/screens/11-marketplace.svg" width="210" alt="Marketplace"></a><br><sub><b>11</b> · Marketplace</sub></td>
    <td align="center" width="33%"><a href="docs/screens/12-licensing-center.svg"><img src="docs/screens/12-licensing-center.svg" width="210" alt="Licensing Center"></a><br><sub><b>12</b> · Licensing Center</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/13-embodiments.svg"><img src="docs/screens/13-embodiments.svg" width="210" alt="Embodiments"></a><br><sub><b>13</b> · Embodiments</sub></td>
    <td align="center" width="33%"><a href="docs/screens/14-control-center.svg"><img src="docs/screens/14-control-center.svg" width="210" alt="Control Center"></a><br><sub><b>14</b> · Control Center</sub></td>
    <td align="center" width="33%"><a href="docs/screens/15-design-language.svg"><img src="docs/screens/15-design-language.svg" width="210" alt="Design Language"></a><br><sub><b>15</b> · Design Language</sub></td>
  </tr>
</table>

**Companion, summoning & connection**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/16-genesis.svg"><img src="docs/screens/16-genesis.svg" width="210" alt="Genesis"></a><br><sub><b>16</b> · Genesis</sub></td>
    <td align="center" width="33%"><a href="docs/screens/17-summon-beacons.svg"><img src="docs/screens/17-summon-beacons.svg" width="210" alt="Summon & Beacons"></a><br><sub><b>17</b> · Summon & Beacons</sub></td>
    <td align="center" width="33%"><a href="docs/screens/18-proactive.svg"><img src="docs/screens/18-proactive.svg" width="210" alt="Proactive"></a><br><sub><b>18</b> · Proactive</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/19-transparency.svg"><img src="docs/screens/19-transparency.svg" width="210" alt="Transparency"></a><br><sub><b>19</b> · Transparency</sub></td>
    <td align="center" width="33%"><a href="docs/screens/20-connections.svg"><img src="docs/screens/20-connections.svg" width="210" alt="Connections"></a><br><sub><b>20</b> · Connections</sub></td>
    <td align="center" width="33%"><a href="docs/screens/21-rooms.svg"><img src="docs/screens/21-rooms.svg" width="210" alt="Rooms"></a><br><sub><b>21</b> · Rooms</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/22-providers.svg"><img src="docs/screens/22-providers.svg" width="210" alt="Providers"></a><br><sub><b>22</b> · Providers</sub></td>
  </tr>
</table>

**Your data promise, lifecycle & the claims**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/23-cloud-model.svg"><img src="docs/screens/23-cloud-model.svg" width="210" alt="Cloud Model"></a><br><sub><b>23</b> · Cloud Model</sub></td>
    <td align="center" width="33%"><a href="docs/screens/24-offline-mode.svg"><img src="docs/screens/24-offline-mode.svg" width="210" alt="Offline Mode"></a><br><sub><b>24</b> · Offline Mode</sub></td>
    <td align="center" width="33%"><a href="docs/screens/25-objection-lifecycle.svg"><img src="docs/screens/25-objection-lifecycle.svg" width="210" alt="Objection & Lifecycle"></a><br><sub><b>25</b> · Objection & Lifecycle</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/26-memorial.svg"><img src="docs/screens/26-memorial.svg" width="210" alt="Memorial"></a><br><sub><b>26</b> · Memorial</sub></td>
    <td align="center" width="33%"><a href="docs/screens/27-ai-assistant.svg"><img src="docs/screens/27-ai-assistant.svg" width="210" alt="AI Assistant"></a><br><sub><b>27</b> · AI Assistant</sub></td>
    <td align="center" width="33%"><a href="docs/screens/28-specialists.svg"><img src="docs/screens/28-specialists.svg" width="210" alt="Specialists"></a><br><sub><b>28</b> · Specialists</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/29-tasks-grants.svg"><img src="docs/screens/29-tasks-grants.svg" width="210" alt="Tasks & Grants"></a><br><sub><b>29</b> · Tasks & Grants</sub></td>
    <td align="center" width="33%"><a href="docs/screens/30-fine-tune.svg"><img src="docs/screens/30-fine-tune.svg" width="210" alt="Fine-Tune"></a><br><sub><b>30</b> · Fine-Tune</sub></td>
    <td align="center" width="33%"><a href="docs/screens/31-your-data-promise.svg"><img src="docs/screens/31-your-data-promise.svg" width="210" alt="Your Data Promise"></a><br><sub><b>31</b> · Your Data Promise</sub></td>
  </tr>
</table>

**Moderation, posting & the persona engine**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/32-moderation.svg"><img src="docs/screens/32-moderation.svg" width="210" alt="Moderation"></a><br><sub><b>32</b> · Moderation</sub></td>
    <td align="center" width="33%"><a href="docs/screens/33-posts.svg"><img src="docs/screens/33-posts.svg" width="210" alt="Posts"></a><br><sub><b>33</b> · Posts</sub></td>
    <td align="center" width="33%"><a href="docs/screens/34-adult-mode.svg"><img src="docs/screens/34-adult-mode.svg" width="210" alt="Adult Mode"></a><br><sub><b>34</b> · Adult Mode</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/35-aging-lifecycle.svg"><img src="docs/screens/35-aging-lifecycle.svg" width="210" alt="Aging & Lifecycle"></a><br><sub><b>35</b> · Aging & Lifecycle</sub></td>
    <td align="center" width="33%"><a href="docs/screens/36-multi-modal.svg"><img src="docs/screens/36-multi-modal.svg" width="210" alt="Multi-Modal"></a><br><sub><b>36</b> · Multi-Modal</sub></td>
    <td align="center" width="33%"><a href="docs/screens/37-persona-embedding.svg"><img src="docs/screens/37-persona-embedding.svg" width="210" alt="Persona Embedding"></a><br><sub><b>37</b> · Persona Embedding</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/38-surfaces.svg"><img src="docs/screens/38-surfaces.svg" width="210" alt="Surfaces"></a><br><sub><b>38</b> · Surfaces</sub></td>
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
    <td align="center" width="33%"><a href="docs/screens/41-log-in.svg"><img src="docs/screens/41-log-in.svg" width="210" alt="Log In"></a><br><sub><b>41</b> · Log In (Apple · Google · Email)</sub></td>
    <td align="center" width="33%"><a href="docs/screens/42-verify-identity.svg"><img src="docs/screens/42-verify-identity.svg" width="210" alt="Verify Identity"></a><br><sub><b>42</b> · Verify Identity</sub></td>
    <td align="center" width="33%"><a href="docs/screens/43-enable-access.svg"><img src="docs/screens/43-enable-access.svg" width="210" alt="Enable Access"></a><br><sub><b>43</b> · Enable Access</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/44-avatar-studio.svg"><img src="docs/screens/44-avatar-studio.svg" width="210" alt="Avatar Studio"></a><br><sub><b>44</b> · Avatar Studio (2D &amp; 3D)</sub></td>
    <td align="center" width="33%"><a href="docs/screens/47-all-set.svg"><img src="docs/screens/47-all-set.svg" width="210" alt="All Set"></a><br><sub><b>47</b> · All Set</sub></td>
    <td align="center" width="33%"></td>
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
    <td align="center" width="33%"><a href="docs/screens/48-social-connections.svg"><img src="docs/screens/48-social-connections.svg" width="210" alt="Social Connections"></a><br><sub><b>48</b> · Social Connections</sub></td>
    <td align="center" width="33%"><a href="docs/screens/49-connected-apps.svg"><img src="docs/screens/49-connected-apps.svg" width="210" alt="Connected Apps"></a><br><sub><b>49</b> · Connected Apps</sub></td>
    <td align="center" width="33%"><a href="docs/screens/50-knowledge-excursions.svg"><img src="docs/screens/50-knowledge-excursions.svg" width="210" alt="Knowledge Excursions"></a><br><sub><b>50</b> · Knowledge Excursions</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/51-files-photos.svg"><img src="docs/screens/51-files-photos.svg" width="210" alt="Files & Photos"></a><br><sub><b>51</b> · Files &amp; Photos</sub></td>
    <td align="center" width="33%"><a href="docs/screens/52-apple-intelligence.svg"><img src="docs/screens/52-apple-intelligence.svg" width="210" alt="Apple Intelligence"></a><br><sub><b>52</b> · Apple Intelligence</sub></td>
    <td align="center" width="33%"><a href="docs/screens/53-google-gemini.svg"><img src="docs/screens/53-google-gemini.svg" width="210" alt="Google Gemini"></a><br><sub><b>53</b> · Google Gemini</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/54-microsoft-copilot.svg"><img src="docs/screens/54-microsoft-copilot.svg" width="210" alt="Microsoft Copilot"></a><br><sub><b>54</b> · Microsoft Copilot</sub></td>
    <td align="center" width="33%"><a href="docs/screens/55-objection-revocation.svg"><img src="docs/screens/55-objection-revocation.svg" width="210" alt="Objection &amp; Revocation"></a><br><sub><b>55</b> · Objection &amp; Revocation</sub></td>
    <td align="center" width="33%"><a href="docs/screens/56-robotics.svg"><img src="docs/screens/56-robotics.svg" width="210" alt="Robotics"></a><br><sub><b>56</b> · Robotics</sub></td>
  </tr>
</table>

**Knowledge packs, robot task mods & embodiment**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/57-knowledge-packs.svg"><img src="docs/screens/57-knowledge-packs.svg" width="210" alt="Knowledge Packs"></a><br><sub><b>57</b> · Knowledge Packs</sub></td>
    <td align="center" width="33%"><a href="docs/screens/58-robot-task-packs.svg"><img src="docs/screens/58-robot-task-packs.svg" width="210" alt="Robot Task Packs"></a><br><sub><b>58</b> · Robot Task Packs</sub></td>
    <td align="center" width="33%"><a href="docs/screens/59-embodied-agent.svg"><img src="docs/screens/59-embodied-agent.svg" width="210" alt="Embodied Agent"></a><br><sub><b>59</b> · Embodied Agent</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/60-publish-a-pack.svg"><img src="docs/screens/60-publish-a-pack.svg" width="210" alt="Publish a Pack"></a><br><sub><b>60</b> · Publish a Pack</sub></td>
    <td align="center" width="33%"><a href="docs/screens/61-pack-registries.svg"><img src="docs/screens/61-pack-registries.svg" width="210" alt="Pack Registries"></a><br><sub><b>61</b> · Pack Registries</sub></td>
    <td align="center" width="33%"><a href="docs/screens/62-rated-placement.svg"><img src="docs/screens/62-rated-placement.svg" width="210" alt="Rated Placement"></a><br><sub><b>62</b> · Rated Placement (18+)</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/63-placement-analytics.svg"><img src="docs/screens/63-placement-analytics.svg" width="210" alt="Placement Analytics"></a><br><sub><b>63</b> · Placement Analytics</sub></td>
    <td align="center" width="33%"><a href="docs/screens/64-creator-payouts.svg"><img src="docs/screens/64-creator-payouts.svg" width="210" alt="Creator Payouts"></a><br><sub><b>64</b> · Creator Payouts</sub></td>
    <td align="center" width="33%"><a href="docs/screens/65-watch-remote.svg"><img src="docs/screens/65-watch-remote.svg" width="210" alt="Watch Remote"></a><br><sub><b>65</b> · Watch Remote</sub></td>
    <td align="center" width="33%"><a href="docs/screens/66-steering.svg"><img src="docs/screens/66-steering.svg" width="210" alt="Steering"></a><br><sub><b>66</b> · Steering</sub></td>
    <td align="center" width="33%"><a href="docs/screens/67-smart-glasses.svg"><img src="docs/screens/67-smart-glasses.svg" width="210" alt="Smart Glasses"></a><br><sub><b>67</b> · Smart Glasses</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/68-gaming-companion.svg"><img src="docs/screens/68-gaming-companion.svg" width="210" alt="Gaming Companion"></a><br><sub><b>68</b> · Gaming Companion</sub></td>
  </tr>
</table>

**Live desks, the audience layer & commerce**

<table>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/69-live-desks.svg"><img src="docs/screens/69-live-desks.svg" width="210" alt="Live Desks"></a><br><sub><b>69</b> · Live Desks</sub></td>
    <td align="center" width="33%"><a href="docs/screens/70-desk-beacons.svg"><img src="docs/screens/70-desk-beacons.svg" width="210" alt="Desk Beacons"></a><br><sub><b>70</b> · Desk Beacons</sub></td>
    <td align="center" width="33%"><a href="docs/screens/71-audience.svg"><img src="docs/screens/71-audience.svg" width="210" alt="Audience"></a><br><sub><b>71</b> · Audience</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/72-gifts-purchases.svg"><img src="docs/screens/72-gifts-purchases.svg" width="210" alt="Gifts &amp; Purchases"></a><br><sub><b>72</b> · Gifts &amp; Purchases</sub></td>
    <td align="center" width="33%"><a href="docs/screens/73-signatures.svg"><img src="docs/screens/73-signatures.svg" width="210" alt="Signatures"></a><br><sub><b>73</b> · Signatures</sub></td>
    <td align="center" width="33%"><a href="docs/screens/74-starter-collection.svg"><img src="docs/screens/74-starter-collection.svg" width="210" alt="Starter Collection"></a><br><sub><b>74</b> · Starter Collection</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/75-live-room.svg"><img src="docs/screens/75-live-room.svg" width="210" alt="Live Room"></a><br><sub><b>75</b> · Live Room</sub></td>
    <td align="center" width="33%"><a href="docs/screens/76-rated-stream.svg"><img src="docs/screens/76-rated-stream.svg" width="210" alt="Rated Stream"></a><br><sub><b>76</b> · Rated Stream (18+)</sub></td>
    <td align="center" width="33%"><a href="docs/screens/77-search-place.svg"><img src="docs/screens/77-search-place.svg" width="210" alt="Search &amp; Place"></a><br><sub><b>77</b> · Search &amp; Place</sub></td>
    <td align="center" width="33%"><a href="docs/screens/78-marketplace-settings.svg"><img src="docs/screens/78-marketplace-settings.svg" width="210" alt="Marketplace Settings"></a><br><sub><b>78</b> · Marketplace Settings</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/79-search-assistant.svg"><img src="docs/screens/79-search-assistant.svg" width="210" alt="Search Assistant"></a><br><sub><b>79</b> · Search Assistant</sub></td>
    <td align="center" width="33%"><a href="docs/screens/80-profile.svg"><img src="docs/screens/80-profile.svg" width="210" alt="Profile"></a><br><sub><b>80</b> · Profile</sub></td>
    <td align="center" width="33%"><a href="docs/screens/82-agents.svg"><img src="docs/screens/82-agents.svg" width="210" alt="Agents"></a><br><sub><b>82</b> · Agents</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/83-chat.svg"><img src="docs/screens/83-chat.svg" width="210" alt="Chat with the agent overlay"></a><br><sub><b>83</b> · Chat · overlay</sub></td>
    <td align="center" width="33%"><a href="docs/screens/84-friends.svg"><img src="docs/screens/84-friends.svg" width="210" alt="Friends"></a><br><sub><b>84</b> · Friends</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/85-my-page.svg"><img src="docs/screens/85-my-page.svg" width="210" alt="My Page"></a><br><sub><b>85</b> · My Page</sub></td>
    <td align="center" width="33%"><a href="docs/screens/86-customise.svg"><img src="docs/screens/86-customise.svg" width="210" alt="Customise"></a><br><sub><b>86</b> · Customise</sub></td>
    <td align="center" width="33%"><a href="docs/screens/87-for-you.svg"><img src="docs/screens/87-for-you.svg" width="210" alt="For You"></a><br><sub><b>87</b> · For You</sub></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="docs/screens/88-your-devices.svg"><img src="docs/screens/88-your-devices.svg" width="210" alt="Your Devices"></a><br><sub><b>88</b> · Your Devices</sub></td>
    <td align="center" width="33%"><a href="docs/screens/89-live-room.svg"><img src="docs/screens/89-live-room.svg" width="210" alt="Live Room"></a><br><sub><b>89</b> · Live Room · chat + actions</sub></td>
    <td align="center" width="33%"><a href="docs/screens/90-full-screen.svg"><img src="docs/screens/90-full-screen.svg" width="210" alt="Full Screen — long press"></a><br><sub><b>90</b> · Full Screen · long press</sub></td>
  </tr>
</table>

<table>
  <tr>
    <td align="center"><a href="docs/screens/91-full-screen-landscape.svg"><img src="docs/screens/91-full-screen-landscape.svg" width="660" alt="Full Screen Landscape"></a><br><sub><b>91</b> · Full Screen · landscape — tilt the phone and the room arrives at its own aspect ratio</sub></td>
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

**Press and hold, and the picture takes the whole phone** (**90**). No title,
no tab bar, nothing but the room and the strip — full screen that stops short
of the chrome is just a larger box. Holding is also what puts the **help
button** back. It used to be welded to every screen on the theory that "on all
screens" is a property of the chrome rather than something 90 screens can each
be trusted to remember, and that theory is right everywhere except here, where
the chrome *is* the thing being taken away: a floating `?` on a full-screen
video is a permanent smudge on it, and it sits in exactly the corner the share
button now occupies. So it comes back the way everything else does — you press
and hold and it surfaces, along with the way into landscape and the way back to
the app. The promise is kept without the pixel.

The held state dims what you are holding rather than floating buttons over a
bright picture, because that is what a phone actually does and because the dim
is what says the room is still there underneath, waiting.

**Tilt the phone and it goes wide** (**91**). This is the one that earns its
place rather than being a checkbox: the desk was shot sixteen-by-nine, and in a
portrait column two thirds of it is cropped away. Turned sideways it arrives at
its own aspect ratio — the bell on the desk and the sign beside it are both in
frame at once, which is the entire situation the feature exists for. The chat
takes the left third and the strip runs along the bottom, with the composer
capped rather than stretched across half a metre of glass.

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
| Creator Ledger & Payouts | One statement for everything a creator earns (`qrme/ledger.py`): every priced pack sale (knowledge, robot task, rated — and federated registry sales, which accrue to the registry), every license fee, **and every verified venue-placement view** (kind `placement`, credited at `PLACEMENT_VIEW_RATE` per verified resolution through a venue beacon — simulated ad/affiliate revenue) is written to the ledger **at transaction time**, attributed to the creator's `owner_id`. Owner-only `GET /profiles/{id}/earnings` shows entries + accrued/paid/lifetime totals with a per-kind breakdown; `POST …/earnings/payout` sweeps the accrued balance (simulated transfer, real accounting) stamping every entry with its payout id; 409 on an empty balance. Free downloads are never money events |
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
| `DELETE /licenses/{grant}` | source owner | Revoke a license (blocks further derivation) |

`consult` licenses forbid derivation; `finetune`/`clone` permit it. `GET /profiles/{id}` reports `licensed_from` on a derived agent.

## Authentication & access control

Identity is proven by a bearer **capability token**, never by asserting an id
in a request body.

| Token | Minted by | Grants |
|---|---|---|
| **owner** | `POST /profiles` and `POST /profiles/genesis` return `owner_token` **once** | Full control of that profile: edit, sources, surfaces, specialists, grants/tasks, fine-tune, moderation queue, stats, export, erasure, departure, and the assistant/perception endpoints |
| **interactor** | `POST /interactors` returns `token` | Reading one's own conversation memory (`GET /profiles/{id}/memory/{interactor}`) |

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

Profile lifecycle: **active** → `restricted` (objection pending) → `terminated` (erased) or back to active; and **active** → `departed` (memorial, via `/sunset`). `GET /profiles/{id}` reports the current `status`.

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
channel; a paired device is a registration and a set of allowed faces. They are
in the catalogue because the registry is what a later feature will need, and a
device somebody already paired for their watch face should not have to be
paired twice. A test asserts no capture path exists here — no record, stream,
listen or sample.

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

**02 Activity is the community layer on a wrist, as counts.** Not the content:
a feed is a reading surface, and reading is the thing a glance cannot do. Same
reasoning that kept agent names off face 01.

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
| Rooms — chat, video, AR, VR | `POST /rooms` — multiparty conversations over any channel (`chat`/`voice`/`video`/`ar`/`vr`) with any mix of real users and synthetic profiles: user↔user, profile↔profile (`/rooms/{id}/advance`), or combinations; every profile turn is moderated, and a room with a minor present always runs strict |
| Marketplace listings | `POST`/`GET /marketplace/listings` — users and businesses share and market synthetic profiles, content, business expertise, or services; browsable by kind, tag, and area (healthcare, finance, relationships, …) |
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
credential of its own):

| Endpoint | What |
|---|---|
| `GET /suite/health` | Which products are mounted and live |
| `POST /suite/session` | Unified sign-on — provision one identity across all three in a single call |
| `POST /suite/erase` | Right to be forgotten, suite-wide, with a per-product receipt |
| `POST /suite/export` | Data portability — one bundle with the identity's data from every product |
| `PUT /suite/consent` · `POST /suite/consent/read` | Centralized consent, sealed in the PDI vault and enforced across products |
| `POST /suite/usage` | Usage metering hooks for a suite-wide subscription |

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
- **LLM**: official Anthropic SDK (`qrme/llm.py`), model `claude-opus-4-8`
  with adaptive thinking. Without credentials (or with `QRME_LLM=stub`) a
  deterministic stub provider is used, so everything runs offline.
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

`python -m qrme phone` builds the studio if it's missing (first run installs the
npm dependencies too), prints the phone URL **with a QR code right in the
terminal**, and starts the API on the network — scan, Add to Home Screen,
done. Flags: `--port`, `--rebuild`, `--no-build`, `--print-only`.

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
<tr><td valign="top"><sub><code>QRME_MODEL</code></sub></td><td valign="top"><sub><code>claude-opus-4-8</code></sub></td><td valign="top"><sub>Model used for profile replies</sub></td></tr>
<tr><td valign="top"><sub><code>ANTHROPIC_API_KEY</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Enables real model replies</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_PDI_URL</code> / <code>QRME_PDI_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>PDI tandem: seal source material in the encrypted vault</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CLOUD_URL</code> / <code>QRME_CLOUD_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Cloud Model Gateway: greater-model inference with local fallback + opt-in contribution (<a href="docs/cloud-model.md">docs/cloud-model.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_RP_ID</code></sub></td><td valign="top"><sub><code>qrme.app</code></sub></td><td valign="top"><sub>The WebAuthn relying party — <b>the deployment's own domain</b>. Passkeys are bound to it, so leaving the default on a real deployment makes every signature fail as "made for a different site" (<a href="docs/signatures.md">docs/signatures.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_RP_ORIGINS</code></sub></td><td valign="top"><sub>any</sub></td><td valign="top"><sub>Comma-separated allowlist of origins a signing ceremony may come from. Unset accepts any origin the relying party matches</sub></td></tr>
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
