pub mod models;
mod py;

use self::py::*;
use self::models::*;
use cpython::{PyModule, Python};
use diesel::prelude::*;
use diesel::*;
use errors::*;
use errors::ErrorKind::*;
use schema::categories;

impl Category {
    pub fn add(conn: &PgConnection, name: &str) -> Result<Self> {
        if name == "" {
            return Err(Error::from(CategoryCreationError(
                "The Category name mustn't be empty".into(),
            )));
        }

        let category = NewCategory { name: name };
        insert(&category)
            .into(categories::table)
            .get_result(conn)
            .map_err(|e| e.into())
    }

    pub fn get(conn: &PgConnection, name: &str) -> Result<Self> {
        categories::table
            .filter(categories::name.eq(name))
            .first(conn)
            .map_err(|e| e.into())
    }

    // TODO: Remove when this is not useful anymore
    fn get_by_id(conn: &PgConnection, id: i32) -> Result<Self> {
        categories::table.find(id).first(conn).map_err(|e| e.into())
    }

    pub fn delete(self, conn: &PgConnection) -> Result<()> {
        delete(categories::table.find(self.id))
            .execute(conn)
            .map(|_| ())
            .map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "categories").unwrap();
    let _ = module.add(py, "add", py_fn!(py, py_add(name: String)));
    let _ = module.add(py, "remove", py_fn!(py, py_remove(name: String)));
    let _ = module.add(
        py,
        "set_alcoholic",
        py_fn!(py, py_set_alcoholic(id: i32, is_alcoholic: bool)),
    );
    let _ = module.add(
        py,
        "set_color",
        py_fn!(py, py_set_color(name: String, color: String)),
    );
    let _ = module.add(
        py,
        "rename",
        py_fn!(py, py_rename(oldname: String, newname: String)),
    );
    module
}
