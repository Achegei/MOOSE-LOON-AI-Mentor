# n8n Workflow Automation

n8n is a workflow automation tool that connects apps, APIs, databases, and AI services through nodes. A workflow usually starts with a trigger, transforms data, calls services, and ends with a useful action.

Important n8n skills include reading node input/output data, mapping fields, using expressions, handling errors, and testing each workflow step. Beginners should build small reliable workflows before adding complex branching.

AI workflows in n8n often combine a trigger, data cleanup, prompt construction, an AI model call, and a storage or notification step. Good workflows log important outputs and avoid sending unnecessary private data to external services.

Starter project: create a workflow that receives a webhook, summarizes the submitted text with AI, and emails the summary to the learner.
