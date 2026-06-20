# Rationale (short description)

Insurers deny claims knowing most people never appeal. The deadline is buried, the policy is hard to read, and the people hurt most are often the sick, the elderly, and those who do not read insurance English fluently. Yet many denials are overturned when someone actually appeals.

ClaimMate is an agent that does that work with you, not for you. You give it the denial letter and your plan. It reads them, surfaces the appeal deadline and the days remaining, and finds the exact plan clause that supports coverage. If no clause supports you, it says so honestly instead of inventing one. It drafts a citation-grounded appeal and refuses to finalize anything without your approval.

The design choice I care about most is honesty under pressure. A normal assistant will happily cite a policy clause that does not exist, and that one lie can sink a real appeal. ClaimMate is wrapped in a deterministic citation gate that blocks any clause not present in the plan, and it abstains when the plan genuinely excludes a service. Diagnosis codes are checked against a public medical API, and the appeal waits behind a human approval step.

It is built with the Agent Development Kit: an orchestrator that delegates to a Clause-Finder specialist over A2A, tools and retrieval, cross-session memory, an evaluation suite, and a trace view. All data shown is synthetic. ClaimMate prepares a draft for you to review and submit. It does not file anything itself.
