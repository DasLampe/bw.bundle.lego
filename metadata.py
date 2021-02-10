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