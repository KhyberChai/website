# Khyber redesign: replace the main website

This is the latest redesign with the desktop wall fix, Instagram handles for both locations, random photo/review rotation and no Facebook footer links. The files are configured for the main domain, not /redesign/.

BACK UP FIRST
1. Select your currently deployed branch in GitHub (usually main).
2. Create a branch named backup-before-redesign from that branch. Leave this branch unchanged.
3. On the current branch, use Code > Download ZIP and keep that archive.

REPLACE THE WEBSITE
1. Extract this ZIP.
2. Return to the branch your existing hosting deploys.
3. In the publishing folder containing your current homepage, choose Add file > Upload files and upload the extracted contents, preserving the folder structure. Commit the changes.
4. Keep your existing CNAME, menu PDFs, order redirect, thank-you page, hosting workflow and other files not included in this archive. Do not delete the whole repository. Leave the separate redesign/ preview folder in place if desired.
5. Let your existing hosting deployment finish, then verify the homepage, both locations, menu PDFs, ordering, reservations and catering.

No build or dependencies are needed. If publishing from docs/ or dist/, upload into that folder instead of the repository root.

The source snapshot covers files. Keep any existing external service settings and data separately; bookings, email configuration, domain/DNS settings and other external services are not migrated by uploading website files.

Random rotation works using the verified content already bundled. Automatic daily Instagram/Google imports are still awaiting account connections. Photo approvals can be prepared at /manage-wall.html, then the downloaded community-content.json must be uploaded into assets/ to apply changes.
