// src/pages/api/applications/index.js
import db from '../../../lib/db.js'; // Adjust path to db.js

export const prerender = false; // Ensure this endpoint is server-rendered

// Handler for GET requests to fetch all applications
export async function GET(context) {
  if (!db) {
    return new Response(JSON.stringify({ error: "Database not available" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
  try {
    const stmt = db.prepare("SELECT * FROM applications ORDER BY created_at DESC");
    const applications = stmt.all();
    return new Response(JSON.stringify(applications), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    console.error("Error fetching applications:", err);
    return new Response(JSON.stringify({ error: "Error fetching applications" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

// Handler for POST requests to add a new application
export async function POST(context) {
  if (!db) {
    return new Response(JSON.stringify({ error: "Database not available" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
  try {
    const newApplication = await context.request.json();

    // Basic validation
    if (!newApplication.company_name || !newApplication.job_title) {
      return new Response(JSON.stringify({ error: "Company name and job title are required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const stmt = db.prepare(`
      INSERT INTO applications (company_name, job_title, application_date, status, job_link, notes)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    const info = stmt.run(
      newApplication.company_name,
      newApplication.job_title,
      newApplication.application_date || null,
      newApplication.status || 'Wishlist/To Apply',
      newApplication.job_link || null,
      newApplication.notes || null
    );

    // Fetch the newly created application to return it
    const newAppStmt = db.prepare("SELECT * FROM applications WHERE id = ?");
    const createdApplication = newAppStmt.get(info.lastInsertRowid);
    
    return new Response(JSON.stringify(createdApplication), {
      status: 201, // 201 Created
      headers: { "Content-Type": "application/json" }
    });

  } catch (err) {
    console.error("Error adding application:", err);
    if (err instanceof SyntaxError) { // JSON parsing error
        return new Response(JSON.stringify({ error: "Invalid JSON payload" }), {
            status: 400,
            headers: { "Content-Type": "application/json" }
        });
    }
    return new Response(JSON.stringify({ error: "Error adding application" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
