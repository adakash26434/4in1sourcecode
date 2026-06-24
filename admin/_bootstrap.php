<?php
/**
 * ════════════════════════════════════════════════════════════
 * ADMIN PANEL BOOTSTRAP — Global Error Guard (v1)
 * ════════════════════════════════════════════════════════════
 * सबै admin/*.php files को सुरुमा यो file include गरिन्छ।
 * के गर्छ?
 *   - includes/config.php load गर्छ (getDB, requireAdminLogin, etc.)
 *   - $pdo global PDO connection उपलब्ध गराउँछ
 *   - PHP fatal error → user-friendly Nepali error page
 *   - Production मा error details hide, log मा मात्र लेख्छ
 *   - Debug mode (?debug=1) मा detailed error देखाउँछ
 * ════════════════════════════════════════════════════════════
 */

define('PORTAL', 'admin');
define('IS_ADMIN_PAGE', true);

require_once __DIR__ . '/../core/init.php';

/* Global $pdo — admin pages ले direct query गर्न मिल्ने गरि */
try {
    $pdo = isset($db) && $db instanceof PDO ? $db : getDB();
} catch (Throwable $e) {
    error_log('[admin-bootstrap-db-fail] ' . $e->getMessage());
    $pdo = null;
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
    if (headers_sent()) {
        echo "\n<!-- Fatal: see server error log -->\n";
        return;
    }
    @http_response_code(500);
    header('Content-Type: text/html; charset=utf-8');

    $isDebug = core_is_debug_request();
    $msg = $isDebug
        ? ($err['message'] . ' @ ' . basename($err['file']) . ':' . $err['line'])
        : 'अप्रत्याशित त्रुटि भयो। कृपया पछि पुनः प्रयास गर्नुहोस्।';
    $home = defined('ADMIN_URL') ? ADMIN_URL : '/admin/';
    error_log('[admin-panel-fatal] ' . $err['message'] . ' @ ' . $err['file'] . ':' . $err['line']);
    core_render_portal_fatal_page([
        'title' => 'त्रुटि — Admin Panel',
        'heading' => 'केहि गलत भयो',
        'message' => 'Admin panel मा अप्रत्याशित त्रुटि भयो। केहि समय पछि पुनः प्रयास गर्नुहोस्।',
        'home' => $home,
        'buttonText' => 'लगिन पृष्ठमा फर्किनुहोस्',
        'showDetail' => $isDebug,
        'detail' => $msg,
    ]);
});

/* Uncaught exception handler */
set_exception_handler(function ($e) {
    core_forward_exception_to_shutdown($e, 'admin-panel-exception');
});
