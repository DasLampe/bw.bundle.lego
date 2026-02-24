defaults = {
    'lego': {
        'version': '4.32.0',
        'arch': 'linux_amd64',
        'checksum': '304c9622cb413e894e0b5c683bda37e23736977c229314384640d8c986e3f330',
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
        #'run_hooks': [],
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
