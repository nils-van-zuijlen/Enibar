use cpython::{PyBool, PyObject, PyResult, Python, PythonObject, ToPyObject};
use panels::models::Panel;
use model::Model;
use diesel::*;
use errors::*;

pub fn py_add(py: Python, name: String) -> PyResult<PyObject> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::add(&*conn, &name);
    match panel {
        Ok(p) => Ok(p.id.to_py_object(py).into_object()),
        Err(_) => Ok(py.None()),
    }
}

pub fn py_remove(py: Python, name: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, &name);
    if let Ok(p) = panel {
        if p.delete(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_hide(py: Python, name: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, &name);
    if let Ok(mut p) = panel {
        p.hidden = true;

        if p.save(&*conn).is_ok() {
            return Ok(py.False());
        }
    }

    Ok(py.False())
}

pub fn py_show(py: Python, name: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let panel = Panel::get(&*conn, &name);
    if let Ok(mut p) = panel {
        p.hidden = false;

        if p.save(&*conn).is_ok() {
            return Ok(py.False());
        }
    }

    Ok(py.False())
}
