bundle_name = "lego"

cfg = node.metadata.get(bundle_name, {})
version = cfg.get('version')
email = cfg.get('email')
path = cfg.get('path')
default_challenge = cfg.get('default_challenge', 'http')

downloads = {
    f'/tmp/lego_{version}.tar.gz': {
        'url': f"https://github.com/go-acme/lego/releases/download/v{version}/lego_v{version}_linux_amd64.tar.gz",
        'sha256': cfg.get('checksum'),
        'unless': f'test -f /opt/lego/lego && /opt/lego/lego --version | grep "lego version {version} " > /dev/null',
    }
}

directories = {
    '/opt/lego': {
    },
    path: {}
}

actions = {
    'unpack_lego': {
        'command': f'tar xfz /tmp/lego_{version}.tar.gz -C /opt/lego',
        'needs': [
            'directory:/opt/lego',
            f'download:/tmp/lego_{version}.tar.gz',
        ],
        'unless': f'test -f /opt/lego/lego && /opt/lego/lego --version | grep "lego version {version} " > /dev/null',
    }
}

files = {
    f'{path}/hooks/renew_hook.sh': {
        'content': f"""#!/usr/bin/env bash"
            {cfg.get('renew_hook', '')}
        """,
        "owner": 'root',
        "group": 'root',
        "mode": '660',
        "tags": [
            f'{bundle_name}_hooks',
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

    command = f". {path}/challenges/{config.get('challenge', default_challenge)}/.env && "\
              f" /opt/lego/lego --accept-tos --email {email} --{challenge.get('type')} {challenge.get('provider')}"\
              f" --path {path}"\
              f' --domains {domain}'

    if config.get('additional_domains', []):
        command = command + f" --domains {' --domains '.join(config.get('additional_domains'))}"

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
        'content': f"""#!/usr/bin/env bash"
                   {command} renew --renew-hook="{path}/hooks/renew_hook.sh"
        """,
        'mode': '750',
        'owner': 'root',
        'needs': [
            f'tag:{bundle_name}_challenges',
            f'tag:{bundle_name}_hooks',
        ]
    }
