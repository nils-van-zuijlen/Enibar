pub mod models;
mod py;

use cpython::{PyModule, Python};
use diesel::*;
use errors::*;
use errors::ErrorKind::*;
use validator::Validate;
use self::models::*;
use self::py::*;
use schema::panels;

impl Panel {
    pub fn add(conn: &PgConnection, name: &str) -> Result<Self> {
        let new_panel = NewPanel { name: name };
        new_panel
            .validate()
            .map_err(|e| Error::from(ValidationError(e)))?;
        insert_into(panels::table)
            .values(&new_panel)
            .get_result(conn)
            .map_err(|e| e.into())
    }

    pub fn get(conn: &PgConnection, name: &str) -> Result<Self> {
        panels::table
            .filter(panels::name.eq(name))
            .first(conn)
            .map_err(|e| e.into())
    }

    pub fn delete(self, conn: &PgConnection) -> Result<()> {
        delete(panels::table.find(self.id))
            .execute(conn)
            .map(|_| ())
            .map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "panels").unwrap();
    let _ = module.add(py, "add", py_fn!(py, py_add(name: &str)));
    let _ = module.add(py, "remove", py_fn!(py, py_remove(name: &str)));
    let _ = module.add(py, "hide", py_fn!(py, py_hide(name: &str)));
    let _ = module.add(py, "show", py_fn!(py, py_show(name: &str)));

    module
}
