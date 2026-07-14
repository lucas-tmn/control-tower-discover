# Access Request Brief (for Devon)

ACCESS REQUEST BRIEF
Eagle Eye Foundation — Dashboard Discovery

To:        Devon Rumpel — Sr. Director, Supply Chain Systems
From:      Lucas Trinh — Product Owner, Supply Chain Analytics (GCC Vietnam)
Re:        Read-only access to Power BI tenant metadata to unblock Discovery
Date:      ______________
Priority:  Blocker — gates the start of the 90-day Discovery plan

THE ONE-LINE ASK

I need read-only admin access to Power BI tenant metadata and activity logs —
or a one-time export of it from the team that owns the tenant. I'm asking you
to (a) point me to that owner and introduce me, and (b) sponsor the request.

WHY THIS IS THE CRITICAL PATH

The entire Eagle Eye Foundation plan begins with one step: scoping the current
reporting estate (the "~3,000 dashboards"). Every later workstream — business
interviews, KPI dictionary, decision mapping, AI prioritization — depends on
that inventory existing first. Until I can see what reports exist, who owns
them, and how they're used, Discovery cannot start.

Today I'm blocked because I don't know who holds the dashboard inventory or who
owns the Power BI tenant. That owner sits outside Supply Chain — which is
exactly where your sponsorship unblocks things faster than I can alone.

WHAT I ACTUALLY NEED (and what I do NOT need)

I do NOT need to open or view 3,000 dashboards manually, and I do NOT need to
see confidential report *contents*.

I need the METADATA, which Power BI can export programmatically:
   - List of all workspaces, reports, dashboards, and datasets
   - Owner / creator and workspace for each
   - Last refresh date and refresh schedule
   - Usage activity — who viewed what, and when (last 60–90 days)
   - Data source / lineage where available
   - Capacity & refresh load (for the cost-of-maintenance estimate)

This data lives in the Power BI Admin Portal, the Admin REST API, and the
Activity Events / Usage Metrics — all read-only, all metadata.

THE PREFERRED PATH

Grant me (or Cherry, our Data Analyst Lead) read-only Power BI / Fabric Admin
access scoped to metadata and activity logs. This lets us pull the inventory
ourselves, refresh it as Discovery progresses, and keep it current.

FALLBACK OPTIONS (if full tenant access is too sensitive)

I recognize tenant-wide admin is a sensitive grant that may need a security
review. To keep this moving, any of these also works:

   Option B — One-time export: the BI Platform team runs the Admin API and
              hands us a CSV of the inventory + usage metadata. We re-request
              a refresh later if needed.

   Option C — Scoped access: workspace-admin (read) on the Supply Chain–related
              workspaces only, rather than the whole tenant.

   Option D — Delegated pull: a named person on the BI team runs the queries
              with us in a working session and shares the output.

Any of B–D unblocks us. The preferred path is fastest over the full project,
but I'd rather start with a scoped option than wait.

WHAT I NEED FROM YOU

   1. Identify and introduce me to the Power BI / Fabric tenant admin owner
      (likely Central IT / BI Platform / M365 administration).
   2. Sponsor the read-only access request, or endorse one of the fallback
      options above.
   3. If a security / governance review is required, help route it so it
      doesn't stall.

TIMING & IMPACT

Target: access or first export within ____ business days, so Discovery can
start on schedule. Every week this stays blocked pushes the 90-day plan — and
the first Eagle Eye deliverables — back by the same amount.

Once unblocked, the first output (a Dashboard Inventory + Ownership Matrix,
including a no-owner / zero-usage breakdown) follows within roughly two weeks.

CONTACT

Lucas Trinh — Product Owner, Supply Chain Analytics
Working with: Cherry Bui — Data Analyst Lead, Global SC Data Analytics
