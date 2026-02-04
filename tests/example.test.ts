/**
 * Example TypeScript Test File
 *
 * This file demonstrates testing patterns for TypeScript projects
 * using Vitest or Jest. Delete or modify for your project.
 *
 * Run with: npm test or npx vitest
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
// For Jest, use: import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';

// ============================================
// Example: Testing Pure Functions
// ============================================

// Function to test (normally imported from src/)
function add(a: number, b: number): number {
  return a + b;
}

function divide(a: number, b: number): number {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}

describe('Math Utilities', () => {
  describe('add', () => {
    it('should add two positive numbers', () => {
      // Arrange
      const a = 2;
      const b = 3;

      // Act
      const result = add(a, b);

      // Assert
      expect(result).toBe(5);
    });

    it('should handle negative numbers', () => {
      expect(add(-1, -2)).toBe(-3);
      expect(add(-1, 2)).toBe(1);
    });

    it('should handle zero', () => {
      expect(add(0, 5)).toBe(5);
      expect(add(5, 0)).toBe(5);
    });
  });

  describe('divide', () => {
    it('should divide two numbers', () => {
      expect(divide(10, 2)).toBe(5);
    });

    it('should throw on division by zero', () => {
      expect(() => divide(10, 0)).toThrow('Division by zero');
    });
  });
});

// ============================================
// Example: Testing Async Functions
// ============================================

// Async function to test
async function fetchUser(id: string): Promise<{ id: string; name: string }> {
  // Simulating API call
  await new Promise((resolve) => setTimeout(resolve, 10));
  if (id === 'not-found') throw new Error('User not found');
  return { id, name: 'Test User' };
}

describe('User API', () => {
  it('should fetch user by id', async () => {
    const user = await fetchUser('123');

    expect(user).toEqual({
      id: '123',
      name: 'Test User',
    });
  });

  it('should throw for non-existent user', async () => {
    await expect(fetchUser('not-found')).rejects.toThrow('User not found');
  });
});

// ============================================
// Example: Testing with Mocks
// ============================================

// Service with dependency
interface Logger {
  log(message: string): void;
}

class UserService {
  constructor(private logger: Logger) {}

  createUser(name: string): { id: string; name: string } {
    const user = { id: crypto.randomUUID(), name };
    this.logger.log(`Created user: ${name}`);
    return user;
  }
}

describe('UserService', () => {
  let mockLogger: Logger;
  let service: UserService;

  beforeEach(() => {
    // Create mock
    mockLogger = {
      log: vi.fn(), // Jest: jest.fn()
    };
    service = new UserService(mockLogger);
  });

  afterEach(() => {
    vi.clearAllMocks(); // Jest: jest.clearAllMocks()
  });

  it('should create user and log', () => {
    const user = service.createUser('Alice');

    expect(user.name).toBe('Alice');
    expect(user.id).toBeDefined();
    expect(mockLogger.log).toHaveBeenCalledWith('Created user: Alice');
    expect(mockLogger.log).toHaveBeenCalledTimes(1);
  });
});

// ============================================
// Example: Testing React Components (with React Testing Library)
// ============================================

/*
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../src/components/Button';

describe('Button', () => {
  it('should render with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('should call onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
*/

// ============================================
// Example: Snapshot Testing
// ============================================

/*
describe('Component Snapshots', () => {
  it('should match snapshot', () => {
    const { container } = render(<UserCard user={{ name: 'Alice', email: 'alice@example.com' }} />);
    expect(container).toMatchSnapshot();
  });
});
*/
