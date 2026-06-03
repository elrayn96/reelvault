# ==========================================
# PHASE 1: Build Frontend (Vite + TypeScript)
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app

# Install dependencies and copy files
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ==========================================
# PHASE 2: Production Container Running
# ==========================================
FROM python:3.11-slim
WORKDIR /app

# Install Node.js runtime inside the final container to run Gateway Proxy
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install python-pip dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and install Node production dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Copy compiled frontend build and files
COPY --from=frontend-builder /app/dist ./dist
COPY --from=frontend-builder /app/server.ts ./server.ts
COPY --from=frontend-builder /app/tsconfig.json ./tsconfig.json
COPY . .

# Environment setups
ENV NODE_ENV=production
ENV PORT=3000

# Install tsx globally or locally to run TypeScript Gateway dynamically
RUN npm install -g tsx

# Expose Gate proxy port
EXPOSE 3000

# Launch server dynamically (starts FastAPI microservice on 8000 and serves express on 3000)
CMD ["tsx", "server.ts"]
