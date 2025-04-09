# Load password from secrets
BGA_USER_PASSWORD=$(cat /run/secrets/bga_pipeline_password)
BGA_PIPELINE_PASSWORD=$(cat /run/secrets/bga_user_password)

# Update user passwords
psql -U postgres -c "ALTER USER bga_user WITH PASSWORD '${BGA_USER_PASSWORD}';"
psql -U postgres -c "ALTER USER bga_pipeline WITH PASSWORD '${BGA_PIPELINE_PASSWORD}';"