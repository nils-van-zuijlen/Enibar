pub mod models;
mod py;

use self::py::*;
use self::models::*;
use cpython::{PyModule, Python};
use diesel::prelude::*;
use diesel::*;
use errors::*;
use errors::ErrorKind::*;
use schema::note_categories;
use validator::Validate;

impl NoteCategory {
    pub fn add(conn: &PgConnection, name: &str) -> Result<Self> {
        let new_category = NewNoteCategory { name: name };
        new_category
            .validate()
            .map_err(|e| Error::from(ValidationError(e)))?;
        insert(&new_category)
            .into(note_categories::table)
            .get_result(conn)
            .map_err(|e| e.into())
    }

    pub fn get(conn: &PgConnection, name: &str) -> Result<Self> {
        note_categories::table
            .filter(note_categories::name.eq(name))
            .first(conn)
            .map_err(|e| e.into())
    }

    pub fn delete(self, conn: &PgConnection) -> Result<()> {
        delete(
            note_categories::table.filter(
                note_categories::id
                    .eq(self.id)
                    .and(note_categories::protected.eq(false)),
            ),
        ).execute(conn)
            .map(|_| ())
            .map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "note_categories").unwrap();
    let _ = module.add(py, "add", py_fn!(py, py_add(name: &str)));
    let _ = module.add(py, "remove", py_fn!(py, py_remove(names: Vec<String>)));
    let _ = module.add(
        py,
        "rename",
        py_fn!(py, py_rename(old_name: &str, new_name: &str)),
    );
    module
}
