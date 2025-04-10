defaults = {
    'lego': {
        'version': '4.22.2',
        'arch': 'linux_amd64',
        'checksum': '04b20aeeb5f495ddf806219797adb8e99418a9bbb4440c67b426680f82b7bd1b',
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
