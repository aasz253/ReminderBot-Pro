# SSL Certificate Setup for ReminderBot Pro

This directory contains SSL certificates for the Nginx reverse proxy.

## Production (Let's Encrypt / Certbot)

### Initial Setup
```bash
# Install certbot on the host
sudo apt-get install certbot

# Obtain certificate (standalone mode - stop nginx first)
sudo certbot certonly --standalone -d reminderbot.example.com -d api.reminderbot.example.com

# Or use webroot mode (nginx running)
sudo certbot certonly --webroot -w /var/www/certbot -d reminderbot.example.com -d api.reminderbot.example.com
```

### Auto-Renewal
Certificates are valid for 90 days. Set up a cron job:
```bash
# Edit crontab
crontab -e

# Add line (runs daily at 3 AM)
0 3 * * * docker exec reminderbot-nginx certbot renew --quiet --post-hook "nginx -s reload"
```

### Using Docker Compose
```bash
# Initial certificate generation
docker compose -f docker-compose.yml run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d reminderbot.example.com

# Renewal (run periodically)
docker compose -f docker-compose.yml run --rm certbot renew
```

### Manual Certificates
For development, you can generate self-signed certificates:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout self-signed/privkey.pem \
  -out self-signed/fullchain.pem \
  -subj "/CN=reminderbot.example.com"
```

## File Structure
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key (keep secure!)
- `chain.pem` - Intermediate certificates

## Security
- Private keys must have restricted permissions (chmod 600)
- Never commit certificates to version control
- Use different certificates for staging/production
