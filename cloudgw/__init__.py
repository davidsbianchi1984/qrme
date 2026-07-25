"""Cloud Model Gateway — the server side of docs/cloud-model.md.

The three products have always been able to *talk* to a gateway: route
inference to a greater hosted model, fall back locally when it is
unreachable, and contribute rated exchanges to improve it. What did not exist
was anything to talk to — the contract was documented and the clients were
tested against fakes.

This is the gateway an operator actually deploys. It is deliberately small:
it authenticates callers, serves inference from one configured model, and
takes contributions into a PDI vault. Everything interesting about consent,
anonymization, and fallback already lives on the client side, where it
belongs — the deployment that holds the data is the one that must decide what
leaves it.

What this adds on the server side is the part a client cannot provide: a
**last line of defence on the intake**. A gateway that trusts its callers to
have stripped identity is one client bug away from a training corpus full of
names, so contributions are screened here too and refused, not sanitized.
"""
