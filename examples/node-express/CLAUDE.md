# Project Instructions for Claude Code

> This file is automatically loaded into context when Claude Code starts.

## Project Overview

This is a Node.js backend API built with Express and TypeScript. It provides [BRIEF_DESCRIPTION] for [TARGET_USERS].

**Tech Stack:**
- Node.js 20+
- Express.js for API framework
- TypeScript for type safety
- Prisma for ORM
- PostgreSQL for database
- Zod for validation
- Jest for testing

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Express App                          │
├─────────────────────────────────────────────────────────┤
│  Routes           │  Middleware       │  Validators      │
│  └── v1/          │  └── auth         │  └── zod         │
│      └── users    │  └── error        │      schemas     │
├─────────────────────────────────────────────────────────┤
│  Controllers (Request/Response handling)                 │
├─────────────────────────────────────────────────────────┤
│  Services (Business Logic)                               │
├─────────────────────────────────────────────────────────┤
│  Prisma Client (Data Access)                             │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
├── src/
│   ├── routes/
│   │   └── v1/                  # API v1 routes
│   ├── controllers/             # Request handlers
│   ├── services/                # Business logic
│   ├── middleware/              # Express middleware
│   ├── validators/              # Zod schemas
│   ├── types/                   # TypeScript types
│   ├── utils/                   # Utility functions
│   ├── config/                  # Configuration
│   └── app.ts                   # Express app setup
├── prisma/
│   ├── schema.prisma            # Database schema
│   └── migrations/              # Database migrations
├── tests/                       # Test files
└── CLAUDE.md                   # This file
```

## Development Commands

### Setup & Run
```bash
# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Run development server
npm run dev

# Run production build
npm run build && npm start
```

### Database
```bash
# Create migration
npx prisma migrate dev --name description

# Apply migrations (production)
npx prisma migrate deploy

# Reset database
npx prisma migrate reset

# Open Prisma Studio
npx prisma studio

# Seed database
npx prisma db seed
```

### Testing
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- users.test.ts
```

### Linting & Formatting
```bash
# Lint
npm run lint

# Fix lint issues
npm run lint:fix

# Format code
npm run format

# Type check
npm run typecheck
```

## Code Style & Conventions

### Route Structure
```typescript
// routes/v1/users.ts
import { Router } from 'express';
import { UserController } from '@/controllers/user.controller';
import { validate } from '@/middleware/validate';
import { createUserSchema, updateUserSchema } from '@/validators/user.schema';
import { authenticate } from '@/middleware/auth';

const router = Router();
const controller = new UserController();

router.post('/', validate(createUserSchema), controller.create);
router.get('/:id', authenticate, controller.getById);
router.patch('/:id', authenticate, validate(updateUserSchema), controller.update);
router.delete('/:id', authenticate, controller.delete);

export default router;
```

### Controller Structure
```typescript
// controllers/user.controller.ts
import { Request, Response, NextFunction } from 'express';
import { UserService } from '@/services/user.service';
import { CreateUserDto, UpdateUserDto } from '@/validators/user.schema';

export class UserController {
  private userService = new UserService();

  create = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = req.body as CreateUserDto;
      const user = await this.userService.create(data);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  };

  getById = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { id } = req.params;
      const user = await this.userService.findById(id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json(user);
    } catch (error) {
      next(error);
    }
  };
}
```

### Service Layer
```typescript
// services/user.service.ts
import { prisma } from '@/config/database';
import { CreateUserDto, UpdateUserDto } from '@/validators/user.schema';
import { hashPassword } from '@/utils/crypto';

export class UserService {
  async create(data: CreateUserDto) {
    const hashedPassword = await hashPassword(data.password);
    return prisma.user.create({
      data: {
        ...data,
        password: hashedPassword,
      },
      select: {
        id: true,
        email: true,
        name: true,
        createdAt: true,
      },
    });
  }

  async findById(id: string) {
    return prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        name: true,
        createdAt: true,
      },
    });
  }
}
```

### Zod Validators
```typescript
// validators/user.schema.ts
import { z } from 'zod';

export const createUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    name: z.string().min(2).max(100),
    password: z.string().min(8),
  }),
});

export const updateUserSchema = z.object({
  params: z.object({
    id: z.string().uuid(),
  }),
  body: z.object({
    email: z.string().email().optional(),
    name: z.string().min(2).max(100).optional(),
  }),
});

export type CreateUserDto = z.infer<typeof createUserSchema>['body'];
export type UpdateUserDto = z.infer<typeof updateUserSchema>['body'];
```

### Prisma Schema
```prisma
// prisma/schema.prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  password  String
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  posts     Post[]
}
```

### Naming Conventions
- **Files**: `kebab-case.ts` for general, `name.type.ts` for typed files
- **Classes**: `PascalCase`
- **Functions/Variables**: `camelCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Types/Interfaces**: `PascalCase`

## Testing Requirements

- All endpoints must have tests
- Aim for 80% coverage on new code
- Use test database for integration tests

### Test Structure
```typescript
// tests/users.test.ts
import request from 'supertest';
import { app } from '@/app';
import { prisma } from '@/config/database';

describe('Users API', () => {
  beforeEach(async () => {
    await prisma.user.deleteMany();
  });

  describe('POST /api/v1/users', () => {
    it('should create a user', async () => {
      const response = await request(app)
        .post('/api/v1/users')
        .send({
          email: 'test@example.com',
          name: 'Test User',
          password: 'password123',
        });

      expect(response.status).toBe(201);
      expect(response.body.email).toBe('test@example.com');
      expect(response.body).not.toHaveProperty('password');
    });

    it('should reject invalid email', async () => {
      const response = await request(app)
        .post('/api/v1/users')
        .send({
          email: 'invalid',
          name: 'Test User',
          password: 'password123',
        });

      expect(response.status).toBe(400);
    });
  });
});
```

## Git Workflow

### Commit Messages
```
feat(users): add email verification
fix(auth): handle token refresh race condition
refactor(middleware): extract validation logic
```

### Branch Naming
- `feature/user-registration`
- `fix/token-expiration`
- `refactor/error-handling`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |
| `NODE_ENV` | development/production | Yes |
| `PORT` | Server port (default: 3000) | No |
| `CORS_ORIGIN` | Allowed CORS origin | No |

## Known Issues & Gotchas

- **Prisma client**: Must run `prisma generate` after schema changes
- **ESM imports**: Use `@/` path alias, configured in tsconfig
- **Error handling**: Always use `next(error)` in async controllers
- **Validation**: Zod validates req.body, req.params, req.query separately

## Rules for Claude

1. **Think first, code second**: Understand the request flow before modifying
2. **Follow the layer pattern**: Route → Controller → Service → Prisma
3. **Validate at boundaries**: Use Zod for all incoming data
4. **Type everything**: Full TypeScript, no `any` without justification
5. **Handle errors properly**: Use middleware, not try-catch in every controller
6. **Test behavior**: Test API responses, not internal implementation
