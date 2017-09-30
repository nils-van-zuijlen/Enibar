use cpython::{Python, PyResult, PyObject, ToPyObject, PythonObject, PyBool};
use categories::models::Category;
use model::Model;

pub fn py_add(py: Python, name: String) -> PyResult<PyObject> {
    let conn = ::DB_POOL.get().unwrap();

    let category = Category::add(&*conn, &name);
    match category {
        Ok(c) => {
            Ok(c.id.to_py_object(py).into_object())
        },
        Err(_) => {
            Ok(py.None())
        }
    }
}

pub fn py_remove(py: Python, name: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let category = Category::get(&*conn, &name);
    if let Ok(c) = category {
        if c.delete(&*conn).is_ok() {
            return Ok(py.True())
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
            return Ok(py.True())
        }
    }

    Ok(py.False())
}

pub fn py_set_color(py: Python, name: String, color: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let category = Category::get(&*conn, &name);

    if let Ok(mut category) = category {
        category.color = color;

        if category.save(&*conn).is_ok() {
            return Ok(py.True())
        }
    }

    Ok(py.False())
}

pub fn py_rename(py: Python, oldname: String, newname: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let category = Category::get(&*conn, &oldname);

    if let Ok(mut category) = category {
        category.name = newname;

        if category.save(&*conn).is_ok() {
            return Ok(py.True())
        }
    }

    Ok(py.False())
}
