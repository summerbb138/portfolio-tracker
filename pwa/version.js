// SINGLE SOURCE OF TRUTH for the app version.
// Consumed by: sw.js (importScripts → cache name), index.html (version badge),
// pwa/server.py and the ICC shell (parsed with a regex). Works both as a
// <script> in the page (self === window) and via importScripts() in the SW.
//
// To release: bump APP_BUILD every deploy (and APP_VERSION for a real version
// change). Everything else derives from these two values — do not hard-code the
// version anywhere else. See docs/SYSTEM_DOCUMENTATION.md §26.
self.APP_VERSION = "1.5";
self.APP_BUILD = 26;
