# Azure Container Apps deployment

ProjectLens is container-ready for Azure Container Apps. Use separate frontend and backend apps, Azure Database for PostgreSQL Flexible Server with the `vector` extension, Azure Container Registry, and Key Vault references for secrets.

Required backend variables are `DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET`, and `CORS_ORIGINS`. Configure ingress on ports 80 and 8000, set the backend health probe to `/api/v1/health`, allow only the deployed frontend origin, and run migrations as a deployment job before shifting traffic. Use managed identity for registry and Key Vault access. Keep PostgreSQL on a private endpoint for production.

The included GitHub workflow validates both applications and images. A production release should add OIDC federation, environment approval, image signing, database backup verification, and a staged revision with smoke tests before promotion.

