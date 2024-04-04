# lego via Bundlewrap

Install and configure Let's Encrypt client written in go [lego](https://go-acme.github.io/lego/) via Bundlewrap.

## Dependencies
- [Download Item](https://github.com/sHorst/bw.item.download)

## Supports
- Linux (AMD64)
- [nginx Bundle](https://github.com/DasLampe/bw.bundle.nginx)

## Config
At minimum lego requires an Email-Address, so please enter at least the `email` field.

```python
node["foobar"] = {
    'metadata': {
        'lego': {
            'version': '4.2.0',
            'checksum': '3b0f6c715b79a6dc692e5c3f5890905bc4404a33469cecc2d0b60c5bf5c2076f',
            'email': 'info@example.org',
            'path': '/etc/lego',
            'default_challenge': 'dns-cloudflare',
            'domains': {
                'example.org': {
                    'challenge': 'dns-cloudflare',
                    'additional_domains': [
                        'www.example.org', 'foobar.example.org',
                    ],
                },
                'yetAnotherDomain.example.org': {},
            },
            'renew_hook': "systemctl restart nginx",
            'challenges': {
                'dns-cloudflare': {
                    'type': 'dns',
                    'provider': 'cloudflare',
                    'environment': {
                        'CLOUDFLARE_DNS_API_TOKEN': '1234567890abcdefghijklmnopqrstuvwxyz',
                    },
                    'additional_params': [
                        '--dns.resolvers 1.1.1.1',
                    ],
                },
            },
        },
    }
}
```
