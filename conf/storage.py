from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ForgivingManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Hashed static files for cache-busting, without hard-failing in production.

    The default ManifestStaticFilesStorage raises a 500 if a template asks for a
    static file that isn't in the manifest. On a small self-hosted site that's a
    page-down risk, so we fall back to the unhashed name for missing entries.
    Files that *are* collected still get content-hashed (and thus cache-busted).
    """

    manifest_strict = False
