# Companion 0.6.5 preview label encoding

Correct corrupted punctuation in the preview dimensions, title and zoom-out button. Use plain x, vertical bar and hyphen characters to avoid encoding-sensitive separators. Read/write modified text explicitly as UTF-8.

Verified the native label equals `1655 x 1117 px  |  86%` at 86% zoom, and the title contains a plain separator. Scanned all companion Python sources for the observed mojibake sequences.
