# Project Instructions for Claude Code

> This file is automatically loaded into context when Claude Code starts.

## Project Overview

This is a React application built with TypeScript and Vite. It provides [BRIEF_DESCRIPTION] for [TARGET_USERS].

**Tech Stack:**
- React 18 with TypeScript
- Vite for build tooling
- React Router for navigation
- TanStack Query for server state
- Zustand for client state
- Tailwind CSS for styling

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      React App                          │
├─────────────────────────────────────────────────────────┤
│  Pages          │  Components      │  Hooks             │
│  └── routes     │  └── ui/         │  └── queries/      │
│                 │  └── features/   │  └── mutations/    │
├─────────────────────────────────────────────────────────┤
│  State (Zustand)        │  API Layer (TanStack Query)   │
├─────────────────────────────────────────────────────────┤
│                    Services / Utils                      │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components (Button, Input, Modal)
│   │   └── features/        # Feature-specific components
│   ├── hooks/
│   │   ├── queries/         # TanStack Query hooks
│   │   └── mutations/       # TanStack Mutation hooks
│   ├── pages/               # Route components
│   ├── services/            # API service functions
│   ├── stores/              # Zustand stores
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
├── public/                  # Static assets
├── tests/                   # Test files
└── CLAUDE.md               # This file
```

## Development Commands

### Build & Run
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- src/components/Button.test.tsx
```

### Linting & Formatting
```bash
# Lint the codebase
npm run lint

# Fix lint issues
npm run lint:fix

# Format code with Prettier
npm run format

# Type checking
npm run typecheck
```

## Code Style & Conventions

### Component Structure
```tsx
// 1. Imports (external, internal, relative, types)
import { useState } from 'react';
import { Button } from '@/components/ui';
import { useUserQuery } from '@/hooks/queries';
import type { User } from '@/types';

// 2. Types/Interfaces
interface UserCardProps {
  userId: string;
  onSelect?: (user: User) => void;
}

// 3. Component
export function UserCard({ userId, onSelect }: UserCardProps) {
  // Hooks first
  const { data: user, isLoading } = useUserQuery(userId);
  const [isExpanded, setIsExpanded] = useState(false);

  // Early returns
  if (isLoading) return <Skeleton />;
  if (!user) return null;

  // Handlers
  const handleClick = () => onSelect?.(user);

  // Render
  return (
    <div onClick={handleClick}>
      {user.name}
    </div>
  );
}
```

### Naming Conventions
- **Components**: `PascalCase` - `UserCard.tsx`
- **Hooks**: `camelCase` with `use` prefix - `useUserQuery.ts`
- **Utils**: `camelCase` - `formatDate.ts`
- **Types**: `PascalCase` - `User`, `ApiResponse<T>`
- **Constants**: `SCREAMING_SNAKE_CASE` - `MAX_RETRIES`

### File Organization
- One component per file
- Co-locate tests: `Button.tsx` + `Button.test.tsx`
- Index files for clean exports: `components/ui/index.ts`

### State Management Rules
- **Server state**: Always use TanStack Query
- **Global client state**: Use Zustand stores
- **Local component state**: Use useState/useReducer
- **Form state**: Use React Hook Form

## Testing Requirements

- All new components must have tests
- Aim for 80% coverage on new code
- Test user interactions, not implementation details

### Test Structure
```tsx
import { render, screen, userEvent } from '@/tests/utils';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  it('renders user name', () => {
    render(<UserCard userId="123" />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', async () => {
    const onSelect = vi.fn();
    render(<UserCard userId="123" onSelect={onSelect} />);

    await userEvent.click(screen.getByRole('button'));

    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: '123' }));
  });
});
```

## Git Workflow

### Commit Messages
```
feat(auth): add OAuth login flow
fix(ui): resolve modal z-index issue
refactor(hooks): extract common query logic
```

### Branch Naming
- `feature/add-user-dashboard`
- `fix/login-redirect-loop`
- `refactor/query-hooks`

## Important Patterns

### API Queries
```tsx
// hooks/queries/useUserQuery.ts
export function useUserQuery(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => userService.getById(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

### Error Boundaries
```tsx
// Wrap feature sections, not the entire app
<ErrorBoundary fallback={<ErrorFallback />}>
  <UserDashboard />
</ErrorBoundary>
```

### Loading States
```tsx
// Use Suspense for data loading
<Suspense fallback={<DashboardSkeleton />}>
  <Dashboard />
</Suspense>
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API base URL | Yes |
| `VITE_AUTH_DOMAIN` | Auth provider domain | Yes |
| `VITE_SENTRY_DSN` | Sentry error tracking | No |

## Known Issues & Gotchas

- **Hot reload breaks with circular imports**: Check for circular dependencies if HMR stops working
- **TanStack Query devtools**: Disabled in production automatically
- **Tailwind purge**: Ensure dynamic classes use complete strings, not concatenation

## Rules for Claude

1. **Think first, code second**: Read related components before modifying
2. **Follow existing patterns**: Check similar components for conventions
3. **Keep components focused**: One responsibility per component
4. **Test user behavior**: Write tests from user perspective
5. **Type everything**: No `any` types without explicit justification
6. **Simplicity wins**: Prefer readable code over clever abstractions
