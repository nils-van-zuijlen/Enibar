use cpython::{PyBool, PyObject, PyResult, Python, PythonObject, ToPyObject};
use notes::models::Note;
use model::Model;
use errors::*;
use diesel::*;

pub fn py_remove(py: Python, names: Vec<String>) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let res = conn.transaction::<_, Error, _>(|| {
        for name in &names {
            let note = Note::get(&*conn, name);
            if let Ok(n) = note {
                n.delete(&conn)?;
            }
        }

        Ok(())
    }).is_ok();

    Ok(py.False())
}
