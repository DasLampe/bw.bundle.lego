bundle_name = "lego"

cfg = node.metadata.get(bundle_name)
version = cfg.get('version')
arch = cfg.get('arch')
email = cfg.get('email')
path = cfg.get('path')
default_challenge = cfg.get('default_challenge', 'http')

files = {
    f'/tmp/lego_{version}.tar.gz': {
        'source': f"https://github.com/go-acme/lego/releases/download/v{version}/lego_v{version}_{arch}.tar.gz",
        'content_type': 'download',
        'unless': f'test -f /opt/lego/lego && /opt/lego/lego --version | grep "lego version {version} " > /dev/null',
    },
    f'{path}/hooks/renew_hook.sh': {
        'source': 'etc/lego/hooks/hook.sh.j2',
        'content_type': 'jinja2',
        'context': {
            'hooks': cfg.get('renew_hooks'),
        },
        'owner': 'root',
        'group': 'root',
        'mode': '770',
        'tags': [
            f'{bundle_name}_hooks',
        ],
    },
    f'{path}/hooks/run_hook.sh': {
        'source': 'etc/lego/hooks/hook.sh.j2',
        'content_type': 'jinja2',
        'context': {
            'hooks': cfg.get('run_hooks', cfg.get('renew_hooks')),
        },
        'owner': 'root',
        'group': 'root',
        'mode': '770',
        'tags': [
            f'{bundle_name}_hooks',
        ],
    },
    f'{path}/renewals/renewals.sh': {
        'source': 'etc/lego/renewals/renewal.sh.j2',
        'content_type': 'jinja2',
        'context': {
            'lego_path': path,
        },
        'owner': 'root',
        'group': 'root',
        'mode': '770',
        'tags': [
            f'{bundle_name}_renewals',
        ],
    },
    f'/etc/systemd/system/lego-renewal.service': {
        'source': 'etc/systemd/system/lego-renewal.service.j2',
        'content_type': 'jinja2',
        'context': {
            'lego_path': path,
        },
        'owner': 'root',
        'group': 'root',
        'mode': '640',
        'triggers': [
            'action:systemctl-daemon-reload',
        ],
        'tags': [
            f'{bundle_name}_renewals',
        ],
    },
    f'/etc/systemd/system/lego-renewal.timer': {
        'source': 'etc/systemd/system/lego-renewal.timer.j2',
        'content_type': 'jinja2',
        'context': {
            'renewal_time': cfg.get('renewal_time'),
            'randomized_delay': cfg.get('randomized_delay'),
        },
        'owner': 'root',
        'group': 'root',
        'mode': '640',
        'triggers': [
            'action:systemctl-daemon-reload',
            f'svc_systemd:lego-renewal.timer:restart'
        ],
        'tags': [
            f'{bundle_name}_renewals',
        ],
    }
}

svc_systemd = {
        'lego-renewal.timer': {
        'running': True,
        'enabled': True,
        'needs': [
            'action:systemctl-daemon-reload',
        ],
    }
}

directories = {
    '/opt/lego': {},
    path: {},
    f'{path}/hooks': {},
    f'{path}/renewals': {},
}

actions = {
    'unpack_lego': {
        'command': f'echo {cfg.get("checksum")} /tmp/lego_{version}.tar.gz | sha256sum -c && tar xfz /tmp/lego_{version}.tar.gz -C /opt/lego',
        'needs': [
            'directory:/opt/lego',
            f'file:/tmp/lego_{version}.tar.gz',
        ],
        'unless': f'test -f /opt/lego/lego && /opt/lego/lego --version | grep "lego version {version} " > /dev/null',
    },
    'systemctl-daemon-reload': {
        'command': 'systemctl daemon-reload',
        'triggered': True,
        'needs': [
            'tag:systemd_units',
        ],
    },
}


for name, challenge in cfg.get('challenges', {}).items():
    files[f'{path}/challenges/{name}/.env'] = {
        'source': 'etc/lego/challenges/env.template',
        'content_type': 'mako',
        'context': {
            'config': challenge.get('environment'),
        },
        'owner': 'root',
        'group': 'root',
        'mode': '0600',
        'tags': [
            f'{bundle_name}_challenges'
        ]
    }

for domain, config in cfg.get('domains').items():
    challenge = cfg.get('challenges', {}).get(config.get('challenge', default_challenge))

    command = f'. {path}/challenges/{config.get("challenge", default_challenge)}/.env && '\
              f' /opt/lego/lego --accept-tos --email {email} --{challenge.get("type")} {challenge.get("provider")}'\
              f' --path {path}'\
              f' --domains {domain}'

    if config.get('additional_domains', []):
        command = command + f' --domains {" --domains ".join(config.get("additional_domains"))}'

    if challenge.get('additional_params', []):
        command = command + ' ' + ' '.join(challenge.get('additional_params'))

    actions[f'request_cert_for_{domain}'] = {
        'command': f'{command} run --run-hook="{path}/hooks/run_hook.sh"',
        'needs': [
            'action:unpack_lego',
            f'tag:{bundle_name}_challenges',
            f'tag:{bundle_name}_hooks',
        ],
        'unless': f'test -f {path}/certificates/{domain}.json && '
                  f'test "$(openssl x509 -in {path}/certificates/{domain}.crt -noout -ext subjectAltName | grep DNS | sed "s/DNS://g" | sed "s/ //g")" = "{",".join(sorted(config.get("additional_domains") + [domain]))}"',
    }

    files[f'{path}/renewals/renewal_{domain.replace("*", "_").replace(".", "_")}.sh'] = {
        'content': f'''#!/usr/bin/env bash
                   {command} renew --renew-hook="{path}/hooks/renew_hook.sh"
        ''',
        'mode': '750',
        'owner': 'root',
        'needs': [
            f'tag:{bundle_name}_challenges',
            f'tag:{bundle_name}_hooks',
        ],
        'tags': [
            f'{bundle_name}_renewals',
        ]
    }

    # For backward compatibility, remove old cronjobs
    files[f'/etc/cron.daily/renew_cert_{domain.replace(".", "_")}'] = {
        'delete': True,
    }
