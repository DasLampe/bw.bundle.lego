defaults = {
    'lego': {
        'version': '4.17.4',
        'checksum': 'f362d59ff5b6f92c599e3151dcf7b6ed853de05533be179b306ca40a7b67fb47',
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
        'renew_hooks': [],
        'renewal_time': 'Mon..Fri *-*-* 03:30:00 UTC', # See https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html
        'randomized_delay': '1h',
    },
}

@metadata_reactor
def backward_compatibility(metadata):
    return {
        'lego': {
            'renew_hooks': [metadata.get('lego/renew_hook', '')],
        }
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
