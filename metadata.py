defaults = {
    'lego': {
        'version': '4.10.0',
        'checksum': 'cc1867d0e4e1ca4c6f545f8311e7a4b7150ce02d22c704a64d1f5c545c2ef7f0',
        'default_challenge': 'http',
        'path': '/etc/lego',
        'challenges': {
            'http': {
                'type': 'http',
                'provider': '--http.webroot /var/www/letsencrypt',
                'environment': {
                }
            }
        },
        'renew_hook': '',
    },
}

@metadata_reactor
def add_nginx_domains(metadata):
    if not node.has_bundle('nginx'):
        raise DoNotRunAgain

    domains = {}
    for domain, config in metadata.get('nginx/sites', {}).items():
        if not config.get('ssl', {}).get('letsencrypt', False):
            continue

        domains[domain] = {
            'additional_domains': config.get('additional_server_names', []),
        }

    return {
        'lego': {
            'domains': domains
        }
    }
