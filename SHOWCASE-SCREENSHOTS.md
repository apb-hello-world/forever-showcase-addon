# Screenshots of Forever Showcase itself

## In-game addon scenes (0.6.3)

Run `/showcase self` to reveal **Forever Showcase** and open the selector. This
does not start or switch a scene. Self-scenes are hidden from ordinary users
until this command is used, and plain `/showcase` hides the entry again. Reload also resets visibility. Then select
and start one of these scenes:

| Scene | What is photographed | Suggested caption |
| --- | --- | --- |
| Scene library | The real Stagekeeper selector, showing installed integrations and the self-scenes | Stage real addon interfaces from one place. |
| Scene picker | The real compact picker | Move between feature scenes without reopening the main window. |
| Scene controls | A read-only copy built by the real toolbar renderer | Navigate, frame and capture without extra commands. |
| Repeatable framing | The real picker inside a persistent demonstration framing guide | Reuse consistent framing across scenes. |
| Charcoal backdrop | The scene library with charcoal automatically selected | Keep the focus on your addon UI. |
| Ivory backdrop | The same library with ivory automatically selected | Choose a background that complements your artwork. |
| Capture records | The real capture-list renderer with five temporary sample records | Review captures before sending them to the optional desktop companion. |

The framing scene includes its guide in the screenshot intentionally; Auto-fit
encloses the whole illustration. Charcoal and Ivory scenes select their backdrop
on entry and restore the previous mode on exit. The staged toolbar is a separate
copy of the same renderer, so operating controls can hide without losing it.

The staged window is read-only. The separate operating toolbar still provides
Next, Previous, Stop, backdrops, Auto-fit and Capture. The photographed window
stays visible when Capture hides the operating controls. Use Auto-fit and the
padding controls, close the guide, choose a backdrop, then Capture. These captures
are real records under Forever Showcase and can be imported/exported normally.
After finishing, **Stop scene**, then open **Captures > Send & reload** to send
the real batch. The staged sample list is never saved or sent.

The library uses the actual installed integration list; it does not invent
support for absent addons. Sample capture-list rows are illustrative staging
content, not assertions that those screenshots already exist. Stopping, switching
or entering combat clears samples and hides the staged subject. Native layout
and shielding still require the owner's in-game verification.

## Desktop companion shot list

Use the normal installed companion and your real captured images. No fixture
import or separate desktop demo mode is needed. Capture the application window
with your normal desktop screenshot tool; the companion does not capture itself.

1. **Overview:** select a polished real image, choose Styled, apply Stagekeeper
   or your preferred preset, and leave the Project dropdown on its addon. Show
   the three-column workflow and a readable, well-framed preview.
   Caption: “Turn full-screen captures into gallery-ready images.”
2. **Batch editing:** Ctrl-click several captures from one project. Keep the
   active image visually clear and show the selection count with the Finish
   controls. Styling applies to the selection, so use a style you want to keep.
   Caption: “Apply a consistent finish to a whole set of captures.”
3. **Export options:** open Export, select PNG and 850 px wide, keep Maintain
   aspect ratio checked, and enter thumbnails in Subfolder. Opening/changing
   export options does not write images until Export is clicked. Use a neutral
   destination such as D:/Photos/ForeverShowcase if you want a public path.
   Caption: “Export multiple sizes and formats, organized by addon.”
4. **Full-size preview:** open the separate viewer and Fit window. Frame it so
   the picture and zoom controls are visible without desktop clutter.
   Caption: “Inspect the final image before publishing.”
5. **Optional paired exports:** export full-size into large, then 850 px wide
   into thumbnails from the same Export window. Use these real outputs in your
   description to demonstrate consistent proportions and styling.

Avoid the settings page in promotional shots unless you deliberately want to
show local account and folder paths. Preview/export dialogs can simply be closed
after taking a desktop screenshot. The existing clipboard Copy Image action
copies the rendered capture, not the companion UI.

## Validation checklist

- Each self-scene starts from the selector and remains visible during Capture.
- Auto-fit surrounds the subject, not the operating toolbar; backdrop leaves
  all subject content visible. The read-only shield prevents subject actions.
- Next/Previous, Stop, failed entry, combat and reload leave ordinary controls
  usable. Sample rows never appear in SavedVariables or the desktop library.
- Stop, open the real capture list, and Send & reload. Confirm the resulting
  images match the guide and belong to the Forever Showcase desktop project.
