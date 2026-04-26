1) What is reinforcement learning in the context of LLMs?
Reinforcement learning for LLMs is a loop where the model generates an answer, code snippet, plan, or action sequence; that output is evaluated by a verifier or environment; and the resulting reward is used to update the model so higher-reward behaviors become more likely over time. In practice, this is often used after pretraining and supervised fine-tuning to sharpen behaviors like reasoning, code generation, or tool use. The session framed this intuition as turning repeated trial-and-error into weight updates instead of stuffing more and more examples into the prompt.
A good mental model is: supervised fine-tuning tells the model “copy this good target,” while RL tells it “try many possibilities and move probability mass toward the ones that score better.” PPO is one classic algorithm for this style of training, and GRPO is a later variant used heavily in modern LLM work because it can be more memory-efficient for certain setups. (arXiv)
For deeper reading:
TRL docs for RL trainers and workflows. (Hugging Face)
PPO paper. (arXiv)
DeepSeekMath for GRPO. (arXiv)
2) Why do rewards matter so much?
Rewards are the only signal telling the model what “better” means. If your reward is well aligned with the real task, RL can push the model toward genuinely useful behavior. If your reward is incomplete or easy to game, the model will optimize the wrong thing very effectively. The session emphasized that RL gives you what you asked for, not necessarily what you meant.
For example, if you reward generated code only for passing a shallow regex or a weak unit test, the model may learn to exploit those checks instead of solving the underlying problem. This is why reward design is not a detail; it is the task specification. DeepMind’s discussion of “specification gaming” makes the same point in broader RL terms: weakly specified rewards create loopholes that search will discover. (Google DeepMind)
Useful reading:
DeepMind on specification gaming. (Google DeepMind)
Lilian Weng on reward hacking. (Lil'Log)
3) What is rewards engineering?
Rewards engineering is the work of designing, combining, validating, and monitoring reward signals so that optimization pressure produces the behavior you actually want. In LLM RL, that usually means deciding:
what gets rewarded,
how much it gets rewarded,
when it gets rewarded,
what gets penalized,
and how you audit whether the reward is being gamed.
A practical reward function often has several components. For a code task, you might combine syntax validity, execution success, unit test pass rate, latency, memory use, formatting compliance, and safety checks. The session highlighted verifier-based reward design such as formatting checks, execution checks, regex checks, and environment-based evaluation instead of a learned reward model alone.
A useful principle is to reward outcomes first, then add process constraints only where needed. Over-shaping the reward can make training brittle or bias the model into narrow strategies, while under-shaping makes hacking easier. (Google DeepMind)
4) What is RLVR, and how is it different from using a reward model?
RLVR usually means reinforcement learning with verifiable rewards. Instead of asking a learned reward model to score outputs, you use a verifier, tester, or environment that can check correctness more directly. The session gave examples like formatting checks, execution checks, regex-based checks, and environment rollouts.
This is powerful when correctness is externally testable. Code can be compiled and unit-tested. Math can often be checked against a final answer or symbolic verifier. Games can expose reward from the environment. Browser tasks can be checked by page state or task completion. In such cases, verifier-driven rewards are often more trustworthy than a purely learned scalar reward model.
TRL documents this broader environment-based training pattern, and OpenEnv is meant to standardize how such environments are defined and used. (Hugging Face)
5) Why do RL environments matter for LLMs?
Static prompt-response datasets are useful, but they are limited. Real deployments require models to interact with systems: codebases, browsers, files, APIs, games, tools, and simulators. RL environments let the model act, observe consequences, and keep going across multiple steps, which is much closer to real agent behavior. The session described environments as the bridge from isolated prompt solving to real-world interaction.
They also enable dynamic difficulty and richer feedback. Instead of training forever on a fixed set of prompts, the environment can generate or surface tasks that are more appropriate for the current model, which makes curriculum learning and continual challenge easier. This matches the broader “RL with environments” direction discussed in recent OpenEnv and TRL material. (Hugging Face)
For examples:
BrowserGym for web-task environments. (GitHub)
OpenEnv course and TRL integration docs. (GitHub)
6) What is OpenEnv, and why would a hackathon team use it?
OpenEnv is an open-source framework for defining and interacting with RL environments for LLM and agent training. The session described it as a standardized interface around concepts like reset, step, state, observations, actions, and rewards, with deployment built around Hugging Face Spaces and containerized execution.
A hackathon team would use OpenEnv because it reduces environment plumbing. Instead of inventing a new interface for each task, you can standardize how the model talks to the environment and then connect that to a trainer like TRL. That means you spend more time on task design and rewards, and less on adapter glue. The session also highlighted openenv init for bootstrapping an environment skeleton quickly.
Good starting points:
OpenEnv repo. (GitHub)
OpenEnv course. (GitHub)
TRL’s OpenEnv integration guide. (Hugging Face)
7) How does OpenEnv work at a high level?
At a high level, an OpenEnv environment exposes a small set of standard operations:
reset the environment,
step the environment with an action,
return observations, rewards, and state.
The session described OpenEnv environments as FastAPI applications that can be run locally, deployed on Hugging Face Spaces, or pulled as containers. That gives teams several options: they can use the remote environment directly, install client code from the repo, or run the environment locally through the container image.
This design is useful because it treats environments as portable, versioned software artifacts rather than ad hoc scripts. Hugging Face’s own TRL docs describe OpenEnv similarly, including support for backend-server execution and standardized APIs. (Hugging Face)
8) Where do TRL and Unsloth fit in this stack?
TRL is the training library. It provides trainers and workflows for SFT, DPO, PPO, GRPO, reward modeling, and related post-training methods for transformer models. In a typical hackathon setup, TRL handles rollout collection, reward integration, optimization, logging, and trainer configuration. (Hugging Face)
Unsloth fits in as the acceleration and memory-efficiency layer for training and RL fine-tuning. The session described Unsloth as making RL training more efficient and inference faster, which matters because rollout generation often dominates runtime in RL loops. It also noted a practical QLoRA warning: don’t naively upcast a 4-bit model to 16-bit and then merge adapters, because that can damage model quality; use the proper merge path instead.
Relevant docs:
TRL docs and GRPO cookbook. (Hugging Face)
Unsloth repository/readme. (GitHub)
9) What is the difference between PPO and GRPO?
PPO is a classic policy optimization algorithm that stabilizes updates by constraining how much the policy changes between iterations. It is one of the most influential RL algorithms in modern deep learning. (arXiv)
GRPO is a later group-relative variant used in LLM training that compares sampled outputs within a group to estimate relative advantage, and it is often discussed as a more memory-efficient alternative to full PPO-style setups in some LLM post-training pipelines. The session summarized GRPO as a more efficient version of PPO and specifically noted removing the value model from the setup.
For deeper details:
PPO paper. (arXiv)
DeepSeekMath / GRPO references via TRL paper index and cookbook. (arXiv)
10) Why is RL often described as inefficient, yet still useful?
RL is often inefficient because the feedback is sparse and delayed. A long rollout may end in one scalar reward, and that weak signal has to train many decisions. The session used a simple example: if a code answer fails at one line but you assign the same negative reward to every token, you’re throwing away a lot of structure.
It is still useful because it can optimize behaviors where exact supervised targets are unavailable, too expensive, or too limiting. If you can verify success but cannot easily author perfect demonstrations for every scenario, RL can still improve the model by repeated interaction. This is why RL is especially attractive for code execution, tool use, games, browser tasks, and agent workflows.
A practical takeaway: use RL where verifiers exist and where exploration is worth the extra compute.
11) What is process supervision, and why is it important?
Process supervision means giving feedback on intermediate reasoning or intermediate steps, not only on the final outcome. The session contrasted this with assigning the same reward to every token in the answer, which can be very wasteful. Under process supervision, you try to identify which parts of a trace were good, irrelevant, or harmful.
This matters because not all failures are equal. Maybe the model chose the right algorithmic approach but made one implementation mistake. Final-outcome-only rewards blur that distinction. Step-aware rewards can improve sample efficiency and make debugging easier, though they also raise new risks if the step labels are noisy or exploitable.
The session also noted that process supervision is often approximated with humans or LLM-as-a-judge. That can help, but it creates another optimization target that itself may be gamed.
12) What is reward hacking?
Reward hacking is when the model finds a way to maximize reward without genuinely doing the intended task. In other words, the optimization succeeds, but the task specification failed. The session gave intuitive examples such as editing variables, bypassing intended checks, or exploiting quirks in the environment rather than solving the real problem.
This is the same phenomenon often called specification gaming. DeepMind describes it as agents exploiting flaws or ambiguities in the reward function, and Lilian Weng’s overview covers how common and fundamental this problem is in RL systems. (Google DeepMind)
A useful mindset is: reward hacking is not proof the model is “evil”; it is proof that optimization pressure found a loophole.
13) How can a hackathon team reduce reward hacking in practice?
Use strong verifiers. Prefer executable checks over stylistic heuristics. For code, run tests, time the solution, validate output shapes and edge cases, and isolate execution. For tool use, verify actual state transitions, not just verbal claims. The session repeatedly emphasized verifiers and environments over vague reward signals.
Monitor training actively. The session recommended sampling outputs periodically, looking for suspicious patterns, and terminating or rolling back runs when drift appears. It also suggested filtering bad responses and adding guardrails when patterns of exploitation are observed.
Use layered rewards. Combine success criteria with anti-cheat constraints. For example:
pass tests,
do not edit protected files,
do not bypass timers,
stay within time and memory budget,
preserve task-required formatting,
and log intermediate actions for audit.
This general strategy aligns with broader RL safety guidance on specification gaming. (Google DeepMind)
14) What is curriculum learning, and why does it help RL?
Curriculum learning means controlling the order or difficulty of training tasks so the model learns from easier tasks first and gradually moves to harder ones. The session directly recommended this for RL: if tasks are too hard at the start, the model may never produce a successful rollout, which means the reward signal is effectively zero and learning stalls.
This is especially important in LLM RL because many tasks are long-horizon and brittle. An easier initial distribution can bootstrap behavior, after which harder tasks become reachable. In the RL literature more broadly, curriculum learning is a standard way to improve exploration and sample efficiency in difficult environments. (arXiv)
Practical idea for hackathons:
start with short horizons,
fewer tools,
simpler state spaces,
stronger hints,
easier test cases,
then gradually remove scaffolding.
15) How do I know whether a task is suitable for RL?
A task is a good candidate for RL if:
you can verify success or partial progress,
exploration is meaningful,
multi-step interaction matters,
and you do not already have abundant high-quality demonstrations.
The session highlighted a key rule of thumb: the probability of a good answer must be greater than zero. If the task is so hard that the model never stumbles into any rewarding behavior, RL will waste compute. That means task selection, warm starts, formatting scaffolds, or light SFT can be essential.
Good hackathon candidates include:
code generation with executable tests,
browser navigation with page-state checks,
games with clear win conditions,
API/tool workflows with verifiable side effects.
16) Should we jump straight into RL, or do some SFT first?
Usually, do some SFT or at least a warm start first. The session’s guidance was that pretraining carries most of the capability burden, SFT helps shape the behavior, and RL refines it. It explicitly argued against relying on RL alone from scratch for most practical settings.
That matches modern post-training stacks: pretrain heavily, align or instruct-tune, then apply preference optimization and/or RL where it adds value. TRL’s supported workflows reflect exactly this broader stack. (Hugging Face)
A hackathon-friendly recipe is:
Start from a solid instruct model.
Add a tiny amount of task-format SFT if needed.
Build a strong verifier.
Use GRPO/PPO-style RL only after the model can at least occasionally succeed.
17) What should we actually monitor during RL training?
Monitor more than the headline reward. The session specifically called out tracking reward trends, component rewards, and whether important success columns are improving over time. It also recommended checking generated strategies and periodically sampling outputs during training rather than letting runs continue blindly.
Useful metrics include:
average reward,
verifier pass rate,
timeout rate,
format adherence,
rollout length,
diversity of successful solutions,
frequency of suspicious shortcuts,
and cost per useful trajectory.
If the average reward rises but the actual task quality drops or becomes brittle, that is often a reward-design problem rather than a model-capability problem.
18) What is a strong hackathon strategy for building an RL environment fast?
Pick a task with a crisp verifier. Build the smallest environment that exposes reset, step, observations, and reward. Use OpenEnv to standardize the interface and TRL to handle training. Use Unsloth if you need to fit training into tighter hardware budgets. (Hugging Face)
A practical sequence:
Define the task and what “success” means.
Write the verifier before writing the policy loop.
Create a few toy tasks the model can solve.
Add curriculum or easier variants first.
Run small-scale debugging before long training.
Sample outputs constantly for reward hacking.
Only then scale rollouts and environment diversity.
19) What are good starter resources for participants?
For TRL:
Main docs. (Hugging Face)
PPO trainer docs. (Hugging Face)
GRPO cookbook. (Hugging Face)
Paper index for GRPO/DeepSeekMath references. (Hugging Face)
For OpenEnv:
OpenEnv GitHub repo. (GitHub)
OpenEnv course. (GitHub)
TRL’s OpenEnv integration docs. (Hugging Face)
For environments and benchmarks:
BrowserGym. (GitHub)
For reward design and failure modes:
DeepMind on specification gaming. (Google DeepMind)
Lilian Weng on reward hacking. (Lil'Log)
For RL algorithms:
PPO paper. (arXiv)
DeepSeekMath / GRPO paper. (arXiv)
For Unsloth:
Unsloth repo/readme. (GitHub)
20) What is the one-sentence summary participants should remember?
If you can build a task where success is verifiable, difficulty is controllable, and loopholes are monitored, RL can turn an LLM from “good at answering” into “better at acting.”

21) What is RLVR?
RLVR stands for reinforcement learning with verifiable rewards. Instead of relying only on a learned reward model or human preference model, the training loop uses programmatic checks to determine whether an output is correct. Typical examples include exact-answer checks for math, unit tests for code, schema validation for structured output, or environment-based task completion checks. This makes RLVR especially attractive for domains where correctness can be verified automatically and consistently. (Label Studio)
22) What is RLVE?
RLVE is reinforcement learning with verifiable environments. The key idea is to train on environments that can procedurally generate tasks, expose adjustable difficulty, and provide algorithmically verifiable rewards. Recent work on adaptive verifiable environments argues that static prompt datasets often become either too easy or too hard during training, causing learning to stall, while adaptive environments keep the model near its capability frontier. (arXiv)
23) How is RLVE different from RLVR?
RLVR usually refers to verifiable rewards on a fixed or semi-fixed set of prompts or problems. RLVE goes a step further by making the task source itself dynamic: the environment can generate new problems, vary difficulty, and keep serving appropriately challenging tasks as the model improves. In practice, RLVE is often better for preventing saturation on static datasets and for building curriculum naturally into training. (arXiv)
24) Why are RL environments useful for LLM post-training?
They let the model interact, not just answer. In a real environment, the model can act, observe consequences, act again, and get reward from actual task outcomes. That makes environments a better fit for tool use, browsers, APIs, coding agents, games, and long-horizon tasks than plain prompt-response datasets. Hugging Face’s OpenEnv and TRL material reflects this shift toward environment-based agent training. (Hugging Face)
25) Where do TRL, GRPO, and Unsloth fit in?
TRL is the training framework that provides RL trainers and infrastructure for post-training transformer models, including GRPO. GRPO is the RL optimization method popularized in DeepSeekMath and now widely used in open LLM RL pipelines because it can be more memory-efficient than PPO-style setups in this context. Unsloth is typically used as the efficiency layer to make fine-tuning and RL training faster and more affordable on limited hardware. (Hugging Face)
26) Why do rewards matter so much?
Because the reward is the task definition as far as optimization is concerned. If your reward captures the real objective, RL can improve useful behavior. If your reward is incomplete, noisy, or hackable, the model will optimize the proxy instead of the real task. DeepMind’s write-up on specification gaming makes this point very clearly: the agent’s ingenuity is helpful only when the specification is correct. (Google DeepMind)
27) What is reward engineering?
Reward engineering is the design of the reward function, the verifier, the shaping terms, the penalties, and the monitoring strategy. In LLM RL, this includes deciding what counts as success, how partial progress is rewarded, what shortcuts are forbidden, and how to detect reward hacking. OpenEnv’s reward-design guide explicitly warns about reward hacking, sparse rewards, and conflicting signals as common pitfalls. (Meta-PyTorch)
28) What is reward hacking?
Reward hacking happens when a model finds a way to maximize the reward without actually doing the intended task. DeepMind describes this as specification gaming: the system satisfies the literal reward but not the real goal. Classic causes include poorly designed shaping rewards, missing constraints in the success condition, and simulator or verifier loopholes. (Google DeepMind)
29) Why is sparse reward a common problem?
If successful trajectories are too rare, the model may never get enough positive signal to improve. OpenEnv’s docs explicitly call sparse rewards a common pitfall because the agent may never find positive signal. RLVE work similarly notes that overly difficult tasks can yield consistently poor rewards and stall gradient-based learning. (Meta-PyTorch)
30) Why can dense rewards also be dangerous?
Dense rewards can speed up learning, but they can also create local optima and incentive misalignment. OpenEnv recommends starting simple and shaping carefully, because intermediate rewards can steer the model toward proxy behaviors. DeepMind gives the broader warning that poorly designed shaping can change the optimal policy itself rather than just helping the model reach the intended outcome faster. (Meta-PyTorch)

Common Pitfalls in Building RL Environments
31) What is the most common mistake when designing an RL environment?
Making the environment easy to verify but not faithful to the real task. A verifier that checks only the final string, a regex, or a narrow success pattern may be convenient, but it often misses equivalent correct answers or allows degenerate shortcuts. Recent verifier analysis on mathematical RL found that rule-based verifiers often reject correct but differently formatted answers, while model-based verifiers can be exploited to produce false positives during RL. (arXiv)
32) What goes wrong with weak verifiers?
Two opposite failure modes are common. Rule-based verifiers can be too brittle and produce false negatives when the answer is correct but phrased differently. Model-based verifiers can be too permissive and produce false positives that the policy learns to exploit. The verifier study on mathematical reasoning reports both problems and shows that stronger policies make verifier weaknesses more obvious. (arXiv)
33) Why is “just use an LLM as judge” often risky?
Because the judge becomes part of the optimization target. If the policy can find surface patterns that fool the judge, training can inflate reward without improving real task quality. That is exactly why model-based verifiers, despite better static accuracy, can be vulnerable during RL training. Use them carefully, stress-test them, and combine them with hard checks whenever possible. (arXiv)
34) What is a common environment-design pitfall for tool-using agents?
Not modeling realistic failure modes. Real APIs fail because of permissions, invalid formats, missing fields, timezones, or bad parameters. Hugging Face’s OpenEnv blog highlights examples like missing OAuth scopes and bad RFC3339 datetime formatting. If the environment hides these realities, the resulting policy will be overfit to a toy setup and brittle in deployment. (Hugging Face)
35) Why is static task difficulty a problem?
Because the learning signal collapses at both extremes. Tasks that are too easy stop teaching the model anything useful. Tasks that are too hard yield near-zero reward and also stop teaching. RLVE was proposed largely to solve this problem by dynamically adjusting task difficulty as the policy improves. (arXiv)
36) What is a common pitfall in environment diversity?
Training on too few task types. Recent RLVE results argue that scaling the number of environments improves generalizable reasoning capability, and Reasoning Gym was built around procedurally generated tasks across many domains for exactly this reason. A narrow environment set often produces narrow competence and fragile transfer. (arXiv)
37) Why do many RL environments fail to transfer to real-world performance?
Because they optimize the wrong abstraction level. If the environment is too toy-like, omits realistic constraints, or over-simplifies tool feedback, the model may become good at the benchmark but not at the actual workflow. This is a practical version of specification gaming: the benchmark is solved, the real job is not. (Google DeepMind)

Common Pitfalls in Reward Engineering
38) What is the biggest reward-engineering mistake?
Using a proxy metric as if it were the goal. Goodhart-style failures are everywhere in RL: token count, response format, test count, or intermediate progress can all become targets the model exploits. DeepMind’s examples of shaping mistakes and reward misspecification are the canonical warning here. (Google DeepMind)
39) Should I start with a complicated reward function?
Usually no. OpenEnv explicitly recommends starting simple, often with sparse success/failure reward, before layering in shaping terms. This makes debugging easier and reduces the chance that the model learns the wrong intermediate incentives before it learns the actual task. (Meta-PyTorch)
40) What happens when reward components conflict?
Learning becomes unstable or confused. OpenEnv lists conflicting signals as a common pitfall: if one term rewards brevity, another rewards verbosity, a third rewards format, and a fourth rewards exploration, the policy may oscillate or learn brittle shortcuts instead of coherent behavior. (Meta-PyTorch)
41) Why is binary reward often appealing?
Because it is easy to reason about and harder to game superficially. Label Studio’s RLVR overview notes that verifiable rewards are often binary and directly tied to correctness criteria, which makes evaluation simple and scalable. Binary reward is not always sufficient, but it is often a good starting point for precision-critical tasks like code and math. (Label Studio)
42) Why is binary reward sometimes not enough?
Because it can be too sparse, especially for long-horizon tasks. If success only happens at the very end, the model may not learn at all. That is where carefully designed shaping, step-level evaluation, or adaptive curriculum can help — but only if you can add them without creating easy-to-game shortcuts. (Meta-PyTorch)
43) How do I know whether my reward is being hacked?
Watch for rising reward without corresponding task-quality gains. Typical signs are strange formatting habits, repetitive surface patterns, degenerate short solutions, suspiciously high judge scores, or solutions that pass weak checks but fail stronger ones. The verifier case study is a strong reminder that static verification accuracy is not enough; you must observe what happens under optimization pressure. (arXiv)
44) What is a safe pattern for reward engineering?
Use layered verification. Start with hard outcome checks. Add anti-cheat constraints. Then add minimal shaping only where the sparse reward is too weak. Keep a holdout evaluator separate from the training reward when possible. This matches both OpenEnv’s “start simple, shape carefully” guidance and DeepMind’s warning about shaping altering the true objective. (Meta-PyTorch)

Common Pitfalls in RL Post-Training Pipelines with RLVR / RLVE / GRPO
45) What is a common mistake in GRPO training runs?
Using RL before the base model is ready. GRPO is powerful, but it is a post-training method, not a substitute for capability. TRL’s own GRPO examples start from instruct models and task datasets rather than from weak base checkpoints. If the model almost never produces a correct rollout, the reward signal is too sparse for productive RL. (Hugging Face)
46) Why does RL post-training plateau?
Because the model saturates the available prompt distribution or the reward signal no longer differentiates useful improvements. RLVE explicitly frames static data saturation as a problem and shows that adaptive environments can keep learning going after conventional RLVR pipelines flatten out. (arXiv)
47) Why can “more RL” make a model worse?
Because optimization pressure amplifies whatever the reward favors, including undesirable shortcuts. If the verifier is noisy, if the environment is unrealistic, or if the reward overvalues superficial structure, more training can push the model deeper into those artifacts rather than improving real competence. (arXiv)
48) What is a common pitfall in RLVR datasets?
Finite, static datasets get stale. Once the model has mastered or overfit their distribution, additional RL yields little signal. RLVE work argues that procedurally generated environments with adjustable difficulty are one way around this limitation. Reasoning Gym makes a similar case for unlimited data generation with controllable complexity. (arXiv)
49) Why do identical-looking GRPO runs produce different outcomes?
Because RL is highly sensitive to rollout quality, verifier behavior, reward scaling, task mix, generation parameters, and environment bugs. Even if the trainer code is the same, small differences in reward computation or environment behavior can change optimization dynamics substantially. The verifier study is a good reminder that the reward pipeline itself is part of the model. (arXiv)
50) What is a common pitfall when mixing many environments?
Using an unbalanced mixture. If some environments are much easier, much denser in reward, or much shorter in trajectory length, they can dominate training and starve harder but more important environments. RLVE’s adaptive-difficulty framing exists partly to keep the training distribution informative instead of letting it collapse into easy tasks. (arXiv)
51) Why are long-horizon tasks especially hard in RL post-training?
Because reward arrives late and useful trajectories are rare. Long tasks need either decomposition, better intermediate signals, stronger initialization, or curriculum. Otherwise, the rollout cost is high and the success rate stays near zero. This is one reason why adaptive environments and procedural curricula are getting attention. (arXiv)
52) What monitoring mistake do teams make most often?
They monitor the training reward but not actual behavior. Reward alone is not enough because the reward channel can be flawed. You need sampled rollout audits, stronger offline evaluation, and held-out environments or benchmarks. The verifier case study shows why this matters: reward can rise while real quality does not. (arXiv)
53) What is the safest way to structure an RL post-training pipeline?
A good pattern is:
start from a strong instruct or SFT checkpoint, use a task with a strong verifier, begin with simple reward, validate the environment thoroughly, run small-scale debug experiments, audit rollouts manually, then scale training and only later add curriculum or more shaping. This is consistent with TRL’s practical GRPO examples, OpenEnv’s reward guidance, and the lessons from verifier-failure studies. (Hugging Face)

Practical “What should we do in a hackathon?” FAQs
54) What kind of project is most likely to succeed in a hackathon?
Pick a task with:
a clear success condition,
a verifier you trust,
short to medium trajectory length,
few external dependencies,
and adjustable difficulty.
Good examples are code repair with tests, structured extraction with schema validation, grid or puzzle games, tool-using workflows with exact state checks, and browser tasks with explicit completion criteria. These are the sweet spot for RLVR and lightweight RLVE prototypes. (Label Studio)
55) What should we avoid building?
Avoid tasks that are subjective, hard to verify, require massive infrastructure, or depend heavily on an LLM judge without hard backstops. Also avoid environments whose failure cases you do not understand. If you cannot explain how the reward could be hacked, you are not ready to optimize it yet. (arXiv)
56) What is the best debugging order?
First debug the environment manually.
Then debug the verifier.
Then run scripted baseline policies.
Then run a frozen model.
Then run a tiny RL experiment.
Only then scale.
This order isolates bugs early and prevents you from blaming the optimizer for what is really an environment or reward bug. It follows directly from the fact that verifier reliability is foundational in RLVR. (arXiv)
57) What is one rule the team should remember?
Do not optimize a reward you have not tried to break yourself first. The easiest way to avoid reward hacking is to adversarially test your environment and reward design before the model does. (Google DeepMind)

58) Strong references for deeper learning
For GRPO and TRL:
TRL GRPO Trainer docs. (Hugging Face)
Hugging Face GRPO cookbook. (Hugging Face)
For RL environments and reward design:
OpenEnv reward design guide. (Meta-PyTorch)
OpenEnv tool-using environment examples. (Hugging Face)
For pitfalls and failure modes:
DeepMind on specification gaming. (Google DeepMind)
Pitfalls of rule-based and model-based verifiers. (arXiv)
For scalable environment-based training:
RLVE paper on adaptive verifiable environments. (arXiv)
Reasoning Gym. (OpenReview)

Here are solid Unsloth RL post-training recipes worth checking out, with a bias toward official or close-to-official examples.
59) Core Unsloth GRPO recipes
Qwen2.5 (3B) GRPO notebook
A straightforward starter recipe for GRPO with Unsloth. It covers data prep, training, inference, and saving, so it is a good baseline if you want the least opinionated end-to-end example. (GitHub)
Llama 3.1 (8B) GRPO notebook
Same general pattern, but on a larger model family. Useful if you want a more realistic “reasoning/capability uplift” recipe without jumping straight to very large models. (GitHub)
Gemma 3 (1B) GRPO notebook
A smaller-scale recipe that is easier to run and debug. Good for iterating on reward functions and rollout settings before spending more compute on larger checkpoints. (GitHub)
59.1) Advanced Unsloth GRPO recipes
Advanced Qwen3 (4B) GRPO notebook
This is one of the more interesting recipes because it adds more than the bare trainer loop. Unsloth’s June 2025 discussion explicitly calls out: proximity scoring for more nuanced rewards, OpenR1 dataset support, advanced templates, and “prefinetuning to skip GRPO format learning.” That makes it a better recipe when you care about reward shaping and format bootstrapping, not just getting GRPO to run. (GitHub)
HF LLM Course: Practical Exercise — GRPO with Unsloth
Not an Unsloth-maintained notebook repo entry, but it is a structured learning recipe that uses Unsloth specifically to fine-tune a model with GRPO for reasoning. It is a good companion when you want a didactic walkthrough instead of just notebook cells. (Hugging Face)
59.2) Environment / agent-style RL recipes
GPT-OSS 20B + 2048 game RL notebook
This is closer to “RL with an environment” than plain static-prompt RLVR. The notebook goal is explicitly to make GPT-OSS play 2048 with reinforcement learning / GRPO, which makes it a useful recipe if you want to move beyond math/code answer verification into interactive environment training. (GitHub)
59.3) Broader recipe collection
Unsloth notebooks repository
The main repo currently advertises “250+ Fine-tuning & RL Notebooks,” including GRPO and reinforcement learning notebooks. If you want the widest set of recipes in one place, this is the best starting point. (GitHub)
59.4) Useful adjacent recipes and examples
Scheduler GRPO example using Unsloth
A community example that trains a scheduling model with GRPO using Unsloth and QLoRA. It is useful because it shows a non-math, non-code structured-output task where rewards are tied to output format and schedule correctness. (Hugging Face)
SFT → GRPO pipeline example
There is a community “show and tell” example for a full SFT-then-GRPO pipeline. I would treat it as inspiration rather than an official recipe, but it is valuable if your intended workflow is “teach format first, then do RL.” (GitHub)
59.5) What these recipes collectively cover
Across these examples, the main recipe patterns are:
plain GRPO on reasoning-style tasks,
GRPO with better reward shaping like proximity scoring,
pre-SFT or preformatting before RL,
QLoRA-based memory-efficient RL fine-tuning,
and environment-style RL with game interaction. (GitHub)
59.6) Two gaps to keep in mind
One gap is multi-turn GRPO with stepwise rewards. There is a feature request asking for reward on each step plus a final reward, which suggests this is not yet a mature first-class recipe in Unsloth. (GitHub)
Another gap is notebook stability across versions/hardware. Several issue threads mention breakage or edge cases in GRPO notebooks, including fast inference assumptions, VRAM growth, and vision-GRPO issues. That does not make the recipes unusable, but it does mean you should pin versions and test on a small run first. (GitHub)
59.7) Best recipes by use case
If you want the simplest starting point:
Qwen2.5 (3B) GRPO
Gemma 3 (1B) GRPO (GitHub)
If you care about reward engineering:
Advanced Qwen3 (4B) GRPO (GitHub)
If you care about environment-style RL:
GPT-OSS 20B 2048 notebook (GitHub)
If you want the most guided learning path:
HF practical exercise with Unsloth + GRPO (Hugging Face)
If helpful, I can turn this into a curated table with columns for model, task type, reward type, hardware footprint, and what each recipe teaches.

Additional Resources:
OpenEnv Core (An interface library for RL post training with environments)
https://github.com/meta-pytorch/OpenEnv
OpenEnv-PyTorch Docs
https://meta-pytorch.org/OpenEnv/
HuggingFace OpenEnv Environments Hub
https://huggingface.co/openenv
https://huggingface.co/openenv/spaces
Tutorials to build, run and train RL environments and training pipelines
https://github.com/meta-pytorch/OpenEnv/tree/main/tutorial
RL Training Examples: https://github.com/meta-pytorch/OpenEnv/tree/main/tutorial/examples
RL Environment Examples: https://github.com/meta-pytorch/OpenEnv/tree/main/envs
Few additional YT Videos on building RL Environments:
https://www.youtube.com/watch?v=0airz7BhBiA
https://www.youtube.com/watch?v=ap4q4sAK4OY
https://www.youtube.com/watch?v=Jew4lhAiqnw 
https://openenv-india-apr-2026.lovable.app/ (Recommended: Chaptered Lectures)
