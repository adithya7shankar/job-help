// src/pages/api/applications/[id].js
import db from '../../../lib/db.js'; // Adjust path to db.js

export const prerender = false; // Ensure this endpoint is server-rendered

// Handler for GET requests to fetch a single application by ID
export async function GET(context) {
  if (!db) {
    return new Response(JSON.stringify({ error: "Database not available" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
  try {
    const id = context.params.id;
    const stmt = db.prepare("SELECT * FROM applications WHERE id = ?");
    const application = stmt.get(id);

    if (application) {
      return new Response(JSON.stringify(application), { status: 200, headers: { "Content-Type": "application/json" } });
    } else {
      return new Response(JSON.stringify({ error: "Application not found" }), { status: 404, headers: { "Content-Type": "application/json" } });
    }
  } catch (err) {
    console.error(`Error fetching application ${context.params.id}:`, err);
    return new Response(JSON.stringify({ error: "Error fetching application" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// Handler for PUT requests to update an application by ID
export async function PUT(context) {
  if (!db) {
    return new Response(JSON.stringify({ error: "Database not available" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
  try {
    const id = context.params.id;
    const updatedData = await context.request.json();

    // Check if application exists
    const checkStmt = db.prepare("SELECT * FROM applications WHERE id = ?");
    const application = checkStmt.get(id);
    if (!application) {
      return new Response(JSON.stringify({ error: "Application not found" }), { status: 404, headers: { "Content-Type": "application/json" } });
    }

    // Basic validation (at least one field to update should be provided)
    if (Object.keys(updatedData).length === 0) {
        return new Response(JSON.stringify({ error: "No update data provided" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }
    
    // Construct SET part of SQL query dynamically
    // Only update fields that are actually provided in the request body
    const fieldsToUpdate = {};
    if (updatedData.company_name !== undefined) fieldsToUpdate.company_name = updatedData.company_name;
    if (updatedData.job_title !== undefined) fieldsToUpdate.job_title = updatedData.job_title;
    if (updatedData.application_date !== undefined) fieldsToUpdate.application_date = updatedData.application_date;
    if (updatedData.status !== undefined) fieldsToUpdate.status = updatedData.status;
    if (updatedData.job_link !== undefined) fieldsToUpdate.job_link = updatedData.job_link;
    if (updatedData.notes !== undefined) fieldsToUpdate.notes = updatedData.notes;

    if (Object.keys(fieldsToUpdate).length === 0) {
        return new Response(JSON.stringify({ error: "No valid fields to update provided" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }
    
    const setClauses = Object.keys(fieldsToUpdate).map(key => `${key} = ?`).join(', ');
    const values = [...Object.values(fieldsToUpdate), id];

    const stmt = db.prepare(`UPDATE applications SET ${setClauses}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`);
    stmt.run(...values);
    
    const updatedAppStmt = db.prepare("SELECT * FROM applications WHERE id = ?");
    const updatedApplication = updatedAppStmt.get(id);

    return new Response(JSON.stringify(updatedApplication), { status: 200, headers: { "Content-Type": "application/json" } });

  } catch (err) {
    console.error(`Error updating application ${context.params.id}:`, err);
    if (err instanceof SyntaxError) { // JSON parsing error
        return new Response(JSON.stringify({ error: "Invalid JSON payload" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }
    return new Response(JSON.stringify({ error: "Error updating application" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// Handler for DELETE requests to delete an application by ID
export async function DELETE(context) {
  if (!db) {
    return new Response(JSON.stringify({ error: "Database not available" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
  try {
    const id = context.params.id;

    // Check if application exists before deleting
    const checkStmt = db.prepare("SELECT id FROM applications WHERE id = ?");
    const application = checkStmt.get(id);
    if (!application) {
      return new Response(JSON.stringify({ error: "Application not found" }), { status: 404, headers: { "Content-Type": "application/json" } });
    }

    const stmt = db.prepare("DELETE FROM applications WHERE id = ?");
    const info = stmt.run(id);

    if (info.changes > 0) {
      return new Response(null, { status: 204 }); // 204 No Content
    } else {
      // This case should ideally be caught by the check above, but as a fallback:
      return new Response(JSON.stringify({ error: "Application not found or already deleted" }), { status: 404, headers: { "Content-Type": "application/json" } });
    }
  } catch (err) {
    console.error(`Error deleting application ${context.params.id}:`, err);
    return new Response(JSON.stringify({ error: "Error deleting application" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}
