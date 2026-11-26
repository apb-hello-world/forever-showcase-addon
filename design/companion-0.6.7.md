# Companion 0.6.7 / addon 0.5.2 save organization

Reuse the existing output setting as Default save location and explain automatic addon folders in Settings. Shared folder-name handling supports display names, older addon IDs, Unicode, Windows filename restrictions and containment checks. Single Save and batch Save group by addon; explicit single Save As remains exact. Add optional addonTitle to future capture records without changing schema/API version. Older records remain usable.

Evidence: 41 tests passed, including mixed-addon batches, display-name fallback, safe folder names and preservation of originals. Native smoke verified two single saves create unique files in the addon folder, Save As honors an explicit path, and Settings persists the base path. Addon 0.5.2 installed with backup and hash verification. User should reload WoW for display names on newly captured records.
