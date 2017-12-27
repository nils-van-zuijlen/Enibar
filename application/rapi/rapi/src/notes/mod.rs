pub mod models;
mod py;

use self::py::*;
pub use self::models::*;
use schema::notes;
use cpython::{PyModule, Python};
use diesel::prelude::*;
use errors::*;

impl Note {
    pub fn get(conn: &PgConnection, name: &str) -> Result<Self> {
        notes::table.filter(notes::nickname.eq(name)).first(conn).map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "notes").unwrap();
    let _ = module.add(py, "remove", py_fn!(py, py_remove(id: Vec<String>)));

    module
}
