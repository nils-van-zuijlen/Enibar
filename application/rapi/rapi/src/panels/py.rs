use cpython::{PyBool, PyObject, PyResult, Python, PythonObject, ToPyObject};
use panels::models::Panel;
use model::Model;
use diesel::*;

pub fn py_add(py: Python, name: &str) -> PyResult<PyObject> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::add(&*conn, name);
    match panel {
        Ok(p) => Ok(p.id.to_py_object(py).into_object()),
        Err(_) => Ok(py.None()),
    }
}

pub fn py_remove(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, name);
    if let Ok(p) = panel {
        if p.delete(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_hide(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, name);
    if let Ok(mut p) = panel {
        p.hidden = true;

        if p.save(&*conn).is_ok() {
            return Ok(py.False());
        }
    }

    Ok(py.False())
}

pub fn py_show(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, name);
    if let Ok(mut p) = panel {
        p.hidden = false;

        if p.save(&*conn).is_ok() {
            return Ok(py.False());
        }
    }

    Ok(py.False())
}

pub fn py_add_products(py: Python, id: i32, product_ids: Vec<i32>) -> PyResult<PyBool> {
    // XXX: Since the python API is so bad, I'm allowing this function to do a SQL request without
    // passing by the rust RAPI for performances reasons.
    use schema::products;
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get_by_id(&*conn, id);
    if let Ok(p) = panel {
        if let Ok(products) = products::table
            .filter(products::id.eq_any(product_ids))
            .load(&*conn)
        {
            return Ok(PyBool::get(py, p.add_products(&*conn, &products).is_ok()));
        }
    }

    Ok(py.False())
}

pub fn py_remove_products(py: Python, id: i32, product_ids: Vec<i32>) -> PyResult<PyBool> {
    use schema::products;
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get_by_id(&*conn, id);
    if let Ok(p) = panel {
        if let Ok(products) = products::table
            .filter(products::id.eq_any(product_ids))
            .load(&*conn)
        {
            return Ok(PyBool::get(
                py,
                p.remove_products(&*conn, &products).is_ok(),
            ));
        }
    }

    Ok(py.False())
}
