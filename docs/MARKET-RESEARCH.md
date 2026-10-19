# Visual machine explainer market research

Research date: October 19, 2026. Scope: consumer explanations of physical mechanisms, interactive STEM libraries, generated visual learning, and the tools a person could use instead. Prices are public observations for the stated market, not recommendations or evidence of willingness to pay.

## Findings that change the product

**An interactive catalog is already available.** [Visual Learning](https://visual-learning.app/) lists 15 machines, including the same washer, espresso, and refrigerator categories contemplated here. Its [washer page](https://visual-learning.app/washing-machine) exposes seven stage buttons, manual/automatic playback, and model readings. The web reader could not fetch it, but direct HTTPS retrieval returned the homepage and lesson HTML. No purchase gate appeared in those retrieved pages; that does not establish its future pricing or a complete entitlement audit.

**Prompt to animated explanation is also occupied.** Curiso presents an automated video pipeline. General assistants can generate interactive explanations. A dedicated app needs a reason to be opened instead: a reliable lesson that starts immediately, explains the exact point of confusion, and distinguishes general mechanisms from documented details of the user's appliance.

**Availability and implementation matter more than a landing-page promise.** Curiso's about page advertises unlimited free generation while its homepage currently says generation is paused. Lumi's marketing describes a broad animated learning platform; its repository marks rendering and mobile components as planned. These are useful alternatives to examine, but neither establishes a measured, reliable service matching the proposed product.

**A catalog and custom generation have different economics.** Reviewed explanations can be authored once and replayed many times. A fresh diagram, artifact, or video for each request repeats inference, rendering, and validation work. Free consumption does not require free unlimited creation.

## Alternatives

“Opportunity” below is our product hypothesis. It is not a claim that a competitor lacks a feature outside the pages reviewed. No accounts were created, payments made, or full applications benchmarked.

| Alternative | What the primary source establishes | Price or access observation | Implication for Inside |
| --- | --- | --- | --- |
| [Visual Learning](https://visual-learning.app/) | 15 everyday-machine lessons; [washer](https://visual-learning.app/washing-machine) has steps, auto/manual controls, readings, and a cutaway | Public HTML accessible without sign-in during retrieval | Closest direct alternative. Ten machine lessons alone are a weak reason to pay. Test whether question-specific teaching and evidence-linked personalization add value. |
| [Bartosz Ciechanowski](https://ciechanow.ski/internal-combustion-engine/) | Detailed engine explanation with interactive illustrations and controls | Article publicly accessible | A high bar for explanatory craft. Borrow the connection between a manipulated variable and its consequence, not the article's artwork or code. |
| [Mozaik and mozaik3D](https://www.mozaweb.com/en/lexikon.php?cmd=getlist&let=3D) | A broad interactive 3D scene library within an education platform | [Main site](https://www.mozaweb.com/en_US/index.php) advertises student access “from 26 EUR”; term, tax, and region were not resolved in the fetched checkout | Competes strongly on breadth. Do not compete by building a smaller general school library. |
| [Tinybop Simple Machines](https://tinybop.com/apps/simple-machines) | Manipulable levers, pulleys, and other elementary mechanisms for children | [US App Store](https://apps.apple.com/us/app/simple-machines-by-tinybop/id936966570) listed $2.99 | A paid native learning experience can work without customer inference. Child-oriented play is an adjacent segment, not our first audience. |
| [PhET](https://phetsims.colorado.edu/en/about) | Free interactive science and math simulations; HTML5 and downloadable use | Free simulations | Interactivity and offline access are established expectations. Our hypothesis is faster application of mechanisms to familiar appliances. |
| [Brilliant](https://brilliant.org/faq/) | Interactive STEM problem-solving within a curriculum | [Official pricing help](https://brilliant.org/help/pricing-and-plans/) describes limited free access and Premium; no stable regional dollar quote extracted | A subscription needs recurring value. A catalog used occasionally has a different demand pattern from ongoing study. |
| [JigSpace](https://www.jig.com/) | 3D/AR presentations and product explanations | [Free plan](https://www.jig.com/help-center/free-plan-limits): evaluation/non-commercial, one Jig per user, three steps per Jig, public visibility only | Relevant authoring alternative. Importing and presenting a model is different from answering an appliance question for an unprepared consumer. |
| [Curiso](https://www.curiso.app/about) | Topic/PDF to narrated Manim video pipeline | About page claims free unlimited generation; [homepage](https://www.curiso.app/) currently says generation is paused | Benchmark existing output before building a broad video generator. The pause does not prove a cost problem; the stated reason is infrastructure improvements. |
| [Lumi](https://lumi.study/) | Marketing describes personalized animated lessons, editable storyboards, and multiple providers with user-supplied keys | Site describes MIT/open-source software plus BYOK; provider/hosting costs remain separate | Potential reusable ideas, not a proven substitute. [Repository](https://github.com/humzakhan/lumi) defaults to mock AI; rendering, ingestion, and mobile components are marked planned. |
| [Google NotebookLM video overviews](https://support.google.com/notebooklm/answer/16454555?hl=en) | Source-based generated videos, formats/styles, playback controls, and optional producer-note review | Help now redirects to “Gemini Notebook”; advanced co-creation is documented for AI Ultra. No general access price inferred | Strong substitute for turning a manual into a video. Our possible advantage is an inspectable mechanism and a short path to one causal answer. |
| [Claude interactive explanations](https://academy.claude.com/use-cases/visualize-the-mechanism-behind-an-explanation-mid-chat) | Inline interactive visuals, variable controls, follow-ups, and quizzes | Feature evidence only; plan/region availability and price were not benchmarked | A dedicated app cannot rely on “AI makes a visual” as its differentiator. Repeatable quality and ready-to-use lessons matter. |
| [Lesics](https://www.lesics.com/) | Engineering animation services | Reviewed page does not establish a consumer subscription price | Professionally produced engineering explanation is an alternative content source and a possible production reference. No content-reuse right inferred. |
| [iFixit](https://www.ifixit.com/) | Free step-by-step repair guides and a repair community | Guides publicly accessible; tools/parts are separate offerings | Stronger alternative when the user's actual goal is repair. Inside should acknowledge that goal rather than disguise a generic lesson as diagnosis. |

## Tools and early candidates

[Anatomy](https://github.com/wheresryan22/anatomy) is the authoring toolkit already inspected and used locally. It is not an end-user explanation service. Its MIT license does not grant rights to other creators' lesson content, product manuals, images, or trademarks.

[AnimLearn](https://animlearn.com/) appeared in discovery with descriptions of educational animation and classroom tools. Direct retrieval returned a JavaScript-required shell, so capabilities, pricing, and production availability were not verified. It remains a follow-up candidate, outside the verified comparison.

## What to compete on

The first segment is someone who has just asked a specific causal question about an everyday machine and found either too much terminology or an answer they cannot visualize. Reach them through that question: a shareable lesson titled “Why the washer spins fast at the end” is a clearer entry point than a general AI-learning homepage.

The proposed advantage has three parts to validate together: a reviewed mechanism visible within seconds; follow-up questions that manipulate or highlight the current mechanism; and exact-machine annotations whose evidence can be inspected. None is sufficient alone. The third is harder to deliver and is not assumed available at first release.

There is no evidence here of unmet willingness to pay, market size, retention, or superior learning outcomes. Those require user sessions and real purchasing choices. Public feature pages establish competition; they do not establish demand for Inside.

## Experiments before major implementation

1. **Replaceability test.** Give 12 adults two appliance questions each. Counterbalance Inside against Visual Learning or a selected existing explanation of the same mechanism. Measure a short transfer question, time to the first useful explanation, and whether they would keep using Inside. Where possible also compare the participant's actual current method.
2. **Specificity test.** Ask five owners to supply a model number and public manual. Determine which facts genuinely change the explanation. Stop if personalization mostly changes names and cosmetic details.
3. **Frequency test.** Ask participants to record real questions for two weeks. Count unprompted occasions and which alternative they used. Avoid asking whether they would theoretically use an attractive demo.
4. **Payment test.** After successful use, offer a real, clearly scoped content pack once the product and purchase flow exist. Compare a one-time pack with an optional capped service. Interview non-buyers about their actual alternative.
5. **Production test.** Author three different mechanism families and record all review minutes, model usage, failures, and corrections. The cost of one polished demonstration is not enough to price generation.

## Research limits

This is a broad primary-source market scan, not an exhaustive census or a hands-on performance ranking. Full account flows, feature quality, retention, revenue, regional checkout prices, and every model-specific claim were not tested. Public listings change; recheck pricing and availability before a release decision. No competitor source was imported into the app.
