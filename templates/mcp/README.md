# Inactive MCP descriptors

Every per-technology `.example.json` is an inventory descriptor, not a drop-in MCP server declaration. No server is started, endpoint guessed or credential supplied. `mcp_servers:{}` and `enabled:false` are deliberate.

For a vendor-documented server, first obtain its exact deployed endpoint and authentication configuration from the vendor UI/docs, then configure it independently in the intended Hermes profile with least-privilege RBAC and `trust: untrusted`. Never embed a token in an example, Git URL, subprocess argument or committed file.

Hermes's native MCP trust model asks before tools not annotated read-only; it does not prove that an annotated tool or query is harmless. Pair trust with server-side permissions and tool allowlisting ([Hermes plugin/MCP documentation](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)).

Vendor-confirmed references for this release are [Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server) and [Splunk](https://help.splunk.com/en/splunk-enterprise/mcp-server-for-splunk-platform/2.0/connecting-to-the-mcp-server-and-settings). Remaining entries say `not_verified`, which means no official server claim is made.
