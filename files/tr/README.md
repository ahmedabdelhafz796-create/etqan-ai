Put the real Turkish course package here as: `course-tr.zip`

`server-reference/api/download.js` looks for this exact filename after
verifying payment. Nothing here is served publicly — it's only reachable
through the download endpoint after a paid order is confirmed.
