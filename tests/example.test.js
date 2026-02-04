/**
 * Example JavaScript Test File
 *
 * This file demonstrates testing patterns for Node.js projects
 * using Jest. Delete or modify for your project.
 *
 * Run with: npm test or npx jest
 */

// ============================================
// Example: Testing Pure Functions
// ============================================

// Functions to test (normally imported from src/)
function add(a, b) {
  return a + b;
}

function divide(a, b) {
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
async function fetchUser(id) {
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
class UserService {
  constructor(logger) {
    this.logger = logger;
  }

  createUser(name) {
    const user = { id: Math.random().toString(36).substr(2, 9), name };
    this.logger.log(`Created user: ${name}`);
    return user;
  }
}

describe('UserService', () => {
  let mockLogger;
  let service;

  beforeEach(() => {
    // Create mock
    mockLogger = {
      log: jest.fn(),
    };
    service = new UserService(mockLogger);
  });

  afterEach(() => {
    jest.clearAllMocks();
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
// Example: Testing with Spies
// ============================================

describe('Spying on methods', () => {
  it('should spy on console.log', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

    console.log('test message');

    expect(consoleSpy).toHaveBeenCalledWith('test message');
    consoleSpy.mockRestore();
  });
});

// ============================================
// Example: Testing Timers
// ============================================

function delayedGreeting(name, callback) {
  setTimeout(() => {
    callback(`Hello, ${name}!`);
  }, 1000);
}

describe('Timer functions', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should call callback after delay', () => {
    const callback = jest.fn();

    delayedGreeting('World', callback);

    // Callback not called yet
    expect(callback).not.toHaveBeenCalled();

    // Fast-forward time
    jest.advanceTimersByTime(1000);

    // Now callback should be called
    expect(callback).toHaveBeenCalledWith('Hello, World!');
  });
});

// ============================================
// Example: Testing with Setup and Teardown
// ============================================

describe('Database operations', () => {
  let db;

  beforeAll(() => {
    // Run once before all tests in this describe block
    // db = connectToTestDatabase();
    db = { connected: true };
  });

  afterAll(() => {
    // Run once after all tests in this describe block
    // db.disconnect();
    db.connected = false;
  });

  beforeEach(() => {
    // Run before each test
    // db.clearTables();
  });

  afterEach(() => {
    // Run after each test
    // db.rollback();
  });

  it('should be connected', () => {
    expect(db.connected).toBe(true);
  });
});

// ============================================
// Example: Testing Error Handling
// ============================================

function validateEmail(email) {
  if (!email) throw new Error('Email is required');
  if (!email.includes('@')) throw new Error('Invalid email format');
  return email.toLowerCase().trim();
}

describe('validateEmail', () => {
  it('should normalize valid email', () => {
    expect(validateEmail('Test@Example.com')).toBe('test@example.com');
  });

  it('should throw for empty email', () => {
    expect(() => validateEmail('')).toThrow('Email is required');
  });

  it('should throw for invalid format', () => {
    expect(() => validateEmail('not-an-email')).toThrow('Invalid email format');
  });
});

// ============================================
// Example: Testing Express Routes (with supertest)
// ============================================

/*
const request = require('supertest');
const app = require('../src/app');

describe('GET /api/users', () => {
  it('should return list of users', async () => {
    const response = await request(app)
      .get('/api/users')
      .expect('Content-Type', /json/)
      .expect(200);

    expect(response.body).toBeInstanceOf(Array);
  });

  it('should return 404 for unknown user', async () => {
    const response = await request(app)
      .get('/api/users/unknown-id')
      .expect(404);

    expect(response.body.error).toBe('User not found');
  });
});

describe('POST /api/users', () => {
  it('should create new user', async () => {
    const newUser = { name: 'Test User', email: 'test@example.com' };

    const response = await request(app)
      .post('/api/users')
      .send(newUser)
      .expect(201);

    expect(response.body.name).toBe('Test User');
    expect(response.body.id).toBeDefined();
  });

  it('should validate required fields', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({})
      .expect(400);

    expect(response.body.error).toContain('required');
  });
});
*/
