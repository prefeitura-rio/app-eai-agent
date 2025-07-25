# Base image
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Define build-time environment variables
ARG NEXT_PUBLIC_IDENTIDADE_CARIOCA_BASE_URL
ARG NEXT_PUBLIC_IDENTIDADE_CARIOCA_CLIENT_ID
ARG NEXT_PUBLIC_IDENTIDADE_CARIOCA_REDIRECT_URI
ARG NEXT_PUBLIC_API_BUSCA_ROOT_URL
ARG NEXT_PUBLIC_BASE_API_URL
ARG NEXT_PUBLIC_GOVBR_BASE_URL
ARG GOOGLE_MAPS_API_KEY
ARG NEXT_PUBLIC_HOTJAR_ID
ARG NEXT_PUBLIC_GOOGLE_ANALYTICS_ID
ARG NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID
ARG API_KEY_SUBPAV_OSA_SMS

# Set environment variables for the build process
ENV NEXT_PUBLIC_IDENTIDADE_CARIOCA_BASE_URL=$NEXT_PUBLIC_IDENTIDADE_CARIOCA_BASE_URL
ENV NEXT_PUBLIC_IDENTIDADE_CARIOCA_CLIENT_ID=$NEXT_PUBLIC_IDENTIDADE_CARIOCA_CLIENT_ID
ENV NEXT_PUBLIC_IDENTIDADE_CARIOCA_REDIRECT_URI=$NEXT_PUBLIC_IDENTIDADE_CARIOCA_REDIRECT_URI
ENV NEXT_PUBLIC_API_BUSCA_ROOT_URL=$NEXT_PUBLIC_API_BUSCA_ROOT_URL
ENV NEXT_PUBLIC_BASE_API_URL=$NEXT_PUBLIC_BASE_API_URL
ENV NEXT_PUBLIC_GOVBR_BASE_URL=$NEXT_PUBLIC_GOVBR_BASE_URL
ENV GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY
ENV NEXT_PUBLIC_HOTJAR_ID=$NEXT_PUBLIC_HOTJAR_ID
ENV NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=$NEXT_PUBLIC_GOOGLE_ANALYTICS_ID
ENV NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID=$NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID
ENV API_KEY_SUBPAV_OSA_SMS=$API_KEY_SUBPAV_OSA_SMS

# Build the Next.js application
RUN \
  if [ -f yarn.lock ]; then yarn run build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy the built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000

# Start the application
CMD HOSTNAME="0.0.0.0" node server.js