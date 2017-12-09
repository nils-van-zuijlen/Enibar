pub mod models;
mod py;

use cpython::{PyModule, Python};
use diesel::*;
use errors::*;
use errors::ErrorKind::*;
use validator::Validate;
use self::models::*;
use self::py::*;
use schema::{categories, panel_content, panels, products};
use products::models::Product;

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

    // TODO: Remove this when it's not necessary anymore
    pub fn get_by_id(conn: &PgConnection, id: i32) -> Result<Self> {
        panels::table.find(id).first(conn).map_err(|e| e.into())
    }

    pub fn add_products(self, conn: &PgConnection, products: &[Product]) -> Result<()> {
        insert_into(panel_content::table)
            .values(&products
                .iter()
                .map(|product| {
                    (
                        panel_content::panel_id.eq(self.id),
                        panel_content::product_id.eq(product.id),
                    )
                })
                .collect::<Vec<_>>())
            .execute(conn)?;

        Ok(())
    }

    pub fn remove_products(self, conn: &PgConnection, products: &[Product]) -> Result<()> {
        delete(
            panel_content::table.filter(
                panel_content::panel_id.eq(self.id).and(
                    panel_content::product_id.eq_any(
                        products
                            .iter()
                            .map(|product| product.id)
                            .collect::<Vec<_>>(),
                    ),
                ),
            ),
        ).execute(conn)?;

        Ok(())
    }

    pub fn content(&self, conn: &PgConnection) -> Result<Vec<PanelItem>> {
        panel_content::table
            .inner_join(products::table.inner_join(categories::table))
            .filter(panel_content::panel_id.eq(self.id))
            .select((products::all_columns, categories::all_columns))
            .load(conn)
            .map_err(|e| e.into())
    }
}

pub fn as_module(py: Python) -> PyModule {
    let module = PyModule::new(py, "panels").unwrap();
    let _ = module.add(py, "add", py_fn!(py, py_add(name: &str)));
    let _ = module.add(py, "remove", py_fn!(py, py_remove(name: &str)));
    let _ = module.add(py, "hide", py_fn!(py, py_hide(name: &str)));
    let _ = module.add(py, "show", py_fn!(py, py_show(name: &str)));
    let _ = module.add(
        py,
        "add_products",
        py_fn!(py, py_add_products(id: i32, product_ids: Vec<i32>)),
    );
    let _ = module.add(
        py,
        "remove_products",
        py_fn!(py, py_remove_products(id: i32, product_ids: Vec<i32>)),
    );
    let _ = module.add(py, "get_content", py_fn!(py, py_get_content(id: i32)));

    module
}
