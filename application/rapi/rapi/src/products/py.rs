use cpython::{PyBool, PyResult, Python};
use products::models::Product;
use model::Model;
use BigDecimal;
use bigdecimal;
use std::str::FromStr;

pub fn py_remove(py: Python, id: i32) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let product = Product::get_by_id(&*conn, id);
    if let Ok(p) = product {
        if p.remove(&conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_rename(py: Python, id: i32, new_name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let product = Product::get_by_id(&*conn, id);
    if let Ok(mut p) = product {
        p.name = new_name.into();
        if p.save(&conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_set_percentage(py: Python, id: i32, percentage: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let product = Product::get_by_id(&*conn, id);
    if let Ok(mut p) = product {
        p.percentage = BigDecimal(bigdecimal::BigDecimal::from_str(&percentage).unwrap());
        if p.save(&conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}
