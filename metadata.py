defaults = {
    'lego': {
        'version': '4.16.1',
        'checksum': 'e9826f955337c1fd825d21b073168692711985e25db013ff6b00e9a55a9644b4',
        'default_challenge': 'http',
        'path': '/etc/lego',
        'challenges': {
            'http': {
                'type': 'http',
                'provider': '--http.webroot /var/www/letsencrypt',
                'environment': {
                },
                'additional_params': '',
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
