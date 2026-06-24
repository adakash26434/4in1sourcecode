<?php
/**
 * ════════════════════════════════════════════════════════════
 * MEMBER PANEL BOOTSTRAP — Global Error Guard (v2)
 * ════════════════════════════════════════════════════════════
 * सबै member/*.php files को सुरुमा यो file include गरिन्छ।
 * के गर्छ?
 *   - PHP fatal error → user-friendly Nepali error page (white-screen रोक्छ)
 *   - Unhandled exceptions लाई gracefully handle गर्छ
 *   - Production मा error details hide, log मा मात्र लेख्छ
 *   - Development mode मा detailed error देखाउँछ (?debug=1)
 * ════════════════════════════════════════════════════════════
 */

define('PORTAL', 'member');

require_once __DIR__ . '/../core/init.php';
if (function_exists('site_license_public_guard')) {
    site_license_public_guard();
}

/* Follow shared environment policy while keeping production safe by default. */
if (function_exists('core_apply_runtime_error_policy')) {
    core_apply_runtime_error_policy();
}

/* Friendly fatal handler — white screen कहिल्यै नदेखियोस् */
register_shutdown_function(function () {
    $err = error_get_last();
    if (!$err || !core_is_fatal_error_type((int)$err['type'])) {
        return;
    }
    /* Output पहिले नै केहि गइसकेको छ भने rewrite गर्न सकिन्न */
    if (headers_sent()) {
        echo "\n<!-- Fatal: see server error log -->\n";
        return;
    }
    @http_response_code(500);
    header('Content-Type: text/html; charset=utf-8');

    $isDebug = core_is_debug_request();
    $msg = $isDebug
        ? htmlspecialchars($err['message'] . ' @ ' . basename($err['file']) . ':' . $err['line'])
        : 'अप्रत्याशित त्रुटि भयो। कार्यालयमा सम्पर्क गर्नुहोस्।';
    $home = defined('SITE_URL') ? SITE_URL : '/';
    error_log('[member-panel-fatal] ' . $err['message'] . ' @ ' . $err['file'] . ':' . $err['line']);
    core_render_portal_fatal_page([
        'title' => 'त्रुटि — Member Portal',
        'heading' => 'केहि गलत भयो',
        'message' => 'हाम्रो team लाई स्वतः सूचित गरियो। केहि समय पछि पुनः प्रयास गर्नुहोस्।',
        'home' => $home . 'member/login.php',
        'buttonText' => 'लगिन पृष्ठमा फर्किनुहोस्',
        'showDetail' => $isDebug,
        'detail' => $msg,
    ]);
});

/* Uncaught exception handler */
set_exception_handler(function ($e) {
    core_forward_exception_to_shutdown($e, 'member-panel-exception');
});
