use cpython::{PyBool, PyObject, PyResult, Python, PythonObject, ToPyObject};
use categories::models::Category;
use model::Model;

pub fn py_add(py: Python, name: &str) -> PyResult<PyObject> {
    let conn = ::DB_POOL.get().unwrap();

    let category = Category::add(&*conn, name);
    match category {
        Ok(c) => Ok(c.id.to_py_object(py).into_object()),
        Err(_) => Ok(py.None()),
    }
}

pub fn py_remove(py: Python, name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let category = Category::get(&*conn, name);
    if let Ok(c) = category {
        if c.delete(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_set_alcoholic(py: Python, id: i32, is_alcoholic: bool) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let category = Category::get_by_id(&*conn, id);

    if let Ok(mut category) = category {
        category.alcoholic = is_alcoholic;

        if category.save(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_set_color(py: Python, name: &str, color: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let category = Category::get(&*conn, name);

    if let Ok(mut category) = category {
        category.color = color.into();

        if category.save(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}

pub fn py_rename(py: Python, old_name: &str, new_name: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let category = Category::get(&*conn, old_name);

    if let Ok(mut category) = category {
        category.name = new_name.into();

        if category.save(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}
