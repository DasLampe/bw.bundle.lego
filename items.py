bundle_name = "lego"

cfg = node.metadata.get(bundle_name)
version = cfg.get('version')
email = cfg.get('email')
path = cfg.get('path')
default_challenge = cfg.get('default_challenge', 'http')

files = {
    f'/tmp/lego_{version}.tar.gz': {
        'source': f"https://github.com/go-acme/lego/releases/download/v{version}/lego_v{version}_linux_amd64.tar.gz",
        'content_type': 'download',
        'unless': f'test -f /opt/lego/lego && /opt/lego/lego --version | grep "lego version {version} " > /dev/null',
    },
    f'{path}/hooks/renew_hook.sh': {
        'source': 'etc/lego/hooks/renew_hook.sh.j2',
        'content_type': 'jinja2',
        'context': {
            'renew_hooks': cfg.get('renew_hooks'),
        },
        'owner': 'root',
        'group': 'root',
        'mode': '770',
        'tags': [
            f'{bundle_name}_hooks',
        ],
    },
}

directories = {
    '/opt/lego': {
    },
    path: {}
}

actions = {
    'unpack_lego': {
        'command': f'echo {cfg.get("checksum")} /tmp/lego_{version}.tar.gz | sha256sum -c && tar xfz /tmp/lego_{version}.tar.gz -C /opt/lego',
        'needs': [
            'directory:/opt/lego',
            f'file:/tmp/lego_{version}.tar.gz',
        ],
        'unless': f'test -f /opt/lego/lego && /opt/lego/lego --version | grep "lego version {version} " > /dev/null',
    }
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

    command = f". {path}/challenges/{config.get('challenge', default_challenge)}/.env && "\
              f" /opt/lego/lego --accept-tos --email {email} --{challenge.get('type')} {challenge.get('provider')}"\
              f" --path {path}"\
              f' --domains {domain}'

    if config.get('additional_domains', []):
        command = command + f" --domains {' --domains '.join(config.get('additional_domains'))}"

    if challenge.get('additional_params', []):
        command = command + ' ' + ' '.join(challenge.get('additional_params'))

    actions[f'request_cert_for_{domain}'] = {
        'command': f"{command} run",
        'needs': [
            'action:unpack_lego',
            f'tag:{bundle_name}_challenges',
            f'tag:{bundle_name}_hooks',
        ],
        'unless': f'test -d {path}/accounts/acme-v02.api.letsencrypt.org/{email} && '
                  f' test -f {path}/certificates/{domain}.json'
    }

    files[f'/etc/cron.daily/renew_cert_{domain.replace(".", "_")}'] = {
        'content': f"""#!/usr/bin/env bash
                   {command} renew --renew-hook="{path}/hooks/renew_hook.sh"
        """,
        'mode': '750',
        'owner': 'root',
        'needs': [
            f'tag:{bundle_name}_challenges',
            f'tag:{bundle_name}_hooks',
        ]
    }
