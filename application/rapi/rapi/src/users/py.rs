use users::models::*;
use cpython::{PyBool, PyResult, Python};

pub fn py_add(py: Python, username: &str, password: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();

    match User::add(&*conn, username, password) {
        Err(_) => Ok(PyBool::get(py, false)),
        Ok(_) => Ok(PyBool::get(py, true)),
    }
}

pub fn py_is_authorized(py: Python, username: &str, hash: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    if let Ok(user) = user {
        let is_authorized = user.is_authorized(hash);
        if let Ok(is_authorized) = is_authorized {
            return Ok(PyBool::get(py, is_authorized));
        }
    }
    Ok(PyBool::get(py, false))
}

pub fn py_change_password(py: Python, username: &str, new_password: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    let is_ok = if let Ok(user) = user {
        user.change_password(&*conn, new_password).is_ok()
    } else {
        false
    };

    Ok(PyBool::get(py, is_ok))
}

pub fn py_remove(py: Python, username: &str) -> PyResult<PyBool> {
    let conn = ::DB_POOL.get().unwrap();
    let user = User::get(&*conn, username);

    if let Ok(user) = user {
        match user.remove(&*conn) {
            Err(_) => return Ok(PyBool::get(py, false)),
            Ok(_) => return Ok(PyBool::get(py, true)),
        }
    }

    Ok(PyBool::get(py, false))
}
