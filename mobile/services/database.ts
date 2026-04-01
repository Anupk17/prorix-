import * as SQLite from 'expo-sqlite';
import { SEED_APPS } from '../constants/Apps';

// Lazy-initialized DB — opened inside initDb() so errors are catchable
let db: SQLite.SQLiteDatabase | null = null;

export const getDb = (): SQLite.SQLiteDatabase => {
  if (!db) {
    db = SQLite.openDatabaseSync('priorix.db');
  }
  return db;
};

export const initDb = async (): Promise<void> => {
  try {
    const database = getDb();
    await database.execAsync(`
      PRAGMA journal_mode = WAL;
      CREATE TABLE IF NOT EXISTS Apps (
        app_id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT UNIQUE NOT NULL,
        app_emoji TEXT,
        is_enabled INTEGER DEFAULT 1
      );

      CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS Priority (
        priority_id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER UNIQUE,
        priority_order INTEGER,
        notifications_count INTEGER DEFAULT 0,
        bandit_weight REAL DEFAULT 1.0,
        FOREIGN KEY (app_id) REFERENCES Apps(app_id)
      );

      CREATE TABLE IF NOT EXISTS Notifications (
        notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        message TEXT,
        timestamp TEXT,
        is_read INTEGER DEFAULT 0,
        is_dismissed INTEGER DEFAULT 0,
        FOREIGN KEY (app_id) REFERENCES Apps(app_id)
      );

      CREATE TABLE IF NOT EXISTS AI_Summaries (
        summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        summary_text TEXT,
        created_at TEXT,
        FOREIGN KEY (app_id) REFERENCES Apps(app_id)
      );
    `);

    // Seed apps
    for (const app of SEED_APPS) {
      await database.runAsync(
        'INSERT OR IGNORE INTO Apps (app_name, app_emoji) VALUES (?, ?)',
        [app.name, app.emoji]
      );
    }

    // Ensure Priority rows only if they don't exist
    const existingPriorities = await database.getAllAsync<{app_id: number}>('SELECT app_id FROM Priority');
    const existingAppIds = new Set(existingPriorities.map(p => p.app_id));
    
    const apps = await database.getAllAsync<{app_id: number}>('SELECT app_id FROM Apps');
    for (let i = 0; i < apps.length; i++) {
      if (!existingAppIds.has(apps[i].app_id)) {
        await database.runAsync(
          'INSERT OR IGNORE INTO Priority (app_id, priority_order) VALUES (?, ?)',
          [apps[i].app_id, i + 1]
        );
      }
    }
  } catch (e) {
    console.error('[DB] initDb error:', e);
    throw e;
  }
};

export const registerUser = async (name: string, email: string, pass: string) => {
  try {
    const result = await getDb().runAsync(
      'INSERT INTO Users (name, email, password) VALUES (?, ?, ?)',
      [name, email, pass]
    );
    return result.lastInsertRowId;
  } catch (e) {
    console.error('[DB] Registration failed:', e);
    throw new Error("Email already exists.");
  }
};

export const loginUser = async (email: string, pass: string) => {
  const user = await getDb().getFirstAsync<any>(
    'SELECT * FROM Users WHERE email = ? AND password = ?',
    [email, pass]
  );
  return user;
};

export const updateUser = async (userId: number, name: string, email: string) => {
  await getDb().runAsync(
    'UPDATE Users SET name = ?, email = ? WHERE user_id = ?',
    [name, email.toLowerCase(), userId]
  );
};

export const getApps = async () => {
  return await getDb().getAllAsync<any>('SELECT * FROM Apps');
};

export const getNotifications = async () => {
  return await getDb().getAllAsync<any>(`
    SELECT n.*, a.app_name, a.app_emoji, p.priority_order, p.bandit_weight
    FROM Notifications n
    JOIN Apps a ON n.app_id = a.app_id
    JOIN Priority p ON p.app_id = n.app_id
    WHERE n.is_read = 0 AND n.is_dismissed = 0 AND a.is_enabled = 1
    ORDER by p.bandit_weight DESC, p.priority_order ASC, n.notif_id ASC
  `);
};

export const markRead = async (notifId: number, _appId: number) => {
  await getDb().runAsync('UPDATE Notifications SET is_read = 1 WHERE notif_id = ?', [notifId]);
};

export const markDismissed = async (notifId: number, _appId: number) => {
  await getDb().runAsync('UPDATE Notifications SET is_dismissed = 1 WHERE notif_id = ?', [notifId]);
};

export const updateBanditWeight = async (appId: number, reward: number) => {
  const row = await getDb().getFirstAsync<{bandit_weight: number}>(
    'SELECT bandit_weight FROM Priority WHERE app_id = ?', [appId]
  );
  if (row) {
    const alpha = 0.1;
    const newWeight = row.bandit_weight + alpha * (reward - row.bandit_weight);
    await getDb().runAsync(
      'UPDATE Priority SET bandit_weight = ? WHERE app_id = ?', [newWeight, appId]
    );
  }
};

export const getDashboardData = async () => {
  return await getDb().getAllAsync<any>(`
    SELECT a.app_name, a.app_emoji,
           COUNT(n.notif_id) as total_notifs,
           SUM(n.is_read) as read_count,
           SUM(n.is_dismissed) as dismissed_count,
           p.bandit_weight
    FROM Apps a
    LEFT JOIN Notifications n ON n.app_id = a.app_id
    JOIN Priority p ON p.app_id = a.app_id
    WHERE a.is_enabled = 1
    GROUP BY a.app_id
  `);
};

export const updateAppStatus = async (appId: number, isEnabled: boolean) => {
  await getDb().runAsync('UPDATE Apps SET is_enabled = ? WHERE app_id = ?', [isEnabled ? 1 : 0, appId]);
};

export const updatePriorityOrder = async (appId: number, order: number) => {
  await getDb().runAsync('UPDATE Priority SET priority_order = ? WHERE app_id = ?', [order, appId]);
};

export const getAppsWithPriority = async () => {
  return await getDb().getAllAsync<any>(`
    SELECT a.*, p.priority_order, p.bandit_weight
    FROM Apps a
    JOIN Priority p ON a.app_id = p.app_id
    ORDER BY p.priority_order ASC
  `);
};

export const saveNotification = async (appId: number, message: string) => {
  await getDb().runAsync(
    'INSERT INTO Notifications (app_id, message, timestamp) VALUES (?, ?, ?)',
    [appId, message, new Date().toISOString()]
  );
};
