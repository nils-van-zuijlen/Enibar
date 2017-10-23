pub mod models;
mod py;

use self::py::*;
use self::models::*;
use schema::products;
use cpython::{PyModule, Python};
use diesel::prelude::*;
use diesel::*;
use errors::*;
use errors::ErrorKind::*;
use BigDecimal;

impl Product {
    pub fn delete(self, conn: &PgConnection) -> Result<()> {
        delete(products::table.find(self.id))
            .execute(conn)
            .map(|_| ())
            .map_err(|e| e.into())
    }

    pub fn get(conn: &PgConnection, name: &str) -> Result<Self> {
        products::table
            .filter(products::name.eq(name))
            .first(conn)
            .map_err(|e| e.into())
    }

    pub fn get_by_id(conn: &PgConnection, id: i32) -> Result<Self> {
        products::table.find(id).first(conn).map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "products").unwrap();
    let _ = module.add(py, "remove", py_fn!(py, py_remove(id: i32)));
    let _ = module.add(py, "rename", py_fn!(py, py_rename(id: i32, name: &str)));
    let _ = module.add(
        py,
        "set_percentage",
        py_fn!(py, py_set_percentage(id: i32, percentage: f64)),
    );

    module
}
