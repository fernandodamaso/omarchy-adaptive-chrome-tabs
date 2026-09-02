# Chrome orientation adapter research — FDM-821

This lane determines whether Chrome/Chromium's native tab-strip orientation can be read and set live through a production-safe Linux mechanism.

The required outcome is one explicit **GO — production adapter** or **NO-GO** decision. Research must pin browser/package versions, test exact state read/set/verification, determine preference scope and sync/policy behavior, and reject unsafe fallbacks.

Remote work may inspect upstream source, prepare safe probes, pure tests, and a deterministic local runbook. Only the target Omarchy machine may claim live browser/accessibility behavior or a GO verdict.

Do not commit raw browser/profile data. Sanitized evidence belongs in reviewed fixtures or reports only.
