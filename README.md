# Mancunianity public website

Static public website for https://mancunianity.uk/.

## Deployment
For branch-based GitHub Pages from `main` / repository root, upload the **contents** of this `public-site` folder to the repository root. Do not upload the enclosing folder and do not upload `project-backup`.

The root must contain `index.html`, `.nojekyll`, `CNAME`, `robots.txt`, `sitemap.xml`, page folders and `assets`.

## Privacy
Never commit project contacts, applications, permissions, DBS data, safeguarding information, financial files or unapproved participant material.

## Updating content
Keep `/map/` permanent. Update page text directly in HTML. Update `sitemap.xml` only when a page is added, removed or materially changed.

## Walk availability
Update `availability.json` with the verified remaining places for all six sessions and set `updatedAt` to the current UTC time whenever counts change. Set unknown counts to `null`; do not estimate. The site only displays scarcity badges for 15 or fewer remaining places, and hides count-based badges when the file is missing, invalid or more than 24 hours old. Confirm final availability against TryBooking.

## Campaign and booking attribution
Use lowercase UTM values on campaign links to `/walks.html`, for example `?utm_source=visitmanchester&utm_medium=referral&utm_campaign=christmas_2026`. The campaign-attribution script carries those labels through internal links and sends a TryBooking `track` tag when a visitor follows a booking link. The six performance buttons include the selected session in that tag. Review completed-booking attribution in TryBooking's tracking-tag report; Cloudflare Web Analytics remains page-view and aggregate-traffic analytics and does not report checkout steps or purchases.
