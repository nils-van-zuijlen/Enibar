pub mod models;
mod py;

use self::models::Note;
use cpython::{PyModule, Python};
use diesel::prelude::*;
use schema::notes;
use errors::*;
use errors::ErrorKind::*;
use self::py::*;

impl Note {
    fn all(conn: &PgConnection) -> Result<Vec<Self>> {
        notes::table.load(conn).map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "notes").unwrap();
    let _ = module.add(py, "get_cache", py_fn!(py, py_get_cache()));
    module
}
