defaults = {
    'lego': {
        'version': '4.2.0',
        'checksum': '3b0f6c715b79a6dc692e5c3f5890905bc4404a33469cecc2d0b60c5bf5c2076f',
        'default_challenge': 'http',
        'path': '/etc/lego',
        'challenges': {
            'http': {
                'provider': '--http.webroot /var/www/letsencrypt',
                'environment': {
                }
            }
        }
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
            'additional_domains': config.get('additional_server_names'),
        }

    return {
        'lego': {
            'domains': domains
        }
    }
