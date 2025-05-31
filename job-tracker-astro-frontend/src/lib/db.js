import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

// Define the path for the database file.
// It will be in the root of the Astro project.
const dbDir = path.join(process.cwd(), '.astro'); // Store it in .astro to keep project root cleaner
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}
const dbPath = path.join(dbDir, 'job_tracker.db');

let db;

try {
    db = new Database(dbPath, { verbose: console.log }); // verbose logs SQLite statements
    console.log('Connected to the SQLite database at', dbPath);

    // Enable WAL mode for better concurrency and performance.
    db.pragma('journal_mode = WAL');

    // Create the applications table if it doesn't exist
    const createTableStmt = `
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            application_date TEXT,
            status TEXT,
            job_link TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    `;
    db.exec(createTableStmt);
    console.log("'applications' table created or already exists.");

    // Optional: Trigger to update 'updated_at' timestamp
    const createTriggerStmt = `
        CREATE TRIGGER IF NOT EXISTS update_applications_updated_at
        AFTER UPDATE ON applications
        FOR EACH ROW
        BEGIN
            UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
    `;
    db.exec(createTriggerStmt);
    console.log("'update_applications_updated_at' trigger created or already exists.");

} catch (err) {
    console.error('Failed to connect to or initialize the database:', err);
    // If the app can't run without the DB, you might want to throw the error
    // or handle it in a way that the app can gracefully inform the user.
    // For now, we'll let db be undefined if connection fails.
}

// Export the database instance directly.
// API routes can import this 'db' instance.
export default db;

// Example of how to use it in an API route:
// import db from '../../lib/db.js'; // Adjust path as needed
//
// export async function GET(context) {
//   if (!db) return new Response("Database not available", { status: 500 });
//   try {
//     const stmt = db.prepare("SELECT * FROM applications");
//     const apps = stmt.all();
//     return new Response(JSON.stringify(apps), {
//       status: 200,
//       headers: { "Content-Type": "application/json" }
//     });
//   } catch (err) {
//     console.error(err);
//     return new Response("Error fetching applications", { status: 500 });
//   }
// }
