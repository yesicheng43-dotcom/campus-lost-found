DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  display_name TEXT NOT NULL,
  student_id TEXT NOT NULL,
  faculty TEXT NOT NULL,
  email TEXT NOT NULL DEFAULT '',
  phone TEXT NOT NULL DEFAULT '',
  role TEXT NOT NULL CHECK (role IN ('user', 'admin')) DEFAULT 'user',
  avatar TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL CHECK (type IN ('lost', 'found')),
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  location TEXT NOT NULL,
  event_time TEXT NOT NULL,
  description TEXT NOT NULL,
  image TEXT,
  contact TEXT NOT NULL,
  status TEXT NOT NULL,
  owner TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
