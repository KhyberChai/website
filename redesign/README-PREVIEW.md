# Khyber redesign preview

Upload the entire redesign/ folder into your existing website publishing folder.

Do not upload the contents of redesign/ directly to the root. Your existing homepage, chai/grill pages, assets, PDFs and hosting configuration stay in place.

If the repo publishes its root, add redesign/ there. If it publishes docs/ or dist/, put redesign/ inside that publishing folder.

After the normal deployment, preview at:
https://www.khyberchai.com/redesign/
https://www.khyberchai.com/redesign/chai/
https://www.khyberchai.com/redesign/grill/

Internal page and asset paths use /redesign/. Existing external menus, ordering, reservations and catering services are retained, so these actions still connect to your real services.

The preview pages request exclusion from search engines; they are not password protected. No build step, workflow change, DNS change or homepage replacement is needed.

When ready to replace the current site, prepare a root-path edition. Do not simply move these files to the root, because this edition intentionally uses /redesign/ paths.
