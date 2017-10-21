use cpython::{PyBool, PyObject, PyResult, Python, PythonObject, ToPyObject};
use note_categories::models::NoteCategory;
use model::Model;
use diesel::*;
use errors::*;

pub fn py_add(py: Python, name: String) -> PyResult<PyObject> {
    let conn = ::DB_POOL.get().unwrap();

    let category = NoteCategory::add(&*conn, &name);
    match category {
        Ok(c) => Ok(c.id.to_py_object(py).into_object()),
        Err(_) => Ok(py.None()),
    }
}

pub fn py_remove(py: Python, names: Vec<String>) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let res = conn.transaction::<_, Error, _>(|| {
        for name in &names {
            let category = NoteCategory::get(&*conn, &name);
            if let Ok(c) = category {
                c.delete(&conn)?;
            }
        }

        Ok(())
    }).is_ok();

    Ok(PyBool::get(py, res))
}

pub fn py_rename(py: Python, old_name: String, new_name: String) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let category = NoteCategory::get(&*conn, &old_name);

    if let Ok(mut category) = category {
        category.name = new_name;

        if category.save(&*conn).is_ok() {
            return Ok(py.True());
        }
    }

    Ok(py.False())
}
