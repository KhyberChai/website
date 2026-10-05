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

## Instagram wall of fame

Six photos/reel covers curated from public collaboration posts visible on @khyber.chai. Each card credits its creator and links to the original Instagram post. The gallery is curated, not automatically synchronized. Edit the wall section in the three HTML pages to add or remove cards; assets/wall-of-fame.json records the sources.

## Random rotation and photo selection

The wall is shuffled on each visit, with a Mix it up button. Reviews are selected at random from verified, approved entries in assets/community-content.json, matched to the location. Vancouver currently has one verified review; more are needed for variety there.

Open /redesign/manage-wall.html to approve or hide photos. Download the content file and replace redesign/assets/community-content.json in GitHub to apply it. This page only saves a file to your device; it cannot directly change live content.

Daily imports are NOT enabled yet. Instagram and Google Business Profile connections still need to be installed, authenticated and verified before a recurring import can be configured. There is no scheduled job in this archive. When connected, new photos should be imported with approved:false and existing approval choices preserved. Reviews retain exact text and source attribution.

## Location social accounts

Vancouver Instagram: @khyber.chai. Surrey Instagram and Facebook: @khyber.chaigrill. The content settings record both Instagram sources for future imports. Automatic imports are still awaiting verified account connections.
