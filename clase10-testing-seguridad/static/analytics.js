// PostHog product analytics + session replay (Semana 10 slide 8/11).
//
// The project API key is fetched from GET /public-config instead of being
// hardcoded here, so it stays sourced from the server's environment
// (POSTHOG_PROJECT_API_KEY in .env) — see app/main.py. This is the official
// posthog-js snippet, loaded on every page.
//
// `capture_exceptions: true` turns on PostHog's exception autocapture:
// uncaught errors (window.onerror) and unhandled promise rejections are
// captured automatically as "$exception" events, no extra code needed. That
// is what turns "Bug intencional #2" (see dashboard.html / GUIA-DE-PRUEBAS.md)
// into something visible in PostHog's Error tracking tab, correlated with the
// session replay recorded at the same time.
!function (t, e) {
  var o, n, p, r; e.__SV || (window.posthog = e, e._i = [], e.init = function (i, s, a) {
    function g(t, e) { var o = e.split("."); 2 == o.length && (t = t[o[0]], e = o[1]), t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))) } }
    (p = t.createElement("script")).type = "text/javascript", p.crossOrigin = "anonymous", p.async = !0, p.src = s.api_host.replace(".i.posthog.com", "-assets.i.posthog.com") + "/static/array.js", (r = t.getElementsByTagName("script")[0]).parentNode.insertBefore(p, r);
    var u = e; for (void 0 !== a ? u = e[a] = [] : a = "posthog", u.people = u.people || [], u.toString = function (t) { var e = "posthog"; return "posthog" !== a && (e += "." + a), t || (e += " (stub)"), e }, u.people.toString = function () { return u.toString(1) + ".people (stub)" }, o = "init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "), n = 0; n < o.length; n++) g(u, o[n]);
    e._i.push([i, s, a])
  }, e.__SV = 1)
}(document, window.posthog || []);

(async function initAnalytics() {
  try {
    const response = await fetch("/public-config");
    const config = await response.json();
    if (!config.posthog_project_api_key) {
      return; // no key configured locally — no-op, mirrors app/analytics.py's server-side no-op
    }
    window.posthog.init(config.posthog_project_api_key, {
      api_host: config.posthog_host,
      capture_exceptions: true, // autocapture uncaught errors + unhandled promise rejections
      enable_recording_console_log: true,
    });
  } catch (err) {
    // Analytics must never break the app itself.
    console.warn("PostHog init skipped:", err);
  }
})();

// Called after a successful login/registro so events recorded before and
// after authentication link to the same PostHog person, matching the
// distinct_id (the user's numeric id) used server-side in app/analytics.py.
function identifyUsuario(perfil) {
  if (window.posthog && window.posthog.identify) {
    window.posthog.identify(String(perfil.id), { email: perfil.email, rol: perfil.rol });
  }
}
