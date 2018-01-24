use cpython::{PyBool, PyDict, PyResult, Python, ToPyObject};
use notes::models::Note;
use notes;
use model::Model;
use errors::*;
use diesel::*;

pub fn py_remove(py: Python, names: Vec<String>) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    let res = conn.transaction::<_, Error, _>(|| {
        for name in &names {
            let note = Note::get(&*conn, name);
            if let Ok(n) = note {
                n.remove(&conn)?;
            }
        }

        Ok(())
    }).is_ok();

    Ok(PyBool::get(py, res))
}

pub fn py_get_cache(py: Python) -> PyResult<PyDict> {
    let conn = ::DB_POOL.get().unwrap();
    let cache = PyDict::new(py);
    for cache_line in &notes::get_cache(&*conn).unwrap() {
        let mut line = cache_line.note.to_py_object(py);
        line.set_item(
            py,
            "categories",
            &cache_line
                .categories
                .iter()
                .map(|c| c.name.as_str())
                .collect::<Vec<&str>>(),
        )?;
        line.set_item(py, "hidden", cache_line.hidden)?;
        cache.set_item(py, &cache_line.note.nickname, line)?;
    }

    Ok(cache)
}

pub fn py_get_note_cache(py: Python, note: String) -> PyResult<PyDict> {
    let conn = ::DB_POOL.get().unwrap();
    if let Ok(cache_line) = notes::get_note_cache(&*conn, &note) {
        let cache = cache_line.note.to_py_object(py);
        cache.set_item(
            py,
            "categories",
            &cache_line
                .categories
                .iter()
                .map(|c| c.name.as_str())
                .collect::<Vec<&str>>(),
        )?;
        cache.set_item(py, "hidden", cache_line.hidden)?;

        return Ok(cache);
    }

    Ok(PyDict::new(py))
}
